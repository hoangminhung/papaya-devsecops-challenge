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
- **Workarounds (OD34):** ask the agent to write the PR text to a file, then run `git push` and
  `gh pr create --body-file <file>` at the `!` prompt; run Docker-based tests in CI on the PR;
  private packages install with the read-only registry token set up for you. For prod questions use
  metrics and masked logs through `ProdReadMetadata` (section 4) before asking for real data (section 5).
- **From phase 1** each `aws`, `pulumi` or `serverless` call asks you first, in auto mode too
  (OD43): until standing prod write is removed, your sign-in can still change prod.
- **From phase 2 you will also notice** (layer 2, examples E8): each WebFetch asks; your own and the project's permission
  rules are ignored, so prompts may rise; sign-in is locked to Papaya's organisation (API-key sessions
  are refused) and the minimum Claude Code version rises; on macOS, servers on localhost fail inside
  the sandbox; native Windows is not supported (use WSL2).
- **Layer:** [2](01-framework.md#layer-2--agent-runtime-controls).

## 2. Reading prod

- **What you do:** with `ProdReadMetadata` (1-hour session) you and your agent read metrics, metadata
  and logs that are redacted at source and masked by a data protection policy (OD28): identifiers
  such as national IDs, bank accounts and diagnoses show as masked values. Lambda configuration is readable per service once its secrets
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
   not be the last person who pushed. An agent never approves a PR (OD5). Managed settings deny `gh pr review` for agents, but
   that is hygiene only: another form of the same call gets past it, so the approval-gate check
   flags approvals that look automated rather than blocking them (OD25).
   - Domain code and stacks: your domain team. Members of the on-call group are co-owners, but
     their approval counts for another team's files only on an incident PR while they are on shift;
     the approval-gate check enforces it (OD27). A PR that touches several teams' files needs an
     owner of each.
   - Process files (`.github/`, `CLAUDE.md`, `.claude/`, the catalogue, the SCP and IAM stacks,
     `tools/risk-stop/`, `tools/ci/`, `oncall/`): **two** members of the L3 owner team (OD26,
     OD32). A night fix that needs an IAM change goes through JIT.
   - Clicking "Update branch" after someone else's merge keeps your approvals as long as your own
     changes are the same; a push that changes them needs a new approval (OD31).
4. Merge (squash only). The deploy job previews prod and applies the change.
5. **If the deploy stops at the risk stop** (stateful replace or delete, IAM, network, a policy
   finding): open a second PR that adds only `deploy-approvals/<stack>/<stopped commit>.yaml` with the
   hash from the job summary. By default the first approver approves it; if they are unavailable,
   another owner of the stack does, which is recorded as a deviation (OD13, OD11). Merging it deploys
   if the new prod preview has the same hash. While the stack is stopped, later merges to it stop too.

- **Time:** same working day from PR to prod; approval wait ≤ 1 hour in working hours (S4 targets).
- **What CI does differently (OD22):** npm install scripts do not run in preview and deploy jobs;
  if a package needs its script, ask the L3 owner team to add it to `tools/ci/allowed-install-scripts.txt`.
  A stack may create IAM roles for its own services only as `svc-*` roles with the standard
  permissions boundary; roles that read claim data (`app-claims-*`) are created in the IAM stack
  and referenced by ARN. PRs that touch infrastructure code also get an automated agent review,
  which is advice, not an approval.
- **Layer:** [3](01-framework.md#layer-3--change-workflow-by-risk-level); diagram
  [`01-change-workflow`](../diagrams/01-change-workflow.svg).

- **Other platforms (OD36, OD40):** mobile releases and over-the-air updates go through the same PR;
  the CI publishes to the `production` EAS channel, and nobody runs `eas update` against it from a
  laptop (your Expo role cannot). GCP prod access for a person is a Privileged Access Manager
  request approved by the on-call approver, never a standing role; k0s access for people is
  read-only through single sign-on once OIDC is in place.

## 3a. Database changes and data fixes

- **Schema and metadata:** write the migration (or GraphQL-engine metadata change) as a file under
  `db/<service>/`, open a PR, get your domain owner's approval as for code. After merge the `sql`
  deploy job applies it with its own database role; nobody, you included, holds database
  credentials (OD29, ADR-0011).
- **Data fix** (a stuck claim, a payout to retry): a file `db/<service>/data-fixes/<tenant>/<ticket>.sql`
  for one tenant, with a `-- expected_rows: N` header. It needs a code owner **and** a different
  person from that tenant's data owners (L3-data-write). The job rolls it back if the row count
  differs, and its summary shows counts only. Name records by their internal IDs only: no account
  numbers, national IDs, names or diagnoses in the file. If the fix needs such a value, the data
  owner uploads it as a values file and your SQL uses `:'variable'`; the `data-fix-scan` check fails
  the PR otherwise (OD48).
- **Expect a stop** for `DROP`, `TRUNCATE`, column type changes, `DELETE`/`UPDATE` without a
  `WHERE`, grants and row-level security, and every metadata change: open the
  `deploy-approvals/` PR as in step 5 above. Prefer expand/contract migrations.
- **In an incident:** the same path; the on-call approver may stand in for the data owner, who
  reviews it the next working day.
- **Layer:** [3](01-framework.md#layer-3--change-workflow-by-risk-level).

## 4. An incident at 2 a.m.

You are the **incident responder**. The **on-call approver** only approves; they never write the fix (OD7).

1. Start an incident-analysis session with read-only roles, in an empty scratch directory outside
   the repository: `claude --restricted --strict-mcp-config --tools "Bash,Read,Grep,Glob"` (no
   WebFetch, no MCP servers; Bash can still reach the network). Read metrics and masked logs; the
   `incident-triage` skill guides the session.
2. Open (or find) the incident issue in Linear. Make the fix in a normal session, preview on
   non-prod, and open a PR labelled `incident` that links the issue: the on-call approval counts
   only while the issue is open and the approver is on shift (OD27).
3. Call the on-call approver (phone in phase 1; routed alerts from phase 2). They review and approve.
   If they find a problem, you push the fix and they approve again.
4. Merge; the deploy job applies the change. If it stops at the risk stop, the approval PR it
   needs (`deploy-approvals/<stack>/`) goes the same way: label it `incident` and link the same
   open issue, or the approval-gate check does not count the on-call approval on it either.

- **Time:** target ≤ 15 min waiting for approval (S7); 11–46 min from decision to apply is an
  estimate (⚠️), measured first during rollout against a 30-minute target.
- **Blockers to know:** a risky change already waiting on `main` blocks your fix for that stack until
  it is approved or reverted; at night, process files (workflows, `CLAUDE.md`, catalogue) wait for the
  L3 owner team, or the JIT fallback applies.
- **Only if the PR path cannot be used** (GitHub Actions down, broken pipeline, an operation not in
  IaC): end your AWS portal session and sign in fresh, then open a JIT request issue in Linear from
  its template (outside GitHub), with the exact commands; it is the record of the request (OD30). The on-call approver approves before the grant by
  moving the issue to "Approved"; the grant then arrives automatically, and is refused if you
  approved it yourself, the approver is not on shift or the incident is closed (OD33).
  You get `InfraOperator-<service>` (1-hour role session; the real window can approach 2 h) and type
  the commands yourself, in a terminal **without an agent**. Afterwards your commands are compared
  with CloudTrail (by hand in phase 1, by a job from phase 2), and you open a PR that codifies the change.
- **Layers:** [3](01-framework.md#layer-3--change-workflow-by-risk-level),
  [7](01-framework.md#layer-7--observability-audit-incident-response-and-break-glass); diagram
  [`03-incident-lane`](../diagrams/03-incident-lane.svg).

## 5. Reading real customer data

- **What you do:** end your AWS portal session and sign in fresh, then open a data-read request issue
  in Linear from its template, with one tenant, purpose, store, time window and the agreement that
  covers it (OD30). You get a data-read role for 1 hour.
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
  tools it needs. A local MCP server is admitted only as a container image pinned by digest or as
  code inside a pinned plugin, not as `npx -y <package>` (OD26). Keep your GitHub CLI token in the
  system credential store (`gh auth status` shows where it is). A catalogue entry is added by a PR with a review record (examples
  [`reviews/`](../examples/claude/marketplace/reviews/)).
- **Approval:** two members of the L3 owner team (the catalogue is a process path, OD26).
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
- Approve another domain's PR only if it is labelled `incident`, links an open incident, and you
  are on shift (OD9, OD27); the approval-gate check does not count it otherwise.
- **Layers:** [3](01-framework.md#layer-3--change-workflow-by-risk-level),
  [7](01-framework.md#layer-7--observability-audit-incident-response-and-break-glass).

## 8. Shared agent knowledge

`CLAUDE.md` and other agent configuration files define how the whole team works, so changes to them
are approved by two members of the L3 owner team; a domain-team approval does not count (OD3, OD26). Review your agent's auto memory
and delete it after a suspicious session (D3). The shared `CLAUDE.md` starts from the template in
`examples/claude/repo-templates/CLAUDE.md`; pull requests use the template in
`examples/github/pull_request_template.md`, which asks which parts an agent wrote.

## 9. Using the agent for DevSecOps tasks

The internal plugin `devsecops-guardrails` carries the skills; invoke them by describing the task
([framework §2](01-framework.md#2-agent-assisted-devsecops-workflows)):

| Task | Skill | Where you run it | What you get |
|---|---|---|---|
| Ship an infrastructure change | `prod-change` | normal session | IaC change, non-prod preview, PR text |
| Triage an alert | `incident-triage` | incident-analysis session (section 4) | likely cause, smallest fix, JIT command list if needed |
| Understand a stopped deploy before approving | `risk-summary-explainer` | normal session, or the CI agent's comment | what each stopped operation does and whether it can be undone |
| Fix a vulnerable dependency | `dependency-fix` | normal session, or a CI-agent PR | one small PR per advisory |

The agent drafts; you approve nothing it wrote yourself, and nobody approves through an agent.

## Where the evidence comes from

You do not write separate evidence: the PR, its approvals, the deploy run and CloudTrail form the
record of every prod change. Compliance's view is in
[`04-compliance-mapping.md`](04-compliance-mapping.md).
