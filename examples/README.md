# Examples

> Status: steps 1 (change workflow, layer 3) and 2 (identity and access, layer 1) reviewed in
> three rounds each; step 3 (agent runtime, supply chain, policy pack: E8–E10) reviewed in
> three rounds. · Updated: 2026-11-09

Concrete files behind [`../docs/01-framework.md`](../docs/01-framework.md). Each one exists to
prove one claim of the framework, and each has a local check. **Nothing here was run against
GitHub, AWS or any live system.** A passing check shows that the file says what the framework
says; it does not show that the platform enforces it. Every row lists what the check does
**not** prove.

Markers: ✅ checked in this repository's sessions (command output in the transcript) ·
📖 official documentation, linked · ⚠️ assumption, not verified · [design] proposal of this
submission, untested.

Placeholders: `example-org`, `<owner team>`, `123456` (app ID), `<AWS_ACCOUNT_ID>`,
`<NONPROD_AWS_ACCOUNT_ID>`, `<ORG_ID>`, `<REPO_ID>`, `<REVOKED_USER_ID_PLACEHOLDER>`. The monorepo
layout (`services/`, `infra/pulumi/`, `k8s/`, `web/`, `tools/`) is invented; Papaya's is unknown.

Where each file would live in the monorepo:

| Here | In the monorepo |
|---|---|
| `github/workflows/*.yml` | `.github/workflows/` |
| `github/CODEOWNERS` | `.github/CODEOWNERS` |
| `github/ruleset-main.json`, `github/environment-production/` | repository settings (REST API bodies), with an expected copy in git (layer 8) |
| `risk-stop/classify.py`, `risk-stop/adapters.py` | `tools/risk-stop/` |
| `risk-stop/deploy-approvals/<stack>/` | `deploy-approvals/<stack>/` at the root |
| `aws/oidc-trust-*.json` | trust policies of the deploy and preview roles, in the IAM stack (`infra/pulumi/iam/`) |
| `aws/scp-prod-ou.json` | the SCP stack (`infra/pulumi/org-scp/`, an L3 path), deployed from the management account |
| `aws/permission-set-prod-read-metadata.json` | the Identity Center stack (`infra/pulumi/iam/`) |
| `claude/managed-settings.phase*.json` | expected copy in git of the server-managed settings, which live in the Claude admin console (layer 2, layer 8) |
| `claude/marketplace/` | its own repository `example-org/claude-plugins`, with its own ruleset and CODEOWNERS (layer 5) |
| `pulumi-policy/` | `policy-packs/aws/` (an L3 path) |
| `risk-stop/fixtures/`, `tests/`, `schemas/`, `tools/`, `validate.sh` | only here, to check the examples |

## How to run

```bash
examples/validate.sh            # tools that are not installed are SKIPPED, and reported as such
ACTIONLINT=/path/actionlint ZIZMOR=/path/zizmor examples/validate.sh
```

Needs Python 3 with `jsonschema`, `PyYAML` and `git`; optional `jq`, `yamllint`, `shellcheck`,
`actionlint`, `zizmor`, `claude` (for `claude plugin validate`), and Node.js with
`npm ci` run once in `pulumi-policy/` (downloads packages; `node_modules/` is not committed).
Tests use the standard `unittest`.

## What each file proves

| # | Files | Proves (framework) | Checked by | Does not prove |
|---|---|---|---|---|
| E1 | [`github/ruleset-main.json`](github/ruleset-main.json) | The approval gate is the merge to `main` (layer 3, ADR-0003): PR required, 1 approval, code-owner review, stale approvals dismissed, approval by someone other than the last pusher, branch up to date (no merge queue), required checks pinned to a source app, no force push or deletion, empty bypass list | JSON Schema of the create-ruleset request body; key-by-path check; design tests | That GitHub enforces it. `approval-gate` comes from a dedicated app whose ID (`123456`) is a placeholder (gap G19). The other checks are pinned to GitHub Actions (ID 15368 ✅ `GET https://api.github.com/apps/github-actions`), so any workflow in the repo can likely post a check with the same name (⚠️ layer 3, G19) |
| E2 | [`github/CODEOWNERS`](github/CODEOWNERS) | L3 process paths: owned by the L3 owner team only; deployable paths: co-owned by the domain team and the on-call group, so one approval from either satisfies code-owner review (OD9, OD13; 📖 R3.2.7); risk-stop approvals: co-owned by the stack's owners and on-call (OD8). Fail-safe default so no file is unowned [design] | Effective owners resolved with GitHub's "last matching pattern takes the most precedence" (📖 [about code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)); every stack in `deploy-on-main.yml` checked for code and approvals owners | That the teams exist and have write access: GitHub drops such owners silently. [`codeowners-validate.yml`](github/workflows/codeowners-validate.yml) covers that in a real repo |
| E3 | [`github/workflows/`](github/workflows/) | "Merge approval = deploy approval" (layer 3): only the reusable [`deploy-prod.yml`](github/workflows/deploy-prod.yml) uses `production`; no ref/SHA input; no `workflow_dispatch`, `issue_comment`, `pull_request_target`, `workflow_run`; one concurrency group per stack, running deploys never cancelled; only the current tip of `main` is deployed (no re-run of an old run) [design]; preview → risk stop → apply, and the stop cannot be skipped, ignored or bypassed by an `if:`; apply commands use only allowed flags. Layer 5: OIDC, per-job permissions, SHA-pinned actions; `npm ci`, Pulumi plugins and the policy pack installed before the AWS credentials are in the job (the Serverless framework download: ⚠️ assumed to happen at `serverless --version`); this does not keep install scripts away from the job's OIDC token (Limits). PRs preview non-prod only | `actionlint`, `zizmor --persona=auditor`, `yamllint`; design tests (`test_workflow_policy.py`) | That the workflows run: the Pulumi/Serverless steps were never executed. The tests see only these files, not a whole monorepo |
| E3b | [`github/environment-production/`](github/environment-production/) | `production` accepts deployments from `main` only and has no required reviewers (not available on GitHub Team for private repos, R3.1.2); names of the k0s/Firebase exception secrets (OD1, OD6) and of the prod variables | JSON Schemas of the two request bodies (environment PUT, branch-policy POST); key-by-path check; design tests | That GitHub applies it; admins can still change or delete the environment (layer 7 compares live settings) |
| E4 | [`aws/oidc-trust-prod-deploy.json`](aws/oidc-trust-prod-deploy.json), [`aws/oidc-trust-nonprod-preview.json`](aws/oidc-trust-nonprod-preview.json) | Layer 1 "CI → AWS", ADR-0008: the prod deploy role trusts only the `production` environment of the monorepo; PRs get only a non-prod role in the non-prod account. Immutable subject format with owner and repository IDs (📖 R3.4.4; environment form ⚠️ R3.7 A2); `aud` = `sts.amazonaws.com` (📖 R3.4.1); `StringEquals` only. No `sts:TagSession`: the action does not tag sessions with OIDC (📖 `configure-aws-credentials` README at the pinned SHA). **Prerequisite:** repositories created before 2026-07-15 keep the old subject format unless the organization or repository opts in (📖 R3.4.4); Papaya's monorepo likely needs that opt-in first, or every deploy is refused. Optional narrowing with `job_workflow_ref` (⚠️ G10). The same trust applies to both prod deploy roles (Pulumi and Serverless) | Design tests | That AWS accepts the policy. `environment:production` alone does not say which branch: the environment's branch rule (E3b) does (⚠️ R3.4.3) |
| E5 | [`aws/scp-prod-ou.json`](aws/scp-prod-ou.json) (phase 2) | Layer 1 SCPs: Lambda code/config changes only by CloudFormation deployment roles, the **Pulumi** prod deploy role and JIT roles (the Serverless deploy role is not exempt: it only passes the CloudFormation role); claim-data reads only by application and approved data-read roles; the names of exempt roles can be created or changed only by the IAM stack's (Pulumi) deploy role; pre-deployed revocation Deny on `identitystore:UserId` (📖 R2.4.4); no tampering with trails in prod accounts. Deny-only; condition keys from R2.3.8. The outside-org write deny (all OUs) is not in this file | Every action exists in the AWS catalogue; size ≤ 10,240 characters minified and as written (📖 R2.3.4); exempt principals, protected role names and trail actions pinned exactly by the tests; claim-data reads checked to include a shared list | How it evaluates with other SCPs. Role names `cfn-deployment-*`, `github-prod-deploy-pulumi`, `app-claims-*` and permission sets `InfraOperator-<service>`, `DataRead-<store>` are [design] names. Identity Center role ARNs have a region segment except when the identity source is in us-east-1, and end in `AWSReservedSSO_<set>_<suffix>` (📖 [referencing permission sets](https://docs.aws.amazon.com/singlesignon/latest/userguide/referencingpermissionsets.html)); both forms are listed. The data-read action list is partial (G13) |
| E6 | [`aws/permission-set-prod-read-metadata.json`](aws/permission-set-prod-read-metadata.json) | Layer 1, ADR-0002: `ProdReadMetadata` reads metrics and metadata; 1-hour session (📖 R2.1.4); raw logs and function configuration only for named services that are redacted or use runtime secrets. Reads that expose configuration, data or secrets are left out (finding 11) | Wildcards expanded with the AWS catalogue; no action AWS marks as a write or permission-management action; no known data read; `Resource: "*"` only for an explicit, reviewed allowlist of metadata actions in the test (no wildcards; AWS's `IsList` is not trusted, finding 12); log and config reads only on one named log group or function each. An action missing from the catalogue fails the test (add its service to `tools/fetch_aws_actions.py`) | Only the **listed** data reads are known to be absent (G13). The file follows the shapes of `CreatePermissionSet` and `PutInlinePolicyToPermissionSet` (⚠️ field names from memory) |
| E7 | [`risk-stop/`](risk-stop/) | The risk stop (layer 3, ADR-0004) can be built: risky prod diffs stop the deploy (per category, for Pulumi and CloudFormation types alike, plus property names on any type); an approval counts only for the exact preview, only if it was merged to `main` on its own after the stopped commit, never edited, and the stack's code is unchanged since the stopped commit; approvals expire 7 days after they were merged; the summary shows which resources and properties change, never values; unreadable input stops | 25 unit tests; approval tests run against throwaway git repositories, including the bypasses found in review (edited approval, merge-commit PR, approval on a side branch, approval merged before a change inside the stack, runtime edit of the file) and one test that documents a gap that stays open (see Limits) | ⚠️ The JSON shapes of `pulumi preview --json` and `serverless diff --json` are **assumed** ([`adapters.py`](risk-stop/adapters.py)). That a real preview gives the same hash twice for unchanged code (Options §8). See "Limits of the risk stop" |
| E8 | [`claude/managed-settings.phase1.json`](claude/managed-settings.phase1.json), [`claude/managed-settings.phase2.json`](claude/managed-settings.phase2.json) | Layer 2, ADR-0007, phases of layer 8 and OD4: phase 1 holds exactly the layer-8 subset (Manual default with auto mode kept, D1; bypass off; an allowlist of two exact repo scripts, `npm test` and `npm run lint`, OD7b, finding 19; `Read(~/.aws/**)` denied and `autoMode.classifyAllShell: true` (owner decision OD21); plugin and MCP catalogue locks; claude.ai connectors off; telemetry on with every content flag `0`; version floor 2.1.248). Phase 2 is Anthropic's `settings-hipaa.json` (✅ fetched at commit `9196319`). **Kept from the template:** provider and login lock, managed-only rules/hooks, shell allow rules that do not skip the auto-mode classifier (`classifyAllShell`), the auto-mode `"$defaults"` pins, the template's credential denies. **Papaya's deviations**, each listed in [E8: deviations from the HIPAA template](#e8-deviations-from-the-hipaa-template): credential denies extended to the stack (AWS, GitHub, GCP, Firebase, Docker, kube, Pulumi, Serverless); sandbox with `aws *`/`pulumi *`/`serverless *` excluded plus matching `ask` rules, so they always prompt (refused in `dontAsk`; bypass is off); `autoAllowBashIfSandboxed: true` (OD12), so sandboxed commands are auto-approved in auto mode too and for them the sandbox, not the classifier, is the control (📖 sandboxing, README-hipaa); managed-only mods; version floor 2.1.310 | Community JSON Schema from schemastore.org (not an Anthropic source) plus the key-by-path check; keys and tool names the schema lacks need a documentation source (📖, listed in the test); design tests | That Claude Code enforces it: the live copy is edited in the admin console and compared monthly (layer 2, G18). On laptops without MDM a different login, an API key or a `CLAUDE_CODE_USE_*` variable skips server-managed settings (📖 R1.1.7); `forceLoginMethod`, `forceLoginOrgUUID` and `forceRemoteSettingsRefresh` only hold from the first start if delivered by MDM, because server-managed settings arrive after the first sign-in (📖 [iam](https://code.claude.com/docs/en/iam.md), [settings reference](https://code.claude.com/docs/en/settings-reference.md#forceremotesettingsrefresh)). `excludedCommands` from a user's `~/.claude/settings.json` and from `--settings` still apply: no managed-only lock covers that list (📖 settings reference). An excluded CLI runs code from the repository outside the sandbox (`pulumi` runs the stack program, `serverless` its config and plugins), and a sandboxed command can write that code without a prompt (OD12); the prompt then shows only `pulumi preview` (📖 sandboxing, `excludedCommands` warning) [limit, accepted in layer 2]. Sandboxed reads are a denylist: anything in the home folder not listed is readable without a prompt, and can leave through any allowed domain, e.g. a push to another GitHub repository (📖 sandboxing, "Security limitations"); Linear/Slack tokens and key files that `GOOGLE_APPLICATION_CREDENTIALS` or `KUBECONFIG` point to elsewhere are not listed (⚠️). MCP entries and network domains are placeholders (G9); the `npx -y <pkg>@<version>` pin fixes the top-level package only, its dependencies float [limit] |
| E9 | [`claude/marketplace/`](claude/marketplace/) | Layer 4, ADR-0006: the plugin catalogue is a private marketplace; every third-party source pinned to a commit (`sha`, 📖 [marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference.md)); one review record per entry, with the layer-4 checklist ([`reviews/`](claude/marketplace/reviews/)) | `claude plugin validate` (✅ Claude Code 2.1.319: it fails on an invalid entry, e.g. a missing `repo` or a malformed `sha`); tests that every external source is pinned (`sha`; for npm a bare package name with an exact `version` and no own `registry`; or `sha256`), no `command` source, and every third-party entry has a review record | `claude plugin validate` accepts an unpinned `github` source and a `command` source (✅ mutation), hence the separate pin test. Plugin contents were not reviewed: the vendors and SHAs are placeholders |
| E10 | [`pulumi-policy/`](pulumi-policy/) (phase 2) | Layer 5, OD8: mandatory Pulumi Policies (formerly CrossGuard, 📖 R4.2.1) that stop a deploy on an IAM `Allow` with `*`, `<service>:*` (also spelled with `?`, 📖 [IAM Action element](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_action.html)), `NotAction` or any wildcard in an `iam`/`sts`/`organizations`/`sso`/`identitystore` action, in a managed, role, user or group policy or a role's inline policy; on attaching `AdministratorAccess`, `PowerUserAccess` or any AWS managed `*FullAccess` policy by these routes (the three attachment types, `PolicyAttachment`, the three `*PolicyAttachmentsExclusive` types, `Role.managedPolicyArns`); on an RDS/Aurora cluster without deletion protection; on an S3 public access block with any flag off | `tsc` on the pack, then 35 cases that call each check with hand-made properties and a minimal stand-in for the CLI's arguments (`isType`), with no Pulumi engine and no cloud; type tokens ✅ against `@pulumi/aws` 7.51.1 | Not covered: Identity Center permission sets (`aws:ssoadmin/*`), admin-equivalent names outside the list (e.g. `AdministratorAccess-Amplify`), RDS instances and global clusters, the account-level S3 public access block; and Serverless stacks, which are not Pulumi (layer 5). Retiring a cluster needs an exception (comment in `policies.ts`). A value unknown during preview (e.g. a policy built with `pulumi.jsonStringify` from a resource of the same update) turns the check into `advisory` for that preview (✅ `@pulumi/policy` 1.21.0 `server.js`); the stop then comes during `pulumi up`, possibly after earlier resources were created (⚠️ not run). Access Analyzer (layer 5) is the preview-time check. Customer-managed policies made outside the stack are not checked. The S3 rule checks only `BucketPublicAccessBlock` resources, not that every claim bucket has one |


The AWS action catalogue in [`schemas/aws-actions.json`](schemas/aws-actions.json) is taken from AWS's
machine-readable Service Authorization Reference (✅ `https://servicereference.us-east-1.amazonaws.com/`,
fetched 2026-11-09, 22 services) by [`tools/fetch_aws_actions.py`](tools/fetch_aws_actions.py).
Mutation runs ✅ for E4–E6 (all made the tests fail): `logs:Get*` or `s3:Get*` on `*`; a misspelled
action; a write action; `StringLike` on the subject; the old subject format; an 8-hour session;
an `Allow` in the SCP.

Schemas in [`schemas/`](schemas/) are extracted from GitHub's REST OpenAPI description
(`github/rest-api-description` at commit `2f8f80e47ea4d3292cf4e37ba9d9b25475e06140`, OpenAPI 3.0.3 ✅)
by [`tools/extract_github_schemas.py`](tools/extract_github_schemas.py), which resolves `$ref` and
`nullable`. They do not forbid unknown keys, so a misspelled key passes schema validation; the
key-by-path check ([`tests/schema_keys.py`](tests/schema_keys.py)) catches it (✅ mutation run:
`require_last_pusher_approval` passes the schema and is reported by the key check).

Mutation runs ✅ (each must make the tests fail, and did): `continue-on-error: true` on the risk
stop; `|| true` after the classifier; `if: always() && …` on an apply step; `pulumi up -f`;
a non-"Apply" step running `pulumi up` with `if: failure()`; `exit 1` replaced by `true` in the
tip-of-`main` guard; the guard reading `commits/main` instead of `git/ref/heads/main`; removing
the "approval merged on main's first-parent history" check;
removing the CODEOWNERS line for `deploy-approvals/claims-api/`; a broad CODEOWNERS line after
the L3 section.

Mutation runs ✅ for E8–E10 (each made the tests fail): an `excludedCommands` entry without ` *`;
`Bash(git log *)` in the phase-1 allowlist; `~/.config/gh` removed from the sandbox credentials;
`autoMode.classifyAllShell` off; an MCP allowlist entry with two keys; `computer-use` removed from
`deniedMcpServers`; a phase-2 key added to phase 1; an unpinned plugin source; a policy set to
`advisory`; the `UserPolicy` check, the `Role.managedPolicyArns` check, the `iam`/`sts` wildcard
rule or the `*FullAccess` match removed from the policy pack. Round 2 of the review found mutations the tests missed (an emptied `hard_deny`, a `*` domain, emptied `denyWrite`, an extra package in an MCP command, an npm `package` with its own version), and round 3 more (a template env var or deny rule removed, `Read(~/.kube/**)` narrowed to one file, `autoMode.allow` without `"$defaults"`, an `allowRead` entry, `*:*` in a policy); each now fails a test.

### E8: deviations from the HIPAA template

Phase 2 starts from Anthropic's `settings-hipaa.json` (📖 [README-hipaa](https://github.com/anthropics/claude-code/blob/main/examples/settings/README-hipaa.md)).
Every key of the template is kept as written except these:

| Template key | Phase 2 | Reason |
|---|---|---|
| `permissions.deny` `WebFetch` | moved to `ask` | Engineers read vendor docs during work; each fetch is approved instead (layer 2) [design] |
| `permissions.deny`, `sandbox.credentials`, `filesystem.denyWrite` | extended | Papaya's stack adds `~/.aws` (whole folder, incl. the SSO cache), `~/.config/gcloud`, Firebase CLI token (⚠️ path `~/.config/configstore/firebase-tools.json` not checked), `~/.docker/config.json`, `~/.kube`, `~/.pulumi`; `~/.config/gh` also hidden from the sandbox (finding 20); `~/.serverlessrc` (⚠️ path not checked); env vars `PULUMI_ACCESS_TOKEN`, `PULUMI_CONFIG_PASSPHRASE`, `FIREBASE_TOKEN`, `SERVERLESS_ACCESS_KEY` (⚠️ names not checked) |
| `strictKnownMarketplaces: []` | the private marketplace repository | The catalogue (layer 4, ADR-0006) |
| `allowedMcpServers: []` | catalogue entries | Same; placeholders (G9) |
| `deniedMcpServers` `ide` | not denied | The IDE bridge (VS Code, JetBrains) is local and is how most engineers use Claude Code; cost of denying it is losing editor integration. `claude-in-chrome` and `computer-use` stay denied: built-in servers are exempt from `allowedMcpServers`, only the denylist reaches them (📖 settings reference, `allowedMcpServers`) |
| `strictPluginOnlyCustomization: true` | not set | Project skills and agents live under `.claude/`, an L3 path reviewed through CODEOWNERS (layer 5); hooks and MCP are already managed-only (`allowManagedHooksOnly`, `allowManagedMcpServersOnly`). Setting it would force every team skill through the marketplace [design]. Left open: an engineer's own `~/.claude/skills` and `~/.claude/agents` load. README-hipaa says to keep the key when `disableAutoMode` is set, which is D1's fallback: set it then |
| `sandbox.filesystem.allowManagedReadPathsOnly: true` | not set | It only filters `allowRead`, which managed settings do not use here, and while set, `permissions.blockReadsOutsideWorkingDirectories` does not reach sandboxed commands (📖 settings reference). The docs' pattern `denyRead: ["~/"]` + `allowRead` for the work folders would close the denylist gap but needs a fixed repository location on every laptop (open item for layer 2). Accepted limit, like user `excludedCommands`: a developer's own `allowRead` entry merges and can re-open part of a denied path (📖 sandboxing, "Keep developers from widening the policy"; whether a `credentials.files` deny still holds then: ⚠️) |
| `env` proxy variables | not set | No egress proxy at Papaya is known; sandboxed commands go through the sandbox's own network allowlist |
| `network.allowedDomains` | GitHub, npm, PyPI (placeholders) | Papaya's registries (G9) |
| — | added (diff against the template): `requiredMinimumVersion`, `permissions.defaultMode`, `permissions.allow`, `permissions.ask` (WebFetch and the three excluded CLIs), `blockedMarketplaces`, `disableClaudeAiConnectors`, `pluginConfigs` (managed-only mods), `sandbox.autoAllowBashIfSandboxed: true` (OD12), `sandbox.excludedCommands`, `sandbox.filesystem.denyRead`. Everything else in phase 2 is the template's | Framework layers 2, 4 and 8 (each 📖 at the row cited there) |

Costs engineers will notice, and the workaround (most from README-hipaa, "What developers lose"):

- Inside the sandbox, `git fetch`/`pull`/`push` to the private monorepo, `gh`, and `npm ci` from a
  private registry fail: SSH keys, git credentials, `~/.npmrc`, the GitHub token variables and the
  `gh` configuration are hidden. The engineer runs these at the `!` prompt, outside Claude's tools;
  the agent cannot push or open the pull request itself.
- Docker and Testcontainers fail (`allowAllUnixSockets: false`); on macOS, servers on localhost
  cannot be started or reached (`allowLocalBinding: false`), git over SSH and Go-based CLIs fail TLS
  (📖 sandboxing, troubleshooting). Such tests run at the `!` prompt or in CI.
- `forceRemoteSettingsRefresh`: Claude Code does not start when the settings cannot be fetched
  (`claude auth` still works). `failIfUnavailable`: Claude Code does not start on native Windows
  (no sandbox there; WSL2 works) (📖 sandboxing).
- `/goal` is gone under `allowManagedHooksOnly` (README-hipaa); `cleanupPeriodDays: 30` deletes
  local transcripts after 30 days; every `aws`, `pulumi`, `serverless` call prompts, in auto mode too (`ask` rules; the managed-only rule lock hides "always allow").
- `strictKnownMarketplaces` without a `skills-dir` entry stops skills-directory plugins under
  `.claude/skills/*/.claude-plugin/` from loading; plain `SKILL.md` skills still load (📖 [plugins for
  organizations](https://code.claude.com/docs/en/plugins/org.md)).
- `forceLoginMethod: claudeai` pre-selects but does not enforce the method on the interactive login
  screen, so a Console login is still possible there (📖 iam); `allowedHttpHookUrls` merges entries
  from a developer's own settings, and `allowManagedHooksOnly` is what decides which hooks run
  (README-hipaa).

## Limits of the risk stop

The risk stop answers one framework problem: on GitHub Team nobody sees the prod diff before
apply (framework §1). It catches **risky prod diffs that nobody looked at**. It is not a boundary
against **malicious or prompt-injected code that was approved**:

- The stack's own code runs with the prod deploy role: `npm` packages are installed before the
  credentials (so install scripts get none), but the Pulumi program runs during `preview` and
  `up`, and Serverless plugins during `package`/`diff`/`deploy`. That code could call AWS
  directly, or tamper with files the classifier reads, in the same job. The defence against it
  is the PR review itself, and from phase 2 IAM Access Analyzer and policy packs (layer 5).
- A stronger variant [design, not in the framework]: preview with a separate prod **preview**
  role (read and state access, no write), run the classifier in its own job on a fresh
  checkout without credentials, and assume the deploy role only in a later job after the stop.
  It adds a role and a job split; it is an open question for the owner.
- `pulumi up` previews again before applying. A change made outside the pipeline between the
  two previews (JIT, drift) is not re-checked. `pulumi preview --save-plan` + `pulumi up --plan`
  would bind the two, but update plans are experimental (📖 R4.1.3).
- Concurrency: a running deploy is never cancelled, but GitHub cancels a run that is still
  pending when a newer one arrives for the same group (📖 GitHub docs source,
  `data/reusables/actions/actions-group-concurrency.md`). Some merged commits therefore have no
  deploy run of their own; the newer run deploys them too, and the change record must link both
  commits to that run. `queue: max` would give every commit its own run, but the same page says
  the order "is not guaranteed": an older commit could then deploy after a newer one and undo it
  in prod. So the default is kept on purpose [design].
- The type lists are examples. For types that are missing, the rule on property names
  (`policy`, `role`, `securityGroup`, `vpcConfig`, `public`, `authorization`, `logging`, …;
  a narrower set on creates) catches some changes, not all.
- **Code in the deploy job can act as any prod deploy role.** `id-token: write` is job-wide, so
  install scripts, the Pulumi program and Serverless plugins can request the job's OIDC token
  (⚠️ from memory of GitHub's OIDC docs) and assume either deploy role, since both trust the same
  subject. The two-role split and the install-before-credentials order stop drift and honest
  mistakes, not malicious approved code. Phase-2 roadmap with OD15: a build job without
  `id-token`, and per-role environments (different subjects) or `job_workflow_ref` (G10).
- **Open gap:** nothing proves that a deploy really stopped at `stopped_commit` with the
  approved hash. An approval merged early (naming a commit whose deploy did not stop, with a
  hash computed in advance, which needs knowledge of prod inputs) is accepted if a later change
  **outside** the stack's directory, such as a shared library, produces exactly that diff. Changes
  inside the stack's directory are rejected. Watching the whole repository instead would cancel
  every approval at each unrelated merge in a monorepo. The fix is for the approval-gate app to
  check, on the approval PR, that the stopped run's summary carries the same hash (G19) [design].
  `test_known_gap_early_approval_and_change_outside_the_stack` documents the current behaviour.
- The approver of the approval PR sees **which** prod resources and properties change, not the
  new values (the summary never prints values, to keep secrets out of logs). The values are
  reviewed in the code of the stopped PR. Framework layer 3 and ADR-0004 say the approver "sees
  the prod diff"; that wording is too strong and is corrected in the framework's final pass.
- Any commit to the stack's directory between the stop and the approval merge cancels the
  approval: the author names the newer stopped commit and the owner approves again. In an
  incident that is one more review round.
- `npm ci` runs before the credentials, but its lifecycle scripts can still write to
  `$GITHUB_ENV` / `$GITHUB_PATH` and so influence later steps that hold them.
  `npm ci --ignore-scripts` reduces this where the stack's packages allow it.
- If the newest merge to `main` carries `[skip ci]` (or similar) in its message, no push run
  exists for the tip and the older runs refuse to deploy; prod stays behind until the next merge
  (📖 GitHub docs source, `content/actions/how-tos/manage-workflow-runs/skip-workflow-runs.md`,
  via review). Operator action: merge an empty change.
- Within 7 days, an approved change that is reverted and then merged again with identical code
  passes without a new approval. This is intended: it is the same code and the same prod diff
  that an owner approved.
- The binding relies on squash-only merges (`ruleset-main.json`); with merge commits, a PR's
  inner commits would be invisible to the first-parent check.

## Findings from writing these files

Points the framework text does not yet say; carried into the framework in the final pass.
Owner decisions 2026-11-09 (framework OD14–OD18): findings 1, 3 and 4 accepted; the risk stop keeps
its current scope (OD15); the early-approval gap is an accepted limit for G19 to close (OD18).
Step 2: finding 16 accepted (OD19); the job-wide OIDC token limit goes to the phase-2 roadmap
with OD15 (OD20).

1. **The risk-stop classifier must be an L3 path** [design]. The deploy runs it from the merged
   commit, so a PR that edits it together with an IAM change, approved by the domain team, could
   switch the stop off. `CODEOWNERS` adds `/tools/risk-stop/` to the L3 owner team. Needs owner
   confirmation: it extends the canonical L3 list of framework layer 5.
2. **An approval must be bound to git history, not only to a hash** [design]. Two review rounds
   found ways for one PR to carry its own risky change and approval, or for an approval to be
   reused. Rules now: read from git objects only; file named `<stopped_commit>.yaml`, never
   edited; stopped commit and approval commit both on `main`'s first-parent history, in that
   order; the approval commit touches only `deploy-approvals/<stack>/`; the stack's directory
   and the classifier unchanged since the stopped commit; at most 7 days old.
3. **Squash-only merges** [design]: `ruleset-main.json` allows only squash, so each PR is one
   commit on `main`. Cost: PR-internal history is not kept on `main`.
4. **Deploy only the tip of `main`** [design]: people with write access can re-run a workflow run
   for up to 30 days, with the same `GITHUB_SHA` (📖 GitHub docs source,
   `content/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs.md`, via review). An
   old deploy run re-run would roll prod back without any approval. `deploy-prod.yml` stops unless
   the run's commit is the current tip of `main`, read with `GET /repos/{owner}/{repo}/git/ref/heads/main`
   (✅ branch-only form; `commits/main` could resolve to a tag named `main`). This is a new
   condition for framework layer 3's "merge approval = deploy approval" list.
5. **Classification beyond the framework's categories** [design]: the property-name rule, the
   audit/detection category and "an unknown operation stops" go beyond layer 3's list
   (stateful replace/delete, IAM, network, policy finding).
6. **The approval hash must cover changed values**, not only resource names, or an approval for
   one IAM policy would let a different change to the same policy through; and it must leave out
   values that change on every build, or an approval never matches. ⚠️ From memory, not checked:
   Serverless puts a timestamped path in the Lambda `Code.S3Key` and a code hash in
   `AWS::Lambda::Version` logical IDs; both are left out of the hash.
7. **Fail-safe CODEOWNERS default** [design]: without it, root `package.json`, a new stack or a new
   `deploy-approvals/<stack>/` folder would be unowned, and GitHub then accepts an approval from
   any writer (📖 about code owners).
8. **Same-repository reusable workflows can use `uses: $/.github/workflows/<file>`**, which GitHub
   now recommends: it resolves to the running commit, not to the runner's workspace (📖 GitHub docs
   source, `data/reusables/actions/reusable-workflow-calling-syntax.md`; flagged by zizmor's
   `self-repository` audit). `actionlint` 1.7.12 (✅ latest release on 2026-11-09, published
   2026-03-30) does not know the syntax; `validate.sh` ignores only that message.
9. **`runner.temp` is not available in job-level `env`** (✅ caught by `actionlint`); paths use
   `$RUNNER_TEMP` inside steps.

### Step 2 (identity and access)

10. **SCP "protect the org trail" is mostly redundant** for member accounts: they cannot delete
    an organization trail or turn its logging off anyway (📖 R2.6.2). E5 instead denies changes
    to any trail inside prod accounts. The framework's layer-1 bullet is reworded in the final pass.
11. **"Metadata" reads can leak configuration, data or secrets** (⚠️ response contents from
    memory of the API references): `lambda:ListFunctions` and `ecs:DescribeTaskDefinition` return
    environment variables and cannot be limited to one resource (✅ catalogue: not resource-scoped);
    `lambda:GetFunction` also returns a code download URL; `ecs:DescribeTasks` returns container
    environment overrides; `cloudformation:DescribeStacks` returns stack outputs (it could be scoped
    per stack); `cloudformation:DescribeStackEvents` returns `ResourceProperties`, "the properties
    used to create the resource" (📖 [StackEvent](https://docs.aws.amazon.com/AWSCloudFormation/latest/APIReference/API_StackEvent.html)),
    which for a function includes its environment variables (⚠️ inferred); `logs:DescribeQueries`
    returns other users' query strings. E6 leaves all of them out [design];
    `lambda:GetFunctionConfiguration` is granted per function instead.
12. **AWS's annotations are signals, not a classification of customer data**: `IsDataPlane` marks
    `cloudwatch:GetMetricData` too; `sqs:ListQueues` is not marked `IsList`; and many `IsList`
    actions return data or configuration (`s3:ListBucket` object keys, `ec2:Describe*` launch
    templates, `ssm:ListCommandInvocations` output; ✅ annotations in the catalogue, ⚠️ response
    contents from memory). The tests use an explicit allowlist for `Resource: "*"`. One entry has a
    condition: `states:ListExecutions` returns execution names, so names must not be built from
    claim data [design].
13. **Two prod deploy roles** (framework layer 1 already implies it): the SCP exempts the Pulumi
    role from the Lambda-update deny, but not the Serverless role, so `serverless deploy function`
    cannot change a function outside CloudFormation (drift). It does not stop malicious code in
    the job (Limits). `deploy-prod.yml` has one credentials step per tool, so an unset role
    variable fails instead of falling back to the other role.
14. **The claim-data deny assumes a naming convention** [design]: every legitimate reader must
    match `app-claims-*` or a `DataRead-*` permission set. Lambda execution roles behind SQS event
    sources, Step Functions execution roles and an AWS Backup role that reads the bucket would be
    denied otherwise (only service-linked roles are outside SCPs, 📖 R2.3.2). Phase-2 prerequisite:
    inventory the real callers of these actions (CloudTrail, IAM last-accessed data) and add them
    before the SCP is attached.
15. **The trail deny blocks every principal in prod accounts**, including deploy roles and
    `OrganizationAccountAccessRole`: a member-account trail can only be changed after a temporary
    change to the SCP (an L3 path), or an exempt audit role would have to be added [design].
16. **Exempt role names must be protected** (OD19): the exemptions are name patterns, so anyone in
    a prod account who could create or re-trust a role named `app-claims-*` or `cfn-deployment-*`
    would bypass both denies. E5 lets only `github-prod-deploy-pulumi` change those roles.
    - **Today that role deploys every Pulumi stack**, not only the IAM stack, and any job in the
      deploy workflow can obtain it (OD20). So "only the IAM stack" holds only after OD20 gives the
      IAM stack its own role and OIDC subject; until then the protection is "only an approved prod
      Pulumi deploy" (agent's reading of OD19, confirmed by the owner 2026-11-09).
    - **Residual risks:** a principal that may pass an `app-claims-*` role could create a new
      function with it (`lambda:CreateFunction` is not denied), and one that may pass
      `cfn-deployment-*` to CloudFormation could change any function through a template;
      `iam:PassRole` is left out on purpose because the Serverless role must pass
      `cfn-deployment-*`. An `InfraOperator-*` grant may change an `app-claims` function's code
      and so read claim data indirectly (accepted with break-glass, ADR-0005; JIT reconciliation
      in layer 7 is the control).
    - **Constraints and prerequisites (phase 2):** Serverless services cannot create their own
      `app-claims-*` execution roles (CloudFormation runs as `cfn-deployment-*`, not exempt); those
      roles live in the Pulumi IAM stack and are referenced by ARN. The protected roles must exist
      before the SCP is attached, and if `github-prod-deploy-pulumi`'s own trust breaks (e.g. the
      subject-format opt-in of E4), only an SCP change from the management account (an L3 path)
      can repair it.
17. **Gaps in the claim-data deny, under G13** (⚠️ not verified): S3 requests through access
    points may be authorised on the access-point ARN, not the bucket ARN; KMS `Decrypt` on the
    claim keys would be a second layer.
    The deny also covers `sqs:StartMessageMoveTask` (a write, ✅ catalogue), which could move claim
    messages to another queue; cost: a JIT grant cannot redrive a claims dead-letter queue.

### Step 3 (agent runtime, supply chain, policy pack)

18. **The settings schema on schemastore.org is community-maintained and lags behind**: it accepts
    unknown keys and lacks `allowedProviders` and `managedSourcesBehavior` (✅ checked). The tests
    therefore check keys by path and require a documentation source for every key it lacks.
19. **The phase-1 allowlist gives no protection for `~/.aws`, and a "read-only" wildcard rule
    can write files** (review step 3): Claude Code runs a built-in set of read-only commands
    (`cat`, `grep`, `head`, read-only `git` …) without a prompt in every mode, and the set is not
    configurable (📖 [permissions](https://code.claude.com/docs/en/permissions.md#read-only-commands)).
    Leaving `cat` out of the allowlist protected nothing. Worse, `Bash(git log *)`, `Bash(git show *)`
    and `Bash(git diff *)` also match `--output=<path>`, which writes chosen content to any path
    (✅ git 2.34.1; the docs use `git log --output=<file>` as an example match). The allowlist is now
    two exact repo scripts, and those run whatever `package.json` says [limit]. Owner decision OD21
    adds two keys to phase 1: a `Read(~/.aws/**)` deny rule, which also applies to recognized
    `cat`/`head`/`tail` (📖 permissions), and `autoMode.classifyAllShell` (📖, ≥ 2.1.193), so the two
    allow rules do not skip the auto-mode classifier. Left open until the phase-2 sandbox: a command
    that reads files without naming them (`grep -r` from `~`) or a script that opens `~/.aws` itself
    is not covered by a deny rule (📖 permissions). Not chosen: `blockReadsOutsideWorkingDirectories`
    (📖, ≥ 2.1.257), which would also block every read outside the repository.
20. **Credential paths beyond the HIPAA template** [design]: `~/.aws` as a whole (the SSO token
    cache opens every role of the engineer, layer 2), `~/.kube`, `~/.pulumi`, `~/.config/gcloud`,
    the Firebase CLI token, `~/.docker/config.json`. `~/.config/gh` must be hidden from the sandbox
    too, not only from Claude's Read tool: sandboxed commands run without a prompt (OD12) and
    `api.github.com` is allowed, so a readable token lets the agent approve PRs as the engineer (OD5).
    This closes only the sandboxed route: an excluded CLI (`pulumi`, `serverless`) runs repository
    code outside the sandbox with full access (finding 22), so hiding credentials from the sandbox
    is hygiene, not a boundary (ADR-0007).
21. **TypeScript 7 is not yet supported by `@pulumi/pulumi`** (✅ npm peer-dependency error:
    `typescript >= 3.8.3 < 7`); the pack pins TypeScript 6.0.3.
22. **`sandbox.excludedCommands` entries match like `Bash(...)` rules** (📖
    [sandboxing](https://code.claude.com/docs/en/sandboxing.md#run-commands-outside-the-sandbox-with-excludedcommands)):
    `aws` alone matches only `aws` with no arguments, so the first draft kept every `aws` call in the
    sandbox, where it fails (no `~/.aws`, no AWS endpoints). Entries are now `aws *`, `pulumi *`,
    `serverless *`. The docs also answer the framework's ⚠️ on matching: every command in the call
    must match; a call with `cd`, a redirect, `$(...)` or a subshell stays sandboxed; the match is on
    the text, so `/usr/local/bin/aws`, a script that calls `aws`, and `npx serverless` do not match.
    Excluded commands go through the permission flow: they prompt in Manual mode, but in auto mode
    the classifier decides (📖 sandboxing), so phase 2 also lists them as `ask` rules, which prompt
    in every mode (📖 auto-mode-config). The prompt shows the command (`pulumi preview`), not the
    repository code it runs, which a sandboxed command may have changed without a prompt.
23. **A mandatory Pulumi policy is only advisory while a value is unknown** (✅ `@pulumi/policy`
    1.21.0 `server.js` catches `UnknownValueError` and reports `advisory`). A PR-time or prod
    preview of a policy built from a resource of the same update passes; the stop comes during the
    update. Access Analyzer is the preview-time check (layer 5).
24. **The first policy pack missed the usual ways to grant admin** (review step 3): user and
    group policies, `AdministratorAccess` attached by ARN, `Role.managedPolicyArns`, and wildcards
    such as `iam:Pass*`. All are now covered and tested. Round 2: IAM also accepts `?`, so `s3:?*` and
    `*?` are full wildcards (📖 IAM Action element); covered too. Round 3: a wildcard in the service
    prefix (`*:*`, `s?:Get*`) is refused as a full wildcard (⚠️ whether IAM accepts it is unverified).
25. **The template's auto-mode `"$defaults"` pins keep the built-in rules in place** (📖
    auto-mode-config: a list without `"$defaults"` replaces the built-in rules; entries from managed
    settings cannot be removed). The first phase-2 draft dropped them, which would let a developer's
    own `hard_deny: []` discard the built-in data-exfiltration rule. Restored and tested. They are not
    a policy boundary: a developer's own `autoMode.allow` or `environment` entries still widen what the
    classifier approves ("the combination is additive, not a hard policy boundary", same page), and
    `allowManagedPermissionRulesOnly` does not cover `autoMode` [limit]. For prod CLIs the boundary is
    the managed `ask` rules plus layers 1 and 3.

## Latest run

`validate.sh` on 2026-11-09 (✅, output shortened; yamllint and actionlint printed nothing):

```text
=== tool versions ===
Python 3.10.12
jsonschema 4.26.0 | PyYAML 6.0.3
jq: jq-1.6
yamllint: yamllint 1.38.0
shellcheck: ShellCheck - shell script analysis tool
actionlint: 1.7.12
zizmor: zizmor 1.30.1
claude: 2.1.319 (Claude Code)
node: v20.15.0
npm: 10.7.0
=== JSON syntax (jq) ===
checked 24 files
actionlint done
=== GitHub Actions security (zizmor, offline, auditor persona) ===
No findings to report. Good job!
=== Claude Code plugin marketplace (claude plugin validate) ===
✔ Validation passed
=== Pulumi policy pack (tsc + unit cases, no Pulumi engine, no cloud) ===
35/35 cases passed; all policies mandatory
=== unit tests (python3 -m unittest) ===
Ran 108 tests in 1.016s
OK
=== result ===
RESULT: all executed checks passed
```
