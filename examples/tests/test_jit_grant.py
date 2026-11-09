"""E16: pre-grant check of the JIT flow (framework layer 7, ADR-0005, OD33).

Proves the [design] rules: an Identity Center grant is made only for an authentic, fresh webhook
(J1) that records a person moving the request to Approved (J2), where the approver is not the
requester (J3), is on shift and the incident is open (J4), and the permission set is an allowed
InfraOperator set given to the requester for 60 minutes (J5). Fails closed on bad input.

Does NOT prove: the receiver, its secret storage, the Identity Center call or the deletion
schedule, nor Linear's real payload shape (assumed, see check.py).
"""
import copy
import hashlib
import hmac
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "jit-grant"))
import check  # noqa: E402

SECRET = "placeholder-not-a-real-secret"
EVENT = {
    "action": "update", "type": "Issue", "createdAt": "2026-11-09T02:00:00Z",
    "actor": {"id": "lin-bob", "type": "User"},
    "data": {"identifier": "JIT-12", "state": "Approved", "creatorId": "lin-alice",
             "incidentId": "INC-7", "permissionSet": "InfraOperator-claims"},
    "updatedFrom": {"state": "Requested"},
}
CTX = {"now": "2026-11-09T02:00:20Z",
       "people": {"lin-alice": "idc-alice", "lin-bob": "idc-bob"},
       "on_shift": ["idc-bob"], "open_incidents": ["INC-7"],
       "permission_sets": ["InfraOperator-claims", "InfraOperator-underwriting"]}


def run(event=None, ctx=None, secret=SECRET, tamper=False):
    raw = json.dumps(event or EVENT).encode()
    header = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    if tamper:
        raw = raw.replace(b"InfraOperator-claims", b"InfraOperator-underwriting")
    return check.decide(raw, header, SECRET, ctx or CTX)


def changed(**kw):
    e = copy.deepcopy(EVENT)
    for k, v in kw.items():
        if k in e["data"]:
            e["data"][k] = v
        else:
            e[k] = v
    return e


class JitGrantTest(unittest.TestCase):
    def test_valid_approval_grants_requester_for_one_hour(self):
        grant, reasons = run()
        self.assertEqual(reasons, [])
        self.assertEqual(grant, {"principal": "idc-alice", "permission_set": "InfraOperator-claims",
                                 "minutes": 60, "request": "JIT-12"})

    def test_forged_or_tampered_or_old_webhook_is_refused(self):
        self.assertIsNone(run(secret="wrong")[0])
        self.assertIsNone(run(tamper=True)[0])
        self.assertIsNone(run(ctx=dict(CTX, now="2026-11-09T02:05:00Z"))[0])

    def test_only_a_person_moving_it_to_approved(self):
        self.assertIsNone(run(changed(actor={"id": "lin-bob", "type": "Integration"}))[0])
        self.assertIsNone(run(changed(updatedFrom={"title": "x"}))[0])  # state did not change
        self.assertIsNone(run(changed(state="Requested"))[0])

    def test_requester_cannot_approve_own_request(self):
        grant, reasons = run(changed(actor={"id": "lin-alice", "type": "User"}),
                             dict(CTX, on_shift=["idc-alice"]))
        self.assertIsNone(grant)
        self.assertIn("J3: approver is the requester", reasons)

    def test_unknown_people_are_refused(self):
        self.assertIsNone(run(changed(actor={"id": "lin-mallory", "type": "User"}))[0])

    def test_approver_on_shift_and_incident_open(self):
        self.assertIsNone(run(ctx=dict(CTX, on_shift=[]))[0])
        self.assertIsNone(run(ctx=dict(CTX, open_incidents=[]))[0])

    def test_only_allowed_infraoperator_sets(self):
        self.assertIsNone(run(changed(permissionSet="AdministratorAccess"))[0])
        self.assertIsNone(run(changed(permissionSet="InfraOperator-payments"))[0])  # not listed

    def test_one_grant_per_request(self):
        # J6: a retried webhook or a second move to Approved does not grant again.
        self.assertIsNotNone(run()[0])
        grant, reasons = run(ctx=dict(CTX, granted_requests=["JIT-12"]))
        self.assertIsNone(grant)
        self.assertIn("J6: this request was already granted once", reasons)

    def test_unreadable_input_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            body, ctx = os.path.join(d, "body.json"), os.path.join(d, "ctx.json")
            with open(body, "w") as f:
                f.write("{not json")
            with open(ctx, "w") as f:
                json.dump(dict(CTX, signature_header="00"), f)
            env = dict(os.environ, JIT_WEBHOOK_SECRET=SECRET, PYTHONDONTWRITEBYTECODE="1")
            p = subprocess.run([sys.executable, os.path.join(HERE, "..", "jit-grant", "check.py"), body, ctx],
                               capture_output=True, env=env)
            self.assertEqual(p.returncode, 1)  # bad signature: refused before parsing
            raw = b"{not json"
            with open(ctx, "w") as f:
                json.dump(dict(CTX, signature_header=hmac.new(SECRET.encode(), raw, hashlib.sha256).hexdigest()), f)
            p = subprocess.run([sys.executable, os.path.join(HERE, "..", "jit-grant", "check.py"), body, ctx],
                               capture_output=True, env=env)
            self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
