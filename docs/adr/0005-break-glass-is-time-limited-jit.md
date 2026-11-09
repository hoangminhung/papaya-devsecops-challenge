# ADR-0005: Break-glass is a time-limited, approved JIT grant, for incidents only

- **Status:** Accepted
- **Date:** 2026-11-09
- **Decided by:** owner of this submission (GĐ-8; Options §9 Q2; D2; OD7, OD13)
- **Scope:** AWS production accounts through IAM Identity Center; k0s and Firebase not covered (G1, G2)

## 1. Context

Some incidents cannot use the PR path: GitHub or Actions is down, the pipeline is broken, or the
operation is not in IaC and has no runbook. Without a defined fallback, people keep standing access
"just in case", which ADR-0002 removes.

## 2. Options considered

| Option | Pros | Cons |
|---|---|---|
| A. No fallback | Single path | Outage of GitHub blocks every fix; pressure to keep standing access |
| B. Standing break-glass account, used first and approved later | Always available | Standing prod write; unapproved use, rejected by the owner (GĐ-8, Options §0.4) |
| C. Approved JIT grant, 1-hour role session, command list, reconciled after | Approval before use; time-boxed; traceable | Approves a command list, not an applied change (partial) |

## 3. Decision

Option C [design], used only during an incident when the PR path cannot be used.

- **Request:** command list, scope, reason, incident link, in a channel that does not depend on GitHub.
- **Approval:** the on-call approver ≠ requester, before the grant; the on-call approver counts as
  owner of the service (OD13).
- **Grant:** `InfraOperator-<service>` [design name], assigned via `CreateAccountAssignment` and removed
  via `DeleteAccountAssignment` (📖 R2.4.2); role session 1 h (📖 R2.1.4).
- **Execution:** the incident responder types the commands in a terminal without an agent (D2, OD7).
- **Example request** (illustrative command ⚠️): "INC-123, ECS service `claims-api`, Actions outage.
  Run `aws ecs update-service --cluster <prod-cluster> --service <svc> --force-new-deployment`. Scope
  `InfraOperator-claims`, 1 h."
- **After:** CloudTrail writes in the window are compared with the list; a codify PR follows by a
  fixed deadline; drift detection runs until it merges.

## 4. Consequences

- **Positive:** no standing prod write even for emergencies; every use has an approval, a window and
  a reconciliation.
- **Negative / trade-offs:** meets the approval rule only partly (owner accepted). "No agent in the
  JIT terminal" is a process rule: the grant is reachable from the same laptop.
- **Risks & how we watch them:** deleting the assignment likely stops only new sessions, so a grant
  can run up to about 2 h (⚠️ R2.4.2, R2.9 #3). An immediate stop needs the revocation SCP, which keeps
  the user blocked ≥ 12 h (📖 R2.4.4); no night-time path to apply it is designed yet (⚠️ G20).
  Metrics: JIT used where a PR was possible, writes outside the list, late codify PRs (review at 1).
- **Next steps:** minimal JIT with per-grant CloudTrail comparison and a manual drift check of the
  touched stacks in phase 1 (a temporary deviation from D2); revocation SCP and
  automated reconciliation in phase 2.

## 5. References

- Framework layer 7 ("Break-glass = JIT fallback"); `work/03-options.md` §4b, §9.
- Related: ADR-0001, ADR-0002.
