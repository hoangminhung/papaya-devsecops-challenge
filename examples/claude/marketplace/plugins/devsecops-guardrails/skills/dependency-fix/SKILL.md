---
name: dependency-fix
description: Use when fixing a vulnerable dependency or base image from a Dependabot alert or an ECR scan finding. Prepares a small pull request with the upgrade and the evidence.
---

# Fix a vulnerable dependency

1. Start from the finding: package, installed version, fixed version, advisory ID, which services
   use it (lockfiles, image digests).
2. Upgrade to the lowest fixed version that the lockfile allows; for a base image, the patched tag
   pinned by digest. Do not upgrade unrelated packages: one advisory per pull request keeps it
   small enough to review (the `pr-size` check fails large agent pull requests).
3. Do not add install scripts: CI runs without them except for the reviewed allowlist (OD22). If
   the new version needs one, stop and tell the engineer.
4. Run the tests and the non-prod preview. In the pull request text, list the advisory, the
   versions, the services affected, what was tested and what was not.
5. The pull request is approved by the owners of the changed files like any other change.
