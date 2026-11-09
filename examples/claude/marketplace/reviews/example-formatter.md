# Catalogue review: `example-formatter` (plugin)

Template for one catalogue entry (framework layer 4, ADR-0006). One file per plugin or MCP
server, added in the same pull request that adds or changes the entry. The pull request is
approved by the L3 owner team (the catalogue is an L3 path). Target: decision within 5 working
days of the request (S6).

| Field | Value |
|---|---|
| Entry | `example-formatter` in `.claude-plugin/marketplace.json` |
| Kind | Plugin (skills only) / MCP server local `stdio` / MCP server remote |
| Publisher | `example-vendor` (third party) |
| Source and pin | `github` `example-vendor/formatter-plugin`, `ref` `v2.0.0`, `sha` `a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0` |
| Components | skills: yes · agents: no · hooks: no · MCP servers: no · monitors: no · LSP servers: no · `bin/` executables: no · mods: no (hooks, monitors, LSP servers and mods run outside the sandbox, with the engineer's access; 📖 sandboxing, "What runs outside the sandbox") |
| What it reads | the files Claude passes to it in the working directory |
| Where it sends data | nowhere (no network calls found in the reviewed source) |
| Supplier register / BAA-DPA | not needed: no data leaves the laptop |
| Token passthrough | none |
| Write tools (Slack, Linear, GitHub) | none |
| Authentication | none |
| Requested by / reason | `<engineer>`, `<ticket>` |
| Reviewer / date | `<reviewer ≠ requester>`, `<YYYY-MM-DD>` |
| Decision | Approved, pinned to the SHA above. Re-review on any change of `sha`. |
| Known gap | For MCP servers, a change of tool descriptions after approval is not covered (framework layer 4, ⚠️ research 6.6): a local server is pinned only by its package version, and a remote server cannot be pinned at all. This entry is a plugin pinned by commit, so its contents change only with a new `sha`. |
