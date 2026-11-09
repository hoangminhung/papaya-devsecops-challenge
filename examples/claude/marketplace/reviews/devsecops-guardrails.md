# Catalogue review: `devsecops-guardrails` (plugin, internal)

Internal entries are reviewed and pinned like third-party ones (OD26): a merge to the marketplace
repository reaches every engineer's laptop, so the pin, not the repository's branch, decides what
runs (📖 R9.4.5: a plugin source with `sha` checks out that commit).

| Field | Value |
|---|---|
| Entry | `devsecops-guardrails` in `.claude-plugin/marketplace.json` |
| Kind | Plugin (four skills) |
| Publisher | DevSecOps (control owner), internal |
| Source and pin | `git-subdir` `example-org/claude-plugins`, path `plugins/devsecops-guardrails`, `ref` `v2026.11.1`, `sha` `3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d` (placeholder; version 0.2.0) |
| Components | skills: `prod-change`, `incident-triage`, `risk-summary-explainer`, `dependency-fix` (framework §2) · agents, hooks, monitors, MCP servers, `bin/`, mods: none |
| What it reads | nothing; instructions only |
| Where it sends data | nowhere |
| Supplier register / BAA-DPA | not needed |
| Token passthrough / credentials | none |
| Authentication | none |
| Write tools | none |
| Requested by / reason | DevSecOps, framework layer 3 (how to ship a prod change) and §2 (agent-assisted DevSecOps workflows) |
| Reviewer / date | `<two L3 owner team members ≠ author>` (OD26: the catalogue is a process path), `<YYYY-MM-DD>` |
| Decision | Approved. Any change of `sha` is a new review. |
