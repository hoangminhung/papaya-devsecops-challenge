# CLAUDE.md — Papaya DevSecOps Challenge 1

## Purpose of this repo

This repository is my submission for Papaya's **DevSecOps Challenge 1 — "DevSecOps with
Coding Agents at Papaya"** (full text: `work/00-challenge.md`). The task is to design the
framework and workflow for how Papaya uses coding agents (Claude Code) for DevSecOps,
reconciling two positions:

- Engineering: "Let Claude Code talk to AWS directly."
- Compliance: "Nothing changes in production without a named human who reviewed and approved it."

Two things make this repo unusual and shape every rule below:

1. **The complete, raw Claude Code session transcripts are part of the submission** and are
   graded. Work transparently: state the reason behind each recommendation, show trade-offs,
   and say so when something is unverified.
2. **I have no access to Papaya's systems or code**, and the challenge does not expect it.
   Everything is a design on top of the stack described in the challenge's Appendix A.

## Hard constraints from the brief

- Design for Papaya's existing stack: AWS (Lambda via Serverless Framework, ECS, EC2, Aurora
  PostgreSQL, SNS/SQS, Step Functions, S3, CloudWatch), GCP (Vertex AI, Gemini), k0s
  Kubernetes, Firebase Hosting, a single GitHub monorepo, GitHub Actions, Pulumi, Claude Code
  (Team Premium) with an internal plugin marketplace, Linear, Slack.
- **Do not propose replacing IaC or CI tooling** (no "switch Pulumi to Terraform", no "move off
  GitHub Actions"). Improve how they are used.
- Compliance context: ISO 27001 (in progress), HIPAA, regional data-protection law; multiple
  insurer tenants in different countries. Sensitive data: medical records, national IDs, bank
  accounts.

## Repository layout

| Path | Contents | Language |
|---|---|---|
| `README.md` | Entry point for graders: what the deliverable is, how to read it | English |
| `docs/` | The deliverable: framework, workflows, policies, rollout plan | English |
| `examples/` | Concrete, copy-pasteable artifacts: Claude Code settings/hooks, GitHub Actions workflows, IAM/OIDC policy sketches, plugin manifests | English |
| `diagrams/` | Architecture and workflow diagrams (source + rendered) | English labels |
| `work/` | Working notes, the challenge text (`00-challenge.md`), scratch analysis, decision log | Vietnamese or English |
| `transcripts/` | Copies of the raw Claude Code session files (`*.jsonl`) for this project, unedited | n/a |
| `CLAUDE.md` | This file | English |

Numbered prefixes (`00-`, `01-`, …) in `docs/` and `work/` define reading order.

## Rule 1 — Every claim about a tool's capability needs a source marker

The deliverable depends on what Claude Code, GitHub Actions, AWS IAM, Pulumi, k0s etc. can
actually do. Model memory is often stale. Therefore every non-trivial statement about a
feature, flag, setting, default, or limit carries one of these markers:

| Marker | Meaning | Required evidence |
|---|---|---|
| ✅ | Verified in this environment | A command run in this session with its output, or a file read here |
| 📖 | Taken from official documentation | A link to the specific doc page, ideally with the version/date |
| ⚠️ | Assumption or recollection, not verified | Say what would be needed to verify it |

Rules of use:

- Never present ⚠️ content as fact. If an assumption is load-bearing for a recommendation,
  flag it in the document as an open item to verify.
- Prefer ✅ over 📖 over ⚠️. If something can be checked locally (e.g. a Claude Code setting
  on this machine), check it.
- Keep markers in the submitted docs too, not only in work notes. Graders should be able to
  see what was verified and what was not.
- When the official docs and memory disagree, docs win; note the discrepancy.
- Do not invent product features, settings keys, CLI flags, or IAM condition keys. If a
  needed capability cannot be confirmed, design around it or mark it as a dependency.

## Rule 2 — No secrets, no personal data

- No credentials, tokens, API keys, account IDs, ARNs with real account IDs, kubeconfigs,
  private keys, or `.env` contents anywhere in this repo or in the chat. Examples use obvious
  placeholders such as `<AWS_ACCOUNT_ID>` or `123456789012`.
- No personal data about real people: no names of Papaya staff, no email addresses other than
  what git already records as commit author, no customer or partner data. The challenge's
  example data categories (medical documents, national IDs) are referenced only as categories.
- Transcripts are committed unedited, as the challenge requires, so **do not paste secrets
  or personal data into the chat in the first place**. Do not print environment variables,
  settings files, or shell history without redacting values. If this rule is accidentally
  broken, stop and tell the user immediately before continuing.
- The git author identity is whatever the user has already configured; do not change it.

## Rule 3 — Language

- **Submitted material** (`README.md`, everything in `docs/`, `examples/`, `diagrams/`,
  commit messages, code comments) is in **English**.
- **Working notes** in `work/` may be in Vietnamese or English.
- In chat, reply in the language the user writes in (currently Vietnamese), keeping technical
  terms in English.
- This file overrides the global rule that writes handover docs in Vietnamese.

## Rule 4 — Working method

- Design, don't execute: this project needs no live infrastructure. Do not run cloud CLIs,
  `kubectl`, `pulumi`, or `serverless` against any real target. Local, read-only commands
  (reading docs, listing files, validating YAML/JSON, rendering diagrams) are fine.
- Keep the challenge's two voices (Engineering vs Compliance) in view; every control should
  say what it costs engineers and what it gives compliance.
- Record decisions and discarded options in `work/` so the reasoning survives the session.
- Ask the user when a choice materially changes the deliverable; otherwise pick the sensible
  default, state it, and continue.
- Before finishing a session, remind the user to copy the current transcript into
  `transcripts/` (see `README.md` for the command).
