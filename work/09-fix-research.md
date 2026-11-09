# 09 — Kiểm docs cho các mục sửa F1–F10

## English summary

- Records the documentation checks made before the fixes in `work/08-fix-proposals.md` (step 1 of
  the agreed process). Four read-only research subagents checked AWS, GitHub/npm/Linear, Claude
  Code and Kubernetes/k0s facts against official documentation on 2026-11-09. Later rounds added
  CI checks on GitHub Team, GCP/Firebase/alerting (R9.5–R9.6), Thailand and Hong Kong law (R9.7)
  and Expo/EAS mobile releases (R9.8) for the follow-up fixes F11–F17. R9.9 adds the sources
  found in the verify step (`work/10-verify.md`, V7 and V11).
- Rows are cited in the deliverable as **R9.x** (this file), next to the existing R*x.y* rows of
  `work/02-research.md`. Verdicts: confirmed / partly / contradicted / not found.
- Quotes marked "per fetcher" come from a summarising web fetcher, not a verbatim copy; treat them as
  📖 with that caveat.
- Findings that change a proposal are listed under "Impact on the fixes" for each part.

> Working note. Updated: 2026-11-09 · Status: complete (R9.1–R9.9; the Identity Center resource types used for E16 were read from the AWS Service Reference file `sso.json`, see `work/08-fix-proposals.md`)

---

## R9.1 GitHub, npm, Linear (read 2026-11-09)

| Row | Question | Answer | Verdict | Source |
|---|---|---|---|---|
| R9.1.1 | Org-wide 2FA requirement | Org owners can require 2FA for members, outside collaborators and billing managers. The page names no plan restriction, but does not say "Team" either | partly | [requiring 2FA](https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-two-factor-authentication-for-your-organization/requiring-two-factor-authentication-in-your-organization) |
| R9.1.2 | SAML SSO for an org | "To use SAML single sign-on, your organization must use GitHub Enterprise Cloud." EMU is an Enterprise Cloud enterprise type | confirmed | [SAML SSO](https://docs.github.com/en/enterprise-cloud@latest/organizations/managing-saml-single-sign-on-for-your-organization/about-identity-and-access-management-with-saml-single-sign-on) |
| R9.1.3 | List price | Team $4, Enterprise $21 per user per month (read 2026-11-09; per fetcher) | confirmed | [pricing](https://github.com/pricing) |
| R9.1.4 | Environment required reviewers and wait timer | On Free, Pro and Team "required reviewers are only available for public repositories"; wait timers likewise (per fetcher) | confirmed (matches R3.1.2) | [deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments) |
| R9.1.5 | Audit-log REST API on Team | The UI article says "Organizations on GitHub Enterprise Cloud can use the GraphQL API and REST API to interact with the audit log." No statement that Team can | not found for Team | [reviewing the audit log](https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization) |
| R9.1.6 | Audit-log streaming | Enterprise Cloud only | confirmed | [GitHub's plans](https://docs.github.com/en/get-started/learning-about-github/githubs-plans) |
| R9.1.7 | Audit-log retention and UI export | 180 days; UI export to JSON or CSV by org owners, capped at 100 MB compressed or 10 minutes; no plan note | confirmed / partly (Team not named) | as R9.1.5 |
| R9.1.8 | Actions artifact and log retention | Default 90 days; private repos 1–400 days; no per-plan difference found; from 2026-10-01 retention also covers checks, workflow runs and commit statuses (per fetcher) | confirmed | [retention](https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization) |
| R9.1.9 | Who can apply labels | Triage role and above | confirmed | [repository roles](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/repository-roles-for-an-organization) |
| R9.1.10 | Review API | Review has `user`, `state`, `submitted_at`, `commit_id`, `author_association`; APPROVE can be sent through `POST .../reviews`; no field shows web vs API; whether an App approval counts is not documented | partly | [pull request reviews](https://docs.github.com/en/rest/pulls/reviews) |
| R9.1.11 | `gh` token storage | Default is the system credential store; "gh will fallback to writing the token to a plain text file"; `--insecure-storage` forces plaintext; no flag forbids the fallback | confirmed | [gh auth login](https://cli.github.com/manual/gh_auth_login) |
| R9.1.12 | Fine-grained PAT policy | Owners can restrict classic PATs, require approval of fine-grained PATs and cap lifetimes; plan availability not stated | confirmed / plan not found | [PAT policy](https://docs.github.com/en/organizations/managing-programmatic-access-to-your-organization/setting-a-personal-access-token-policy-for-your-organization) |
| R9.1.13 | npm scripts | `ignore-scripts`: "npm does not run scripts specified in package.json files" (coverage of dependencies not stated explicitly); `npm rebuild <pkg>` runs install scripts of the named packages only; npm v11 has an `allowScripts` policy in package.json / `allow-scripts` config (rejected as a flag on `npm ci`) | partly | [npm config v11](https://docs.npmjs.com/cli/v11/using-npm/config), [npm rebuild](https://docs.npmjs.com/cli/v11/commands/npm-rebuild) |
| R9.1.14 | Linear history and export | Activity feed records changes and actors; webhooks send previous values of changed properties; CSV export by admins without per-field history; audit log is Enterprise only, 90 days | partly | [API and webhooks](https://linear.app/docs/api-and-webhooks), [exporting data](https://linear.app/docs/exporting-data), [audit log](https://linear.app/docs/audit-log) |
| R9.1.15 | Ruleset approvals on Team | Repo-level rulesets on Team; required approvals 0–10; code-owner review; org-level rulesets Enterprise only. A rule requiring teams to review "when a pull request changes certain files or directories" exists, but its availability on Team was not found | confirmed / not found | [about rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets), [available rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) |

**Impact on the fixes:**

- **F2:** 2FA can be required (plan not named, so "verify in the org settings" ⚠️). SAML/EMU need
  Enterprise Cloud (R9.1.2); price gap $17 per user per month (R9.1.3). A review cannot be told apart
  as web or API (R9.1.10), so the `gh` deny rule stays hygiene.
- **F3:** a 2-approval rule for process paths cannot be a path-scoped ruleset on Team (R9.1.15 not
  found), and the count is repo-wide. So the second approval is checked by the approval-gate app
  [design]. `gh` may fall back to plaintext (R9.1.11): the guide tells engineers to check
  `gh auth status`.
- **F6:** Actions retention can be raised to 400 days (R9.1.8). That is still short of 6 years, so the
  nightly export is still needed, but the export can catch up later. The audit-log API is not
  confirmed on Team (R9.1.5): phase 1 uses a monthly UI export by an org owner, recorded as a manual
  step. Linear: approval evidence comes from webhook or API export into S3, not from Linear's audit
  log (R9.1.14).
- **F1:** use npm v11 `allowScripts` in `package.json` plus `npm ci --ignore-scripts`; whether
  `ignore-scripts` also covers dependencies is ⚠️ (not stated) until tested.
- **F9:** labels can be applied by Triage and above (R9.1.9), so the label alone proves nothing. This
  confirms the review's finding E-2.

---

## R9.2 AWS (read 2026-11-09)

| Row | Question | Answer | Verdict | Source |
|---|---|---|---|---|
| R9.2.1 | `iam:PermissionsBoundary` pattern | IAM User Guide example: Allow create/attach/put only with `StringEquals iam:PermissionsBoundary` = the boundary ARN; Deny changes to the boundary policy (`CreatePolicyVersion`, `DeletePolicy`, `DeletePolicyVersion`, `SetDefaultPolicyVersion`); Deny removing the boundary. Written for users; for roles the AWS Security Blog uses `iam:CreateRole` and `iam:DeleteRolePermissionsBoundary`. The exact role-action list was not read (Service Authorization Reference did not load) | confirmed for users, partly for roles | [permissions boundaries](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html), [blog](https://aws.amazon.com/blogs/security/when-and-where-to-use-iam-permissions-boundaries/) |
| R9.2.2 | Identity Center CloudTrail events | Event source `sso.amazonaws.com`; the list includes CreateAccountAssignment, DeleteAccountAssignment, CreatePermissionSet, UpdatePermissionSet, PutInlinePolicyToPermissionSet, AttachManagedPolicyToPermissionSet, AttachCustomerManagedPolicyReferenceToPermissionSet, PutPermissionsBoundaryToPermissionSet, ProvisionPermissionSet (and the delete/detach variants). Which account's trail records events made from a delegated admin: not found | confirmed / not found | [Identity Center in CloudTrail](https://docs.aws.amazon.com/singlesignon/latest/userguide/sso-info-in-cloudtrail.html) |
| R9.2.3 | Delegated administrator for Identity Center | Possible (one at a time). It cannot enable or delete Identity Center, manage permission sets provisioned in the management account, register delegated admins, or change user access in the management account | confirmed | [delegated admin](https://docs.aws.amazon.com/singlesignon/latest/userguide/delegated-admin-how-to-register.html) |
| R9.2.4 | `OrganizationAccountAccessRole` | Created automatically for accounts created through Organizations, not for invited accounts; "full administrative permissions in the member account", trusted by the management account | confirmed | [accessing member accounts](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_access.html), [cross-account role](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_access-cross-account-role.html) |
| R9.2.5 | Centralized root access | Exists: root credentials management (delete member-account root password, keys, MFA) and privileged root actions through `sts:AssumeRoot`; new Organizations accounts have no root credentials by default | confirmed | [centralize root access](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-enable-root-access.html) |
| R9.2.6 | SCP scope | SCPs affect all users and roles in member accounts "including the root user" (few exceptions); no effect on the management account; "do not affect any service-linked role". `OrganizationAccountAccessRole` is not named, so it is covered by the general rule (inference) | confirmed / partly | [SCPs](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html) |
| R9.2.7 | CloudWatch Logs data protection | Audit and mask sensitive data at ingestion (earlier events stay unmasked); masked "at all egress points, including CloudWatch Logs Insights, metric filters, and subscription filters"; `logs:Unmask` needed to see it (it is in `CloudWatchLogsFullAccess`) | confirmed | [mask sensitive data](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/mask-sensitive-log-data.html) |
| R9.2.8 | Managed data identifiers for Papaya's countries | **None** for Vietnam, Thailand or Hong Kong: health identifiers exist only for US, GB, FR, CA, EU; `NationalIdentificationNumber` only DE, ES, IT; `BankAccountNumber` only DE, ES, FR, GB, IT, US | contradicted (no coverage) | [managed identifiers](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL-managed-data-identifiers.html) |
| R9.2.9 | Custom data identifiers | Supported; at most 10 per policy; regex at most 200 characters | confirmed | [custom identifiers](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL-custom-data-identifiers.html) |
| R9.2.10 | Price | "Data protection costs $0.12 per GB of data scanned" (2023 announcement); per-Region table row not read | partly | [announcement](https://aws.amazon.com/about-aws/whats-new/2023/04/amazon-cloudwatch-logs-data-protection-aws-commercial-regions/) |
| R9.2.11 | Aurora PostgreSQL IAM database authentication | Supported; 15-minute tokens; policy grants `rds-db:connect` on the `dbuser` ARN; "CloudWatch and CloudTrail don't log IAM authentication"; once `rds_iam` is granted, IAM auth takes precedence over passwords for that user | confirmed | [IAM DB auth](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/UsingWithRDS.IAMDBAuth.html), [policy](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/UsingWithRDS.IAMDBAuth.IAMPolicy.html) |
| R9.2.12 | S3 Object Lock | Compliance mode: no user, root included, can delete or shorten retention; requires versioning; cannot be disabled once enabled. Enabling on an existing bucket: not found | confirmed / not found | [Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html) |
| R9.2.13 | CloudTrail identity of changes CloudFormation makes through a stack role | Not documented in what was read; `invokedBy` appears for requests made by a service role. `UpdateStack` events carry the caller and the stack ARN | not found | [userIdentity](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html), [CloudFormation in CloudTrail](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-api-logging-cloudtrail.html) |

**Impact on the fixes:**

- **F4:** masking with **custom** identifiers only (≤ 10 regexes, ≤ 200 characters) for national IDs
  and bank accounts of VN/TH/HK; free-text medical content cannot be caught by a regex. So masking is a
  secondary layer; the SAST rule and code review stay the primary control, stated honestly. Only events
  ingested after the policy is set are masked: apply it before the log group is opened. No role readable
  by agents gets `logs:Unmask` or `CloudWatchLogsFullAccess`.
- **F7:** `OrganizationAccountAccessRole` exists in accounts created through Organizations, with full admin
  access, and SCPs apply to it (inference): deny its use in the prod OU except in break-glass. Centralized
  root access is available: remove member-account root credentials. Identity Center events are
  confirmed for alerting.
- **F1:** boundary pattern confirmed for users and for `CreateRole` (blog); the full role action list ⚠️.
- **F5:** IAM database auth for CI is fine, but connections are not in CloudTrail: database-side logging
  is needed (`pgaudit` or `log_connections`, not researched ⚠️; Database Activity Streams are already in
  layer 7).
- **F6:** use a new bucket created with Object Lock (existing-bucket enablement not confirmed).
- **C-5 (outside the ten):** CloudFormation attribution stays an open item, measured in item 1.1.

---

## R9.3 Kubernetes and k0s (read 2026-11-09; k0s docs show v1.37.2+k0s.1, Papaya's version unknown)

| Row | Question | Answer | Verdict | Source |
|---|---|---|---|---|
| R9.3.1 | Extra kube-apiserver flags on k0s | `spec.api.extraArgs` map; "Any behavior triggered by these parameters is outside k0s support" | confirmed | [k0s configuration](https://docs.k0sproject.io/stable/configuration/) |
| R9.3.2 | Audit logging on k0s | Off by default ("does not have any audit policy configuration"); "users can customize it in spec.api.extraArgs"; no k0s page with an end-to-end example | partly | [k0s CIS benchmark](https://docs.k0sproject.io/head/cis_benchmark/) |
| R9.3.3 | Kubernetes audit | `--audit-policy-file` (no policy, no events), `--audit-log-path`; level `Metadata` logs user, verb, resource, without bodies; the example logs Secrets at `Metadata` | confirmed | [auditing](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/) |
| R9.3.4 | Structured authentication (`--authentication-config`) | Alpha 1.29, beta 1.30, stable 1.34; JWT issuers with `claimValidationRules` (CEL) and `claimMappings.username`; can trust an external issuer such as GitHub's `https://token.actions.githubusercontent.com` (pairing is inference, no GitHub example); cannot be combined with `--oidc-*` flags; `discoveryURL` can point to a mirror; JWKS fetched at runtime, no inline JWKS found | confirmed (mechanism) | [authentication](https://kubernetes.io/docs/reference/access-authn-authz/authentication/) |
| R9.3.5 | Structured authentication on k0s | Not documented; k0s's OIDC example uses only `--oidc-*` flags through `extraArgs` | not found | [k0s OIDC](https://docs.k0sproject.io/head/examples/oidc/oidc-cluster-configuration/) |
| R9.3.6 | Time-limited ServiceAccount tokens | `kubectl create token --duration`; server may shorten; long-lived Secret-based tokens still possible by hand but discouraged | confirmed | [service accounts admin](https://kubernetes.io/docs/reference/access-authn-authz/service-accounts-admin/) |
| R9.3.7 | RBAC escalation paths | `escalate`, `bind`, `impersonate`, `create serviceaccounts/token`; `list`/`watch` on Secrets reveal contents; creating workloads grants the API access of any ServiceAccount in the namespace; `nodes/proxy` "bypasses audit logging and admission control" | confirmed | [RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/) |
| R9.3.8 | GitHub-hosted runners to a private network | Documented options only at a high level (API gateway with OIDC, WireGuard overlay) | partly | [private networking](https://docs.github.com/en/actions/how-tos/manage-runners/github-hosted-runners/connect-to-a-private-network) |
| R9.3.9 | GitHub OIDC `sub` format | Repositories created after 2026-07-15 use an immutable format with IDs (matches the existing ⚠️ R3.7 A2); a CEL rule written for the old format would fail on new repositories | confirmed | [GitHub OIDC reference](https://docs.github.com/en/actions/reference/security/oidc) |

**Impact on the fixes:**

- **F8:** audit logging and OIDC trust on k0s are possible only through `extraArgs`, which is outside k0s
  support (R9.3.1): state this as a risk. Interim RBAC: no Secret read, no `escalate`/`bind`/`impersonate`,
  no `serviceaccounts/token`, no `nodes/proxy`. Creating workloads already grants the ServiceAccounts of
  that namespace (R9.3.7): keep the deploy namespaces free of privileged ServiceAccounts. Target
  structured authentication needs Kubernetes ≥ 1.30 (GA 1.34) and an API server reachable from the
  runner (R9.3.8). The CEL rule must match the repository's actual `sub` format (R9.3.9).

---

## R9.4 Claude Code (read 2026-11-09)

| Row | Question | Answer | Verdict | Source |
|---|---|---|---|---|
| R9.4.1 | Bash deny rules for `gh pr review` | `*` may be anywhere in a rule ("at the start, in the middle, or at the end"), so `Bash(gh pr review *)` and `Bash(gh api *reviews*)` are valid; deny rules apply when any subcommand of a compound command matches; they do not match other forms such as `bash -c '…'` or an absolute path ("isn't a security boundary around the program"); a PreToolUse hook's allow does not override a deny | confirmed | [permissions](https://code.claude.com/docs/en/permissions.md) |
| R9.4.2 | MCP allowlist and plugin servers | The allowlist blocks non-matching servers "wherever it's defined, including plugin servers"; stdio servers match by `serverCommand`, remote servers by `serverUrl`; `serverName` "is not a security control"; `allowManagedPermissionRulesOnly` does not enforce the MCP allowlist | confirmed | [managed MCP](https://code.claude.com/docs/en/managed-mcp.md) |
| R9.4.3 | Plugin-bundled MCP server | Documented: `.mcp.json` in the plugin runs `node ${CLAUDE_PLUGIN_ROOT}/server.js`; the plugin path changes per version, and how `${CLAUDE_PLUGIN_ROOT}` expands inside a `serverCommand` allowlist entry is not documented | confirmed / not found | [plugin components](https://code.claude.com/docs/en/plugins/components.md) |
| R9.4.4 | Pinning the marketplace | `strictKnownMarketplaces` github/git sources accept `ref` (and "An entry without `ref` doesn't cover a source with `ref`"); there is **no `sha`** field for marketplace sources | partly | [org plugins](https://code.claude.com/docs/en/plugins/org.md), [marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference.md) |
| R9.4.5 | Pinning a plugin | Plugin `source` for `github`, `url`, `git-subdir` takes `sha` (full 40-character commit; checked out when both `ref` and `sha` are set); relative sources resolve from the marketplace's files | confirmed | [marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference.md) |
| R9.4.6 | Auto-update | Off by default for marketplaces other than Anthropic's and those added from claude.ai; managed `autoUpdate` on an `extraKnownMarketplaces` entry locks the toggle; `DISABLE_AUTOUPDATER` in managed `env` turns plugin auto-update off | confirmed | [plugin loading](https://code.claude.com/docs/en/plugins/loading.md), [org plugins](https://code.claude.com/docs/en/plugins/org.md) |
| R9.4.7 | Force-enabled plugins and hooks | Managed `enabledPlugins: true` force-enables (needs the marketplace registered and allowed); under `allowManagedHooksOnly` hooks of force-enabled plugins keep running, hooks of other plugins are blocked | confirmed | [settings reference](https://code.claude.com/docs/en/settings-reference.md) |
| R9.4.8 | OTel tool events | `tool_decision` / `tool_result` carry `tool_name` and decision by default; Bash command text and MCP tool names only with `OTEL_LOG_TOOL_DETAILS=1` | confirmed | [monitoring usage](https://code.claude.com/docs/en/monitoring-usage.md) |

**Impact on the fixes:**

- **F2:** the `gh pr review` deny rules are valid syntax and hygiene only (R9.4.1); state the bypasses.
- **F3:** the marketplace can be pinned to a `ref` but not a commit (R9.4.4), so it is pinned to a
  release **tag** that a tag ruleset protects (⚠️ tag rulesets not researched here). Each plugin,
  internal ones included, carries a `sha` (R9.4.5), so the internal plugin moves from `./plugins/…` to a
  `github` source with `sha`. Auto-update stays off (R9.4.6); updates are a reviewed change of the pin.
  Local MCP servers: an exact `serverCommand` that pins an immutable artifact. For third-party servers
  the clearest documented form is a container image by digest [design]; plugin-bundled servers are
  matched by `serverCommand` too, but their path changes per version (R9.4.3 ⚠️), so they are
  re-allowlisted on each update.

---

## R9.5 CI security checks on GitHub Team (read 2026-11-09; for F16)

| Row | Question | Answer | Verdict | Source |
|---|---|---|---|---|
| R9.5.1 | Secret Protection / Code Security on Team | "You must be on a GitHub Team or GitHub Enterprise plan in order to purchase GitHub Code Security or GitHub Secret Protection"; Secret Protection = secret scanning + push protection; Code Security = CodeQL code scanning, Copilot Autofix, dependency review | confirmed | [about Advanced Security](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security) |
| R9.5.2 | Price | Secret Protection $19, Code Security $30 per active committer per month (marketing page); active = pushed a commit in the last 90 days | confirmed | [advanced-security](https://github.com/enterprise/advanced-security), [billing](https://docs.github.com/en/billing/concepts/product-billing/github-advanced-security) |
| R9.5.3 | Dependency review action on private repos | Needs a license ("GitHub Advanced Security license" in the README; newer docs list dependency review under Code Security); fails on vulnerabilities at or above `fail-on-severity` and on licenses outside `allow-licenses` | partly | [dependency-review-action](https://github.com/actions/dependency-review-action) |
| R9.5.4 | Dependabot on private repos, Team | Alerts and security updates free on every plan | confirmed | [security features](https://docs.github.com/en/code-security/getting-started/github-security-features) |
| R9.5.5 | CodeQL languages | JavaScript/TypeScript, Python, GitHub Actions workflows; no IaC on the languages page (absence) | confirmed / partly | [CodeQL languages](https://codeql.github.com/docs/codeql-overview/supported-languages-and-frameworks/) |
| R9.5.6 | Trivy misconfiguration scanning | Terraform, CloudFormation, ARM, Helm, Dockerfile, Kubernetes; Serverless Framework and Pulumi not listed | confirmed / not found | [Trivy misconfiguration](http://trivy.dev/latest/docs/scanner/misconfiguration/) |
| R9.5.7 | ECR scanning | Basic (OS packages; manual or on push) vs enhanced (Amazon Inspector; OS and language packages; on push or continuous); switching discards earlier results | confirmed | [ECR image scanning](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanning.html) |
| R9.5.8 | ECR image signing | Managed signing with AWS Signer on push (recommended) or Notation CLI; AWS Signer documents verification on Kubernetes | confirmed | [ECR image signing](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-signing.html), [Signer container workflow](https://docs.aws.amazon.com/signer/latest/developerguide/container-workflow.html) |
| R9.5.9 | Sigstore / Kyverno admission | Sigstore policy-controller: "still actively under development"; Kyverno `verifyImages` supports keyless, but sits under a "ClusterPolicy Deprecated" section in the 1.18 docs | partly | [policy-controller](https://docs.sigstore.dev/policy-controller/overview/), [Kyverno verifyImages](https://release-1-18-0.kyverno.io/docs/policy-types/cluster-policy/verify-images/sigstore/) |
| R9.5.10 | Artifact attestations | "If you are on a GitHub Free, GitHub Pro, or GitHub Team plan, artifact attestations are only available for public repositories" | confirmed | [attest-build-provenance](https://github.com/actions/attest-build-provenance) |
| R9.5.11 | PR size limit | No ruleset limits PR size; push rules (file path, size) exist, page is the Enterprise Cloud version, Team availability not confirmed | confirmed / partly | [available rules](https://docs.github.com/en/enterprise-cloud@latest/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) |

**Impact on F16:** Dependabot alerts (free) plus a CI scanner give the dependency check without a
license; secret push protection and CodeQL need Secret Protection / Code Security, a priced decision
for Papaya. Images: ECR enhanced scanning and ECR managed signing with AWS Signer (GitHub attestations
are not available for private repos on Team). Admission on k0s: tool choice open, both options not
yet stable. PR size: a CI check, no GitHub setting.

---

## R9.6 GCP, Firebase, alert routing, k0s human access (read 2026-11-09; for F13, F15)

Google pages now redirect to `docs.cloud.google.com`; quotes come from a summarising fetcher.

| Row | Question | Answer | Verdict | Source |
|---|---|---|---|---|
| R9.6.1 | GCP Privileged Access Manager | Just-in-time temporary role grants through "entitlements" with optional approval; max duration 7 days (30 min–168 h); events in Cloud Audit Logs; core GA 2024-09-16; multi-level approval is Preview and needs SCC Enterprise/Premium; self-approval and PAM price not found | confirmed / not found | [PAM overview](https://docs.cloud.google.com/iam/docs/pam-overview), [entitlements](https://docs.cloud.google.com/iam/docs/pam-create-entitlements), [release notes](https://docs.cloud.google.com/iam/docs/release-notes) |
| R9.6.2 | IAM Conditions and deny policies | Time-bound bindings with `request.time`; not on basic roles; deny policies at org/folder/project, denial conditions only on resource tags | confirmed | [conditions](https://docs.cloud.google.com/iam/docs/conditions-overview), [deny](https://docs.cloud.google.com/iam/docs/deny-overview) |
| R9.6.3 | Audit logs | Admin Activity always on; "Except for BigQuery, Data Access audit logs are disabled by default"; Vertex AI Data Access logs off unless enabled (`generateContent` is DATA_READ); enabled through `auditConfigs` | confirmed | [audit logs](https://docs.cloud.google.com/logging/docs/audit), [Vertex audit logging](https://docs.cloud.google.com/vertex-ai/docs/general/audit-logging) |
| R9.6.4 | Vertex AI data use and BAA | "Google won't use your data to train or fine-tune any AI/ML models without your prior permission or instruction"; the HIPAA list names "Generative AI on Agent Platform" and "Gemini Enterprise Agent Platform" (product renamed); whether that equals the Gemini API on Vertex AI is not stated | confirmed / partly | [data governance](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/data-governance), [HIPAA](https://docs.cloud.google.com/security/compliance/hipaa) |
| R9.6.5 | Firebase Hosting deploy without a key | `FirebaseExtended/action-hosting-deploy` requires a service-account JSON key; the Firebase CLI recommends Application Default Credentials in CI, and `google-github-actions/auth` (WIF) writes an ADC credential file, but no official page says `firebase deploy` works with WIF | confirmed / not found | [action-hosting-deploy](https://github.com/FirebaseExtended/action-hosting-deploy), [Firebase CLI](https://firebase.google.com/docs/cli), [auth](https://github.com/google-github-actions/auth) |
| R9.6.6 | Firebase Hosting rollback | Release history in the console; rollback "create[s] a new release that serves the same version of content as a previous release"; CLI `firebase hosting:clone`; preview channel URLs are public to anyone with the link | confirmed | [manage hosting](https://firebase.google.com/docs/hosting/manage-hosting-resources), [preview](https://firebase.google.com/docs/hosting/test-preview-deploy) |
| R9.6.7 | AWS alert routing | Amazon Q Developer in chat applications (formerly AWS Chatbot) sends SNS alarm notifications to Slack; SNS HTTPS subscriptions to a paging tool (no private endpoints); **Incident Manager closed to new customers from 2025-11-07** | confirmed | [chat applications](https://docs.aws.amazon.com/chatbot/latest/adminguide/what-is.html), [SNS HTTPS](https://docs.aws.amazon.com/sns/latest/dg/sns-http-https-endpoint-as-subscriber.html), [Incident Manager](https://docs.aws.amazon.com/incident-manager/latest/userguide/incident-manager-availability-change.html) |
| R9.6.8 | GCP alert routing | Cloud Monitoring channels: email, Pub/Sub, webhook, Slack, PagerDuty; Slack, PagerDuty, webhook and mobile "share a single point of failure", so pair with email or Pub/Sub | confirmed | [notification options](https://docs.cloud.google.com/monitoring/support/notification-options) |
| R9.6.9 | k0s human access | OIDC through `spec.api.extraArgs` (`oidc-issuer-url`, …; outside k0s support); `k0s kubeconfig create` makes client certificates valid one year that "cannot be revoked"; docs recommend OIDC | confirmed | [k0s OIDC](https://docs.k0sproject.io/stable/examples/oidc/oidc-cluster-configuration/), [user management](https://docs.k0sproject.io/stable/user-management/) |

**Impact:** F13 — GCP human prod access through PAM entitlements with approval (no standing roles),
Data Access logs turned on for Vertex AI and Cloud Storage holding partner documents, HIPAA coverage
of the renamed product to be confirmed with Google in writing; Firebase deploy through WIF plus
`firebase deploy` is a spike, the action needs a key; k0s humans through OIDC, client certificates
only for break-glass. F15 — no Incident Manager; CloudWatch → SNS → paging tool and Slack, GCP →
paging tool plus email/Pub/Sub backup.

---

## R9.7 Thailand PDPA and Hong Kong PDPO (read 2026-11-09; for F14)

pdpc.or.th, the Royal Gazette PDF of the Act, pcpd.org.hk, elegislation.gov.hk and ia.org.hk could not
be fetched (403 or bot checks). Thai Act text: university-hosted **unofficial** English translation;
transfer notification: official Gazette PDF (Thai) plus unofficial English; breach notification:
machine translation. Hong Kong: Government and Legislative Council papers. Not legal advice.

| Row | Country / question | Answer | Verdict | Source |
|---|---|---|---|---|
| R9.7.1 | TH transfer abroad | s.28: destination with adequate protection, or an exception (consent, contract, vital or public interest, law); s.29: certified BCRs or "appropriate safeguards": own clauses with set content, ASEAN Model Contractual Clauses, EU GDPR SCCs, certification. Cloud storage or transit that no outside person can access "due to technical measures or legal conditions" is not a transfer. No adequacy list found | confirmed (unofficial translation) | [Act](https://cc.kmutt.ac.th/Files/Act%20Eng/personal-data-protection-act-2019-en.pdf) s.28–29; [s.29 notification, Gazette](https://ratchakitcha.soc.go.th/documents/14913.pdf), [English](https://privacy.cmu.ac.th/wp-content/uploads/2025/06/Notification-of-the-Personal-Data-Protection-Committee-Section-29.pdf) |
| R9.7.2 | TH sensitive data | s.26: health, biometric, genetic data etc. need explicit consent unless an exception applies; higher fine tier (s.84, up to THB 5M) | confirmed | Act s.26, s.84 |
| R9.7.3 | TH breach notice | s.37(4): notify the PDPC Office "without delay and, where feasible, within 72 hours after having become aware"; data subjects too if risk is high; late report with justification, at most 15 days (2022 notification, machine translation); processors must tell the controller within 72 hours | confirmed / partly | Act s.37(4); [breach notification](https://clinregs.niaid.nih.gov/sites/default/files/documents/thailand/Reporting%20Personal%20Data%20Breaches_GoogleTranslation.pdf) |
| R9.7.4 | TH processors | s.40: processor acts on instructions, keeps security, reports breaches; controller must have an agreement | confirmed | Act s.40 |
| R9.7.5 | TH residency | No in-country rule in the PDPA; insurance regulator (OIC) cloud rules not found in an official source | partly / not found | Act s.28–29 |
| R9.7.6 | HK transfer abroad | s.33 "has never come into force"; transfers fall under DPP3 (purpose or consent) and DPP2(3)/DPP4(2) (contractual means with processors); PCPD model clauses voluntary | confirmed | [LegCo RO IN02/2024](https://app7.legco.gov.hk/rpdb/en/uploads/2024/IN/IN02_2024_20240126_en.pdf), [LCQ19 2015](https://www.info.gov.hk/gia/general/201504/29/P201504280758_print.htm) |
| R9.7.7 | HK sensitive data | No statutory sensitive-data category | confirmed | IN02/2024 |
| R9.7.8 | HK breach notice | Voluntary: "no statutory requirement for the data user to notify the PCPD or the data subject" (2020); a mandatory scheme still only proposed in October 2025 | confirmed | [LegCo paper 2020](https://www.legco.gov.hk/yr19-20/english/panels/ca/papers/ca20200120cb2-512-3-e.pdf), [LegCo report 2025](https://www.legco.gov.hk/yr2025/english/panels/ca/reports/ca20251022cb2-1907-e.pdf) |
| R9.7.9 | HK processors, residency | Processors not directly regulated; data user binds them by contract; no localisation rule; Insurance Authority outsourcing guideline GL14 not readable (403) | confirmed / not found | LegCo 2020 para 14; LegCo 2025 para 51 |
| R9.7.10 | HK generative AI | In October 2025 the PCPD pointed LegCo to its March 2025 "Checklist on Guidelines for the Use of Generative AI by Employees" (not read) | partly | LegCo 2025 paras 53–57 |

**Impact on F14 (inference, needs Papaya's legal counsel):** pasting Thai claim data into a model
hosted abroad is very likely a transfer under s.28/29, and health data is s.26 sensitive data; the
design's rule of keeping PHI out of agent sessions (ADR-0009) is the cheapest control, plus s.29
safeguards in the provider contract for the non-PHI data the agent may read under a grant. Breach
handling should be written for the strictest regime (Thailand 72 hours) and log the time of awareness;
an agent session or prompt log that received claim data counts as a possible breach. Hong Kong:
DPP3 purpose and processor contracts; follow the PCPD generative-AI checklist. Sector rules of the
insurer partners (OIC, IA GL14) stay open items.

## R9.8 Expo / EAS mobile releases (read 2026-11-09; for F17; docs.expo.dev pages carry no version)

| ID | Topic | Finding | Status | Source |
|---|---|---|---|---|
| R9.8.1 | Channel, branch, build | A binary points to one channel, fixed at build time (`eas.json` build profile); a channel points to a branch. From SDK 54 a release build may switch channel at runtime | confirmed | [deployment](https://docs.expo.dev/eas-update/deployment/) |
| R9.8.2 | Update to prod users | `eas update --channel production`; builds on that channel with a matching runtime version receive it; gradual rollout with `--rollout-percentage`, changed with `eas update:edit` | confirmed | [deployment](https://docs.expo.dev/eas-update/deployment/) |
| R9.8.3 | Rollback, republish | `eas update:republish --destination-channel production` promotes a tested update without a rebuild; `eas update:rollback` (interactive) goes back to an earlier update or to the embedded one; its non-interactive flags not found | confirmed / partly | [rollbacks](https://docs.expo.dev/eas-update/rollbacks/) |
| R9.8.4 | Roles | Owner, Admin, Release Manager, Developer, Runner, Viewer; no custom roles. Developer can build, publish updates and manage credentials unless resources are protected. Per-action matrix not found | partly | [account types](https://docs.expo.dev/accounts/account-types/) |
| R9.8.5 | Protected channels | `eas channel:protect <name>` (EAS CLI >= 24.0.0): only Release Manager, Admin, Owner may publish, republish, roll back, edit the channel or its rollout. Credentials protection limits build/submit/push credentials to the same roles. Moving a project to another account removes protection. No plan requirement stated | confirmed | [protected resources](https://docs.expo.dev/eas/protected-resources/) |
| R9.8.6 | Tokens | Personal tokens inherit the creator's rights unless "Limit access" is set; robot users cannot log in and hold a role; a robot token is limited only by that role; used as `EXPO_TOKEN`; revoked in the dashboard | confirmed | [programmatic access](https://docs.expo.dev/accounts/programmatic-access/) |
| R9.8.7 | OIDC from GitHub | Not mentioned; `expo/expo-github-action` takes a `token` input | not found | same; [expo-github-action](https://github.com/expo/expo-github-action) |
| R9.8.8 | Update code signing | Private key signs the manifest locally (`eas update --private-key-path`); certificate is in the build; the app checks the signature before applying. Production or Enterprise plan. Explicit "rejects unsigned updates" wording not found; KMS-backed signing not documented | confirmed / partly | [code signing](https://docs.expo.dev/eas-update/code-signing/) |
| R9.8.9 | Audit log | Actor, entity, action, time; entities include project, user, permission, credentials, hosting deployment; Enterprise only; `eas account:audit <account> --json`; kept 1.5 years, immutable. Update publish, build and submit not listed as entities | confirmed / partly | [audit logs](https://docs.expo.dev/accounts/audit-logs/) |
| R9.8.10 | GitHub Action | `expo/expo-github-action` inputs `token`, `eas-version`, `packager`, `eas-cache`; examples run `eas update --auto --non-interactive` on push to main | confirmed | [expo-github-action](https://github.com/expo/expo-github-action) |
| R9.8.11 | EAS Workflows | Own `on: push` trigger via Expo's GitHub app; jobs run with at most Developer rights, so they cannot publish to a protected channel | confirmed | [workflows](https://docs.expo.dev/eas/workflows/get-started/), [protected resources](https://docs.expo.dev/eas/protected-resources/) |
| R9.8.12 | Submit, store keys | Non-interactive submit uses keys assigned in EAS (Google service-account key stored on the Expo account) or local key paths in `eas.json`; store-side roles not in these pages | partly | [submit Android](https://docs.expo.dev/submit/android/), [submit iOS](https://docs.expo.dev/submit/ios/) |
| R9.8.13 | Store review, phased rollout | Android submit defaults to the internal track; `releaseStatus: draft` lets a person finish the release in Play Console. Apple/Google roles and phased release not read | partly / not found | [submit Android](https://docs.expo.dev/submit/android/) |
| R9.8.14 | SSO, 2FA | OIDC-based SSO on Production or Enterprise plan; offboarding manual; 2FA per user, no org enforcement documented | partly | [SSO](https://docs.expo.dev/accounts/sso/), [2FA](https://docs.expo.dev/accounts/two-factor/) |

Impact on F17:

- Technical control: protect the `production` channel and credentials; no human holds Release
  Manager or above day to day; CI publishes with a robot user (Release Manager) whose token sits in
  the `production` environment of GitHub, so only a merged `main` run reaches it.
- Limits: no OIDC, so the robot token is a long-lived secret (secrets inventory, rotation); Owner and
  Admin can remove protection; EAS Workflows cannot publish to a protected channel, so prod goes
  through GitHub Actions and Expo's GitHub app is not connected for prod triggers.
- Code signing (paid plan) is the strongest control: a stolen Expo token cannot ship an update
  without the private key. Key in the `production` environment; KMS signing ⚠️ not documented.
- Detection without Enterprise audit log: reconcile updates on the `production` channel against
  deploy runs and merged commits (evidence export).
- Rollback is a protected action: in the incident lane it runs as a reviewed PR/re-run of the
  previous update via `republish`, or by a Release Manager under JIT.
- Store side (App Store / Play review, phased rollout) is a separate gate; roles not verified.

---

## R9.9 Sources added in the verify step (read 2026-11-09; for V7 and V11 of `work/10-verify.md`)

Each page was fetched in this session (HTTP 200) and the quoted terms counted in the page text
(`grep -oF`). Pages without a version are the current docs on that date.

| ID | Topic | Finding | Status | Source |
|---|---|---|---|---|
| R9.9.1 | GitHub default variables | `GITHUB_ENV`, `GITHUB_PATH`, `RUNNER_TEMP` are default variables of every job | confirmed | [variables reference](https://docs.github.com/en/actions/reference/workflows-and-actions/variables) |
| R9.9.2 | Same-repository reusable workflow | "`$/.github/workflows/{filename}` for a reusable workflow in the same repository. This is the recommended syntax"; not available on GHE Server; no `@{ref}` | confirmed | [workflow syntax, `jobs.<job_id>.uses`](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) |
| R9.9.3 | Structured authentication file | `apiVersion: apiserver.config.k8s.io/v1`, `kind: AuthenticationConfiguration`; JWT issuers with `issuer.audiences`, `claimValidationRules[].expression` (CEL), `claimMappings` | confirmed | [Kubernetes authentication](https://kubernetes.io/docs/reference/access-authn-authz/authentication/) |
| R9.9.4 | Audit policy and log flags | "The first matching rule sets the audit level of the event"; `omitStages: ["RequestReceived"]` in the example policy; `--audit-log-maxage` "the maximum number of days to retain old audit log files" | confirmed | [Kubernetes auditing](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/) |
| R9.9.5 | RBAC and token mounting | `RoleBinding` with `roleRef` and rules with `apiGroups`; `automountServiceAccountToken: false` on a ServiceAccount or Pod | confirmed | [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/), [service accounts](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/) |
| R9.9.6 | Pulumi CLI | `pulumi preview` and `pulumi up` take `--stack`; environment variables `PULUMI_BACKEND_URL`, `PULUMI_CONFIG_PASSPHRASE`, `PULUMI_ACCESS_TOKEN` | confirmed | [pulumi preview](https://www.pulumi.com/docs/iac/cli/commands/pulumi_preview/), [pulumi up](https://www.pulumi.com/docs/iac/cli/commands/pulumi_up/), [environment variables](https://www.pulumi.com/docs/iac/cli/environment-variables/) |
| R9.9.7 | Serverless Framework CLI | `serverless deploy --stage` documented. The CI credential is `SERVERLESS_LICENSE_KEY` ("Set the `SERVERLESS_LICENSE_KEY` environment variable in your environment or CI/CD pipeline"). `SERVERLESS_ACCESS_KEY` not found on the deploy, license-keys or getting-started pages | partly | [deploy](https://www.serverless.com/framework/docs/providers/aws/cli-reference/deploy), [license keys](https://www.serverless.com/framework/docs/guides/license-keys) |
| R9.9.8 | Cloud Storage permission | `storage.objects.get` is the object read permission | confirmed | [Cloud Storage IAM permissions](https://cloud.google.com/storage/docs/access-control/iam-permissions) |
| R9.9.9 | Firebase CLI in CI | Application Default Credentials preferred; "(Legacy) Use `FIREBASE_TOKEN` … This is less secure" | confirmed | [Firebase CLI reference](https://firebase.google.com/docs/cli) |
| R9.9.10 | npm configuration | Environment variables starting with `npm_config_` set configuration; per-user config file "configurable via CLI option `--userconfig` or environment variable `$NPM_CONFIG_USERCONFIG`" | confirmed | [npm v11 config](https://docs.npmjs.com/cli/v11/using-npm/config) |
| R9.9.11 | Identity Center `CreateAccountAssignment` | The actions table lists, for `CreateAccountAssignment` and `DeleteAccountAssignment`: `Account*`; `Instance*` with `aws:ResourceTag/${TagKey}`, `sso:PrimaryRegion`; `PermissionSet*` with `aws:ResourceTag/${TagKey}`, `sso:PrimaryRegion`. ARN formats: `arn:${Partition}:sso:::account/${AccountId}`, `…:instance/${InstanceId}`, `…:permissionSet/${InstanceId}/${PermissionSetId}`. The machine-readable `sso.json` omits the per-action tag key (it lists only `sso:PrimaryRegion` there, and no `aws:ResourceTag` on any action-resource entry; `ecs.json` does list them), so the HTML page is the source. The tagging guide says tags in IAM policies can control access to permission sets | confirmed | [Service Authorization Reference, IAM Identity Center](https://docs.aws.amazon.com/service-authorization/latest/reference/list_iam-identity-center.html#list_iam-identity-center-action-CreateAccountAssignment), [tagging](https://docs.aws.amazon.com/singlesignon/latest/userguide/tagging.html); `sso.json` as above |
| R9.9.12 | IAM condition keys used in examples | `ecs:cluster` is an action condition key of `ecs:RunTask`; `iam:PassedToService` of `iam:PassRole`; `iam:PermissionsBoundary` has type `ARN` | confirmed | [`ecs.json`](https://servicereference.us-east-1.amazonaws.com/v1/ecs/ecs.json), [`iam.json`](https://servicereference.us-east-1.amazonaws.com/v1/iam/iam.json) |

Impact on the deliverable (applied 2026-11-09):

- V11: markers added where these terms are used (`examples/README.md`, `docs/01-framework.md`,
  `docs/07-framework-appendix.md`, `examples/k0s/*.yaml`,
  `examples/github/environment-production/secrets.md`). `SERVERLESS_ACCESS_KEY` stays ⚠️ and
  `SERVERLESS_LICENSE_KEY` (R9.9.7) was added to the phase-2 env denylist, its test and README (owner decision). `ecs:cluster` in E15
  (R9.9.12) and the `$/` syntax in examples finding 8 (R9.9.2) now cite these rows.
- V7: the verify step first read only `sso.json` and marked the tag condition as unconfirmed; the
  HTML reference lists `aws:ResourceTag` for the `PermissionSet` resource of
  `CreateAccountAssignment` (R9.9.11), so it is 📖. E16, layer 7 and rollout 1.13 cite it; a
  drill grant in a sandbox account remains the acceptance test (documentation is not behaviour).
  The IAM policy simulator cannot answer this question: the user supplies the values of other
  condition keys, and it "does not determine which services support a given global condition
  key" ([testing policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_testing-policies.html)).
