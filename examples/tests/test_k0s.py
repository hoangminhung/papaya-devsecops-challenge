"""E11: interim k0s deploy credential and API audit policy (framework layers 5 and 7; OD24).

Proves the [design] rules hold in the files: the deploy ServiceAccount gets a namespaced Role
without the escalation paths listed in Kubernetes' RBAC good practices (R9.3.7), and the audit
policy keeps Secret and token contents out of the log (R9.3.3).

Does NOT prove: that a k0s cluster accepts these files (no cluster here), that k0s passes the
audit flags through `spec.api.extraArgs` as expected (outside k0s support, R9.3.1), or anything
about the target authentication config, which is untested.
"""
import os
import unittest

import yaml

HERE = os.path.dirname(__file__)
K0S = os.path.join(HERE, "..", "k0s")

# Resources and verbs the deploy credential must never hold (R9.3.7).
FORBIDDEN_RESOURCES = {
    "secrets", "pods/exec", "pods/attach", "pods/portforward", "pods/log", "serviceaccounts",
    "serviceaccounts/token", "roles", "rolebindings", "clusterroles", "clusterrolebindings",
    "nodes", "nodes/proxy", "*",
}
FORBIDDEN_VERBS = {"escalate", "bind", "impersonate", "delete", "deletecollection", "*"}


def load_all(name):
    with open(os.path.join(K0S, name)) as f:
        return [d for d in yaml.safe_load_all(f) if d]


class DeployRbacTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = {d["kind"]: d for d in load_all("deploy-rbac.yaml")}

    def test_namespaced_only(self):
        self.assertEqual(set(self.docs), {"ServiceAccount", "Role", "RoleBinding"})
        ns = {d["metadata"]["namespace"] for d in self.docs.values()}
        self.assertEqual(len(ns), 1, "one namespace per deploy credential")
        self.assertEqual(self.docs["RoleBinding"]["roleRef"]["kind"], "Role")

    def test_no_escalation_paths(self):
        for rule in self.docs["Role"]["rules"]:
            with self.subTest(rule=rule):
                self.assertFalse(set(rule["resources"]) & FORBIDDEN_RESOURCES)
                self.assertFalse(set(rule["verbs"]) & FORBIDDEN_VERBS)
                self.assertNotIn("*", rule["apiGroups"])

    def test_token_not_mounted(self):
        self.assertIs(self.docs["ServiceAccount"]["automountServiceAccountToken"], False)

    def test_binding_targets_the_deploy_account_only(self):
        sa = self.docs["ServiceAccount"]["metadata"]
        [subject] = self.docs["RoleBinding"]["subjects"]
        self.assertEqual((subject["kind"], subject["name"], subject["namespace"]),
                         ("ServiceAccount", sa["name"], sa["namespace"]))


class AuditPolicyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        [cls.policy] = load_all("audit-policy.yaml")

    def test_secret_contents_never_logged(self):
        first = self.policy["rules"][0]
        self.assertEqual(first["level"], "Metadata")
        names = {r for g in first["resources"] for r in g.get("resources", [])}
        self.assertLessEqual({"secrets", "configmaps", "serviceaccounts/token"}, names)

    def test_no_rule_logs_response_bodies(self):
        for rule in self.policy["rules"]:
            self.assertNotEqual(rule["level"], "RequestResponse")

    def test_everything_else_is_logged(self):
        last = self.policy["rules"][-1]
        self.assertEqual(set(last), {"level"}, "catch-all rule last")
        self.assertNotEqual(last["level"], "None")

    def test_k0s_fragment_points_at_the_policy(self):
        [cfg] = load_all("k0s-apiserver-audit.yaml")
        args = cfg["spec"]["api"]["extraArgs"]
        self.assertTrue(args["audit-policy-file"].endswith("audit-policy.yaml"))
        self.assertTrue(args["audit-log-path"])


class TargetAuthenticationTest(unittest.TestCase):
    def test_only_the_k0s_environment_is_trusted(self):
        [cfg] = load_all("authentication-config.target.yaml")
        [jwt] = cfg["jwt"]
        self.assertEqual(jwt["issuer"]["url"], "https://token.actions.githubusercontent.com")
        [rule] = jwt["claimValidationRules"]
        self.assertRegex(rule["expression"], r'claims\.sub == ".*:environment:production-k0s"$')


if __name__ == "__main__":
    unittest.main()
