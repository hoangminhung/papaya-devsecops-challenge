# ADR-0008: CI uses OIDC; no long-lived CI keys, with one time-boxed exception

- **Status:** Accepted
- **Date:** 2026-11-09
- **Decided by:** owner of this submission (framing Q8; OD1, OD6; target S2)
- **Scope:** GitHub Actions deploy workflows to AWS, GCP, k0s and Firebase

## 1. Context

CI becomes the only routine production writer (ADR-0001), so it is the main target. Repository
secrets can be read by anyone with write access (📖 R3.5.3b), which, in the single monorepo, likely includes every engineer (⚠️ assumed) and their
agent. A long-lived key there is standing prod write in disguise.

## 2. Options considered

| Option | Pros | Cons |
|---|---|---|
| A. Keep stored keys, rotate them | No migration | Standing prod write for all writers |
| B. OIDC everywhere, no exception | S2 = 0 | k0s and Firebase may not support it yet (G1, G2) |
| C. OIDC for AWS and GCP; a controlled exception for k0s/Firebase deploy credentials | Removes most keys now | One exception to manage |

## 3. Decision

Option C.

- **AWS:** GitHub OIDC (📖 R3.4.1); the prod role trusts only the `production` environment of the
  monorepo (📖 R3.4.3, R3.4.4), ideally narrowed by `job_workflow_ref` (📖 R3.4.5; on Team ⚠️ G10).
- **GCP:** Workload Identity Federation restricted to Papaya's GitHub organization (📖 R3.4.5b).
- **k0s/Firebase exception** (OD1, OD6): CI deploy credentials only, until it is checked whether they
  can use OIDC. Conditions [design]: a `production` environment secret, never a repository secret
  (📖 R3.1.2, R3.1.3); GitHub-hosted runners, because on self-hosted runners environment secrets act
  like repository secrets (📖 R3.1.5); if k0s needs a self-hosted runner, it is dedicated to the
  `production` deploy and the residual risk is recorded (⚠️ G15); a single source of truth; owner, expiry, rotation.
- `GITHUB_TOKEN` default "restricted" (📖 R3.5.3); actions pinned by lockfile or full SHA (📖 R3.5.5).

## 4. Consequences

- **Positive:** no stored AWS or GCP keys to leak (S2); every deploy credential is tied to a reviewed
  workflow on `main`.
- **Negative / trade-offs:** one-time migration; slower action updates. The exception remains until
  G1/G2 are solved.
- **Risks & how we watch them:** admins can change or delete the environment, and a deleted
  environment comes back without protection (⚠️ R3.1.4); alerts and a settings comparison cover it.
  The GitHub Apps used for CI agents and the required check have their own keys (⚠️ G19).
  Runtime credentials inside the cluster are out of the exception (OD6).
- **Next steps:** OIDC and removal of stored keys in phase 1; k0s/Firebase credentials moved to
  environment secrets before standing prod write is removed.

## 5. References

- Framework layer 1 ("CI → AWS", "CI → GCP"), layer 5 ("Credentials").
- Related: ADR-0001.
