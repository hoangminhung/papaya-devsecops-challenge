# Rollout plan: 45 / 75 / 100 days

> Status: moved out of framework layer 8 on 2026-11-09 and expanded. The items, their order and the
> phase-1 subset were approved with the framework (OD4, OD7, OD21); the allowlist became two repo
> scripts after examples finding 19. Added here and approved by the author (owner of this submission, not Papaya) on
> 2026-11-09 ("done when" checks stay [design]): the owner and "done when" of each item, the "measured from" column, item 2.9 (from OD15,
> OD20), the run-log export in 2.4 (from layer 3, G7) and the S4 risk (framing §5). After the
> independent review, the owner approved fixes that add or change items (from OD22: 1.6, 1.12, 1.15, 1.17,
> 1.18, 1.19–1.23, 1.11, 2.2, 2.4, 2.9, 2.10; from OD31: 1.6, 1.8, 1.11, 1.13, 1.16, 2.8, 2.11–2.13,
> S4 and the effort estimate) · Updated:
> 2026-11-09 · Builds on [`01-framework.md`](01-framework.md)

## How to read this

The rollout takes about 100 days (re-baselined from the 90 of GĐ-12 after the effort estimate, OD49). Effort is estimated roughly in
[Load and risks](#load-and-risks) (⚠️ no Papaya data): the 23 phase-1 items do not fit 30 days with
1–2 people, so that section names the minimum safe phase 1 and the headcount it needs (OD35), and
phase 1 now runs 45 days; the items that do not fit move into the first weeks of phase 2. Markers and codes are those of the
[framework](01-framework.md#how-to-read-this). "Done when" is the check that closes an item
[design]; examples `E1`–`E19` (with E3b, E4b, E9b) are the expected configuration in [`examples/`](../examples/README.md).

**Owners** (framework layer 8): **DS** DevSecOps (1–2 people, GĐ-1) · **PL** a platform team or the
named engineers who own deploy workflows (whether Papaya has a platform team is unknown ⚠️) ·
**CO** Compliance · **EL** engineering leads · **EM** engineering management.

**Order.** Framing Q8 ranked the first 30 days: (1) remove long-lived CI credentials, (2) narrow
standing prod access, (3) the MCP/plugin catalogue; the on-call approver list comes before or with (2).
One rule from layer 8 shapes the whole plan: **access is never removed before its replacement works.**

## Phase 1 — days 0–45: the pull request becomes the default prod write path

| # | Item | Owner | Done when | Layer |
|---|---|---|---|---|
| 1.1 | Measure the incident PR lane on one service. First task once that service has an OIDC deploy workflow (Options §9). Include the prompt for each `aws` read, which the allowlist does not cover. The minimal version (one drill, decision to apply, on one service) is a hard prerequisite of 1.16 (OD53); measuring more services may follow in phase 2 | DS, PL | Decision-to-apply time measured; the target is ≤ 30 min. If the drill exceeds it, the slow step is fixed before 1.16 | 3, 7 |
| 1.2 | Scan non-prod for real data | DS, CO | First scan result recorded (S11) | 6 |
| 1.3 | OIDC for deploy workflows; remove long-lived keys, except k0s/Firebase under OD1 | PL | No AWS access key used by a workflow (S2, with the OD1 caveat); E4 trust policy applied | 1, 5 |
| 1.4 | Move laptop deploys to CI (GĐ-10, unconfirmed) | PL | No laptop deploy in CloudTrail since the move | 1 |
| 1.5 | Rulesets, CODEOWNERS and the CODEOWNERS validation check | DS; EL decide CODEOWNERS content | E1, E2 and `codeowners-validate` live on `main`; a test PR shows whether "Update branch" keeps approvals (OD31). The ruleset requires only checks that exist (OD53): `approval-gate`, `codeowners-validate`, and `data-fix-scan` with 1.23; each S10 check of 1.8 and `agent-eval` (OD45) joins the required list the day it runs on every PR, so no merge waits for a check that never reports | 3, 5 |
| 1.6 | The approval-gate app (decision logic E12): human approvals only, kept across a branch update that leaves the diff unchanged (OD31), two L3 owner team members on process paths (OD26), on-call approvals for another team only with an open incident and on shift (OD27), flagged approvals in the monthly report. Live before or with 1.5, whose ruleset requires its check (G19). Rolled out in two steps (OD49): two weeks report-only, where the app posts its result but the ruleset does not yet require it and every failure it would have caused is reviewed; then required. Availability target: 99.5 % of working hours, and an alert when it has not answered a PR event within 5 minutes [design]; if it is down longer than an hour, the controlled removal of the required check (layer 3: two L3 approvals, alerted, time-boxed) is the tested fallback | DS | App is the required source of the `approval-gate` check; a test PR shows each rule; the report-only fortnight reviewed; the removal runbook drilled once | 3 |
| 1.7 | Remove human write kubeconfigs for prod k0s (interim) | PL | No human holds a prod k0s write kubeconfig | 1 |
| 1.8 | S10 checks (OD39): `dependency-check` (Dependabot plus a lockfile scanner), `secret-scan` and `sast` (GitHub Secret Protection and Code Security if Papaya buys them, else open-source scanners), `iac-scan` (Trivy), `workflow-lint`, `pr-size`. Access Analyzer and policy packs follow in phase 2, so until then OD8 relies on the risk stop alone | DS | Required checks on every PR to `main` (S10) | 5 |
| 1.9 | Minimal real-data read flow: request, 1-hour data-read role, approver ≠ requester, data-owner review afterwards | DS, CO | One request handled end to end | 6 |
| 1.10 | `ProdReadMetadata` becomes the only standing prod role. Existing broad read roles go only once 1.9 works | DS | E6 assigned; broad read roles removed | 1 |
| 1.11 | Start moving secrets to runtime resolution and redacting logs at source, service by service. A log group opens to `ProdReadMetadata` only after its masking policy is set (E14) and the SAST rule against logging whole events passes for that service (OD28) | PL, service owners | First services done, each with masking and the SAST rule; list of the rest with dates: every claims service by the end of phase 2 (day 75), the rest by day 100 (OD34; ⚠️ estimate) | 1, 6 |
| 1.12 | On-call approver schedule and a minimal incident-responder schedule, named, 24/7. On-call approvers only approve (OD7). The approver schedule is the file `oncall/schedule.yaml` (an L3 path) that the approval-gate app reads; incidents are Linear issues (OD27) | EM | Both schedules published with primary and backup (S7); the app reads the file | 3, 7 |
| 1.13 | Minimal JIT fallback: the Linear request template (scope as a `jit-scope` label, the incident as an issue relation) and a receiver that grants only after its pre-grant check, once per request, with the scoped role of E16 (OD33, OD41); before building it, a real webhook payload is captured and the AWS TEAM sample is compared, **with** a CloudTrail comparison per grant and a drift check of the stacks it touched. By hand until automated: a temporary deviation from D2, which asks for a drift job. No immediate stop yet: deleting the assignment ends new sessions only, so a grant can run up to about 2 h (⚠️ R2.9 #3) | DS | One drill grant reconciled. The revocation Deny SCP follows in phase 2 (2.2) | 7 |
| 1.14 | Risk stop in the deploy job (E7). The policy-finding trigger works from phase 2 | PL, DS | Every prod deploy job runs it | 3 |
| 1.15 | k0s/Firebase deploy credentials moved to secrets of the `production-k0s` environment (OD24); the k0s credential becomes the namespaced, time-limited ServiceAccount token, and the Kubernetes API audit log is on (E11) | PL | No repository secret holds them (E3b); the old admin kubeconfig is revoked; an audit event of a test deploy is found | 1, 5, 7 |
| 1.16 | **Then** remove standing prod write, including Expo roles above Developer for people and the protection of the `production` EAS channel and credentials (OD40) | DS | S1 = 0 | 1 |
| 1.17 | MCP/plugin catalogue v1 (E9): marketplace repository with its rulesets (two approvals, protected release tags, E9b), every plugin pinned by `sha`, local MCP servers as image digests (OD26) | DS | Marketplace live with rulesets; first release tag; first review records | 4 |
| 1.18 | Managed settings, phase-1 subset (E8): `defaultMode` (D1 said "immediately"); `disableBypassPermissionsMode`; `ask` for `aws`, `pulumi`, `serverless` until standing write is gone and after (OD43); `enabledPlugins` for the internal plugin (OD47); the keys that enforce the catalogue (`strictKnownMarketplaces` pinned to a release tag, `extraKnownMarketplaces` with auto-update off (OD26), `blockedMarketplaces`, `disableSideloadFlags`, `allowedMcpServers` + `allowManagedMcpServersOnly`, `disableClaudeAiConnectors`); the OTel exporter with content flags `0`, which is the evidence for D1's auto-mode metric and the plugin events of layer 4; `requiredMinimumVersion`; the `permissions.allow` list of two repo scripts (OD7b; finding 19 of the examples); a `Read(~/.aws/**)` deny rule and `autoMode.classifyAllShell: true` (OD21); deny rules for the `gh` token file, `gh pr review` and `gh api …reviews…` (OD25) | DS | Settings live; monthly export matches git | 2, 8 |
| 1.19 | Deploy-job isolation (OD22): environments `production`, `production-iam` and `production-db` (ADR-0011) with their own OIDC subjects and roles; domain deploy roles bounded to `svc-*` roles with the permissions boundary; install scripts off in deploy and preview jobs, with the allowlist in `tools/ci/`; agent review on PRs touching infrastructure code | PL, DS | E3, E4, E4b live; a test PR's install script does not run in CI | 1, 5 |
| 1.20 | Administrators of the administrators (OD23), phase-1 part: name the management-account group (≥ 2 L3 owners, hardware MFA); remove member-account root credentials through centralized root access (📖 R9.2.5); list where `OrganizationAccountAccessRole` exists | DS | Group recorded in C-03; root credentials absent in prod accounts; inventory done | 1 |
| 1.21 | GitHub identity (OD25): organization requires 2FA (⚠️ check the setting on Team), login register from HR joiners and leavers, outside collaborators without write, classic tokens restricted, fine-grained tokens approved with a maximum lifetime | DS, CO | Register covers every member; 2FA required; token policy set | 1, 3 |
| 1.22 | Evidence store (OD30): evidence bucket with Object Lock (compliance, 6 years) in the log-archive account; nightly export workflow (E13); Actions retention set to 400 days; monthly UI export of the org audit log; Linear template for JIT and data-read requests with its webhook mirror | DS, CO | First night's export in the bucket; first audit-log export; one JIT drill request recorded | 7 |
| 1.23 | Database changes (OD29, ADR-0011): `tools/db/` wrappers for the migration tool in use, the `db-change` ECS task inside the prod VPC with its image, task role (IAM database authentication) and the GraphQL-engine admin secret in Secrets Manager, the CI role that may only start that task (E15), the `sql` deploy job, a `data-owners-<tenant>` team per tenant, with read access to the repository, read by the approval-gate app (not code owners, so no write access) | PL, DS; data owners | One migration and one drill data fix applied through the job | 3, 6 |

**Version floor for item 1.18:** the higher of 2.1.248 (needed by `--restricted`, D3, and above the
2.1.179 plugin-pin fix) and the latest fixed high advisory at rollout. Phase 2 raises it to 2.1.310
(`allowedProviders` needs 2.1.285; monitor blocking under `allowManagedHooksOnly` needs 2.1.310;
📖 settings reference, see the E8 row of [`examples/README.md`](../examples/README.md)).

### Hard prerequisites before standing prod write is removed (item 1.16)

1. OIDC deploys from CI (1.3).
2. Rulesets + CODEOWNERS (1.5).
3. The on-call approver and responder schedules (1.12), and the approval-gate app that reads them (1.6), past its report-only fortnight and required by the ruleset (OD49).
4. Minimal JIT (1.13).
5. The risk stop (1.14).
6. The k0s/Firebase secret move (1.15): a repository secret would be standing prod write (layer 5).
7. The database change path (1.23): without it, removing standing write leaves migrations and data fixes no legitimate path (ADR-0011).
8. No human write kubeconfig for prod k0s (1.7): S1 counts k0s too, and a write kubeconfig is standing prod write (OD42).
9. Laptop deploys moved to CI (1.4, OD53): without it, removing standing write leaves the services still deployed from laptops (GĐ-10, unconfirmed) without a path.
10. The incident PR lane measured once (minimal 1.1, OD53): direct access goes only once the replacement's real time is known.

If one of these slips, standing prod write stays until it lands, and the slip is reported. Likewise,
broad read roles stay until the minimal real-data read flow (1.9) works.

### What may slip, and what may not

- **May slip to phase 2** without blocking 1.16: catalogue v1 (1.17), together with the
  managed-settings keys that enforce it; log redaction and secret moves beyond the first services.
  Catalogue v1 slipping is a deviation from framing Q8, which ranked it third for the first 30
  days, and needs owner agreement.
- **May not slip:** `defaultMode`, the allowlist (D1 "immediately", OD7b), the OD21 keys, the OD25 deny rules, the OD43 `ask` rules for cloud CLIs, and the
  OTel exporter (the evidence for D1).

## Phase 2 — days 45–75: guardrails that need phase 1 in place

| # | Item | Owner | Layer |
|---|---|---|---|
| 2.1 | Rest of the managed baseline (E8 phase 2) and verification of the SSM option (both moved here by the owner, OD4). First one pilot team for about two weeks, with S4 measured (prompts per session, time to open a PR) and a narrow push-and-PR credential for the agent evaluated; the rest of Papaya only when S4 holds for the pilot (OD50). Server-managed settings have no per-group targeting (📖 R1.1.6), so the pilot's phase-2 keys come as an endpoint file on its laptops, composed with the org settings through `managedSourcesBehavior: "merge"` (📖 R1.1.4); which source must carry that key and how the merged sandbox keys behave is checked in the pilot (⚠️) | DS | 2, 7 |
| 2.2 | SCPs: data-plane deny, Lambda update deny, revocation Deny, deny of trail changes in prod accounts, protection of the boundary policy (OD22), deny of `OrganizationAccountAccessRole` in the prod OU (OD23) (E5); outside-org write deny on every OU (not in E5) | DS | 1, 7 |
| 2.3 | Scheduled drift detection; automated JIT reconciliation | DS, PL | 7 |
| 2.4 | Change records linking the exported evidence (1.22), automated monthly reconciliation of prod changes with approvals (S3), alerts on audit-log events | DS, CO | 3, 7 |
| 2.5 | Access Analyzer and policy-pack checks (E10); the risk stop's policy-finding trigger starts working | DS | 3, 5 |
| 2.6 | Aurora activity streams | PL | 6, 7 |
| 2.7 | Emergency federation for Identity Center outages | DS | 7 |
| 2.8 | Alert routing (OD38): paging tool chosen and fed by SNS and GCP alert policies, Slack through Amazon Q Developer, GCP email or Pub/Sub backup, severities and escalation per service, incident issue opened from the page (G5 for the product) | EM, DS | 7 |
| 2.9 | Separate preview role and split of the deploy job (OD15); the per-environment roles of OD20 moved to phase 1 (1.19, OD22) | PL, DS | 3, 5 |
| 2.10 | Identity Center permission sets and assignments as code in `infra/pulumi/identity-center/` (L3 owner team only), alerts on Identity Center changes by any other principal (OD23, 📖 R9.2.2) | DS | 1, 7 |
| 2.11 | Images (OD39): ECR enhanced scanning and managed signing with AWS Signer; images referenced by digest. Done when: every prod image scanned on push and signed; no tag references in prod stacks | PL, DS | 5 |
| 2.12 | Mobile (OD40): EAS Update code signing (paid Expo plan), the CI robot as the only Release Manager, the nightly comparison of `production` channel updates with deploy runs; test that the app rejects an unsigned update. Done when: a test update without a run raises an alert; an unsigned update is rejected on a test device | PL, DS | 5, 7 |
| 2.13 | Prod access on GCP, Firebase and k0s (OD36): PAM entitlements, Data Access logs for Vertex AI and partner-document buckets, WIF narrowed to the `production` subject, the Firebase WIF spike, k0s OIDC for people. Done when: no standing GCP prod role for people; spike result recorded; one sealed k0s break-glass certificate | DS, PL | 1, 7 |
| 2.14 | Isolated agent runtime, evaluated with the pilot of 2.1 (OD58, framework layer 2): a development box with its own AWS role and a per-session GitHub App token; compared with OD50's narrow credential on S4, P1a and cost. Done when: the pilot team used it for two weeks; result and recommendation recorded for the final review (3.5) | DS, PL | 1, 2 |

## Phase 3 — days 75–100: test, measure, review

| # | Item | Owner | Layer |
|---|---|---|---|
| 3.1 | Planted-injection test on the real configuration (📖 R6.1.1, R6.1.5; ⚠️ R6.5 #12). A deliberate trade-off: auto mode runs from day 1 (D1) without this data; until the test, only D1's other fallback triggers apply | DS | 2, 8 |
| 3.2 | Auto-mode non-prod environment (D1 c) | DS, PL | 2 |
| 3.3 | Separate OS user or container for prod-reading sessions | DS | 2 |
| 3.4 | First ISO evidence pack ([compliance register](04-compliance-mapping.md)) | CO | 8 |
| 3.5 | 90-day review of D1–D3 | DS, CO, EL | 8 |

## Metrics by phase

S1–S11 are the success criteria of framing §5, unchanged; targets were confirmed by the owner.

| # | Criterion | Target | Measured from |
|---|---|---|---|
| S1 | No long-lived prod write credential on laptops; no standing prod write for people | 0 | Phase 1, after 1.16 |
| S2 | No long-lived cloud credential in GitHub secrets | 0 (k0s/Firebase excepted, OD1; Expo, OD40) | Phase 1, after 1.3 |
| S3 | Every prod change approved by a named person other than the author, **before** it is applied | 0 unmatched / 0 late | Phase 2 (2.4); by hand before that |
| S4 | Engineers keep their speed: PR to prod the same working day; approval wait ≤ 1 h in working hours; in the non-prod loop, only the phase-2 steps of OD34 (push and PR at the `!` prompt, a confirmation per cloud CLI call), with prompts per session and PR-opening time measured | as stated | Phase 1 (phase-2 steps from the first phase-2 team) |
| S5 | Every laptop gets the organisation's Claude Code policy; no one can turn off all prompts unnoticed. **Met only on laptops with MDM (OD54):** without it, another login, an API key or a `CLAUDE_CODE_USE_*` variable skips server-managed settings (📖 R1.1.7), so on those laptops S5 is reported as not met, and what is measured instead is the share of sessions whose OTel data shows the managed policy | 100 % / 0 on MDM laptops; not met without MDM (layer 2) | Phase 1 (1.18) |
| S6 | No MCP server or plugin outside the catalogue; new requests decided in ≤ 5 working days | 0 / ≤ 5 days | When 1.17 lands |
| S7 | Named on-call including approvers; all prod alerts in one channel; incident approval wait ≤ 15 min, 24/7 | as stated | Schedules: phase 1; alert routing: phase 2 |
| S8 | Evidence for a random prod change shown in ≤ 30 min without asking anyone | ≤ 30 min | Records kept from phase 1 (1.22); linked lookup from phase 2 (2.4); first full pack in 3.4 |
| S9 | No real-data read on prod without an approved request | 0 | When 1.9 lands: phase 1, or early phase 2 in the minimum variant (Load and risks) |
| S10 | 100 % of PRs to `main` pass secret scan, dependency check and SAST; 0 direct pushes; 0 secrets found after merge | 100 % / 0 / 0 | When 1.8 lands: phase 1, or early phase 2 in the minimum variant |
| S11 | No real data in non-prod | 0 | When 1.2 lands: phase 1, or early phase 2 in the minimum variant |

The framework adds two metric sets: the prompt metrics of [layer 2](01-framework.md#layer-2--agent-runtime-controls)
(OTel `permission_mode` and time blocked on the user; thresholds ⚠️) and the JIT metrics of
[layer 7](01-framework.md#layer-7--observability-audit-incident-response-and-break-glass) (JIT used
where a PR was possible, writes outside the command list, late codify PRs, grants per month; starting
thresholds ⚠️). A breach of a JIT metric leads to a faster PR lane or a runbook, never a wider JIT.

## Load and risks

- **Phase-1 load (OD35) [design; every number ⚠️ an estimate by the author, not measured, assuming
  about 10 deployable services and an engineer who knows the tools].** Phase 1 holds 23 items
  (1.19–1.23 added after the review) for 1–2 DevSecOps people (GĐ-1) plus the owners of deploy
  workflows. In person-days (pd):

  | Items | Estimate | Note |
  |---|---|---|
  | 1.6 approval-gate app | 10–15 pd | The largest item: GitHub App, hosting in the tooling account, webhooks, reading CODEOWNERS and teams; decision logic exists (E12). No off-the-shelf app with these rules was found (⚠️ not searched exhaustively) |
  | 1.23 database path | 6–10 pd | Depends on Papaya's migration tool (unknown) |
  | 1.13 JIT, 1.14 risk stop | 5–8 pd each | 1.14: adapters checked against real `--json` output first (E7 is ⚠️ on field names). 1.13: the AWS TEAM sample instead of the receiver, if its approval rules meet OD33 (⚠️ not checked) |
  | 1.3, 1.4, 1.19 OIDC, CI deploys, job isolation | 12–18 pd together | Roughly half a day per deploy workflow plus the two environments and roles |
  | 1.22 evidence store, 1.17 catalogue, 1.9 data-read flow | 3–5 pd each | |
  | the other 12 items | 1–4 pd each, 25–35 pd together | Settings, schedules, scans, register, first masking |
  | **Total** | **≈ 75–110 pd** | One person has about 20 working days in 30 calendar days |

  **Minimum headcount:** about 4 people full time for 30 days, which Papaya does not have (GĐ-1).
  **Critical path:** 1.6 → 1.5 (the ruleset requires the app's check) → 1.16, about three weeks
  for the app alone; in parallel 1.3 → 1.19 → 1.14 → 1.23 → 1.16. **Minimum safe phase 1** (what
  removing standing prod write needs, plus the items that may not slip): minimal 1.1, 1.3, 1.4, 1.5,
  1.6, 1.7, 1.12, 1.13, 1.14, 1.15, 1.16, 1.18 (may-not-slip keys), 1.19, 1.21, 1.22, 1.23: about
  62–90 pd, i.e. **2 DevSecOps people plus one platform engineer for about 45 days**, or 1–2 people
  for about 65 days (OD53 added 1.4 and the minimal 1.1, ⚠️ +5–7 pd). The other items (1.2,
  1.8–1.11, 1.17, 1.20) move into the first weeks of phase 2 in that order; until 1.8 lands, the
  S10 checks are not required (1.5) and PRs carry only the approval-gate and data-fix checks; broad read roles stay until 1.9 and 1.10 land. Until 1.20 lands,
  `OrganizationAccountAccessRole` remains a standing admin path from the management account, so
  S1 is reported as "0 except the management account's named group" in that window. Which variant (more people or more
  days) is a decision for Papaya's management.
- **Steady-state run cost (OD57) [design; every number ⚠️ an estimate].** The custom parts need an
  owner after they ship. Per year, in person-days:

  | Component | Run effort | What it is |
  |---|---|---|
  | Approval-gate app (E12) | 15–25 pd | Dependency and GitHub API updates, rule changes, its alerts (answered by the DevSecOps owner in working hours; out of hours it fails closed and the JIT path applies), flagged-approval triage |
  | Risk stop and SQL classifier (E7) | 8–15 pd | Following Pulumi and Serverless output changes, false-positive handling |
  | JIT receiver (E16), Linear mirror, evidence export (E13) | 7–14 pd | Payload changes, failed nights re-run |
  | Reconciliation jobs, settings comparison, monthly report | 15–20 pd | About a day a month plus fixes |
  | Catalogue reviews, managed settings, `data-fix-scan` | 15–30 pd | Depends on request volume (S6) |
  | **Total** | **≈ 60–105 pd a year** | About a third to a half of one DevSecOps person |

  GitHub Enterprise Cloud removes part of the reconciliation and register work (framework layer 3,
  "GitHub plan"). The 24/7 approver and responder rotas are sized by Papaya's engineering
  management (OD51) and are not in this table.
- **Lean first version, a decision for Papaya (OD57).** If the headcount above is not available,
  phase 1 can ship the degraded mode below on purpose instead of the approval-gate app: about
  10–15 pd less in phase 1 and about 15–25 pd a year less to run, at the price of R2–R4 being
  detected the next morning instead of blocked. It needs Compliance's written acceptance with an
  end date, as below; the app follows in phase 2.
- **If the approval-gate app is late (degraded mode).** The ruleset ships without the
  `approval-gate` check; GitHub still enforces code-owner review, no self-approval and approval
  after the last push (layer 3). Rules R2–R4 (on-call only in an incident, two L3 approvers, the
  data owner) are then checked every night by running E12 over the exported reviews (E13) and
  reported: detective, not preventive. Standing prod write (1.16) is removed in this mode only if
  Compliance accepts that interim in writing, with an end date.
- **Engineering speed (S4).** If S1–S3 are met but S4 is not, engineers will find a way around the
  controls (framing §5, P3b), and S1–S3 will not hold. S4 is measured from phase 1 and reviewed with
  the security metrics, not after them.
- **Exceptions:** a ticket with owner, reason and expiry (layer 8).
