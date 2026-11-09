#!/usr/bin/env python3
"""Decision logic of the `approval-gate` required check (framework layer 3; gap G19) [design].

The GitHub App that runs this (hosting, key storage, triggers: still open, G19) collects the
input below from GitHub (PR, reviews, CODEOWNERS owners per file, team members), from the
incident register and from the on-call schedule, and posts the result as the `approval-gate`
check, which the ruleset requires (E1). This file is the part that can be written and tested
without a live system.

  exit 0  pass: every rule holds
  exit 1  fail: the check stays red, merge is blocked
  exit 2  input cannot be read: fail closed

Rules:
  R1  An approval counts only if it is an APPROVED review by a human, who is not the author,
      not the last pusher and not the person who triggered an app-opened PR (layer 5; OD5),
      on the PR's head commit or on an earlier commit whose diff against its merge base is the
      same as the head's (OD31). So "Update branch" after another merge to `main` does not cost
      a new approval as long as the PR's own changes are unchanged; a push that changes them
      does. GitHub itself dismisses an approval as stale when the diff changes (📖 GitHub docs,
      "About protected branches"); the gate checks the same thing itself instead of trusting
      it. Reviews carry `commit_id`, `submitted_at`, `user` (📖 R9.1.10).
  R2  Every changed file needs a counted approval from a member of one of its owner teams.
      An approval from the on-call group counts for a file of another team only if the PR
      carries the `incident` label, links an incident that is open now, and the approver is on
      shift now (OD27). Anyone with Triage can apply a label (📖 R9.1.9), so the label alone
      grants nothing.
  R3  A file owned only by the L3 owner team (a process path: workflows, CODEOWNERS, agent
      config, catalogue, SCP and IAM stacks, risk stop, ...) needs counted approvals from TWO different
      L3 owner team members (OD26). The ruleset keeps one approval for the rest of the repository,
      because a path-scoped reviewer rule was not found for GitHub Team (📖 R9.1.15).
  R4  A data fix (`db/<service>/data-fixes/<tenant>/...`, L3-data-write, OD29) needs, besides the
      R2 approval, an approval from a different person who is a member of the team
      `data-owners-<tenant>`. The tenant comes from the path, not from CODEOWNERS, so data owners
      need only read access to the repository, not write (a code owner must have write); a tenant
      without such a team fails the check (fail closed). In an incident the on-call approver stands in for the data owner,
      who reviews it the next working day (layer 6); the check passes with a warning.
  W1  Warning, not a failure: an approval submitted less than MIN_REVIEW_SECONDS after the last
      push, or between 22:00 and 06:00 in the approver's own time zone without an open incident. Warnings go to the
      monthly report (layer 7) as signals of rubber-stamping or of an approval made through a
      compromised login (threat T23). Nothing here can tell a web approval from an API one
      (📖 R9.1.10).

Input JSON:
  {"pr": {"author": "a", "last_pusher": "a", "triggered_by": null, "head_sha": "<sha>",
          "diff_ids": {"<sha>": "<patch id>"}, "last_push_at": "...", "labels": ["incident"], "incident_id": "INC-12",
          "files": {"services/claims/serverless.yml": ["team-claims", "oncall-approvers"]}},
   "reviews": [{"user": "b", "user_type": "User", "state": "APPROVED", "commit_id": "<sha>",
                "submitted_at": "..."}],
   "teams": {"team-claims": ["a", "c"], "oncall-approvers": ["b"], "l3-owners": ["d", "e"]},
   "open_incidents": ["INC-12"], "on_shift": ["b"], "utc_offsets": {"b": 8}}
  `diff_ids` maps commit SHAs of the PR to the patch ID of the PR's changes at that commit:
  `git diff $(git merge-base origin/main <sha>) <sha> | git patch-id --stable` (✅ `git patch-id`
  has `--stable` in git here). `last_pusher` and `last_push_at` are those of the last push that
  changed the patch ID, so a branch update that leaves the PR's changes alone does not make the
  updater the last pusher. A missing ID never matches (fail closed).
  `open_incidents` and `on_shift` are read by the app when the check runs: in phase 1 from the
  incident issues in Linear and the schedule file `oncall/schedule.yaml` (an L3 path); from
  phase 2 from the paging tool (G5).
"""
import datetime
import json
import re
import sys

ONCALL = "oncall-approvers"
L3 = "l3-owners"
DATA_OWNERS = "data-owners-"
DATA_FIX = re.compile(r"^db/[^/]+/data-fixes/([^/]+)/")
MIN_REVIEW_SECONDS = 120  # [design] calibrate from the first months of data
NIGHT_START, NIGHT_END = 22, 6  # local hours, [design]
DEFAULT_UTC_OFFSET = 7  # Vietnam, Thailand; Hong Kong is +8, so offsets come per approver


def _time(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def counted_approvals(data):
    """R1: the approvals that count, latest per user."""
    pr = data["pr"]
    excluded = {pr["author"], pr["last_pusher"], pr.get("triggered_by")}
    diff_ids = pr.get("diff_ids") or {}
    head_diff = diff_ids.get(pr["head_sha"])

    def same_changes(commit):
        return commit == pr["head_sha"] or (head_diff is not None and diff_ids.get(commit) == head_diff)

    latest = {}
    for r in sorted(data["reviews"], key=lambda r: r["submitted_at"]):
        latest[r["user"]] = r  # a later review (e.g. changes requested) replaces an earlier one
    return [r for r in latest.values()
            if r["state"] == "APPROVED" and same_changes(r["commit_id"])
            and r.get("user_type", "User") == "User" and r["user"] not in excluded]


def incident_active(data):
    pr = data["pr"]
    return "incident" in pr.get("labels", []) and pr.get("incident_id") in data.get("open_incidents", [])


def decide(data):
    """Return (passed, reasons, warnings)."""
    teams, pr = data["teams"], data["pr"]
    approvals = counted_approvals(data)
    approvers = {r["user"] for r in approvals}
    on_shift = set(data.get("on_shift", []))
    incident = incident_active(data)
    reasons, warnings = [], []

    for path, owners in sorted(pr["files"].items()):
        if owners == [L3]:  # R3: process path
            l3 = approvers & set(teams.get(L3, []))
            if len(l3) < 2:
                reasons.append(f"{path}: process path, needs 2 approvals from {L3} (has {len(l3)})")
            continue
        code_owners = owners
        m = DATA_FIX.match(path)
        data_teams = [DATA_OWNERS + m.group(1)] if m else []
        r2_users, oncall_users = set(), set()
        for user in approvers:  # R2
            domain = any(user in teams.get(t, []) for t in code_owners if t != ONCALL)
            oncall = ONCALL in code_owners and user in teams.get(ONCALL, []) and incident and user in on_shift
            if domain or oncall:
                r2_users.add(user)
            if oncall:
                oncall_users.add(user)
        if not r2_users:
            hint = "" if incident else " (on-call approvals count only with an open incident and on shift)"
            reasons.append(f"{path}: no counted approval from {', '.join(code_owners)}{hint}")
        elif data_teams and data_teams[0] not in teams:  # R4, fail closed
            reasons.append(f"{path}: no data-owner team {data_teams[0]} for this tenant")
        elif data_teams:  # R4
            data_users = {u for u in approvers for t in data_teams if u in teams.get(t, [])}
            if any(d != u for d in data_users for u in r2_users):
                pass
            elif oncall_users:
                warnings.append(f"{path}: data owner stood in for by the on-call approver; review due next working day")
            else:
                reasons.append(f"{path}: data fix needs a second approval from {', '.join(data_teams)}")

    last_push = _time(pr["last_push_at"])
    for r in approvals:  # W1
        t = _time(r["submitted_at"])
        if (t - last_push).total_seconds() < MIN_REVIEW_SECONDS:
            warnings.append(f"{r['user']}: approved {int((t - last_push).total_seconds())} s after the last push")
        offset = data.get("utc_offsets", {}).get(r["user"], DEFAULT_UTC_OFFSET)
        local_hour = (t.hour + offset) % 24
        if (local_hour >= NIGHT_START or local_hour < NIGHT_END) and not incident:
            warnings.append(f"{r['user']}: approved at night without an open incident")
    if not approvals:
        reasons.append("no counted approval")
    return not reasons, reasons, warnings


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        with open(argv[0]) as f:
            data = json.load(f)
        passed, reasons, warnings = decide(data)
    except Exception as e:  # fail closed
        print(f"approval-gate: cannot read input ({type(e).__name__}: {e}); failing", file=sys.stderr)
        return 2
    for line in reasons:
        print("FAIL", line)
    for line in warnings:
        print("WARN", line)
    print("approval-gate:", "pass" if passed else "fail")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
