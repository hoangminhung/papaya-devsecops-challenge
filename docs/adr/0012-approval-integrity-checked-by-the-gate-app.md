# ADR-0012: Approval integrity is checked by the approval-gate app: two approvals on process paths, on-call approvals only for open incidents

- **Status:** Accepted; supersedes in part ADR-0003 (domain review on normal days as a process rule; one approval for cross-team PRs, OD10) and ADR-0010 (one approver for L3 process paths)
- **Date:** 2026-11-09
- **Decided by:** owner of this submission, after the independent review (`work/07-review.md`; OD26, OD27)
- **Scope:** pull requests to `main` of the monorepo; the `approval-gate` required check

## 1. Context

ADR-0003 made the merge to `main` the approval gate, with an on-call group that co-owns every
deployable path, so that one primary can approve any fix at night. GitHub accepts an approval from
any listed owner (📖 R3.2.7), so on normal days that group could approve any domain's PR, and the
`incident` label that was meant to limit this can be applied by anyone with Triage (📖 R9.1.9).
ADR-0010 kept one approver for every level. The review also found that a compromised plugin or
local MCP server runs on every laptop and could give an attacker many GitHub logins at once
(threat T23), so a single approval on the files that define the process is one stolen login away.
A path-scoped reviewer rule was not found for GitHub Team (📖 R9.1.15), and the ruleset's approval
count is repository-wide.

## 2. Options considered

| Option | Pros | Cons |
|---|---|---|
| A. Keep process rules and the monthly report | No new logic | The label is free to apply; the report misses labelled PRs; one login changes the process |
| B. Raise the ruleset to two approvals for every PR | Built into GitHub | Doubles review for every change, against S4 and the owner's two-person rule |
| C. The approval-gate app, already required, checks the rules per file | Exact rules per path; works on Team | More logic in a custom app that every merge depends on (G19) |

## 3. Decision

Option C [design]. The app's decision logic is examples E12 (`examples/approval-gate/gate.py`):

- an approval counts only if it is on the head commit, or on an earlier commit with the same diff
  against its merge base (OD31), by a human who is not the author, the last pusher of a change to
  that diff or the person who triggered an app-opened PR (📖 R9.1.10 for the review fields);
- every changed file needs a counted approval from one of its owner teams;
- an on-call group member's approval counts for another team's file only if the PR carries the
  `incident` label, links an incident that is open when the check runs, and the approver is on
  shift (OD27);
- a file owned only by the L3 owner team (a process path, including the IAM stack since OD32) needs
  two different members of that team (OD26);
- approvals within two minutes of the last push, or at night without an incident, are flagged for
  the monthly report, not blocked.

## 4. Consequences

- **Positive:** domain review on normal days and the two-person rule on process paths are enforced,
  not trained; the incident lane cannot be opened by a label alone; flagged approvals give a
  detection signal for rubber-stamping and stolen logins.
- **Negative / trade-offs:** process-path PRs need two L3 owner team members; a cross-team PR on a
  normal day needs an owner of each team (OD10's single approval now holds only in incidents);
  a stale schedule or incident record blocks a night approval until the backup or a domain owner
  approves; every merge depends more on the app.
- **Risks & how we watch them:** if the app is down, every merge is blocked, incident PRs included,
  and the JIT fallback applies (layer 7); its hosting, key and triggers stay open (G19); the schedule
  file is an L3 path; the monthly report lists every `incident` PR and every flagged approval.
- **Next steps:** the app becomes a hard prerequisite in phase 1, before the ruleset requires its
  check (rollout).

## 5. References

- Framework layer 3 ("L3 approvals", "Who approves at night"), layer 4 ("Pinning what every
  laptop runs"), layer 7 (on-call); threat model T7, T23.
- Related: ADR-0003, ADR-0006, ADR-0010.
