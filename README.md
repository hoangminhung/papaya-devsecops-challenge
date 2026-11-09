# Papaya DevSecOps Challenge 1 — Coding Agents for DevSecOps

Submission for [DevSecOps Challenge 1](https://github.com/papaya-insurtech/pumpkin/blob/main/Hiring/DevSecOps_Challenges/DevSecOps_Challenge_1.md)
(local copy: [work/00-challenge.md](work/00-challenge.md)).

> Status: complete for review; the compliance register awaits the owner's review · Updated: 2026-11-09

## The problem and the answer

Engineering wants Claude Code to talk to AWS directly; Compliance wants nothing to change in
production without a named human who reviewed and approved it. The two only disagree about **writes
to production**: reads of metadata and all of non-prod are outside Compliance's sentence.

The answer ("A + D2'", owner decision): **every prod change is a pull request**, approved by a code
owner who is not the author and applied by CI, incidents included. A time-boxed, approved JIT grant,
used by a human without an agent, is the only fallback during an incident when the PR path cannot be
used. Nobody, human or agent, holds standing prod write or long-lived credentials (one exception:
k0s/Firebase CI deploy credentials, kept as `production` environment secrets, OD1).

| Engineering gets | Compliance gets |
|---|---|
| A free non-prod loop with the agent; read-only prod metadata | Approval **before** apply by a named human ≠ author, enforced by GitHub and AWS IAM, outside the agent |
| One approval, same-day ship; incident approval ≤ 15 min, 24/7 | One evidence chain per change; target ≤ 30 min to retrieve it, realistic from phase 2 |
| **Costs:** slower incident lane (est. 11–46 min); no raw logs of unredacted services at first; more prompts; 24/7 approver duty; ≤ 5 days for a new tool | **It does not give:** a technical stop on an agent approving through its engineer's login; prevention of admins editing the gate (logged only) |

**Where it falls short** (stated in [framework §1](docs/01-framework.md#1-the-decision-in-one-page)):
the JIT fallback meets the approval rule only partly; on GitHub Team nobody sees the prod diff before
apply, so a risk stop holds risky diffs for a second approval; high-risk (L3) changes get one
approver, from the owners of the path; admins can edit the gate (logged, not prevented); on normal
days domain review by the on-call group is a process rule; "an agent never approves a PR" is
policy and training, not a technical control; k0s and Firebase are weaker; if the required-check GitHub App is down, every merge is blocked, incident PRs included; whether HIPAA applies is a
legal question.

## How to read it

| You are | Read | Time |
|---|---|---|
| Decision panel | This page, [framework §1](docs/01-framework.md#1-the-decision-in-one-page), [rollout plan](docs/03-rollout-plan.md), [diagrams](diagrams/README.md) | ~15 min |
| Compliance | [Compliance register](docs/04-compliance-mapping.md), [threat model](docs/05-threat-model.md), [problem → control map](docs/06-problem-control-map.md) | ~45 min |
| Engineer | [Engineer guide](docs/02-engineer-guide.md), [examples](examples/README.md), framework layers 1–3 | ~45 min |

| Path | Contents |
|---|---|
| [docs/](docs/) | Framework (8 layers: principle, Papaya's stack, audit evidence, cost/value), guide, rollout, register, threat model, map, [ADRs](docs/adr/README.md) |
| [examples/](examples/README.md) | Ruleset, CODEOWNERS, workflows, a runnable risk stop, IAM/OIDC/SCP, managed settings, plugin marketplace, policy pack; each with a local check and what it does **not** prove |
| [diagrams/](diagrams/README.md) | Change workflow, trust boundaries, incident lane |
| [work/](work/) | Working notes and decision log (Vietnamese, with English summaries) |
| [transcripts/](transcripts/) | Complete, raw, unedited Claude Code session files |
| [CLAUDE.md](CLAUDE.md) | The rules the agent followed in this repository |

## Evidence markers

Every claim about a tool carries one: ✅ verified here · 📖 official documentation, with a link or a research row `R x.y` in
[work/02-research.md](work/02-research.md) · ⚠️ inference or not verified · [design] my proposal, untested.
Nothing was run against Papaya's systems; I had no access to them.

## How this was built

The repository was written with Claude Code under the same approach it recommends:

- [CLAUDE.md](CLAUDE.md) set the rules: source markers, no secrets, design only.
- From the research step on, each step went to an **independent reviewer subagent** (given the file
  and the criteria, not my conclusions) until no HIGH/MEDIUM finding remained or the owner stopped the
  rounds; [the log](work/session-log.md) notes fixes that were not re-reviewed. The framing was reviewed with the owner.
- **Deviation:** `CLAUDE.md` planned Manual permission mode from session 2, but the VS Code extension
  started most working sessions in **auto mode** (transcripts record `permissionMode: "auto"`;
  `"default"` only in three short sessions, ✅ grep). Auto mode is allowed by choice (D1), but these
  transcripts do not show Manual-mode prompts. Sessions 1–2 (2026-11-08) used the default config profile; later sessions the clean one.
- Material choices went to the owner (OD1–OD21 in the framework).

**Deviation from the agreed form** (framing Q14): there is no Claude Code hook example. The framework
defines no specific hook, and hooks fail open unless set to block (framework layer 2); `allowManagedHooksOnly` is in the managed
settings example instead (owner decision, [work/05-deliverable-plan.md](work/05-deliverable-plan.md) §5 Q6).

## Transcripts

All Claude Code sessions for this challenge were run in this repository. The sessions of
2026-11-08 up to session 2 used the default profile (`~/.claude`); later sessions use a clean profile (`~/.claude-papaya`, see
[work/setup-clean-config.sh](work/setup-clean-config.sh)). Each session is one
`<session-id>.jsonl` file plus an optional `<session-id>/` directory holding subagent
transcripts and large tool results (📖 [Claude directory reference](https://code.claude.com/docs/en/claude-directory#cleaned-up-automatically)).
They are copied, unedited, into [transcripts/](transcripts/) before each commit that ends a session:

```bash
for CFG in ~/.claude ~/.claude-papaya; do
  SRC="$CFG/projects/-home-do-hoang-minh-hung-papaya-devsecops-challenge"
  [ -d "$SRC" ] && rsync -a --exclude='memory/' --include='*.jsonl' --include='*/' --include='*/**' "$SRC"/ transcripts/
done
```

Claude Code deletes local transcripts after `cleanupPeriodDays` (default 30 days, minimum 1,
cannot be disabled). Both profiles on the machine used for this challenge set it to 365 days.
