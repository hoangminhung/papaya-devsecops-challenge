---
name: prod-change
description: Use when the user wants to change anything in production. Explains the only allowed path - a pull request applied by CI - and what to do in an incident.
---

# Changing production

1. Never change production from this session. Production is written only by the deploy
   workflow after a reviewed pull request is merged to `main` (framework layer 3).
2. Prepare the change as code (Pulumi, `serverless.yml`, Kubernetes manifests) and preview it
   against non-prod. The engineer pushes the branch and opens the pull request: from phase 2
   the managed sandbox hides git and GitHub credentials from this session. In phase 1, when the
   engineer asks, you may run `git push` and `gh pr create` for the engineer's own change.
3. Never approve or review-approve a pull request, from any session or tool. The approver is
   always a person who is not the author (OD5); managed settings deny `gh pr review` (OD25).
4. If the deploy stops at the risk stop, prepare a change that adds only
   `deploy-approvals/<stack>/<stopped commit>.yaml` with the hash from the job summary, and ask
   the engineer to open the pull request for it.
5. In an incident: the pull request links the open incident issue and carries the `incident`
   label; the on-call approver reviews it (OD27). If the pull request path cannot be used at all,
   the incident responder requests a JIT grant with a command list; that terminal runs no agent
   (framework layer 7).
