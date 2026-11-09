"""E12: decision logic of the `approval-gate` required check (framework layer 3; OD26, OD27; G19).

Proves the [design] rules: which approvals count (R1, including an unchanged diff after a branch
update, OD31), domain review enforced on normal days and
on-call approvals only with an open incident and on shift (R2, OD27), two L3 approvals on process
paths (R3, OD26), and warnings that feed the monthly report (W1).

Does NOT prove: anything about the GitHub App around it (hosting, key, triggers, and how it reads
reviews, teams, incidents and the schedule: G19), nor that GitHub treats its check as required.
"""
import copy
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "approval-gate"))
import gate  # noqa: E402

HEAD = "a" * 40
CLAIMS_FILE = "services/claims/serverless.yml"
WORKFLOW_FILE = ".github/workflows/deploy-prod.yml"

BASE = {
    "pr": {"author": "alice", "last_pusher": "alice", "triggered_by": None, "head_sha": HEAD, "diff_ids": {},
           "last_push_at": "2026-11-09T03:00:00Z", "labels": [], "incident_id": None,
           "files": {CLAIMS_FILE: ["team-claims", "oncall-approvers"]}},
    "reviews": [],
    "teams": {"team-claims": ["alice", "frank"], "oncall-approvers": ["bob", "carol"],
              "l3-owners": ["dan", "erin", "bob"]},
    "open_incidents": [], "on_shift": [],
}


def review(user, at="2026-11-09T03:30:00Z", state="APPROVED", commit=HEAD, user_type="User"):
    return {"user": user, "user_type": user_type, "state": state, "commit_id": commit, "submitted_at": at}


def case(**changes):
    d = copy.deepcopy(BASE)
    for key, value in changes.items():
        if key in d["pr"]:
            d["pr"][key] = value
        else:
            d[key] = value
    return d


class ApprovalGateTest(unittest.TestCase):
    def passes(self, data):
        return gate.decide(data)[0]

    def test_domain_owner_approval_passes(self):
        self.assertTrue(self.passes(case(reviews=[review("frank")])))

    def test_author_last_pusher_and_trigger_never_count(self):
        self.assertFalse(self.passes(case(reviews=[review("alice")])))
        self.assertFalse(self.passes(case(last_pusher="frank", reviews=[review("frank")])))
        self.assertFalse(self.passes(case(author="ci-agent[bot]", triggered_by="frank",
                                          reviews=[review("frank")])))

    def test_stale_bot_and_withdrawn_approvals_never_count(self):
        self.assertFalse(self.passes(case(reviews=[review("frank", commit="b" * 40)])))
        self.assertFalse(self.passes(case(reviews=[review("frank", user_type="Bot")])))
        later = review("frank", at="2026-11-09T03:40:00Z", state="CHANGES_REQUESTED")
        self.assertFalse(self.passes(case(reviews=[review("frank"), later])))

    def test_branch_update_keeps_approval_when_the_changes_are_the_same(self):
        # OD31: an approval on an earlier commit counts if the PR's diff against its merge base is
        # unchanged ("Update branch" after another merge); a changed diff, or no ID, does not.
        old = "b" * 40
        same = case(diff_ids={HEAD: "p1", old: "p1"}, reviews=[review("frank", commit=old)])
        self.assertTrue(self.passes(same))
        changed = case(diff_ids={HEAD: "p2", old: "p1"}, reviews=[review("frank", commit=old)])
        self.assertFalse(self.passes(changed))
        missing = case(diff_ids={old: "p1"}, reviews=[review("frank", commit=old)])
        self.assertFalse(self.passes(missing))
        none_both = case(diff_ids={}, reviews=[review("frank", commit=old)])
        self.assertFalse(self.passes(none_both))

    def test_oncall_cross_domain_needs_open_incident_and_shift(self):
        # OD27: the label alone grants nothing (anyone with Triage can apply it, R9.1.9).
        self.assertFalse(self.passes(case(reviews=[review("bob")])))
        self.assertFalse(self.passes(case(labels=["incident"], reviews=[review("bob")])))
        self.assertFalse(self.passes(case(labels=["incident"], incident_id="INC-1",
                                          reviews=[review("bob")], on_shift=["bob"])))  # not open
        self.assertFalse(self.passes(case(labels=["incident"], incident_id="INC-1",
                                          open_incidents=["INC-1"], reviews=[review("bob")])))  # off shift
        self.assertTrue(self.passes(case(labels=["incident"], incident_id="INC-1", open_incidents=["INC-1"],
                                         on_shift=["bob"], reviews=[review("bob")])))

    def test_process_path_needs_two_l3_approvals(self):
        files = {WORKFLOW_FILE: ["l3-owners"]}
        self.assertFalse(self.passes(case(files=files, reviews=[review("dan")])))
        self.assertFalse(self.passes(case(files=files, reviews=[review("dan"), review("frank")])))
        self.assertTrue(self.passes(case(files=files, reviews=[review("dan"), review("erin")])))
        # an incident does not lower it: process paths are not co-owned by the on-call group
        self.assertFalse(self.passes(case(files=files, labels=["incident"], incident_id="INC-1",
                                          open_incidents=["INC-1"], on_shift=["dan"],
                                          reviews=[review("dan")])))

    def test_every_file_needs_its_owner(self):
        files = {CLAIMS_FILE: ["team-claims", "oncall-approvers"], WORKFLOW_FILE: ["l3-owners"]}
        _, reasons, _ = gate.decide(case(files=files, reviews=[review("dan"), review("erin")]))
        self.assertEqual(len(reasons), 1)
        self.assertIn(CLAIMS_FILE, reasons[0])

    def test_warnings_quick_or_night_approval(self):
        _, _, warnings = gate.decide(case(reviews=[review("frank", at="2026-11-09T03:00:30Z")]))
        self.assertTrue(any("after the last push" in w for w in warnings))
        # 16:30 UTC = 23:30 local (UTC+7), no incident
        _, _, warnings = gate.decide(case(last_push_at="2026-11-09T15:00:00Z",
                                          reviews=[review("frank", at="2026-11-09T16:30:00Z")]))
        self.assertTrue(any("at night" in w for w in warnings))
        _, _, warnings = gate.decide(case(reviews=[review("frank")]))
        self.assertEqual(warnings, [])
        # 15:30 UTC is 22:30 in Bangkok (UTC+7) but 23:30 in Hong Kong (UTC+8); 14:30 UTC is
        # 21:30 / 22:30: the same approval is night-time only for the Hong Kong approver.
        hk = case(last_push_at="2026-11-09T13:00:00Z", reviews=[review("frank", at="2026-11-09T14:30:00Z")])
        self.assertEqual(gate.decide(hk)[2], [])
        hk["utc_offsets"] = {"frank": 8}
        self.assertTrue(any("at night" in w for w in gate.decide(hk)[2]))

    def test_data_fix_needs_the_tenant_data_owner(self):
        # R4, OD29: L3-data-write = a code owner plus a different person from the data owners.
        files = {"db/claims/data-fixes/tenant-a/LIN-1.sql": ["team-claims", "oncall-approvers"]}
        teams = dict(BASE["teams"], **{"data-owners-tenant-a": ["frank", "grace"]})
        self.assertFalse(self.passes(case(files=files, teams=teams, reviews=[review("frank")])))  # one person
        self.assertTrue(self.passes(case(files=files, teams=teams, reviews=[review("frank"), review("grace")])))
        # in an incident the on-call approver stands in; the data owner reviews next working day
        night = case(files=files, teams=teams, labels=["incident"], incident_id="INC-1",
                     open_incidents=["INC-1"], on_shift=["bob"], reviews=[review("bob")])
        passed, _, warnings = gate.decide(night)
        self.assertTrue(passed)
        self.assertTrue(any("next working day" in w for w in warnings))
        # a tenant without a data-owner team fails closed, even with two approvals
        other = {"db/claims/data-fixes/tenant-b/LIN-2.sql": ["team-claims", "oncall-approvers"]}
        self.assertFalse(self.passes(case(files=other, teams=teams, reviews=[review("frank"), review("grace")])))

    def test_cli_fails_closed(self):
        tmp = tempfile.mkdtemp()
        try:
            good, bad = os.path.join(tmp, "good.json"), os.path.join(tmp, "bad.json")
            with open(good, "w") as f:
                json.dump(case(reviews=[review("frank")]), f)
            with open(bad, "w") as f:
                f.write("{")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(gate.main([good]), 0)
                self.assertEqual(gate.main([bad]), 2)
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
