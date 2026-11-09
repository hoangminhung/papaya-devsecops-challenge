# Architecture decision records

Each record states one major decision behind [`../01-framework.md`](../01-framework.md), the options weighed
and what it costs. The reasoning and its sources live in the framework, audit evidence in
[`../04-compliance-mapping.md`](../04-compliance-mapping.md); an ADR only records the choice. Markers follow the framework legend: 📖 R*x.y* = documented research row in
`work/02-research.md`, ⚠️ = inference or unverified, [design] = proposal of this submission. OD*n* = owner
decisions in the framework's last table; D1–D3 = owner decisions in research 6.6. Other codes (GĐ-n
assumptions, S-n success criteria, P-n problems, G-n gaps, Options §n, framing §n) are explained in the
framework's "How to read this" section.

| ADR | Decision | Framework layer |
|---|---|---|
| [0001](0001-prod-changes-only-through-ci.md) | Every production change goes through a reviewed PR applied by CI ("IaC first") | 3, 5 |
| [0002](0002-no-standing-prod-write-read-only-agent-identity.md) | Nobody holds standing prod write; in prod the only standing role (the engineer's, so the agent's) reads metadata | 1, 2 |
| [0003](0003-merge-to-main-is-the-approval-gate.md) | The merge to `main` is the approval gate: two people, code owners, on-call co-ownership | 3 |
| [0004](0004-risk-stop-on-risky-prod-diffs.md) | Risky prod diffs stop the deploy until a stack owner approves the prod preview | 3 |
| [0005](0005-break-glass-is-time-limited-jit.md) | Break-glass is a time-limited, approved JIT grant, for incidents only | 7 |
| [0006](0006-mcp-and-plugins-only-from-allowlist.md) | MCP servers and plugins are allowed only from a reviewed, pinned catalogue | 4 |
| [0007](0007-agent-settings-are-hygiene-not-the-boundary.md) | Claude Code managed settings are hygiene, not the security boundary | 2 |
| [0008](0008-oidc-no-long-lived-ci-keys.md) | CI uses OIDC; no long-lived CI keys, with one time-boxed exception | 1, 5 |
| [0009](0009-agent-stays-outside-phi.md) | The coding agent stays outside PHI; real-data reads are approved per tenant | 1, 6 |
| [0010](0010-risk-level-decides-who-approves.md) | Risk level decides who approves, not how many; non-prod needs no approval | 3 |

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
