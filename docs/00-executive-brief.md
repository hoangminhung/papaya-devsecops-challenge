# Executive brief: coding agents for DevSecOps at Papaya

> For the decision panel (Engineering and Compliance). About ten minutes. Plain language; the
> detail, sources and evidence markers are in the [framework](01-framework.md) and the files it
> links. This is the author's proposal: where the documents say "owner", they mean the author of
> this submission, not Papaya. Updated: 2026-11-09

## The question

Engineering: "Let Claude Code talk to AWS directly." Compliance: "Nothing changes in production
without a named human who reviewed and approved it." Both are right about what they care about,
and they only collide on one thing: **changing production**. Reading metadata, working in non-prod
and drafting code are not what Compliance's sentence is about. Real customer data has its own,
stricter rules.

## The answer

- **Every production change is a pull request.** A person who owns the changed files, and did not
  write the change, approves it; the pipeline applies it. The same path serves incidents, with an
  on-call approver available around the clock.
- **The agent is never the boundary.** The agent acts with its engineer's access, so the limits sit
  where an agent cannot move them: in AWS permissions and in GitHub's merge rules. Agent settings
  are a second layer.
- **Nobody keeps standing write access to production**, people or agents. The pipeline uses
  short-lived credentials instead of stored keys. The exceptions are named, each with an owner
  and an expiry: deploy credentials for k0s, Firebase and the mobile update channel, and the
  private keys of two small GitHub Apps the design adds.
- **Break-glass exists but is narrow:** when the pull-request path cannot be used during an
  incident, a person gets a one-hour grant, approved by the on-call approver before it starts, and
  types an approved list of commands without an agent. Afterwards the commands are compared with
  the audit log and turned into code.

## What a working day looks like

| Situation | What happens |
|---|---|
| A routine change (more memory for a Lambda) | The engineer and the agent change the code, preview it on non-prod, open a pull request; a teammate approves; the pipeline deploys. Same day. |
| A risky change (deleting a database, changing access) | Same, but the pipeline previews production first and stops. An owner of that system reads what will change and approves it before anything is applied. |
| An incident at 2 a.m. | The responder and the agent read metrics and masked logs, write the fix as a pull request marked as an incident, and page the on-call approver, who approves within 15 minutes. |
| A data fix for one insurer | A file in the repository, scoped to one tenant, with the expected number of rows; the code owner and that tenant's data owner both approve. |
| Someone needs to see real customer data | A request for one tenant, one store, one hour, approved by someone else and by the Papaya employee who is data owner for that insurer (at night, the data owner reviews it the next working day). Agents never receive raw medical documents. |

## How Papaya uses the agents for DevSecOps

Beyond writing code, the agents triage alerts, explain to an approver what a stopped deploy would
do, review every infrastructure pull request for security, fix vulnerable dependencies, draft the
code that follows a break-glass fix, prepare reviews of new tools, and pull together evidence for an
auditor. People still approve, run break-glass commands and decide on data access
([framework §2](01-framework.md#2-agent-assisted-devsecops-workflows)).

## What it costs

- **Engineering:** an approver for every production change; a confirmation for each cloud command
  the agent runs; from phase 2, pushing and opening pull requests by hand; raw logs of a service only
  once its logs are masked; a 24/7 rota; a slower incident lane than a direct console fix
  (estimated 11–46 minutes from decision to change, to be measured).
- **Papaya:** the first phase needs about two DevSecOps people and one platform engineer for about
  45 days, because several small tools must be built (the approval check, the break-glass grant,
  the database change path). A GitHub Enterprise upgrade removes part of this work.

## What it does not solve

- Break-glass approves a list of commands, not the applied change.
- An agent could still approve a pull request through its engineer's login; this is forbidden,
  discouraged by settings and flagged, but not technically impossible.
- GitHub administrators can change the merge rules; this is logged, not prevented.
- k0s, Firebase and the mobile update channel have weaker controls than AWS.
- Whether HIPAA applies, and Papaya's legal role for each insurer, are questions for counsel.

## Decisions Papaya must take

The list, with the author's recommendation for each, is in
[framework §1](01-framework.md#1-the-decision-in-one-page): accepting break-glass as partial
compliance, one or two approvers for high-risk changes, GitHub Team or Enterprise, scanning
licences, the stored-credential exceptions, phase-1 staffing and the yearly cost of running the custom tools, a lean first version of the approval check, an isolated runtime for the agent, the on-call rota, auto mode, and the
legal questions.

## Rollout

Three phases over about 100 days: days 0–45, 45–75 and 75–100 ([rollout plan](03-rollout-plan.md)). Phase 1 makes the pull
request the only way to change production and removes standing write access, but only once its
replacements work: pipeline deploys, the merge rules, the approval check, the on-call rota,
break-glass, the risk stop and the database path. Phase 2 adds the AWS guardrails, the full agent
settings, alert routing and automated evidence. Phase 3 tests and reviews.

## Codes used in the other documents

| Code | Meaning |
|---|---|
| L0–L3 | Risk levels: read; non-prod change; routine prod change; high-risk prod change ([layer 3](01-framework.md#layer-3--change-workflow-by-risk-level)) |
| OD-n | A design decision by the author of this submission ([framework appendix](07-framework-appendix.md#r-authors-design-decisions-od-n-2026-11-09)) |
| GĐ-n | An assumption made at the start (from Vietnamese "giả định"); the ones the documents use are listed below |
| S-n | A success criterion, e.g. S1 "no standing prod write" ([rollout plan](03-rollout-plan.md#metrics-by-phase)) |
| G-n | A gap: not designed, or only an open item |
| D1 | Permission mode: Manual by default, auto mode allowed and measured, with a switch to turn it off |
| D2 | Break-glass commands are typed by a person in a terminal without an agent |
| D3 | Session types: daily development, incident analysis with `--restricted`, CI agent; shared knowledge in `CLAUDE.md` and skills |
| E-n | A checked example file ([examples](../examples/README.md)) |
| C-n | A control in the [compliance register](04-compliance-mapping.md) |
| T-n | A threat in the [threat model](05-threat-model.md) |
| P-n, A-n | A problem from the brief or its appendix ([problem map](06-problem-control-map.md)) |
| R x.y, R9.x.y | A research row with its source, in `work/02-research.md` or `work/09-fix-research.md` |
| ✅ 📖 ⚠️ [design] | Verified here · from official documentation · not verified · the author's untested proposal |
| "Options §n", "framing Qn", "research 6.9.4" | Sections of the working notes in `work/` where a decision was argued; the decision itself is restated where it is used |

Assumptions used in the documents (✔ confirmed by the author at the start; the others are marked
"unconfirmed" where they matter):

| Assumption | Meaning |
|---|---|
| GĐ-1 ✔ | 20–60 engineers; no separate security team; DevSecOps is 1–2 people |
| GĐ-3 | Tenants are separated logically (schema, bucket, prefix) in shared accounts |
| GĐ-4 | k0s runs on AWS; engineers reach it with kubeconfigs, no single sign-on |
| GĐ-5 ✔ | Papaya is on GitHub Team, not Enterprise (an assumption, not a fact about Papaya) |
| GĐ-6 ✔ | Laptops are not trusted; the main controls sit in the cloud and CI |
| GĐ-8 ✔ | Every prod change is approved before it is applied, incidents included |
| GĐ-9 ✔ | By default the agent reads metadata, not real customer data; exceptions need an approved request |
| GĐ-10 | Pulumi previews can run in CI; some Serverless deploys run from laptops today |
| GĐ-11 ✔ | The reviewer is neither the author nor the agent that made the change |
| GĐ-12 | The rollout takes about 90 days, alongside ISO 27001 preparation |
| GĐ-14 ✔ | Non-prod holds only synthetic or masked data |

Success criteria S1–S11 with their targets are in the [rollout plan](03-rollout-plan.md#metrics-by-phase).
