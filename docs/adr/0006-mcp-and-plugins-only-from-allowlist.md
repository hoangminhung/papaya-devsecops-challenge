# ADR-0006: MCP servers and plugins are allowed only from a reviewed, pinned catalogue

- **Status:** Accepted
- **Date:** 2026-11-09
- **Decided by:** owner of this submission (framework approval 2026-11-09; rollout priority framing Q8)
- **Scope:** Claude Code on all engineer laptops and in CI; Papaya's internal plugin marketplace

## 1. Context

Local MCP servers, plugins and hooks run with the engineer's access (📖 R1.6.2, R5.5.5); remote MCP
servers receive tokens and data. Papaya runs an internal plugin marketplace (brief, Appendix A), and
engineers install MCP servers without review (brief); use of Linear and Slack through MCP is assumed
(⚠️ G9). An unreviewed server or a plugin update can read the repo, the SSO cache or claim
data and send it out.

## 2. Options considered

| Option | Pros | Cons |
|---|---|---|
| A. Free choice, guidance only | No friction | No inventory; any server can exfiltrate |
| B. Denylist known-bad servers | Low friction | Misses new and changed servers |
| C. Allowlist (catalogue) enforced by managed settings | Inventory and supplier records; blocks unknown servers | Up to 5 working days' wait for a new tool (S6) |

## 3. Decision

Option C. The catalogue is a file in git, changed by PR under the L3 owner team.

- **Plugins:** only Papaya's marketplace via managed `strictKnownMarketplaces`, plus
  `blockedMarketplaces` (📖 R1.4.2); sources pinned to `ref`/`sha` (📖 R1.4.1b, link only);
  `disableSideloadFlags` (📖 R1.4.2); version floor covering the plugin-pin fix of 2.1.179 (📖 R6.2.7).
- **MCP:** `allowedMcpServers` with `allowManagedMcpServersOnly: true` (📖 R1.3.1, R1.3.4); match by
  `serverUrl` or `serverCommand` (exact argv), never `serverName`, which "is not a security control"
  (📖 R1.3.3); `disableClaudeAiConnectors: true` (📖 R1.3.7).
- **Review checklist** [design]: publisher, local or remote, what it reads and where it sends data,
  supplier-register entry and BAA/DPA status, no token passthrough (📖 R6.4.2), pinned version.
  Example entry: `serverCommand` = `["npx", "<package>@<exact-version>"]` [design; placeholder].
- **CI:** server-managed settings do not reach a CI job (📖 R1.7.10); CI uses a managed-settings
  file on the runner and a fixed MCP set, because `.mcp.json` loads without a prompt in `-p` runs
  (📖 R1.3.5).

## 4. Consequences

- **Positive:** Compliance gets an asset inventory and supplier records (P4c); unknown servers are
  refused before they load.
- **Negative / trade-offs:** waiting time for new tools; review effort for 1–2 DevSecOps people.
- **Risks & how we watch them:** the enforced copy lives in server-managed settings, edited in the
  admin console by Owners, not by PR (📖 R1.1.5); an Owner exports and diffs it with git monthly until
  G18 is solved (ADR-0007). `disableSideloadFlags` does not cover `.mcp.json` or `claude mcp add`
  (📖 R1.4.2), so the MCP allowlist must be locked. No per-group targeting in server-managed settings
  (📖 R1.1.6). Tool description changes after approval are not covered (⚠️). Without MDM, laptops can
  bypass server-managed settings (📖 R1.1.7; ⚠️ G11). Evidence: OTel `plugin_installed` /
  `plugin_loaded` (📖 R1.4.6).
- **Next steps:** catalogue v1 in phase 1 (may slip to phase 2 only with owner agreement).

## 5. References

- Framework layer 4; layer 8 rollout.
- Related: ADR-0007.
