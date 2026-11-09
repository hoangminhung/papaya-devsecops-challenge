---
name: prod-change
description: Use when the user wants to change anything in production. Explains the only allowed path - a pull request applied by CI - and what to do in an incident.
---

# Changing production

1. Never change production from this session. Production is written only by the deploy
   workflow after a reviewed pull request is merged to `main` (framework layer 3).
2. Prepare the change as code (Pulumi, `serverless.yml`, Kubernetes manifests), preview it
   against non-prod, and ask the engineer to push the branch and open the pull request: under
   the managed sandbox this session has no git or GitHub credentials. A code owner who is not
   the engineer approves it; an agent never approves a pull request (OD5).
3. If the deploy stops at the risk stop, open a pull request that adds only
   `deploy-approvals/<stack>/<stopped commit>.yaml` with the hash from the job summary.
4. In an incident: label the pull request `incident`; the on-call approver reviews it.
   If the pull request path cannot be used at all, the incident responder requests a JIT grant
   with a command list; that terminal runs no agent (framework layer 7).
