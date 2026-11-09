#!/usr/bin/env python3
"""Pre-grant check of the JIT flow (framework layer 7, "Break-glass"; ADR-0005; OD33) [design].

The JIT request is a Linear issue (OD30). When the on-call approver moves it to "Approved", Linear
sends a webhook to the receiver in the tooling account (the approval-gate app's account). The
receiver runs this check and calls `sso-admin:CreateAccountAssignment` only if it passes; nobody
else assigns `InfraOperator-*` (layer 1, OD23: an alert fires on any other principal's change).
This file is the part that can be written and tested without a live system.

  exit 0  grant: print the assignment to make
  exit 1  refuse: print the reasons; the request stays without a grant
  exit 2  input cannot be read: refuse (fail closed)

Rules:
  J1  The webhook is authentic: HMAC-SHA256 of the raw body with the webhook's signing secret
      equals the `Linear-Signature` header, and it was sent within 60 seconds (📖 Linear docs,
      developers/webhooks: hex-encoded HMAC-SHA256; "within a minute" recommended).
  J2  The change is the issue's state moving to "Approved" (`updatedFrom` holds the previous
      state, 📖 same page), made by a `User`, not an OAuth client or an integration (`actor`).
  J3  Approver != requester, compared as Identity Center users through the people register
      (the register of OD25, extended with Linear user IDs). Anyone not in it: refuse.
  J4  The approver is on shift now (oncall/schedule.yaml) and the linked incident is open.
  J5  The permission set is one `InfraOperator-<service>` from the allowlist; the grant goes to
      the requester only, for 60 minutes (the receiver schedules the DeleteAccountAssignment).
  J6  One grant per request: Linear retries a webhook up to 3 times (📖 same page), and an issue
      can be moved back and forth; a request ID already granted is refused, so nothing extends
      or repeats a grant. A new window needs a new request.

⚠️ The shape of `data` is assumed and is checked against a real webhook when the receiver is
built (rollout 1.13). The receiver takes as few values as possible from free text: the
permission set from one label of a `jit-scope` label group, the incident from the issue's
relation to the incident issue (whether Linear exposes relations in the webhook: ⚠️), and the
people from Linear user IDs, which must be single-sign-on accounts in the people register.

Not covered here: the receiver itself (hosting, the signing secret in the tooling account's
secrets store, the Identity Center role it assumes), the deletion schedule, and data-read
requests (`DataRead-*`), which add the data owner's approval (layer 6).
"""
import datetime
import hashlib
import hmac
import json
import os
import sys

APPROVED = "Approved"
MAX_AGE_SECONDS = 60
GRANT_MINUTES = 60
PREFIX = "InfraOperator-"


def signature_ok(raw_body, header, secret):
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header or "")


def _time(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def decide(raw_body, header, secret, ctx):
    """Return (grant or None, reasons). `ctx` is what the receiver reads when the webhook
    arrives: request fields, the people register, who is on shift, open incidents, the time."""
    reasons = []
    if not signature_ok(raw_body, header, secret):
        return None, ["J1: signature does not match"]
    event = json.loads(raw_body)
    age = (_time(ctx["now"]) - _time(event["createdAt"])).total_seconds()
    if not 0 <= age <= MAX_AGE_SECONDS:
        reasons.append(f"J1: webhook is {age:.0f} s old")

    data, before = event.get("data", {}), event.get("updatedFrom") or {}
    actor = event.get("actor") or {}
    if event.get("action") != "update" or data.get("state") != APPROVED or before.get("state") in (None, APPROVED):
        reasons.append("J2: not a change of state to Approved")
    if actor.get("type") != "User":
        reasons.append(f"J2: changed by a {actor.get('type')}, not a person")

    people = ctx["people"]  # Linear user ID -> Identity Center user ID
    requester, approver = people.get(data.get("creatorId")), people.get(actor.get("id"))
    if requester is None or approver is None:
        reasons.append("J3: requester or approver not in the people register")
    elif requester == approver:
        reasons.append("J3: approver is the requester")

    if approver not in ctx["on_shift"]:
        reasons.append("J4: approver is not on shift")
    if data.get("incidentId") not in ctx["open_incidents"]:
        reasons.append("J4: linked incident is not open")

    pset = data.get("permissionSet", "")
    if not pset.startswith(PREFIX) or pset not in ctx["permission_sets"]:
        reasons.append(f"J5: '{pset}' is not an allowed JIT permission set")

    if data.get("identifier") in ctx.get("granted_requests", []):
        reasons.append("J6: this request was already granted once")

    if reasons:
        return None, reasons
    return {"principal": requester, "permission_set": pset, "minutes": GRANT_MINUTES,
            "request": data.get("identifier")}, []


def main():
    try:
        with open(sys.argv[1], "rb") as f:
            raw = f.read()
        with open(sys.argv[2]) as f:
            ctx = json.load(f)
        secret = os.environ["JIT_WEBHOOK_SECRET"]  # from the tooling account's secrets store
        grant, reasons = decide(raw, ctx["signature_header"], secret, ctx)
    except (OSError, ValueError, KeyError, IndexError, TypeError) as e:
        print(f"refuse: input cannot be read ({e})", file=sys.stderr)
        return 2
    if grant:
        print(json.dumps(grant))
        return 0
    print("\n".join(reasons))
    return 1


if __name__ == "__main__":
    sys.exit(main())
