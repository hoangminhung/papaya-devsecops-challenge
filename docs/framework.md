# Framework: coding agents for DevSecOps at Papaya

> Status: v3 after 17 independent review rounds; approved by the owner 2026-11-09 · Updated: 2026-11-09
> Audience: a panel of Engineering and Compliance. Each layer ends with what it costs engineers and
> what it gives Compliance.

## How to read this

Eight layers. Each has a **Principle** (tool-independent), **On Papaya's stack** (Pulumi,
Serverless Framework, GitHub Actions, AWS, GCP, k0s, Claude Code) and **Audit evidence** (records an
auditor can test without asking anyone). Copy-paste detail belongs in `examples/`.

| Marker | Meaning |
|---|---|
| 📖 R*x.y* | Documented. R*x.y* is a ✅/📖 row in `work/02-research.md` that quotes or links the official page (a few rows cite vendor blogs, bulletins or example files instead, e.g. R2.4.1b, R6.3.5, R5.5.4). |
| ⚠️ R*x.y* | Inference, open question or "What this means for Papaya" conclusion in the research (sections 1.8, 2.9, 3.6, 3.7, 4.6, 5.6, 5.7, 6.5), or the ⚠️ part of a mixed row. Reasoned, not documented. |
| ⚠️ | Not verified at all, e.g. an illustrative command. |
| [design] | My proposal, built from documented parts, untested. Treat as ⚠️. |

Nothing here was checked locally (✅): this is a design without access to Papaya's systems.
**GĐ-n** = assumption in `work/01-problem-framing.md` §4 (owner-confirmed: GĐ-1, 2, 5, 6, 8, 9, 11,
14; the others are marked "unconfirmed" where used); **S-n** = success criteria
(§5); **P/A-n** = problems (§1); **D1–D3** = owner decisions in research 6.6; **Options §n** =
`work/03-options.md`; **G-n** = gaps; **OD-n** = owner decisions on this draft (both at the end).
Earlier owner answers are cited with their source: "research 6.9.4 Q4", "framing Q8", "Options §9 Q2".

---

## 1. The decision in one page

Engineering and Compliance disagree only about **writes to production**; reads of metadata and all
of non-prod are outside Compliance's sentence (framing §3.1). Real customer data is layer 6.

**Chosen approach "A + D2'"** (Options §9, owner decision 2026-11-09):

1. **Default path:** every prod change is a pull request, approved by a named human who is not the
   author, applied by CI. Incidents included ("IaC first").
2. **Fallback (break-glass):** only when the PR path cannot be used, a human gets an approved grant
   with a 1-hour role session (effective window up to about 2 h, ⚠️ R2.9 #3) and runs an approved command list in a terminal without an agent (layer 7) [design].
3. **Nothing standing:** no human or agent holds standing prod write; no long-lived credentials.

| Engineering gets | Compliance gets |
|---|---|
| A free loop in non-prod: read, change, deploy without approval (non-prod is synthetic or masked, GĐ-14; stores not yet scanned are excluded, layer 6). | Every prod change approved **before** apply by a named human ≠ author (GĐ-8, GĐ-11), enforced in GitHub and AWS IAM, outside the agent (limits below). |
| Read-only prod metadata for the agent. | No standing prod write (S1), no long-lived CI keys (S2, with an owner-approved exception for k0s/Firebase deploy credentials, OD1, OD6; storage conditions [design], layer 5). |
| Self-service PRs, one approval, same-day ship (S4). | One evidence chain per change; approval and change records ≥ 6 years (📖 R5.2.9; applied to change records ⚠️ R5.7 #2). |
| Incident lane: approval wait ≤ 15 min, 24/7 (S7). Decision-to-apply target ≤ 30 min (Options §9); current estimate 11–46 min ⚠️, measured first in rollout. | Agent-side controls as a second layer, not the control of record. |

**Where the design falls short, stated openly:**

- **The fallback meets the approval rule only partly** (approves a command list, not an applied
  change); accepted by the owner (Options §9 Q2). It is a second, process-controlled path, while the
  framing asked for one technically enforced path (framing §3.3, Options §7). It stays narrow only
  if most incidents are expressible in IaC (unknown, Options §8); layer 7 measures this.
- **On GitHub Team nobody sees the prod diff before apply** (⚠️ R4.6 #1; Team assumed, GĐ-5).
  Risky prod diffs stop the deploy until an owner of the stack approves the prod preview [design].
- **Admins can edit the gate**; logged, not prevented (logging 📖 R3.2.2; ability to edit ⚠️ R3.2.2,
  R3.6 #1). An admin's agent has
  the same power, because the agent uses its engineer's GitHub login (⚠️ R6.5 #10).
- **Some rules are process, not technology:** see "Process rules" in layer 1. The owner's rule
  "the PR approver is always an engineer, never an agent" (OD5) is absolute as policy, but on
  laptops it is enforced by policy and training, not by a technical control: an agent could approve
  through its engineer's login, and no detection was found.
- **Incident approvers vs domain review:** code-owner review means an approver must own the file,
  at L2 as at L3. So that one on-call primary can approve any deployable path at 2 a.m., the on-call approver
  group co-owns every deployable path (owner decision OD9, layer 3). The cost: GitHub accepts an
  approval from any listed owner (📖 R3.2.7), so on normal days that group could approve another
  domain's PR. Domain review on normal days becomes a process rule with a monthly check, not a
  technical control. Because on-call approvers only
  approve (OD7), a night incident needs two people awake: the incident responder and the on-call
  approver (the backup only replaces an unavailable primary).
- **One approver for high-risk changes.** L3 changes (IAM, stateful deletes, workflow files) get one
  approver, like L2, but the path is owned by the L3 owner team (or by the stack's owners for L3
  content in domain files, OD8), and risky prod diffs stop for a look at
  the prod preview (OD2, OD8, layer 3). A single reviewer can miss things; this is the owner's trade-off
  for speed.
- **k0s and Firebase are weaker:** no prod preview or risk stop, no CloudTrail for k0s changes
  (so S3 reconciliation does not cover them), and no break-glass when Actions is down (G1, G2).
- **New dependencies on two GitHub Apps** (required check, CI agent): if the required-check app is
  down, every merge to `main` is blocked, incident PRs included; that counts as "pipeline
  unavailable" for JIT. Their keys and hosting are open (G19).
- **HIPAA applicability is a legal question** (⚠️ R1.11.1.11); the design treats Papaya as a
  business associate, as the brief implies.

**Cross-cutting rules** (owner's balance principle, research 6.8):

1. **The boundary is IAM and the CI gate.** Server-managed settings are "a client-side control, not
   a security boundary" (📖 R1.1.7); local admins can edit endpoint files (📖 R1.1.8).
2. **Assume prompt injection succeeds:** neither OWASP nor NIST knows a full prevention (📖 R6.1.1, R6.1.2).
3. **Friction where damage is large, none where it is small**, measured, with a time-boxed escape.
4. **Evidence by construction:** the path produces the records.

### Roles

| Role | Rule |
|---|---|
| Author (engineer + their agent) | Never approves own change; GitHub blocks PR authors from approving (📖 R3.3.1). |
| Approver | Always an engineer, never an agent (owner rule, OD5). Named in CODEOWNERS; ≠ author, ≠ last pusher (📖 R3.2.3); for an app-opened PR, ≠ the person who triggered it (⚠️ R3.3.4, layer 5). |
| Incident responder | Engineer who diagnoses and writes the fix or the JIT request. Never the on-call approver of the same shift (OD7). |
| On-call approver | Engineer on the on-call schedule, primary + backup, 24/7; wait ≤ 15 min (S7). While on call they only approve: they write no fix and file no JIT request, so the approver is always distinct from the author (OD7). The primary approves; the backup replaces an unavailable primary (OD2). No platform-team membership is required; all engineers follow one agreed approval procedure (OD2). |
| Data owner [design] | Named per tenant; co-approves real-data reads, or reviews a night-time read the next working day (layer 6). |
| Control owner | DevSecOps (1–2 people, GĐ-1); owns policies and metrics; not the only approver. |
| L3 owner team | Owns the process-defining L3 paths and the SCP stack (layer 3); composition open (G17). |

---

## Layer 1 — Identity and access

**Principle.** Every action traces to one named human. Nobody holds standing prod write: prod is
written by the pipeline role, or in the fallback by an approved, time-boxed grant. Prod reads default
to metadata. No long-lived credentials. Prod and non-prod are separate boundaries.

**On Papaya's stack**

- **The engineer's access is the agent's access.** The agent uses the engineer's AWS SSO cache, and
  one portal session reaches every role assigned to that engineer (📖 R2.2.1, R2.2.2; token-reuse
  detail ⚠️ R2.2.2). A separate
  "agent" permission set does not separate them (⚠️ R2.9 #1). The control is what the **engineer**
  holds.
- **Process rules** that follow from this:
  - the JIT terminal runs no agent, though the grant is reachable from the same laptop (owner
    accepted as a process control, D2);
  - the incident-analysis session is meant to use only read-only roles (D2; `--restricted` per D3,
    research 6.9.4 Q2);
  - the real-data terminal runs no agent when the store holds PHI [design], same weakness as D2;
  - an agent never approves PRs: an owner rule (OD5), enforced on laptops by policy and training.
    GitHub blocks self-approval only. The auto-mode default block list
    excerpt read names "approving Claude's own pull request" (📖 R6.3.3); whether approving
    someone else's PR is blocked is unverified (⚠️), and the list
    applies only in auto mode. No detection was found (⚠️; `actor_is_agent` in the audit log has no
    documented meaning, R3.5.6).
- **IAM Identity Center permission sets** (📖 R2.1.1) [design names]:
  - `ProdReadMetadata`: metrics, redacted log groups, configuration; no data-plane read on claim
    stores; 1 h session, the minimum (📖 R2.1.4). Until a service's logs are redacted at source
    (layer 6), it gets that service's metrics only. Lambda configuration can hold secrets resolved by
    Serverless in plain text (⚠️ R4.4.7), so configuration reads are allowed per service only after
    its secrets move to runtime resolution (⚠️ R4.6 #7). Cost: until then the agent reads
    timeout/memory from the IaC code;
  - `NonProdDeveloper`: broad, non-prod accounts only;
  - `InfraOperator-<service>`: assigned only by the JIT flow (layer 7), via a partner product, the
    TEAM sample (📖 R2.4.1, R2.4.1b) or a small home-built flow (⚠️ R2.4.2) on the documented APIs
    `CreateAccountAssignment` / `DeleteAccountAssignment` (📖 R2.4.2);
  - no standing prod-write permission set.
- **SCPs on the prod OU** [design] (SCPs cap member-account principals, 📖 R2.3.1, R2.3.2):
  - deny data-plane reads on claim stores except application roles and the approved data-read role,
    by `aws:PrincipalArn` (📖 R2.3.8; pattern ⚠️ R2.9 #4). Actions, e.g. `s3:GetObject`,
    `sqs:ReceiveMessage`, `states:GetExecutionHistory`, are incomplete and unchecked (⚠️ G13);
  - deny `lambda:UpdateFunctionCode` / `lambda:UpdateFunctionConfiguration` (⚠️ R4.6 #3) except
    CloudFormation `deploymentRole`s, the Pulumi prod deploy role (if Pulumi manages Lambdas) and the
    JIT roles. This closes `serverless deploy function`, which changes config outside CloudFormation
    (📖 R4.4.4), and needs `deploymentRole` set on every Serverless stack (key 📖 R4.4.5; need ⚠️ R4.6 #3);
  - a pre-deployed revocation Deny on `identitystore:UserId` (📖 R2.4.4); protect the org trail (📖 R2.6.2).
  - Limits: 10 SCPs per target, 10,240 characters; no SCP applies to the management account
    (📖 R2.3.2, R2.3.4), so whatever deploys SCPs there is the most sensitive role (L3 path, held by the L3 owner team only, not co-owned by the on-call group; OD13).
- **Sessions/MFA:** portal session length set on purpose; an IdP session can extend it silently
  (📖 R2.1.5, R2.1.6). MFA lives in the external IdP if one is used (📖 R2.1.7).
- **CI → AWS:** GitHub OIDC, no stored keys (📖 R3.4.1). The prod role trusts only the `production`
  environment of the monorepo, in its `sub` format (📖 R3.4.3, R3.4.4; immutable format assumed,
  ⚠️ R3.7 A2), ideally customised with the deploy workflow's `job_workflow_ref` (📖 R3.4.5; on Team ⚠️ G10).
- **CI → GCP:** Workload Identity Federation restricted to Papaya's GitHub organization, which Google
  requires (📖 R3.4.5b).
- **k0s, GCP and Firebase for humans:** same principles; mechanisms not researched (G1–G3). Today
  k0s is reached with kubeconfigs, no SSO (GĐ-4, unconfirmed). Interim: no admin kubeconfig and no GCP
  owner role on laptops; prod deploys only from CI. Firebase is not on the GCP BAA list (📖 R5.5.3), so
  Firebase Hosting must hold no PHI (⚠️ R5.7 #7).

**Audit evidence.** Identity Center assignment export (S1); CloudTrail `CreateAccountAssignment` /
`DeleteAccountAssignment` per grant (📖 R2.4.2), linked to its approval by request ID [design]; SCPs
and trust policies as Pulumi code; IAM Access Analyzer `check-no-new-access` on policy PRs
(📖 R2.8.1; from phase 2); quarterly access review of permission sets and GitHub admins.

**Cost / value.** Engineers lose standing prod write and keep a free non-prod loop. Prod reads stay
fast for metrics and metadata, but shrink during the transition: because the engineer's access is the
agent's access, from phase 1 the engineer too loses raw logs and configuration of services not yet
redacted or moved to runtime secrets. Configuration values come from the IaC code instead (layer 1
above); raw logs that may hold customer data need an L3-data grant. The data owner is not on the
on-call schedule, so at night the grant is approved by the on-call approver alone and the data owner
reviews it the next working day [design]; the wait still counts against S7. This is
the largest cost of the first months. Compliance gets least privilege that is enforced.

---

## Layer 2 — Agent runtime controls

**Principle.** Agent-side controls are hygiene, not the boundary. They are central, versioned in git
and the same for everyone. Defaults are safe; overrides are measured. The session that reads
untrusted content holds as little power as possible (📖 R6.1.2).

**On Papaya's stack**

- **Delivery:** server-managed settings (available on Team, 📖 R1.1.5) for all laptops. With MDM, also
  an endpoint file; by default one managed source supplies most keys, so the two must carry the same
  keys or use `managedSourcesBehavior: "merge"` (📖 R1.1.3, R1.1.4). MDM is unknown; both are prepared.
- **Baseline** (template: Anthropic's `settings-hipaa.json`, 📖 R5.5.4). All keys 📖 at the row cited. Only the phase-1 subset in layer 8 ships first; the other keys (sandbox, `allowManagedHooksOnly`, credential denies, `allowManagedPermissionRulesOnly`, `allowedProviders`, `forceLoginOrgUUID`, the `ask` rule for WebFetch, and the other deny rules) arrive in phase 2 (OD4):

  | Key | Value and reason |
  |---|---|
  | `permissions.defaultMode` | `default` (Manual). A default, not a lock: users can switch to auto; VS Code remembers the last pick (D1, R6.9.3). |
  | `permissions.allow` | Read-only commands Papaya uses, to cut prompts (R6.9.3). It contains no command listed in `sandbox.excludedCommands` (`aws`, `pulumi`, `serverless`): an allowed excluded command would run outside the sandbox, with `~/.aws` and the network, without a prompt (⚠️ inference from R1.2.6, R1.6.4) [design]. Cost: a prompt for every `aws` read. |
  | `allowManagedPermissionRulesOnly` | `true`, one rule set (D1, research 6.9.4 Q4; R1.2.5). Cost: project and user rules are ignored, so the managed set must carry every deny/ask rule projects need; prompts likely rise (⚠️ research 6.9.4 Q4). |
  | `permissions.disableBypassPermissionsMode` | `"disable"`: removes bypass mode (P3a; R1.2.2). Auto mode, where a classifier approves instead of a person, stays available (D1) and is measured through `permission_mode`. |
  | `permissions.deny` / `ask` | Deny credential paths (R5.5.4; `Read(...)` syntax ⚠️ R1.8 #5). Ask for `WebFetch`, which the sandbox domain list does not limit (R1.6.2); cost: a prompt per fetch. The HIPAA template denies WebFetch (R5.5.4); "ask" is a deliberate deviation so that documentation lookups still work. |
  | `requiredMinimumVersion` | ≥ 2.1.285 for `allowedProviders` (R1.1.15), which also covers `--restricted` (2.1.248, R6.9.1b) and the plugin-pin fix (2.1.179, R6.2.7); ≥ 2.1.295 if any managed hook uses `onFailure: "block"` (R1.5.2); and ≥ the latest fixed advisory at rollout (R6.3.9). It does not end running sessions and fails open on a bad value (R1.1.13). |
  | `allowedProviders` + `forceLoginOrgUUID` | `["anthropic"]` + Papaya's org; closes most bypasses on **endpoint-managed** machines (R1.1.15). `forceLoginOrgUUID` checks claude.ai sign-ins only, not Claude Console sign-ins (R5.5.5); with it set, sessions on `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` or `apiKeyHelper` are refused (R1.11.3.11). |
  | `allowManagedHooksOnly` | `true` (R1.5.4). |
  | sandbox | `sandbox.enabled`, `failIfUnavailable`, `allowUnsandboxedCommands: false`, narrow `network.allowedDomains` locked by `network.allowManagedDomainsOnly`; `credentials` / `filesystem.denyRead` on `~/.aws`, which the sandbox can otherwise read (R1.6.3, R1.6.4). |
  | `sandbox.autoAllowBashIfSandboxed` | Left at its default `true` (owner decision OD12). This widens D1's "Manual + read-only allowlist": every sandboxed command, writes in the working directory and calls to allowed domains included, runs without a prompt. Detail: sandboxed Bash runs without a prompt, so in Manual mode prompts are for edits, unsandboxed commands and fetches, not every command (R5.5.5b). A deliberate choice: the sandbox (no `~/.aws`, allowlisted network) is the control for those commands. The HIPAA README says to set `false` if policy needs a person to approve each command (R5.5.5b); cost of `false`: a prompt per command. |
  | MCP, plugins | Layer 4. |
  | OTel | Exporter on, content flags `0` (R1.1.20, R5.5.4). |

- **Trade-off on AWS credentials [design].** With `~/.aws` hidden from the sandbox, the plan is to
  list `aws`, `pulumi` and `serverless` in `sandbox.excludedCommands`. Excluded commands run "with
  full access" (📖 R1.6.4), which likely includes the network (⚠️ inference). How the list matches
  commands (prefix or text, and chained commands) is not researched (⚠️). This is worse than an
  egress channel: `pulumi preview` runs the Pulumi program and `serverless` loads its config and
  plugins, all code in the repo that the agent can edit, so excluding them lets repo code run
  outside the sandbox with network access and with `~/.aws` readable (⚠️ inference). For these
  commands the sandbox gives no protection. And an injected `aws` command could send out the SSO
  token cache itself. That token likely opens every role assigned to the engineer for the rest of the
  portal session (📖 R2.1.5; token reuse ⚠️ R2.2.2), probably including JIT or data-read grants added
  later in that session (⚠️ inference). Mitigations [design]: a short portal session (📖 R2.1.5); end
  the existing portal session and sign in fresh **before** a JIT or data-read grant is created
  (whether ending a session invalidates a token already stolen is unverified ⚠️; ending it does not
  end role sessions, 📖 R2.4.3); an SCP that denies writes to resources outside Papaya's organization using
  `aws:ResourceOrgID` (key 📖 R2.3.8), on every OU, since the token can be stolen from a non-prod
  session; legitimate writes to outside resources need exceptions (⚠️ not inventoried). That SCP only stops Papaya's own credentials writing to a
  foreign bucket; it does not stop a command that sends the token to a non-AWS endpoint or uses the
  attacker's credentials (⚠️ inference). Prefer running `pulumi` and `serverless` against real
  accounts only in CI; on laptops keep them to non-prod roles, and move them into the phase-3
  container. Residual risk: token theft during a session. It is accepted
  because the engineer holds no **standing** prod write and no **standing** PHI read; during a JIT
  or data-read window the protection is the process rule in layer 1 (D2). Stronger option, phase 3:
  a separate OS user or container for prod-reading sessions
  (⚠️ R6.5 #2).
- **Session types:**

  | Session | Identity | Flags | Enforcement |
  |---|---|---|---|
  | Daily development (laptop) | non-prod roles + `ProdReadMetadata` | baseline | Auto mode by choice (D1); `--restricted` recommended (D3). |
  | Incident analysis (laptop) | meant to be `ProdReadMetadata` only | `--restricted --tools "Bash,Read,Grep,Glob"`, started in an empty scratch directory, not the repo [design] | Process rule (D3, research 6.9.4 Q1–Q2). No WebFetch, and file tools confined to the working directory (📖 R6.9.1b); Edit/Write are excluded only if `--tools` acts as an exclusive list (⚠️ unverified), but Bash can still write in its working directory (📖 R1.6.3) and call any role in the cache. |
  | CI agent (hosted runner) | own GitHub App token; never `production` | `--restricted`, explicit `--tools`; all rules in a managed-settings file on the runner | Workflow file under CODEOWNERS (D3, research 6.9.4 Q5). The file is advisory if `Bash` is in `--tools` (layer 5). |
  | JIT terminal | JIT grant | no agent | Process rule (D2). |
  | Auto-mode environment (phase 3) | non-prod only | auto encouraged | D1 option (c). |

- **Phase-1 interim posture:** the sandbox and credential denies arrive in phase 2 (OD4), so for
  the first 30–60 days `~/.aws` is readable and the network is open to every Bash command; in auto
  mode the classifier is the only gate. Impact is bounded once standing prod write is removed at the
  end of phase 1 (layer 1); before that, today's exposure continues, and token theft is easier in this window.
- **Hard limits:** Bash rules are not a boundary (📖 R1.2.6); hooks fail open unless
  `"onFailure": "block"` (📖 R1.5.2); `--restricted` cannot be forced by a setting (📖 R6.9.1), and a `PATH` wrapper on laptops can be bypassed (⚠️ R6.9.1c);
  on laptops **without MDM**, a different login, an API key or a `CLAUDE_CODE_USE_*` variable skips
  server-managed settings, `allowedProviders` included (📖 R1.1.7; ⚠️ R1.8 #3, G11). So S5's
  "nobody can turn off all prompts unnoticed" is likely unreachable without MDM (⚠️).
- **Auto memory:** engineers review it and delete it after a suspicious session; residual risk with a
  named owner (D3).
- **Fallback:** switch to `disableAutoMode` (📖 R1.2.2) if the planted-injection test steers auto mode, a serious
  advisory appears, or an audit finds auto mode touched a protected scope (D1).

**Audit evidence.** Managed settings as an expected copy in git with PR approvals. The live copy is
edited in the Claude admin console by Owners / Primary Owners (📖 R1.1.5), not by PR, and Team audit
events for settings changes are unconfirmed (⚠️ R1.1.12). `/status` shows which managed source
applies (📖 R1.1.18), and likely not the key values (⚠️), so it cannot detect a console edit; until a way to read the
live values is found (G18), an Owner exports the console settings monthly and diffs them with git
[design], and the list of Claude org Owners is kept short and reviewed quarterly; `/status` and `claude doctor` from
sampled machines (📖 R1.1.18); OTel `claude_code.tool_decision` (`permission_mode`) and
`claude_code.tool.blocked_on_user` (`duration_ms`, rubber-stamping signal) (fields 📖 research 6.6
D1 metrics; thresholds ⚠️).

**Cost / value.** More prompts than auto mode, partly offset by the read-only allowlist. Compliance
gets one organization policy with evidence instead of personal choices (P3c).

---

## Layer 3 — Change workflow by risk level

**Principle.** The level is set by the damage a change can do. One default path above non-prod: a
reviewed PR applied by the pipeline, with the JIT fallback (layer 7) as the only other write path.
The approver reviews the code change that will be applied. Every prod change needs two people, and
no more by default: one who makes it and one who approves it; the on-call backup only replaces an
unavailable primary (OD2). Higher risk narrows **who** may approve (the owners of that path), not how
many. Separately, any prod diff that looks risky stops the deploy, whatever its level; that adds a
second approval by an owner of the same stack, which keeps it to two people (OD8). Confirmed by the owner
(OD13): the original author opens the approval PR and the first approver
approves it. If the first approver is unavailable, another owner of the stack approves; that makes
three people and is recorded as a deviation, counted monthly (OD11). A cross-team PR needs one
approval, as GitHub accepts one on-call group member for files of several owner teams (OD10,
OD9, 📖 R3.2.7); domain review there is a recommendation, counted in the monthly report. A real-data read is not a change and has its own rule, L3-data. Incidents use the same
path with faster people, not fewer security checks.

| Level | What | Examples | Approval | Path |
|---|---|---|---|---|
| **L0** | Read: non-prod anything; prod metadata | metrics, redacted logs | none | read-only identity |
| **L1** | Change in non-prod | deploy a branch to dev; `pulumi preview` on non-prod (needs state-write permission on a DIY S3 backend, 📖 R4.3.3) | author only | non-prod roles or PR pipeline |
| **L2** | Routine prod change in code | Lambda timeout/memory, ECS desired count, release | 1 code owner ≠ author, ≠ last pusher | PR → `main` → deploy workflow |
| **L3** | High-risk prod change | IAM/SCP; replace/delete of stateful resources; network; `.github/**`, CODEOWNERS, `CLAUDE.md`, `CLAUDE.local.md`, `.claude/**`, `.claude.json`, `.mcp.json`, `.husky/`, `.gitmodules`, `.ripgreprc`, plugin/MCP catalogue and the rest of the canonical list in layer 5; advisory policy finding | 1 code owner ≠ author, ≠ last pusher. L3 paths (workflow and agent-config files, catalogue, the SCP stack): the L3 owner team only (OD13); IAM-only stacks are deployable, so the L3 owner team plus the on-call group (OD9). L3 content inside a domain file (an IAM statement in `serverless.yml`, a stateful delete): the stack's owner, then the risk stop (OD8). In incidents: the on-call approver for deployable paths (OD9); paths that define the process (CODEOWNERS, agent config, catalogue, workflows) wait for the L3 owner team | same path; for IaC changes the risk stop also applies; workflow and agent-config files have no prod diff |
| **L3-JIT** | Break-glass | ECS force-redeploy while Actions is down | on-call approver ≠ requester (Options §4b); incidents only, as the owner accepted it (Options §9 Q2); the on-call approver counts as owner of the service in the request (OD13) | layer 7 |
| **L3-data** | Real customer data read | one tenant's failed claim record | an approver ≠ requester and an agreement (GĐ-9); data-owner co-approval [design], beyond GĐ-9; at night, see layer 6 | layer 6 |

`CLAUDE.md` and the other agent configuration files are L3, because they define the workflow for
the whole team (OD3). With code-owner review on, every PR, L2 included, needs an approval from an
owner of the files it touches (📖 R3.2.3, R3.2.7; per-file behaviour ⚠️ not a separate research row).
What differs at L3 is **which team** owns the path: L3 paths are owned in CODEOWNERS by a designated
L3 owner team (deployable L3 paths also by the on-call group, OD9), L2 paths by their domain team; and IaC changes at L3 meet the
risk stop. Most IAM, network and stateful changes sit inside domain files, so they are approved by
the stack's owners, not the L3 team (OD8); automated checks make up for this: IAM Access Analyzer
`check-no-new-access` (📖 R2.8.1) and the Pulumi policy pack (📖 R4.2.2), both from phase 2 (layer 5). Cost: changes to `CLAUDE.md` (where D3 puts shared knowledge) need the L3 owner team, not
the domain team that edits it most.

**On Papaya's stack**

- **Gate = merge to `main`.** On Team, environment reviewers do not exist for private repos
  (📖 R3.1.2). Ruleset on `main`: PR required, 1 approval, code-owner review, dismiss stale approvals,
  approval by someone other than the last pusher, required checks from a pinned source app, no force
  push, empty bypass list (📖 R3.2.2, R3.2.3, R3.2.5). Branch up to date before merge, since there is
  no merge queue (⚠️ R4.6 #1; whether updating drops approvals is open, Options §8).
- **L3 approvals [design]:** CODEOWNERS plus code-owner review only, no path-based required
  reviewers rule. That rule (📖 R3.2.4) asks for approvals from specific teams, which the on-call
  group would not satisfy at night, and how it combines several teams is not researched (⚠️), so it
  would break OD9 or add a third person. GitHub stops the author from approving (📖 R3.3.1). A required check with a pinned source app (📖 R3.2.5), set by a dedicated GitHub App that reacts to review events and is the pinned source [design; hosting, key storage and whether its key counts against S2 are not researched, ⚠️ G19], adds what
  the rules cannot: for app-opened PRs it excludes the person who triggered the agent, and it counts
  only human approvals, since an app's approval might count (⚠️ R3.3.4, R3.7 A3). A workflow
  instead of an app is weaker: pinning the source to GitHub Actions likely lets any workflow set a
  check of the same name, and the trigger that runs on review events from trusted code is not
  researched (⚠️ G19).
- **Who approves at night (OD9):** a fixed GitHub team with write permission (owners without it
  are silently not assigned, 📖 R3.2.7; the CODEOWNERS validation check covers this), the on-call approvers, is listed as
  co-owner on every deployable path in CODEOWNERS (infrastructure and service code), next to the
  domain team. Confirmed by the owner (OD13): the group does **not** co-own the paths that
  define the process (`.github/**`, CODEOWNERS, `CLAUDE.md` and agent config, catalogue); those stay
  with the L3 owner team only. If a broken workflow blocks a night fix, the pipeline counts as
  unavailable and the JIT fallback applies (layer 7). One primary and one backup from that team are on call. Technically any member can approve any
  path; by rule the primary approves and the backup only if the primary is unavailable (OD2).
  Membership is fixed, not changed per shift [design]. GitHub team membership is set in organization
  settings, not by a PR; managing it as code (e.g. with Pulumi's GitHub provider) and the audit
  event for a membership change are not researched (⚠️ G16). Meanwhile the layer-7 settings
  comparison includes the group's member list. Cost: an approval from any
  listed owner satisfies code-owner review (📖 R3.2.7), so on normal days a member could approve
  another domain's PR, on or off shift. Mitigation [design]: process rule "approve another
  domain's PR only if it carries the `incident` label and you are on shift", and a monthly report of
  every cross-domain approval by group members on PRs without that label (layer 7). Whether Papaya's team size allows full coverage is unknown
  (§1, S7).
- **Risk stop [design]:** applies to every deploy, whatever the level. The deploy job previews prod;
  on stateful replace/delete, an IAM change, a network or security-group change, or an advisory
  policy finding (from phase 2) it stops and posts the filtered preview. The original author opens a second PR that adds
  `deploy-approvals/<stack>/<sha>.yaml` (`<sha>` = the stopped commit) holding that SHA and the
  preview hash; the workflow does not open it, because the setting that lets Actions create and approve PRs stays
  off (📖 R3.3.3; ⚠️ R3.6 #3). CODEOWNERS on `deploy-approvals/<stack>/` names the owners of that stack and the
  on-call group (OD8, OD9). The approver is ≠ author and may be the first PR's approver, who now sees
  the prod diff. Merging it triggers the deploy on the new HEAD, which previews again and continues
  only if the hash matches the approved one; if another PR merged in between, the hash differs and
  the deploy stops again (Options §1; hash stability ⚠️ Options §8). Cost: while a stack is
  stopped, later merges to that stack stop too until a matching approval lands; in an incident, a
  risky change already waiting on `main` blocks the fix for the same stack until it is approved or
  reverted. A
  `mandatory` policy violation always blocks `pulumi up` (📖 R4.2.2): the fix is a code change, or a
  change to the policy pack through its own L3 PR. Preview output is filtered for
  outputs and secrets before it is posted (Options §1; ⚠️ R4.6 #2).
- **Merge approval = deploy approval** only if (⚠️ R3.6 #1, from 📖 R3.1.3, R3.4.5c): `production`
  allows only `main`; only the reusable deploy workflow (under CODEOWNERS) references it; no ref/SHA
  inputs; no `issue_comment`, `pull_request_target` or `workflow_run` triggers; one concurrency group
  per stack without `cancel-in-progress` (📖 R4.1.4).
- **Pulumi:** PRs preview non-prod only, because a prod preview runs PR code with state-write and
  secret access (📖 R4.3.3, R4.3.4; ⚠️ R4.6 #2). On `main`: prod preview, then `pulumi up` with the
  policy pack, which stops on a mandatory violation (📖 R4.2.2). Prod runs allow no `--skip-preview`
  (📖 R4.1.2) and no targeting, replace, `state`, `import`, `destroy` (⚠️ R4.6 #3, G12). Pulumi Cloud,
  if used: OIDC via `pulumi/auth-actions`, no stored token (📖 R4.1.4).
- **Serverless v4:** `serverless package`; `serverless diff --json` (sf-core ≥ 4.37.0), parsed by CI
  because differences do not change the exit code (📖 R4.4.2); `serverless deploy --package`
  (📖 R4.4.3); a least-privilege `deploymentRole`, which cannot be removed later and is usable by
  anyone who may operate the stack (📖 R4.4.5), so JIT roles get no stack-operation rights.
- **State:** writable by deploy roles (and possibly the drift role, layer 7); Pulumi
  secrets via `awskms` on a DIY backend (📖 R4.3.3, R4.3.4; ⚠️ R4.6 #7).
- **k0s [design]:** manifests in the monorepo, applied by CI; no write RBAC for humans or agents in
  prod; read roles exclude logs and exec in namespaces with claim data (mechanism: G1). The risk
  stop is described for Pulumi and Serverless only; for k0s manifests (RBAC changes are the IAM
  equivalent) a `kubectl diff`-based stop is a candidate, not researched (⚠️ G1). Firebase deploys
  have no preview step in this design (⚠️ G2).
- **Incident lane:** label `incident`, on-call approver paged, security checks always run (S10), only
  slow unrelated tests skipped [design]. A required check skipped by a path filter may stay
  pending and block the merge (open, Options §8); this directly affects S7.

**Example: Lambda timeouts at 2 a.m.** (Options §6)

The incident responder is engineer E; the on-call approver is R (a backup replaces R only if R is
unavailable).

1. E's incident-analysis session reads metrics and redacted logs and proposes `timeout` 30 → 90 s,
   memory 1024 → 2048 MB, and a larger visibility timeout on the source queue (ratio ⚠️ Options §8).
2. A second session (edit tools; not meant to use prod roles) edits `serverless.yml`, runs
   `serverless diff` on non-prod, and opens a PR labelled `incident` as E.
3. R, a co-owner of `serverless.yml` through the on-call group (OD9), reviews the diff. If R
   catches a missing queue change, R does not fix it (OD7): E pushes the fix, the stale approval is
   dismissed, and R approves again, one more review round (Options §6). E merges.
4. The deploy workflow packages, previews prod, finds no risky change, deploys with the OIDC role.
5. Estimate 11–46 min (⚠️ Options §6) against ≤ 30 min: measured first in rollout.

**Audit evidence.** The PR (diff, approvers, checks); run log and preview artifact, exported because
retention is unverified (⚠️ G7); deploy-role CloudTrail events; all linked by commit SHA and run ID.

**Cost / value.** One approver for every prod change, from the owners of the path; two approvals,
usually by the same approver, when the risk stop fires (OD13; OD11). Cross-team PRs: one approval (OD10). None in non-prod.
Compliance gets four-eyes enforced by GitHub. Gap: on Team the prod diff is not seen before apply.

---

## Layer 4 — Supply chain for MCP servers and plugins

**Principle.** Local MCP servers, plugins and hooks run with the engineer's access (📖 R1.6.2, R5.5.5); remote MCP servers receive tokens and data.
Only reviewed, pinned entries from a catalogue are allowed. The catalogue is the inventory (P4c).
Review takes ≤ 5 working days (S6), or people work around it.

**On Papaya's stack**

- **Plugins:** a private marketplace repo with `.claude-plugin/marketplace.json` (📖 R1.4.1), sources
  pinned to `ref`/`sha` (📖 R1.4.1b, link only). Managed `strictKnownMarketplaces` = Papaya only,
  `blockedMarketplaces`, `enabledPlugins: false` to pull one (📖 R1.4.2), checked before download and
  at session start (📖 R1.4.3). `disableSideloadFlags` rejects `--plugin-dir`, `--plugin-url`,
  `--agents`, `--mcp-config` but not `.mcp.json` or `claude mcp add` (📖 R1.4.2). With
  `allowManagedHooksOnly`, plugin hooks run only for force-enabled plugins (📖 R1.5.4). User mods are
  blocked by the `allowManagedModsOnly` option under `pluginConfigs` → `cc-plugin-sec-default@builtin`
  → `options` (📖 R1.5.6). The version floor covers the plugin-pin fix of 2.1.179 (📖 R6.2.7).
- **MCP:** "approved catalogue" = `allowedMcpServers` + `allowManagedMcpServersOnly: true`; without
  the lock users can widen it (📖 R1.3.1, R1.3.4). Match by `serverUrl` or `serverCommand`, never
  `serverName` ("not a security control", 📖 R1.3.3); `serverCommand` matches the exact argv (📖 R1.3.3), so the catalogue entry pins an exact package version in it [design].
  `disableClaudeAiConnectors: true` (📖 R1.3.7). With MDM, `managed-mcp.json` gives exclusive control;
  it cannot come from server-managed settings (📖 R1.3.2).
- **Review checklist** [design]: publisher; local `stdio` or remote (📖 R6.4.3); what it reads and where
  it sends data, with a supplier-register entry and BAA/DPA status (⚠️ R5.6); no token passthrough
  (📖 R6.4.2); write tools for Slack, Linear, GitHub only where needed (⚠️ R6.5 #6); how the server authenticates (Linear and Slack: G9); pinned version,
  reviewer, date.
- **Known gaps:** no per-group targeting in server-managed settings (📖 R1.1.6, R1.4.4); tool
  description changes after approval are not covered (⚠️ research 6.6).

**Audit evidence.** Catalogue file in git (each entry = an approved PR); supplier register; OTel
`claude_code.plugin_installed` / `plugin_loaded` (📖 R1.4.6). MCP tool logging needs
`OTEL_LOG_TOOL_DETAILS=1` (📖 R1.3.8); it stays off until we know whether it logs tool inputs (⚠️).

**Cost / value.** Up to 5 days' wait for a new tool. Compliance gets an asset inventory and supplier
records.

---

## Layer 5 — CI/CD hardening

**Principle.** CI is the default production writer, so it is the main target. Short-lived,
least-privilege credentials per job. Every CI dependency is pinned. Agent-written code passes the same
checks as human code (S10).

**On Papaya's stack**

- **Credentials:** OIDC instead of keys and tokens in repository secrets, which any writer can read
  (📖 R3.4.1, R3.5.3b). Org default for `GITHUB_TOKEN` set to "restricted", `permissions:` per job (📖 R3.5.3).
  "Allow GitHub Actions to create and approve pull requests" off (📖 R3.3.3). Serverless License Key in
  SSM, read by the deploy role (sf ≥ 4.4.19, 📖 R4.4.8). Until G1/G2 are solved, k0s and Firebase
  deploys may need a stored credential in GitHub: a kubeconfig or token for k0s, a Firebase token or
  service-account key for Firebase Hosting. The owner accepts this as an exception to S2 = 0 until it
  is checked whether k0s and Firebase deploys can use OIDC (OD1, OD6). Conditions [design]:
  - stored only as an **environment secret of `production`**, never as a repository secret. Anyone
    with write access can read repository secrets (📖 R3.5.3b), which would turn the exception into
    standing prod write for every engineer and their agent. Environment secrets and a deployment
    branch rule limited to `main` are available on Team for private repos (📖 R3.1.2, R3.1.3), and
    only the reviewed deploy workflow references the environment (layer 3);
  - the deploy job runs on GitHub-hosted runners. On self-hosted runners, jobs "are not run in an
    isolated container, even if they use environments", so environment secrets there must be
    treated like repository secrets (📖 R3.1.5). Self-hosted runners "can be persistently
    compromised by untrusted code" from anyone who can open a PR, and runner groups limit only which
    repositories use them (📖 R3.5.2); in a monorepo any workflow can likely target the runner's label (⚠️ G15).
    How to restrict a runner to one workflow is not researched (⚠️ G15); just-in-time runners exist
    (📖 R3.5.2, not read in detail). If reaching k0s needs a self-hosted runner, that
    runner is dedicated to the `production` deploy, and the residual risk is recorded;
  - that environment secret is the single source of truth: no copy elsewhere (OD1);
  - an owner, an expiry and rotation in the exception register;
  - optionally a separate environment (e.g. `production-k0s`), limited to `main` and referenced
    only by the k0s/Firebase deploy workflow, so AWS deploy jobs cannot read these secrets
    [design].

  Residual risk: admins can change the environment, and a deleted environment comes back without
  protection (⚠️ R3.1.4); the alerts and settings comparison in layer 7 cover this. The exception
  covers **CI deploy credentials only**. Runtime credentials, such as a k0s autoscaler's AWS access to
  add or remove nodes, live in the cluster, not in GitHub; they follow layer 1 (no static keys, a
  role attached to the machine; ⚠️ not researched for k0s, G1).
- **Side paths:** Pulumi ESC, Pulumi Deployments and Serverless Dashboard providers reach AWS
  (📖 R4.4.9) outside the GitHub gate (⚠️ R4.4.9); not used for prod (⚠️ R4.6 #6).
- **Pinning:** workflow lockfile (`gh actions-lock`) or full SHA, enforced by the org policy "Require
  actions to be pinned to a full-length commit SHA" (availability on Team ⚠️); the lockfile does not pin reusable workflows, so
  the deploy workflow lives in the same repo (📖 R3.5.5; conclusion [design]).
- **CODEOWNERS** on `.github/`, `CLAUDE.md`, `CLAUDE.local.md`, `.claude/`, `.claude.json`, `.mcp.json`,
  `.husky/`, `.gitmodules`, `.ripgreprc`, `.devcontainer/` (📖 R3.2.8; list ⚠️ R6.5 #5, R6.3.11), plus
  `.npmrc` (registry redirection) [design], the policy packs, the SCP code and the
  catalogue file. This is the canonical L3 path list that layer 3 refers to. Not on it:
  `deploy-approvals/<stack>/`, owned by the stack's owners and the on-call group (OD8, OD9). The private plugin
  marketplace is a separate repo and needs its own ruleset and CODEOWNERS [design]. CI validates the file, because
  invalid lines are skipped silently (📖 R3.2.7).
- **No privileged triggers with untrusted code** (`pull_request_target`, `workflow_run` + checkout,
  📖 R3.5.4).
- **Agent review:** an independent agent (not the one that made the change) may post an automated
  review as an extra check; it never counts as an approval (GĐ-11).
- **Agents in CI:** `claude-code-action` with a custom GitHub App limited to Contents, Issues, Pull
  requests (📖 R1.7.8), whose own credentials are listed in the S2 inventory (⚠️ G19); Anthropic workload identity federation, not a personal OAuth token (📖 R1.7.6);
  `--restricted` and explicit `--tools` (D3; passing it through `claude_args` unverified, ⚠️ research
  6.9.4 Q5); a managed-settings file on the runner, which also guards against mods (📖 R1.5.6; for
  federation auth ⚠️); MCP set fixed by CI because `.mcp.json` loads without a prompt in `-p` runs
  (📖 R1.3.5); never `environment: production` (⚠️ R3.6 #4). Hosted runners give `sudo` (📖 R3.5.1),
  so with `Bash` in `--tools` the runner file is advisory (⚠️ R3.5.1, R3.6 #4).
- **App-opened PRs:** a required check set by a dedicated GitHub App, pinned as its source (layer 3), confirms at least one approval by a
  human who did not trigger the run; counting approvals is not enough, since the app's own approval
  might count (⚠️ R3.3.4, R3.7 A3; 📖 R3.2.5).
- **Required checks (S10):** from phase 1, secret scanning, dependency check, SAST (products: G4);
  from phase 2, IAM Access Analyzer `check-no-new-access` (📖 R2.8.1) and Pulumi policy packs
  (📖 R4.2.2). For Serverless stacks, Access Analyzer would check the IAM policies in the
  CloudFormation template that `serverless package` produces, against the deployed ones (⚠️ not
  researched); policy packs do not apply to them. Until phase 2, the only compensation for OD8 is
  the risk stop, which fires on every IAM change in the prod preview.

**Audit evidence.** Workflows and lockfile in git; audit-log events such as
`org.update_actions_secret`, `repo.set_workflow_permission_can_approve_pr`, `repository_ruleset.update`
(📖 R3.3.3, R3.5.6). An audit event for environment-secret changes was not researched (⚠️); the
settings comparison in layer 7 covers the S2 exception meanwhile. Check results per PR; secrets inventory (S2).

**Cost / value.** One-time migration to OIDC and pinned actions; slower action updates. Compliance
gets S2 and the same guardrails for agent and human code.

---

## Layer 6 — Data protection and prompt-injection defence

**Principle.** The design keeps PHI from reaching the coding agent (owner decision, research 1.9).
Some paths rely on process (below), so this is a target, not a guarantee. Other customer
personal data is outside that hard boundary ("not extended", research 5.8): the agent reads metadata
by default and may read such data case by case under GĐ-9. Real-data reads are approved, name one
tenant, are time-boxed, and need an agreement (BAA/DPA, partner contract) (GĐ-9). Everything read
from outside is untrusted. Non-prod is synthetic or masked (GĐ-14).

**On Papaya's stack**

- **Paths to PHI** (research 1.11.4 lists 17):
  - AWS stores: closed by identity, through `ProdReadMetadata` as the only standing prod role from
    phase 1 (existing broad read roles are removed) and the SCP from phase 2
    (layer 1); no Aurora credentials, no prod exec, no `lambda:InvokeFunction` for agent-usable roles
    [design; actions ⚠️ G13];
  - k0s logs/exec and GCP stores (L1, L11, L13): same principle, mechanism open (G1, G3);
  - tickets/chat via MCP, pasted text, internal admin pages, prod AI traces, fixtures, CI logs (L5,
    L8–L10, L12, L14): process and hygiene only;
  - logs redacted at source with raw payloads in a separate log group; alerts carry IDs, not payloads [design].
- **Real-data request** [design]: tenant, purpose, store, window, agreement; approved by the data owner
  and an approver ≠ requester; JIT data-read role, 1 h. At night the data owner is not on call: the
  on-call approver approves alone and the data owner reviews the grant the next working day. This
  applies to non-PHI and PHI alike; for PHI the reader is still a human without an agent. Per-tenant scoping through session tags
  (📖 R2.1.8) is unresolved, because tags come from user attributes (⚠️).
  - **PHI:** a human reads in a terminal without an agent (process rule, layer 1); the agent gets a
    redacted summary. This
    narrows GĐ-9 because the agent stays outside PHI scope (research 1.9) and Team is not shown as
    BAA-covered (⚠️ R1.11.3.4). Enterprise + BAA only for a separate environment if needed (research 1.9).
  - **Non-PHI personal data:** the agent may read it within the approved request (GĐ-9). Claim
    tables mix health, ID and bank data (research 1.11.4 L2), so a store that holds PHI is treated as
    PHI unless the agent reads a view or extract without PHI [design].
- **Partner-uploaded claim documents (A7b):** never in an agent session raw; reproduce with synthetic
  documents, or de-identify first [design]. The document is PHI and an injection vector (research
  1.11.4 L6).
- **Injection** (these lower frequency; layers 1 and 3 limit impact): Manual by default (sandboxed Bash runs without a prompt, layer 2); the auto-mode
  classifier missed 17 % of 52 real overeager actions and 5.7 % of 1,000 synthetic exfiltration
  attempts (📖 R6.3.5). Broad allowed domains such as `github.com` are a documented exfiltration path
  (📖 R6.3.7). The incident session has no WebFetch, likely no edit tools (layer 2), and runs outside
  the repo, but its Bash can still write locally and send data out through excluded
  commands (layer 2), including the SSO token cache; "no standing write, no PHI read" limits what
  the token opens, except during a JIT or data-read window (layer 2 mitigations). Shared knowledge
  goes in `CLAUDE.md` under review; auto memory is exempt from the protected-path rules unless `--restricted` (📖 R6.3.11, D3).
- **Tenants:** one tenant per data-read grant; a session that read one tenant's data does not post to
  shared places without review (⚠️ R6.5 #8, process). Logical separation in shared accounts is assumed
  (GĐ-3, unconfirmed).
- **Non-prod:** no prod copies (S11). A scan of non-prod stores runs at the start of phase 1 (tool:
  G4); a store not yet scanned follows the L3-data rule (GĐ-14: until cleaned, non-prod follows the GĐ-9 data-read rule). Cost: until scanned, that store is
  not part of the free loop.
- **Local stores:** transcripts and memory hold what the agent read (research 1.11.4); set
  `cleanupPeriodDays` (30 in the HIPAA sample, 📖 R5.5.4; what it deletes ⚠️).
- **Cross-border (Vietnam example):** processing data collected in Vietnam on a platform abroad is a
  transfer (📖 R5.4.5); agent flows, including employee names in logs and transcripts, update the
  transfer impact assessment (⚠️ R5.7 #4, needs Papaya legal).

**Audit evidence.** SCP/IAM text as the written access rule for sensitive data (📖 R5.4.3; ⚠️ R5.7 #5);
data-read requests and the data-read role's CloudTrail; planted-injection reports (layer 8); non-prod
scan results (S11).

**Cost / value.** Debugging with redacted and synthetic data; a request for the rare real-data read.
Compliance gets "minimum necessary" (📖 R1.11.1.8) enforced by IAM for AWS stores (fully from phase 2;
actions ⚠️ G13) and by process
elsewhere, and a record per exception (S9).

---

## Layer 7 — Observability, audit, incident response and break-glass

**Principle.** One tamper-evident evidence chain per prod change. One routed alert channel with a
named on-call, approvers included. Unapproved change is detected (drift, reconciliation). Break-glass
is approved before use, time-boxed and reconciled after.

**On Papaya's stack**

- **Audit stores:**
  - organization CloudTrail to a log-archive account with integrity validation (📖 R2.6.2, R2.6.4,
    R2.6.5); change records ≥ 6 years; raw-log retention for Papaya's compliance owner (⚠️ R5.7 #2).
    Data events only on PHI buckets, prod Lambda invoke and prod SQS (cost 📖 R2.6.3; selection
    ⚠️ R2.9 #5), which makes the archive
    PHI-bearing (⚠️ research 1.11.4 L15). CloudTrail Lake is closed to new customers (📖 R2.6.6);
  - GitHub org audit log kept 180 days, so exported (📖 R3.5.6);
  - alerts on `repository_ruleset.update`, `environment.update_protection_rule`,
    `environment.remove_protection_rule`, `environment.delete`, `protected_branch.policy_override`
    (📖 R3.5.6, R3.1.4; selection ⚠️ R3.6 #1). UI changes to the branch policy may leave no event, and a
    deleted `production` environment comes back unprotected (⚠️ R3.1.4): a job compares live settings
    with an expected copy (G8);
  - Aurora SQL is likely invisible to CloudTrail (⚠️ R2.7.1): Database Activity Streams, alerts on
    lost-record events (📖 R2.7.2; Serverless v2 ⚠️), stream treated as PHI (⚠️ R2.7.3);
  - Claude Code OTel without prompt content (layer 2).
- **Change record [design]:** keyed by commit SHA or JIT request ID; links PR, approvals, run ID,
  preview and CloudTrail events. Monthly reconciliation: every prod write event matches a record
  approved before apply (S3). Actor: `onBehalfOf.userId` where present, else session name plus
  directory lookup (📖 R2.5.1; ⚠️ R2.5.3).
- **Drift [design]:** its own role, trusted only from a `drift` environment on `main`; it can read
  prod secrets in state, which is noted (⚠️ R4.6 #2). Scheduled `pulumi preview --refresh
  --expect-no-changes` or `pulumi refresh --preview-only` (📖 R4.1.1, R4.3.1, R4.3.2). On a DIY S3
  backend, preview needs state-write permission (📖 R4.3.3); whether a refresh preview writes more
  than locks is open (⚠️ R4.6 #2, G14). So either the drift role gets state write (and the same
  trust care as the deploy role), or Pulumi Cloud drift detection is used (📖 R4.3.2, Pro+). The
  latter runs on Pulumi Deployments, which holds credentials to prod, so it re-opens a side path that
  layer 5 excludes and needs the same trust narrowing and audit (📖 R4.4.9; ⚠️ R4.6 #6). CloudFormation
  drift detection, explicitly set properties only (📖 R4.4.6). No auto-remediation: it is an unreviewed
  `pulumi up --refresh` (📖 R4.3.2). Each finding gets an actor and a ticket.
- **On-call:** phase 1 delivers the named approver schedule (primary + backup engineers, 24/7), as
  decided in framing round 1, and, because of OD7, a minimal incident-responder schedule; the
  latter extends that decision. The primary approves; the backup steps in only if the primary is
  unavailable (OD2). On-call approvers only approve during their shift; the fix is written by an
  incident responder (OD7). Alert routing and the
  rest of on-call follow in phase 2 (tools: G5); in phase 1 the responder calls the approver by phone from the published schedule.
- **Break-glass = JIT fallback** [design unless marked]:

  | Step | Rule |
  |---|---|
  | When | Only during an incident (Options §9 Q2), when the PR path cannot be used: operation not in IaC and no runbook; GitHub/Actions down; pipeline broken. The approver refuses JIT for anything expressible in IaC while the pipeline works, and records why. Outside incidents, an operation not in IaC waits for IaC or a runbook. |
  | Request | Command list, scope, reason, incident link, in a channel that does not depend on GitHub. |
  | Approval | On-call approver ≠ requester, before the grant (Options §4b; OD7; backup rule OD2). |
  | Grant | `InfraOperator-<service>`; role session 1 h (📖 R2.1.4). Deleting the assignment likely stops only new sessions (⚠️ R2.4.2, R2.9 #3), so the real window can approach 2 h; ending the portal session does not end role sessions (📖 R2.4.3). An immediate stop needs the revocation SCP, which must keep the user blocked for at least 12 h (📖 R2.4.4). Applying it is a management-account change held by the L3 owner team only, and no night-time path for it is designed yet (⚠️ G20): until one exists, a misused grant may run to the end of its window. Candidate: a pre-approved revocation runbook for one named L3 owner reachable by phone, or an org-wide `aws:TokenIssueTime` Deny as kill switch (⚠️ R2.9 #3). |
  | Execution | The grant goes to the requester (the incident responder), who types the commands; no agent in that terminal (D2). D2 said the on-call person runs them; OD7 moves that to the responder, since on-call engineers only approve. |
  | After | A job compares CloudTrail writes in the window with the list; a codify PR within a fixed deadline (as soon as GitHub is back); drift detection until it merges. |
  | Identity Center outage | Emergency SAML federation to roles, built and tested in advance (📖 R2.1.11; ⚠️ R2.9 #2); no user mapped until an approved activation, which is alerted. |

  **Example request (illustrative command ⚠️):** "INC-123, ECS service `claims-api`, Actions outage. Run
  `aws ecs update-service --cluster <prod-cluster> --service <svc> --force-new-deployment`. Scope
  `InfraOperator-claims`, 1 h."

  **Metrics** (Options §7; starting thresholds ⚠️ to calibrate): JIT used where a PR was possible
  (review at 1); writes outside the list (review at 1); codify PRs late (review at 1); grants per
  month and share of incidents needing non-IaC operations (review above about 25 %, a value new in
  this draft). On a breach,
  make the PR lane faster or add a runbook; do not widen JIT.
- **Roadmap:** runbooks for repeated non-IaC operations, if SSM Automation's approval step meets three
  conditions (Options §2; outside 02-research, G6); break-glass from an environment without the agent
  (D2, ⚠️).

**Audit evidence.** Validated CloudTrail; exported GitHub audit log; change records and monthly
reconciliation (S3, S8 ≤ 30 min); JIT requests, reconciliations, codify PRs; drift tickets; on-call
schedule and approval waits (S7); monthly report of cross-domain approvals by on-call group members
on PRs without the `incident` label (OD9).

**Cost / value.** The incident lane is slower than direct access (estimated 11–46 vs 2–20 min,
Options §6), and JIT needs a written command list. Compliance gets approval before apply even in
incidents, plus detection.

---

## Layer 8 — Governance and rollout

**Principle.** Every control has an owner, a metric and a review date. Policies are files changed by
PR. Access is never removed before its replacement works. Controls are tested against realistic
attacks.

**On Papaya's stack**

- **Owners:** DevSecOps (framework, managed settings, catalogue, metrics); a platform team or named
  engineers (deploy workflows, rulesets, pipelines; whether Papaya has a platform team is unknown ⚠️); Compliance (evidence review, supplier register, Statement of
  Applicability); engineering leads (decide CODEOWNERS content; changes to it are approved by the L3 owner team); engineering management (on-call schedule).
- **Policy as code:** catalogue, SCPs, trust policies, CODEOWNERS and workflows are files under
  CODEOWNERS. Settings that live outside files are kept as an expected copy in git and compared with
  the live state: GitHub settings (⚠️ R3.6 #1; G8) and Claude managed settings, which are edited in
  the admin console (📖 R1.1.5; comparison method in layer 2). Few GitHub admins and Claude org
  Owners, reviewed quarterly.
- **Metrics:** S1–S11 exactly as in framing §5; this framework adds the JIT metrics (layer 7) and the
  prompt metrics (layer 2). S2 and S5 have caveats (OD1; layer 2).
- **Rollout** (≈ 90 days, GĐ-12 unconfirmed). Framing Q8 (round 1): (1) remove long-lived CI credentials,
  (2) narrow standing prod access, (3) MCP/plugin catalogue; the on-call approver list before or with (2).

  | Phase | Days | Items, in order |
  |---|---|---|
  | 1 | 0–30 | Measure the incident PR lane on one service (first task once that service has an OIDC deploy workflow, Options §9), including the prompt for each `aws` read, which the allowlist excludes (layer 2). Non-prod data scan. OIDC for deploy workflows; remove long-lived keys (except k0s/Firebase under OD1); move laptop deploys to CI (GĐ-10, unconfirmed). Rulesets, CODEOWNERS and its validation check; the required-check app, before any agent workflow may open PRs (G19); remove human write kubeconfigs for prod k0s (interim, layer 1); phase-1 S10 checks (secret scanning, dependency check, SAST; Access Analyzer and policy packs follow in phase 2, so until then OD8 relies on the risk stop alone). Minimal real-data read flow (request, 1-h data-read role, approver ≠ requester, data-owner review afterwards; layer 6). `ProdReadMetadata` becomes the only standing prod role (existing broad prod read roles removed only once that flow works, layer 8 principle); start moving secrets to runtime resolution and redacting logs at source, service by service. On-call approver schedule and a minimal incident-responder schedule (named, 24/7), because on-call approvers only approve (OD7); minimal JIT fallback **with** per-grant CloudTrail comparison and a drift check of the stacks it touched (by hand until automated: a temporary deviation from D2, which asks for a drift job). Phase-1 JIT has no immediate stop: deleting the assignment ends new sessions only, so a grant can run up to about 2 h (⚠️ R2.9 #3); the revocation Deny SCP is deployed with the other SCPs in phase 2 (layer 7); risk stop in the deploy job (the policy-finding trigger works from phase 2); k0s/Firebase deploy credentials moved to `production` environment secrets; **then** remove standing prod write. MCP/plugin catalogue v1. Managed settings, phase-1 subset: `defaultMode` (D1 said "immediately"), `disableBypassPermissionsMode`, the keys that enforce the catalogue (`strictKnownMarketplaces`, `blockedMarketplaces`, `disableSideloadFlags`, `allowedMcpServers` + `allowManagedMcpServersOnly`, `disableClaudeAiConnectors`), the OTel exporter with content flags `0` (no prompts added; it is the evidence for D1's auto-mode metric and the plugin events of layer 4), and `requiredMinimumVersion` (phase-1 floor: the higher of 2.1.248, needed by `--restricted` (D3) and above the 2.1.179 plugin-pin fix, and the latest fixed high advisory at rollout; 2.1.285 when `allowedProviders` arrives in phase 2). Also the read-only `permissions.allow` list, kept with Manual mode as D1 paired them (OD7b). |
  | 2 | 30–60 | Rest of the managed baseline and verification of the SSM option (moved here by the owner, OD4). SCPs: data-plane deny, Lambda update deny, revocation Deny, protection of the org trail, outside-org write deny; scheduled drift detection; automated JIT reconciliation; audit-log export, change records, monthly reconciliation; Access Analyzer and policy-pack checks; Aurora activity streams; emergency federation for Identity Center outages; alert routing and the rest of on-call. |
  | 3 | 60–90 | Planted-injection test on the real configuration (📖 R6.1.1, R6.1.5; ⚠️ R6.5 #12); a deliberate trade-off: auto mode runs from day 1 (D1) without this data, and until then only D1's other fallback triggers apply; auto-mode non-prod environment (D1 c); separate OS user or container for prod-reading sessions; first ISO evidence pack; 90-day review of D1–D3. |

- **Phase-1 load [design; effort not estimated ⚠️]:** phase 1 holds about 20 items for 1–2 DevSecOps
  people (GĐ-1) plus the owners of deploy workflows, within ~90 days overall (GĐ-12, unconfirmed). This is
  the main rollout risk. Hard prerequisites before standing prod write is removed: OIDC deploys from
  CI, rulesets + CODEOWNERS, the on-call approver and responder schedules, minimal JIT, the risk
  stop, and the k0s/Firebase secret move (a repository secret would be standing prod write, layer 5).
  Items that may slip to phase 2 without blocking that step: catalogue v1 (a deviation from framing
  Q8, which ranked it third for the first 30 days; needs owner agreement) together with the
  managed-settings keys that enforce it, and log redaction and secret moves beyond the first
  services. Not allowed to slip: `defaultMode`, the read-only allowlist (D1 "immediately", OD7b) and
  the OTel exporter (evidence for D1).
  If a hard prerequisite slips, standing prod write stays until it lands, and the slip is reported.
  Likewise, broad read roles stay until the minimal real-data read flow works.

- **Exceptions:** a ticket with owner, reason and expiry.
- **Standards mapping** (⚠️ R5.6; HIPAA and Vietnam text 📖 R5.2, R5.4; ISO IDs recalled, not read,
  ⚠️ R5.1):

  | Layers | ISO 27001:2022 Annex A (⚠️) | HIPAA Security Rule | Vietnam example |
  |---|---|---|---|
  | 1, 6 access | 5.15–5.18, 8.2, 8.3, 8.5 | 164.312(a)(2)(i); 164.308(a)(3)–(4) | Decree 356 Art. 4(2) |
  | 3, 5 change | 8.32, 8.31, 8.25, 5.3 | 164.312(c); 164.316(b) | — |
  | 7 logging, break-glass | 8.15, 8.16, 5.28 | 164.312(b); 164.308(a)(1)(ii)(D); 164.312(a)(2)(ii) (mapping ⚠️ R5.7 #3) | Law 91 Art. 23 72 h notice (📖 R5.4.6; mapping ⚠️, new in this draft) |
  | 4 suppliers | 5.19–5.23 | 164.308(b), 164.314(a) | Law 91 Art. 20 |

  "A named human approves" is Papaya's chosen way to meet these controls, not a literal requirement
  (⚠️ R5.7 #1).
- **Out of scope:** security of the production AI agents (A7a); noted as a follow-up.

**Audit evidence.** Git history of policy files; monthly metrics; 90-day review minutes; exception
register; planted-injection reports.

**Cost / value.** Steady, small overhead for DevSecOps and the owners of deploy workflows. Compliance gets a managed system
with owners and review dates.

---

## Gaps (not covered, or only as an open item, in `work/02-research.md`)

| # | Gap | Layers |
|---|---|---|
| G1 | k0s: authentication, RBAC, audit logging, kubeconfig issuance (GĐ-4); break-glass when Actions is down | 1, 3, 6, 7 |
| G2 | Firebase Hosting deploy from CI without a stored token; break-glass when Actions is down | 1, 5, 7 |
| G3 | Human and agent access to GCP (roles, data access) | 1, 6 |
| G4 | Secret scanning, dependency check, SAST, non-prod data scanning on the Team plan | 5, 6 |
| G5 | Paging and alert routing; approving a PR from a phone | 7 |
| G6 | SSM Automation `aws:approve` (read in `work/03-options.md` §2, not in 02-research) | 7 |
| G7 | GitHub Actions log and artifact retention, and export | 3, 7 |
| G8 | Rulesets and environment settings through the API | 7, 8 |
| G9 | How Linear and Slack MCP servers authenticate | 4, 6 |
| G10 | OIDC subject customisation (`job_workflow_ref`) on GitHub Team | 1 |
| G11 | Closing provider/login bypasses on laptops without MDM | 2 |
| G12 | `pulumi up` flag reference for the prod allowlist | 3 |
| G13 | IAM actions for every data-plane read (S3, SQS, Step Functions, Secrets Manager, RDS, ECS Exec, Lambda invoke) | 1, 6 |
| G14 | Which state writes a Pulumi refresh preview needs on a DIY S3 backend | 3, 7 |
| G15 | Restricting a self-hosted runner to one workflow in a monorepo; just-in-time runners | 5 |
| G16 | Managing GitHub team membership as code; audit event for a membership change | 3, 7 |
| G17 | Who forms the L3 owner team and how many people (GĐ-1: never a single reviewer) | 3, 8 |
| G18 | Reading the live values of server-managed settings (API or local cache) to compare with git | 2, 8 |
| G19 | Required-check app and CI-agent app: review-event triggers, source pinning against same-name checks, hosting, private-key storage and whether those keys count against S2 | 3, 5 |
| G20 | Emergency revocation at night: who can apply the revocation Deny SCP (management account) within minutes; `aws:TokenIssueTime` kill switch (⚠️ R2.9 #3) | 1, 7 |

Open checks from `work/03-options.md` §8 remain open.

## Owner decisions (2026-11-09)

The owner answered the open questions of draft v3. English rendering; the original Vietnamese
answers are recorded in `work/session-log.md`.

| # | Question | Decision |
|---|---|---|
| OD1 | Exception to S2 = 0 for k0s/Firebase deploy credentials? | Yes, provided each credential has a single source of truth. (The first reason given, continuous scale-in/scale-out, concerns runtime credentials; OD6 narrowed the scope.) |
| OD2 | L3: must one approver be from the platform team? | Not necessarily; one approval procedure is agreed for all engineers, and the on-call engineer is enough. Clarified in follow-ups: every change involves two people, one who makes it and one who approves; the on-call backup only replaces an unavailable primary. Asked whether L3 should need more approvers than L2, the owner chose "L3 = 1 approver at all times"; in the agent's framing of that option, the approver must own the path. |
| OD3 | `CLAUDE.md` changes: L2 or L3? | L3, because the workflow must be consistent across the whole team. |
| OD4 | Move the rest of the managed baseline and the SSM check to phase 2? | Yes. |
| OD5 | "An agent does not approve PRs" only a process rule? | It is a rule: the PR approver is always an engineer, never an agent. |
| OD6 | Scope of OD1: CI deploy credentials only, or also runtime scaling credentials? | CI deploy credentials (k0s kubeconfig/token, Firebase token in GitHub secrets) only, until it is checked whether k0s and Firebase can use OIDC. |
| OD7 | (a) If the on-call engineer writes an L3 fix, who approves? (b) Keep the read-only allowlist in phase 1? | (a) "While on call, never change the process"; clarified: on-call engineers only approve, and fixes are written by another engineer (the incident responder), so the approver is never the author. (b) Yes, as proposed. |
| OD8 | IAM/network/stateful changes inside a domain file: who approves the risk stop? | The stack's owners (may be the first approver); always two people. The L3 owner team keeps only the real L3 paths; Access Analyzer and policy packs compensate. |
| OD9 | How can one on-call primary approve any path at night? | The on-call approver group co-owns every deployable path; one primary + one backup. Normal-day domain review is a process rule with a monthly check. |
| OD10 | A PR touching files of several domain teams: split, or one approval? | One approval is enough (two-person rule kept); domain review on such PRs is a recommendation, counted in the monthly report. |
| OD11 | Risk stop when the first approver is unavailable: may another owner of the stack approve? | Yes; it makes three people and is recorded as a deviation. |
| OD12 | `sandbox.autoAllowBashIfSandboxed`: `true` or `false`? | Keep `true` (fewer prompts, relies on the sandbox, which arrives in phase 2). |
| OD13 | Confirm three agent readings: (1) OD8, who opens and approves the risk-stop approval PR; (2) OD9, scope of the on-call group; (3) L3-JIT, does the on-call approver count as service owner? | Confirmed: (1) the original author opens it and the first approver approves it; (2) the on-call group does not co-own process-defining paths or the SCP stack, which only the L3 owner team approves; (3) yes. |
