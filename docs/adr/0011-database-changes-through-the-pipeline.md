# ADR-0011: Database schema changes and data fixes go through the pipeline like any prod change

- **Status:** Accepted
- **Date:** 2026-11-09
- **Decided by:** owner of this submission, after the independent review (`work/07-review.md`; OD29)
- **Scope:** Aurora PostgreSQL schema migrations, GraphQL-engine (Hasura) metadata, and data fixes on prod

## 1. Context

"Every prod change is a pull request" (ADR-0001) had no designed path for the two most frequent
prod changes of a claims platform on Aurora with a GraphQL engine: schema migrations and data fixes
(a stuck claim, a payout to retry). Once standing prod write is removed (rollout 1.16), nobody has a
legitimate way to run them, which invites a shared database account or an admin endpoint: the
shortcut the framework exists to remove. Data fixes also touch one tenant's customer data, which
layer 6 treats as L3-data. IAM database authentication is not logged by CloudTrail (📖 R9.2.11).

## 2. Options considered

| Option | Pros | Cons |
|---|---|---|
| A. JIT grant with `psql` for data fixes; migrations at app start | Fast; no new tooling | An approved command list, not an approved change (ADR-0005's weakness) for routine work; migrations run with the app's role |
| B'. As B, but a self-hosted runner inside the VPC connects directly | One less hop | A long-lived runner with prod network access (framework layer 5 avoids self-hosted runners) |
| B. Migration and data-fix files in the monorepo, applied by the deploy workflow with a database role of its own, behind the risk stop | Same gate, same evidence as every other change | A migration job and two wrapper scripts per migration tool; data fixes need two approvers |
| C. A separate database change tool with its own approvals | Purpose-built | A second approval system outside GitHub; a side path (T20) |

## 3. Decision

Option B [design]:

- **Files:** migrations, GraphQL-engine metadata and data fixes live under `db/<service>/`; data
  fixes under `db/<service>/data-fixes/<tenant>/<ticket>.sql`, one tenant per file, with an
  `-- expected_rows: N` header. Records are named by opaque internal IDs only; sensitive values
  come at run time from a values file only the task reads; the `data-fix-scan` check enforces it
  (OD48, examples E19).
- **Approval:** migrations and metadata as any deployable path (domain owner, on-call in an
  incident). Data fixes are **L3-data-write**: a code owner plus a different person from that
  tenant's data-owner team, checked by the approval-gate app (E12, rule R4), which reads the
  tenant from the path; data owners are not code owners, so they need read access only, and a
  tenant without a data-owner team fails the check. In an incident the on-call approver stands
  in and the data owner reviews the next working day (layer 6).
- **Apply:** a `sql` job of the deploy workflow lists the pending files, runs the risk stop on them
  (`--tool sql`: DROP, TRUNCATE, column type changes, unscoped DELETE/UPDATE, grants, roles,
  row-level security, COPY, function bodies, every metadata change, and any INSERT, UPDATE or
  DELETE in a migration, which belongs in a data fix, stop for a stack owner's approval), then applies exactly the classified files, each in its own transaction; a data fix
  whose affected-row count differs from its header is rolled back.
- **Where it runs and credentials:** Aurora is private to the prod VPC, so the GitHub-hosted job
  does not connect to it. The job runs in its own environment, `production-db`, which no other
  deploy job can use, and installs no package. Its OIDC role may only start the `db-change-<service>` ECS task on one
  cluster, pass that task's roles and use one S3 prefix; the one-off Fargate task runs in private
  subnets, checks the SHA-256 of the classified bundle, and connects with `rds-db:connect` as the
  migration user (📖 R9.2.11). Metadata is applied by the same task with `hasura metadata apply`
  and the engine's admin secret, injected from Secrets Manager (📖 Hasura CLI docs, framework
  layer 3). No person holds database credentials or the admin secret day to day (examples E15).
- **Evidence:** the PR, the job log and summary (statement kinds and row counts, never values),
  the risk-stop record; database-side activity through Database Activity Streams (layer 7),
  because IAM database authentication is not in CloudTrail.

## 4. Consequences

- **Positive:** the most common prod changes get the same gate and evidence chain as code; data
  fixes are scoped to one tenant and approved by its data owner; no standing database access.
- **Negative / trade-offs:** a data fix takes a PR, two approvals and a deploy run instead of a
  `psql` session; the two `tools/db/` scripts, the task image and its task definition must be
  built for Papaya's migration tool (unknown here); a Fargate task start adds about a minute per
  run (⚠️ not measured); the SQL classifier is a heuristic, not a parser (examples E7).
- **Risks & how we watch them:** a destructive statement hidden in a form the heuristic does not
  know (function bodies and `EXECUTE` already stop); a wrong `expected_rows` is caught only if the
  count differs; long migrations hold locks (expand/contract recommended, not enforced).
- **Next steps:** `tools/db/` wrappers and the migration role in phase 1, before standing prod write
  is removed (rollout 1.23).

## 5. References

- Framework layer 3 ("Database changes"), layer 6 (L3-data), layer 7 (Database Activity Streams).
- Examples E3 (`sql` job), E7 (SQL rules), E12 (rule R4), E15 (the CI and task roles).
- Related: ADR-0001, ADR-0004, ADR-0009, ADR-0012.
