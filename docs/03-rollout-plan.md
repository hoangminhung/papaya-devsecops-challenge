# Rollout plan: 30 / 60 / 90 days

> Status: moved out of framework layer 8 on 2026-11-09 and expanded. The items, their order and the
> phase-1 subset were approved with the framework (OD4, OD7, OD21); the allowlist became two repo
> scripts after examples finding 19. Added here, for owner review
> [design]: the owner and "done when" of each item, the "measured from" column, item 2.9 (from OD15,
> OD20), the run-log export in 2.4 (from layer 3, G7) and the S4 risk (framing §5) · Updated:
> 2026-11-09 · Builds on [`01-framework.md`](01-framework.md)

## How to read this

The rollout takes about 90 days (GĐ-12, unconfirmed). Effort is not estimated (⚠️): the main risk is
the phase-1 load (see [Load and risks](#load-and-risks)). Markers and codes are those of the
[framework](01-framework.md#how-to-read-this). "Done when" is the check that closes an item
[design]; examples `E1`–`E10` are the expected configuration in [`examples/`](../examples/README.md).

**Owners** (framework layer 8): **DS** DevSecOps (1–2 people, GĐ-1) · **PL** a platform team or the
named engineers who own deploy workflows (whether Papaya has a platform team is unknown ⚠️) ·
**CO** Compliance · **EL** engineering leads · **EM** engineering management.

**Order.** Framing Q8 ranked the first 30 days: (1) remove long-lived CI credentials, (2) narrow
standing prod access, (3) the MCP/plugin catalogue; the on-call approver list comes before or with (2).
One rule from layer 8 shapes the whole plan: **access is never removed before its replacement works.**

## Phase 1 — days 0–30: the pull request becomes the default prod write path

| # | Item | Owner | Done when | Layer |
|---|---|---|---|---|
| 1.1 | Measure the incident PR lane on one service. First task once that service has an OIDC deploy workflow (Options §9). Include the prompt for each `aws` read, which the allowlist does not cover | DS, PL | Decision-to-apply time measured; the target is ≤ 30 min | 3, 7 |
| 1.2 | Scan non-prod for real data | DS, CO | First scan result recorded (S11) | 6 |
| 1.3 | OIDC for deploy workflows; remove long-lived keys, except k0s/Firebase under OD1 | PL | No AWS access key used by a workflow (S2, with the OD1 caveat); E4 trust policy applied | 1, 5 |
| 1.4 | Move laptop deploys to CI (GĐ-10, unconfirmed) | PL | No laptop deploy in CloudTrail since the move | 1 |
| 1.5 | Rulesets, CODEOWNERS and the CODEOWNERS validation check | DS; EL decide CODEOWNERS content | E1, E2 and `codeowners-validate` live on `main` | 3, 5 |
| 1.6 | The required-check app, before any agent workflow may open PRs (G19) | DS | App is the required source of the `approval-gate` check | 3 |
| 1.7 | Remove human write kubeconfigs for prod k0s (interim) | PL | No human holds a prod k0s write kubeconfig | 1 |
| 1.8 | S10 checks: secret scanning, dependency check, SAST. Access Analyzer and policy packs follow in phase 2, so until then OD8 relies on the risk stop alone | DS | Required checks on every PR to `main` (S10) | 5 |
| 1.9 | Minimal real-data read flow: request, 1-hour data-read role, approver ≠ requester, data-owner review afterwards | DS, CO | One request handled end to end | 6 |
| 1.10 | `ProdReadMetadata` becomes the only standing prod role. Existing broad read roles go only once 1.9 works | DS | E6 assigned; broad read roles removed | 1 |
| 1.11 | Start moving secrets to runtime resolution and redacting logs at source, service by service | PL, service owners | First services done; list of the rest | 1, 6 |
| 1.12 | On-call approver schedule and a minimal incident-responder schedule, named, 24/7. On-call approvers only approve (OD7) | EM | Both schedules published with primary and backup (S7) | 3, 7 |
| 1.13 | Minimal JIT fallback **with** a CloudTrail comparison per grant and a drift check of the stacks it touched. By hand until automated: a temporary deviation from D2, which asks for a drift job. No immediate stop yet: deleting the assignment ends new sessions only, so a grant can run up to about 2 h (⚠️ R2.9 #3) | DS | One drill grant reconciled. The revocation Deny SCP follows in phase 2 (2.2) | 7 |
| 1.14 | Risk stop in the deploy job (E7). The policy-finding trigger works from phase 2 | PL, DS | Every prod deploy job runs it | 3 |
| 1.15 | k0s/Firebase deploy credentials moved to `production` environment secrets | PL | No repository secret holds them (E3b) | 5 |
| 1.16 | **Then** remove standing prod write | DS | S1 = 0 | 1 |
| 1.17 | MCP/plugin catalogue v1 (E9) | DS | Marketplace live; first review records | 4 |
| 1.18 | Managed settings, phase-1 subset (E8): `defaultMode` (D1 said "immediately"); `disableBypassPermissionsMode`; the keys that enforce the catalogue (`strictKnownMarketplaces`, `blockedMarketplaces`, `disableSideloadFlags`, `allowedMcpServers` + `allowManagedMcpServersOnly`, `disableClaudeAiConnectors`); the OTel exporter with content flags `0`, which is the evidence for D1's auto-mode metric and the plugin events of layer 4; `requiredMinimumVersion`; the `permissions.allow` list of two repo scripts (OD7b; finding 19 of the examples); a `Read(~/.aws/**)` deny rule and `autoMode.classifyAllShell: true` (OD21) | DS | Settings live; monthly export matches git | 2, 8 |

**Version floor for item 1.18:** the higher of 2.1.248 (needed by `--restricted`, D3, and above the
2.1.179 plugin-pin fix) and the latest fixed high advisory at rollout. Phase 2 raises it to 2.1.310
(`allowedProviders` needs 2.1.285; monitor blocking under `allowManagedHooksOnly` needs 2.1.310;
📖 settings reference, see the E8 row of [`examples/README.md`](../examples/README.md)).

### Hard prerequisites before standing prod write is removed (item 1.16)

1. OIDC deploys from CI (1.3).
2. Rulesets + CODEOWNERS (1.5).
3. The on-call approver and responder schedules (1.12).
4. Minimal JIT (1.13).
5. The risk stop (1.14).
6. The k0s/Firebase secret move (1.15): a repository secret would be standing prod write (layer 5).

If one of these slips, standing prod write stays until it lands, and the slip is reported. Likewise,
broad read roles stay until the minimal real-data read flow (1.9) works.

### What may slip, and what may not

- **May slip to phase 2** without blocking 1.16: catalogue v1 (1.17), together with the
  managed-settings keys that enforce it; log redaction and secret moves beyond the first services.
  Catalogue v1 slipping is a deviation from framing Q8, which ranked it third for the first 30
  days, and needs owner agreement.
- **May not slip:** `defaultMode`, the allowlist (D1 "immediately", OD7b), the OD21 keys, and the
  OTel exporter (the evidence for D1).

## Phase 2 — days 30–60: guardrails that need phase 1 in place

| # | Item | Owner | Layer |
|---|---|---|---|
| 2.1 | Rest of the managed baseline (E8 phase 2) and verification of the SSM option (both moved here by the owner, OD4) | DS | 2, 7 |
| 2.2 | SCPs: data-plane deny, Lambda update deny, revocation Deny, deny of trail changes in prod accounts (E5); outside-org write deny on every OU (not in E5) | DS | 1, 7 |
| 2.3 | Scheduled drift detection; automated JIT reconciliation | DS, PL | 7 |
| 2.4 | GitHub audit-log export, export of deploy run logs and risk-stop summaries (retention ⚠️ G7), change records, monthly reconciliation of prod changes with approvals (S3) | DS, CO | 3, 7 |
| 2.5 | Access Analyzer and policy-pack checks (E10); the risk stop's policy-finding trigger starts working | DS | 3, 5 |
| 2.6 | Aurora activity streams | PL | 6, 7 |
| 2.7 | Emergency federation for Identity Center outages | DS | 7 |
| 2.8 | Alert routing and the rest of on-call (G5) | EM, DS | 7 |
| 2.9 | Separate preview role and split of the deploy job (OD15), and narrowing the job-wide OIDC token (OD20) | PL, DS | 3, 5 |

## Phase 3 — days 60–90: test, measure, review

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
| S2 | No long-lived cloud credential in GitHub secrets | 0 (k0s/Firebase excepted, OD1) | Phase 1, after 1.3 |
| S3 | Every prod change approved by a named person other than the author, **before** it is applied | 0 unmatched / 0 late | Phase 2 (2.4); by hand before that |
| S4 | Engineers keep their speed: PR to prod the same working day; approval wait ≤ 1 h in working hours; no new step in the non-prod loop | as stated | Phase 1 |
| S5 | Every laptop gets the organisation's Claude Code policy; no one can turn off all prompts unnoticed | 100 % / 0 (depends on GĐ-6; caveat in layer 2) | Phase 1 (1.18) |
| S6 | No MCP server or plugin outside the catalogue; new requests decided in ≤ 5 working days | 0 / ≤ 5 days | When 1.17 lands |
| S7 | Named on-call including approvers; all prod alerts in one channel; incident approval wait ≤ 15 min, 24/7 | as stated | Schedules: phase 1; alert routing: phase 2 |
| S8 | Evidence for a random prod change shown in ≤ 30 min without asking anyone | ≤ 30 min | Phase 2 (2.4); first full pack in 3.4 |
| S9 | No real-data read on prod without an approved request | 0 | Phase 1 (1.9) |
| S10 | 100 % of PRs to `main` pass secret scan, dependency check and SAST; 0 direct pushes; 0 secrets found after merge | 100 % / 0 / 0 | Phase 1 (1.8) |
| S11 | No real data in non-prod | 0 | Phase 1 (1.2) |

The framework adds two metric sets: the prompt metrics of [layer 2](01-framework.md#layer-2--agent-runtime-controls)
(OTel `permission_mode` and time blocked on the user; thresholds ⚠️) and the JIT metrics of
[layer 7](01-framework.md#layer-7--observability-audit-incident-response-and-break-glass) (JIT used
where a PR was possible, writes outside the command list, late codify PRs, grants per month; starting
thresholds ⚠️). A breach of a JIT metric leads to a faster PR lane or a runbook, never a wider JIT.

## Load and risks

- **Phase-1 load [design; effort not estimated ⚠️]:** phase 1 holds 18 items for 1–2 DevSecOps
  people (GĐ-1) plus the owners of deploy workflows. This is the main rollout risk. The
  answer is the order above: the hard prerequisites first, the items that may slip last.
- **Engineering speed (S4).** If S1–S3 are met but S4 is not, engineers will find a way around the
  controls (framing §5, P3b), and S1–S3 will not hold. S4 is measured from phase 1 and reviewed with
  the security metrics, not after them.
- **Exceptions:** a ticket with owner, reason and expiry (layer 8).
