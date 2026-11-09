# Engineer guide: working with Claude Code at Papaya

> Status: a summary of the approved framework; it adds no rule · Updated: 2026-11-09 · Builds on
> [`01-framework.md`](01-framework.md)

This page answers one question: **what changes in my working day?** Each section says what you do,
who approves, and how long it takes. The rules and their sources are in the framework layer linked
from each section; if this page and the framework differ, the framework wins. Times are targets from
the success criteria (S-n) or estimates marked ⚠️.

## The short version

- **Non-prod is yours.** Build, deploy and debug in non-prod with the agent, with no new approval (S4),
  once a store has been scanned for real data (until then it follows the real-data rule, section 5).
- **Prod reads are metrics and metadata.** No standing prod write for anyone, you included.
- **Every prod change is a pull request.** One code owner who is not you approves; CI applies it.
- **In an incident the path is the same, with faster people:** an on-call approver, 24/7.
- **Real customer data, new tools and break-glass need a request.** Each has a named approver and a time limit.

## 1. Daily development (non-prod)

- **What you do:** use Claude Code as you do today, with non-prod roles. Manual permission mode is the
  default; you may switch to auto mode (D1). Commands that run inside the sandbox run without a prompt
  (phase 2, OD12).
- **Approval:** none (risk level L1).
- **What is different:** the organisation's managed settings apply to everyone; bypass mode is
  removed; plugins and MCP servers come from the catalogue only (section 6). From phase 2 the sandbox
  hides credentials and blocks Unix sockets, so `git push`, `gh`, Docker and private-registry `npm ci` fail inside it: run
  them yourself at the `!` prompt. Using `--restricted` is recommended (D3).
- **From phase 2 you will also notice** (layer 2, examples E8): each `aws`, `pulumi` or `serverless`
  call asks you first, in auto mode too; each WebFetch asks; your own and the project's permission
  rules are ignored, so prompts may rise; sign-in is locked to Papaya's organisation (API-key sessions
  are refused) and the minimum Claude Code version rises; on macOS, servers on localhost fail inside
  the sandbox; native Windows is not supported (use WSL2).
- **Layer:** [2](01-framework.md#layer-2--agent-runtime-controls).

## 2. Reading prod

- **What you do:** with `ProdReadMetadata` (1-hour session) you and your agent read metrics, metadata
  and logs that are redacted at source. Lambda configuration is readable per service once its secrets
  are resolved at runtime; until then, read timeout and memory from the IaC code.
- **Approval:** none (L0).
- **Cost to know:** in the first months, raw logs of services not yet redacted are not readable
  without a data-read request (section 5). This is the largest cost of the transition.
- **Remember:** the agent uses **your** AWS SSO session, so it can do whatever you can (layer 1). Keep
  the portal session short.
- **Layer:** [1](01-framework.md#layer-1--identity-and-access).

## 3. Shipping a prod change

1. Write the change as code (Pulumi, `serverless.yml`, Kubernetes manifests) and preview it on non-prod.
2. Push the branch and open a pull request. The PR runs secret scanning, dependency checks and SAST
   (S10), and previews non-prod only.
3. One code owner of the changed files approves. You cannot approve your own PR, and the approver may
   not be the last person who pushed. An agent never approves a PR (OD5).
   - Domain code and stacks: your domain team. Members of the on-call group are co-owners, but by
     rule they approve another domain's PR only if it is labelled `incident` and they are on shift;
     other cases appear in a monthly report (OD9).
   - Process files (`.github/`, `CLAUDE.md`, `.claude/`, the catalogue, the SCP stack,
     `tools/risk-stop/`): the L3 owner team only.
4. Merge (squash only). The deploy job previews prod and applies the change.
5. **If the deploy stops at the risk stop** (stateful replace or delete, IAM, network, a policy
   finding): open a second PR that adds only `deploy-approvals/<stack>/<stopped commit>.yaml` with the
   hash from the job summary. By default the first approver approves it; if they are unavailable,
   another owner of the stack does, which is recorded as a deviation (OD13, OD11). Merging it deploys
   if the new prod preview has the same hash. While the stack is stopped, later merges to it stop too.

- **Time:** same working day from PR to prod; approval wait ≤ 1 hour in working hours (S4 targets).
- **Layer:** [3](01-framework.md#layer-3--change-workflow-by-risk-level); diagram
  [`01-change-workflow`](../diagrams/01-change-workflow.svg).

## 4. An incident at 2 a.m.

You are the **incident responder**. The **on-call approver** only approves; they never write the fix (OD7).

1. Start an incident-analysis session with read-only roles, in an empty scratch directory outside
   the repository: `--restricted --tools "Bash,Read,Grep,Glob"` (no WebFetch; Bash can still reach
   the network). Read metrics and redacted logs.
2. Make the fix in a normal session, preview on non-prod, open a PR labelled `incident`.
3. Call the on-call approver (phone in phase 1; routed alerts from phase 2). They review and approve.
   If they find a problem, you push the fix and they approve again.
4. Merge; the deploy job applies the change.

- **Time:** target ≤ 15 min waiting for approval (S7); 11–46 min from decision to apply is an
  estimate (⚠️), measured first during rollout against a 30-minute target.
- **Blockers to know:** a risky change already waiting on `main` blocks your fix for that stack until
  it is approved or reverted; at night, process files (workflows, `CLAUDE.md`, catalogue) wait for the
  L3 owner team, or the JIT fallback applies.
- **Only if the PR path cannot be used** (GitHub Actions down, broken pipeline, an operation not in
  IaC): end your AWS portal session and sign in fresh, then request a JIT grant in the incident
  channel outside GitHub, with the exact commands. The on-call approver approves before the grant.
  You get `InfraOperator-<service>` (1-hour role session; the real window can approach 2 h) and type
  the commands yourself, in a terminal **without an agent**. Afterwards your commands are compared
  with CloudTrail (by hand in phase 1, by a job from phase 2), and you open a PR that codifies the change.
- **Layers:** [3](01-framework.md#layer-3--change-workflow-by-risk-level),
  [7](01-framework.md#layer-7--observability-audit-incident-response-and-break-glass); diagram
  [`03-incident-lane`](../diagrams/03-incident-lane.svg).

## 5. Reading real customer data

- **What you do:** end your AWS portal session and sign in fresh, then request it with one tenant,
  purpose, store, time window and the agreement that covers it. You get a data-read role for 1 hour.
  After reading one tenant's data, do not post to shared places without review.
- **Approval:** an approver who is not you, plus the data owner. At night the on-call approver
  approves alone, and the data owner reviews it the next working day.
- **PHI (medical records):** you read it yourself, in a terminal **without an agent**; give the agent
  only a redacted summary. A store that holds PHI counts as PHI unless the agent reads a view without
  it. Partner-uploaded claim documents never go into an agent session raw: reproduce with synthetic
  documents, or de-identify them first.
- **Non-prod** should hold no real data; a store not yet scanned follows this section's rule.
- **Layer:** [6](01-framework.md#layer-6--data-protection-and-prompt-injection-defence).

## 6. Adding a plugin or MCP server

- **What you do:** open a request with what the tool reads, where it sends data and which write
  tools it needs. A catalogue entry is added by a PR with a review record (examples
  [`reviews/`](../examples/claude/marketplace/reviews/)).
- **Approval:** the L3 owner team (the catalogue is an L3 path).
- **Time:** decided within 5 working days (S6).
- **Not allowed:** installing a plugin or MCP server outside the catalogue, or sideloading one with
  command-line flags.
- **Layer:** [4](01-framework.md#layer-4--supply-chain-for-mcp-servers-and-plugins).

## 7. When you are the on-call approver

- You are on a named 24/7 schedule: a primary and a backup. The primary approves; the backup steps in
  only if the primary is unavailable (OD2).
- While on call you **only approve**: you do not write fixes or request JIT grants (OD7). A night
  incident therefore needs two people awake: the responder and you.
- Target: approve within 15 minutes (S7). Approve JIT only when the PR path cannot be used, and record
  why you refuse it otherwise.
- Approve another domain's PR only if it carries the `incident` label (OD9).
- **Layers:** [3](01-framework.md#layer-3--change-workflow-by-risk-level),
  [7](01-framework.md#layer-7--observability-audit-incident-response-and-break-glass).

## 8. Shared agent knowledge

`CLAUDE.md` and other agent configuration files define how the whole team works, so changes to them
are approved by the L3 owner team only; a domain-team approval does not count (OD3). Review your agent's auto memory
and delete it after a suspicious session (D3).

## Where the evidence comes from

You do not write separate evidence: the PR, its approvals, the deploy run and CloudTrail form the
record of every prod change. Compliance's view is in
[`04-compliance-mapping.md`](04-compliance-mapping.md).
