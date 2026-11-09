# Architecture decision records

Each record states one major decision behind [`../01-framework.md`](../01-framework.md), the options weighed
and what it costs. The reasoning and its sources live in the framework, audit evidence in
[`../04-compliance-mapping.md`](../04-compliance-mapping.md); an ADR only records the choice. Markers follow the framework legend: 📖 R*x.y* = documented research row in
`work/02-research.md`, ⚠️ = inference or unverified, [design] = proposal of this submission. OD*n* = owner
decisions in the [framework appendix](../07-framework-appendix.md#r-authors-design-decisions-od-n-2026-11-09); D1–D3 = owner decisions in research 6.6. Other codes (GĐ-n
assumptions, S-n success criteria, P-n problems, G-n gaps, Options §n, framing §n) are explained in the
framework's "How to read this" section.

| ADR | Decision | Framework layer |
|---|---|---|
| [0001](0001-prod-changes-only-through-ci.md) | Every production change goes through a reviewed PR applied by CI ("IaC first") | 3, 5 |
| [0002](0002-no-standing-prod-write-read-only-agent-identity.md) | Nobody holds standing prod write; in prod the only standing role (the engineer's, so the agent's) reads metadata | 1, 2 |
| [0003](0003-merge-to-main-is-the-approval-gate.md) | The merge to `main` is the approval gate: two people, code owners, on-call co-ownership (superseded in part by 0012) | 3 |
| [0004](0004-risk-stop-on-risky-prod-diffs.md) | Risky prod diffs stop the deploy until a stack owner approves the prod preview | 3 |
| [0005](0005-break-glass-is-time-limited-jit.md) | Break-glass is a time-limited, approved JIT grant, for incidents only | 7 |
| [0006](0006-mcp-and-plugins-only-from-allowlist.md) | MCP servers and plugins are allowed only from a reviewed, pinned catalogue | 4 |
| [0007](0007-agent-settings-are-hygiene-not-the-boundary.md) | Claude Code managed settings are hygiene, not the security boundary | 2 |
| [0008](0008-oidc-no-long-lived-ci-keys.md) | CI uses OIDC; no long-lived CI keys, with time-boxed exceptions (k0s/Firebase, then Expo, OD40) | 1, 5 |
| [0009](0009-agent-stays-outside-phi.md) | The coding agent stays outside PHI; real-data reads are approved per tenant | 1, 6 |
| [0010](0010-risk-level-decides-who-approves.md) | Risk level decides who approves, not how many; non-prod needs no approval (superseded in part by 0012) | 3 |
| [0011](0011-database-changes-through-the-pipeline.md) | Database schema changes and data fixes go through the pipeline like any prod change | 3, 6 |
| [0012](0012-approval-integrity-checked-by-the-gate-app.md) | The approval-gate app checks approval integrity: two approvals on process paths, on-call approvals only for open incidents | 3, 4 |

Not recorded as ADRs, because they follow from the decisions above: the audit chain (change records,
monthly reconciliation, drift detection; framework layer 7), the rollout plan
([`../03-rollout-plan.md`](../03-rollout-plan.md)) and the CI-agent setup
(layer 5; covered in parts by ADR-0006 and ADR-0007).

Rule: an accepted ADR is not edited. A changed decision gets a new ADR that supersedes the old one.

## Refinements since acceptance

Writing and testing the files in [`../../examples/`](../../examples/README.md) made some details more
precise. None changes a decision, so no ADR is superseded; the framework carries the current wording.

- **ADR-0003:** "merge approval = deploy approval" gains two conditions: squash-only merges (OD16)
  and deploying only the current tip of `main`, because a writer can re-run an old deploy run for
  30 days and roll prod back without approval (OD17; examples finding 4).
- **ADR-0004:** "the approver sees the prod diff" means the approver sees **which** prod resources and
  properties change, not the new values, which stay out of the job summary so that secrets stay out of
  logs; values are reviewed in the code of the stopped PR. The approval is also bound to git history
  (examples E7, finding 2), and an early approval can match a later change outside the stack, an
  accepted gap until G19 (OD18).
- **ADR-0007:** the "read-only allowlist" became two exact repo scripts, because Claude Code already runs
  read-only commands without a prompt and wildcard rules can write files (examples finding 19); phase 1
  adds a `Read(~/.aws/**)` deny rule and `autoMode.classifyAllShell` (OD21). `sandbox.excludedCommands`
  entries need a trailing ` *` and are paired with `ask` rules, so each excluded CLI call prompts, auto
  mode included (examples finding 22).

After the independent review (`work/07-review.md`; owner decisions from OD22, 2026-11-09). Two
changes are decisions and got their own ADR: ADR-0011 (database changes) and ADR-0012, which
supersedes parts of ADR-0003 and ADR-0010. The others narrow how a decision is carried out:

- **ADR-0002:** "nobody holds standing prod write" now also covers who administers Identity Center:
  permission sets and assignments are code owned by the L3 owner team only, other changes raise an
  alert, `OrganizationAccountAccessRole` is denied in the prod OU and member-account root
  credentials are removed (OD23). The management account stays outside SCPs: detected, not prevented.
- **ADR-0003 / ADR-0004:** what runs in the deploy job is limited from phase 1: one GitHub
  environment per kind of stack (`production-iam` for the IAM stack), bounded domain deploy roles,
  no install scripts except a reviewed allowlist, and an agent review on infrastructure PRs (OD22).
  This was OD20's phase-2 roadmap item. The risk stop's scope is unchanged (OD15).
- **ADR-0008:** the k0s exception gets conditions: a separate `production-k0s` environment (was
  optional), a namespaced, time-limited ServiceAccount token instead of a kubeconfig, and the
  Kubernetes API audit log; target is k0s trusting GitHub OIDC directly (OD24).
- **ADR-0006:** its example entry `serverCommand` = `["npx", "<package>@<exact-version>"]` is no longer allowed: it pins the package, not its dependencies. "Pinned catalogue" now covers what reaches every laptop: the marketplace is pinned
  to a protected release tag, every plugin (internal ones too) to a commit, auto-update is off, and
  local MCP servers are admitted only as immutable artifacts (OD26).
- **ADR-0003 / ADR-0007:** managed deny rules for `gh pr review` and the `gh` token file from phase 1,
  as hygiene behind OD5; a login register maps GitHub accounts to people (OD25). The parts of
  ADR-0003 that ADR-0012 supersedes are listed in ADR-0012.
- **ADR-0004:** the SQL risk stop of ADR-0011 adds stops for DML in migrations and for every
  GraphQL-engine metadata change; the IAM stack's risk-stop approvals need two L3 owner team
  members (OD32, OD42).
- **ADR-0007:** the `ask` rules for `aws`, `pulumi` and `serverless` ship in phase 1, while
  engineers' sessions can still write to prod (OD43); still hygiene, not the boundary.
- **ADR-0008:** one environment per kind of credential holder: `production-db` for the database
  job, `production-mobile` for the Expo token and update-signing key, the second exception (OD40,
  OD42).
- **ADR-0005:** a receiver grants the JIT role only after checking approver ≠ requester, on shift
  and an open incident, once per request, with a role scoped to tagged permission sets (OD33,
  OD41, OD42).
- **ADR-0009:** log groups the agent may read get a second layer outside application code: a
  CloudWatch Logs masking policy with custom identifiers, no `logs:Unmask` for agent-usable roles,
  and a SAST rule against logging whole events (OD28).
- **ADR-0005:** JIT requests and approvals are Linear issues from a template, mirrored to the
  evidence bucket with Object Lock; no longer "a channel" left open (OD30).
