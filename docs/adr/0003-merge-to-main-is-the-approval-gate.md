# ADR-0003: The merge to `main` is the approval gate: two people, code owners, on-call co-ownership

- **Status:** Accepted; superseded in part by [ADR-0012](0012-approval-integrity-checked-by-the-gate-app.md)
  (which approvals count, two approvers on process paths, on-call approvals only in an incident)
- **Date:** 2026-11-09
- **Decided by:** owner of this submission (GĐ-5, GĐ-8, GĐ-11; OD2, OD5, OD7, OD9, OD10, OD13)
- **Scope:** GitHub monorepo rulesets, CODEOWNERS, `production` environment, on-call schedule

## 1. Context

Papaya is assumed to be on GitHub Team (GĐ-5), where environment required reviewers do not exist for
private repositories (📖 R3.1.2), so the approval must happen before the deploy job. Incidents need an
approver within 15 minutes, 24/7 (S7), and code-owner review requires an approval from an owner of the files (📖 R3.2.3, R3.2.7;
per-file behaviour ⚠️).

## 2. Options considered

| Option | Pros | Cons |
|---|---|---|
| A. Upgrade to Enterprise for environment reviewers | Approval sits next to the deploy | Cost; not assumed (GĐ-5) |
| B. Merge to `main` as the gate; `production` limited to `main` | Works on Team; the approver sees the code that will be applied | Nobody sees the prod diff before apply (partly handled by ADR-0004) |
| C. More approvers for high-risk changes | More eyes | Slower; the owner wants two people per change |

## 3. Decision

Option B. Ruleset on `main`: PR required, 1 approval, code-owner review, dismiss stale approvals,
approval by someone other than the last pusher, required checks from a pinned source app, no force
push, empty bypass list (📖 R3.2.2, R3.2.3, R3.2.5); branch up to date, since there is no merge queue
(⚠️ R4.6 #1). `production` accepts only `main` (📖 R3.1.3).

- **Merge = deploy approval** only if the reusable deploy workflow alone references `production`,
  with no ref/SHA inputs, no `issue_comment`, `pull_request_target` or `workflow_run` triggers, one
  concurrency group per stack without `cancel-in-progress` (📖 R4.1.4; ⚠️ R3.6 #1, from 📖 R3.1.3, R3.4.5c).
- **Two people per change:** one makes it, one approves it; the approver is always an engineer,
  never an agent (OD2, OD5). L3 changes need one approver too, who must own the path.
- **Incidents:** on-call engineers only approve; an incident responder writes the fix (OD7).
- **Night coverage:** an on-call approver group co-owns every deployable path in CODEOWNERS; one
  primary, one backup (OD9). It does not co-own process-defining paths (`.github/**`, CODEOWNERS,
  agent config, catalogue) or the SCP stack, which only the L3 owner team approves (OD13); IAM-only
  stacks are deployable, so it co-owns them with the L3 owner team. *Superseded by OD32: the IAM
  stack is a process path, L3 owner team only.*
- **Agent review:** an independent agent may post an automated review; it never counts as an
  approval (GĐ-11).
- **Cross-team PRs:** one approval is enough (OD10). *Superseded by ADR-0012: each team's files need
  their own owner's approval; the on-call approval covers another team's files only in an incident (OD27).*

## 4. Consequences

- **Positive:** four-eyes enforced by GitHub, not by the agent; one rule for normal days and incidents.
- **Negative / trade-offs:** GitHub accepts an approval from any listed owner (📖 R3.2.7), so the
  on-call group can approve another domain's PR; domain review on normal days is a process rule.
- **Risks & how we watch them:** admins can edit the gate, logged, not prevented (⚠️ R3.2.2, R3.6 #1;
  logging 📖 R3.2.2); alerts on ruleset changes; monthly report of cross-domain approvals. An agent could approve through its engineer's login; no detection found (⚠️). The
  required-check app's hosting, key and triggers are open (⚠️ G19).
- **Next steps:** rulesets, CODEOWNERS and its validation check in phase 1; the required-check app
  before any agent workflow may open PRs; L3 owner team composition open (G17).

## 5. References

- Framework layer 3 ("Gate = merge to `main`", "Who approves at night"), layer 7 (audit alerts).
- Related: ADR-0001, ADR-0004.
