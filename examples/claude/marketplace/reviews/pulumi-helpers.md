# Catalogue review: `pulumi-helpers` (plugin)

Second example of a review record (template: `example-formatter.md`). This one has a hook, so
the review is stricter: hooks run outside the sandbox with the engineer's access (📖 R1.5.5),
and with `allowManagedHooksOnly` (phase 2) a plugin's hooks run only if the plugin is
force-enabled in managed `enabledPlugins` (📖 R1.5.4).

| Field | Value |
|---|---|
| Entry | `pulumi-helpers` in `.claude-plugin/marketplace.json` |
| Kind | Plugin (skills + one `PostToolUse` hook) |
| Publisher | `example-vendor` (third party) |
| Source and pin | `git-subdir` `example-vendor/agent-tools`, path `plugins/pulumi-helpers`, `ref` `v1.3.0`, `sha` `0f1e2d3c4b5a69788796a5b4c3d2e1f00f1e2d3c` |
| Components | skills: yes · agents: no · monitors: no · LSP servers: no · `bin/` executables: no · hooks: one, reformats preview output files that the engineer already wrote with `pulumi preview --diff`; it does not run `pulumi` · MCP servers: no · mods: no |
| What it reads | Pulumi preview output in the working directory |
| Where it sends data | nowhere (reviewed: no network calls in the hook script) |
| Supplier register / BAA-DPA | not needed |
| Token passthrough / credentials | none: the hook runs no `pulumi` command and never reads `~/.aws` or `~/.pulumi` (reviewed) |
| Authentication | none |
| Write tools | none |
| Requested by / reason | `<engineer>`, `<ticket>` |
| Reviewer / date | `<reviewer ≠ requester>`, `<YYYY-MM-DD>` |
| Decision | Approved for non-prod work. Re-review on any change of `sha`; any new hook or MCP server is a new review. Under phase 2 (`allowManagedHooksOnly`) the hook runs only once the plugin is force-enabled in managed `enabledPlugins`, which `managed-settings.phase2.json` does not do yet: until then only the skills work. |
