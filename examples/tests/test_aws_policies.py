"""E4 OIDC trust policies, E5 SCP for the prod OU, E6 `ProdReadMetadata` permission set,
E4b per-stack deploy-role limits and the service-role permissions boundary (OD22).

Checked offline against AWS's Service Authorization Reference (schemas/aws-actions.json,
fetched by tools/fetch_aws_actions.py): every action must exist (catches typos), wildcards are
expanded before the checks, and the permission set may hold no action AWS marks as a write.

Not checked: that AWS accepts the policies (IAM Access Analyzer `validate-policy` is an AWS API
call, and this repository touches no live system), nor how they evaluate together with other
policies. The data-read action list is a partial list (gap G13).
"""
import fnmatch
import json
import os
import re
import unittest

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")


def load(*parts):
    with open(os.path.join(ROOT, *parts)) as f:
        return json.load(f)


CATALOGUE = load("schemas", "aws-actions.json")["services"]

# Reads of customer data or secrets: never in ProdReadMetadata, in any form (G13: partial).
DATA_READS = [
    "s3:GetObject", "s3:GetObjectVersion", "s3:GetObjectAttributes", "s3:GetObjectTorrent",
    "sqs:ReceiveMessage", "states:GetExecutionHistory", "states:DescribeExecution",
    "secretsmanager:GetSecretValue", "ssm:GetParameter", "ssm:GetParameters",
    "ssm:GetParametersByPath", "kms:Decrypt", "dynamodb:GetItem", "dynamodb:BatchGetItem",
    "dynamodb:Query", "dynamodb:Scan", "rds-data:ExecuteStatement", "lambda:InvokeFunction",
    "lambda:GetFunction", "lambda:ListFunctions", "ecs:ExecuteCommand", "ecs:DescribeTaskDefinition",
    "cloudformation:DescribeStacks", "cloudformation:GetTemplate", "logs:Unmask",
    "xray:GetTraceSummaries", "xray:BatchGetTraces", "ssm:GetParameterHistory",
    "secretsmanager:BatchGetSecretValue", "rds:DownloadDBLogFilePortion", "rds:DownloadCompleteDBLogFile",
    "ecs:DescribeTasks", "s3:GetObjectVersionTorrent", "states:StartSyncExecution",
    "lambda:ListVersionsByFunction", "ec2:DescribeLaunchTemplateVersions", "ec2:DescribeInstanceAttribute",
    "ssm:ListCommandInvocations", "s3:ListBucket", "xray:ListRetrievedTraces", "rds:DescribeDBLogFiles",
    "cloudformation:DescribeStackEvents",  # ResourceProperties holds creation properties (📖 StackEvent)
    "logs:DescribeQueries",  # other users' query strings, which may contain identifiers (⚠️)
]
# Claim-store data access that the prod-OU SCP must deny to everyone but app/data-read roles:
# reads, plus `sqs:StartMessageMoveTask` (a write, ✅ catalogue) because it can move claim messages
# to a queue with another name. Cost: JIT roles cannot redrive a claims DLQ in an incident.
SCP_CLAIM_DATA_READS = [
    "s3:GetObject", "s3:GetObjectVersion", "s3:GetObjectTorrent", "s3:GetObjectVersionTorrent",
    "sqs:ReceiveMessage", "states:GetExecutionHistory", "states:DescribeExecution",
    "states:StartSyncExecution", "sqs:StartMessageMoveTask",
]
# The ONLY actions allowed with `Resource: "*"` (layer 1), each reviewed as returning metrics or
# metadata, not customer data, secrets or environment variables. AWS's IsList annotation is not
# trusted on its own: many IsList actions return data (review round 2 of step 2). Adding an
# action here is a reviewed change.
REVIEWED_METADATA = {
    "cloudwatch:GetMetricData", "cloudwatch:GetMetricStatistics", "cloudwatch:ListMetrics",
    "cloudwatch:DescribeAlarms", "cloudwatch:DescribeAlarmHistory",
    "logs:DescribeLogGroups", "logs:DescribeLogStreams",
    "ecs:ListClusters", "ecs:ListServices", "ecs:ListTasks", "ecs:DescribeClusters", "ecs:DescribeServices",
    "sqs:ListQueues", "sqs:GetQueueAttributes", "sqs:ListDeadLetterSourceQueues",
    "states:ListStateMachines", "states:DescribeStateMachine",
    "states:ListExecutions",  # execution names: must not be built from claim data (⚠️, finding 12)
    "rds:DescribeDBClusters", "rds:DescribeDBInstances", "rds:DescribeEvents",
    "sns:ListTopics", "cloudformation:ListStacks",
    "cloudformation:DescribeStackResources", "health:DescribeEvents",
    "ec2:DescribeInstances", "elasticloadbalancing:DescribeTargetGroups",
    "elasticloadbalancing:DescribeTargetHealth", "lambda:ListEventSourceMappings",
    "lambda:GetFunctionConcurrency",
}
# Exact exemptions in the SCP [design names; Identity Center ARN forms 📖 referencingpermissionsets].
SSO = "arn:aws:iam::*:role/aws-reserved/sso.amazonaws.com/"
LAMBDA_EXEMPT = [
    "arn:aws:iam::*:role/cfn-deployment-*",
    "arn:aws:iam::*:role/github-prod-deploy-pulumi",
    SSO + "AWSReservedSSO_InfraOperator-*",
    SSO + "*/AWSReservedSSO_InfraOperator-*",
]
DATA_EXEMPT = [
    "arn:aws:iam::*:role/app-claims-*",
    SSO + "AWSReservedSSO_DataRead-*",
    SSO + "*/AWSReservedSSO_DataRead-*",
]
TRAIL_ACTIONS = [
    "cloudtrail:StopLogging", "cloudtrail:DeleteTrail", "cloudtrail:UpdateTrail",
    "cloudtrail:PutEventSelectors", "cloudtrail:PutInsightSelectors",
    "cloudtrail:DeleteEventDataStore", "cloudtrail:StopEventDataStoreIngestion",
    "cloudtrail:UpdateEventDataStore",
]
PROTECTED_ROLE_ACTIONS = [
    "iam:CreateRole", "iam:DeleteRole", "iam:UpdateAssumeRolePolicy", "iam:PutRolePolicy",
    "iam:AttachRolePolicy", "iam:DeleteRolePolicy", "iam:DetachRolePolicy",
    "iam:PutRolePermissionsBoundary", "iam:DeleteRolePermissionsBoundary", "iam:UpdateRole",
]
PROTECTED_ROLE_NAMES = [
    "arn:aws:iam::*:role/app-claims-*", "arn:aws:iam::*:role/cfn-deployment-*",
    "arn:aws:iam::*:role/github-prod-deploy-*",
]
# OD22: per-stack deploy roles [design names].
IAM_STACK_ROLE = "arn:aws:iam::*:role/github-prod-deploy-iam"
BOUNDARY_NAME = "app-permissions-boundary"
BOUNDARY_POLICY_ACTIONS = [
    "iam:CreatePolicyVersion", "iam:DeletePolicy", "iam:DeletePolicyVersion", "iam:SetDefaultPolicyVersion",
]
ROLE_PERMISSION_CHANGES = [
    "iam:CreateRole", "iam:PutRolePolicy", "iam:DeleteRolePolicy", "iam:AttachRolePolicy",
    "iam:DetachRolePolicy", "iam:PutRolePermissionsBoundary",
]
# Reads that may show raw logs or configuration: only with per-service ARNs (layer 1).
PER_SERVICE_ONLY = [
    "logs:GetLogEvents", "logs:FilterLogEvents", "logs:StartQuery", "logs:GetQueryResults",
    "logs:GetLogRecord", "logs:StartLiveTail", "lambda:GetFunctionConfiguration",
]


def expand(action):
    """Expand an IAM action pattern (e.g. logs:Get*) to concrete actions in the catalogue."""
    if action == "*":
        return [f"{s}:{a}" for s, acts in CATALOGUE.items() for a in acts]
    svc, name = action.split(":", 1)
    acts = CATALOGUE.get(svc, {})
    return [f"{svc}:{a}" for a in acts if fnmatch.fnmatchcase(a.lower(), name.lower())]


def as_list(x):
    return x if isinstance(x, list) else [x]


class TrustPolicyTest(unittest.TestCase):
    # Immutable subject format (R3.4.4; environment form inferred, ⚠️ R3.7 A2).
    SUB = r"^repo:example-org@<ORG_ID>/monorepo@<REPO_ID>:"

    def check(self, name, suffix, account):
        doc = load("aws", name)
        [st] = doc["Statement"]
        self.assertEqual(st["Effect"], "Allow")
        self.assertEqual(st["Action"], "sts:AssumeRoleWithWebIdentity")
        self.assertEqual(st["Principal"]["Federated"],
                         f"arn:aws:iam::{account}:oidc-provider/token.actions.githubusercontent.com")
        cond = st["Condition"]
        self.assertEqual(list(cond), ["StringEquals"], "no StringLike / wildcard operators")
        eq = cond["StringEquals"]
        self.assertEqual(eq["token.actions.githubusercontent.com:aud"], "sts.amazonaws.com")
        sub = eq["token.actions.githubusercontent.com:sub"]
        self.assertIsInstance(sub, str, "one subject, not a list")
        self.assertRegex(sub, self.SUB + re.escape(suffix) + "$")
        self.assertNotRegex(sub, r"[*?]")

    def test_prod_deploy_trusts_only_the_production_environment(self):
        self.check("oidc-trust-prod-deploy.json", "environment:production", "<AWS_ACCOUNT_ID>")

    def test_iam_stack_role_trusts_only_the_production_iam_environment(self):
        # OD22: a domain stack's job (environment `production`) cannot obtain this role.
        self.check("oidc-trust-prod-iam-deploy.json", "environment:production-iam", "<AWS_ACCOUNT_ID>")

    def test_db_change_role_trusts_only_the_production_db_environment(self):
        # ADR-0011: a domain stack's job (environment `production`) cannot start the db-change task.
        self.check("oidc-trust-prod-db-change.json", "environment:production-db", "<AWS_ACCOUNT_ID>")

    def test_evidence_export_trusts_only_the_evidence_environment(self):
        # OD30: role in the log-archive account; PutObject only (EvidenceArchiveTest).
        self.check("oidc-trust-evidence-export.json", "environment:evidence", "<LOG_ARCHIVE_ACCOUNT_ID>")

    def test_nonprod_preview_trusts_pull_requests_in_the_nonprod_account(self):
        self.check("oidc-trust-nonprod-preview.json", "pull_request", "<NONPROD_AWS_ACCOUNT_ID>")


class ScpTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = load("aws", "scp-prod-ou.json")
        with open(os.path.join(ROOT, "aws", "scp-prod-ou.json")) as f:
            cls.raw = f.read()
        cls.by_sid = {s["Sid"]: s for s in cls.doc["Statement"]}

    def test_size_within_scp_limit(self):
        # 10,240 characters (R2.3.4). Whether whitespace counts is unverified, so both forms.
        self.assertLessEqual(len(json.dumps(self.doc, separators=(",", ":"))), 10240)
        self.assertLessEqual(len(self.raw), 10240)

    def test_deny_only(self):
        for st in self.doc["Statement"]:
            self.assertEqual(st["Effect"], "Deny", st["Sid"])

    def test_actions_exist(self):
        for st in self.doc["Statement"]:
            for a in as_list(st["Action"]):
                if a != "*":
                    self.assertTrue(expand(a), f"unknown action {a}")

    def test_condition_keys_are_documented_ones(self):
        allowed = {"aws:PrincipalArn", "identitystore:UserId"}  # R2.3.8
        for st in self.doc["Statement"]:
            for op in st.get("Condition", {}).values():
                self.assertLessEqual(set(op), allowed, st["Sid"])

    def test_lambda_updates_only_by_deploy_and_jit_roles(self):
        st = self.by_sid["LambdaChangesOnlyThroughDeployAndJitRoles"]
        self.assertEqual(sorted(st["Action"]),
                         ["lambda:UpdateFunctionCode", "lambda:UpdateFunctionConfiguration"])
        self.assertEqual(st["Condition"]["ArnNotLike"]["aws:PrincipalArn"], LAMBDA_EXEMPT)
        # The Serverless deploy role is NOT exempt: it only passes the CloudFormation role.
        self.assertNotIn("serverless", json.dumps(st).lower())

    def test_revocation_deny_is_predeployed(self):
        st = self.by_sid["RevokedIdentityCenterUsers"]
        self.assertEqual((st["Action"], st["Resource"]), ("*", "*"))
        ids = st["Condition"]["StringEquals"]["identitystore:UserId"]
        self.assertTrue(ids, "the pre-deployed list holds at least a placeholder (R2.4.4)")

    def test_claim_data_reads_only_by_app_and_data_read_roles(self):
        st = self.by_sid["ClaimDataReadsOnlyByAppAndApprovedDataReadRoles"]
        self.assertLessEqual(set(SCP_CLAIM_DATA_READS), set(st["Action"]))
        self.assertEqual(st["Condition"]["ArnNotLike"]["aws:PrincipalArn"], DATA_EXEMPT)

    def test_exempt_role_names_are_protected(self):
        st = self.by_sid["ExemptRoleNamesOnlyChangedByTheIamStack"]
        self.assertEqual(st["Resource"], PROTECTED_ROLE_NAMES)
        self.assertEqual(sorted(st["Action"]), sorted(PROTECTED_ROLE_ACTIONS))
        self.assertNotIn("iam:PassRole", st["Action"])  # the Serverless role must pass cfn-deployment-*
        # OD22: the IAM stack's own role, no longer the shared Pulumi role (was OD19's interim).
        self.assertEqual(st["Condition"]["ArnNotLike"]["aws:PrincipalArn"], [IAM_STACK_ROLE])
        # every exempt name in the other statements is covered by a protected pattern
        exempt = LAMBDA_EXEMPT + DATA_EXEMPT
        for arn in exempt:
            if "aws-reserved" in arn:
                continue  # Identity Center roles: only Identity Center can create them
            self.assertTrue(any(fnmatch.fnmatchcase(arn, p) for p in PROTECTED_ROLE_NAMES), arn)

    def test_trail_tampering_denied(self):
        st = self.by_sid["NoTamperingWithTrailsInProdAccounts"]
        self.assertEqual(sorted(st["Action"]), sorted(TRAIL_ACTIONS))

    def test_boundary_policy_only_changed_by_the_iam_stack(self):
        st = self.by_sid["BoundaryPolicyOnlyChangedByTheIamStack"]
        self.assertEqual(sorted(st["Action"]), sorted(BOUNDARY_POLICY_ACTIONS))
        self.assertEqual(st["Resource"], "arn:aws:iam::*:policy/" + BOUNDARY_NAME)
        self.assertEqual(st["Condition"]["ArnNotLike"]["aws:PrincipalArn"], [IAM_STACK_ROLE])

    def test_organization_access_role_cannot_act_in_prod(self):
        # F7: the role Organizations creates with full admin rights (R9.2.4) is denied in the prod
        # OU; break-glass use needs an SCP change from the management account (an L3 path).
        st = self.by_sid["NoOrganizationAccountAccessRoleInProd"]
        self.assertEqual((st["Action"], st["Resource"]), ("*", "*"))
        self.assertEqual(st["Condition"],
                         {"ArnLike": {"aws:PrincipalArn": ["arn:aws:iam::*:role/OrganizationAccountAccessRole"]}})


class EvidenceArchiveTest(unittest.TestCase):
    """OD30: the nightly evidence export may only add objects to a bucket under Object Lock."""

    def test_role_can_only_put_objects(self):
        [st] = load("aws", "evidence-export-role-policy.json")["Statement"]
        self.assertEqual((st["Effect"], st["Action"]), ("Allow", "s3:PutObject"))
        self.assertTrue(expand(st["Action"]))
        self.assertTrue(st["Resource"].endswith("/github/*"))

    def test_compliance_mode_six_years(self):
        lock = load("aws", "evidence-bucket-object-lock.json")
        self.assertEqual(lock["ObjectLockEnabled"], "Enabled")
        retention = lock["Rule"]["DefaultRetention"]
        self.assertEqual(retention["Mode"], "COMPLIANCE")  # not even root can shorten it (R9.2.12)
        self.assertGreaterEqual(retention.get("Years", 0), 6)  # HIPAA documentation rule (R5.2.9)


class LogMaskingTest(unittest.TestCase):
    """OD28: masking for log groups ProdReadMetadata reads. Custom identifiers only (R9.2.8),
    at most 10, each regex at most 200 characters (R9.2.9). Checked with Python's `re`, which is
    close to, not the same as, the engine CloudWatch uses (⚠️)."""

    @classmethod
    def setUpClass(cls):
        cls.doc = load("aws", "logs-data-protection-policy.json")
        cls.ids = {i["Name"]: re.compile(i["Regex"]) for i in cls.doc["Configuration"]["CustomDataIdentifier"]}

    def test_limits(self):
        custom = self.doc["Configuration"]["CustomDataIdentifier"]
        self.assertLessEqual(len(custom), 10)
        for i in custom:
            self.assertLessEqual(len(i["Regex"]), 200, i["Name"])

    def test_audit_and_mask_cover_every_identifier(self):
        by_sid = {st["Sid"]: st for st in self.doc["Statement"]}
        self.assertEqual(set(by_sid["audit"]["DataIdentifier"]), set(self.ids))
        self.assertEqual(set(by_sid["mask"]["DataIdentifier"]), set(self.ids))
        self.assertIn("Deidentify", by_sid["mask"]["Operation"])

    def test_structured_log_fields_are_caught(self):
        # Synthetic values only. The A-1b case: a handler logs the whole event as JSON.
        line = ('{"claim_id":"C-1","national_id":"012345678901","hkid":"A123456(7)",'
                '"bank_account":"0123456789","diagnosis":"placeholder diagnosis text",'
                '"insured_name":"Placeholder Name","thai_id":"1234567890123"}')
        for name, rx in self.ids.items():
            with self.subTest(identifier=name):
                self.assertTrue(rx.search(line), name)

    def test_arns_and_ids_used_for_debugging_survive(self):
        line = '{"function":"arn:aws:lambda:ap-southeast-1:123456789012:function:claims-ingest","claim_id":"C-123456789012"}'
        for name, rx in self.ids.items():
            self.assertFalse(rx.search(line), name)


class DomainDeployRoleTest(unittest.TestCase):
    """OD22: a domain stack's deploy role may create or change only `svc-*` roles, and only with
    the boundary attached (pattern 📖 R9.2.1). The boundary itself cannot be changed or removed."""

    @classmethod
    def setUpClass(cls):
        cls.doc = load("aws", "deploy-role-domain-iam-limits.json")
        cls.by_sid = {s["Sid"]: s for s in cls.doc["Statement"]}
        cls.boundary = load("aws", "app-permissions-boundary.json")

    def test_actions_exist(self):
        for doc in (self.doc, self.boundary):
            for st in doc["Statement"]:
                for a in as_list(st["Action"]):
                    if a != "*":
                        self.assertTrue(expand(a), f"unknown action {a}")

    def test_role_policy_changes_require_the_boundary(self):
        boundary_arn = "arn:aws:iam::<AWS_ACCOUNT_ID>:policy/" + BOUNDARY_NAME
        for st in self.doc["Statement"]:
            if st["Effect"] != "Allow":
                continue
            self.assertEqual(st["Resource"], "arn:aws:iam::<AWS_ACCOUNT_ID>:role/svc-*", st["Sid"])
            touches_permissions = set(as_list(st["Action"])) & set(ROLE_PERMISSION_CHANGES)
            if touches_permissions:
                self.assertEqual(st["Condition"], {"StringEquals": {"iam:PermissionsBoundary": boundary_arn}},
                                 st["Sid"])
        allowed = {a for st in self.doc["Statement"] if st["Effect"] == "Allow" for a in as_list(st["Action"])}
        self.assertLessEqual(set(ROLE_PERMISSION_CHANGES), allowed)
        conditioned = set(as_list(self.by_sid["CreateOrChangeServiceRolesOnlyWithTheBoundary"]["Action"]))
        self.assertEqual(conditioned, set(ROLE_PERMISSION_CHANGES), "no permission change outside the boundary rule")

    def test_boundary_cannot_be_removed_or_edited(self):
        self.assertEqual(self.by_sid["NeverRemoveABoundary"]["Action"], "iam:DeleteRolePermissionsBoundary")
        st = self.by_sid["NeverChangeTheBoundaryPolicy"]
        self.assertEqual(sorted(st["Action"]), sorted(BOUNDARY_POLICY_ACTIONS))
        self.assertTrue(st["Resource"].endswith(":policy/" + BOUNDARY_NAME))

    def test_no_exempt_role_names(self):
        # svc-* never overlaps a name the SCP exempts or protects.
        for p in PROTECTED_ROLE_NAMES:
            self.assertFalse(fnmatch.fnmatchcase("arn:aws:iam::*:role/svc-x", p))

    def test_boundary_denies_identity_changes(self):
        denied = {a for st in self.boundary["Statement"] if st["Effect"] == "Deny" for a in as_list(st["Action"])}
        self.assertIn("iam:*", denied)
        self.assertIn("sts:AssumeRoot", denied)


class PermissionSetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = load("aws", "permission-set-prod-read-metadata.json")
        cls.statements = cls.doc["InlinePolicy"]["Statement"]

    def test_one_hour_session(self):
        self.assertEqual(self.doc["PermissionSet"]["SessionDuration"], "PT1H")  # R2.1.4

    def test_only_allow_with_action_and_resource(self):
        for st in self.statements:
            self.assertEqual(st["Effect"], "Allow")
            self.assertNotIn("NotAction", st)
            self.assertNotIn("NotResource", st)

    def test_every_action_exists_and_none_writes(self):
        for st in self.statements:
            for pattern in as_list(st["Action"]):
                actions = expand(pattern)
                self.assertTrue(actions, f"unknown action {pattern}")
                for a in actions:
                    svc, name = a.split(":")
                    meta = CATALOGUE[svc][name]
                    self.assertFalse(meta["write"], f"{a} is a write action")
                    self.assertFalse(meta["permission_mgmt"], f"{a} manages permissions")

    def test_no_data_reads(self):
        granted = {a for st in self.statements for p in as_list(st["Action"]) for a in expand(p)}
        self.assertFalse(granted & set(DATA_READS), sorted(granted & set(DATA_READS)))

    def test_wildcard_resource_only_for_reviewed_metadata(self):
        for st in self.statements:
            if "*" not in as_list(st["Resource"]):
                continue
            for p in as_list(st["Action"]):
                with self.subTest(action=p):
                    self.assertNotRegex(p, r"[*?]", "no action wildcards with Resource *")
                    self.assertIn(p, REVIEWED_METADATA, "not a reviewed metadata read")

    def test_raw_logs_and_config_only_per_service(self):
        for st in self.statements:
            granted = {a for p in as_list(st["Action"]) for a in expand(p)}
            if granted & set(PER_SERVICE_ONLY):
                for r in as_list(st["Resource"]):
                    with self.subTest(sid=st["Sid"], resource=r):
                        # One named log group (optionally its streams, ":*") or one named function.
                        self.assertRegex(r, r"^arn:aws:(logs:\*:<AWS_ACCOUNT_ID>:log-group:/[\w/.-]+(:\*)?"
                                            r"|lambda:\*:<AWS_ACCOUNT_ID>:function:[\w.-]+)$")


class DbChangeRolesTest(unittest.TestCase):
    """E15, ADR-0011: the GitHub-hosted `sql` job only starts one ECS task inside the VPC; the
    task's role, not the job's, connects to Aurora, and only as the migration user."""

    def setUp(self):
        self.ci = load("aws", "db-change-ci-role-policy.json")["Statement"]
        self.task = load("aws", "db-change-task-role-policy.json")["Statement"]

    def test_actions_exist(self):
        for st in self.ci + self.task:
            for a in as_list(st["Action"]):
                with self.subTest(action=a):
                    self.assertTrue(expand(a), f"{a} is not an AWS action")

    def test_ci_role_never_connects_to_the_database(self):
        actions = {a for st in self.ci if st["Effect"] == "Allow" for a in as_list(st["Action"])}
        self.assertFalse({a for a in actions if a.startswith("rds")})
        self.assertFalse({a for a in actions if "*" in a})

    def test_run_task_is_one_family_on_one_cluster(self):
        [st] = [s for s in self.ci if s["Effect"] == "Allow" and "ecs:RunTask" in as_list(s["Action"])]
        self.assertRegex(st["Resource"], r":task-definition/db-change-[\w-]+:\*$")
        self.assertIn("ecs:cluster", st["Condition"]["ArnEquals"])

    def test_pass_role_only_to_ecs_tasks_and_named_roles(self):
        [st] = [s for s in self.ci if "iam:PassRole" in as_list(s["Action"])]
        for r in as_list(st["Resource"]):
            with self.subTest(resource=r):
                self.assertNotIn("*", r)
        self.assertEqual(st["Condition"]["StringEquals"]["iam:PassedToService"], "ecs-tasks.amazonaws.com")

    def test_no_shell_into_the_task(self):
        denied = {a for s in self.ci if s["Effect"] == "Deny" for a in as_list(s["Action"])}
        self.assertIn("ecs:ExecuteCommand", denied)

    def test_task_connects_as_one_user(self):
        [st] = [s for s in self.task if "rds-db:connect" in as_list(s["Action"])]
        self.assertRegex(st["Resource"], r":dbuser:[^*/]+/[a-z_]+$")



class JitReceiverRoleTest(unittest.TestCase):
    """E16, OD33: the JIT receiver can assign only permission sets tagged for JIT, in the prod
    account, and can never create, change or re-tag a permission set. Resource types and ARN
    formats of the sso actions: AWS Service Reference (sso.json), fetched 2026-11-09."""

    def setUp(self):
        self.st = load("aws", "jit-receiver-role-policy.json")["Statement"]

    def test_actions_exist(self):
        for st in self.st:
            for a in as_list(st["Action"]):
                with self.subTest(action=a):
                    self.assertTrue(expand(a), f"{a} is not an AWS action")

    def test_assignments_only_on_tagged_permission_sets(self):
        allows = [s for s in self.st if s["Effect"] == "Allow"
                  and "sso:CreateAccountAssignment" in as_list(s["Action"])]
        ps = [s for s in allows if any(":permissionSet/" in r for r in as_list(s["Resource"]))]
        self.assertEqual(len(ps), 1)
        self.assertEqual(ps[0]["Condition"], {"StringEquals": {"aws:ResourceTag/jit-grant": "infra-operator"}})
        for s in allows:
            for r in as_list(s["Resource"]):
                with self.subTest(resource=r):
                    self.assertRegex(r, r"^arn:aws:sso:::(permissionSet/<SSO_INSTANCE_ID>/\*"
                                        r"|instance/<SSO_INSTANCE_ID>|account/<PROD_ACCOUNT_ID>)$")

    def test_no_other_write(self):
        allowed = {a for s in self.st if s["Effect"] == "Allow" for a in as_list(s["Action"])}
        writes = {a for a in allowed if CATALOGUE["sso"][a.split(":")[1]]["write"]}
        self.assertEqual(writes, {"sso:CreateAccountAssignment", "sso:DeleteAccountAssignment"})
        denied = {a for s in self.st if s["Effect"] == "Deny" for a in as_list(s["Action"])}
        self.assertTrue({"sso:TagResource", "sso:PutInlinePolicyToPermissionSet",
                         "sso:CreatePermissionSet"} <= denied)


if __name__ == "__main__":
    unittest.main()
