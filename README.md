# Papaya DevSecOps Challenge 1 — Coding Agents for DevSecOps

Submission for [DevSecOps Challenge 1](https://github.com/papaya-insurtech/pumpkin/blob/main/Hiring/DevSecOps_Challenges/DevSecOps_Challenge_1.md)
(local copy: [work/00-challenge.md](work/00-challenge.md)).

> Status: repository skeleton only. Deliverable content is not written yet.

## How to read this repo

| Path | What is in it |
|---|---|
| [docs/](docs/) | The deliverable: framework and workflow for using coding agents in DevSecOps at Papaya |
| [examples/](examples/) | Concrete configuration examples (Claude Code settings and hooks, GitHub Actions, IAM/OIDC, plugin manifests) |
| [diagrams/](diagrams/) | Architecture and workflow diagrams |
| [work/](work/) | Working notes and decision log (may be in Vietnamese) |
| [transcripts/](transcripts/) | Complete, raw, unedited Claude Code session files for this challenge |
| [CLAUDE.md](CLAUDE.md) | Working rules the coding agent followed in this repo |

## Evidence markers used in the documents

- ✅ verified in this environment (command output or file read in the session)
- 📖 from official documentation (with link)
- ⚠️ assumption, not verified

## Transcripts

All Claude Code sessions for this challenge were run in this repository, so their native
session files live under `~/.claude/projects/<encoded-repo-path>/`. Each session is one
`<session-id>.jsonl` file plus an optional `<session-id>/` directory holding subagent
transcripts and large tool results (📖 [Claude directory reference](https://code.claude.com/docs/en/claude-directory#cleaned-up-automatically)).
Both are copied, unedited, into [transcripts/](transcripts/) before each commit that ends a session:

```bash
SRC=~/.claude/projects/-home-do-hoang-minh-hung-papaya-devsecops-challenge
rsync -a --exclude='memory/' --include='*.jsonl' --include='*/' --include='*/**' "$SRC"/ transcripts/
```

Claude Code deletes local transcripts after `cleanupPeriodDays` (default 30 days, minimum 1,
cannot be disabled). On the machine used for this challenge it is set to 365 days.
