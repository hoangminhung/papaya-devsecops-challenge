# Prod environments, their secrets and variables (names only)

Every prod environment uses the same settings as `environment.json` and `branch-policy.json`
here: deployments from `main` only, no required reviewers (not available on GitHub Team for
private repos). Secrets are set through the environment-secrets REST API or the settings UI, never
as repository secrets, and never stored in git. Framework layers 1 and 5; OD1, OD6, OD22, OD24,
OD36, OD40.

| Environment | Used by | OIDC trust (examples/aws/) | Secrets |
|---|---|---|---|
| `production` | `deploy-prod.yml`, domain stacks (Pulumi, Serverless) | `oidc-trust-prod-deploy.json` | none |
| `production-iam` | `deploy-prod.yml`, stack `iam` only (OD22) | `oidc-trust-prod-iam-deploy.json` | none |
| `production-db` | `deploy-prod.yml`, tool `sql` only (ADR-0011) | `oidc-trust-prod-db-change.json` | none |
| `production-k0s` | the k0s and Firebase deploy workflow only (OD24) | the k0s API trusts this subject in the target design (`examples/k0s/authentication-config.target.yaml`) | `K0S_DEPLOY_TOKEN`, `FIREBASE_SERVICE_ACCOUNT_KEY` |
| `production-mobile` | the mobile release workflow only (OD40) | none: Expo has no OIDC for GitHub (R9.8.7) | `EXPO_ROBOT_TOKEN`, `EAS_UPDATE_SIGNING_KEY` |

Secrets, all S2 exceptions with an owner, an expiry and a rotation in the exception register:

| Secret | What it is | Why it exists |
|---|---|---|
| `K0S_DEPLOY_TOKEN` | Time-limited token of the namespaced deploy ServiceAccount (`examples/k0s/deploy-rbac.yaml`), not a kubeconfig | Until the k0s API trusts GitHub OIDC (OD24, G1) |
| `FIREBASE_SERVICE_ACCOUNT_KEY` | Service-account JSON key for Firebase Hosting deploys; the official action needs one (R9.6.5) | Until the WIF spike shows `firebase deploy` works without a key (OD36, G2) |
| `EXPO_ROBOT_TOKEN` | Access token of the Expo robot user with the Release Manager role | Expo has no keyless login from GitHub (R9.8.7) |
| `EAS_UPDATE_SIGNING_KEY` | Private key that signs EAS updates (R9.8.8) | Lives only here, so a stolen Expo token alone cannot ship code |

A separate environment per secret holder means jobs of the AWS deploy workflow cannot read them,
and each environment is referenced by one workflow file (all under CODEOWNERS, L3). On
self-hosted runners environment secrets act like repository secrets (R3.1.5), so these jobs run
on GitHub-hosted runners.

Environment **variables** (prod-only, kept on the environment rather than the repository):
`AWS_REGION`, `PROD_PULUMI_DEPLOY_ROLE_ARN`, `PROD_SERVERLESS_DEPLOY_ROLE_ARN` on `production`
and `production-iam`; `PROD_DB_CHANGE_ROLE_ARN` on `production-db`; `PULUMI_BACKEND_URL`,
`PULUMI_CLI_VERSION`, `NODE_VERSION`. They are read by `workflows/deploy-prod.yml` only.
