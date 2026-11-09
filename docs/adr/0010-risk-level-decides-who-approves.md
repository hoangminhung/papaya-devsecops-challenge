# ADR-0010: Risk level decides who approves, not how many; non-prod needs no approval

- **Status:** Accepted
- **Date:** 2026-11-09
- **Decided by:** owner of this submission (GĐ-14; OD2, OD3, OD8, OD9, OD13)
- **Scope:** every change made by engineers and their agents, from non-prod to production

## 1. Context

Engineering says "Let Claude Code talk to AWS directly" (brief); the need is speed. Compliance's
sentence covers production writes only (framing §3.1). A single rule for all changes either slows non-prod for
no gain or leaves high-risk prod changes with too light a review. The owner also wants every prod
change to need two people, no more by default: one who makes it and one who approves it (OD2).

## 2. Options considered

| Option | Pros | Cons |
|---|---|---|
| A. Same approval for everything | Simple | Non-prod loop slowed for no gain; high-risk changes get no extra scrutiny |
| B. More approvers as risk grows (e.g. two for L3) | More eyes on dangerous changes | Breaks the two-person rule; slower incidents |
| C. Risk level narrows who may approve, plus a risk stop; non-prod free | Fast where damage is small; specialist owners where it is large | One reviewer for high-risk changes can miss things |

## 3. Decision

Option C [design levels]:

| Level | What | Approval |
|---|---|---|
| L0 | Reads: non-prod anything, prod metadata | none |
| L1 | Changes in non-prod (synthetic or masked data only, GĐ-14) | none, author only |
| L2 | Routine prod change, e.g. Lambda memory 1024 → 2048 MB | 1 code owner ≠ author, ≠ last pusher |
| L3 | IAM/SCP, stateful replace/delete, network, workflow and agent-config files, catalogue, advisory policy finding (full list: framework layer 5) | 1 owner of that path |
| L3-JIT | Break-glass in an incident | on-call approver ≠ requester (ADR-0005) |
| L3-data | Real customer data read | approver ≠ requester + agreement; data-owner co-approval [design] (ADR-0009) |

`CLAUDE.md` and the other agent-configuration files are L3, because they define the workflow for the
whole team (OD3). Process-defining paths and the SCP stack are owned by the L3 owner team; IAM or
stateful changes inside a domain file are approved by that stack's owners (OD8, OD13). At every level,
the risk stop applies to any deploy whose prod diff is risky (ADR-0004).

## 4. Consequences

- **Positive:** a free non-prod loop for engineers and agents (S4); the same two-person rule for every
  prod change, incidents included (three people only by recorded deviation, OD11). Compliance gets a written rule for who may approve what.
- **Negative / trade-offs:** one approver for high-risk changes (owner's trade-off for speed);
  `CLAUDE.md` edits wait for the L3 owner team, not the domain team that edits them most.
- **Risks & how we watch them:** the free loop holds only if non-prod has no real data; a non-prod
  store not yet scanned follows the L3-data rule until scanned (S11). A risky diff hidden in an L2 PR is
  caught by the risk stop, not by the level (Pulumi and Serverless stacks only;
  k0s and Firebase have none yet, G1, G2).
- **Next steps:** non-prod data scan and CODEOWNERS with the L3 path list in phase 1; composition of
  the L3 owner team is open (G17).

## 5. References

- Framework layer 3 (levels table), layer 5 (canonical L3 path list), layer 6 (non-prod).
- Related: ADR-0003, ADR-0004, ADR-0005, ADR-0009.
