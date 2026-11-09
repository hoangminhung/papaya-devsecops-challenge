"""E3: design conditions on the GitHub Actions workflows that linters do not know about.

Framework layer 3, "Merge approval = deploy approval", holds only if:
  - only the reusable deploy workflow references `production`;
  - it has no ref/SHA input and is not reachable from workflow_dispatch;
  - no workflow uses `issue_comment`, `pull_request_target` or `workflow_run`;
  - one concurrency group per stack, without cancel-in-progress;
  - the IAM stack alone deploys from `production-iam`, and no install script runs except the
    reviewed allowlist (OD22).
Layer 5 adds: every `uses:` pinned to a full commit SHA (or the same-repository `$/` form),
`permissions:` declared per job with an empty workflow default, and `id-token: write` only
where OIDC is needed.

Scope: the files in examples/github/workflows only, not a whole monorepo.
"""
import glob
import os
import re
import shlex
import unittest

import yaml

HERE = os.path.dirname(__file__)
WF_DIR = os.path.join(HERE, "..", "github", "workflows")
DEPLOY = "deploy-prod.yml"
OIDC_JOBS = {("deploy-prod.yml", "deploy"), ("pr-preview-nonprod.yml", "preview"),
             ("evidence-export.yml", "export"),
             ("agent-security-review.yml", "review")}  # Anthropic federation, no cloud role
OIDC_CALLERS = {("deploy-on-main.yml", "claims-data"), ("deploy-on-main.yml", "claims-api"),
                ("deploy-on-main.yml", "iam"), ("deploy-on-main.yml", "claims-db")}
# OD22: only the IAM stack deploys from `production-iam`; the mapping lives in deploy-prod.yml.
DEPLOY_ENVIRONMENT = ("${{ inputs.stack == 'iam' && 'production-iam' || inputs.tool == 'sql' && 'production-db'"
                      " || 'production' }}")
FORBIDDEN_TRIGGERS = {"issue_comment", "pull_request_target", "workflow_run"}
SHA_PIN = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")
SELF_REPO = re.compile(r"^\$/\.github/workflows/[\w.-]+\.ya?ml$")


def read(name):
    with open(os.path.join(WF_DIR, name)) as f:
        return f.read()


def load_all():
    out = {}
    for path in sorted(glob.glob(os.path.join(WF_DIR, "*.yml"))):
        with open(path) as f:
            # PyYAML (YAML 1.1) reads the key `on` as True.
            doc = yaml.safe_load(f)
        doc["on"] = doc.pop(True, doc.get("on"))
        out[os.path.basename(path)] = doc
    return out


def triggers(doc):
    on = doc["on"]
    if isinstance(on, str):
        return {on}
    if isinstance(on, list):
        return set(on)
    return set(on.keys())


def environment_name(job):
    env = job.get("environment")
    if isinstance(env, dict):
        return env.get("name")
    return env


class WorkflowPolicyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wfs = load_all()

    def test_files_found(self):
        self.assertIn(DEPLOY, self.wfs)
        self.assertGreaterEqual(len(self.wfs), 3)

    def test_only_deploy_workflow_uses_production(self):
        for name, doc in self.wfs.items():
            for job_id, job in doc["jobs"].items():
                env = environment_name(job)
                if env and str(env).startswith("production"):
                    self.assertEqual((name, job_id), (DEPLOY, "deploy"))

    def test_environment_per_kind_of_stack(self):
        job = self.wfs[DEPLOY]["jobs"]["deploy"]
        self.assertEqual(job["environment"], DEPLOY_ENVIRONMENT)
        # Callers pass no environment of their own.
        for job_id, caller in self.wfs["deploy-on-main.yml"]["jobs"].items():
            self.assertNotIn("environment", caller.get("with", {}), job_id)

    def test_install_scripts_off_except_allowlist(self):
        for name, job_id in [(DEPLOY, "deploy"), ("pr-preview-nonprod.yml", "preview")]:
            env = self.wfs[name]["jobs"][job_id].get("env", {})
            self.assertEqual(env.get("npm_config_ignore_scripts"), "true", f"{name}:{job_id}")
        runs = [s.get("run", "") for s in self.steps()]
        rebuild = [r for r in runs if "npm rebuild" in r]
        self.assertEqual(len(rebuild), 1)
        self.assertIn("tools/ci/allowed-install-scripts.txt", rebuild[0])
        for r in runs:
            self.assertNotRegex(r, r"ignore-scripts=false(?!.*allowed)", "scripts re-enabled outside the allowlist step")
            self.assertNotIn("npm_config_ignore_scripts", r)

    def test_evidence_export_only_adds(self):
        # OD30: the export writes new objects; Object Lock keeps them (examples/aws).
        job = self.wfs["evidence-export.yml"]["jobs"]["export"]
        self.assertEqual(job["environment"], "evidence")
        self.assertEqual(triggers(self.wfs["evidence-export.yml"]), {"schedule"})
        runs = "\n".join(st.get("run", "") for st in job["steps"])
        self.assertIn("aws s3 cp --recursive", runs)
        for bad in ("aws s3 rm", "aws s3 sync", "--delete", "s3api delete", "put-object-retention"):
            self.assertNotIn(bad, runs)
        perms = job["permissions"]
        self.assertTrue(all(v == "read" for k, v in perms.items() if k != "id-token"), perms)

    def test_deploy_is_reusable_only(self):
        self.assertEqual(triggers(self.wfs[DEPLOY]), {"workflow_call"})

    def test_deploy_has_no_ref_or_sha_input(self):
        inputs = self.wfs[DEPLOY]["on"]["workflow_call"].get("inputs", {})
        for key in inputs:
            self.assertNotRegex(key.lower(), r"ref|sha|commit|branch|tag")

    def test_deploy_checks_out_the_running_commit(self):
        for step in self.wfs[DEPLOY]["jobs"]["deploy"]["steps"]:
            if str(step.get("uses", "")).startswith("actions/checkout@"):
                self.assertNotIn("ref", step.get("with", {}))
                self.assertNotIn("repository", step.get("with", {}))

    def test_no_forbidden_triggers_and_no_manual_deploy(self):
        for name, doc in self.wfs.items():
            with self.subTest(workflow=name):
                self.assertFalse(triggers(doc) & FORBIDDEN_TRIGGERS)
                calls_deploy = any(
                    str(j.get("uses", "")).endswith("/" + DEPLOY) for j in doc["jobs"].values()
                )
                if calls_deploy:
                    self.assertNotIn("workflow_dispatch", triggers(doc))
                    self.assertEqual(doc["on"]["push"]["branches"], ["main"])

    def test_deploy_concurrency_per_stack_never_cancelled(self):
        conc = self.wfs[DEPLOY]["jobs"]["deploy"]["concurrency"]
        self.assertIn("inputs.stack", conc["group"])
        self.assertIs(conc["cancel-in-progress"], False)

    def steps(self):
        return self.wfs[DEPLOY]["jobs"]["deploy"]["steps"]

    def test_apply_commands_use_only_allowed_flags(self):
        # Tokenised, so short forms (-f = --skip-preview, -t = --target) are caught too.
        allowed = {
            ("pulumi", "up"): {"--stack", "--yes", "--policy-pack"},
            ("pulumi", "preview"): {"--stack", "--json"},
            ("npx", "serverless"): {"--stage", "--package", "--json", "--version"},
            ("npx", "sls"): {"--stage", "--package", "--json"},
        }
        seen = set()
        for step in self.steps():
            for line in step.get("run", "").splitlines():
                tokens = shlex.split(line.split(">")[0])
                if len(tokens) < 2:
                    continue
                key = (tokens[0], tokens[1])
                if key in allowed:
                    seen.add(key)
                    flags = {t.split("=")[0] for t in tokens if t.startswith("-")}
                    self.assertLessEqual(flags, allowed[key], line)
        self.assertLessEqual({("pulumi", "up"), ("pulumi", "preview"), ("npx", "serverless")}, seen)
        runs = "\n".join(s.get("run", "") for s in self.steps())
        for bad in ("pulumi state", "pulumi import", "pulumi destroy", "pulumi refresh", "deploy function"):
            self.assertNotIn(bad, runs)

    def test_risk_stop_cannot_be_skipped_or_ignored(self):
        job = self.wfs[DEPLOY]["jobs"]["deploy"]
        self.assertNotIn("continue-on-error", job)
        [stop] = [s for s in self.steps() if s.get("name") == "Risk stop"]
        self.assertNotIn("continue-on-error", stop)
        self.assertNotIn("if", stop)
        run = " ".join(stop["run"].split())
        self.assertTrue(run.startswith("python3 tools/risk-stop/classify.py "), run)
        for token in ("||", "&&", ";", "|", "&", "$(", "`"):
            self.assertNotIn(token, run)

    def test_apply_runs_only_after_a_passing_risk_stop(self):
        # Any step that applies (by command, not by name) comes after the stop and runs only
        # on its tool's plain condition: no always(), failure(), cancelled(), continue-on-error.
        names = [s.get("name", "") for s in self.steps()]
        stop = names.index("Risk stop")
        apply_re = re.compile(r"\b(pulumi\s+up|(serverless|sls)\s+deploy)\b|tools/db/apply\.sh")
        applies = [(i, s) for i, s in enumerate(self.steps()) if apply_re.search(s.get("run", ""))]
        self.assertEqual(len(applies), 3)
        for i, s in applies:
            self.assertGreater(i, stop)
            self.assertNotIn("continue-on-error", s)
            self.assertIn(s.get("if"), ("inputs.tool == 'pulumi'", "inputs.tool == 'serverless'",
                                        "inputs.tool == 'sql'"))
        for s in self.steps()[stop + 1:]:
            self.assertNotIn("continue-on-error", s)

    def test_only_the_tip_of_main_is_deployed(self):
        steps = self.steps()
        [guard] = [i for i, s in enumerate(steps) if s.get("name", "").startswith("Refuse to deploy")]
        self.assertNotIn("if", steps[guard])
        self.assertNotIn("continue-on-error", steps[guard])
        run = steps[guard]["run"]
        self.assertIn('repos/$REPO/git/ref/heads/main', run)  # branch only, never a tag
        self.assertRegex(run, r'if \[ "\$tip" != "\$GITHUB_SHA" \]; then')
        body = run.split("then", 1)[1].split("fi", 1)[0]
        self.assertEqual(body.strip().splitlines()[-1].strip(), "exit 1")
        creds = next(i for i, s in enumerate(steps)
                     if str(s.get("uses", "")).startswith("aws-actions/configure-aws-credentials@"))
        self.assertLess(guard, creds)

    def test_downloads_happen_before_prod_credentials(self):
        steps = self.steps()
        creds = next(i for i, s in enumerate(steps)
                     if str(s.get("uses", "")).startswith("aws-actions/configure-aws-credentials@"))
        install_re = re.compile(r"\b(npm ci|npm rebuild|pulumi install|serverless --version|npm install|pulumi plugin install)\b")
        installs = [i for i, s in enumerate(steps) if install_re.search(s.get("run", ""))]
        self.assertTrue(installs)
        for i in installs:
            self.assertLess(i, creds, steps[i].get("name"))

    def test_one_credentials_step_per_tool_without_fallback(self):
        creds = [s for s in self.steps()
                 if str(s.get("uses", "")).startswith("aws-actions/configure-aws-credentials@")]
        roles = {s["if"]: s["with"]["role-to-assume"] for s in creds}
        self.assertEqual(roles, {
            "inputs.tool == 'pulumi'": "${{ vars.PROD_PULUMI_DEPLOY_ROLE_ARN }}",
            "inputs.tool == 'serverless'": "${{ vars.PROD_SERVERLESS_DEPLOY_ROLE_ARN }}",
            "inputs.tool == 'sql'": "${{ vars.PROD_DB_CHANGE_ROLE_ARN }}",
        })

    def test_database_apply_uses_the_classified_files(self):
        # ADR-0011: what is applied is exactly the JSON the risk stop classified and hashed.
        runs = [s.get("run", "") for s in self.steps()]
        [pending] = [r for r in runs if "tools/db/pending.sh" in r]
        [apply] = [r for r in runs if "tools/db/apply.sh" in r]
        self.assertIn('> "$RUNNER_TEMP/preview.json"', pending)
        self.assertIn('"$RUNNER_TEMP/preview.json"', apply)

    def test_full_history_for_approval_checks(self):
        [co] = [s for s in self.steps() if str(s.get("uses", "")).startswith("actions/checkout@")]
        self.assertEqual(co["with"].get("fetch-depth"), 0)

    def test_actions_pinned(self):
        for name, doc in self.wfs.items():
            for job_id, job in doc["jobs"].items():
                if "uses" in job:  # reusable workflow call
                    self.assertRegex(job["uses"], SELF_REPO, f"{name}:{job_id}")
                for step in job.get("steps", []):
                    if "uses" in step:
                        self.assertRegex(step["uses"], SHA_PIN, f"{name}:{job_id}")

    def test_permissions_per_job(self):
        for name, doc in self.wfs.items():
            with self.subTest(workflow=name):
                self.assertEqual(doc.get("permissions"), {}, "workflow default must be empty")
                for job_id, job in doc["jobs"].items():
                    self.assertIn("permissions", job, f"{name}:{job_id}")

    def test_id_token_only_where_needed(self):
        for name, doc in self.wfs.items():
            for job_id, job in doc["jobs"].items():
                has = (job.get("permissions") or {}).get("id-token") == "write"
                needed = (name, job_id) in OIDC_JOBS | OIDC_CALLERS
                self.assertEqual(has, needed, f"{name}:{job_id}")

    def test_ci_agent_reviews_read_only_and_never_reaches_prod(self):
        # Framework §2 and layer 5 (OD22): comments only, no environment, no Bash, no MCP.
        doc = self.wfs["agent-security-review.yml"]
        self.assertEqual(set(doc["on"]), {"pull_request"})
        job = doc["jobs"]["review"]
        self.assertEqual(job["environment"], "ci-agent")  # holds the App key only; no prod trust
        self.assertEqual(job["permissions"], {"contents": "read", "id-token": "write"})
        steps = {s.get("name"): s for s in job["steps"]}
        token = steps["Token of the CI-agent GitHub App (comments only)"]["with"]
        perms = {k: v for k, v in token.items() if k.startswith("permission-")}
        self.assertEqual(perms, {"permission-contents": "read", "permission-pull-requests": "write"})
        review = steps["Security review"]["with"]
        self.assertIn("anthropic_federation_rule_id", review)
        self.assertNotIn("anthropic_api_key", review)
        args = review["claude_args"]
        for flag in ("--restricted", "--strict-mcp-config", '--tools "Read,Grep,Glob"'):
            self.assertIn(flag, args)
        self.assertNotIn("Bash", args)
        self.assertIn("Never approve", review["prompt"])

    def test_no_aws_keys(self):
        for name in self.wfs:
            text = read(name)
            self.assertNotRegex(text, r"aws-access-key-id|aws-secret-access-key|AWS_SECRET_ACCESS_KEY")


if __name__ == "__main__":
    unittest.main()
