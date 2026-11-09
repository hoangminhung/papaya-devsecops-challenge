# ADR-0002: Nobody holds standing prod write; in prod, the engineer's (and so the agent's) only standing role reads metadata

- **Status:** Accepted
- **Date:** 2026-11-09
- **Decided by:** owner of this submission (Options §9; D2)
- **Scope:** AWS IAM Identity Center permission sets and SCPs on the prod OU; k0s, GCP and Firebase by the same principle

## 1. Context

On a laptop the agent uses the engineer's AWS SSO cache, and one portal session reaches every role
assigned to that engineer (📖 R2.2.1, R2.2.2; token-reuse detail ⚠️ R2.2.2). A separate "agent"
permission set therefore does not separate the agent from the engineer (⚠️ R2.9 #1). Whatever the
engineer holds, the agent holds.

## 2. Options considered

| Option | Pros | Cons |
|---|---|---|
| A. Separate agent permission set, engineer keeps write | Looks like least privilege | Same SSO cache: the agent can still assume the write role |
| B. No standing prod write for anyone; `ProdReadMetadata` as the only standing prod role | Agent cannot write prod with the engineer's identity | Engineers also lose direct writes and raw-log reads |
| C. Separate OS user or container for agent sessions | Real separation of credentials | More setup; planned for phase 3 only |

## 3. Decision

Option B. Prod is written only by the CI pipeline role, or by an approved, time-boxed JIT grant
(ADR-0005). The standing prod role is `ProdReadMetadata` [design name]: metrics, redacted log groups,
configuration of services whose secrets are resolved at runtime; no data-plane reads of claim stores;
1-hour role session, the minimum (📖 R2.1.4). From phase 2, SCPs on the prod OU deny data-plane reads and
direct Lambda updates except for named roles (pattern ⚠️ R2.9 #4, R4.6 #3). Option C follows in phase 3.

## 4. Consequences

- **Positive:** once standing write and broad read roles are removed (end of phase 1), an agent,
  even a manipulated one, cannot write prod AWS or read AWS claim stores with the engineer's standing
  identity (data-plane action list ⚠️ G13); k0s and GCP follow the same principle, mechanisms open
  (G1, G3). In non-prod the agent keeps broad rights (`NonProdDeveloper`, ADR-0010 L1). Compliance gets least privilege enforced by IAM (S1).
- **Negative / trade-offs:** during the transition, engineers lose raw logs and configuration of
  services not yet redacted. Configuration values then come from the IaC code; raw logs need a
  data-read grant in an incident. Process rules remain where
  IAM cannot separate engineer and agent: no agent in the JIT terminal (D2).
- **Risks & how we watch them:** SSO-token theft during a session could open later grants (⚠️);
  mitigations [design] are a short portal session and a fresh sign-in before a grant. The data-plane action
  list is incomplete (⚠️ G13). Identity Center assignment export is reviewed quarterly.
- **Next steps:** phase 1 removes broad read roles only after the minimal real-data read flow works,
  then removes standing prod write once its prerequisites are in place.

## 5. References

- Framework layer 1, layer 2 ("Trade-off on AWS credentials"), layer 8 rollout.
- Related: ADR-0001, ADR-0005, ADR-0009.
