#!/usr/bin/env python3
"""Risk stop for production deploys (framework layer 3, ADR-0004) [design].

Reads a prod preview, decides whether it contains a risky change, and either lets the
deploy continue or stops it until an owner of the stack approves this exact preview.

  exit 0  no risky change, or a valid approval matches this preview's hash
  exit 3  risky change and no valid approval: STOP, nothing is applied
  exit 2  the preview could not be read: STOP (fail closed)

What it guards against: risky prod diffs that the PR approver did not see, because on GitHub
Team nobody sees the prod diff before apply (framework §1). It is NOT a boundary against
malicious code that was approved: the stack's own code runs with the deploy role during the
preview and during `pulumi up` (see examples/README.md, "Limits of the risk stop").

Risky (whatever the change level):
  - replace or delete of a stateful resource (data, keys, logs);
  - any change to an IAM, resource-policy or network resource type;
  - any change to an audit or detection resource (CloudTrail, Config, GuardDuty, ...);
  - on any type, a changed property whose NAME looks like access, exposure or logging control
    (policy, role, security group, VPC, public, authorization, principal, KMS key, logging);
    on creates a narrower set (policy, principal, public, ACL, grant, trust, authorization);
  - an operation the classifier does not know;
  - in a pending SQL migration or data-fix file (--tool sql): DROP, TRUNCATE, a column type
    change, DELETE/UPDATE without a top-level WHERE, grants/roles/row-level security, COPY, and
    any function body, DO block or EXECUTE, which cannot be classified. A heuristic, not a
    parser (adapters.py); the hash covers the exact SQL text.
Advisory policy findings join in phase 2 (not implemented here).

Approval (framework layer 3; OD8, OD13): the original author opens a PR that adds
deploy-approvals/<stack>/<stopped-commit>.yaml with `preview_hash`; CODEOWNERS makes an owner of
the stack (or the on-call group) approve it. An approval counts only if, in git history (read from git objects, never the working tree):
  1. the file is named <stopped_commit>.yaml, its `stack` matches the folder, and it was never
     edited after it was added (a changed approval is a new file);
  2. `stopped_commit` and the commit that added the file are both on main's first-parent
     history, the second after the first. With squash-only merges (ruleset-main.json) each PR
     is one first-parent commit, so a PR cannot carry its own risky change and its approval;
  3. that commit changes nothing outside deploy-approvals/<stack>/;
  4. the stack's directory and this classifier are unchanged between `stopped_commit` and
     HEAD: what is deployed is what was stopped and shown to the approver;
  5. that commit is at most MAX_AGE_DAYS older than HEAD.
The deploy also previews again on HEAD and continues only if the hash is the same (Options §1).
Not covered: nothing proves a deploy really stopped at `stopped_commit` with this hash. An
approval merged early, naming a commit whose deploy did not stop, is accepted if a later change
OUTSIDE the stack's directory (a shared library) produces exactly that hash. Closing this needs
the approval-gate app to check the stopped run's hash on the approval PR (gap G19) [design].

The hash covers type, name, operation and a digest of the changed values, leaving out values
that change on every build (adapters.py). The summary shows type, name, operation and changed
property NAMES only: no values, outputs or secrets. So the approver sees WHICH prod resources
and properties change; the values themselves are reviewed in the code of the stopped PR.

Normalized input (produced by adapters.py from the tool's own JSON):
  {"changes": [{"type": "aws:iam/role:Role", "name": "deployer", "op": "update",
                "changed_keys": ["assumeRolePolicy"], "detail_digest": "<sha256>"}]}
  op: create | update | replace | delete | same | <anything else = unknown>
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

import adapters

MAX_AGE_DAYS = 7  # [design]

# Each category lists the Pulumi AWS type prefix and the matching CloudFormation type, side by
# side, so the two tools are covered alike. Examples, not complete [design]; the property-name
# rule below is the safety net for types that are missing here.
STATEFUL_TYPES = [
    ("aws:rds/", "AWS::RDS::"),
    ("aws:s3/bucket:", "AWS::S3::Bucket"),
    ("aws:s3/bucketV2:", "AWS::S3::Bucket"),
    ("aws:dynamodb/table", "AWS::DynamoDB::Table"),
    ("aws:efs/", "AWS::EFS::"),
    ("aws:kms/key:", "AWS::KMS::Key"),
    ("aws:sqs/queue:", "AWS::SQS::Queue"),
    ("aws:sns/topic:", "AWS::SNS::Topic"),
    ("aws:elasticache/", "AWS::ElastiCache::"),
    ("aws:secretsmanager/secret:", "AWS::SecretsManager::Secret"),
    ("aws:cloudwatch/logGroup", "AWS::Logs::LogGroup"),
    ("aws:ec2/instance", "AWS::EC2::Instance"),
    ("aws:ebs/", "AWS::EC2::Volume"),
    ("aws:opensearch/", "AWS::OpenSearchService::"),
    ("aws:backup/", "AWS::Backup::"),
]
ACCESS_TYPES = [
    ("aws:iam/", "AWS::IAM::"),
    ("aws:organizations/", "AWS::Organizations::"),
    ("aws:s3/bucketPolicy", "AWS::S3::BucketPolicy"),
    ("aws:s3/bucketPublicAccessBlock", "AWS::S3::BucketPublicAccessBlock"),
    ("aws:sqs/queuePolicy", "AWS::SQS::QueuePolicy"),
    ("aws:sns/topicPolicy", "AWS::SNS::TopicPolicy"),
    ("aws:lambda/permission", "AWS::Lambda::Permission"),
    ("aws:lambda/functionUrl", "AWS::Lambda::Url"),
    ("aws:kms/keyPolicy", "AWS::KMS::Key"),
    ("aws:kms/grant", "AWS::KMS::Grant"),
    ("aws:secretsmanager/secretPolicy", "AWS::SecretsManager::ResourcePolicy"),
    ("aws:apigateway/", "AWS::ApiGateway::"),
    ("aws:apigatewayv2/", "AWS::ApiGatewayV2::"),
    ("aws:cognito/", "AWS::Cognito::"),
]
NETWORK_TYPES = [
    ("aws:ec2/securityGroup", "AWS::EC2::SecurityGroup"),
    ("aws:vpc/", "AWS::EC2::SecurityGroup"),
    ("aws:ec2/vpc", "AWS::EC2::VPC"),
    ("aws:ec2/subnet", "AWS::EC2::Subnet"),
    ("aws:ec2/routeTable", "AWS::EC2::RouteTable"),
    ("aws:ec2/route:", "AWS::EC2::Route"),
    ("aws:ec2/internetGateway", "AWS::EC2::InternetGateway"),
    ("aws:ec2/natGateway", "AWS::EC2::NatGateway"),
    ("aws:ec2/networkAcl", "AWS::EC2::NetworkAcl"),
    ("aws:ec2/vpcEndpoint", "AWS::EC2::VPCEndpoint"),
    ("aws:ec2/vpcPeeringConnection", "AWS::EC2::VPCPeeringConnection"),
    ("aws:ec2/eip", "AWS::EC2::EIP"),
    ("aws:lb/", "AWS::ElasticLoadBalancingV2::"),
    ("aws:alb/", "AWS::ElasticLoadBalancingV2::"),
    ("aws:cloudfront/", "AWS::CloudFront::"),
    ("aws:route53/", "AWS::Route53::"),
]
AUDIT_TYPES = [
    ("aws:cloudtrail/", "AWS::CloudTrail::"),
    ("aws:cfg/", "AWS::Config::"),
    ("aws:guardduty/", "AWS::GuardDuty::"),
    ("aws:securityhub/", "AWS::SecurityHub::"),
    ("aws:accessanalyzer/", "AWS::AccessAnalyzer::"),
]
# Other providers for the same AWS services (Pulumi AWS Native). Prefix match only [design].
OTHER_PROVIDER_ACCESS = ("aws-native:iam:", "aws-native:organizations:")
OTHER_PROVIDER_NETWORK = ("aws-native:ec2:",)

# Property names that control access or network exposure, checked on updates and replaces...
RISKY_KEY = re.compile(
    r"polic|assumerole|role(arn)?$|^role|securitygroup|vpcconfig|subnet|public|"
    r"authoriz|principal|kmskey|grant|acl$|cors|trust|logging",
    re.IGNORECASE,
)
# ...and a narrower set on creates, so that every new function with an execution role does
# not stop the deploy: a new resource that carries its own policy, grant or public exposure.
RISKY_CREATE_KEY = re.compile(r"polic|principal|public|acl$|grant|trust|authoriz", re.IGNORECASE)
KNOWN_OPS = {"create", "update", "replace", "delete", "same"}

# SQL statement kinds (adapters.sql_kinds) that stop a deploy (framework layer 3, "Database
# changes"; ADR-0011) [design]: data loss, unscoped data changes, access and tenant-isolation
# changes (grants, roles, row-level security), data export, and code that cannot be classified.
SQL_RISKY_KINDS = {
    "drop": "drop", "drop_column": "drop column or constraint", "truncate": "truncate",
    "alter_column_type": "column type change", "delete_unscoped": "DELETE without WHERE",
    "update_unscoped": "UPDATE without WHERE", "privilege": "privilege or role change",
    "row_security": "row-level security change", "copy": "COPY",
    "dynamic_sql": "function body, DO block or EXECUTE (not classified)",
    "metadata": "GraphQL-engine metadata: permissions per role (not classified)",
    "dml_in_migration": "data change (INSERT, UPDATE or DELETE) in a migration, not in data-fixes/<tenant>/",
}


def _matches(rtype, table):
    return any(rtype.startswith(p) or rtype.startswith(c) for p, c in table)


def reasons_for(change):
    t, op = change["type"], change["op"]
    if op == "same":
        return []
    if op not in KNOWN_OPS:
        return [f"unknown operation '{op}'"]
    if t.startswith("sql:"):
        kinds = [SQL_RISKY_KINDS[k] for k in change.get("changed_keys", []) if k in SQL_RISKY_KINDS]
        return ["SQL: " + ", ".join(kinds)] if kinds else []
    out = []
    if op in ("replace", "delete") and _matches(t, STATEFUL_TYPES):
        out.append(f"{op} of a stateful resource")
    if _matches(t, ACCESS_TYPES) or t.startswith(OTHER_PROVIDER_ACCESS):
        out.append("IAM or resource-policy change")
    if _matches(t, NETWORK_TYPES) or t.startswith(OTHER_PROVIDER_NETWORK):
        out.append("network change")
    if _matches(t, AUDIT_TYPES):
        out.append("audit or detection change")
    rule = RISKY_CREATE_KEY if op == "create" else RISKY_KEY
    keys = sorted(k for k in change.get("changed_keys", []) if rule.search(k))
    if keys and op != "delete":
        out.append("access, exposure or logging property: " + ", ".join(keys))
    return out


def preview_hash(changes):
    material = sorted(
        (c["type"], c["name"], c["op"], c.get("detail_digest", ""))
        for c in changes
        if c["op"] != "same" and not c.get("volatile")
    )
    return "sha256:" + hashlib.sha256(json.dumps(material).encode()).hexdigest()


# ---------------------------------------------------------------- approvals

def _git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


def _is_ancestor(repo, a, b):
    return _git(repo, "merge-base", "--is-ancestor", a, b).returncode == 0


def _commit_time(repo, rev):
    out = _git(repo, "show", "-s", "--format=%ct", rev).stdout.strip()
    return datetime.datetime.fromtimestamp(int(out), datetime.timezone.utc)


def _parse_yaml_flat(text):
    fields = {}
    for line in text.splitlines():
        m = re.match(r"^([a-z_]+)\s*:\s*\"?([^\"#]*?)\"?\s*(#.*)?$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip()
    return fields


def check_approval(repo, approvals_dir, name, watched):
    """Return (preview_hash, None) if the approval file is valid, else (None, reason).

    `watched` lists the paths whose content must be the same at the stopped commit and at
    HEAD: the stack's directory and the classifier itself. Everything is read from git
    objects, never from the working tree, so files changed at run time do not count.
    """
    approvals_rel = os.path.relpath(approvals_dir, repo).rstrip("/")
    rel = f"{approvals_rel}/{name}"
    stack = os.path.basename(approvals_rel)
    head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    mainline = set(_git(repo, "rev-list", "--first-parent", "HEAD").stdout.split())
    commits = _git(repo, "log", "--format=%H", "--", rel).stdout.split()
    if not commits:
        return None, "file is not in git history"
    if len(commits) > 1:
        return None, "file was changed after it was added; add a new approval file instead"
    added = commits[0]
    fields = _parse_yaml_flat(_git(repo, "show", f"{added}:{rel}").stdout)
    h, stopped = fields.get("preview_hash", ""), fields.get("stopped_commit", "")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", h):
        return None, "no valid preview_hash"
    if not re.fullmatch(r"[0-9a-f]{40}", stopped):
        return None, "no valid stopped_commit"
    if name.rsplit(".", 1)[0] != stopped or fields.get("stack") != stack:
        return None, "file name must be <stopped_commit>.yaml and `stack` must match the folder"
    if stopped == head or stopped not in mainline:
        return None, "stopped_commit is not an earlier commit on main's first-parent history"
    if added not in mainline or added == stopped or not _is_ancestor(repo, stopped, added):
        return None, "approval was not merged to main after stopped_commit"
    touched = _git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", f"{added}^1", added).stdout.split()
    if any(not p.startswith(approvals_rel + "/") for p in touched):
        return None, "the commit that added it also changes files outside " + approvals_rel + "/"
    changed = _git(repo, "diff", "--name-only", stopped, head, "--", *watched).stdout.split()
    if changed:
        return None, "code changed since stopped_commit: " + ", ".join(sorted(changed)[:5])
    # Measured against the later of HEAD's commit time and the wall clock, so re-running an
    # old run does not keep an approval alive.
    now = max(_commit_time(repo, head), datetime.datetime.now(datetime.timezone.utc))
    age = now - _commit_time(repo, added)
    if age > datetime.timedelta(days=MAX_AGE_DAYS):
        return None, f"older than {MAX_AGE_DAYS} days"
    return h, None


def read_approvals(repo, approvals_dir, watched):
    """Return ({preview_hash: file}, [(file, reason) for rejected files])."""
    valid, rejected = {}, []
    if not os.path.isdir(approvals_dir):
        return valid, rejected
    for name in sorted(os.listdir(approvals_dir)):
        if name.endswith((".yaml", ".yml")):
            h, why = check_approval(repo, approvals_dir, name, watched)
            if h:
                valid[h] = name
            else:
                rejected.append((name, why))
    return valid, rejected


# ---------------------------------------------------------------- decision

def decide(normalized, approvals):
    changes = normalized["changes"]
    risky = [(c, r) for c in changes for r in [reasons_for(c)] if r]
    h = preview_hash(changes)
    if not risky:
        return 0, h, risky, None
    if h in approvals:
        return 0, h, risky, approvals[h]
    return 3, h, risky, None


def summary_text(code, h, risky, approved_by_file, rejected=()):
    lines = ["# Risk stop", "", f"Preview hash: `{h}`", ""]
    if not risky:
        lines.append("No risky change. Deploy continues.")
    elif code == 0:
        lines.append(f"Risky changes approved by `{approved_by_file}` (hash matches). Deploy continues.")
    else:
        lines += [
            "**Deploy stopped.** Risky changes need an approval from an owner of this stack:",
            "open a PR that adds only `deploy-approvals/<stack>/<this commit>.yaml` with the hash above.",
        ]
    if risky:
        lines += ["", "| Type | Name | Operation | Why |", "|---|---|---|---|"]
        for c, r in risky:
            lines.append(f"| `{c['type']}` | `{c['name']}` | {c['op']} | {'; '.join(r)} |")
    if rejected:
        lines += ["", "Approval files not accepted:"]
        lines += [f"- `{n}`: {why}" for n, why in rejected]
    return "\n".join(lines) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--tool", required=True, choices=["pulumi", "serverless", "sql", "normalized"])
    p.add_argument("--preview", required=True)
    p.add_argument("--approvals", required=True, help="deploy-approvals/<stack> directory")
    p.add_argument("--repo", default=".", help="git checkout with full history")
    p.add_argument("--workdir", required=True,
                   help="stack directory, relative to --repo; must be unchanged since the stopped commit")
    p.add_argument("--summary", help="write the markdown summary here as well")
    a = p.parse_args(argv)
    try:
        with open(a.preview) as f:
            raw = json.load(f)
        normalized = adapters.ADAPTERS[a.tool](raw)
    except Exception as e:  # fail closed
        print(f"risk-stop: cannot read preview ({type(e).__name__}: {e}); stopping", file=sys.stderr)
        return 2
    classifier_dir = os.path.relpath(os.path.dirname(os.path.abspath(__file__)), os.path.abspath(a.repo))
    watched = [a.workdir] + ([classifier_dir] if not classifier_dir.startswith("..") else [])
    approvals, rejected = read_approvals(a.repo, a.approvals, watched)
    code, h, risky, approved = decide(normalized, approvals)
    text = summary_text(code, h, risky, approved, rejected)
    print(text)
    for path in filter(None, [a.summary, os.environ.get("GITHUB_STEP_SUMMARY")]):
        with open(path, "a") as f:
            f.write(text)
    return code


if __name__ == "__main__":
    sys.exit(main())
