# Framework: coding agents for DevSecOps at Papaya

> Status: v3, approved by the author (the owner of this submission, not Papaya) 2026-11-09; detail, gaps and decisions moved to the [appendix](07-framework-appendix.md) (OD52) · Updated: 2026-11-09
> Audience: a panel of Engineering and Compliance. Each layer ends with what it costs engineers and
> what it gives Compliance.

## How to read this

Start with the [executive brief](00-executive-brief.md) if you have ten minutes. §1 is the
decision on one page, with the choices left to Papaya; §2 is how the agents are used for DevSecOps
work. Then eight layers. Each has a **Principle** (tool-independent), **On Papaya's stack** (Pulumi,
Serverless Framework, GitHub Actions, AWS, GCP, k0s, Claude Code) and **Audit evidence** (records an
auditor can test without asking anyone). Copy-paste detail belongs in `examples/`.

| Marker | Meaning |
|---|---|
| 📖 R*x.y* | Documented. R*x.y* is a ✅/📖 row in `work/02-research.md` that quotes or links the official page (a few rows cite vendor blogs, bulletins or example files instead, e.g. R2.4.1b, R6.3.5, R5.5.4). |
| ⚠️ R*x.y* | Inference, open question or "What this means for Papaya" conclusion in the research (sections 1.8, 2.9, 3.6, 3.7, 4.6, 5.6, 5.7, 6.5), or the ⚠️ part of a mixed row. Reasoned, not documented. |
| ⚠️ | Not verified at all, e.g. an illustrative command. |
| [design] | My proposal, built from documented parts, untested. Treat as ⚠️. |
| 📖 + inline link | Official page linked in place, or in the cited examples finding / E-row: facts found while writing `examples/` (2026-11-09), after the research file. |
| 📖 R9.*x* | Documentation check made for the review fixes (OD22–OD30), recorded with links in `work/09-fix-research.md`. |

This is a design without access to Papaya's systems; nothing was run against them. The files in
[`examples/`](../examples/README.md) were checked locally (✅, commands and output there), and
"examples finding n" / "E*n*" point to that file.
Codes (OD-n decisions, GĐ-n assumptions, S-n success criteria, G-n gaps, D1–D3, P/A-n problems)
are defined in the [executive brief](00-executive-brief.md#codes-used-in-the-other-documents); gaps
and decisions are listed in the [appendix](07-framework-appendix.md). The text states the design
as it is; a code in brackets only says which decision or source it comes from, and can be skipped.
References to the working notes in `work/` ("Options §n", "research n") remain only where they back
a number or an open point. "Owner" means the author of this submission, not Papaya; the choices
left to Papaya are in §1.

---

## 1. The decision in one page

**Who decided.** This is a proposal by the author of this submission. Where the documents say
"owner" or cite an owner decision (OD-n), that is the author's design decision taken while writing
it, not a sign-off by Papaya. The choices that are Papaya's to make are in the last table below.

**The disagreement is narrower than it looks.** Engineering wants Claude Code to talk to AWS
directly; Compliance wants nothing to change in production without a named person who reviewed and
approved it. Reading metadata and working in non-prod are outside Compliance's sentence. The
conflict is only about **writes to production**, and about real customer data, which has its own
rules (layer 6).

**The answer:**

1. Every production change is a pull request: approved by a person who owns the changed files and
   did not write the change, then applied by the pipeline. Incidents use the same path, with a
   24/7 on-call approver.
2. Only when that path cannot be used during an incident, a person gets a one-hour approved grant
   and types an approved list of commands in a terminal without an agent.
3. Nobody, person or agent, keeps standing write access to production, and the pipeline uses no
   stored cloud keys (a few exceptions, each with an owner and an expiry).

| Engineering gets | Compliance gets |
|---|---|
| An agent that works freely in non-prod and reads production metadata | Approval before every production change, by a named person who is not the author, enforced by GitHub and AWS, not by the agent |
| One approval for most changes, same-day shipping, an approver within 15 minutes at night | One evidence record per change, kept six years in locked storage |
| Agent help with incidents, risky-deploy reviews, dependency fixes and audits (§2) | Agent controls as a second layer, never the control of record |
| **Costs:** a slower incident lane; a confirmation for each cloud command; from phase 2, pushing and opening pull requests yourself; raw logs only after masking; night duty | **Not delivered:** a technical stop on an agent approving through its engineer's login; prevention (not just logging) of administrators editing the gate; full approval of the break-glass path, which approves a command list rather than the applied change |

**Decisions Papaya must take** (the design works either way; the recommendation is the author's):

| Decision | Recommendation | Where |
|---|---|---|
| Accept break-glass as partly meeting "approved before applied" | Accept, with its metrics reviewed monthly; Compliance signs | layer 7 |
| One approver for high-risk changes in service code, or two | One, plus the risk stop; two on the files that define the process | layer 3 |
| GitHub Team or Enterprise Cloud | Enterprise Cloud in phase 2 if up to about 100 users: identity-linked approvals, prod diff before apply | layer 3 |
| GitHub secret-scanning and code-scanning licences | At least secret scanning with push protection | layer 5 |
| Stored deploy credentials for k0s, Firebase, Expo | Accept with an expiry until keyless login works | layer 5 |
| Staffing of phase 1 | Two DevSecOps people and one platform engineer for about 45 days | rollout plan |
| A 24/7 rota of approvers and responders | Yes; two people awake for a night incident | layer 7 |
| Auto mode on laptops | Allowed, measured, with a switch to turn it off | layer 2 |
| An isolated runtime for the agent (own AWS role and GitHub token, not the engineer's) | Evaluate in the phase-2 pilot; adopt if it restores the agent's push and PRs and costs less than the friction it removes | layer 2 |
| The approval-gate app in phase 1, or a lean first version | Build the app: it prevents; the lean version (GitHub's own rules plus a nightly check of the same rules) only detects, and is acceptable only if Compliance accepts it in writing | rollout plan |
| Whether HIPAA applies; Papaya's role per insurer (controller or processor) | Legal counsel | compliance register |

Sources and detail: the limits in §1a, the research rows in `work/02-research.md` and
`work/09-fix-research.md`, the author's decisions in the [appendix](07-framework-appendix.md).

### 1a. Limits and trade-offs, in detail

The chosen approach is called "A + D2'" in the working notes: option A, the PR path
for every prod change, plus D2', a narrow JIT fallback. The codes used from here on are explained
in "How to read this". Its limits, each argued with its sources in [appendix A](07-framework-appendix.md#a-limits-and-trade-offs-in-detail):

- the fallback meets "approved before applied" only partly (a command list, not the applied
  change), and stays narrow only if most incidents can be written as IaC; layer 7 measures it;
- on GitHub Team nobody sees the prod diff before apply; risky prod diffs stop for an owner's look
  at the prod preview instead (layer 3);
- admins can edit the gate, and so can an admin's agent: logged, not prevented;
- "an agent never approves" rests on policy, training and deny rules that are hygiene; "named" means
  a GitHub login that a register maps to a person (layer 1);
- an on-call approver counts for another team's file only in an open incident, checked by the
  approval-gate app; a night incident needs two people awake (layer 3);
- one approver for most high-risk changes; two on the process paths (layer 3);
- k0s and Firebase have weaker controls (G1, G2);
- the approval-gate app blocks every merge when it is down, and is the longest phase-1 item;
- whether HIPAA applies is a legal question.
**Cross-cutting rules:**

1. **The boundary is IAM and the CI gate.** Server-managed settings are "a client-side control, not
   a security boundary" (📖 R1.1.7); local admins can edit endpoint files (📖 R1.1.8).
2. **Assume prompt injection succeeds:** neither OWASP nor NIST knows a full prevention (📖 R6.1.1, R6.1.2).
3. **Friction where damage is large, none where it is small**, measured, with a time-boxed escape.
4. **Evidence by construction:** the path produces the records.

### Roles

| Role | Rule |
|---|---|
| Author (engineer + their agent) | Never approves own change; GitHub blocks PR authors from approving (📖 R3.3.1). |
| Approver | Always an engineer, never an agent (owner rule, OD5). Named in CODEOWNERS; ≠ author, ≠ last pusher (📖 R3.2.3); for an app-opened PR, ≠ the person who triggered it (⚠️ R3.3.4, layer 5). Their GitHub account is in the login register (OD25). Process paths need two (OD26). |
| Incident responder | Engineer who diagnoses and writes the fix or the JIT request. Never the on-call approver of the same shift (OD7). |
| On-call approver | Engineer on the on-call schedule, primary + backup, 24/7; wait ≤ 15 min (S7). Approves another team's file only for a PR linked to an open incident while on shift, checked by the approval-gate app (OD27). While on call they only approve: they write no fix and file no JIT request, so the approver is always distinct from the author (OD7). The primary approves; the backup replaces an unavailable primary (OD2). No platform-team membership is required; all engineers follow one agreed approval procedure (OD2). |
| Data owner [design] | A Papaya employee named for one insurer tenant (for example the lead of that insurer's account or operations), not the insurer's own staff (OD56): approving needs a GitHub account in the login register and the Linear request flow, and the insurer's contract governs what Papaya tells it, not who approves inside Papaya. Members of the tenant's `data-owners-<tenant>` team, with read access to the repository only. Co-approves real-data reads and data fixes of that tenant, or reviews a night-time one the next working day (layers 3 and 6). |
| Control owner | DevSecOps (1–2 people, GĐ-1); owns policies and metrics; not the only approver. |
| L3 owner team | Owns the process-defining L3 paths and the SCP stack (layer 3); composition open (G17). |

---

## 2. Agent-assisted DevSecOps workflows

The layers below say what agents may not do. This section says what Papaya's engineers use them
for in DevSecOps work, inside those limits [design]. Each workflow names the session it runs in
(layer 2), the identity it uses (layer 1), the skill that encodes it (internal plugin
`devsecops-guardrails`, examples E9), its output, the person accountable, and the metric that shows
whether it helps.

| Workflow | Session and identity | Skill / tool | Output | Accountable | Value metric |
|---|---|---|---|---|---|
| **Ship an infrastructure change** | Daily development; non-prod roles + `ProdReadMetadata` | `prod-change` | IaC change, non-prod preview, PR text; the engineer opens the PR | Author; approver | PR to prod same day (S4) |
| **Triage an alert or incident** | Incident analysis: `--restricted`, read-only tools, scratch directory; `ProdReadMetadata` | `incident-triage` | Likely cause, smallest fix as a PR or a JIT command list, timeline draft | Incident responder | Time from page to fix PR (S7) |
| **Explain a stopped deploy** | Daily development, or the CI agent on the approval PR | `risk-summary-explainer` | Plain-language comment on `deploy-approvals/<stack>/`: what each stopped operation does, what is irreversible, what the summary cannot show | The approver decides | Approval wait on risk-stop PRs |
| **Review a PR for security** | CI agent, its own GitHub App token, never `production` (layer 5) | `claude-code-action` with the review prompt, read-only tools, no MCP (examples E18) | Review comments on every PR touching infrastructure; never an approval (OD5, OD22) | The human approver | Findings accepted per month |
| **Fix a vulnerable dependency or image** | CI agent from a Dependabot alert or an ECR scan finding (layer 5) | `dependency-fix` | One small PR per advisory, tests run, `pr-size` check passed | Owners of the changed files | Time to fix high and critical findings |
| **Codify after break-glass or drift** | Daily development, after the JIT window or a drift finding (layer 7) | `prod-change` | The codify PR that brings IaC in line with what was changed by hand | Incident responder | Late codify PRs (JIT metric) |
| **Prepare a catalogue review** | Daily development on the marketplace repository | — | Draft review record for a new MCP server or plugin (reviews/, examples E9) | Two L3 owner team members | Requests decided in ≤ 5 days (S6) |
| **Answer an auditor's question** | Daily development with read access to the evidence bucket (no write) | — | The change record of a sampled change from PR, run log, risk summary and CloudTrail | Compliance | Evidence shown in ≤ 30 min (S8) |

Shared context that makes these work, all in the monorepo and reviewed as L3 paths:

- **A shared `CLAUDE.md`** at the repository root: how production changes, the Pulumi and
  Serverless conventions, logging rules, the data rule (template: examples
  `claude/repo-templates/CLAUDE.md`).
- **A pull request template** that records which parts an agent wrote, the expected prod impact,
  the data touched and the rollback (examples `github/pull_request_template.md`). It makes the
  reviewer read agent-written code as a stranger's code.
- **The skills above** in the internal plugin, pinned and reviewed like any catalogue entry (OD26).

What stays manual on purpose: approving, running anything in a JIT window, deciding a data-read
request, and changing the gate itself.

**Measuring the value.** Papaya's current numbers are unknown, so each metric gets a baseline in
the first 30 days (from GitHub, the paging tool and the scanners, before the workflow is switched
on) and a target agreed at the final review (rollout 3.5) [design]. A workflow whose metric does
not improve over its baseline by then is dropped or changed, so that the agent's place in the
process is earned, not assumed:

| Metric | Source | Baseline | Target |
|---|---|---|---|
| PR to prod, median (ship a change) | GitHub, deploy runs | first 30 days | same working day (S4) |
| Page to fix PR, median (incident triage) | paging tool, PR timestamps | first 30 days | lower than baseline |
| Approval wait on risk-stop PRs (explainer) | `deploy-approvals/` PRs | first 30 days | ≤ 1 h in working hours |
| Security review comments accepted per month (review) | PR review threads | — (new) | reviewed at the final review; turned off if noise |
| Days to fix high and critical findings (dependency fix) | Dependabot, ECR scans | first 30 days | lower than baseline |
| Late codify PRs (codify) | JIT records | — (new) | 0 |

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
  - an agent never approves PRs: an owner rule (OD5), enforced on laptops by policy, training and
    managed deny rules for `Bash(gh pr review *)` and `Bash(gh api *reviews*)` plus
    `Read(~/.config/gh/**)` from phase 1 (OD25; valid patterns, not a boundary, 📖 R9.4.1).
    GitHub blocks self-approval only. The auto-mode default block list
    excerpt read names "approving Claude's own pull request" (📖 R6.3.3); whether approving
    someone else's PR is blocked is unverified (⚠️), and the list
    applies only in auto mode. No detection was found (⚠️; `actor_is_agent` in the audit log has no
    documented meaning, R3.5.6).
- **IAM Identity Center permission sets** (📖 R2.1.1) [design names]:
  - `ProdReadMetadata`: metrics, redacted log groups, configuration; no data-plane read on claim
    stores; 1 h session, the minimum (📖 R2.1.4). Some "metadata" reads (mostly ⚠️) return configuration or
    secrets, so `Resource: "*"` only for a reviewed action list (examples E6, findings 11, 12). Until a service's logs are redacted at source
    and masked (layer 6, OD28), it gets that service's metrics only. Lambda configuration can hold secrets resolved by
    Serverless in plain text (⚠️ R4.4.7), so configuration reads are allowed per service only after
    its secrets move to runtime resolution (⚠️ R4.6 #7). Cost: until then the agent reads
    timeout/memory from the IaC code;
  - `NonProdDeveloper`: broad, non-prod accounts only;
  - `InfraOperator-<service>`: assigned only by the JIT flow's receiver (layer 7, OD33) after its
    pre-grant check (examples E16), on the documented APIs `CreateAccountAssignment` /
    `DeleteAccountAssignment` (📖 R2.4.2). A partner product or the TEAM sample (📖 R2.4.1,
    R2.4.1b) can replace the receiver only if it enforces the same checks before the grant;
  - no standing prod-write permission set.
- **SCPs on the prod OU** [design] (SCPs cap member-account principals, 📖 R2.3.1, R2.3.2):
  deny data-plane reads on claim stores except application roles and the approved data-read role
  (action list incomplete, ⚠️ G13); deny direct Lambda code and configuration updates except
  CloudFormation deployment roles, the Pulumi deploy role and JIT roles, which closes `serverless
  deploy function` (📖 R4.4.4); a pre-deployed revocation Deny (📖 R2.4.4) and a deny on trail
  changes; only the IAM stack's own role (environment `production-iam`) may create or change the
  SCP-exempt roles, while domain deploy roles create only `svc-*` roles under a fixed permissions
  boundary (OD19, OD22; examples E4b); every action of `OrganizationAccountAccessRole` denied in
  the prod OU (OD23). No SCP applies to the management account (📖 R2.3.4), so whatever deploys
  SCPs there is the most sensitive role (L3 path, L3 owner team only, OD13). Statement by
  statement: [appendix B](07-framework-appendix.md#b-scps-on-the-prod-ou).
- **GitHub identity (OD25).** An approval proves a GitHub account; Compliance needs a named person
  [design unless marked]:
  - the organization requires two-factor authentication (📖 R9.1.1; the page names no plan, so
    ⚠️ check the setting in Papaya's Team organization);
  - a login register maps every member's GitHub login to an employee, fed by HR joiners and
    leavers; a leaver is removed from the organization on the last day; reviewed quarterly (C-03);
  - outside collaborators get no write access to the monorepo; classic personal access tokens are
    restricted and fine-grained tokens need approval and a maximum lifetime (📖 R9.1.12; plan not
    stated ⚠️);
  - SAML SSO, which would tie the login to the identity provider, needs Enterprise Cloud
    (📖 R9.1.2); see "GitHub plan" in layer 3.
- **Who administers the administrators (OD23) [design unless marked].** Whoever administers IAM
  Identity Center can assign themselves any permission set. So permission sets and assignments are
  code in an identity stack (L3 path) applied from CI; the JIT receiver is the only other writer;
  any other Identity Center change alerts (📖 R9.2.2); daily administration runs from a delegated
  administrator account (📖 R9.2.3); the management account has no workloads and a named group of
  at least two L3 owners with hardware MFA; member-account root credentials are removed
  (📖 R9.2.5). Detail: [appendix C](07-framework-appendix.md#c-who-administers-the-administrators).
- **Sessions/MFA:** portal session length set on purpose; an IdP session can extend it silently
  (📖 R2.1.5, R2.1.6). MFA lives in the external IdP if one is used (📖 R2.1.7).
- **CI → AWS:** GitHub OIDC, no stored keys (📖 R3.4.1). The prod role trusts only the `production`
  environment of the monorepo, in its `sub` format (📖 R3.4.3, R3.4.4; immutable format assumed,
  ⚠️ R3.7 A2), ideally customised with the deploy workflow's `job_workflow_ref` (📖 R3.4.5; on Team ⚠️ G10).
- **GCP, Firebase and k0s (OD36, OD24) [design unless marked]:** the same principles with each
  platform's own mechanism ([appendix D](07-framework-appendix.md#d-gcp-firebase-and-k0s-identity)):
  - CI → GCP through Workload Identity Federation, limited to the monorepo and the `production`
    subject; people get a read-metadata role and time-bound Privileged Access Manager grants approved
    by on-call (📖 R9.6.1); Data Access logs on for Vertex AI and partner-document buckets; Papaya
    confirms with Google that its Vertex use is BAA-covered before PHI goes there (📖 R9.6.4);
  - Firebase Hosting holds no PHI; its deploy key is an environment secret until a WIF spike
    removes it; previews come from non-prod only;
  - k0s: people move from kubeconfigs to OIDC (outside k0s support, 📖 R9.6.9) with one sealed
    break-glass certificate; CI deploys with a namespaced, time-limited ServiceAccount token that
    cannot read Secrets, exec, read logs or change RBAC (examples E11); target: the API server
    trusts GitHub OIDC directly.
**Audit evidence.** Identity Center assignment export (S1), CloudTrail grant events per JIT request, SCP and trust-policy code, Access Analyzer results from phase 2, and a quarterly access review; full register: [04-compliance-mapping.md](04-compliance-mapping.md#register).

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
- **Baseline** (template: Anthropic's `settings-hipaa.json`, 📖 R5.5.4). All keys 📖 at the row cited. Only the phase-1 subset ([rollout plan](03-rollout-plan.md) item 1.18) ships first; the other keys (sandbox, `allowManagedHooksOnly`, most credential denies, `allowManagedPermissionRulesOnly`, `allowedProviders`, `forceLoginOrgUUID`, the `ask` rule for WebFetch, and the other deny rules) arrive in phase 2 (OD4). The `ask` rules for `aws`, `pulumi` and `serverless` ship in phase 1 (OD43):

  | Key | Value and reason |
  |---|---|
  | `permissions.defaultMode` | `default` (Manual). A default, not a lock: users can switch to auto; VS Code remembers the last pick (D1, R6.9.3). |
  | `permissions.allow` | Two exact repo scripts (`npm test`, `npm run lint`) [design]. Read-only commands need no rule: a built-in set runs without a prompt in every mode (R6.9.3); wildcard rules such as `Bash(git log *)` can write files (examples finding 19). Phase 1 also denies `Read(~/.aws/**)` and sets `autoMode.classifyAllShell` (OD21). |
  | `allowManagedPermissionRulesOnly` | `true`, one rule set (D1, research 6.9.4 Q4; R1.2.5). Cost: project and user rules are ignored, so the managed set must carry every deny/ask rule projects need; prompts likely rise (⚠️ research 6.9.4 Q4). |
  | `permissions.disableBypassPermissionsMode` | `"disable"`: removes bypass mode (P3a; R1.2.2). Auto mode, where a classifier approves instead of a person, stays available (D1) and is measured through `permission_mode`. |
  | `permissions.deny` / `ask` | Deny credential paths (R5.5.4; `Read(...)` syntax ⚠️ R1.8 #5), and from phase 1 `Read(~/.config/gh/**)`, `Bash(gh pr review *)` and `Bash(gh api *reviews*)` (OD25; patterns 📖 R9.4.1, hygiene only). Ask for `WebFetch`, which the sandbox domain list does not limit (R1.6.2); cost: a prompt per fetch. The HIPAA template denies WebFetch (R5.5.4); "ask" is a deliberate deviation so that documentation lookups still work. Ask for `Bash(aws *)`, `Bash(pulumi *)`, `Bash(serverless *)` and the forms `sls *`, `npx pulumi *`, `npx serverless *`, `npx sls *`, which prompts even in auto mode (📖 [auto mode config](https://code.claude.com/docs/en/auto-mode-config.md); examples finding 22). Credential denies extend to the known credential stores of Papaya's stack; some paths are ⚠️ and some stores are not covered (examples E8, with every deviation from the template). |
  | `requiredMinimumVersion` | ≥ 2.1.310 in phase 2: 2.1.285 for `allowedProviders` (R1.1.15), 2.1.310 so `allowManagedHooksOnly` also blocks monitors of plugins that are not force-enabled (📖 [settings reference](https://code.claude.com/docs/en/settings-reference.md#allowmanagedhooksonly)); which also covers `--restricted` (2.1.248, R6.9.1b) and the plugin-pin fix (2.1.179, R6.2.7); ≥ 2.1.295 if any managed hook uses `onFailure: "block"` (R1.5.2); and ≥ the latest fixed advisory at rollout (R6.3.9). It does not end running sessions and fails open on a bad value (R1.1.13). |
  | `allowedProviders` + `forceLoginOrgUUID` | `["anthropic"]` + Papaya's org; closes most bypasses on **endpoint-managed** machines (R1.1.15). `forceLoginOrgUUID` checks claude.ai sign-ins only, not Claude Console sign-ins (R5.5.5); with it set, sessions on `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` or `apiKeyHelper` are refused (R1.11.3.11). |
  | `allowManagedHooksOnly` | `true` (R1.5.4). |
  | `autoMode` | `classifyAllShell: true` and the template's `"$defaults"` pins, which keep the built-in rules; not a boundary (examples finding 25). |
  | sandbox | `sandbox.enabled`, `failIfUnavailable`, `allowUnsandboxedCommands: false`, narrow `network.allowedDomains` locked by `network.allowManagedDomainsOnly`; `credentials` / `filesystem.denyRead` on `~/.aws` and the other credential stores, which the sandbox can otherwise read (R1.6.3, R1.6.4). Reads are a denylist and allowed domains are exfiltration paths; `git push`, `gh`, Docker and private-registry `npm ci` fail inside the sandbox (limits and costs: examples E8). |
  | `sandbox.autoAllowBashIfSandboxed` | Left at its default `true` (owner decision OD12). This widens D1's "Manual + allowlist": every sandboxed command, writes in the working directory and calls to allowed domains included, runs without a prompt. Detail: sandboxed Bash runs without a prompt, so in Manual mode prompts are for edits, unsandboxed commands and fetches, not every command (R5.5.5b). A deliberate choice: the sandbox (no `~/.aws`, allowlisted network) is the control for those commands. The HIPAA README says to set `false` if policy needs a person to approve each command (R5.5.5b); cost of `false`: a prompt per command. |
  | MCP, plugins | Layer 4. |
  | OTel | Exporter on, content flags `0` (R1.1.20, R5.5.4). |

- **Trade-off on AWS credentials [design].** With `~/.aws` hidden from the phase-2 sandbox,
  `aws`, `pulumi` and `serverless` run outside it (`sandbox.excludedCommands`) with full access and
  network (📖 R1.6.4). Repo code they load (the Pulumi program, Serverless plugins) then runs
  unsandboxed, and an injected command could send out the SSO token cache (⚠️ inference). Each call
  prompts through the `ask` rules; real-account runs belong in CI. Residual risk, accepted: token
  theft during a session, bounded because nobody holds standing prod write or PHI read. Mitigations
  and their limits: [appendix E](07-framework-appendix.md#e-aws-credentials-on-laptops).
- **What Engineering loses in phase 2, and what gives part of it back (OD34) [design unless
  marked].** These are the largest day-to-day costs of the design; S4 ("no new step in the non-prod
  loop", rollout plan) is restated to match them and measured from the first phase-2 team. The
  phase-2 sandbox goes to one pilot team first; the rest of Papaya gets it only once S4 holds for
  that team (OD50, rollout 2.1):

  | Loss | Why | What reduces it |
  |---|---|---|
  | The agent cannot `git push`, `git fetch`, `gh` or open the PR | The sandbox hides git credentials and the `gh` token (examples E8) | The engineer runs `git push` and `gh pr create --body-file <file the agent wrote>` at the `!` prompt, outside the agent's tools: one step per PR (time ⚠️, measured). Under evaluation in the phase-2 pilot (OD50): a narrow credential readable in the sandbox that can push feature branches and open PRs; `main` is protected by the ruleset whatever the token. GitHub's permission for opening a PR (pull requests: write) also allows submitting a review (⚠️ recalled, to check), so the approval-gate check, which counts no bot or agent-session approval it can detect, stays the control (layer 3) |
  | Every `aws`, `pulumi`, `serverless` call prompts, in auto mode too | They are excluded from the sandbox and run with full access (above), so a person confirms each one | Run `pulumi`/`serverless` against real accounts only in CI (PR previews, layer 3); on laptops keep them to non-prod. Prompts per session are counted from OTel (layer 8). A policy that drops these prompts for a non-prod-only environment needs per-group managed settings, which server-managed settings do not offer; the self-hosted Claude apps gateway does (📖 R1.1.6). Phase-3 option, with its own cost |
  | Docker and Testcontainers fail; localhost servers fail on macOS | Unix sockets and local binding are blocked (examples E8) | Such tests run in CI on the PR, or at the `!` prompt |
  | `npm ci` from a private registry fails | `~/.npmrc` is hidden | A read-only, install-only registry token in a separate npm user config that is not on the denylist (`NPM_CONFIG_USERCONFIG`; ⚠️ not tested with the sandbox), and the registry domain allowed; `~/.npmrc` stays hidden and publish tokens never sit on laptops [design] |
  | No raw prod logs of a service, and no prod configuration values, until the service is fixed | Logs and plain-text Serverless variables can carry PHI and secrets (layers 1, 6) | A deadline, not an open end: every claims service's log groups get masking and the SAST rule by the end of phase 2, the rest by day 100 (rollout 1.11; ⚠️ estimate). Once masked, the agent queries them through `ProdReadMetadata` with Logs Insights, and masking applies there too (📖 R9.2.7); nobody it uses holds `logs:Unmask`. Configuration comes from the IaC code until runtime secret resolution lands per service. Real data only through a data-read request (layer 6) |

  The agent-safe prod debugging path is therefore: metrics and masked logs through
  `ProdReadMetadata` in an incident-analysis session (session types below); the code and IaC in
  the repository; synthetic reproduction in non-prod; a data-read request only when real rows are
  needed.
- **Session types:**

  | Session | Identity | Flags | Enforcement |
  |---|---|---|---|
  | Daily development (laptop) | non-prod roles + `ProdReadMetadata` | baseline | Auto mode by choice (D1). `--restricted` removes Bash and the other code-running tools unless `--tools` names them (✅ `claude --help`, 2.1.319), so it is not used for daily development, where the agent must run tests; D3's recommendation applies to the incident session. |
  | Incident analysis (laptop) | meant to be `ProdReadMetadata` only | `--restricted --strict-mcp-config --tools "Bash,Read,Grep,Glob,Skill"`, started in an empty scratch directory, not the repo [design] | Process rule (D3, research 6.9.4 Q1–Q2). No WebFetch, and file tools confined to the working directory (📖 R6.9.1b). `--tools` sets the list of available built-in tools, so Edit and Write are not in it (✅ `claude --help`, 2.1.319). `--restricted` still loads MCP servers unless `--strict-mcp-config` is added (✅ same help text), so with it and no `--mcp-config` the session has no Linear or Slack tool to post through. Bash can still write in its working directory (📖 R1.6.3) and call any role in the cache. Skills of the internal plugin load because managed settings force-enable it (OD47); `Skill` is in `--tools` so the model can invoke them (whether an explicit `--tools` list without it blocks skills is ⚠️ not tested). |
  | CI agent (hosted runner) | own GitHub App token; never `production` | `--restricted`, explicit `--tools`; all rules in a managed-settings file on the runner | Workflow file under CODEOWNERS (D3, research 6.9.4 Q5). The file is advisory if `Bash` is in `--tools` (layer 5). |
  | JIT terminal | JIT grant | no agent | Process rule (D2). |
  | Auto-mode environment (phase 3) | non-prod only | auto encouraged | D1 option (c). |

- **Phase-1 interim posture:** the sandbox and most credential denies arrive in phase 2 (OD4), so for
  the first 45–75 days the network is open to every Bash command, and `~/.aws` is protected only by
  the `Read(~/.aws/**)` deny rule (OD21), which does not cover a command that reads files without
  naming them or a script that opens them itself (📖 [permissions](https://code.claude.com/docs/en/permissions.md)); in auto mode the classifier
  is the only other gate. Impact is bounded once standing prod write is removed at the
  end of phase 1 (layer 1); before that, today's exposure continues, and token theft is easier in
  this window. Interim measure (OD43): the phase-1 subset already carries the `ask` rules for
  `aws`, `pulumi` and `serverless` (with the `sls` alias and the `npx` forms), which prompt in
  auto mode too (📖 [auto mode config](https://code.claude.com/docs/en/auto-mode-config.md)), so
  the usual ways of calling a cloud CLI with the engineer's still-writable session need a person to
  confirm them. Auto mode itself stays allowed (D1). Bash rules match the command text and are not a
  boundary (📖 R1.2.6): a full path, a wrapper script or a script that calls the AWS SDK directly is
  not caught.
- **Isolated agent runtime, a phase-2 option (OD58) [design; numbers ⚠️ estimates].** Today the
  agent runs as the engineer: CloudTrail cannot tell them apart (P1a), an injected command can use
  the engineer's SSO tokens (trade-off above), and the sandbox that limits this costs Engineering
  push, PRs and Docker. The option: the agent runs where the engineer's credentials are not, in a
  development box in a non-prod account (or a container under a separate OS user on the laptop):
  - AWS: the box's own role, non-prod accounts plus a metadata-only prod read role that trusts only
    the box's role; CloudTrail shows the agent as its own principal, with the engineer in the role
    session name (how the box sets it ⚠️ to design);
  - GitHub: a short-lived token from a GitHub App per session, allowed to push branches other than
    `main` and open PRs; the ruleset protects `main`, and the approval-gate app counts no approval
    from an app (R1), whatever the token's review permission (⚠️ recalled that opening PRs also
    allows reviews);
  - what it gives: P1a covered for everything done in the box; a stolen token opens only the
    box's roles; Engineering gets back agent push and PRs, Docker inside the box and no prompt per
    non-prod cloud CLI call;
  - cost: about 15–25 pd to build (image, provisioning, token broker, roles) and the compute per
    engineer; laptop sessions and their layer-2 controls stay for those who do not use it.
  It is evaluated with the phase-2 pilot next to OD50's narrow credential (rollout 2.14); Papaya
  decides at the final review whether it replaces phase 3's item 3.3 (§1).
- **Hard limits:** Bash rules are not a boundary (📖 R1.2.6); hooks fail open unless
  `"onFailure": "block"` (📖 R1.5.2); `--restricted` cannot be forced by a setting (📖 R6.9.1), and a `PATH` wrapper on laptops can be bypassed (⚠️ R6.9.1c);
  on laptops **without MDM**, a different login, an API key or a `CLAUDE_CODE_USE_*` variable skips
  server-managed settings, `allowedProviders` included (📖 R1.1.7; ⚠️ R1.8 #3, G11). So S5's
  "nobody can turn off all prompts unnoticed" is met only on laptops with MDM; elsewhere it is
  reported as not met (OD54, rollout metrics).
- **Auto memory:** engineers review it and delete it after a suspicious session; residual risk with a
  named owner (D3).
- **Fallback:** switch to `disableAutoMode` (📖 R1.2.2) if the planted-injection test steers auto mode, a serious
  advisory appears, or an audit finds auto mode touched a protected scope (D1).

**Audit evidence.** Managed settings as an expected copy in git with PR approvals, a monthly diff with the console export (G18), sampled `/status`, and OTel permission-mode metrics; full register: [04-compliance-mapping.md](04-compliance-mapping.md#register).

**Cost / value.** More prompts than auto mode, partly offset by the built-in read-only commands and
the two allowed repo scripts. Compliance
gets one organization policy with evidence instead of personal choices (P3c).

---

## Layer 3 — Change workflow by risk level

**Principle.** The level is set by the damage a change can do. Above non-prod there is one default
path: a reviewed PR applied by the pipeline. The JIT fallback (layer 7) is the only other write
path. The approver reviews the code change that will be applied. Incidents use the same path with
faster people, not fewer checks. A real-data read is not a change and has its own rule (L3-data).

Who approves:

- **Two people by default:** one makes the change, one who owns the changed files approves it.
  Higher risk narrows *who* may approve (the owners of that path), not how many.
- **Process paths** (the files that define the workflow itself, listed in layer 5): two members of
  the L3 owner team.
- **A PR touching several teams' files:** an owner of each team; in an incident, the on-call
  approver on shift can cover them all.
- **A risky prod diff** stops the deploy whatever its level; the original author opens an approval
  PR and an owner of that stack, usually the first approver, approves it. If that person is
  unavailable, another owner approves, and the third person is counted monthly as a deviation.

Decisions behind these rules: OD2, OD8, OD11, OD13, OD26, OD27 in the
[appendix](07-framework-appendix.md#r-authors-design-decisions-od-n-2026-11-09).

| Level | What | Examples | Approval | Path |
|---|---|---|---|---|
| **L0** | Read: non-prod anything; prod metadata | metrics, redacted logs | none | read-only identity |
| **L1** | Change in non-prod | deploy a branch to dev; `pulumi preview` on non-prod (needs state-write permission on a DIY S3 backend, 📖 R4.3.3) | author only | non-prod roles or PR pipeline |
| **L2** | Routine prod change in code | Lambda timeout/memory, ECS desired count, release | 1 code owner ≠ author, ≠ last pusher | PR → `main` → deploy workflow |
| **L3** | High-risk prod change | IAM/SCP; replace/delete of stateful resources; network; `.github/**`, CODEOWNERS, `CLAUDE.md`, `CLAUDE.local.md`, `.claude/**`, `.claude.json`, `.mcp.json`, `.husky/`, `.gitmodules`, `.ripgreprc`, plugin/MCP catalogue and the rest of the canonical list in layer 5; advisory policy finding | 1 code owner ≠ author, ≠ last pusher; the stack's owner, then the risk stop, for L3 content inside a domain file (an IAM statement in `serverless.yml`, a stateful delete). Process paths: **2** L3 owner team members, never the on-call group; the IAM stack is one of them, with an incident rule below. In incidents the on-call approver covers every deployable path | same path; for IaC changes the risk stop also applies; workflow and agent-config files have no prod diff |
| **L3-JIT** | Break-glass | ECS force-redeploy while Actions is down | on-call approver ≠ requester, who counts as owner of the service in the request; incidents only; Papaya's Compliance signs off that this meets the approval rule only partly (§1) | layer 7 |
| **L3-data** | Real customer data read | one tenant's failed claim record | an approver ≠ requester and an agreement (GĐ-9); data-owner co-approval [design], beyond GĐ-9; at night, see layer 6 | layer 6 |
| **L3-data-write** | Data fix on one tenant's records | retry a stuck payout | a code owner plus a different member of that tenant's data-owner team, checked by the approval-gate app; in an incident the on-call approver stands in and the data owner reviews next working day (OD29) | PR → `sql` deploy job ("Database changes" below) |

**The IAM stack** (`infra/pulumi/iam/` and its risk-stop approvals) is a process path: it creates
and re-trusts the SCP-exempt roles and the permissions boundary, so the on-call group does not
co-own it (OD32). JIT cannot change those roles either, because the SCP lets only the IAM stack's
deploy role touch them. So in an incident the approval-gate app accepts one L3 owner team member,
reached by phone, plus the on-call approver on shift, and flags it for the monthly report (OD55).
This is rare by design: the IAM stack holds only those roles and the boundary; a service's everyday
permissions live in its domain stack as `svc-*` roles under the boundary, which on-call can approve.

`CLAUDE.md` and the other agent configuration files are L3, because they define the workflow for
the whole team (OD3). With code-owner review on, every PR, L2 included, needs an approval from an
owner of the files it touches (📖 R3.2.3, R3.2.7; per-file behaviour ⚠️ not a separate research row).
What differs at L3 is **which team** owns the path: L3 paths are owned in CODEOWNERS by a designated
L3 owner team, L2 paths by their domain team; and IaC changes at L3 meet the
risk stop. Most IAM, network and stateful changes sit inside domain files, so they are approved by
the stack's owners, not the L3 team (OD8); automated checks make up for this: IAM Access Analyzer
`check-no-new-access` (📖 R2.8.1) and the Pulumi policy pack (📖 R4.2.2), both from phase 2 (layer 5). Cost: changes to `CLAUDE.md` (where D3 puts shared knowledge) need the L3 owner team, not
the domain team that edits it most.

**On Papaya's stack**

- **Gate = merge to `main`.** On Team, environment reviewers do not exist for private repos
  (📖 R3.1.2). Ruleset on `main`: PR required, 1 approval, code-owner review, dismiss stale approvals,
  approval by someone other than the last pusher, required checks from a pinned source app, no force
  push, empty bypass list (📖 R3.2.2, R3.2.3, R3.2.5). Branch up to date before merge, since there is
  no merge queue (⚠️ R4.6 #1). GitHub dismisses an approval as stale only when the PR's diff
  changes, e.g. after "Update branch" if the merge base brings new changes (📖
  [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches));
  the approval-gate check follows the same rule (OD31), so a branch update that leaves the PR's
  own changes alone costs no new approval. Cost: when another merge does change the diff, the PR
  is approved again; how often that happens in the monorepo is measured in rollout (S4). What
  "most recent reviewable push" means for "Update branch" is not documented (⚠️); it is tested
  when the ruleset is built (rollout 1.5). Residual risk, accepted (OD31): the same patch ID can
  still clash in meaning with code that reached `main` since the approval; CI checks and the risk
  stop run again on the new commit, but no person reviews the combination.
- **L3 approvals [design]:** CODEOWNERS plus code-owner review, no path-based required
  reviewers rule. That rule (📖 R3.2.4) asks for approvals from specific teams, which the on-call
  group would not satisfy at night, and how it combines several teams is not researched (⚠️), so it
  would break OD9 or add a third person; its availability on Team was not found either
  (📖 R9.1.15). GitHub stops the author from approving (📖 R3.3.1). A required check with a pinned source app (📖 R3.2.5), set by a dedicated GitHub App that reacts to review events and is the pinned source [design; hosting, key storage and whether its key counts against S2 are not researched, ⚠️ G19], adds what
  the rules cannot (decision logic: examples E12):
  - it counts only human approvals of the head commit, or of an earlier commit whose diff against
    its merge base is the same (`git patch-id`, OD31), by someone who is not the author, the last
    pusher of a change to that diff or, for app-opened PRs, the person who triggered the agent, since an app's approval
    might count (⚠️ R3.3.4, R3.7 A3; review fields 📖 R9.1.10);
  - it requires two different L3 owner team members on process paths (OD26), because the
    ruleset's approval count is repository-wide (📖 R9.1.15);
  - it applies the on-call rule of OD27 (next bullet);
  - it flags, without blocking, approvals made within two minutes of the last push or at night
    (in the approver's time zone) without an incident; they go to the monthly report as signals
    of rubber-stamping or of a stolen login (threat T23).
  - **Running it [design]:** a dedicated tooling AWS account and its own repository with two L3
    approvals; the key stays in that account's secrets store and is on the inventory. It **fails
    closed**; during an incident an outage counts as "pipeline unavailable" (JIT), and a long outage
    is handled by a recorded, alerted removal of its check (T13). Detail: [appendix F](07-framework-appendix.md#f-running-the-approval-gate-app).
- **Who approves at night (OD9, OD27) [design unless marked]:** a fixed GitHub team of on-call
  approvers (with write permission, 📖 R3.2.7) co-owns every deployable path in CODEOWNERS next to
  the domain team, but not the paths that define the process (OD13); one primary and one backup are
  on call. GitHub would accept their approval on any day (📖 R3.2.7), so the approval-gate app
  counts it for another team's file only if the PR links an incident that is open when the check
  runs and the approver is on shift; the `incident` label alone grants nothing (📖 R9.1.9). In
  phase 1 incidents are Linear issues and the shift comes from `oncall/schedule.yaml` (an L3 path);
  from phase 2 both come from the paging tool. Every `incident` PR is in the monthly report, which
  is what catches an invented incident in phase 1. Cost: on normal days a cross-team PR needs an
  owner of each team. Detail: [appendix G](07-framework-appendix.md#g-who-approves-at-night).
- **GitHub plan: Team or Enterprise Cloud (OD44).** Several controls here work around GitHub
  Team. Enterprise Cloud ($21 against $4 per user per month, 📖 R9.1.3) would replace the GitHub
  login register (SAML SSO), the monthly manual audit-log export and the unseen prod diff
  (environment reviewers), but not the approval-gate rules, the JIT receiver, the risk stop, the
  database path or the evidence bucket. **Recommendation:** move to Enterprise Cloud in phase 2 if
  Papaya has up to about 100 GitHub users, for Compliance's sake rather than for build effort
  (roughly 5–10 person-days saved, ⚠️); the design works on Team either way (GĐ-5). Comparison
  table: [appendix H](07-framework-appendix.md#h-github-team-or-enterprise-cloud).
- **Risk stop [design] (ADR-0004):** applies to every deploy, whatever the level. The deploy job
  previews prod; on a stateful replace or delete, an IAM, network or security-group change, or
  (from phase 2) an advisory policy finding, it stops and posts a filtered summary without values.
  The original author opens a second PR adding `deploy-approvals/<stack>/<sha>.yaml` with the
  stopped SHA and the preview hash (Actions may not open PRs, 📖 R3.3.3); an owner of the stack or
  the on-call group, ≠ author, approves it after reading what will change (OD8, OD9). Merging it
  re-runs the deploy, which continues only if the new preview hash matches (examples E7). It
  catches risky diffs nobody looked at, not approved malicious code (OD15). Cost: while a stack is
  stopped, later merges to it wait. Mechanics and limits: [appendix I](07-framework-appendix.md#i-risk-stop-mechanics).
- **Database changes (OD29, ADR-0011) [design].** Aurora schema migrations, GraphQL-engine
  (Hasura) metadata and data fixes are files under `db/<service>/`, merged like code and applied by
  the `sql` job of the deploy workflow from its own `production-db` environment (examples E3). The
  GitHub-hosted job only starts a one-off Fargate task inside the prod VPC, which connects with IAM
  database authentication and applies exactly the files the SQL risk stop classified (examples E7,
  E15). Destructive statements, grants, every metadata change and any data change inside a
  migration stop for approval. Data fixes touch one tenant, declare their expected row count, name
  records by opaque IDs only (`data-fix-scan`, examples E19, OD48) and need that tenant's data
  owner (L3-data-write). No person holds database credentials day to day. Mechanism, evidence and
  costs: [appendix J](07-framework-appendix.md#j-database-changes-mechanism).
- **Merge approval = deploy approval** only if (⚠️ R3.6 #1, from 📖 R3.1.3, R3.4.5c): `production`
  allows only `main`; only the reusable deploy workflow (under CODEOWNERS) references it; no ref/SHA
  inputs; no `issue_comment`, `pull_request_target` or `workflow_run` triggers; one concurrency group
  per stack without `cancel-in-progress` (📖 R4.1.4); squash-only merges, so each PR is one commit on
  `main` (OD16); and the job deploys only the current tip of `main`, because a writer can re-run an
  old run for 30 days and roll prod back without approval (OD17; 📖 GitHub docs, linked in examples finding 4).
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
- **Every prod write path and its gate (OD36).** "Every prod change is a PR" holds only for the
  paths listed here; a path not in the list is a gap. Platforms named in the brief:

  | Platform | Write path | Gate | Gap or open item |
  |---|---|---|---|
  | Lambda (Serverless) | `serverless deploy` from the deploy job | PR, risk stop, SCP on Lambda updates (phase 2) | none beyond layer 3 |
  | AWS infrastructure (Pulumi): ECS, EC2, SNS/SQS, Step Functions, S3, IAM | `pulumi up` from the deploy job | PR, risk stop, policy pack (phase 2) | console changes outside IaC: drift detection (layer 7) |
  | ECS services, EC2 | image or AMI change through the stack; `ecs update-service` only by JIT | PR; JIT | image signing and scanning (layer 5); EC2 instances changed by hand or SSM: not inventoried (⚠️) |
  | Aurora | `sql` job (ADR-0011) | PR, SQL risk stop, data owner for data fixes | none beyond ADR-0011 |
  | GraphQL engine metadata | same job, `hasura metadata apply` | PR, always stops | none |
  | k0s (production AI agents) | manifests from the k0s deploy job (OD24) | PR; namespaced token | no prod preview or risk stop; humans until OIDC |
  | Production AI agents' prompts, models, tools | the same k0s deploy | PR; AI team + `agent-eval` check; tools as a process path (OD45) | evaluation sets per tenant to build |
  | GCP / Vertex AI | deploy job with WIF to the prod service account | PR | PAM for humans; Data Access logs (above) |
  | Firebase Hosting (and Next.js sites on it) | Firebase deploy job | PR | JSON key until the WIF spike works |
  | Mobile apps (React Native / Expo) | EAS Update to the `production` channel; store submission | PR, then the CI robot (OD40) | layer 5, "Mobile releases" |
  | Secrets and configuration | runtime resolution; Secrets Manager writes through the stack | PR | values set by hand: JIT only |
  | GitHub, Identity Center, Claude Code settings, the plugin catalogue | rulesets, identity stack, settings as code, marketplace repo | L3 paths, two L3 approvers | admins can edit the gate (§1) |

  Where Next.js is hosted (Firebase, Vercel, Amplify or ECS) is not stated in the brief (⚠️): the
  row follows whichever it is.
- **Changes to the production AI agents (OD45) [design].** Coding agents will also change the
  claim-assessment, extraction and fraud agents that run on k0s; a prompt or model change alters
  claim outcomes per insurer without any infrastructure diff, so the risk stop cannot see it.
  Their prompts and model settings (`ai-agents/<agent>/prompts/`, `model.yaml`) are owned by the AI
  team, not the on-call group, and a required check `agent-eval` runs the agent's evaluation set
  per tenant when they change and fails on a regression beyond the agreed threshold; the result is
  kept with the PR as evidence. Their tool permissions and identity (`tools.yaml`, the agents'
  RBAC) are a process path: two L3 owner team members (OD26). The runtime security of these agents
  (prompt injection from partner documents, A7a) stays out of scope.
- **Incident lane:** label `incident` plus a link to the open incident issue, on-call approver
  paged, security checks always run (S10), only slow unrelated tests skipped, and only when the
  approval-gate app sees an open incident (OD27) [design]. A required check skipped by a path filter may stay
  pending and block the merge (⚠️ Options §8), which would directly affect S7. So no required
  check uses a workflow-level path filter: each runs on every PR and decides inside the job
  whether its paths changed, passing as "not applicable" when they did not (`agent-eval`,
  `iac-scan` and `workflow-lint` included) [design].

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

**Audit evidence.** The PR (diff, approvers, checks), the deploy run log and risk-stop summary (exported, retention ⚠️ G7), the `deploy-approvals/` PR, and CloudTrail events linked by commit SHA and run ID; walk-through: [04-compliance-mapping.md](04-compliance-mapping.md#evidence-for-one-prod-change-s8).

**Cost / value.** One approver for every prod change, from the owners of the path (two L3 owner
team members on process paths, OD26); two approvals,
usually by the same approver, when the risk stop fires (OD13; OD11). Cross-team PRs: an owner of each team on normal days, one on-call approver in an incident (OD27). None in non-prod.
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
- **Pinning what every laptop runs (OD26) [design unless marked].** One compromised plugin, hook or
  local MCP server would hand an attacker many engineers' logins at once, enough to be both author
  and approver (threat T23). So the marketplace is pinned to a protected release tag (📖 R9.4.4),
  every plugin entry, internal ones included, carries a commit `sha` and a review record
  (📖 R9.4.5), auto-update stays off (📖 R9.4.6), and an update is a reviewed change of the pin
  (examples E9b). Cost: a plugin release takes three reviewed steps. Detail: [appendix K](07-framework-appendix.md#k-pinning-what-every-laptop-runs).
- **MCP:** "approved catalogue" = `allowedMcpServers` + `allowManagedMcpServersOnly: true`; without
  the lock users can widen it (📖 R1.3.1, R1.3.4). Match by `serverUrl` or `serverCommand`, never
  `serverName` ("not a security control", 📖 R1.3.3); `serverCommand` matches the exact argv (📖 R1.3.3).
  The allowlist covers servers that plugins bring too (📖 R9.4.2). A local server is admitted only
  as an artifact that cannot change under the same command (OD26) [design]: a container image by
  digest (`docker run --rm -i <image>@sha256:…`), or code shipped inside a pinned plugin
  (📖 R9.4.3; its path changes per version, so it is re-allowlisted on each update, ⚠️). Not
  `npx -y <pkg>@<version>`: that pins the package, not its dependencies [limit, examples E8].
  `disableClaudeAiConnectors: true` (📖 R1.3.7). With MDM, `managed-mcp.json` gives exclusive control;
  it cannot come from server-managed settings (📖 R1.3.2).
- **Review checklist** [design]: publisher; local `stdio` or remote (📖 R6.4.3); what it reads and where
  it sends data, with a supplier-register entry and BAA/DPA status (⚠️ R5.6); no token passthrough
  (📖 R6.4.2); write tools for Slack, Linear, GitHub only where needed (⚠️ R6.5 #6); how the server authenticates (Linear and Slack: G9); pinned version,
  reviewer, date.
- **Known gaps:** no per-group targeting in server-managed settings (📖 R1.1.6, R1.4.4); tool
  description changes after approval are not covered (⚠️ research 6.6); a remote server's
  behaviour can change behind the same `serverUrl`; a reviewed but malicious update still runs
  everywhere once its pin is approved.

**Audit evidence.** Catalogue file in git with an approved PR and a review record per entry, the supplier register, and OTel plugin events; full register: [04-compliance-mapping.md](04-compliance-mapping.md#register).

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
  service-account key for Firebase Hosting. This is an accepted exception to S2 = 0 until it
  is checked whether k0s and Firebase deploys can use OIDC (OD1, OD6). Conditions [design], in short: an environment secret of `production-k0s` (Expo: `production-mobile`), never a
  repository secret, which any writer can read (📖 R3.5.3b); GitHub-hosted runners, or a runner
  dedicated to that deploy; one copy; an owner, expiry and rotation in the exception register; for
  k0s, the namespaced, time-limited token of layer 1 and a Kubernetes API audit log. The exception
  covers CI deploy credentials only, not runtime credentials in the cluster. Detail and residual
  risk: [appendix L](07-framework-appendix.md#l-conditions-on-stored-deploy-credentials).
- **What runs in the deploy job (OD22, phase 1).** Approved code runs with a prod deploy role:
  the Pulumi program during preview and apply, Serverless plugins, and any install script.
  The risk stop sees resources, not SDK calls the program makes while it runs, so it cannot
  catch this (OD15). Three controls limit the damage instead [design]:
  - **one environment per kind of stack:** the IAM stack deploys from `production-iam`, database
    changes from `production-db`, every other stack from `production`; each has its own OIDC
    subject and roles, so a domain stack's job cannot obtain the IAM stack's role or the database
    change role (layer 1; examples E3, E4, E15). The `production-db` job installs no package and
    runs no Pulumi program, only the L3 scripts in `tools/db/` and the risk stop;
  - **domain roles are bounded:** they create or change only `svc-*` roles carrying the fixed
    permissions boundary (layer 1);
  - **no install scripts:** `npm_config_ignore_scripts` is set for the whole deploy and preview
    job ("npm does not run scripts specified in package.json files", 📖 R9.1.13; whether this
    covers every dependency is ⚠️ until tested on the runner). Packages that need their script
    are listed in `tools/ci/allowed-install-scripts.txt`, an L3 path, and rebuilt one by one
    (`npm rebuild <pkg>`, 📖 R9.1.13). npm v11 also has an `allowScripts` policy (📖 R9.1.13),
    an alternative once the CI npm version is known.

  What stays (OD51): every domain stack deploys from the one `production` environment, and the
  OIDC trust is per environment, not per stack, so the domain deploy roles are shared. Approved
  but malicious code in any domain stack (the website's, say) can therefore change every other
  domain stack's resources, the claims services included, within the limits above: no IAM-stack
  role, no SCP-exempt role, no database role. Splitting `production` into one environment and
  role per domain (`production-claims`, `production-web`, …) would confine it to its own domain;
  it is the next step after phase 1, sized with the number of domains. The separate preview role
  of OD15 stays on the phase-2 roadmap (item 2.9), because `pulumi up` runs the same program again
  with the apply role.
- **Side paths:** Pulumi ESC, Pulumi Deployments and Serverless Dashboard providers reach AWS
  (📖 R4.4.9) outside the GitHub gate (⚠️ R4.4.9); not used for prod (⚠️ R4.6 #6).
- **Pinning:** workflow lockfile (`gh actions-lock`) or full SHA, enforced by the org policy "Require
  actions to be pinned to a full-length commit SHA" (availability on Team ⚠️); the lockfile does not pin reusable workflows, so
  the deploy workflow lives in the same repo (📖 R3.5.5; conclusion [design]).
- **CODEOWNERS** on `.github/`, `CLAUDE.md`, `CLAUDE.local.md`, `.claude/`, `.claude.json`, `.mcp.json`,
  `.husky/`, `.gitmodules`, `.ripgreprc`, `.devcontainer/` (📖 R3.2.8; list ⚠️ R6.5 #5, R6.3.11), plus
  `.npmrc` (registry redirection) [design], the policy packs, the SCP code, the
  catalogue file and the risk-stop classifier `tools/risk-stop/` (OD14: the deploy runs it from the
  merged commit, so a domain-approved PR could otherwise switch it off), the install-script allowlist `tools/ci/` (OD22), the Identity Center stack (OD23), the IAM stack `infra/pulumi/iam/` and its `deploy-approvals/iam/` (OD32), the k0s RBAC and API-server configuration (OD24), and the on-call schedule `oncall/` (OD27). This is the canonical L3 path list that layer 3 refers to. Not on it:
  the other `deploy-approvals/<stack>/` folders, owned by the stack's owners and the on-call group (OD8, OD9). The private plugin
  marketplace is a separate repo with its own, stricter rulesets: two approvals, protected release
  tags (OD26; examples E9b). CI validates the file, because
  invalid lines are skipped silently (📖 R3.2.7). A fail-safe default line (`*` → L3 owner team and
  on-call group) keeps new stacks and root files from being unowned, since an unowned file accepts
  an approval from any writer (examples finding 7) [design].
- **No privileged triggers with untrusted code** (`pull_request_target`, `workflow_run` + checkout,
  📖 R3.5.4).
- **Agent review:** an independent agent (not the one that made the change) may post an automated
  review as an extra check; it never counts as an approval (GĐ-11). It runs on every PR that
  touches `infra/**`, `policy-packs/**` or a `serverless.yml` (OD22), so the human approver of
  code that will run with a deploy role always has a second reading of it [design].
- **Agents in CI** (example: the security review, E18): `claude-code-action` with a custom GitHub App limited to Contents, Issues, Pull
  requests (📖 R1.7.8), whose own credentials are listed in the S2 inventory (⚠️ G19); Anthropic workload identity federation, not a personal OAuth token (📖 R1.7.6);
  `--restricted` and explicit `--tools` (D3; passing it through `claude_args` unverified, ⚠️ research
  6.9.4 Q5); a managed-settings file on the runner, which also guards against mods (📖 R1.5.6; for
  federation auth ⚠️); MCP set fixed by CI because `.mcp.json` loads without a prompt in `-p` runs
  (📖 R1.3.5); never `environment: production` (⚠️ R3.6 #4). Hosted runners give `sudo` (📖 R3.5.1),
  so with `Bash` in `--tools` the runner file is advisory (⚠️ R3.5.1, R3.6 #4).
- **App-opened PRs:** a required check set by a dedicated GitHub App, pinned as its source (layer 3), confirms at least one approval by a
  human who did not trigger the run; counting approvals is not enough, since the app's own approval
  might count (⚠️ R3.3.4, R3.7 A3; 📖 R3.2.5).
- **Required checks (S10), concrete (OD39) [design unless marked]:**

  | Check | Tool on GitHub Team | Covers | Cost, limit |
  |---|---|---|---|
  | `dependency-check` | Dependabot alerts and security updates (free on every plan, 📖 R9.5.4) plus a CI scanner of the lockfiles that fails on high and critical findings (tool ⚠️ not chosen) | npm and Python dependencies of every service | GitHub's dependency-review action needs a paid licence on private repos (📖 R9.5.3) |
  | `secret-scan` | **Decision for Papaya:** GitHub Secret Protection, $19 per active committer per month (📖 R9.5.1, R9.5.2), adds push protection that stops a secret before it lands; without it, a CI scanner (tool ⚠️ not chosen) finds it after the push | the whole diff, all files | without push protection a pushed secret must be rotated |
  | `sast` | **Decision for Papaya:** CodeQL through GitHub Code Security, $30 per active committer per month (📖 R9.5.1, R9.5.2): JavaScript/TypeScript, Python and GitHub Actions workflows (📖 R9.5.5); without it, an open-source SAST tool (⚠️ not chosen). Plus the OD28 rule against logging whole events | application code, workflows | CodeQL has no IaC languages (📖 R9.5.5) |
  | `iac-scan` | Trivy misconfiguration scanning (📖 R9.5.6) on Dockerfiles, Kubernetes manifests and Helm charts, and on the CloudFormation template that `serverless package` produces | k0s manifests, images, Lambda stacks | Pulumi and Serverless sources are not supported (📖 R9.5.6): Pulumi through the policy pack (phase 2) |
  | `workflow-lint` | actionlint and zizmor on `.github/` changes (✅ both run on the examples here) | workflows | — |
  | `pr-size` | a small CI check: an app-opened PR above 400 changed lines fails, a human PR above it gets a warning (threshold [design]); GitHub has no PR-size rule (📖 R9.5.11) | agent PRs that are too large to review | split the PR |

  For 30 active committers (⚠️ Papaya's number unknown) the two licences cost about $1,470 a
  month (📖 R9.5.2 prices). From phase 2, IAM Access Analyzer `check-no-new-access` (📖 R2.8.1)
  and Pulumi policy packs (📖 R4.2.2) join. For Serverless stacks, Access Analyzer would check the IAM policies in the
  CloudFormation template that `serverless package` produces, against the deployed ones (⚠️ not
  researched); policy packs do not apply to them. Until phase 2, the only compensation for OD8 is
  the risk stop, which fires on every IAM change in the prod preview. A mandatory policy is only
  advisory during a preview while a value is still unknown (✅ `@pulumi/policy` 1.21.0 source,
  examples finding 23), so Access Analyzer is the preview-time IAM check; the policy-pack example
  (E10) also lists the routes it does not cover.
- **Images (OD39):** ECR enhanced scanning (Amazon Inspector, OS and language packages, on push and
  continuously; 📖 R9.5.7) for every image ECS, Lambda containers and k0s pull; ECR managed signing
  with AWS Signer on push (📖 R9.5.8). GitHub artifact attestations are not available for private
  repositories on Team (📖 R9.5.10). ECS and Lambda reference images by digest from the stack;
  signature verification at admission on k0s is a phase-3 decision, because both candidates are not
  stable yet (Kyverno `verifyImages` sits under a deprecated policy type in its 1.18 docs, Sigstore's
  policy-controller is "still actively under development", 📖 R9.5.9).
- **Mobile releases (OD40) [design unless marked].** EAS Update can push JavaScript to every
  installed app on a channel without a store review (📖 R9.8.1, R9.8.2), so it is a prod write
  path. The `production` channel is protected in Expo; only a CI robot with the Release Manager role
  publishes, from the `production-mobile` environment; updates are signed with a key that lives only
  there; a nightly job reconciles channel updates with deploy runs, because Expo's audit log does
  not list publishes (📖 R9.8.9). Detail: [appendix M](07-framework-appendix.md#m-mobile-releases-through-expo-eas).
**Audit evidence.** Workflows and lockfile in git, the secrets inventory and exception register (S2), audit-log events for secrets and Actions settings, and check results per PR; full register: [04-compliance-mapping.md](04-compliance-mapping.md#register).

**Cost / value.** One-time migration to OIDC and pinned actions; slower action updates. Compliance
gets S2 and the same guardrails for agent and human code.

---

## Layer 6 — Data protection and prompt-injection defence

**Principle.** The design keeps PHI from reaching the coding agent.
Some paths rely on process (below), so this is a target, not a guarantee. Other customer
personal data is outside that hard boundary: the agent reads metadata
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
    Redaction lives in application code, so one approved PR that logs a whole event would put
    PHI in a log group the agent reads. A second layer outside the code (OD28) [design]:
    - a CloudWatch Logs data protection policy on every log group `ProdReadMetadata` reads, set
      **before** the group is opened, because masking applies at ingestion only; masked data is
      hidden "at all egress points, including CloudWatch Logs Insights" (📖 R9.2.7);
    - custom identifiers keyed on field names (national ID, HKID, bank account, diagnosis,
      insured name; examples E14), because AWS has no managed identifier for Vietnam, Thailand
      or Hong Kong (📖 R9.2.8); at most 10, each regex ≤ 200 characters (📖 R9.2.9);
    - no agent-usable role holds `logs:Unmask`, and none gets `CloudWatchLogsFullAccess`, which
      includes it (📖 R9.2.7; E6 test);
    - a required SAST rule against logging whole events or payload objects in the claims
      services' handlers (S10; product open, G4); a log-level change already stops at the risk
      stop (`logging` property), because debug output can carry PHI.
    Limit: field-name masking catches structured logs, not free text in a message. It is a second
    layer; code review and the SAST rule remain the first. Cost: $0.12 per GB scanned
    (📖 R9.2.10) and masked values while debugging.
- **Real-data request** [design]: tenant, purpose, store, window, agreement; approved by the data owner
  and an approver ≠ requester; JIT data-read role, 1 h. At night the data owner is not on call: the
  on-call approver approves alone and the data owner reviews the grant the next working day. This
  applies to non-PHI and PHI alike; for PHI the reader is still a human without an agent. Per-tenant scoping through session tags
  (📖 R2.1.8) is unresolved, because tags come from user attributes (⚠️).
  - **PHI:** a human reads in a terminal without an agent (process rule, layer 1); the agent gets a
    redacted summary. This
    narrows GĐ-9 because the agent stays outside PHI scope and Team is not shown as
    BAA-covered (⚠️ R1.11.3.4). Enterprise + BAA only for a separate environment if needed.
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
- **Cross-border, per tenant country (OD37):** processing data collected in Vietnam on a platform
  abroad is a transfer (📖 R5.4.5); agent flows, including employee names in logs and transcripts,
  update the transfer impact assessment (⚠️ R5.7 #4, needs Papaya legal). Thailand: health data is
  sensitive (s.26) and a transfer abroad needs an adequate destination or a s.29 safeguard in the
  provider contract (📖 R9.7.1, R9.7.2); breaches go to the PDPC Office within 72 hours where
  feasible (📖 R9.7.3). Hong Kong: purpose limitation and processor contracts; breach notice is
  voluntary today (📖 R9.7.6, R9.7.8). Each tenant's profile and the breach row are in the
  compliance register (C-18, C-26); sector rules of the insurance regulators stay open (O-10, O-11).

**Audit evidence.** SCP/IAM text as the written access rule for sensitive data, real-data requests with the data-read role's CloudTrail events, and non-prod scan results; full register: [04-compliance-mapping.md](04-compliance-mapping.md#register).

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

- **Audit stores [design unless marked]:** organization CloudTrail to a log-archive account with
  integrity validation (📖 R2.6.2, R2.6.4), data events only on PHI buckets, prod Lambda invoke and
  prod SQS; an **evidence bucket** with Object Lock in compliance mode for 6 years (📖 R9.2.12),
  filled nightly with merged PRs, reviews, checks and deploy logs (examples E13) and monthly with
  the GitHub audit log, exported by hand on Team (📖 R9.1.5); JIT and data-read requests as Linear
  issues mirrored to the bucket by webhook (OD30); alerts on ruleset and environment changes and a
  comparison of live GitHub settings with an expected copy (G8); Database Activity Streams for
  Aurora SQL (📖 R2.7.2); Claude Code OTel without prompt content; the k0s API audit log. Detail:
  [appendix N](07-framework-appendix.md#n-audit-stores).
- **Change record [design]:** keyed by commit SHA or JIT request ID; links PR, approvals, run ID,
  preview and CloudTrail events. Monthly reconciliation: every prod write event matches a record
  approved before apply (S3). Actor: `onBehalfOf.userId` where present, else session name plus
  directory lookup (📖 R2.5.1; ⚠️ R2.5.3).
- **Drift [design]:** a scheduled `pulumi preview --refresh --expect-no-changes` (📖 R4.1.1,
  R4.3.1) with its own role, trusted only from a `drift` environment on `main`, plus CloudFormation
  drift detection (📖 R4.4.6); no auto-remediation, which would be an unreviewed `pulumi up`
  (📖 R4.3.2). Each finding gets an actor and a ticket. Which state writes the refresh needs is open
  (G14). Detail: [appendix O](07-framework-appendix.md#o-drift-detection).
- **On-call:** phase 1 delivers two named 24/7 schedules: approvers (primary and backup) and
  incident responders. The primary approves; the backup steps in only if the primary is
  unavailable. On-call approvers only approve during their shift; the fix is written by an incident
  responder, so the approver is never the author (OD2, OD7). Alert routing and the
  rest of on-call follow in phase 2 (tools: G5); in phase 1 the responder calls the approver by phone from the published schedule.
  The schedule is also an input of the approval-gate app (OD27): in phase 1 it is the file
  `oncall/schedule.yaml` (an L3 path) and open incidents are incident issues in Linear, created
  before the PR is linked. The monthly report lists every `incident` PR with its incident, approver
  and shift, and every approval the app flagged (layer 3).
- **Alerts and incident declaration, target (OD38) [design unless marked].** Built in phase 2
  (item 2.8): CloudWatch alarms → SNS → one paging tool (product open, G5) that holds the schedule
  and pages primary, then backup; GCP alerts to the same tool and also to email or Pub/Sub; Slack
  through Amazon Q Developer (📖 R9.6.7, R9.6.8); AWS Incident Manager is closed to new customers
  (📖 R9.6.7). Three severities, escalation after 10 and 20 minutes. An incident is declared as a
  Linear issue, which the approval-gate app and the JIT receiver read; a suspected data exposure
  starts the tenant country's breach clock (C-26). Full table: [appendix P](07-framework-appendix.md#p-alert-routing-and-incident-declaration).
- **Break-glass = JIT fallback** [design unless marked]:

  | Step | Rule |
  |---|---|
  | When | Only during an incident, when the PR path cannot be used: operation not in IaC and no runbook; GitHub/Actions down; pipeline broken. The approver refuses JIT for anything expressible in IaC while the pipeline works, and records why. Outside incidents, an operation not in IaC waits for IaC or a runbook. |
  | Request | Command list, scope, reason, incident link, in a channel that does not depend on GitHub. |
  | Approval | On-call approver ≠ requester, before the grant (OD2, OD7). The approver moves the Linear request to "Approved"; a receiver in the tooling account (next to the approval-gate app) gets the signed webhook (📖 [Linear webhooks](https://linear.app/developers/webhooks): HMAC-SHA256 `Linear-Signature`, `actor`, `updatedFrom`) and grants only if the signature is valid and fresh, a person made the change, the approver ≠ the requester as Identity Center users (people register, OD25), the approver is on shift, the incident is open and the permission set is an allowed `InfraOperator-*` (OD33; examples E16). One grant per request: a retried webhook or a second move to "Approved" grants nothing (Linear retries up to 3 times, 📖 same page). The receiver's role may assign only permission sets tagged `jit-grant`, in the prod accounts, and may never create, change or re-tag a permission set (examples E16; resource types ✅ AWS Service Reference). Linear accounts sign in through single sign-on and are in the people register (Linear plan for SSO ⚠️ not checked). The AWS TEAM sample is compared with the receiver before building it (rollout 1.13). If the receiver is down, an L3 owner team member grants by hand against the same checklist; the Identity Center alert (layer 1) fires on it and the monthly report reviews it. |
  | Grant | `InfraOperator-<service>`; role session 1 h (📖 R2.1.4). Deleting the assignment likely stops only new sessions (⚠️ R2.4.2, R2.9 #3), so the real window can approach 2 h; ending the portal session does not end role sessions (📖 R2.4.3). An immediate stop needs the revocation SCP, which must keep the user blocked for at least 12 h (📖 R2.4.4). Applying it is a management-account change held by the L3 owner team only, and no night-time path for it is designed yet (⚠️ G20): until one exists, a misused grant may run to the end of its window. Candidate: a pre-approved revocation runbook for one named L3 owner reachable by phone, or an org-wide `aws:TokenIssueTime` Deny as kill switch (⚠️ R2.9 #3). |
  | Execution | The grant goes to the requester (the incident responder), who types the commands; no agent in that terminal (D2). On-call approvers do not run commands; they only approve. |
  | After | A job compares CloudTrail writes in the window with the list; a codify PR within a fixed deadline (as soon as GitHub is back); drift detection until it merges. |
  | Identity Center outage | Emergency SAML federation to roles, built and tested in advance (📖 R2.1.11; ⚠️ R2.9 #2); no user mapped until an approved activation, which is alerted. |

  **Example request (illustrative command ⚠️):** "INC-123, ECS service `claims-api`, Actions outage. Run
  `aws ecs update-service --cluster <prod-cluster> --service <svc> --force-new-deployment`. Scope
  `InfraOperator-claims`, 1 h."

  **Metrics** (starting thresholds ⚠️ to calibrate): JIT used where a PR was possible
  (review at 1); writes outside the list (review at 1); codify PRs late (review at 1); grants per
  month and share of incidents needing non-IaC operations (review above about 25 % [design]); incident approvals of the IAM stack by one L3 owner and the on-call approver
  (OD55; review above one per quarter [design]: then more of the IAM stack's content moves into
  domain stacks as `svc-*` roles). On a breach,
  make the PR lane faster or add a runbook; do not widen JIT.
- **Roadmap:** runbooks for repeated non-IaC operations, if SSM Automation's approval step meets three
  conditions (Options §2; outside 02-research, G6); break-glass from an environment without the agent
  (D2, ⚠️).

**Audit evidence.** Validated CloudTrail, the exported GitHub audit log, change records and monthly reconciliation (S3, S8), JIT records, drift tickets and incident approval waits (S7); full register: [04-compliance-mapping.md](04-compliance-mapping.md#register).

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
- **Metrics:** S1–S11 (rollout plan); this framework adds the JIT metrics (layer 7) and the
  prompt metrics (layer 2). S2 and S5 have caveats (OD1; layer 2).
- **Rollout** (≈ 100 days, re-baselined from GĐ-12's 90 after the effort estimate, OD49): [`03-rollout-plan.md`](03-rollout-plan.md),
  with owners and "done when" checks [design]. Order: (1) remove long-lived CI credentials, (2) narrow standing prod
  access, (3) MCP/plugin catalogue; the on-call approver list before or with (2). Phase 1 (days 0–45)
  makes the PR the default prod write path, with ten hard prerequisites (OD53) before standing prod write is
  removed; phase 2 (45–75) adds SCPs, the rest of the managed baseline and automated
  reconciliation; phase 3 (75–100) tests and reviews. The phase-1 load is the main rollout risk: a
  rough estimate (⚠️) is 75–110 person-days, so the rollout plan names a minimum safe phase 1 for 2
  DevSecOps people and one platform engineer over about 45 days, and a degraded mode if the
  approval-gate app is late (OD35).

- **Exceptions:** a ticket with owner, reason and expiry.
- **Standards mapping:** ISO 27001:2022 Annex A (IDs recalled, ⚠️ R5.1), HIPAA Security Rule
  (📖 R5.2) and Vietnam law (📖 R5.4) are mapped per control area in the
  [compliance register](04-compliance-mapping.md#standards-cross-reference), with every caveat. "A named human approves"
  is Papaya's chosen way to meet these controls, not a literal requirement (⚠️ R5.7 #1).
- **Out of scope:** security of the production AI agents (A7a); noted as a follow-up.

**Audit evidence.** Git history of policy files, monthly metrics, 90-day review minutes, the exception register and planted-injection reports; standards: [04-compliance-mapping.md](04-compliance-mapping.md#standards-cross-reference).

**Cost / value.** Steady, small overhead for DevSecOps and the owners of deploy workflows. Compliance gets a managed system
with owners and review dates.

---

## Gaps and the author's decisions

Twenty gaps (G1–G20: not designed, or only an open item) and the author's design decisions
(OD1–OD59) are in the appendix: [gaps](07-framework-appendix.md#q-gaps),
[decisions](07-framework-appendix.md#r-authors-design-decisions-od-n-2026-11-09).
