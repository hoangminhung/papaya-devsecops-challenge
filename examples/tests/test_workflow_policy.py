"""E3: design conditions on the GitHub Actions workflows that linters do not know about.

Framework layer 3, "Merge approval = deploy approval", holds only if:
  - only the reusable deploy workflow references `production`;
  - it has no ref/SHA input and is not reachable from workflow_dispatch;
  - no workflow uses `issue_comment`, `pull_request_target` or `workflow_run`;
  - one concurrency group per stack, without cancel-in-progress.
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
OIDC_JOBS = {("deploy-prod.yml", "deploy"), ("pr-preview-nonprod.yml", "preview")}
OIDC_CALLERS = {("deploy-on-main.yml", "claims-data"), ("deploy-on-main.yml", "claims-api")}
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
        text = read(DEPLOY)
        for bad in ("pulumi state", "pulumi import", "pulumi destroy", "pulumi refresh", "deploy function"):
            self.assertNotIn(bad, text)

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
        apply_re = re.compile(r"\b(pulumi\s+up|(serverless|sls)\s+deploy)\b")
        applies = [(i, s) for i, s in enumerate(self.steps()) if apply_re.search(s.get("run", ""))]
        self.assertEqual(len(applies), 2)
        for i, s in applies:
            self.assertGreater(i, stop)
            self.assertNotIn("continue-on-error", s)
            self.assertIn(s.get("if"), ("inputs.tool == 'pulumi'", "inputs.tool == 'serverless'"))
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
        install_re = re.compile(r"\b(npm ci|pulumi install|serverless --version|npm install|pulumi plugin install)\b")
        installs = [i for i, s in enumerate(steps) if install_re.search(s.get("run", ""))]
        self.assertTrue(installs)
        for i in installs:
            self.assertLess(i, creds, steps[i].get("name"))

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

    def test_no_aws_keys(self):
        for name in self.wfs:
            text = read(name)
            self.assertNotRegex(text, r"aws-access-key-id|aws-secret-access-key|AWS_SECRET_ACCESS_KEY")


if __name__ == "__main__":
    unittest.main()
