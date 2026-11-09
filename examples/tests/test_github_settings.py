"""E1 ruleset on `main` and E3b `production` environment.

Three checks per file:
  1. schema: the body validates against the request schema extracted from GitHub's REST
     OpenAPI description (examples/schemas/, see tools/extract_github_schemas.py);
  2. keys: every key exists at that path in the schema (the schemas do not forbid extra
     keys, so check 1 alone would accept a misspelled key);
  3. design: the values the framework requires (layer 3 "Gate = merge to main"; layer 5).

Not checked: that GitHub enforces the settings as described. That needs a real repository.
"""
import json
import os
import unittest

import jsonschema

from schema_keys import unknown_keys

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")


def load(*parts):
    with open(os.path.join(ROOT, *parts)) as f:
        return json.load(f)


GITHUB_ACTIONS_APP_ID = 15368  # GET https://api.github.com/apps/github-actions


class RulesetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = load("github", "ruleset-main.json")
        cls.schema = load("schemas", "github-ruleset-create.json")
        cls.rules = {r["type"]: r.get("parameters", {}) for r in cls.body["rules"]}

    def test_schema(self):
        jsonschema.validate(self.body, self.schema)

    def test_no_unknown_keys(self):
        self.assertEqual(unknown_keys(self.body, self.schema), [])

    def test_targets_main_and_active(self):
        self.assertEqual(self.body["target"], "branch")
        self.assertEqual(self.body["enforcement"], "active")
        self.assertEqual(self.body["conditions"]["ref_name"]["include"], ["refs/heads/main"])

    def test_nobody_bypasses(self):
        self.assertEqual(self.body["bypass_actors"], [])

    def test_no_force_push_no_delete(self):
        self.assertIn("non_fast_forward", self.rules)
        self.assertIn("deletion", self.rules)

    def test_pull_request_rule(self):
        pr = self.rules["pull_request"]
        self.assertEqual(pr["required_approving_review_count"], 1)  # OD2: two people, not more
        self.assertTrue(pr["require_code_owner_review"])
        self.assertTrue(pr["dismiss_stale_reviews_on_push"])
        self.assertTrue(pr["require_last_push_approval"])
        self.assertNotIn("required_reviewers", pr)  # layer 3: no path-based reviewers (OD9)
        # Squash only: each PR is one first-parent commit, which the risk-stop approval check needs.
        self.assertEqual(pr["allowed_merge_methods"], ["squash"])
        # Copilot-only extra approval (R3.3.2) would make a third person necessary (OD2).
        self.assertNotIn("require_extra_approval_for_unattributed_changes", pr)

    def test_status_checks_strict_and_pinned(self):
        sc = self.rules["required_status_checks"]
        self.assertTrue(sc["strict_required_status_checks_policy"])  # no merge queue
        checks = {c["context"]: c.get("integration_id") for c in sc["required_status_checks"]}
        for context, app in checks.items():
            with self.subTest(context=context):
                self.assertIsNotNone(app, "every required check is pinned to a source app")
        # The approval check comes from a dedicated app, not from GitHub Actions (layer 3, G19).
        self.assertNotEqual(checks["approval-gate"], GITHUB_ACTIONS_APP_ID)
        for required in ("codeowners-validate", "secret-scan", "dependency-check", "sast"):
            self.assertIn(required, checks)


class EnvironmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = load("github", "environment-production", "environment.json")
        cls.env_schema = load("schemas", "github-environment-put.json")
        cls.policy = load("github", "environment-production", "branch-policy.json")
        cls.policy_schema = load("schemas", "github-deployment-branch-policy-post.json")

    def test_schema(self):
        jsonschema.validate(self.env, self.env_schema)
        jsonschema.validate(self.policy, self.policy_schema)

    def test_no_unknown_keys(self):
        self.assertEqual(unknown_keys(self.env, self.env_schema), [])
        self.assertEqual(unknown_keys(self.policy, self.policy_schema), [])

    def test_only_main_can_deploy(self):
        dbp = self.env["deployment_branch_policy"]
        self.assertTrue(dbp["custom_branch_policies"])
        self.assertFalse(dbp["protected_branches"])
        self.assertEqual(self.policy, {"name": "main", "type": "branch"})

    def test_no_reviewers_on_team_plan(self):
        # Required reviewers are not available for private repos on GitHub Team (R3.1.2);
        # the approval gate is the ruleset on main.
        for key in ("reviewers", "wait_timer", "prevent_self_review"):
            self.assertNotIn(key, self.env)


if __name__ == "__main__":
    unittest.main()
