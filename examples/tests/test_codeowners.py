"""E2: CODEOWNERS gives each path the owners the framework requires.

Resolves the *effective* owners of sample paths with GitHub's rule "the last matching
pattern takes the most precedence" (GitHub docs, about-code-owners), so a broad line
placed after the L3 section would make this test fail.

The pattern matcher implements the gitignore subset CODEOWNERS supports: leading `/`
anchors to the root, trailing `/` matches a directory and everything below it, `*`
does not cross `/`, `**` does, and a pattern with no inner `/` matches at any depth.
It is checked against the examples in GitHub's docs (MatcherTest). It is a model of
GitHub's behaviour, not GitHub itself.

Not checked (needs the real repository): that teams exist and have write access.
GitHub skips such owners silently.
"""
import os
import re
import unittest

import yaml

HERE = os.path.dirname(__file__)
CODEOWNERS = os.path.join(HERE, "..", "github", "CODEOWNERS")

L3 = "@example-org/l3-owners"
ONCALL = "@example-org/oncall-approvers"

# Canonical L3 path list, framework layer 5 "CODEOWNERS" bullet, one sample file each.
PROCESS_L3_SAMPLES = [
    ".github/workflows/deploy-prod.yml",
    ".github/CODEOWNERS",
    "CLAUDE.md",
    "services/claims/CLAUDE.md",        # nested CLAUDE.md inside a domain path
    "CLAUDE.local.md",
    ".claude/settings.json",
    "services/claims/.claude/settings.json",
    ".claude.json",
    ".mcp.json",
    "services/claims/.mcp.json",
    ".husky/pre-commit",
    ".gitmodules",
    ".ripgreprc",
    ".devcontainer/devcontainer.json",
    ".npmrc",
    "services/claims/.npmrc",
    "policy-packs/aws/index.ts",
    "tools/risk-stop/classify.py",     # OD14
    "infra/pulumi/org-scp/index.ts",
    "agent-config/managed-settings.json",
    "infra/pulumi/iam/index.ts",            # OD32: two L3 approvers, no on-call co-owner
    "deploy-approvals/iam/0123abcd.yaml",   # OD32
    "apps/mobile/certs/certificate.pem",    # OD40
    "ai-agents/claim-assessor/tools.yaml",  # OD45
]

# Deployable paths: (sample file, domain team that must be an owner).
DEPLOYABLE_SAMPLES = [
    ("services/claims/serverless.yml", "@example-org/team-claims"),
    ("services/claims/src/handler.ts", "@example-org/team-claims"),
    ("services/underwriting/serverless.yml", "@example-org/team-underwriting"),
    ("web/firebase.json", "@example-org/team-web"),
    ("infra/pulumi/claims-data/index.ts", "@example-org/team-claims"),
    ("k8s/claims/deployment.yaml", "@example-org/team-claims"),
]

RISK_STOP_SAMPLES = [
    ("deploy-approvals/claims-data/0123abcd.yaml", "@example-org/team-claims"),
]


def pattern_to_regex(pattern):
    anchored = pattern.startswith("/")
    p = pattern.lstrip("/")
    directory = p.endswith("/")
    p = p.rstrip("/")
    if "/" in p:
        anchored = True  # gitignore: a slash in the middle anchors the pattern
    out = ""
    i = 0
    while i < len(p):
        if p.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif p.startswith("**", i):
            out += ".*"
            i += 2
        elif p[i] == "*":
            out += "[^/]*"
            i += 1
        elif p[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(p[i])
            i += 1
    prefix = "^" if anchored else "^(?:.*/)?"
    # A literal name (e.g. `/apps/github`, `**/logs`) also matches a directory of that
    # name and its contents; a directory pattern matches only contents; a last segment
    # with a wildcard (`docs/*`) does not descend further (GitHub docs example).
    last = p.rsplit("/", 1)[-1]
    if directory:
        suffix = "/.*$"
    elif "*" in last or "?" in last:
        suffix = "$"
    else:
        suffix = "(?:/.*)?$"
    return re.compile(prefix + out + suffix)


def parse(path):
    rules = []
    with open(path) as f:
        for n, line in enumerate(f, 1):
            line = line.split(" #")[0].strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            rules.append((n, parts[0], parts[1:]))
    return rules


def owners_of(rules, path):
    result = None
    for _, pattern, owners in rules:
        if pattern_to_regex(pattern).match(path):
            result = owners
    return result


def pattern_of(rules, path):
    """The pattern of the last matching line (the one GitHub applies)."""
    result = None
    for _, pattern, _owners in rules:
        if pattern_to_regex(pattern).match(path):
            result = pattern
    return result


FAIL_SAFE_PATTERNS = {"*", "/deploy-approvals/"}


class MatcherTest(unittest.TestCase):
    """The matcher against the examples in GitHub's CODEOWNERS docs."""

    def test_docs_examples(self):
        self.assertTrue(pattern_to_regex("*.js").match("a/b/c.js"))
        self.assertTrue(pattern_to_regex("/build/logs/").match("build/logs/x/y.log"))
        self.assertFalse(pattern_to_regex("/build/logs/").match("src/build/logs/y.log"))
        self.assertTrue(pattern_to_regex("docs/*").match("docs/getting-started.md"))
        self.assertFalse(pattern_to_regex("docs/*").match("docs/build-app/troubleshooting.md"))
        self.assertTrue(pattern_to_regex("apps/").match("x/apps/y.js"))
        self.assertTrue(pattern_to_regex("**/logs").match("deeply/nested/logs/a"))
        self.assertTrue(pattern_to_regex("/apps/github").match("apps/github/a.js"))

    def test_last_match_wins(self):
        rules = [(1, "/apps/", ["@octocat"]), (2, "/apps/github", ["@doctocat"])]
        self.assertEqual(owners_of(rules, "apps/github/x"), ["@doctocat"])
        self.assertEqual(owners_of(rules, "apps/other/x"), ["@octocat"])


class CodeownersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = parse(CODEOWNERS)

    def test_syntax(self):
        for n, pattern, owners in self.rules:
            with self.subTest(line=n):
                self.assertNotIn("!", pattern, "negation does not work in CODEOWNERS")
                self.assertNotRegex(pattern, r"\[", "character ranges do not work in CODEOWNERS")
                self.assertTrue(owners, "a pattern without owners removes ownership")
                for o in owners:
                    self.assertRegex(o, r"^@[\w.-]+/[\w.-]+$", "owners must be org teams")

    def test_process_paths_only_l3_team(self):
        for path in PROCESS_L3_SAMPLES:
            with self.subTest(path=path):
                self.assertEqual(owners_of(self.rules, path), [L3])

    def test_deployable_paths_domain_plus_oncall(self):
        for path, team in DEPLOYABLE_SAMPLES:
            with self.subTest(path=path):
                owners = owners_of(self.rules, path)
                self.assertIsNotNone(owners, "unowned deployable path: any writer could approve")
                self.assertIn(team, owners)
                self.assertIn(ONCALL, owners)

    def test_risk_stop_approvals_stack_owners_plus_oncall(self):
        for path, team in RISK_STOP_SAMPLES:
            with self.subTest(path=path):
                self.assertEqual(sorted(owners_of(self.rules, path)), sorted([team, ONCALL]))

    def test_every_deployed_stack_is_owned(self):
        """Each stack deployed by deploy-on-main.yml: its code and its approvals folder are
        owned by a domain team plus the on-call group; the IAM stack only by the L3 owner team,
        so it needs two L3 approvers through the gate's process-path rule (OD32)."""
        with open(os.path.join(HERE, "..", "github", "workflows", "deploy-on-main.yml")) as f:
            jobs = yaml.safe_load(f)["jobs"]
        self.assertTrue(jobs)
        for job in jobs.values():
            stack, workdir = job["with"]["stack"], job["with"]["workdir"]
            for path in (f"deploy-approvals/{stack}/abc.yaml", f"{workdir}/x"):
                with self.subTest(path=path):
                    owners = owners_of(self.rules, path)
                    if stack == "iam":
                        self.assertEqual(owners, [L3])
                    else:
                        self.assertIn(ONCALL, owners)
                        self.assertTrue(any(o != ONCALL for o in owners))
                    # the fail-safe default alone does not count as "owned by the stack": a line
                    # for that stack must match
                    self.assertNotIn(pattern_of(self.rules, path), FAIL_SAFE_PATTERNS, path)

    def test_production_agent_prompts_owned_by_the_ai_team_only(self):
        # OD45: a prompt or model change is never an incident fix, so on-call does not co-own it.
        for path in ("ai-agents/claim-assessor/prompts/system.md", "ai-agents/claim-assessor/model.yaml"):
            with self.subTest(path=path):
                self.assertEqual(owners_of(self.rules, path), ["@example-org/team-ai"])

    def test_no_file_is_unowned(self):
        for path in ("package.json", "package-lock.json", "infra/pulumi/new-stack/index.ts",
                     "deploy-approvals/new-stack/abc.yaml", "README.md"):
            with self.subTest(path=path):
                self.assertTrue(owners_of(self.rules, path))

    def test_oncall_never_on_process_paths(self):
        for _, pattern, owners in self.rules:
            if L3 in owners and ONCALL not in owners:
                continue
            for path in PROCESS_L3_SAMPLES:
                if pattern_to_regex(pattern).match(path):
                    # allowed only if a later L3-only line overrides it (checked above)
                    self.assertEqual(owners_of(self.rules, path), [L3])


if __name__ == "__main__":
    unittest.main()
