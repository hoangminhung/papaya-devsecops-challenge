# ADR-0001: Every production change goes through a reviewed PR applied by CI

- **Status:** Accepted
- **Date:** 2026-11-09
- **Decided by:** owner of this submission (Options §9, "A + D2'")
- **Scope:** all writes to production AWS, GCP, k0s and Firebase; incidents included (k0s and Firebase
  have no risk stop and no break-glass yet, G1, G2; human GCP access is open, G3)

## 1. Context

Engineering wants Claude Code to talk to AWS directly; Compliance wants no production change without
a named human who reviewed and approved it. "Most engineers' profiles can reach production" (brief), and deploys from laptops are assumed
(GĐ-10, unconfirmed), so an agent on that laptop can deploy too. Incidents are where the pressure to bypass
review is highest.

## 2. Options considered

| Option | Pros | Cons |
|---|---|---|
| A. PR → approval → CI deploy for everything ("IaC first") | One path, approval before apply, evidence by construction | Slower incidents (est. 11–46 min ⚠️ vs 2–20 min, Options §6) |
| B. SSM Automation runbooks with an approval step | Approval inside AWS | Not verified that it meets the approval rule (G6); only for operations someone scripted. Kept on the roadmap, verified in phase 2 (OD4) |
| C. JIT direct access for the engineer + agent | Fastest | Approves access, not the change; agent holds prod write |
| D. Hosted agent with its own identity | Clean separation | New platform; does not remove the need for approval |

## 3. Decision

"A + D2'": option A is the default path for every production change, incidents included. A narrow JIT
fallback exists only when the PR path cannot be used during an incident (ADR-0005). The owner accepts
that this fallback meets the approval rule only partly (Options §9 Q2). Incident target: ≤ 30 min from
decision to apply.

## 4. Consequences

- **Positive:** the PR, its approvals, the run log and CloudTrail form one evidence chain keyed by
  commit SHA. Agent-written and human-written changes pass the same checks (S10).
- **Negative / trade-offs:** slower incident fixes; operations that are not in IaC must first be
  written as code or a runbook. Two write paths remain (PR and JIT), while the framing asked for one.
- **Risks & how we watch them:** the fallback stays narrow only if most incidents are expressible in
  IaC (unknown, Options §8). Metrics: JIT grants per month, share of incidents needing non-IaC
  operations; above about 25 % (⚠️ starting threshold), make the PR lane faster or add a runbook, never widen JIT.
- **Example:** Lambda timeouts at 2 a.m. The responder's agent proposes `timeout` 30 → 90 s in
  `serverless.yml`; the PR is labelled `incident`; the on-call approver reviews and approves; CI
  packages, previews prod and deploys with the OIDC role. Estimate 11–46 min (⚠️ Options §6).
- **Next steps:** measure the incident PR lane on one service first (phase 1).

## 5. References

- Framework §1 and layer 3; `work/03-options.md` §1, §6, §9.
- Related: ADR-0002, ADR-0003, ADR-0005.
