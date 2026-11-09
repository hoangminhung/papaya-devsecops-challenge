# Compliance mapping: control and evidence register

> Status: approved by the owner 2026-11-09 · Updated: 2026-11-09 · Builds on [`01-framework.md`](01-framework.md)
> Audience: Compliance and auditors.

## How to use this register

- One row per main control of the [framework](01-framework.md), linked to its layer. No new controls or decisions.
- **Evidence** is a record an auditor can read without asking anyone. Controls are designs, not
  checked on Papaya's systems; rows say what they *should* produce.
- Markers as in the framework: 📖 R*x.y* documented (row in `work/02-research.md`); ⚠️ inference or
  unverified; [design] untested proposal. E1–E10 are the locally checked examples in
  [`examples/`](../examples/README.md): the expected configuration in git.
- **Not** a Statement of Applicability or a legal analysis (out of scope, `work/05-deliverable-plan.md`
  §4). HIPAA applicability is a legal question (⚠️ R1.11.1.11).
- Short forms: **6 y** = at least 6 years, HIPAA's documentation rule (📖 R5.2.9), applied by the
  framework to approval and change records (⚠️ R5.7 #2). **O-n** = not decided in the framework, see
  [open items](#known-gaps-for-compliance). **Ph n** and **From phase** = rollout phase ([rollout plan](03-rollout-plan.md)); "—" = not set
  in the rollout plan.
  **Owner:** DevSecOps is the control owner of every row ([Roles](01-framework.md#roles)); the
  column adds who runs or approves it where the framework says.

**Who retrieves.** PRs, reviews, checks, git files and active rulesets: anyone with read access to the
monorepo (📖 R3.2.2 for rulesets; the rest ⚠️). GitHub org audit log: only org owners (📖 R3.5.6), so Compliance reads the
export (Ph 2). Log archive and change records: O-3.

## Register

Standards for each group: [cross-reference](#standards-cross-reference).

### Access ([layer 1](01-framework.md#layer-1--identity-and-access))

| ID | Control | From phase | Owner | Evidence → where | Kept | Checked | S |
|---|---|---|---|---|---|---|---|
| C-01 | No standing prod write; `ProdReadMetadata` is the only standing prod role | 1 | IAM code: L3 owner team + on-call group (OD9) | Identity Center assignment export; IAM users and keys with prod write; permission sets and trust policies in git (E4, E6) | git; export O-2 | quarterly; monthly S1 | S1, S9 |
| C-02 | SCPs on the prod OU and outside-org write deny, Ph 2 | 2 | L3 owner team only (OD13) | SCP code and PRs (E5), the written access rule for sensitive data (📖 R5.4.3; ⚠️ R5.7 #5); Access Analyzer `check-no-new-access` on policy PRs (📖 R2.8.1) | git | per PR | S1, S9 |
| C-03 | Review of permission sets, GitHub admins, Claude org Owners | — | O-6 | Review record (O-6) | O-2 | quarterly | S1 |

### Change ([layer 3](01-framework.md#layer-3--change-workflow-by-risk-level), [layer 5](01-framework.md#layer-5--cicd-hardening))

| ID | Control | From phase | Owner | Evidence → where | Kept | Checked | S |
|---|---|---|---|---|---|---|---|
| C-04 | Every prod change is a PR approved before merge by a code owner ≠ author, ≠ last pusher | 1 | code owner of the path | PR: author, final diff, reviews with times, checks, squash commit (OD16) | GitHub (⚠️ not researched); 6 y in C-19 | per change | S3, S4 |
| C-05 | Ruleset on `main` (E1 lists the rules) | 1; alerts 2 | platform team or named engineers (⚠️ team unknown) | Copy in git (E1); live comparison (G8); `repository_ruleset.update`, `protected_branch.policy_override` (📖 R3.5.6), alerted Ph 2 | git; audit log 180 days (📖 R3.5.6), export O-4 | on event; comparison O-5 | S3, S10 |
| C-06 | CODEOWNERS: L3 paths for the L3 owner team; deployable paths co-owned by the on-call group; validation check | 1 | content: engineering leads; changes: L3 owner team | File in git (E2); validation per PR; report of cross-domain approvals without `incident` label (OD9) and cross-team PRs without domain review (OD10) | git; reports O-2 | per PR; monthly | S3 |
| C-07 | Merge approval = deploy approval: `production` only from `main` and the deploy workflow; prod OIDC roles trust only it; tip of `main` only (OD17) | 1 | platform team or named engineers; changes: L3 owner team | E3, E3b, E4 in git; deploy run log; CloudTrail session `deploy-<run_id>-<attempt>` [design, E3]; `environment.*` events (📖 R3.1.4) | run log ⚠️ G7 | per change | S2, S3 |
| C-08 | Risk stop: a risky prod diff waits for a stack owner's approval of the preview | 1; policy trigger 2 | stack owners (OD8); classifier: L3 owner team (OD14) | `risk-summary` artifact, names not values (E7); `deploy-approvals/<stack>/<sha>.yaml` with preview hash, and its PR; three-person deviations (OD11) | git; artifact ⚠️ G7 | per deploy; monthly | S3 |
| C-09 | Required checks: secret scan, dependency check, SAST (Ph 1, G4); Access Analyzer, policy packs (Ph 2, E10); approval-gate check for app-opened PRs (G19) | 1; Access Analyzer, policy packs 2 | DevSecOps | Check results per PR; required checks in E1 | GitHub (⚠️) | per PR; monthly | S10 |
| C-10 | Incident lane: `incident` label, on-call approver paged, checks still run, approval wait ≤ 15 min | 1 | engineering management (schedule) | PR label and review times; on-call schedule (C-22) | O-2 | per incident; monthly | S7 |

### Agent runtime and supply chain ([layer 2](01-framework.md#layer-2--agent-runtime-controls), [layer 4](01-framework.md#layer-4--supply-chain-for-mcp-servers-and-plugins), layer 5)

| ID | Control | From phase | Owner | Evidence → where | Kept | Checked | S |
|---|---|---|---|---|---|---|---|
| C-11 | Managed settings (phase-1 subset, rest Ph 2, OD4); OTel without prompt content | 1 subset; rest 2 | DevSecOps; console edits: Claude org Owners (📖 R1.1.5) | Copy in git with PR approvals (E8); console export diffed with git [design] (G18); `/status`, `claude doctor` samples (📖 R1.1.18; values ⚠️); OTel `permission_mode`, `blocked_on_user` (fields 📖 research 6.6 D1; thresholds ⚠️), backend O-8 (not tamper-proof, 📖 R1.1.20). Team settings audit events ⚠️ R1.1.12 | git; rest O-2 | monthly; sampling O-5 | S5 |
| C-12 | Plugin/MCP catalogue, review ≤ 5 working days | 1 (may slip to 2) | DevSecOps | Marketplace file in git, one PR and review record per entry (E9); OTel `plugin_installed` / `plugin_loaded` (📖 R1.4.6). Which MCP server or tool was called is not recorded: that needs `OTEL_LOG_TOOL_DETAILS=1` (📖 R1.3.8), kept off until it is known whether it also logs tool inputs (⚠️); so "0 MCP servers outside the catalogue" rests on the managed lock (C-11) | git | per request; monthly | S6 |
| C-13 | Supplier register: certificate, BAA/DPA status, allowed data (list ⚠️ R5.6) | — | Compliance | Register (O-9) | O-2 | per supplier; O-9 | S6 |
| C-14 | CI credentials: OIDC, no stored keys, Actions cannot approve PRs, pinned actions; k0s/Firebase exception as `production` environment secret (OD1, OD6) | 1 | platform team or named engineers; exception owner | Workflows, lockfile (E3); secrets inventory; exception register; `org.update_actions_secret`, `repo.set_workflow_permission_can_approve_pr` (📖 R3.5.6, R3.3.3); no researched event for environment secrets (⚠️), so the settings comparison (C-21) covers the S2 exception | git; audit log as C-05 | monthly; at expiry | S2 |

### Data protection ([layer 6](01-framework.md#layer-6--data-protection-and-prompt-injection-defence))

| ID | Control | From phase | Owner | Evidence → where | Kept | Checked | S |
|---|---|---|---|---|---|---|---|
| C-15 | Real-data read (L3-data): one tenant, window, agreement; approver ≠ requester; data owner co-approves or reviews next day | 1 | approver; data owner [design] | Request and approvals (O-1); data-read role CloudTrail; Aurora activity streams, Ph 2 (📖 R2.7.2), as PHI (⚠️ R2.7.3) | O-2 | per grant; monthly | S9 |
| C-16 | PHI out of agent sessions: logs redacted at source, no raw partner documents, no PHI on Firebase, `cleanupPeriodDays` (Ph 2) | 1, per service | DevSecOps | SCP/IAM text (C-02); log-redaction reviews ([threat model](05-threat-model.md) T17); managed settings (C-11); planted-injection report (C-24) | git | per service, before its raw logs open | S9 |
| C-17 | Non-prod synthetic or masked; non-prod scan; unscanned store follows L3-data | 1 | DevSecOps; tool G4 | Scan results | O-2 | start of Ph 1; then O-5 | S11 |
| C-18 | Vietnam example: agent data flows update the transfer impact assessment (⚠️ R5.7 #4) | — | Papaya legal | Updated dossier | O-2 | every 6 months when something changes (📖 R5.4.5) | — |

### Logging, incident response and break-glass ([layer 7](01-framework.md#layer-7--observability-audit-incident-response-and-break-glass))

| ID | Control | From phase | Owner | Evidence → where | Kept | Checked | S |
|---|---|---|---|---|---|---|---|
| C-19 | Change record per prod change; monthly reconciliation, Ph 2 | 2 | DevSecOps | Record keyed by commit SHA or JIT request ID, linking PR, approvals, run, preview, CloudTrail [design]; exported run log (⚠️ G7); report of unmatched writes and late approvals | 6 y | monthly | S3, S8 |
| C-20 | Organization CloudTrail to a log-archive account, integrity validation, selected data events | — | DevSecOps | Logs and signed digests (📖 R2.6.4); actor `onBehalfOf.userId` (📖 R2.5.1) or session name + directory lookup (⚠️ R2.5.3); holds PHI (⚠️ research 1.11.4 L15) | until a lifecycle rule (📖 R2.6.5); O-2 | via C-19; digests O-5 | S3, S8 |
| C-21 | GitHub audit-log export; alerts on ruleset and environment events; settings comparison incl. on-call members (G8, G16); drift detection, Ph 2 | 2 | DevSecOps | Export (📖 R3.5.6); alerts; comparison results; drift tickets with actor | 180 days in GitHub; export O-4 | on event; O-5 | S3, S8 |
| C-22 | Named on-call approvers (primary + backup, 24/7) and responders; alert routing Ph 2 (G5) | 1; alert routing 2 | engineering management | Published schedules; approval waits (C-10) | O-2 | monthly | S7 |
| C-23 | JIT break-glass: incidents only, approval before grant, 1-hour role, command list, reconciliation, codify PR; emergency federation, Ph 2 | 1; automated reconciliation, emergency federation 2 | on-call approver; revocation SCP: L3 owner team (G20) | Request and approval (O-1); `CreateAccountAssignment` / `DeleteAccountAssignment` (📖 R2.4.2) linked by request ID [design]; writes-vs-list comparison (by hand Ph 1); codify PR; JIT metrics | 6 y | per grant; monthly | S3, S7 |

### Governance ([layer 8](01-framework.md#layer-8--governance-and-rollout))

| ID | Control | From phase | Owner | Evidence → where | Kept | Checked | S |
|---|---|---|---|---|---|---|---|
| C-24 | Policy as code; metrics S1–S11, JIT and prompt metrics; exception register; 90-day review of D1–D3; planted-injection test (Ph 3) | 1; injection test 3 | DevSecOps; Compliance reviews evidence | Git history of policy files; monthly report; register; review minutes; test report | git; rest O-2 | per PR; monthly; 90 days | all |

## Evidence for one prod change (S8)

**Target** (framing §5): for a prod change picked at random, show who proposed, who approved, what
was approved, what was applied and when, in ≤ 30 minutes, without asking anyone. Not yet timed
(⚠️; first measured in rollout).

Start **backward**, from a prod write in CloudTrail: unlike starting from a PR, this also finds
unapproved writes, as the monthly reconciliation does (S3).

| Step | Question | Record | Where |
|---|---|---|---|
| 1 | What was applied, when? | Write event: `eventTime`, `eventName`, resource; session name `deploy-<run_id>-<attempt>` [design, E3] in `principalId` (📖 R2.5.3) | CloudTrail; digests prove integrity (📖 R2.6.4) |
| 2 | Which run, which commits? | Run ID → deploy run: stack, commit SHA, preview, risk-stop result. A run can deploy several commits: GitHub cancels a pending run when a newer one arrives, so the run deploys every commit on `main` between the stack's previous successful deploy and its own SHA ([examples, limits of the risk stop](../examples/README.md#limits-of-the-risk-stop)) | Actions log (⚠️ G7; export Ph 2) |
| 3 | What was approved? | Each of those commits → its squash-merged PR (OD16). Stale approvals are dismissed (📖 R3.2.3), so approval covers the final diff | GitHub PR |
| 4 | Who proposed? | PR author; for an app-opened PR, the person who triggered it, from the approval-gate check (G19) | GitHub PR |
| 5 | Who approved, before apply? | Review name and time; approver ≠ author, ≠ last pusher (📖 R3.2.3, R3.3.1); approver owns the path (CODEOWNERS at that commit). Approval < merge < `eventTime` | GitHub PR; git |
| 6 | Was the gate on? | E1 copy; no `repository_ruleset.update` or `protected_branch.policy_override` between the approval and `eventTime`; G8 results | git; audit-log export |
| 7 | Did the risk stop fire? | `risk-summary`; `deploy-approvals/` PR with hash and stack-owner approval; second run shows the hash matched | artifact (⚠️ G7); git; PR |

From Ph 2 the change record (C-19) holds these links, so steps 2–7 are one lookup. In Ph 1 there is
no change record, export or reconciliation: the auditor follows links by hand, and old records may be
gone (audit log 180 days, 📖 R3.5.6; Actions ⚠️ G7). S8 is realistic only from Ph 2 (⚠️ inference).

**Serverless stacks:** CloudFormation makes the changes with the stack's `deploymentRole` (layer 3),
so those events may not carry the run's session name (⚠️ not researched). The link is the deploy
session's CloudFormation call plus the stack's events.

**Incident lane:** the same chain, plus the `incident` label and the on-call schedule showing the
approver was the primary on shift, or the backup while the primary was unavailable (O-7). The wait
(S7) runs from review request to approval. In Ph 1 the approver is called by phone, so paging time is
not recorded (G5).

**JIT fallback**, keyed by the JIT request ID ([layer 7](01-framework.md#layer-7--observability-audit-incident-response-and-break-glass)):
(1) proposed: command list, scope, reason, incident link, in a channel independent of GitHub (O-1);
(2) approved: on-call approver ≠ requester, before the grant; (3) granted: `CreateAccountAssignment`
and `DeleteAccountAssignment` (📖 R2.4.2); (4) applied: CloudTrail writes of the
`InfraOperator-<service>` session, the human named by `onBehalfOf.userId` where present (📖 R2.5.1),
else by session name and directory lookup, not a stable key (⚠️ R2.5.3); (5) reconciled: writes compared with the list, codify PR merged, drift
ticket until then. The approver approved a **command list**, not the applied change; a write outside
the list is found afterwards, not prevented.

## Known gaps for Compliance

**Approval before apply, met only partly:**

1. **JIT fallback**, accepted by the owner (Options §9 Q2, [§1](01-framework.md#1-the-decision-in-one-page)).
   Window up to about 2 h (⚠️ R2.9 #3); no night-time revocation (G20).
2. **Process-only rules**, checked by sampling or monthly reports: an agent never approves; its
   approval through the engineer's login is not detected (OD5; `actor_is_agent` undefined, R3.5.6).
   No agent in the JIT or PHI terminal (D2); incident-session flags (D3); normal-day domain review (OD9, OD10).
3. **Prod diff unseen on GitHub Team** unless the risk stop fires (⚠️ R4.6 #1). The stop misses
   approved malicious code (OD15) and has the OD18 limit; hash stability ⚠️ Options §8. One L3 approver (OD2).
4. **Admins can edit the gate:** logged, not prevented (📖 R3.2.2; ⚠️ R3.6 #1); UI changes to the
   `production` branch policy may leave no event (⚠️ R3.1.4).

**Evidence gaps** ([framework Gaps](01-framework.md#gaps-not-covered-or-only-as-an-open-item-in-work02-researchmd)):
change records, reconciliation, export and alerts arrive in Ph 2, so S3 and S8 are not routine
before then. Also G7, G8, G16, G18, G19, G17, G5; no CloudTrail chain or risk stop for k0s and
Firebase (G1, G2); Aurora SQL likely invisible to CloudTrail before activity streams (⚠️ R2.7.1).
Standards: ISO IDs, other jurisdictions and Papaya's sector under Decree 356 Art. 8 are open (R5.8);
the HIPAA proposed rule is not in force (📖 R5.3.1), so its items are forward-looking (⚠️ R5.7 #6).

**Open items, not decided in the framework:**

| # | Item |
|---|---|
| O-1 | Where JIT and real-data requests and approvals are stored (JIT tool not chosen, layer 1) |
| O-2 | Retention of raw logs, exports, telemetry and reports, and whether real-data approvals count as approval records (6 y); Papaya's compliance owner (⚠️ R5.7 #2) |
| O-3 | Who (Compliance, external auditors) can read the log archive and change records |
| O-4 | Destination and retention of the audit-log export and exported run logs (G7) |
| O-5 | Frequency of settings comparisons, machine sampling, digest validation, drift and non-prod scans |
| O-6 | Who performs the quarterly access review; where its record lives |
| O-7 | How on-call shifts and "primary unavailable" are recorded |
| O-8 | Telemetry backend for OTel |
| O-9 | Location and refresh cycle of the supplier register |

## Standards cross-reference

Mapping is inference (⚠️ R5.6). HIPAA and Vietnam text is documented (📖 R5.2, R5.4). ISO IDs are
recalled, not read (⚠️ R5.1): check them against Papaya's licensed copy or the NIST crosswalk (R5.8).

| Area (rows) | ISO 27001:2022 Annex A (⚠️ R5.1) | HIPAA Security Rule | Vietnam example |
|---|---|---|---|
| Access, layers 1, 6 (C-01–C-03, C-15) | 5.15–5.18, 8.2, 8.3, 8.5 | 164.312(a)(2)(i) (📖 R5.2.6); 164.308(a)(3)–(4) (📖 R5.2.3, R5.2.4); 164.312(d) (📖 R5.2.8) | Decree 356 Art. 4(2) (📖 R5.4.3); Law 91 Art. 30(3) (📖 R5.4.7) |
| Change, layers 3, 5 (C-04–C-10, C-14) | 8.32, 8.31, 8.25, 5.3, 8.9, 8.4 | 164.312(c) (📖 R5.2.8); 164.316(b) (📖 R5.2.9); no change-approval standard exists (📖 R5.2.10) | — (none found; nearest Law 91 Art. 22, ⚠️ R5.6) |
| Suppliers and agent tools, layers 2, 4 (C-11–C-13) | 5.19–5.23, 8.19 | 164.308(b), 164.314(a) (📖 R1.11.3.1); workstations 164.310(b)–(d) (📖 R5.2.11; relevance ⚠️) | Law 91 Art. 20 (📖 R5.4.5); Decree 356 Arts. 10, 12 (📖 R5.4.7) |
| Data protection, layer 6 (C-15–C-18) | 5.12, 5.34, 8.11, 8.12, 8.33 | Minimum necessary, 164.502(b), Privacy Rule (📖 R1.11.1.8) | Decree 356 Art. 4(2); Law 91 Arts. 20, 22 (📖 R5.4.5) |
| Logging, break-glass, layer 7 (C-19–C-23) | 8.15, 8.16, 5.28, 5.33, 5.24–5.27 | 164.312(b) (📖 R5.2.7); 164.308(a)(1)(ii)(D) (📖 R5.2.2); 164.308(a)(6) (📖 R5.2.5); 164.312(a)(2)(ii) (📖 R5.2.6; mapping ⚠️ R5.7 #3) | Law 91 Art. 23, 72 h notice (📖 R5.4.6; mapping ⚠️); Decree 356 Art. 8(1), finance sector only (📖 R5.4.4; sector ⚠️) |
| Governance, layer 8 (C-24) | 5.2, 5.37, 6.3 | 164.308(a)(8) (📖 R5.2.10); 164.316(b) (📖 R5.2.9) | — |

"A named human approves" is Papaya's chosen way to meet these controls, not a literal requirement
(⚠️ R5.7 #1). The record chain in this register is what shows Papaya follows its own policy.
