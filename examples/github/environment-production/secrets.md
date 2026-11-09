# `production` environment secrets and variables (names only)

Set through the environment-secrets REST API or the repository settings UI, never as
repository secrets. Values are never stored in git. Framework layer 5, owner decisions OD1 and OD6.

| Secret name | What it is | Owner | Expiry / rotation | Why it exists |
|---|---|---|---|---|
| `K0S_DEPLOY_KUBECONFIG` | Deploy-only kubeconfig for the prod k0s cluster | `<owner team>` | `<date>`, in the exception register | S2 exception until k0s deploys can use OIDC (G1) |
| `FIREBASE_DEPLOY_TOKEN` | Firebase Hosting deploy credential | `<owner team>` | `<date>`, in the exception register | S2 exception until Firebase deploys can use OIDC (G2) |

No AWS secret is listed: AWS is reached through OIDC (`examples/aws/oidc-trust-prod-deploy.json`;
the same trust is used by both prod deploy roles).

Optional, layer 5 [design]: put these two secrets in a separate environment `production-k0s`,
also limited to `main` and referenced only by the k0s/Firebase deploy workflow, so AWS deploy
jobs cannot read them.

Environment **variables** (not secret, but prod-only, so kept on the environment rather than the
repository; set through the environment-variables API): `AWS_REGION`, `PROD_PULUMI_DEPLOY_ROLE_ARN`, `PROD_SERVERLESS_DEPLOY_ROLE_ARN`,
`PULUMI_BACKEND_URL`, `PULUMI_CLI_VERSION`, `NODE_VERSION`. They are read by
`workflows/deploy-prod.yml` only.
