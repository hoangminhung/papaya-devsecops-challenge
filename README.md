# Papaya DevSecOps Challenge 1 — Coding Agents for DevSecOps

Submission for [DevSecOps Challenge 1](https://github.com/papaya-insurtech/pumpkin/blob/main/Hiring/DevSecOps_Challenges/DevSecOps_Challenge_1.md)
(local copy: [work/00-challenge.md](work/00-challenge.md)) · Status: complete · Updated: 2026-11-09

## The problem and the answer

- **Engineering: "Let Claude Code talk to AWS directly."** Yes: freely in non-prod, and in prod
  for reading metadata. A change to prod is a pull request, which the agent can help write.
- **Compliance: "Nothing changes in production without a named human who reviewed and approved
  it."** Yes: every prod change is approved before it is applied, by a named person who is not its
  author, enforced by GitHub and AWS IAM outside the agent. One partial exception: the break-glass
  fallback during an incident (below).

The two only disagree about **writes to production**: reads of metadata and all of non-prod are
outside Compliance's sentence.

The answer (the author's proposal): **every prod change is a pull request**, approved by a code
owner who is not the author and applied by CI, incidents included. A time-boxed, approved JIT grant,
used by a human without an agent, is the only fallback during an incident when the PR path cannot be
used. Nobody, human or agent, holds standing prod write or long-lived credentials. The exceptions
are named, each with an owner and an expiry: CI deploy credentials for k0s and Firebase, the Expo
robot token and update-signing key, and the private keys of two GitHub Apps the design adds
([framework §1](docs/01-framework.md#1-the-decision-in-one-page)).

| Engineering gets | Compliance gets |
|---|---|
| A free non-prod loop with the agent; read-only prod metadata | Approval **before** apply by a named human ≠ author, enforced by GitHub and AWS IAM, outside the agent |
| One approval (two on process paths and data fixes), same-day ship; incident approval ≤ 15 min, 24/7 | One evidence chain per change, kept 6 years under Object Lock from phase 1; target ≤ 30 min to retrieve it, realistic from phase 2 |

**What it costs Engineering** (also in the [executive brief](docs/00-executive-brief.md#what-it-costs)):

- a slower incident lane than a console fix: an estimated 11–46 min from decision to change;
- from phase 1, a confirmation for every `aws`, `pulumi` and `serverless` call, in auto mode too;
- from phase 2, the agent cannot push, open pull requests, run Docker or reach a private registry
  without a workaround;
- raw logs of a service only after its masking lands (deadline: end of phase 2 for claims services);
- a 24/7 approver rota, and up to 5 days to get a new tool approved.

**What it does not give Compliance:**

- a technical stop on an agent approving through its engineer's login (deny rules are hygiene;
  such approvals are only flagged);
- on GitHub Team, a GitHub login tied to the identity provider (a register maps logins to people);
- prevention of admins editing the gate (it is logged).

**Where else it falls short** (all limits, with sources, in
[framework §1a](docs/01-framework.md#1a-limits-and-trade-offs-in-detail)):

- the break-glass fallback meets "approved before applied" only partly: it approves a command
  list, not the applied change;
- on GitHub Team nobody sees the prod diff before apply, so a risk stop holds risky diffs for a
  second approval;
- if the approval-gate GitHub App is down, every merge is blocked, incident PRs included;
- k0s and Firebase have weaker controls than AWS; whether HIPAA applies is a legal question.

## How to read it

| You are | Read | Time |
|---|---|---|
| Short on time | This page and the [change workflow diagram](diagrams/01-change-workflow.svg) | ~5 min |
| Decision panel | [Executive brief](docs/00-executive-brief.md) (plain language, no codes), [framework §1](docs/01-framework.md#1-the-decision-in-one-page) with the decisions Papaya must take, [diagrams](diagrams/README.md) | ~20 min |
| Compliance | [Compliance register](docs/04-compliance-mapping.md), [threat model](docs/05-threat-model.md), [problem → control map](docs/06-problem-control-map.md) | ~45 min |
| Engineer | [Engineer guide](docs/02-engineer-guide.md), [framework §2](docs/01-framework.md#2-agent-assisted-devsecops-workflows) (how the agents are used), [examples](examples/README.md), framework layers 1–3 | ~45 min |

| Path | Contents |
|---|---|
| [docs/](docs/) | Executive brief; framework (the decision, agent-assisted workflows, 8 layers: principle, Papaya's stack, audit evidence, cost/value); guide, rollout, register, threat model, map, [framework appendix](docs/07-framework-appendix.md) (detail, gaps, the author's decisions), [ADRs](docs/adr/README.md) |
| [examples/](examples/README.md) | Ruleset, CODEOWNERS, workflows, a runnable risk stop, IAM/OIDC/SCP, managed settings, plugin marketplace, policy pack; each with a local check and what it does **not** prove |
| [diagrams/](diagrams/README.md) | Change workflow, trust boundaries, incident lane |
| [work/](work/) | Working notes and decision log (Vietnamese, with English summaries), including the [independent review](work/07-review.md) and the [verify report](work/10-verify.md) |
| [transcripts/](transcripts/) | Complete Claude Code session files, raw except the redaction of two work email addresses (see below); [session index](transcripts/README.md) |
| [CLAUDE.md](CLAUDE.md) | The rules the agent followed in this repository |

## Evidence markers

Every claim about a tool carries one: ✅ verified here · 📖 official documentation, with a link or a research row `R x.y` in
[work/02-research.md](work/02-research.md) · ⚠️ inference or not verified · [design] my proposal, untested.
Nothing was run against Papaya's systems; I had no access to them.

## How this was built

**Tools.** The work was done in Claude Code, mostly through the VS Code extension, with Claude
Opus 5.5 for the main sessions and most subagents (✅ `model` fields in the transcripts). From
session 3 the clean profile loaded only my personal DevOps AI kit: rules for safety gates, source
markers and secrets, plus skills such as `grill-me` (used for the framing review) and
`infra-researcher` subagents (used to check documentation for the review fixes). I also used
claude.ai chat outside Claude Code; those conversations are not part of the transcripts. Each phase
opened with a written prompt that named the goal and the output file; the agent proposed, I
decided, and every choice that changed the deliverable was recorded as an owner decision (OD-n).
Research and design steps went to fresh reviewer subagents that got the file and the criteria but
not my conclusions; factual fixes were applied directly, and fixes that changed the design waited
for my decision. Nothing ran
against real infrastructure: the agent read documentation, wrote files and ran local checks.

The repository was written with Claude Code under the same approach it recommends:

- [CLAUDE.md](CLAUDE.md) set the rules: source markers, no secrets, design only.
- "Owner" in these documents is the author of this submission, who approved each document while
  writing it; it is not a Papaya sign-off.
- Machine checks (syntax, policy scanners, links, secret scan, marker coverage) and their output are
  in [work/10-verify.md](work/10-verify.md).
- From the research step on, each step went to an **independent reviewer subagent** (given the file
  and the criteria, not my conclusions) until no HIGH/MEDIUM finding remained or the owner stopped the
  rounds; [the log](work/session-log.md) notes fixes that were not re-reviewed. The framing was reviewed with the owner.
- **Deviation:** `CLAUDE.md` planned Manual permission mode from session 2, but the VS Code extension
  started most working sessions in **auto mode** (transcripts record `permissionMode: "auto"`;
  `"default"` only in three short sessions, ✅ grep). Auto mode is allowed by choice (D1), but these
  transcripts do not show Manual-mode prompts. Sessions 1–2 (2026-11-08) used the default config profile; later sessions the clean one.
- Material choices were taken by the author, called "owner" in the documents (OD1–OD21, listed in the [framework appendix](docs/07-framework-appendix.md#r-authors-design-decisions-od-n-2026-11-09); OD22 onwards are the fixes after an [independent review](work/07-review.md)). They are not Papaya sign-offs; the choices left to Papaya are in [framework §1](docs/01-framework.md#1-the-decision-in-one-page).

**Deviation from the agreed form** (framing Q14): there is no Claude Code hook example. The framework
defines no specific hook, and hooks fail open unless set to block (framework layer 2); `allowManagedHooksOnly` is in the managed
settings example instead (owner decision, [work/05-deliverable-plan.md](work/05-deliverable-plan.md) §5 Q6).

## Transcripts

All Claude Code sessions for this challenge were run in this repository. The sessions of
2026-11-08 up to session 2 used the default profile (`~/.claude`); later sessions use a clean profile (`~/.claude-papaya`, see
[work/setup-clean-config.sh](work/setup-clean-config.sh)). Each session is one
`<session-id>.jsonl` file plus an optional `<session-id>/` directory holding subagent
transcripts and large tool results (📖 [Claude directory reference](https://code.claude.com/docs/en/claude-directory#cleaned-up-automatically)).
[transcripts/README.md](transcripts/README.md) lists every session with its date and phase.
They are copied into [transcripts/](transcripts/) before each commit that ends a session. One
mechanical redaction is applied: the author's two work email addresses are replaced with
`<redacted-work-email>` by [work/redact-emails.py](work/redact-emails.py) (matched by SHA-256;
nothing else changes). Git history was rewritten on 2026-11-09 to apply it to every commit.

```bash
for CFG in ~/.claude ~/.claude-papaya; do
  SRC="$CFG/projects/$(pwd | tr '/.' '--')"   # run from the repository root
  [ -d "$SRC" ] && rsync -a --exclude='memory/' --include='*.jsonl' --include='*/' --include='*/**' "$SRC"/ transcripts/
done
python3 work/redact-emails.py transcripts
python3 work/redact-emails.py --check transcripts   # must print "total: 0"
```

Claude Code deletes local transcripts after `cleanupPeriodDays` (⚠️ from the settings reference as read
in an earlier session, not re-checked: default 30 days, minimum 1, cannot be disabled). Both profiles on the machine used for this challenge set it to 365 days.
