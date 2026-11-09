# Framework: coding agents for DevSecOps at Papaya

> Status: v3 after 17 independent review rounds; approved by the author (the owner of this submission, not Papaya) 2026-11-09 · Updated: 2026-11-09
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
Every code is also defined in the [executive brief](00-executive-brief.md#codes-used-in-the-other-documents).
**GĐ-n** = assumption in `work/01-problem-framing.md` §4 (owner-confirmed: GĐ-1, 2, 5, 6, 8, 9, 11,
14; the others are marked "unconfirmed" where used); **S-n** = success criteria
(§5); **P/A-n** = problems (§1); **D1–D3** = owner decisions in research 6.6; **Options §n** =
`work/03-options.md`; **G-n** = gaps; **OD-n** = the author's design decisions on this draft (both
at the end). "Owner" throughout means the author of this submission, not Papaya; the choices left
to Papaya are in §1.
Earlier owner answers are cited with their source: "research 6.9.4 Q4", "framing Q8", "Options §9 Q2".

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
| Whether HIPAA applies; Papaya's role per insurer (controller or processor) | Legal counsel | compliance register |

Sources and detail: the limits in §1a, the research rows in `work/02-research.md` and
`work/09-fix-research.md`, the author's decisions at the end of this file.

### 1a. Limits and trade-offs, in detail

The chosen approach is called "A + D2'" in the working notes (Options §9): option A, the PR path
for every prod change, plus D2', a narrow JIT fallback. The codes used from here on are explained
in "How to read this".


- **The fallback meets the approval rule only partly** (approves a command list, not an applied
  change); accepted by the author (Options §9 Q2), to be signed off by Papaya's Compliance (§1). It is a second, process-controlled path, while the
  framing asked for one technically enforced path (framing §3.3, Options §7). It stays narrow only
  if most incidents are expressible in IaC (unknown, Options §8); layer 7 measures this.
- **On GitHub Team nobody sees the prod diff before apply** (⚠️ R4.6 #1; Team assumed, GĐ-5).
  Risky prod diffs stop the deploy until an owner of the stack approves the prod preview [design].
- **Admins can edit the gate**; logged, not prevented (logging 📖 R3.2.2; ability to edit ⚠️ R3.2.2,
  R3.6 #1). An admin's agent has
  the same power, because the agent uses its engineer's GitHub login (⚠️ R6.5 #10).
- **Some rules are process, not technology:** see "Process rules" in layer 1. The owner's rule
  "the PR approver is always an engineer, never an agent" (OD5) is absolute as policy, but on
  laptops it rests on policy, training and managed deny rules for `gh pr review` (OD25), which
  are hygiene: another form of the same call is not matched (📖 R9.4.1). An agent could still
  approve through its engineer's login. A review does not show whether it came from the web or
  the API (📖 R9.1.10); the approval-gate app only flags suspicious approvals (OD27). And "named"
  means a GitHub account that a register maps to a person: SAML SSO needs Enterprise Cloud
  (📖 R9.1.2), so on Team the mapping is a process (layer 1, OD25).
- **Incident approvers vs domain review:** code-owner review means an approver must own the file,
  at L2 as at L3. So that one on-call primary can approve any deployable path at 2 a.m., the on-call approver
  group co-owns every deployable path (owner decision OD9, layer 3). GitHub accepts an
  approval from any listed owner (📖 R3.2.7), so the approval-gate app enforces the rest (OD27,
  [design]): an on-call approval counts for another team's file only if the PR links an open
  incident and the approver is on shift. A label alone grants nothing, since anyone with Triage
  can apply it (📖 R9.1.9). Because on-call approvers only
  approve (OD7), a night incident needs two people awake: the incident responder and the on-call
  approver (the backup only replaces an unavailable primary).
- **One approver for most high-risk changes.** L3 changes in deployable code (IAM, stateful
  deletes, network) get one approver, like L2, from the owners of the path (the stack's owners for
  L3 content in domain files, OD8), and risky prod diffs stop for a look at the prod preview (OD2,
  OD8, layer 3). A single reviewer can miss things; this is the owner's trade-off for speed. The
  exception is the **process paths** (workflows, CODEOWNERS, agent config, catalogue, SCP and IAM
  stacks, risk stop): two L3 owner team members, enforced by the approval-gate app (OD26). They change
  rarely, are never urgent at night, and one compromised login must not be enough to change them.
- **k0s and Firebase are weaker:** no prod preview or risk stop, no break-glass when Actions is
  down (G1, G2), and their deploy credentials are stored in GitHub (OD1). For k0s, the interim
  controls of OD24 (a namespaced, time-limited deploy token and the Kubernetes API audit log) rely
  on `extraArgs`, which is "outside k0s support" (📖 R9.3.1).
- **New dependencies on two GitHub Apps** (required check, CI agent): if the required-check app is
  down, every merge to `main` is blocked, incident PRs included; that counts as "pipeline
  unavailable" for JIT. The required-check app now enforces OD26 and OD27 too, so it is a hard
  phase-1 prerequisite (rollout); its decision logic is an example (E12), its keys and hosting are
  open (G19). It is also the longest phase-1 item (10–15 person-days, ⚠️ estimate, OD35).
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
| Approver | Always an engineer, never an agent (owner rule, OD5). Named in CODEOWNERS; ≠ author, ≠ last pusher (📖 R3.2.3); for an app-opened PR, ≠ the person who triggered it (⚠️ R3.3.4, layer 5). Their GitHub account is in the login register (OD25). Process paths need two (OD26). |
| Incident responder | Engineer who diagnoses and writes the fix or the JIT request. Never the on-call approver of the same shift (OD7). |
| On-call approver | Engineer on the on-call schedule, primary + backup, 24/7; wait ≤ 15 min (S7). Approves another team's file only for a PR linked to an open incident while on shift, checked by the approval-gate app (OD27). While on call they only approve: they write no fix and file no JIT request, so the approver is always distinct from the author (OD7). The primary approves; the backup replaces an unavailable primary (OD2). No platform-team membership is required; all engineers follow one agreed approval procedure (OD2). |
| Data owner [design] | Named per tenant; co-approves real-data reads, or reviews a night-time read the next working day (layer 6). |
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
  - deny data-plane reads on claim stores except application roles and the approved data-read role,
    by `aws:PrincipalArn` (📖 R2.3.8; pattern ⚠️ R2.9 #4). Actions, e.g. `s3:GetObject`,
    `sqs:ReceiveMessage`, `states:GetExecutionHistory`, are incomplete and unchecked (⚠️ G13);
  - deny `lambda:UpdateFunctionCode` / `lambda:UpdateFunctionConfiguration` (⚠️ R4.6 #3) except
    CloudFormation `deploymentRole`s, the Pulumi prod deploy role (if Pulumi manages Lambdas) and the
    JIT roles. The Serverless prod deploy role is a separate role and is not exempt: it only passes
    the `deploymentRole` (examples finding 13). This closes `serverless deploy function`, which changes config outside CloudFormation
    (📖 R4.4.4), and needs `deploymentRole` set on every Serverless stack (key 📖 R4.4.5; need ⚠️ R4.6 #3);
  - a pre-deployed revocation Deny on `identitystore:UserId` (📖 R2.4.4); deny changes to any trail
    in prod accounts, since member accounts cannot touch the organization trail anyway (📖 R2.6.2;
    examples findings 10, 15);
  - exempt role names are protected: only the IAM stack's deploy role may create or change such
    roles (OD19), and from phase 1 that is a role of its own (OD22): the IAM stack deploys from a
    separate GitHub environment, `production-iam`, whose OIDC subject only that role trusts. So
    code running in a domain stack's deploy job cannot obtain it. Domain deploy roles (and the
    CloudFormation `deploymentRole` of each Serverless stack) may create or change only `svc-*`
    roles, and only with a fixed permissions boundary attached that they cannot remove or edit
    (pattern 📖 R9.2.1; role action list ⚠️; examples E4b). The boundary denies `iam:*` and
    root sessions. Cost: Lambda and ECS roles that read claim data (`app-claims-*`) live in the
    IAM stack and are referenced by ARN (examples finding 16);
  - deny every action of `OrganizationAccountAccessRole` in the prod OU (OD23). Organizations
    creates this role with "full administrative permissions" in each account it creates, trusted
    by the management account (📖 R9.2.4); SCPs cover it as any other member-account role
    (📖 R9.2.6, inference). Using it in an emergency needs an SCP change, an L3 path.
  - Limits: 10 SCPs per target, 10,240 characters; no SCP applies to the management account
    (📖 R2.3.2, R2.3.4), so whatever deploys SCPs there is the most sensitive role (L3 path, held by the L3 owner team only, not co-owned by the on-call group; OD13).
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
- **Who administers the administrators (OD23).** Whoever administers IAM Identity Center can
  assign themselves any permission set, so "no standing prod write" holds only if that power is
  itself controlled [design unless marked]:
  - permission sets and account assignments are code in an identity stack (an L3 path, L3 owner
    team only, not the on-call group), applied from CI; the only other writer is the JIT flow's
    automation, which creates and deletes `InfraOperator-*` and `DataRead-*` assignments;
  - an alert fires on Identity Center changes (`CreateAccountAssignment`, `CreatePermissionSet`,
    `PutInlinePolicyToPermissionSet`, `AttachManagedPolicyToPermissionSet` and the other events
    with source `sso.amazonaws.com`, 📖 R9.2.2) made by any principal other than those two;
    which account's trail records changes made from a delegated administrator is not documented
    (📖 R9.2.2 "not found"), so the organization trail covers both accounts;
  - day-to-day administration from a delegated administrator account (📖 R9.2.3). It cannot touch
    permission sets provisioned in the management account, which stays a smaller circle;
  - the management account: no workloads, a named group of at least two L3 owners with hardware
    MFA, reviewed quarterly (C-03). SCPs never apply there (📖 R9.2.6), so this group is a
    detective control only;
  - member-account root users: credentials removed through centralized root access; privileged
    root tasks run from the management account with `sts:AssumeRoot` (📖 R9.2.5).
- **Sessions/MFA:** portal session length set on purpose; an IdP session can extend it silently
  (📖 R2.1.5, R2.1.6). MFA lives in the external IdP if one is used (📖 R2.1.7).
- **CI → AWS:** GitHub OIDC, no stored keys (📖 R3.4.1). The prod role trusts only the `production`
  environment of the monorepo, in its `sub` format (📖 R3.4.3, R3.4.4; immutable format assumed,
  ⚠️ R3.7 A2), ideally customised with the deploy workflow's `job_workflow_ref` (📖 R3.4.5; on Team ⚠️ G10).
- **CI → GCP (OD36):** Workload Identity Federation. Google requires a condition that limits the pool
  to Papaya's GitHub organization and advises the numeric `*_id` claims, which cannot be reused (📖
  [WIF with deployment pipelines](https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines);
  R3.4.5b). Narrower than that, as on AWS [design]: the pool condition also names the monorepo by
  `repository_id`; `google.subject` maps `assertion.sub` (📖 same page), so the subject carries the
  environment (`repo:…:environment:production`, 📖 R3.4.3); and only the `production` subject may
  impersonate the prod service account. Granting by subject rather than by a mapped attribute is
  ⚠️ (the page shows the `principalSet …/attribute.` form, which works with an `environment`
  attribute mapped from the token: also ⚠️, since the page lists no GitHub `environment` claim).
  Vertex AI model and endpoint changes deploy this way, from the monorepo, like any other stack.
- **GCP for humans and agents (OD36) [design unless marked]:** no standing role on prod projects for
  people. Agents and engineers get a custom read-metadata role (no `storage.objects.get`, no Vertex
  prediction calls such as `generateContent`, which is a data read, 📖 R9.6.3); writes and data reads
  come from Privileged Access Manager entitlements with approval, time-bound (30 min to 7 days, 📖
  R9.6.1), approved by the on-call approver. Whether PAM stops a requester approving their own
  grant is not documented (📖 R9.6.1 "not found"), so the entitlement lists the on-call group as
  approvers and the engineers as requesters, tested in phase 2. Data Access audit logs are off by
  default except BigQuery (📖 R9.6.3), so they are switched on for Vertex AI and for the buckets
  that hold partner documents; cost: log volume. The HIPAA list names the renamed products
  ("Generative AI on Agent Platform"), not "Vertex AI Gemini API" (📖 R9.6.4): Papaya confirms in
  writing with Google that its use is covered before PHI goes there.
- **Firebase Hosting (OD36):** not on the GCP BAA list (📖 R5.5.3), so it holds no PHI (⚠️ R5.7 #7).
  Deploy: the official action needs a service-account JSON key (📖 R9.6.5), kept as a secret of the
  `production-k0s` environment (OD24). A phase-2 spike tries WIF (`google-github-actions/auth`
  writes an Application Default Credentials file, 📖 R9.6.5) with `firebase deploy`; no official
  page says that works (📖 R9.6.5 "not found"). If it does, the key goes. Rollback creates a new
  release that serves an earlier version (console or `firebase hosting:clone`, 📖 R9.6.6): in an
  incident, a revert PR, or JIT when Actions is down. Preview channel URLs are public to anyone with
  the link (📖 R9.6.6), so previews come from the non-prod Firebase project only.
- **k0s for humans (OD36):** today kubeconfigs, no SSO (GĐ-4, unconfirmed). Target: OIDC through the
  API server's `extraArgs` (`oidc-issuer-url` and related flags) against Papaya's identity
  provider, which k0s documents but places outside its support (📖 R9.6.9); IdP groups map to a
  read-only ClusterRole without Secrets, exec or logs of claim services. Client-certificate
  kubeconfigs from `k0s kubeconfig create` are valid one year and "cannot be revoked" (📖 R9.6.9),
  so after OIDC works none is issued to a person except one break-glass admin certificate in the L3
  owner team's sealed store, alerted on use through the API audit log (E11). Interim: no admin
  kubeconfig and no GCP owner role on laptops; prod deploys only from CI.
- **k0s deploy identity (OD24).** Interim, phase 1: the CI credential is a time-limited
  ServiceAccount token, not an admin kubeconfig, bound to a namespaced Role that cannot read
  Secrets, exec into pods, read pod logs, issue tokens, change RBAC, impersonate or delete
  (📖 R9.3.6, R9.3.7; examples E11). Creating a workload grants it the API access of any
  ServiceAccount in its namespace (📖 R9.3.7), so deploy namespaces hold no privileged
  ServiceAccount. Target: kube-apiserver trusts GitHub's OIDC tokens directly through structured
  authentication, stable from Kubernetes 1.34 (📖 R9.3.4), so nothing is stored in GitHub; k0s
  does not document it (📖 R9.3.5), the API server must be reachable from the runner (📖 R9.3.8),
  and the claim rule must use the repository's real `sub` format (📖 R9.3.9).

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
  | `permissions.deny` / `ask` | Deny credential paths (R5.5.4; `Read(...)` syntax ⚠️ R1.8 #5), and from phase 1 `Read(~/.config/gh/**)`, `Bash(gh pr review *)` and `Bash(gh api *reviews*)` (OD25; patterns 📖 R9.4.1, hygiene only). Ask for `WebFetch`, which the sandbox domain list does not limit (R1.6.2); cost: a prompt per fetch. The HIPAA template denies WebFetch (R5.5.4); "ask" is a deliberate deviation so that documentation lookups still work. Ask for `Bash(aws *)`, `Bash(pulumi *)`, `Bash(serverless *)`, which prompts even in auto mode (📖 [auto mode config](https://code.claude.com/docs/en/auto-mode-config.md); examples finding 22). Credential denies extend to the known credential stores of Papaya's stack; some paths are ⚠️ and some stores are not covered (examples E8, with every deviation from the template). |
  | `requiredMinimumVersion` | ≥ 2.1.310 in phase 2: 2.1.285 for `allowedProviders` (R1.1.15), 2.1.310 so `allowManagedHooksOnly` also blocks monitors of plugins that are not force-enabled (📖 [settings reference](https://code.claude.com/docs/en/settings-reference.md#allowmanagedhooksonly)); which also covers `--restricted` (2.1.248, R6.9.1b) and the plugin-pin fix (2.1.179, R6.2.7); ≥ 2.1.295 if any managed hook uses `onFailure: "block"` (R1.5.2); and ≥ the latest fixed advisory at rollout (R6.3.9). It does not end running sessions and fails open on a bad value (R1.1.13). |
  | `allowedProviders` + `forceLoginOrgUUID` | `["anthropic"]` + Papaya's org; closes most bypasses on **endpoint-managed** machines (R1.1.15). `forceLoginOrgUUID` checks claude.ai sign-ins only, not Claude Console sign-ins (R5.5.5); with it set, sessions on `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` or `apiKeyHelper` are refused (R1.11.3.11). |
  | `allowManagedHooksOnly` | `true` (R1.5.4). |
  | `autoMode` | `classifyAllShell: true` and the template's `"$defaults"` pins, which keep the built-in rules; not a boundary (examples finding 25). |
  | sandbox | `sandbox.enabled`, `failIfUnavailable`, `allowUnsandboxedCommands: false`, narrow `network.allowedDomains` locked by `network.allowManagedDomainsOnly`; `credentials` / `filesystem.denyRead` on `~/.aws` and the other credential stores, which the sandbox can otherwise read (R1.6.3, R1.6.4). Reads are a denylist and allowed domains are exfiltration paths; `git push`, `gh`, Docker and private-registry `npm ci` fail inside the sandbox (limits and costs: examples E8). |
  | `sandbox.autoAllowBashIfSandboxed` | Left at its default `true` (owner decision OD12). This widens D1's "Manual + allowlist": every sandboxed command, writes in the working directory and calls to allowed domains included, runs without a prompt. Detail: sandboxed Bash runs without a prompt, so in Manual mode prompts are for edits, unsandboxed commands and fetches, not every command (R5.5.5b). A deliberate choice: the sandbox (no `~/.aws`, allowlisted network) is the control for those commands. The HIPAA README says to set `false` if policy needs a person to approve each command (R5.5.5b); cost of `false`: a prompt per command. |
  | MCP, plugins | Layer 4. |
  | OTel | Exporter on, content flags `0` (R1.1.20, R5.5.4). |

- **Trade-off on AWS credentials [design].** With `~/.aws` hidden from the sandbox, phase 2 lists
  `aws *`, `pulumi *` and `serverless *` in `sandbox.excludedCommands`. Excluded commands run "with
  full access" (📖 R1.6.4), network included ("no filesystem restrictions and no network proxy", 📖 [sandboxing](https://code.claude.com/docs/en/sandboxing.md#run-commands-outside-the-sandbox-with-excludedcommands)). Matching follows `Bash(...)` rule
  syntax on the command text (same page; details in examples finding 22); each excluded
  call prompts through the `ask` rules above. This is worse than an
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
  | Daily development (laptop) | non-prod roles + `ProdReadMetadata` | baseline | Auto mode by choice (D1); `--restricted` recommended (D3). |
  | Incident analysis (laptop) | meant to be `ProdReadMetadata` only | `--restricted --strict-mcp-config --tools "Bash,Read,Grep,Glob"`, started in an empty scratch directory, not the repo [design] | Process rule (D3, research 6.9.4 Q1–Q2). No WebFetch, and file tools confined to the working directory (📖 R6.9.1b). `--tools` sets the list of available built-in tools, so Edit and Write are not in it (✅ `claude --help`, 2.1.319). `--restricted` still loads MCP servers unless `--strict-mcp-config` is added (✅ same help text), so with it and no `--mcp-config` the session has no Linear or Slack tool to post through. Bash can still write in its working directory (📖 R1.6.3) and call any role in the cache. Skills of the internal plugin load because managed settings force-enable it (OD47). |
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
  `aws`, `pulumi` and `serverless`, which prompt in auto mode too (📖 [auto mode config](https://code.claude.com/docs/en/auto-mode-config.md)),
  so an agent cannot run a cloud CLI with the engineer's still-writable session without a person
  confirming it. Auto mode itself stays allowed (D1). Bash rules are not a boundary (📖 R1.2.6):
  a script that calls the AWS SDK directly is not caught.
- **Hard limits:** Bash rules are not a boundary (📖 R1.2.6); hooks fail open unless
  `"onFailure": "block"` (📖 R1.5.2); `--restricted` cannot be forced by a setting (📖 R6.9.1), and a `PATH` wrapper on laptops can be bypassed (⚠️ R6.9.1c);
  on laptops **without MDM**, a different login, an API key or a `CLAUDE_CODE_USE_*` variable skips
  server-managed settings, `allowedProviders` included (📖 R1.1.7; ⚠️ R1.8 #3, G11). So S5's
  "nobody can turn off all prompts unnoticed" is likely unreachable without MDM (⚠️).
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

**Principle.** The level is set by the damage a change can do. One default path above non-prod: a
reviewed PR applied by the pipeline, with the JIT fallback (layer 7) as the only other write path.
The approver reviews the code change that will be applied. By default a prod change needs two
people: one who makes it and one who approves it; the on-call backup only replaces an unavailable
primary (OD2). Higher risk narrows **who** may approve (the owners of that path), not how many, with
two exceptions: a process path needs two L3 owner team members (OD26), and a PR that touches files of
several teams needs an owner of each, except in an incident (OD27). Separately, any prod diff that looks risky stops the deploy, whatever its level; that adds a
second approval by an owner of the same stack, which keeps it to two people (OD8). Confirmed by the owner
(OD13): the original author opens the approval PR and the first approver
approves it. If the first approver is unavailable, another owner of the stack approves; that makes
three people and is recorded as a deviation, counted monthly (OD11). A cross-team PR needs an
approval from an owner of each team's files: OD10 allowed one on-call group member to cover them
all, but since OD27 that counts only for an incident (layer 3, "Who approves at night"). A real-data read is not a change and has its own rule, L3-data. Incidents use the same
path with faster people, not fewer security checks.

| Level | What | Examples | Approval | Path |
|---|---|---|---|---|
| **L0** | Read: non-prod anything; prod metadata | metrics, redacted logs | none | read-only identity |
| **L1** | Change in non-prod | deploy a branch to dev; `pulumi preview` on non-prod (needs state-write permission on a DIY S3 backend, 📖 R4.3.3) | author only | non-prod roles or PR pipeline |
| **L2** | Routine prod change in code | Lambda timeout/memory, ECS desired count, release | 1 code owner ≠ author, ≠ last pusher | PR → `main` → deploy workflow |
| **L3** | High-risk prod change | IAM/SCP; replace/delete of stateful resources; network; `.github/**`, CODEOWNERS, `CLAUDE.md`, `CLAUDE.local.md`, `.claude/**`, `.claude.json`, `.mcp.json`, `.husky/`, `.gitmodules`, `.ripgreprc`, plugin/MCP catalogue and the rest of the canonical list in layer 5; advisory policy finding | 1 code owner ≠ author, ≠ last pusher. L3 process paths (workflow and agent-config files, catalogue, the SCP stack and the rest of the layer-5 list): **2** members of the L3 owner team (OD13, OD26). The IAM stack and its risk-stop approvals are process paths too (OD32): they create and re-trust the SCP-exempt roles and the permissions boundary, so on-call does not co-own them and a night change there uses JIT. That is rare by design: the IAM stack holds only those roles and the boundary (OD22); a service's everyday permissions live in its domain stack as `svc-*` roles under the boundary, which on-call can approve in an incident. L3 content inside a domain file (an IAM statement in `serverless.yml`, a stateful delete): the stack's owner, then the risk stop (OD8). In incidents: the on-call approver for deployable paths (OD9); paths that define the process (CODEOWNERS, agent config, catalogue, workflows) wait for the L3 owner team | same path; for IaC changes the risk stop also applies; workflow and agent-config files have no prod diff |
| **L3-JIT** | Break-glass | ECS force-redeploy while Actions is down | on-call approver ≠ requester (Options §4b); incidents only, as the author accepted it, for Papaya's sign-off (Options §9 Q2); the on-call approver counts as owner of the service in the request (OD13) | layer 7 |
| **L3-data** | Real customer data read | one tenant's failed claim record | an approver ≠ requester and an agreement (GĐ-9); data-owner co-approval [design], beyond GĐ-9; at night, see layer 6 | layer 6 |
| **L3-data-write** | Data fix on one tenant's records | retry a stuck payout | a code owner plus a different member of that tenant's data-owner team, checked by the approval-gate app; in an incident the on-call approver stands in and the data owner reviews next working day (OD29) | PR → `sql` deploy job ("Database changes" below) |

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
  - **Running it [design; ⚠️ not researched beyond E12]:** the app runs in a dedicated tooling
    AWS account, outside prod and non-prod workloads; its private key sits in that account's
    secrets store, readable only by the app's role, and is listed in the secrets inventory with an
    owner and rotation (C-14), like the S2 exceptions; its code has its own repository with the
    marketplace's rules (two L3 approvals). It **fails closed**: no answer means no merge. If it is
    down during an incident, the pipeline counts as unavailable and JIT applies (layer 7). If it
    is down for longer, removing its check from the ruleset is an admin edit of the gate (T13):
    allowed only with two L3 owner team members' approval recorded in a ticket, alerted
    (`repository_ruleset.update`), and reverted when the app is back. A workflow
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
  comparison includes the group's member list. An approval from any listed owner satisfies
  code-owner review (📖 R3.2.7), so on its own GitHub would let a member approve another domain's
  PR on a normal day. **OD27 makes the rule technical** [design]: the approval-gate app counts an
  on-call member's approval for a file of another team only if the PR carries the `incident`
  label, links an incident that is open when the check runs, and the approver is primary or
  backup on shift. The label alone grants nothing, since anyone with Triage can apply it
  (📖 R9.1.9). In phase 1 the open incidents are incident issues in Linear and the shift comes from
  `oncall/schedule.yaml`, an L3 path whose content engineering management decides; from phase 2
  both come from the paging tool (G5). The monthly report lists every PR labelled `incident` with
  its incident, the incident's creator and the approver (layer 7). Residual: in phase 1 anyone can
  open an incident issue, so the report, not the app, catches an invented incident. Cost: a stale schedule file blocks a night approval until
  the backup or a domain owner approves; on normal days a cross-team PR needs an owner of each
  team. Whether Papaya's team size allows full coverage is unknown (§1, S7).
- **GitHub plan: Team or Enterprise Cloud (OD44).** Several controls here work around GitHub
  Team. Enterprise Cloud lists at $21 against $4 per user per month (📖 R9.1.3, read 2026-11-09).
  What the upgrade replaces, and what stays custom either way [estimates ⚠️, as in the rollout plan]:

  | Built here for Team | With Enterprise Cloud | Effort saved |
  |---|---|---|
  | GitHub login register from HR joiners and leavers (OD25, rollout 1.21) | SAML SSO ties each GitHub login to the identity provider (📖 R9.1.2) | 1–2 pd, plus monthly upkeep; closes "a GitHub login tied to the identity provider" in the README's "does not give" |
  | Monthly manual audit-log export (C-21) | Audit-log API and streaming (📖 R9.1.5, R9.1.6) | about half a day a month, and the 180-day gap risk |
  | Prod diff seen only when the risk stop fires | Environment required reviewers on private repos (📖 R9.1.4): a risky deploy can wait for a reviewer who sees the preview (only risky deploys waiting, e.g. through a second environment used after the risk stop fires, is [design] ⚠️) | part of the approval-PR mechanics of 1.14; closes "prod diff unseen" in §1 |
  | Approval-gate app rules R1–R4, W1 (E12), JIT receiver, risk-stop classifier, database path, evidence bucket (6 years is longer than any GitHub retention) | unchanged: no GitHub rule found that counts on-call approvals only in an incident, needs a tenant's data owner, or classifies a prod diff | none |

  **Recommendation:** the saving in build effort is small (roughly 5–10 person-days once and
  6–10 a year, ⚠️); the case for the upgrade is Compliance's: approvals tied to the identity
  provider and a prod diff seen before apply. For 50 users the difference is about $10,200 a
  year (⚠️ Papaya's user count unknown). Recommended: move to Enterprise Cloud in phase 2, before
  the first ISO evidence pack (rollout 3.4), if Papaya has up to about 100 GitHub users [design
  threshold]; above that, decide with the measured value of the manual steps. The design does not
  depend on it: everything here works on Team (GĐ-5).
- **Risk stop [design]:** applies to every deploy, whatever the level. The deploy job previews prod;
  on stateful replace/delete, an IAM change, a network or security-group change, or an advisory
  policy finding (from phase 2) it stops and posts the filtered preview. The original author opens a second PR that adds
  `deploy-approvals/<stack>/<sha>.yaml` (`<sha>` = the stopped commit) holding that SHA and the
  preview hash; the workflow does not open it, because the setting that lets Actions create and approve PRs stays
  off (📖 R3.3.3; ⚠️ R3.6 #3). CODEOWNERS on `deploy-approvals/<stack>/` names the owners of that stack and the
  on-call group (OD8, OD9). The approver is ≠ author and may be the first PR's approver, who now sees
  which prod resources and properties change; values stay out of the summary to keep secrets out
  of logs, and are reviewed in the code of the stopped PR. Merging it triggers the deploy on the new HEAD, which previews again and continues
  only if the hash matches the approved one; if another PR merged in between, the hash differs and
  the deploy stops again (Options §1; hash stability ⚠️ Options §8). The approval is bound to git
  history, not only to the hash (six conditions, 7-day expiry; examples E7, finding 2) [design].
  Known gap (OD18): an early approval can match a later change outside the stack (G19 closes it: the app checks that the stopped run's summary carries the same hash).
  The stop catches risky diffs nobody looked at, not approved malicious code (OD15); OD22 limits what such code can reach (layer 5). Cost: while a stack is
  stopped, later merges to that stack stop too until a matching approval lands; in an incident, a
  risky change already waiting on `main` blocks the fix for the same stack until it is approved or
  reverted. A
  `mandatory` policy violation always blocks `pulumi up` (📖 R4.2.2): the fix is a code change, or a
  change to the policy pack through its own L3 PR. Preview output is filtered for
  outputs and secrets before it is posted (Options §1; ⚠️ R4.6 #2).
- **Database changes (OD29, ADR-0011) [design].** Aurora schema migrations, GraphQL-engine
  (Hasura) metadata and data fixes are files under `db/<service>/`, merged like code and applied by
  a `sql` job of the deploy workflow (examples E3):
  - where it runs [design]: Aurora is reachable only inside the prod VPC, and layer 5 avoids
    self-hosted runners, so the GitHub-hosted job never connects to the database. Its OIDC role may
    only start one ECS task definition (`db-change-<service>`) on one cluster, pass that task's two
    roles, and use one S3 prefix, and it trusts only the `production-db` environment, so no other
    deploy job can obtain it (examples E15). The bundle hash proves integrity between the job and
    the task; approval comes from the job itself, which runs only reviewed L3 code from `main`. The one-off Fargate task runs in private subnets
    from an image pinned by digest; its role may only `rds-db:connect` as the migration user (IAM
    database authentication, 📖 R9.2.11). ECS lets the caller override the command and environment
    of a task (📖 [RunTask](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_RunTask.html)),
    so the task re-checks the SHA-256 of the file bundle the risk stop classified and refuses any
    other; `ecs:ExecuteCommand` is denied. That `iam:PassRole` is what lets a caller start a task
    with a role is ⚠️ recalled, not checked in this round;
  - GraphQL-engine metadata is not a database change: the task applies it with
    `hasura metadata apply`, which needs the engine's admin secret and replaces all metadata
    (📖 [Hasura CLI](https://hasura.io/docs/2.0/hasura-cli/commands/hasura_metadata_apply/),
    [manage metadata](https://hasura.io/docs/2.0/migrations-metadata-seeds/manage-metadata/)). The
    secret sits in Secrets Manager and reaches only the task, through its task definition. No
    person holds database credentials or the admin secret day to day; a break-glass role that
    can read Secrets Manager can read it, which the JIT record shows (layer 7);
  - it lists the pending files through `tools/db/` wrappers around Papaya's migration tool (an L3
    path; the tool is not known here), runs the risk stop on them with `--tool sql`, and applies
    exactly the classified files, each in its own transaction;
  - the SQL risk stop (a heuristic, not a parser; examples E7) stops on DROP, TRUNCATE, column type
    changes, DELETE or UPDATE without a top-level WHERE, grants, roles, row-level security, COPY,
    function bodies and `EXECUTE`; every metadata change stops too, because it holds row
    permissions per role, i.e. tenant isolation; and any INSERT, UPDATE or DELETE inside a
    migration stops, because data changes belong in `data-fixes/<tenant>/`, where the data owner
    approves;
  - data fixes (`db/<service>/data-fixes/<tenant>/<ticket>.sql`) touch one tenant, declare
    `-- expected_rows: N`, and are rolled back when the count differs; approval is L3-data-write
    (table above); the job summary shows statement kinds and row counts, never values;
  - a data fix names records only by opaque internal IDs, because the file stays in git and every
    engineer and agent session can read it (OD48). A sensitive value the fix needs (a corrected
    bank account) goes into a values file that the data owner puts in the `db-change` bucket,
    which only the in-VPC task reads; the SQL refers to it as a psql variable [design]. A required
    check, `data-fix-scan`, fails a PR whose data fix matches one of the masking identifiers of
    layer 6 or holds a run of 9 or more digits (examples E19);
  - IAM database authentication is not in CloudTrail (📖 R9.2.11), so database-side evidence comes
    from Database Activity Streams (layer 7). Expand/contract migrations are recommended, not
    enforced. Cost: a data fix takes a PR and two approvals instead of a `psql` session.
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
usually by the same approver, when the risk stop fires (OD13; OD11). Cross-team PRs: an owner of each team on normal days, one on-call approver in an incident (OD10 as narrowed by OD27). None in non-prod.
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
- **Pinning what every laptop runs (OD26).** A plugin, hook or local MCP server runs on every
  engineer's laptop, outside the sandbox, with that engineer's GitHub and AWS sessions. One
  compromised entry would hand an attacker many logins at once, enough to be both author and
  approver of a PR (threat T23). So nothing that reaches laptops follows a moving branch [design
  unless marked]:
  - managed settings pin the marketplace to one release tag: marketplace sources take a `ref`,
    with no `sha` field (📖 R9.4.4; a community schema describes `ref` as "branch, tag, or SHA",
    a SHA there is ⚠️ untested). In the marketplace repository, release tags can be created only by
    the L3 owner team and never moved or deleted, and every change needs two approvals (rulesets,
    examples E9b);
  - every plugin entry, internal ones included, carries a commit `sha` (📖 R9.4.5) and a review
    record; a relative `./plugins/…` source is not used, because it follows the marketplace's files;
  - auto-update stays off for the marketplace, locked through managed `extraKnownMarketplaces`
    (📖 R9.4.6); an update is a reviewed change of the pin;
  - engineers keep the GitHub CLI token in the system credential store; `gh` falls back to a
    plain-text file when there is none (📖 R9.1.11), so the guide asks them to check `gh auth status`.
  Cost: a plugin release takes three reviewed steps (change, tag, settings), and onboarding a local
  MCP server means packaging it (next bullet).
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
  service-account key for Firebase Hosting. The owner accepts this as an exception to S2 = 0 until it
  is checked whether k0s and Firebase deploys can use OIDC (OD1, OD6). Conditions [design]:
  - stored only as an **environment secret** of a protected environment (`production-k0s`, below), never as a repository secret. Anyone
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
    runner is dedicated to the `production-k0s` deploy, and the residual risk is recorded;
  - that environment secret is the single source of truth: no copy elsewhere (OD1);
  - an owner, an expiry and rotation in the exception register;
  - a separate environment `production-k0s` (required since OD24, was optional), limited to
    `main` and referenced only by the k0s/Firebase deploy workflow, so AWS deploy jobs cannot read
    these secrets [design];
  - for k0s, the credential is the namespaced, time-limited ServiceAccount token of layer 1
    (OD24), rotated before it expires, and the cluster writes a Kubernetes API audit log: k0s has
    none by default and enables it only through `spec.api.extraArgs`, "outside k0s support"
    (📖 R9.3.1, R9.3.2). Secrets and token requests are logged at `Metadata` level so their
    contents stay out of the log (📖 R9.3.3; examples E11). A leaked token is then limited to
    deploys in its namespaces and leaves a trace; shipping that log to the log archive is part
    of G1.

  Residual risk: admins can change the environment, and a deleted environment comes back without
  protection (⚠️ R3.1.4); the alerts and settings comparison in layer 7 cover this. The exception
  covers **CI deploy credentials only**. Runtime credentials, such as a k0s autoscaler's AWS access to
  add or remove nodes, live in the cluster, not in GitHub; they follow layer 1 (no static keys, a
  role attached to the machine; ⚠️ not researched for k0s, G1).
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
  installed app on a channel without a store review (📖 R9.8.1, R9.8.2), so it is a prod write path:
  - the `production` channel and the build and submit credentials are protected in Expo; only
    Release Manager, Admin or Owner may publish, republish, roll back or change rollout there
    (📖 R9.8.5). No person holds those roles day to day; the CI publishes as a robot user with the
    Release Manager role from a job in its own environment, `production-mobile` (limited to `main`,
    used by the mobile release workflow only, like `production-k0s`), so only a run of a merged
    `main` reaches the token and AWS deploy jobs cannot read it (layer 3; examples E3b);
  - Expo has no OIDC for GitHub (📖 R9.8.7 "not found"), so the robot token is a long-lived secret
    in that environment, on the secrets inventory (S2 exception, like k0s/Firebase), rotated;
    Owner and Admin can remove the protection: at least two named Owners, in the identity register;
  - updates are signed (EAS Update code signing; Production or Enterprise plan, 📖 R9.8.8): the app
    carries the certificate, and the private key lives only in `production-mobile`, so a stolen
    Expo token alone cannot ship code. Whether the app rejects an unsigned update is not stated
    plainly (⚠️ R9.8.8): tested before relying on it. The certificate in the repository is an L3
    path (CODEOWNERS, examples E2);
  - EAS Workflows cannot publish to a protected channel (📖 R9.8.11), and Expo's GitHub app is not
    connected for prod triggers; production builds and store submissions run from the same CI job;
    Android submissions go to a draft release that a person finishes in Play Console (📖 R9.8.13);
  - evidence: Expo's audit log is Enterprise-only and does not list update publishes (📖 R9.8.9),
    so the nightly evidence export also compares the updates on the `production` channel with the
    deploy runs and merged commits; an update without a run is an incident;
  - rollback is `eas update:republish` of the previous update or `eas update:rollback`, both
    protected actions (📖 R9.8.3): a revert PR in the normal lane, JIT on the robot in an incident.

**Audit evidence.** Workflows and lockfile in git, the secrets inventory and exception register (S2), audit-log events for secrets and Actions settings, and check results per PR; full register: [04-compliance-mapping.md](04-compliance-mapping.md#register).

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

- **Audit stores:**
  - organization CloudTrail to a log-archive account with integrity validation (📖 R2.6.2, R2.6.4,
    R2.6.5); change records ≥ 6 years; raw-log retention for Papaya's compliance owner (⚠️ R5.7 #2).
    Data events only on PHI buckets, prod Lambda invoke and prod SQS (cost 📖 R2.6.3; selection
    ⚠️ R2.9 #5), which makes the archive
    PHI-bearing (⚠️ research 1.11.4 L15). CloudTrail Lake is closed to new customers (📖 R2.6.6);
  - **evidence bucket** (OD30) [design]: an S3 bucket in the log-archive account with Object Lock
    in compliance mode, 6 years, which nobody, root included, can shorten or delete (📖 R9.2.12;
    a new bucket, since enabling it on an existing one was not confirmed). From phase 1 a nightly
    workflow writes the last day's merged PRs with their reviews and check runs, and the logs and
    artifacts (`risk-summary`) of deploy runs, through a role that may only `PutObject`
    (examples E13). Actions keeps logs 90 days by default, at most 400 (📖 R9.1.8): set 400 as
    a buffer;
  - GitHub org audit log kept 180 days (📖 R3.5.6). Its REST API is documented for Enterprise
    Cloud, not Team (📖 R9.1.5), so an org owner exports it monthly from the UI (JSON) into the
    evidence bucket, a manual step in the monthly report (📖 R9.1.7);
  - **JIT and real-data request records** (OD30): an issue in a dedicated Linear team, from a
    template with required fields (command list or store, scope, tenant, reason, incident link,
    agreement); the approver approves by moving it to an "Approved" state. Linear's audit log is
    Enterprise-only and kept 90 days, and its CSV export has no field history (📖 R9.1.14), so a
    webhook receiver in the tooling account (the approval-gate app's) writes every change, with
    the previous values Linear sends, to the evidence bucket. Not Slack;
  - alerts on `repository_ruleset.update`, `environment.update_protection_rule`,
    `environment.remove_protection_rule`, `environment.delete`, `protected_branch.policy_override`
    (📖 R3.5.6, R3.1.4; selection ⚠️ R3.6 #1). UI changes to the branch policy may leave no event, and a
    deleted `production` environment comes back unprotected (⚠️ R3.1.4): a job compares live settings
    with an expected copy (G8);
  - Aurora SQL is likely invisible to CloudTrail (⚠️ R2.7.1): Database Activity Streams, alerts on
    lost-record events (📖 R2.7.2; Serverless v2 ⚠️), stream treated as PHI (⚠️ R2.7.3);
  - Claude Code OTel without prompt content (layer 2);
  - Kubernetes API audit log of prod k0s (OD24, layer 5); destination open (G1).
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
  The schedule is also an input of the approval-gate app (OD27): in phase 1 it is the file
  `oncall/schedule.yaml` (an L3 path) and open incidents are incident issues in Linear, created
  before the PR is linked. The monthly report lists every `incident` PR with its incident, approver
  and shift, and every approval the app flagged (layer 3).
- **Alerts and incident declaration, target (OD38) [design unless marked].** Today alerts are
  spread over CloudWatch, GCP and Slack, with no paging (brief). Target, built in phase 2 (item 2.8):

  | Step | Design |
  |---|---|
  | Sources | CloudWatch alarms → SNS topics per severity; GCP Cloud Monitoring alert policies; GitHub audit alerts and the evidence-reconciliation jobs (layers 3, 7, OD40) |
  | Paging | One paging tool (product open, a decision for Papaya: G5) holds the on-call schedule and pages the primary, then the backup. SNS reaches it through an HTTPS subscription; SNS cannot call private endpoints (📖 R9.6.7). GCP sends to it directly and also to email or Pub/Sub, because Google states that Slack, PagerDuty, webhook and mobile channels "share a single point of failure" (📖 R9.6.8). AWS Incident Manager is not an option: closed to new customers since 2025-11-07 (📖 R9.6.7) |
  | Chat | Amazon Q Developer in chat applications (formerly AWS Chatbot) posts SNS notifications to one Slack alerts channel (📖 R9.6.7); the paging tool opens one Slack channel per incident |
  | Severities | SEV1: claims cannot be submitted or paid, or data exposure suspected → page now, 24/7, open an incident. SEV2: degraded for one tenant or a backlog that will breach the insurer SLA → page in working hours, at night only if it grows. SEV3: ticket. Thresholds per service with the service owners [design] |
  | Escalation | Responder unanswered after 10 min → backup responder; approver unanswered → backup approver (OD2); no answer after 20 min → engineering manager on call [design times] |
  | Declaration | The responder (or the paging tool) opens the Linear incident issue with severity and tenant; that open issue is what the approval-gate app and the JIT receiver read (OD27, OD33). A suspected data exposure also starts the breach-notification clock of the tenant's country (compliance register, C-26) |
  | Agents | The incident-analysis session (layer 2) starts from the alert: metrics and masked logs through `ProdReadMetadata`; it proposes a fix, the responder writes the PR (layer 3) |

  Approving a PR from a phone works through GitHub Mobile (⚠️ not checked for code-owner reviews);
  until it is, the approver uses a laptop. The routing is the same for AWS and GCP from day one of
  phase 2; k0s alerts follow its monitoring stack (not known here, ⚠️).
- **Break-glass = JIT fallback** [design unless marked]:

  | Step | Rule |
  |---|---|
  | When | Only during an incident (Options §9 Q2), when the PR path cannot be used: operation not in IaC and no runbook; GitHub/Actions down; pipeline broken. The approver refuses JIT for anything expressible in IaC while the pipeline works, and records why. Outside incidents, an operation not in IaC waits for IaC or a runbook. |
  | Request | Command list, scope, reason, incident link, in a channel that does not depend on GitHub. |
  | Approval | On-call approver ≠ requester, before the grant (Options §4b; OD7; backup rule OD2). The approver moves the Linear request to "Approved"; a receiver in the tooling account (next to the approval-gate app) gets the signed webhook (📖 [Linear webhooks](https://linear.app/developers/webhooks): HMAC-SHA256 `Linear-Signature`, `actor`, `updatedFrom`) and grants only if the signature is valid and fresh, a person made the change, the approver ≠ the requester as Identity Center users (people register, OD25), the approver is on shift, the incident is open and the permission set is an allowed `InfraOperator-*` (OD33; examples E16). One grant per request: a retried webhook or a second move to "Approved" grants nothing (Linear retries up to 3 times, 📖 same page). The receiver's role may assign only permission sets tagged `jit-grant`, in the prod accounts, and may never create, change or re-tag a permission set (examples E16; resource types ✅ AWS Service Reference). Linear accounts sign in through single sign-on and are in the people register (Linear plan for SSO ⚠️ not checked). The AWS TEAM sample is compared with the receiver before building it (rollout 1.13). If the receiver is down, an L3 owner team member grants by hand against the same checklist; the Identity Center alert (layer 1) fires on it and the monthly report reviews it. |
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
  this draft); grants needed because the IAM stack had to change (OD32; review above one per
  quarter [design]: then an incident rule of on-call approver plus one L3 owner team member by
  phone is considered, keeping the PR path). On a breach,
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
- **Metrics:** S1–S11 exactly as in framing §5; this framework adds the JIT metrics (layer 7) and the
  prompt metrics (layer 2). S2 and S5 have caveats (OD1; layer 2).
- **Rollout** (≈ 100 days, re-baselined from GĐ-12's 90 after the effort estimate, OD49): [`03-rollout-plan.md`](03-rollout-plan.md), moved
  there with its items unchanged except syncs with the examples' findings (trail deny, allowlist,
  phase-2 version floor), and expanded with owners and checks [design]. Order (framing Q8): (1) remove long-lived CI credentials, (2) narrow standing prod
  access, (3) MCP/plugin catalogue; the on-call approver list before or with (2). Phase 1 (days 0–45)
  makes the PR the default prod write path, with eight hard prerequisites before standing prod write is
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

## Gaps (not covered, or only as an open item, in `work/02-research.md`)

| # | Gap | Layers |
|---|---|---|
| G1 | k0s: OIDC for humans designed (OD36), not tested on Papaya's version; placing the audit policy on controllers and shipping the audit log; the target OIDC trust for CI (OD24 gives interim controls); break-glass when Actions is down | 1, 3, 6, 7 |
| G2 | Firebase Hosting deploy from CI without a stored key: a phase-2 spike (OD36); break-glass when Actions is down | 1, 5, 7 |
| G3 | GCP: the read-metadata role's permission list and PAM self-approval are not checked (OD36); BAA coverage of the renamed Vertex products to confirm with Google | 1, 6 |
| G4 | Tool choice where no licence is bought (secret scan, SAST, dependency scanner); non-prod data scanning; k0s admission (OD39) | 5, 6 |
| G5 | Choice of the paging tool; alert thresholds per service; approving a PR from GitHub Mobile (routing designed, OD38) | 7 |
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
| G19 | Required-check app and CI-agent app: review-event triggers, source pinning against same-name checks, hosting, private-key storage and whether those keys count against S2; the app's check that a risk-stop approval matches the stopped run's hash (OD18); reading Linear incidents and the schedule (OD27). The decision logic itself is examples E12 | 3, 5 |
| G20 | Emergency revocation at night: who can apply the revocation Deny SCP (management account) within minutes; `aws:TokenIssueTime` kill switch (⚠️ R2.9 #3) | 1, 7 |

Open checks from `work/03-options.md` §8 remain open.

## Author's design decisions (OD-n, 2026-11-09)

"Owner" here is the author of this submission. These decisions shaped the design; none is a
Papaya sign-off. Papaya's own decisions are listed in §1.

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
| OD14 | Add the risk-stop classifier (`tools/risk-stop/`) to the canonical L3 path list? (found while writing `examples/`) | Yes: it is a control, so only the L3 owner team may change it. |
| OD15 | Scope of the risk stop: risky diffs nobody looked at, or also malicious approved code? | Keep the current scope and state its limits; a separate prod preview role and a job split go to the phase-2 roadmap. |
| OD16 | Squash-only merges to `main` (needed so a PR cannot carry its own risk-stop approval)? | Yes; the cost is that PR-internal commit history is not kept on `main`. |
| OD17 | Deploy only the current tip of `main`, so re-running an old run cannot roll prod back? | Yes; added to the layer-3 "merge approval = deploy approval" conditions. |
| OD18 | An approval merged before a deploy stops, matched by a later change outside the stack's directory, is still accepted | Accepted as a stated limit; the approval-gate app (G19) is to close it by checking the stopped run's hash. |
| OD19 | Protect the names of SCP-exempt roles (`app-claims-*`, `cfn-deployment-*`, `github-prod-deploy-*`) so that only the IAM stack's deploy role can create or change them? (found while writing `examples/`) | Yes. Confirmed reading: "only the IAM stack" holds once OD20 gives the IAM stack its own role and OIDC subject; until then the protection is "only an approved prod Pulumi deploy". OD22 gives the IAM stack that role and subject in phase 1. |
| OD20 | Code in the deploy job (install scripts, Pulumi program, Serverless plugins) can request the job's OIDC token for either prod deploy role: fix now or roadmap? | Roadmap phase 2, together with OD15: a build job without `id-token`, and per-role environments (different OIDC subjects) or `job_workflow_ref`. Until then it is a stated limit. **Superseded in timing by OD22:** per-environment roles move to phase 1. |
| OD21 | Phase 1 lets built-in read-only commands (`cat`, `head` …) read `~/.aws` without a prompt, and allow rules skip the auto-mode classifier: add keys to the phase-1 subset? | Yes: add a `Read(~/.aws/**)` deny rule and `autoMode.classifyAllShell: true` (examples finding 19). |

**Fixes after the independent review** (`work/07-review.md`; proposals and the owner's choices in
`work/08-fix-proposals.md`, documentation checks in `work/09-fix-research.md`). The owner accepted
every proposal on 2026-11-09:

| # | Review finding | Decision |
|---|---|---|
| OD22 | Approved code runs with a prod deploy role, which can change SCP-exempt roles (review A-1) | Moves OD20 into phase 1: the IAM stack gets its own environment `production-iam` and role; domain deploy roles change only `svc-*` roles under a fixed permissions boundary; no install scripts in deploy and preview jobs except a reviewed allowlist (L3 path); agent review on every PR touching infrastructure code. The separate preview role (OD15) stays in phase 2. |
| OD23 | Identity Center administrators and `OrganizationAccountAccessRole` can grant prod write outside the design (review C-4) | Identity Center permission sets and assignments as code (L3 owner team only) with alerts on other changes; an SCP denies `OrganizationAccountAccessRole` in the prod OU; member-account root credentials removed; a named management-account group. |
| OD24 | The long-lived k0s deploy credential is undetectable if leaked, on the cluster that runs AI agents reading partner documents (review A-4) | Phase 1: a namespaced, time-limited ServiceAccount token without Secret, exec, log, token, RBAC or delete rights; `production-k0s` environment required; Kubernetes API audit log. Target: k0s trusts GitHub OIDC directly. |
| OD25 | An approval proves a GitHub account, not a named person; an agent can approve through its engineer's login (review C-1) | Required 2FA, a login register fed by HR with quarterly review, restricted personal access tokens; from phase 1, managed deny rules for `gh pr review`, `gh api …reviews…` and the `gh` token file (hygiene); Enterprise Cloud (SAML, environment reviewers, audit-log streaming) is listed with its price as a decision for Papaya. |
| OD26 | A component that runs on every laptop (plugin, hook, local MCP server) can give an attacker many logins at once, so author ≠ approver is no longer two independent people (review A-2, A-3) | Threat T23; marketplace pinned to a protected release tag, every plugin (internal too) pinned by `sha`, auto-update off; local MCP servers only as immutable artifacts (image digest or pinned plugin); approval-gate app flags suspicious approvals; **process paths need two L3 owner team members** (partly reverses OD2, ADR-0012). |
| OD27 | The `incident` label opens cross-domain approval, and anyone with Triage can apply it (review E-2) | The approval-gate app counts an on-call approval for another team's file only with an open incident and the approver on shift; the label alone grants nothing; every `incident` PR is in the monthly report. Consequence: on normal days a cross-team PR needs an owner of each team (changes the effect of OD10; ADR-0012). The app becomes a hard phase-1 prerequisite. |
| OD28 | PHI could reach the agent through a log group it may read, if one approved PR logs a whole event (review A-1b) | CloudWatch Logs masking with custom identifiers on those log groups, set before they open; no `logs:Unmask` for agent-usable roles; a SAST rule against logging whole events. Stated as a second layer: AWS has no managed identifiers for VN/TH/HK. |
| OD29 | No designed path for schema migrations and data fixes (review E-1) | `sql` job of the deploy workflow with its own database role (IAM auth), SQL risk stop, metadata changes always stop, data fixes per tenant with expected rows and a data owner's approval (L3-data-write); ADR-0011. A hard prerequisite of removing standing prod write. |
| OD30 | Evidence before phase 2 can expire; JIT and data-read approvals have no store (review C-2, C-3) | From phase 1: evidence bucket with Object Lock (compliance, 6 years), nightly export of PRs, reviews, checks, deploy logs and artifacts; monthly manual export of the org audit log; Linear template for JIT and data-read requests, mirrored to the bucket by webhook. Closes O-1 and O-4. |
| OD31 | Strict up-to-date branches plus head-commit-only approvals make every merge stale every other PR (independent review round 3, #4) | The approval-gate check counts an approval on an earlier commit when the PR's diff against its merge base is unchanged (patch ID), as GitHub's own stale-approval rule does; the last pusher is the last person who changed that diff. Strict up-to-date stays. |
| OD32 | The IAM stack, which creates and re-trusts the SCP-exempt roles and the boundary, needed one approver co-owned by on-call (round 3, #5) | `infra/pulumi/iam/` and `deploy-approvals/iam/` become process paths: two L3 owner team members, no on-call co-owner; a night IAM fix uses JIT. |
| OD33 | Nothing checked "approver ≠ requester" before a JIT grant (round 3, #7) | A receiver in the tooling account grants `InfraOperator-*` only after checking the signed Linear webhook, a person's state change, approver ≠ requester, on shift, open incident and the allowed set (E16); manual grant by the L3 owner team as the degraded mode, alerted. |
| OD34 | Phase-2 costs for Engineering were stated only in the examples (independent review G1 #3, G2 #4, G3 #1) | Costs listed in §1, layer 2, the README and S4; mitigations: push and PR at the `!` prompt, cloud CLIs against real accounts in CI, Docker tests in CI, a read-only registry token in the sandbox, a deadline for masked logs per service and Logs Insights through masking as the agent-safe debugging path; per-group settings via the Claude apps gateway as a phase-3 option. |
| OD35 | Phase 1 had no effort estimate (review G-7; rounds G1 #7, G2 #5, G3 #9) | Rough estimate per item (≈ 75–110 person-days), critical path through the approval-gate app, a minimum safe phase 1 (≈ 57–83 pd: 2 DevSecOps + 1 platform engineer for ~45 days, or 1–2 people for ~60 days), and a detective degraded mode if the app is late, accepted only by Compliance in writing. |
| OD36 | GCP, Firebase and human k0s access were "same principles"; several prod write paths were never named (review G-4; rounds G1 #8, G2 #8, G3 #6) | GCP: WIF limited to the monorepo and the `production` subject, PAM entitlements instead of standing roles, Data Access logs for Vertex AI and partner documents, written BAA confirmation; Firebase: WIF spike, rollback by revert PR, previews from non-prod only; k0s: OIDC for people, one sealed break-glass certificate; a table of every prod write path and its gate in layer 3. |
| OD37 | Thailand and Hong Kong were not mentioned (round G1 #9) | Register rows for transfers per tenant country and breach notification (C-18, C-26), a tenant compliance profile, and open items for the insurance regulators (O-10, O-11); the controls stay the same, the paperwork and the clock change. |
| OD38 | Fragmented monitoring had one principle and a placeholder (review G-4; rounds G1 #10, G2 #9, G3 #10) | Target routing: CloudWatch → SNS → one paging tool and Slack via Amazon Q Developer; GCP → the paging tool plus email or Pub/Sub; no AWS Incident Manager; three severities, escalation times, incident declaration as a Linear issue that the gate and JIT read; agents start from the alert. |
| OD39 | S10 checks had names only; no image scanning or signing; no limit on agent PR size (round G1 #12) | Concrete checks per tool with the two GitHub licences as a priced decision for Papaya, Trivy for Dockerfiles, manifests and generated templates, ECR enhanced scanning and managed signing, a PR-size check for app-opened PRs; k0s admission open. |
| OD40 | Mobile releases through Expo EAS (OTA updates) bypassed the merge gate (round G2 #8) | Protected `production` channel and credentials, CI robot with Release Manager only in the `production-mobile` environment, signed updates, no EAS Workflows for prod, nightly reconciliation of channel updates against deploy runs. |
| OD41 | Open points of OD31–OD33 (owner, 2026-11-09) | OD31: the semantic-clash residual is accepted and recorded; GitHub's behaviour is tested when built. OD32: stated as rare (the IAM stack holds only exempt roles and the boundary); a JIT metric for IAM-stack grants decides whether an incident rule is needed. OD33: real payload checked when built; scope from a label and the incident from an issue relation; one grant per request; Linear through SSO in the people register; compared with the AWS TEAM sample. |
| OD42 | Independent review round after G5 (2026-11-09) | `production-db` environment for the database job; DML in a migration stops; data owners read by the gate from the path, not code owners; `production-mobile` for the Expo secrets; threats for the tooling account and its keys (T26) and a scoped role for the JIT receiver; 1.7 a hard prerequisite. |
| OD43 | The first 45–60 days keep writable SSO sessions with auto mode and no prompts for cloud CLIs (round after G5, #6) | The `ask` rules for `aws`, `pulumi` and `serverless` move into the phase-1 subset (may not slip); auto mode stays allowed (D1). |
| OD44 | No cost comparison of the custom tooling with GitHub Enterprise Cloud (#7) | A table of what Enterprise replaces (identity register, manual audit-log export, prod diff before apply) and what stays custom (gate rules, JIT receiver, risk stop, database path, evidence bucket); recommendation: upgrade in phase 2 up to about 100 users. |
| OD45 | Changes to the production AI agents had no risk class (#11) | Their prompts and model settings: owned by the AI team, with a required evaluation check; their tool permissions and identity: a process path (two L3 approvers). Runtime security of those agents stays out of scope. |
| OD46 | The panel could not read the deliverable quickly; "owner" read as Papaya's sign-off; agents appeared mostly as a risk (review G-1–G-3; every grading round) | An executive brief without codes; §1 rewritten as one page with the decisions Papaya must take and their recommendations; "owner" stated as the author everywhere it matters; §2 with eight agent-assisted DevSecOps workflows, three new skills, a shared `CLAUDE.md` template and a PR template (E17). |
| OD47 | Final review round: the internal skills did not load under `--restricted`; the incident session kept MCP servers; path-filtered required checks could hang (2026-11-09) | Internal plugin force-enabled through managed `enabledPlugins`; `--strict-mcp-config` in the incident session; every required check runs on every PR; a CI review workflow example (E18) and value baselines for §2. |
| OD48 | Data-fix files could carry tenant personal data into git (final review #4) | Data fixes name records by opaque IDs; sensitive values come at run time from a values file only the in-VPC task reads; the required check `data-fix-scan` fails on masking identifiers or long digit runs (E19). |
| OD49 | Custom tooling on the critical path; phase headings still "0–30" (final review #3) | Phases re-baselined to days 0–45, 45–75, 75–100; the approval-gate app runs two weeks report-only before it is required, with an availability target, an alert and a drilled removal runbook. |
| OD50 | Engineering loses agent push and PR in phase 2 through controls the design calls hygiene (final review #2) | The phase-2 sandbox goes to one pilot team first and to everyone only once S4 holds; a narrow push-and-PR credential for the agent is evaluated in the pilot. |
| OD51 | Blast radius of approved domain-stack code understated (final review #6); on-call not sized (#10) | #6: the real blast radius is stated, with per-domain environments as the next step. #10: not changed; the rota is sized by Papaya's engineering management (author's choice). |
