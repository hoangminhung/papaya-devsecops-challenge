"""OD48: the `data-fix-scan` required check keeps personal data out of data-fix files in git.

Proves: a field-name-plus-value match of any E14 identifier, or a run of 9+ digits, under
db/<service>/data-fixes/ fails the check; migrations and opaque IDs pass; output names the rule,
never the value; unreadable input fails closed. Synthetic values only.
Does NOT prove: that Papaya's real IDs never take a shape the rules miss (free text, short IDs).
"""
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(__file__)
SCRIPT = os.path.join(HERE, "..", "db", "check_data_fixes.py")
POLICY = os.path.join(HERE, "..", "aws", "logs-data-protection-policy.json")


def run(files, policy=POLICY):
    with tempfile.TemporaryDirectory() as root:
        for path, text in files.items():
            full = os.path.join(root, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w") as f:
                f.write(text)
        p = subprocess.run([sys.executable, "-I", SCRIPT, root, policy], capture_output=True, text=True,
                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        return p.returncode, p.stdout


class DataFixScanTest(unittest.TestCase):
    FIX = "db/claims/data-fixes/tenant-a/LIN-1.sql"

    def test_opaque_ids_and_psql_variables_pass(self):
        code, _ = run({self.FIX: "-- expected_rows: 1\nUPDATE payouts SET account_ref = :'new_account'\n"
                                 "WHERE payout_id = 'pay_8f3a2c';\n"})
        self.assertEqual(code, 0)

    def test_identifier_values_fail_without_printing_them(self):
        for text in ("UPDATE p SET bank_account = '00112233445566' WHERE id = 'pay_1';",
                     "UPDATE c SET national_id = '079912345678' WHERE id = 'clm_1';",
                     "UPDATE c SET diagnosis = 'synthetic diagnosis text' WHERE id = 'clm_1';"):
            with self.subTest(text=text[:30]):
                code, out = run({self.FIX: text})
                self.assertEqual(code, 1)
                self.assertIn("F1", out)
                self.assertNotIn("0011223344", out)
                self.assertNotIn("synthetic diagnosis", out)

    def test_long_digit_runs_fail(self):
        code, out = run({self.FIX: "UPDATE p SET status = 'retry' WHERE ref = '123456789012';"})
        self.assertEqual(code, 1)
        self.assertIn("F2", out)

    def test_only_data_fixes_are_scanned(self):
        code, _ = run({"db/claims/migrations/001.sql": "-- 123456789012 in a comment of a migration\n"})
        self.assertEqual(code, 0)

    def test_unreadable_policy_fails_closed(self):
        code, _ = run({self.FIX: "SELECT 1;"}, policy="/nonexistent.json")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
