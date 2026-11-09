# CLAUDE.md (monorepo root, template)

<!-- Template for the monorepo's shared CLAUDE.md (framework §2). This file is an L3 path:
     changes need two members of the L3 owner team (CODEOWNERS, OD3, OD26). Replace the
     <placeholders>; keep it short, because every session loads it. -->

## What this repository is

<one paragraph: services, stacks, who owns what; link to CODEOWNERS>

## How production changes

- Production is written only by the deploy workflow after a reviewed pull request is merged to
  `main`. Never run `pulumi up`, `serverless deploy`, `kubectl apply`, `eas update` or a
  database client against production from a session. Use the `prod-change` skill.
- Preview against non-prod: `pulumi preview --stack <service>-nonprod`,
  `npx serverless diff --stage nonprod`. PR checks show the same preview.
- Never approve a pull request. The engineer pushes and opens it.
- Database changes: files under `db/<service>/`; data fixes under
  `db/<service>/data-fixes/<tenant>/<ticket>.sql` with `-- expected_rows: N`, naming records by
  internal IDs only (no account numbers, national IDs, names or diagnoses; values the fix needs
  come as psql variables). A data change inside a migration stops the deploy.

## Conventions

- Pulumi: <project layout, naming, where IAM roles live (`svc-*` with the permissions boundary;
  `app-claims-*` only in `infra/pulumi/iam/`)>.
- Serverless: <plugins allowed, how secrets are resolved at runtime (no plain-text variables)>.
- Logging: never log a whole event or request body; log IDs, not values (the SAST rule fails it).
- Tests: `npm test`, `npm run lint` (the only allowlisted commands).

## Data

- Non-prod holds synthetic data only. Never paste real claim data, national IDs, bank accounts or
  medical text into a session. If a log or file you read contains such data, stop and tell the
  engineer.

## Skills

- `prod-change`, `incident-triage`, `risk-summary-explainer`, `dependency-fix` (internal plugin
  `devsecops-guardrails`).
