---
name: incident-triage
description: Use when the user is investigating a production alert or incident. Reads metrics, masked logs and the repository; proposes a fix as a pull request; never changes production.
---

# Triage a production incident

You run in an incident-analysis session: started with
`--restricted --strict-mcp-config --tools "Bash,Read,Grep,Glob,Skill"` in an empty scratch directory,
signed in with `ProdReadMetadata` only (framework layer 2). You have no MCP tools: never try to
post to Slack, Linear or a ticket; the engineer does that.

1. Start from the alert: service, metric, time window, tenant if known. Ask the engineer for the
   incident issue ID; every later step refers to it.
2. Read metrics and masked logs through `ProdReadMetadata` (CloudWatch Logs Insights; masking
   applies there too). Never ask for unmasked data, never print a value that looks like a national
   ID, bank account or diagnosis: if one appears, stop and tell the engineer, because masking
   missed it (framework layer 6, threat T24).
3. Read the service's code and IaC in a separate, normal session if the engineer opens one; this
   session has no repository.
4. Write down: what changed recently (deploy runs, merged PRs), the likely cause, and the
   smallest change that would fix it, as IaC or code. Say what you did not verify.
5. Hand over to the incident responder: the fix becomes a pull request labelled `incident` that
   links the open incident issue (prod-change skill). If the fix is not expressible as a pull
   request, draft the JIT command list for the responder to request; you never run it, and the
   JIT terminal runs no agent.
6. Afterwards: draft the timeline for the incident issue from what you read, without customer
   data.
