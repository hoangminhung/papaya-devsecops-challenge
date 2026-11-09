"""E7: risk stop classifier (examples/risk-stop/).

Proves the [design] logic: what stops a deploy (per category, for Pulumi and CloudFormation
types alike), that an approval counts only for the exact preview and only with the git
history the framework's flow produces, and that the summary carries no property values.

Approval tests build a throwaway git repository, because the approval rules are about history:
the stopped commit must be an ancestor of HEAD, the approval must be added later by a commit
that touches only deploy-approvals/<stack>/, and it must be recent.

Does NOT prove: the real JSON shape of `pulumi preview --json` / `serverless diff --json`
(adapters are ⚠️ assumptions, fixtures are hand-written), nor that a real preview gives the
same hash twice for unchanged code (⚠️ Options §8).
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

HERE = os.path.dirname(__file__)
RS = os.path.join(HERE, "..", "risk-stop")
sys.path.insert(0, RS)
import adapters  # noqa: E402
import classify  # noqa: E402


def fixture(name):
    return os.path.join(RS, "fixtures", name)


def load(name):
    with open(fixture(name)) as f:
        return json.load(f)


def run(tool, preview, approvals, repo=".", workdir="infra"):
    out = io.StringIO()
    env_summary = os.environ.pop("GITHUB_STEP_SUMMARY", None)
    try:
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            code = classify.main(["--tool", tool, "--preview", preview,
                                  "--approvals", approvals, "--repo", repo, "--workdir", workdir])
    finally:
        if env_summary is not None:
            os.environ["GITHUB_STEP_SUMMARY"] = env_summary
    return code, out.getvalue()


def risky(change):
    return bool(classify.reasons_for(change))


class Repo:
    """A throwaway git repository with a fixed identity (no real person)."""

    def __init__(self, path):
        self.path = path
        self.git("init", "-q", "-b", "main")
        self.date = 1_800_000_000  # fixed clock, advanced per commit

    def git(self, *args, env=None):
        full_env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull,
                        GIT_AUTHOR_NAME="test", GIT_AUTHOR_EMAIL="test@example.invalid",
                        GIT_COMMITTER_NAME="test", GIT_COMMITTER_EMAIL="test@example.invalid")
        full_env.update(env or {})
        r = subprocess.run(["git", "-C", self.path, *args], capture_output=True, text=True, env=full_env)
        if r.returncode:
            raise RuntimeError(r.stderr)
        return r.stdout.strip()

    def commit(self, files, msg, days_later=0):
        for rel, content in files.items():
            p = os.path.join(self.path, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                f.write(content)
        self.git("add", "-A")
        self.date += 60 + days_later * 86400
        stamp = f"@{self.date} +0000"
        self.git("commit", "-q", "-m", msg, env={"GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp})
        return self.git("rev-parse", "HEAD")


def approval_yaml(stopped, h):
    return f"stack: claims-data\nstopped_commit: {stopped}\npreview_hash: {h}\n"


class ClassificationTest(unittest.TestCase):
    def test_benign_change_continues(self):
        self.assertEqual(run("normalized", fixture("normalized-benign.json"), "/nonexistent")[0], 0)

    def test_iam_change_stops(self):
        code, out = run("normalized", fixture("normalized-iam.json"), "/nonexistent")
        self.assertEqual(code, 3)
        self.assertIn("IAM", out)

    def test_stateful_replace_stops(self):
        self.assertEqual(run("normalized", fixture("normalized-stateful-delete.json"), "/nonexistent")[0], 3)

    def test_categories_for_both_tools(self):
        cases = [
            # (type, op, changed_keys) -> must be risky
            ("aws:iam/role:Role", "update", []), ("AWS::IAM::Role", "update", []),
            ("aws:ec2/securityGroup:SecurityGroup", "update", []), ("AWS::EC2::SecurityGroup", "update", []),
            ("aws:apigateway/method:Method", "update", []), ("AWS::ApiGateway::Method", "update", []),
            ("aws:apigatewayv2/route:Route", "update", []), ("AWS::ApiGatewayV2::Route", "update", []),
            ("aws:lambda/functionUrl:FunctionUrl", "create", []), ("AWS::Lambda::Url", "create", []),
            ("aws:sns/topicPolicy:TopicPolicy", "update", []), ("AWS::SNS::TopicPolicy", "update", []),
            ("aws:s3/bucketPublicAccessBlock:BucketPublicAccessBlock", "update", []),
            ("AWS::S3::BucketPublicAccessBlock", "update", []),
            ("aws:cloudwatch/logGroup:LogGroup", "delete", []), ("AWS::Logs::LogGroup", "delete", []),
            ("aws:ec2/instance:Instance", "delete", []), ("AWS::EC2::Instance", "delete", []),
            ("aws:rds/cluster:Cluster", "replace", []), ("AWS::RDS::DBCluster", "replace", []),
            # inline policies and roles on types that are not in any list
            ("aws:kms/key:Key", "update", ["policy"]), ("aws:sqs/queue:Queue", "update", ["policy"]),
            ("aws:ecs/taskDefinition:TaskDefinition", "update", ["taskRoleArn"]),
            ("AWS::ECS::TaskDefinition", "update", ["TaskRoleArn"]),
            ("aws:lambda/function:Function", "update", ["vpcConfig"]),
            ("AWS::Lambda::Function", "update", ["Role"]),
        ]
        for t, op, keys in cases:
            with self.subTest(type=t, op=op, keys=keys):
                self.assertTrue(risky({"type": t, "name": "x", "op": op, "changed_keys": keys}))

    def test_routine_changes_are_not_risky(self):
        for t, op, keys in [
            ("aws:lambda/function:Function", "update", ["timeout", "memorySize"]),
            ("AWS::Lambda::Function", "update", ["Timeout", "MemorySize"]),
            ("aws:ecs/service:Service", "update", ["desiredCount"]),
            ("AWS::Lambda::Version", "delete", []),  # replaced on every Serverless code change
            ("aws:sqs/queue:Queue", "update", ["visibilityTimeoutSeconds"]),
        ]:
            with self.subTest(type=t):
                self.assertFalse(risky({"type": t, "name": "x", "op": op, "changed_keys": keys}))

    def test_unknown_operation_stops(self):
        self.assertTrue(risky({"type": "aws:lambda/function:Function", "name": "f", "op": "import"}))

    def test_unreadable_preview_fails_closed(self):
        tmp = tempfile.mkdtemp()
        try:
            p = os.path.join(tmp, "bad.json")
            with open(p, "w") as f:
                f.write("{not json")
            self.assertEqual(run("pulumi", p, "/nonexistent")[0], 2)
            with open(p, "w") as f:
                json.dump({"unexpected": []}, f)
            self.assertEqual(run("pulumi", p, "/nonexistent")[0], 2)
        finally:
            shutil.rmtree(tmp)

    def test_summary_has_no_property_values(self):
        code, out = run("pulumi", fixture("pulumi-preview.json"), "/nonexistent")
        self.assertEqual(code, 3)  # S3 bucket replaced
        self.assertNotIn("PLACEHOLDER-SECRET-LIKE-VALUE", out)
        self.assertNotIn("2048", out)

    def test_serverless_adapter_iam_stops(self):
        code, out = run("serverless", fixture("serverless-diff.json"), "/nonexistent")
        self.assertEqual(code, 3)
        self.assertIn("AWS::IAM::Role", out)

    def test_serverless_hash_ignores_build_volatile_values(self):
        a = {"resources": [
            {"logicalId": "FnLambdaFunction", "type": "AWS::Lambda::Function", "action": "modify",
             "properties": {"Code": {"S3Key": "serverless/svc/prod/1700000000000/fn.zip"}, "Role": "arn-a"}},
            {"logicalId": "FnLambdaVersionAAAA", "type": "AWS::Lambda::Version", "action": "add", "properties": {}}]}
        b = json.loads(json.dumps(a))
        b["resources"][0]["properties"]["Code"]["S3Key"] = "serverless/svc/prod/1700000099999/fn.zip"
        b["resources"][1]["logicalId"] = "FnLambdaVersionBBBB"
        ha = classify.preview_hash(adapters.serverless(a)["changes"])
        hb = classify.preview_hash(adapters.serverless(b)["changes"])
        self.assertEqual(ha, hb)
        b["resources"][0]["properties"]["Role"] = "arn-b"
        self.assertNotEqual(ha, classify.preview_hash(adapters.serverless(b)["changes"]))


class ApprovalTest(unittest.TestCase):
    """The approval flow of framework layer 3, against real git history."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.repo = Repo(self.tmp)
        self.preview = fixture("normalized-iam.json")
        self.h = classify.preview_hash(load("normalized-iam.json")["changes"])
        self.appr_dir = os.path.join(self.tmp, "deploy-approvals", "claims-data")
        self.base = self.repo.commit({"infra/a.ts": "v1"}, "base")
        self.stopped = self.repo.commit({"infra/a.ts": "v2 iam change"}, "risky change, deploy stopped")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def approve(self, stopped=None, h=None, extra=None, days_later=0):
        files = {f"deploy-approvals/claims-data/{stopped or self.stopped}.yaml":
                 approval_yaml(stopped or self.stopped, h or self.h)}
        files.update(extra or {})
        return self.repo.commit(files, "approval", days_later=days_later)

    def result(self, preview=None):
        return run("normalized", preview or self.preview, self.appr_dir, repo=self.tmp)

    def test_valid_approval_continues(self):
        self.approve()
        code, out = self.result()
        self.assertEqual(code, 0, out)
        self.assertIn("approved by", out)

    def test_no_approval_stops(self):
        self.assertEqual(self.result()[0], 3)

    def test_approval_in_the_same_commit_as_the_change_is_rejected(self):
        # One PR carries both the risky change and an approval with a predicted hash,
        # naming an older commit as "stopped".
        self.approve(stopped=self.base, extra={"infra/a.ts": "v3 another iam change"})
        code, out = self.result()
        self.assertEqual(code, 3)
        self.assertIn("changes files outside", out)

    def test_approval_naming_a_commit_not_on_main_is_rejected(self):
        fake = "f" * 40
        self.repo.commit({f"deploy-approvals/claims-data/{fake}.yaml": approval_yaml(fake, self.h)}, "x")
        code, out = self.result()
        self.assertEqual(code, 3)
        self.assertIn("first-parent", out)

    def test_old_approval_is_not_replayed(self):
        self.approve(days_later=0)
        self.repo.commit({"docs/notes.md": "unrelated"}, "later work", days_later=classify.MAX_AGE_DAYS + 1)
        code, out = self.result()
        self.assertEqual(code, 3)
        self.assertIn("older than", out)

    def test_approval_does_not_cover_a_different_iam_change(self):
        self.approve()
        doc = load("normalized-iam.json")
        doc["changes"][1]["detail_digest"] = "policy-version-B"
        p = os.path.join(self.tmp, "b.json")
        with open(p, "w") as f:
            json.dump(doc, f)
        self.assertEqual(self.result(p)[0], 3)

    def test_change_merged_in_between_stops_again(self):
        self.approve()
        doc = load("normalized-iam.json")
        doc["changes"].append({"type": "aws:sqs/queue:Queue", "name": "x", "op": "update", "detail_digest": "z"})
        p = os.path.join(self.tmp, "later.json")
        with open(p, "w") as f:
            json.dump(doc, f)
        self.assertEqual(self.result(p)[0], 3)

    def test_edited_approval_file_is_rejected(self):
        # A legitimately added approval for another hash is edited by a later PR that also
        # carries a new risky change (round-2 review H1).
        self.approve(h="sha256:" + "0" * 64)
        rel = f"deploy-approvals/claims-data/{self.stopped}.yaml"
        self.repo.commit({rel: approval_yaml(self.stopped, self.h), "infra/a.ts": "v3 risky"}, "edit + change")
        code, out = self.result()
        self.assertEqual(code, 3)
        self.assertIn("changed after it was added", out)

    def test_working_tree_edit_is_ignored(self):
        # Code running in the job rewrites the approval on disk; git objects are what count.
        self.approve(h="sha256:" + "0" * 64)
        with open(os.path.join(self.appr_dir, f"{self.stopped}.yaml"), "w") as f:
            f.write(approval_yaml(self.stopped, self.h))
        self.assertEqual(self.result()[0], 3)

    def test_pr_merged_with_a_merge_commit_cannot_approve_itself(self):
        # One PR: C1 risky change, C2 approval only; landed with a merge commit (review H2).
        self.repo.git("checkout", "-q", "-b", "feature", self.stopped)
        c1 = self.repo.commit({"infra/a.ts": "v3 risky"}, "C1")
        self.repo.commit({f"deploy-approvals/claims-data/{c1}.yaml": approval_yaml(c1, self.h)}, "C2")
        self.repo.git("checkout", "-q", "main")
        self.repo.git("merge", "-q", "--no-ff", "-m", "merge feature", "feature",
                      env={"GIT_AUTHOR_DATE": f"@{self.repo.date + 60} +0000",
                           "GIT_COMMITTER_DATE": f"@{self.repo.date + 60} +0000"})
        code, out = self.result()
        self.assertEqual(code, 3)
        self.assertIn("first-parent", out)

    def test_approval_merged_before_the_risky_change_is_rejected(self):
        # PR Y adds an approval naming the current tip; PR X then merges the risky change (M1).
        tip = self.stopped
        self.repo.commit({f"deploy-approvals/claims-data/{tip}.yaml": approval_yaml(tip, self.h)}, "Y")
        self.repo.commit({"infra/a.ts": "v3 risky change from X"}, "X")
        code, out = self.result()
        self.assertEqual(code, 3)
        self.assertIn("code changed since stopped_commit", out)

    def test_approval_added_on_a_side_branch_is_rejected(self):
        # stopped_commit is on main, but the approval reached main only inside a merge commit.
        self.repo.git("checkout", "-q", "-b", "side", self.stopped)
        self.repo.commit({f"deploy-approvals/claims-data/{self.stopped}.yaml":
                          approval_yaml(self.stopped, self.h)}, "approval on side branch")
        self.repo.git("checkout", "-q", "main")
        self.repo.git("merge", "-q", "--no-ff", "-m", "merge side", "side",
                      env={"GIT_AUTHOR_DATE": f"@{self.repo.date + 60} +0000",
                           "GIT_COMMITTER_DATE": f"@{self.repo.date + 60} +0000"})
        code, out = self.result()
        self.assertEqual(code, 3)
        self.assertIn("not merged to main", out)

    def test_known_gap_early_approval_and_change_outside_the_stack(self):
        # Documents a gap that is NOT closed (README "Limits", classify.py docstring): an
        # approval merged early, naming a commit whose deploy did not stop, is accepted when a
        # later change outside the stack's directory produces the approved hash.
        tip = self.stopped
        self.repo.commit({f"deploy-approvals/claims-data/{tip}.yaml": approval_yaml(tip, self.h)}, "early")
        self.repo.commit({"libs/shared.ts": "changes what the stack deploys"}, "outside the stack")
        self.assertEqual(self.result()[0], 0)

    def test_file_name_and_stack_must_match(self):
        rel = "deploy-approvals/claims-data/not-the-sha.yaml"
        self.repo.commit({rel: approval_yaml(self.stopped, self.h)}, "bad name")
        self.assertEqual(self.result()[0], 3)

    def test_uncommitted_approval_file_is_rejected(self):
        os.makedirs(self.appr_dir, exist_ok=True)
        with open(os.path.join(self.appr_dir, "dropped-at-runtime.yaml"), "w") as f:
            f.write(approval_yaml(self.stopped, self.h))
        self.assertEqual(self.result()[0], 3)


if __name__ == "__main__":
    unittest.main()
