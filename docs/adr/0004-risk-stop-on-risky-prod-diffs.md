# ADR-0004: Risky prod diffs stop the deploy until a stack owner approves the prod preview

- **Status:** Accepted
- **Date:** 2026-11-09
- **Decided by:** owner of this submission (OD8, OD11, OD13)
- **Scope:** deploy workflows for Pulumi and Serverless stacks; k0s and Firebase not covered yet

## 1. Context

With the gate at merge time (ADR-0003), the approver reviews the code change, not the prod diff. A
PR may not preview prod, because that would run PR code with state-write and secret access
(📖 R4.3.3, R4.3.4; ⚠️ R4.6 #2). So a stateful delete or an IAM change can reach prod without anyone
seeing its real effect. Most IAM, network and stateful changes sit inside domain files such as
`serverless.yml`, not in separate L3 paths (assumed ⚠️; we have no access to the repo).

## 2. Options considered

| Option | Pros | Cons |
|---|---|---|
| A. Accept the gap | No extra step | Destructive diffs applied unseen |
| B. Risk stop, approved by the L3 owner team | Specialist review | Often a third person; L3 team must be on call 24/7 |
| C. Risk stop, approved by an owner of the stack | Stays at two people; works at night | Less specialist review; compensated by automated checks |

## 3. Decision

Option C [design]. The deploy job on `main` previews prod. On stateful replace/delete, an IAM
change, a network or security-group change, or (from phase 2) an advisory policy finding, it stops
and posts the filtered preview. The original author opens a PR (the workflow does not, as "Allow GitHub Actions to create and
approve pull requests" stays off, 📖 R3.3.3; ⚠️ R3.6 #3) adding
`deploy-approvals/<stack>/<sha>.yaml` with the SHA and preview hash (owned by the stack's owners and the
on-call group, OD8, OD9); the first approver approves it
(OD13). If that approver is unavailable, another stack owner approves; this makes three people and
is recorded as a deviation (OD11). After the merge the workflow previews again on the new HEAD and
continues only if the hash matches. Serverless uses `serverless diff --json` (sf-core ≥ 4.37.0), parsed by CI because
differences do not change the exit code (📖 R4.4.2). A `mandatory` Pulumi policy violation always
blocks `pulumi up` (📖 R4.2.2; policy packs from phase 2).

## 4. Consequences

- **Positive:** the person who approves now sees the prod diff for the changes that can do lasting
  damage. Still two people in the normal case.
- **Negative / trade-offs:** while a stack is stopped, later deploys to it stop too (the hash
  differs), including an incident fix, until the approval lands or the change is reverted. One more review round when the stop fires.
- **Risks & how we watch them:** preview output may not be stable enough to hash (⚠️ Options §8); if
  not, compare a structured summary. Until phase 2, the risk stop is the only compensation for OD8;
  Access Analyzer `check-no-new-access` (📖 R2.8.1) and policy packs follow. k0s and Firebase have no
  preview step in this design (⚠️ G1, G2).
- **Next steps:** risk stop in the deploy job in phase 1.

## 5. References

- Framework layer 3 ("Risk stop"), layer 5 (required checks); `work/03-options.md` §1.
- Related: ADR-0001, ADR-0003.
