# 02 — Research: what the tools can actually do today

Purpose: ground every later design decision in current, official documentation, not model memory.
Written in English (it will be quoted in `docs/`); short Vietnamese notes where useful.

## Evidence markers used in this file

This step uses the marker definitions the user set for the research phase (they are slightly
narrower than `CLAUDE.md` Rule 1, where ✅ means "verified in this environment"):

| Marker | Meaning here |
|---|---|
| ✅ | I opened and read the official page in this session; the statement paraphrases or quotes it. Where I also checked something on this machine, the line says **(local check)** |
| 📖 | From official documentation, but I did not open the specific page/section this session (e.g. known only from a link or summary), or the behaviour was not tried |
| ⚠️ | Assumption or inference, not confirmed by a source. Says what is needed to confirm it |

Rules: every claim has a link; no setting or feature name is used unless it appears in the cited
page; access dates are given per topic because these products change weekly.

Process (agreed 2026-11-08, see `CLAUDE.md` Rule 4): each topic is checked by an independent
reviewer subagent; review → fix → re-review until no HIGH/MEDIUM findings remain. Each topic ends
with a short review log.

Local environment for reference: Claude Code `2.1.319` (`claude --version`, **local check**).
Many documented features carry a minimum version (e.g. "requires v2.1.259 or later"); Papaya must
pin a minimum client version (see `requiredMinimumVersion` below).

---

## Topic 1 — Claude Code at organization level

**Accessed:** 2026-11-08. Pages (all under `https://code.claude.com/docs/en/`, also read as raw
`.md`): [settings](https://code.claude.com/docs/en/settings) ·
[settings-reference](https://code.claude.com/docs/en/settings-reference) ·
[managed-settings](https://code.claude.com/docs/en/managed-settings) ·
[server-managed-settings](https://code.claude.com/docs/en/server-managed-settings) ·
[permissions](https://code.claude.com/docs/en/permissions) ·
[permission-modes](https://code.claude.com/docs/en/permission-modes) ·
[hooks](https://code.claude.com/docs/en/hooks) ·
[mcp](https://code.claude.com/docs/en/mcp) ·
[managed-mcp](https://code.claude.com/docs/en/managed-mcp) ·
[plugins/org](https://code.claude.com/docs/en/plugins/org) ·
[plugins/mods/admin](https://code.claude.com/docs/en/plugins/mods/admin) ·
[plugin-marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) ·
[sandboxing](https://code.claude.com/docs/en/sandboxing) ·
[env-vars](https://code.claude.com/docs/en/env-vars) ·
[security](https://code.claude.com/docs/en/security) ·
[hipaa-setup](https://code.claude.com/docs/en/hipaa-setup) ·
[zero-data-retention](https://code.claude.com/docs/en/zero-data-retention) ·
[monitoring-usage](https://code.claude.com/docs/en/monitoring-usage) ·
[headless](https://code.claude.com/docs/en/headless) ·
[cli-reference](https://code.claude.com/docs/en/cli-reference) ·
[github-actions](https://code.claude.com/docs/en/github-actions) ·
[claude-code-action security.md](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md)

### 1.1 Configuration users cannot override ("managed settings")

| # | Finding | Marker | Source |
|---|---|---|---|
| 1.1.1 | Precedence, highest first: **managed** → command line (`--settings`) → project local (`.claude/settings.local.json`) → shared project (`.claude/settings.json`) → user (`~/.claude/settings.json`). "Nothing in your own settings files or `--settings` overrides a managed key." | ✅ | [settings#settings-precedence](https://code.claude.com/docs/en/settings#settings-precedence) |
| 1.1.2 | List keys (e.g. `permissions.allow`) **merge** across scopes rather than override; deny from any scope beats allow from any scope. "A managed settings deny can't be overridden by `--allowedTools`." | ✅ | [settings](https://code.claude.com/docs/en/settings#lists-merge-instead-of-overriding), [permissions#settings-precedence](https://code.claude.com/docs/en/permissions#settings-precedence) |
| 1.1.3 | Four delivery mechanisms: **server-managed** (claude.ai admin console, fetched at startup, polled hourly), **MDM/OS policy** (macOS profile domain `com.anthropic.claudecode`, Windows `HKLM\SOFTWARE\Policies\ClaudeCode`, checked every 30 min), **file** (`/etc/claude-code/managed-settings.json` on Linux/WSL, `/Library/Application Support/ClaudeCode/` on macOS, `C:\Program Files\ClaudeCode\` on Windows, plus a `managed-settings.d/` drop-in dir), **HKCU registry** (lowest). | ✅ | [managed-settings#choose-a-delivery-mechanism](https://code.claude.com/docs/en/managed-settings#choose-a-delivery-mechanism) |
| 1.1.4 | By default only **one** managed source supplies most keys (server-managed first, then MDM, then file); `managedSourcesBehavior: "merge"` composes them. **Exceptions:** "cross-source keys" are read from every admin source, e.g. `allowManagedMcpServersOnly`, `deniedMcpServers`, `disableClaudeAiConnectors`, the sandbox managed-only locks, `forceRemoteSettingsRefresh`, and `env` (merged per variable). `allowedProviders` has its own rule (machine list and server list intersect). `managed-mcp.json` is read separately from the settings tier. | ✅ | [managed-settings#keys-read-from-every-admin-source](https://code.claude.com/docs/en/managed-settings#keys-read-from-every-admin-source), [plugins/org](https://code.claude.com/docs/en/plugins/org#which-managed-source-applies-on-a-machine) |
| 1.1.5 | **Server-managed settings are available on Claude for Teams and Enterprise**; editing needs the **Owner / Primary Owner** role. Relevant: Papaya is on Team Premium. | ✅ | [server-managed-settings#requirements](https://code.claude.com/docs/en/server-managed-settings#requirements) |
| 1.1.6 | Server-managed limitations: settings apply **uniformly to the whole org** (no per-group policy yet); `managed-mcp.json` cannot be delivered this way. Per-group policy is possible with separate endpoint files/profiles, or with a self-hosted **Claude apps gateway**, which "delivers managed settings per IdP group". | ✅ | [server-managed-settings#current-limitations](https://code.claude.com/docs/en/server-managed-settings#current-limitations), [managed-settings#choose-a-delivery-mechanism](https://code.claude.com/docs/en/managed-settings#choose-a-delivery-mechanism) |
| 1.1.7 | Docs state plainly that server-managed settings are "**a client-side control, not a security boundary**. On unmanaged devices, a user doesn't need admin or sudo access to bypass them." Bypass cases listed: editing/deleting the local cache, modified or older binary, **authenticating with a different org or a Console API key**, or **setting a `CLAUDE_CODE_USE_*` provider variable** (`…_BEDROCK`, `…_VERTEX`, `…_MANTLE`, `…_FOUNDRY`, `…_ANTHROPIC_AWS`) **or a non-default `ANTHROPIC_BASE_URL`**. | ✅ | [server-managed-settings#security-considerations](https://code.claude.com/docs/en/server-managed-settings#security-considerations) |
| 1.1.8 | Endpoint-managed (MDM/file) "provide stronger security guarantees because the settings file can be protected from user modification at the OS level", but a developer with **local admin** can still edit the managed source; managed settings "bind Claude Code only" — another API client is not covered. | ✅ | [server-managed-settings](https://code.claude.com/docs/en/server-managed-settings#choose-between-server-managed-and-endpoint-managed-settings), [managed-settings#what-a-developer-can-change](https://code.claude.com/docs/en/managed-settings#what-a-developer-can-change) |
| 1.1.9 | `forceRemoteSettingsRefresh: true` makes startup **fail closed**: the CLI blocks until a fresh fetch succeeds and exits if it fails. **Caveats:** it does not close the 1.1.7 bypasses — "A session that doesn't fetch server-managed settings starts without waiting"; and if `api.anthropic.com` is unreachable, nobody can start Claude Code. | ✅ | [server-managed-settings#enforce-fail-closed-startup](https://code.claude.com/docs/en/server-managed-settings#enforce-fail-closed-startup) |
| 1.1.10 | Server-delivered **hooks, shell-command settings, some `env` vars and sandbox-weakening keys** show a security approval dialog **in interactive sessions**; if the user rejects, Claude Code exits. In a non-interactive run (`claude -p`, Agent SDK, VS Code chat panel, desktop Code tab) "Claude Code can't show the dialog. When the delivered settings would require approval, they apply for that run only." A managed `claudeMd` value needs no approval. | ✅ | [server-managed-settings#security-approval-dialogs](https://code.claude.com/docs/en/server-managed-settings#security-approval-dialogs) |
| 1.1.11 | Invalid managed entries: many locks **fail closed** (e.g. an unreadable `permissions.disableBypassPermissionsMode` reads as its restrictive value; an unreadable `deny` list withholds `allow`), from v2.1.282. **Fail-open cases also exist:** "`requiredMinimumVersion` and `requiredMaximumVersion` fail open by design"; an invalid `disableAllHooks` is dropped; and "If the operating system denied the read, for example on a root-only file, every session starts without that source's policies" (reported only in `/status`, `claude doctor`, and stderr of `-p` runs; no startup error). ⇒ A wrongly-permissioned policy file silently removes the policy. | ✅ | [managed-settings#keys-that-fail-closed](https://code.claude.com/docs/en/managed-settings#keys-that-fail-closed), [managed-settings#find-entries-claude-code-dropped](https://code.claude.com/docs/en/managed-settings#find-entries-claude-code-dropped) |
| 1.1.12 | Audit events for settings changes (who, which device, old/new value) exist "through the compliance API or audit log export. Contact your Anthropic account team for access." | ✅ (exists) / ⚠️ (availability on **Team** plan not stated — ask Anthropic) | [server-managed-settings#audit-logging](https://code.claude.com/docs/en/server-managed-settings#audit-logging) |
| 1.1.13 | `requiredMinimumVersion` (and `requiredMaximumVersion`) blocks a binary outside the range from starting; does not end a running session; an invalid value fails open. | ✅ | [managed-settings#where-and-when-a-policy-applies](https://code.claude.com/docs/en/managed-settings#where-and-when-a-policy-applies), [managed-settings#keys-that-fail-closed](https://code.claude.com/docs/en/managed-settings#keys-that-fail-closed) |
| 1.1.14 | A few security keys honour a **stricter** value from a lower scope even over managed (e.g. `permissions.blockReadsOutsideWorkingDirectories: true`, `permissions.blockWritesOutsideWorkingDirectories: true` (v2.1.314+), `disableClaudeAiConnectors: true`). Users can tighten, not loosen. | ✅ | [settings#exceptions-to-managed-settings-precedence](https://code.claude.com/docs/en/settings#exceptions-to-managed-settings-precedence) |
| 1.1.15 | **`allowedProviders`** (managed, v2.1.285+) lists which providers a machine may use (`anthropic`, `bedrock`, `vertex`, `foundry`, `anthropicAws`, `mantle`, `customEndpoint`, `gateway`); "A session on a provider that isn't listed is refused at startup, at login, and when it next contacts the API". A list from MDM/file keeps applying when server-managed settings also send one ("can narrow … but never widen"). Pair with `forceLoginOrgUUID` / `forceLoginMethod` to pin sign-in to Papaya's org. ⇒ On endpoint-managed machines this closes most of the 1.1.7 bypasses. | ✅ | [settings-reference#allowedproviders](https://code.claude.com/docs/en/settings-reference#allowedproviders), [settings-reference#forceloginorguuid](https://code.claude.com/docs/en/settings-reference#forceloginorguuid) |
| 1.1.16 | **Managed instructions:** key `claudeMd` (managed scope) injects organization-wide CLAUDE.md text "ahead of user and project CLAUDE.md files". It is instruction text, not enforcement. | ✅ | [settings-reference#claudemd](https://code.claude.com/docs/en/settings-reference#claudemd) |
| 1.1.17 | A managed `model` "is a starting default, not a lock"; the locks are `availableModels` and `deniedModels`. | ✅ | [settings#settings-precedence](https://code.claude.com/docs/en/settings#settings-precedence) |
| 1.1.18 | Proving a policy is in force: `/status` shows `Setting sources` (and the managed source); `claude doctor` lists dropped entries and an `Organization policy` line (v2.1.261+). Useful as audit evidence. | ✅ | [managed-settings#check-that-a-policy-is-in-force](https://code.claude.com/docs/en/managed-settings#check-that-a-policy-is-in-force), [managed-settings#keys-only-a-managed-source-can-set](https://code.claude.com/docs/en/managed-settings#keys-only-a-managed-source-can-set) |
| 1.1.19 | On Team/Enterprise an Owner turns **Remote Control** and **cloud sessions** on/off org-wide; `disableRemoteControl` disables Remote Control per device. Cloud sessions in Anthropic-hosted environments receive **only server-managed** settings. | ✅ | [managed-settings#keys-only-a-managed-source-can-set](https://code.claude.com/docs/en/managed-settings#keys-only-a-managed-source-can-set) (note), [managed-settings#where-and-when-a-policy-applies](https://code.claude.com/docs/en/managed-settings#where-and-when-a-policy-applies) |
| 1.1.20 | **Telemetry is not a tamper-proof audit log:** OTel exporter selectors follow normal precedence and "A developer's setting can still disable a signal … so set the selectors in managed settings too". | ✅ | [monitoring-usage](https://code.claude.com/docs/en/monitoring-usage) |
| 1.1.21 | Server-managed settings page recommends network-level **Tenant Restrictions** to stop sign-in to other Claude orgs. | 📖 (support article not opened) | [support.claude.com/…/13198485](https://support.claude.com/en/articles/13198485) |

### 1.2 Blocking permission-bypass modes

| # | Finding | Marker | Source |
|---|---|---|---|
| 1.2.1 | Permission modes: `default` (labelled Manual), `acceptEdits`, `plan`, `auto` (a background classifier reviews actions), `dontAsk` (auto-deny anything that would prompt), `bypassPermissions` (skip prompts; "Only use this mode in isolated environments like containers or VMs"). | ✅ | [permissions#permission-modes](https://code.claude.com/docs/en/permissions#permission-modes) |
| 1.2.2 | **To block bypass and auto:** set `permissions.disableBypassPermissionsMode` and/or `permissions.disableAutoMode` to `"disable"`. Works from any scope; in managed settings it cannot be overridden. | ✅ | [permissions#permission-modes](https://code.claude.com/docs/en/permissions#permission-modes), [permissions#managed-settings](https://code.claude.com/docs/en/permissions#managed-settings) |
| 1.2.3 | "With Claude Code v2.1.283 or later, **auto mode is the built-in starting permission mode** for interactive terminal and VS Code sessions." Auto mode is **not** bypass: a classifier reviews actions and blocks those it judges unsafe, and explicit ask/deny rules still apply. `-p` runs start in `default` (Manual). So, out of the box, routine prompts are replaced by a model's judgement unless the org sets `disableAutoMode` or a `defaultMode`. | ✅ | [permission-modes#which-mode-a-session-starts-in](https://code.claude.com/docs/en/permission-modes#which-mode-a-session-starts-in), [security#permission-based-architecture](https://code.claude.com/docs/en/security#permission-based-architecture) |
| 1.2.4 | `permissions.defaultMode` values `auto` and `bypassPermissions` **do not take effect from project or local settings** — a cloned repo cannot switch them on. ("Before v2.1.257, `bypassPermissions` took effect from any file.") | ✅ | [settings#a-value-you-set-is-ignored](https://code.claude.com/docs/en/settings#a-value-you-set-is-ignored) |
| 1.2.5 | `allowManagedPermissionRulesOnly` (managed-only) makes managed settings the **only** source of permission rules. | ✅ | [managed-settings#keys-only-a-managed-source-can-set](https://code.claude.com/docs/en/managed-settings#keys-only-a-managed-source-can-set) |
| 1.2.6 | **Bash permission rules are not a security boundary.** `Bash(git push *)` in deny does not stop `git -C . push …`, `/usr/bin/curl`, or `sh -c '…'`. The docs point to sandboxing or a PreToolUse hook for real enforcement. | ✅ | [permissions#what-a-bash-rule-doesnt-match](https://code.claude.com/docs/en/permissions#what-a-bash-rule-doesnt-match) |
| 1.2.7 | CLI flags `--dangerously-skip-permissions` and `--allow-dangerously-skip-permissions` exist on the installed client. Setting `skipDangerousModePermissionPrompt` (user, local or managed scope) skips the confirmation dialog before bypass mode. | ✅ **(local check: `claude --help`)**; ✅ settings-reference | [settings-reference#skipdangerousmodepermissionprompt](https://code.claude.com/docs/en/settings-reference#skipdangerousmodepermissionprompt) |
| 1.2.8 | **Workspace trust:** a project's `permissions.allow` and `additionalDirectories` apply only after the user accepts the trust dialog; `deny`/`ask` apply immediately. The dialog exists only in interactive sessions. | ✅ | [permissions#project-allow-rules-and-workspace-trust](https://code.claude.com/docs/en/permissions#project-allow-rules-and-workspace-trust) |
| 1.2.9 | `permissions.blockReadsOutsideWorkingDirectories` / `blockWritesOutsideWorkingDirectories` stop the **file tools** (Read/Edit) from leaving the working directories — something the sandbox does not cover (see 1.6.2). | ✅ | [settings#exceptions-to-managed-settings-precedence](https://code.claude.com/docs/en/settings#exceptions-to-managed-settings-precedence), [permissions#block-file-tool-reads-and-writes-outside-the-working-directories](https://code.claude.com/docs/en/permissions#block-file-tool-reads-and-writes-outside-the-working-directories) |

### 1.3 Controlling MCP servers

| # | Finding | Marker | Source |
|---|---|---|---|
| 1.3.1 | Patterns: **Disable MCP** (`managed-mcp.json` with empty map), **Fixed deployment** (`managed-mcp.json`), **Provided servers** (`managedMcpServers`, v2.1.259+), **Approved catalog** (`allowedMcpServers` + `allowManagedMcpServersOnly: true`), **Plugin servers only** (`strictPluginOnlyCustomization` with `mcp`), **Soft allowlist** (`allowedMcpServers` without the lock — users can broaden it), **Denylist only** (`deniedMcpServers`). | ✅ | [managed-mcp#choose-a-pattern](https://code.claude.com/docs/en/managed-mcp#choose-a-pattern) |
| 1.3.2 | `managed-mcp.json` gives **exclusive control** (users cannot add servers, plugin servers and `--mcp-config` are blocked) but must be deployed to a **system path** by MDM/fleet tooling — it **cannot** come from server-managed settings. | ✅ | [managed-mcp#exclusive-control-with-managed-mcpjson](https://code.claude.com/docs/en/managed-mcp#exclusive-control-with-managed-mcpjson) |
| 1.3.3 | Allow/deny entries match by `serverUrl` (wildcards), `serverCommand` (exact argv) or `serverName`. **`serverName` "is not a security control"** (user-chosen label). Denylist always wins. | ✅ | [managed-mcp#match-servers-by-url-command-or-name](https://code.claude.com/docs/en/managed-mcp#match-servers-by-url-command-or-name) |
| 1.3.4 | Without `allowManagedMcpServersOnly`, user allowlists merge in and can **broaden** the org list. `allowManagedPermissionRulesOnly` does **not** enforce the MCP allowlist. | ✅ | [managed-mcp#policy-based-control-with-allowlists-and-denylists](https://code.claude.com/docs/en/managed-mcp#policy-based-control-with-allowlists-and-denylists) |
| 1.3.5 | In interactive sessions, project `.mcp.json` servers need approval and a cloned repo cannot pre-approve them; **in `claude -p`, SDK and cloud sessions they load without asking.** | ✅ | [mcp](https://code.claude.com/docs/en/mcp) (project scope), [permissions#what-runs-before-you-trust-a-folder](https://code.claude.com/docs/en/permissions#what-runs-before-you-trust-a-folder) |
| 1.3.6 | "Anthropic reviews connectors against its listing criteria before adding them to the Anthropic Directory, but does not security-audit or manage any MCP server." | ✅ | [security#mcp-security](https://code.claude.com/docs/en/security#mcp-security) |
| 1.3.7 | claude.ai connectors: `disableClaudeAiConnectors: true` turns off the connectors Claude Code fetches itself (honoured from any scope); `managed-mcp.json` suppresses them unless `allowAllClaudeAiMcps` is set. | ✅ | [managed-mcp#allow-claudeai-connectors-alongside-the-managed-set](https://code.claude.com/docs/en/managed-mcp#allow-claudeai-connectors-alongside-the-managed-set), [settings#exceptions-to-managed-settings-precedence](https://code.claude.com/docs/en/settings#exceptions-to-managed-settings-precedence) |
| 1.3.8 | OpenTelemetry with `OTEL_LOG_TOOL_DETAILS=1` records which MCP servers/tools are invoked. | ✅ (stated) / 📖 (event schema not opened) | [managed-mcp#monitor-mcp-usage](https://code.claude.com/docs/en/managed-mcp#monitor-mcp-usage) |

### 1.4 Controlling the plugin marketplace

| # | Finding | Marker | Source |
|---|---|---|---|
| 1.4.1 | A marketplace is a git repo (can be **private**) with `.claude-plugin/marketplace.json`; plugin sources: relative path, `github`, `git-subdir` (monorepo subdirectory), `url`, `archive`, `npm`, `command`. | ✅ | [plugin-marketplaces#choose-a-plugin-source](https://code.claude.com/docs/en/plugin-marketplaces#choose-a-plugin-source) |
| 1.4.1b | Git-based plugin sources can be pinned to a `ref` or `sha`. | 📖 (stated by link only; reference page not opened) | [plugins/marketplace-reference#plugin-sources](https://code.claude.com/docs/en/plugins/marketplace-reference#plugin-sources) |
| 1.4.2 | Policy keys in the control matrix: `strictKnownMarketplaces` (allowlist of sources; `[]` blocks all), `blockedMarketplaces` (checked first), `enabledPlugins` (`true` force-enables, `false` blocks everywhere; any scope, locked when managed), `disableSideloadFlags` (rejects `--plugin-dir`, `--plugin-url`, `--agents`, `--mcp-config`; does **not** restrict `.mcp.json` or `claude mcp add`), `strictPluginOnlyCustomization`, `disableCommandPluginSources`, `syncClaudeAiPlugins: false`. "Every key in the table is a managed setting, apart from `enabledPlugins`, `syncClaudeAiPlugins`, …". `extraKnownMarketplaces` (not in the matrix) registers a marketplace. | ✅ | [plugins/org#control-matrix](https://code.claude.com/docs/en/plugins/org#control-matrix), [plugins/org#require-a-marketplace-and-its-plugins](https://code.claude.com/docs/en/plugins/org#require-a-marketplace-and-its-plugins) |
| 1.4.3 | Allowlist is checked **before download and again at session start**; an installed plugin from a no-longer-allowed source stops loading. | ✅ | [plugins/org#restrict-what-users-can-install](https://code.claude.com/docs/en/plugins/org#restrict-what-users-can-install) |
| 1.4.4 | Gaps the docs list themselves: no per-group targeting via server-managed settings; cannot restrict individual entries inside an allowed marketplace except via `enabledPlugins: false`; no key hides `/plugin`. | ✅ | [plugins/org#plan-for-what-managed-settings-cant-enforce](https://code.claude.com/docs/en/plugins/org#plan-for-what-managed-settings-cant-enforce) |
| 1.4.5 | For CI/containers: pre-build a **seed** directory and set `CLAUDE_CODE_PLUGIN_SEED_DIR`; seeds are read-only and still subject to the allowlist. | ✅ | [plugins/org#seed-containers-and-ci](https://code.claude.com/docs/en/plugins/org#seed-containers-and-ci) |
| 1.4.6 | Telemetry: `claude_code.plugin_installed` / `claude_code.plugin_loaded` OTel events; Analytics API per-plugin counts on **Enterprise** plan. | ✅ | [plugins/org#audit-and-review](https://code.claude.com/docs/en/plugins/org#audit-and-review) |

### 1.5 Controlling hooks

| # | Finding | Marker | Source |
|---|---|---|---|
| 1.5.1 | Hook events include `PreToolUse`, `PermissionRequest`, `PostToolUse`, `UserPromptSubmit`, `SessionStart`, `SessionEnd`, `ConfigChange`, `InstructionsLoaded`, `Stop`, among others. | ✅ | [hooks](https://code.claude.com/docs/en/hooks) |
| 1.5.2 | A `PreToolUse` hook **blocks** a call by exiting `2` (stderr is shown to Claude) or by returning JSON `permissionDecision: "deny"`. Exit 2 blocks even if JSON says allow. **By default hooks fail open:** any other non-zero exit, a hook that does not start, invalid JSON, or (on `PreToolUse`) a timeout lets the action go ahead. **To fail closed**, set `"onFailure": "block"` on a `command` or `http` hook (v2.1.295+). | ✅ | [hooks](https://code.claude.com/docs/en/hooks) (exit codes; "Block the action when a hook fails") |
| 1.5.3 | Hook decisions never bypass deny/ask rules; a blocking hook beats allow rules. | ✅ | [permissions#precedence-among-rules-hooks-and-mods](https://code.claude.com/docs/en/permissions#precedence-among-rules-hooks-and-mods) |
| 1.5.4 | `allowManagedHooksOnly` (managed-only): user, project, local and plugin hooks are blocked, except hooks from plugins force-enabled in managed `enabledPlugins`. `disableAllHooks` in a lower scope **cannot** disable managed hooks. HTTP hooks can be limited with `allowedHttpHookUrls` and `httpHookAllowedEnvVars`. | ✅ | [hooks](https://code.claude.com/docs/en/hooks) (enterprise controls), [managed-settings](https://code.claude.com/docs/en/managed-settings#keys-only-a-managed-source-can-set) |
| 1.5.5 | Hooks run **outside** the sandbox, "with your full access". | ✅ | [sandboxing#what-runs-outside-the-sandbox](https://code.claude.com/docs/en/sandboxing#what-runs-outside-the-sandbox) |
| 1.5.6 | "Mods" (plugins that run JS inside Claude Code) can approve calls a deny rule refuses **unless** managed settings or a Team/Enterprise `/login` is present. "A session that runs on an API key or a long-lived `CLAUDE_CODE_OAUTH_TOKEN` instead isn't using that login" ⇒ a CI run on an API key **without** managed settings is exposed. Admin control: option `allowManagedModsOnly` under `pluginConfigs` → `cc-plugin-sec-default@builtin` → `options` in managed settings (not a top-level key). | ✅ | [permissions#precedence-among-rules-hooks-and-mods](https://code.claude.com/docs/en/permissions#precedence-among-rules-hooks-and-mods), [plugins/mods/admin#stop-user-installed-mods-from-loading](https://code.claude.com/docs/en/plugins/mods/admin#stop-user-installed-mods-from-loading) |
| 1.5.7 | Docs recommend `ConfigChange` hooks to "audit or block settings changes during sessions". **Caveat:** they do not run "when server-managed settings arrive or refresh, or when an MDM profile or registry policy changes, and a hook can't block a `policy_settings` change." | ✅ | [security#team-security](https://code.claude.com/docs/en/security#team-security), [server-managed-settings#security-considerations](https://code.claude.com/docs/en/server-managed-settings#security-considerations) |

### 1.6 Sandbox and data handling

| # | Finding | Marker | Source |
|---|---|---|---|
| 1.6.1 | Sandbox is **off by default**; runs on macOS (Seatbelt), Linux and WSL2 (`bubblewrap` + `socat`); **native Windows runs commands unsandboxed**. | ✅ | [sandboxing](https://code.claude.com/docs/en/sandboxing) |
| 1.6.2 | Scope: **shell commands only** (Bash, PowerShell, Monitor). Outside it, two groups: (a) built-in **file and web tools** (Read, Edit, Write, WebFetch, WebSearch) "follow permission rules instead. A `denyRead` entry doesn't stop the Read tool, and `allowedDomains` doesn't limit WebFetch"; (b) **hooks, local MCP servers, LSP servers, helpers, mods**, `!` shell-mode commands and `excludedCommands` run "with your full access". | ✅ | [sandboxing#what-runs-outside-the-sandbox](https://code.claude.com/docs/en/sandboxing#what-runs-outside-the-sandbox) |
| 1.6.3 | Defaults: writes limited to working dir + temp; **reads allowed for most of the machine including `~/.aws/credentials` and `~/.ssh`**; network goes through a proxy with an initially empty domain allowlist. | ✅ | [sandboxing](https://code.claude.com/docs/en/sandboxing) |
| 1.6.4 | Keys used for a hardened profile: `sandbox.enabled`, `sandbox.failIfUnavailable`, `sandbox.allowUnsandboxedCommands: false` (ignore the escape parameter), `sandbox.filesystem.denyRead`, `sandbox.credentials` (deny/mask; "affects sandboxed Bash commands only"), `sandbox.network.allowedDomains`, `sandbox.network.allowManagedDomainsOnly` (managed-only), `sandbox.excludedCommands` (excluded commands run with full access). | ✅ | [sandboxing](https://code.claude.com/docs/en/sandboxing), [managed-settings](https://code.claude.com/docs/en/managed-settings#keys-only-a-managed-source-can-set) |
| 1.6.5 | `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` strips credentials from subprocesses (Bash, hooks, stdio MCP servers), recognised by variable name or value shape — **but it "leaves GitHub tokens and proxy settings in place"** (`GITHUB_TOKEN`, `GH_TOKEN`, …). Docs: give Actions jobs the narrowest `permissions`, and use a `sandbox.credentials` deny to remove a GitHub token from sandboxed Bash. | ✅ | [env-vars](https://code.claude.com/docs/en/env-vars) (subprocess environment scrub) |
| 1.6.6 | Docs recommend, for extra isolation, running the **whole Claude Code process** in the sandbox runtime or a dev container. | ✅ | [security#working-with-sensitive-code](https://code.claude.com/docs/en/security#working-with-sensitive-code), [devcontainer](https://code.claude.com/docs/en/devcontainer) (not opened, 📖) |
| 1.6.7 | **HIPAA configuration is Enterprise-only and requires a BAA:** "The HIPAA configuration is an organization setting on Claude Enterprise plans, for organizations that handle protected health information (PHI) and have a Business Associate Agreement (BAA)". The VS Code/JetBrains extensions are **not covered by the BAA**. Anthropic's `settings-hipaa.json` example can still serve as a technical template, but it does not make a Team org HIPAA-ready. | ✅ | [hipaa-setup](https://code.claude.com/docs/en/hipaa-setup), [managed-settings#choose-a-delivery-mechanism](https://code.claude.com/docs/en/managed-settings#choose-a-delivery-mechanism) |
| 1.6.8 | **Zero Data Retention** for Claude Code "is available to qualified accounts on Claude for Enterprise". | ✅ | [zero-data-retention](https://code.claude.com/docs/en/zero-data-retention) |

### 1.7 Running Claude Code in CI

| # | Finding | Marker | Source |
|---|---|---|---|
| 1.7.1 | Non-interactive: `claude -p`, with `--allowedTools`, `--permission-mode`, `--output-format json|stream-json`, `--json-schema`, `--max-budget-usd` (headless page); `--disallowedTools` and `--max-turns` (cli-reference; `--max-turns` is "print mode only" and is **not listed** in local `claude --help` 2.1.319). From v2.1.302 a `-p` run starts in **Manual** mode and denies anything needing approval unless a rule/hook approves it. `dontAsk` is described as "useful for locked-down CI runs". | ✅ (+ **local check**) | [headless](https://code.claude.com/docs/en/headless), [cli-reference](https://code.claude.com/docs/en/cli-reference) |
| 1.7.2 | `--bare` skips auto-discovery of hooks, skills, plugins, MCP servers, CLAUDE.md; "recommended mode for scripted and SDK calls" and planned to become the default for `-p`. Hooks do not run in bare mode (even via `--settings` or a plugin). Bare mode never reads OAuth credentials. **Whether managed hooks, managed permission rules and the sandbox still apply under `--bare` is not stated in the pages read.** | ✅ (documented parts) / ⚠️ (managed policy under `--bare` — test on a runner) | [headless#start-faster-with-bare-mode](https://code.claude.com/docs/en/headless#start-faster-with-bare-mode) |
| 1.7.3 | **Risk:** in a `-p` run the folder is never trusted, yet the repo's settings **hooks, `env` block, helper commands such as `apiKeyHelper`, and a project skill's hooks** run, and `.mcp.json` servers connect without asking. Even with `--bare`, "the project's `env` block and helpers such as `awsAuthRefresh` in its settings files still apply". Documented mitigations: `--setting-sources user`, `--settings '{"disableAllHooks": true}'`, `disabledMcpjsonServers`. (Project `permissions.allow` is *not* used in untrusted `-p`.) | ✅ | [permissions#what-runs-before-you-trust-a-folder](https://code.claude.com/docs/en/permissions#what-runs-before-you-trust-a-folder), [headless](https://code.claude.com/docs/en/headless#start-faster-with-bare-mode) |
| 1.7.4 | `--permission-prompts none` (v2.1.259+) matters mainly when a permission host exists (`canUseTool`, `--permission-prompt-tool`); "In a `-p` run with no host, these requests are denied either way". `PermissionRequest` hooks can still allow. Denials appear in `permission_denials`. | ✅ | [headless#turn-off-permission-prompts-in-unattended-runs](https://code.claude.com/docs/en/headless#turn-off-permission-prompts-in-unattended-runs) |
| 1.7.5 | GitHub Action `anthropics/claude-code-action@v1`: interactive mode (`@claude` mention) or automation mode (`prompt` input); inputs include `claude_args`, `settings`, `plugin_marketplaces`, `plugins`, `use_bedrock`, `use_vertex`. | ✅ | [github-actions](https://code.claude.com/docs/en/github-actions) |
| 1.7.6 | Auth options: `ANTHROPIC_API_KEY`; `CLAUDE_CODE_OAUTH_TOKEN` ("tied to the subscription of the person who ran `claude setup-token`" — not for shared org use); **Anthropic workload identity federation** via the workflow's GitHub OIDC token (`anthropic_federation_rule_id`, needs `id-token: write`); or **Bedrock / Vertex via OIDC** (no static cloud keys). | ✅ | [github-actions#set-up-for-an-organization](https://code.claude.com/docs/en/github-actions#set-up-for-an-organization) |
| 1.7.7 | Trigger guard: actor must have **write access**; bots rejected unless in `allowed_bots` — but "**Allowed bots are not checked for repository permissions**"; `allowed_non_write_users` is "a significant security risk". `claude-code-base-action` "does not perform actor permission checks". | ✅ | [github-actions#who-can-trigger-runs](https://code.claude.com/docs/en/github-actions#who-can-trigger-runs), [action security.md](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md) |
| 1.7.8 | The official Claude GitHub App requests a **broad** permission set; GitHub does not allow accepting a subset. A **custom GitHub App** with Contents/Issues/Pull requests only is the documented alternative. **Discrepancy between official sources:** code.claude.com lists Actions "Read and write" and Workflows "Read and write"; the action's security.md lists Actions as "Read" and Workflows RW under permissions "requested but not yet actively used". | ✅ (both read) | [github-actions#github-app-permissions](https://code.claude.com/docs/en/github-actions#github-app-permissions), [action security.md](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md) |
| 1.7.9 | `pull_request_target` / `workflow_run` run with base-repo secrets: "Do not check out an untrusted ref into the workspace root before this action." On PRs the action **restores Claude config from the base branch** (`.claude/`, `.mcp.json`, `CLAUDE.md`, …) but `package.json`, lockfiles, `Makefile` stay at PR head. Input sanitisation strips HTML comments, invisible characters, hidden attributes, "but new bypass techniques may emerge". Commits are unsigned by default (`use_commit_signing` available). | ✅ | [action security.md](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md) |
| 1.7.10 | **Server-managed settings do not reach a CI job** authenticated with a Console API key, workload identity federation, or Bedrock/Vertex. Docs give two options: (a) an OAuth token from `claude setup-token` authorised for the Team org — ties CI to one person's subscription (conflicts with 1.7.6) and does not work with `--bare`; (b) an endpoint `managed-settings.json` on the machine that runs the job. | ✅ | [server-managed-settings#platform-availability](https://code.claude.com/docs/en/server-managed-settings#platform-availability) |

### 1.8 What this means for Papaya (inferences — to be used in the design)

These are my conclusions from the findings above, not documented facts:

1. **Policy layer exists and is real, but it is client-side.** Managed settings can lock bypass/auto
   mode, MCP, plugins and hooks (1.1, 1.2). The docs themselves say it is not a security boundary
   (1.1.7, 1.1.8), and some failure modes are silent (1.1.11). ⇒ Compliance's rule ("named human
   approves prod changes") **cannot rest on Claude Code settings**. It must be enforced where the
   agent cannot reach: AWS IAM / GitHub (Topics 2–3). Claude Code settings are a *safety and
   hygiene* layer (fewer mistakes), not the control of record.
2. **Team plan is enough for the technical policy layer, not for PHI.** Team has server-managed
   settings (1.1.5) but not the HIPAA configuration/BAA (1.6.7), ZDR (1.6.8) or the Analytics API
   (1.4.6); settings-change audit on Team is uncertain (1.1.12). ⇒ Either the design guarantees
   that **agents never see PHI/production data** (fits Topic-0 scope: non-prod is synthetic), or
   Papaya moves to Enterprise + BAA. This is a decision for Papaya (open item).
3. **Two delivery paths are needed:** server-managed for laptops; an endpoint `managed-settings.json`
   (+ `managed-mcp.json` if exclusive MCP control is wanted, + `allowedProviders`/`forceLoginOrgUUID`
   to close provider bypasses, 1.1.15) on every machine that runs an agent unattended, because
   server-managed settings do not reach CI (1.7.10) and are skipped when a provider env var is set
   (1.1.7). On **GitHub-hosted runners** there is no image to bake into: the file would be written
   by a workflow step, and the agent step must not be able to rewrite it (⚠️ depends on whether the
   agent step has sudo — check in Topic 3). Self-hosted runners or a container image are cleaner.
4. **Defaults are permissive for this context:** interactive sessions start in auto mode, where a
   classifier — not a human — approves routine actions (1.2.3); sandbox is off (1.6.1); hooks fail
   open (1.5.2); `-p` runs execute repo hooks, `env` and helpers and connect `.mcp.json` (1.7.3).
   Each needs an explicit control: org settings (`disableAutoMode`, `sandbox.enabled`), per-hook
   `onFailure: "block"` on managed hooks, and CI flags (`--setting-sources user`,
   `--settings '{"disableAllHooks": true}'`).
5. **Bash deny rules are advisory** (1.2.6), and the sandbox covers only shell commands (1.6.2).
   Keeping prod credentials away from the agent needs several layers: sandbox
   `denyRead`/`credentials` for Bash, `Read(...)` deny rules and `blockReadsOutsideWorkingDirectories`
   for file tools, env scrub (which keeps GitHub tokens, 1.6.5), or the whole process in a
   container (1.6.6). The decisive layer is still **no prod credentials on the agent's machine at
   all**, plus IAM on the AWS side.

### 1.9 Open items to verify (Topic 1)

#### Quyết định của owner (2026-11-08)

Recorded verbatim, as written by the repo owner in the session of 2026-11-08:

> - Về PHI: Mặc định agent DevSecOps nằm ngoài phạm vi PHI, thiết kế để PHI không tới được agent. Chỉ xem xét gói Enterprise + BAA cho một môi trường riêng nếu sau này có nhu cầu thật.
> - Về MDM: chưa biết, thiết kế chuẩn bị cho cả hai.

#### Items

- [ ] ⚠️ Is the compliance API / audit-log export for settings changes available on the **Team**
      plan, or Enterprise only? (1.1.12) — needs Anthropic account team.
- [x] **Decided 2026-11-08 (owner)** — see "Quyết định của owner" above. Decision for Papaya:
      "agents never touch PHI" vs. Enterprise + BAA + ZDR (1.6.7, 1.6.8, 1.8 #2). → Chosen:
      the agent is outside PHI scope by default; Enterprise + BAA is considered only for a separate
      environment if there is a real need. Note: this item's wording included ZDR, but the owner
      decision names only "Enterprise + BAA". ZDR may conflict with the BAA's Covered Models
      (1.11.3.10). Definitions and leak paths: 1.11.
- [ ] ⚠️ Do managed hooks / permission rules / sandbox still apply under `--bare`? (1.7.2) — test
      on a runner with a managed-settings file.
- [x] **Answered in Topic 3 (3.5.1):** On GitHub-hosted runners, can the agent step write to
      `/etc/claude-code/`? (1.8 #3). Standard Linux runners have passwordless `sudo`, so yes,
      if the agent has shell access.
- [ ] 📖 Read the `settings-hipaa.json` example and the Tenant Restrictions article (Topic 5).
- [ ] 📖 Open the settings-reference entries for `allowManagedHooksOnly`,
      `strictPluginOnlyCustomization` before quoting exact semantics in `examples/`.
- [x] **Design approach decided 2026-11-08 (owner)** — see "Quyết định của owner" above. ⚠️ Whether
      Papaya devices are under MDM (decides if `managed-mcp.json` exclusive control and endpoint
      `allowedProviders` are possible on laptops). Unknown; the design must offer both paths.
- [ ] ⚠️ The MDM fact itself is still unknown: ask Papaya whether devices are under MDM (the answer
      chooses which of the two prepared paths applies).

### 1.10 Review log (Topic 1)

- **Round 1 (2026-11-08)**, independent reviewer subagent, re-read all cited pages as raw `.md`:
  57 rows checked, 32 OK; findings: 4 HIGH, 12 MEDIUM, 12 LOW (some on §1.8 items, not rows),
  16 coverage gaps. I re-verified the HIGH and
  most MEDIUM findings myself against the downloaded pages before changing anything. All accepted.
  Main changes: hooks fail open by default + `onFailure: "block"` (1.5.2); HIPAA/ZDR are
  Enterprise-only (1.6.7, 1.6.8, 1.8 #2); sandbox does not cover file tools (1.6.2, 1.8 #5);
  `allowedProviders` closes provider bypasses (1.1.15); fail-open cases (1.1.11); non-interactive
  approval caveat (1.1.10); mods key location (1.5.6); `-p` trust risks expanded (1.7.3); plus
  rows 1.1.15–1.1.21, 1.2.8–1.2.9, 1.3.7 from the coverage gaps.
- **Round 2 (2026-11-08)**, same reviewer, re-checked every fix and every new/changed row against
  the raw pages: all round-1 HIGH/MEDIUM FIXED; 0 HIGH, 0 MEDIUM; 4 LOW (wording in 1.1.11, the
  Actions discrepancy in 1.7.8, wording of 1.8 #4, counts in this log). All 4 fixed after round 2.
  **Topic 1 closed.**
- **Owner decisions (2026-11-08)**: the repo owner (the user) decided the PHI and MDM items; recorded
  verbatim in 1.9 and the two items ticked. At the owner's request, 1.11 was added (PHI vs PII
  definitions, Papaya data mapping, model-provider BAA conditions, PHI leak paths for Phase 4).
  1.1–1.8 unchanged.
  - Review round 1 (independent reviewer subagent, eCFR text and Anthropic/AWS/NIST pages):
    0 HIGH, 5 MEDIUM, 8 LOW, 6 coverage gaps. I re-checked the MEDIUM items against the sources;
    all were accepted and fixed. The fixes:
    - Console API key coverage only with ZDR (1.11.3.5).
    - Bedrock claim split into ✅ and ⚠️ parts (1.11.3.7).
    - Alternative BAA routes added (1.11.3.9).
    - ZDR vs Covered Models conflict (1.11.3.10 and a note in 1.9).
    - Leak paths L13–L17 and the outflow note.
    - The LOW items and gaps: 1.11.3.11, quote fixes, the 1.9 item results, the MDM fact kept
      open, and 1.11.2 "Neither".
  - Review round 2 (same reviewer): all 13 round-1 findings FIXED; 0 HIGH, 0 MEDIUM; 5 LOW and
    1 small gap. All fixed:
    - "Claude Console" exclusion vs Console-API-key coverage (1.11.3.11);
    - cross-references corrected;
    - ZDR qualifier (1.11.3.9);
    - "processing" in L13;
    - outflow paragraph wording;
    - federation credentials row (1.11.3.8b).

    **1.11 closed.**

### 1.11 PHI và dữ liệu nhạy cảm: định nghĩa và phạm vi

Accessed 2026-11-08. Sources:

- Regulation text: 45 CFR 160.103, 164.308, 164.314, 164.501, 164.502, 164.504, 164.514. Read on
  eCFR via its official API, as of 2026-11-01 (**local check**: `curl --compressed`, HTTP 200).
- Anthropic: the BAA help article and the [hipaa-setup](https://code.claude.com/docs/en/hipaa-setup)
  page.
- AWS: the HIPAA eligible services reference.
- NIST CSRC glossary.

**Source gap:** the HHS.gov HIPAA pages (Privacy Rule summary, business associates, cloud computing
guidance, de-identification) returned **HTTP 403** to both WebFetch and curl (**local check**). I
could not read them, so every claim below rests on the regulation text that HHS administers. The
HHS links are given for human readers, marked 📖.

#### 1.11.1 Definitions

| # | Finding | Marker | Source |
|---|---|---|---|
| 1.11.1.1 | **Health information** is any information, "oral or recorded in any form or medium", that (1) "is created or received by a health care provider, health plan, public health authority, employer, life insurer, school or university, or health care clearinghouse" and (2) "relates to the past, present, or future physical or mental health or condition of an individual; the provision of health care to an individual; or the past, present, or future **payment** for the provision of health care to an individual." | ✅ | [45 CFR 160.103](https://www.ecfr.gov/current/title-45/section-160.103) |
| 1.11.1.2 | **Individually identifiable health information** is "a subset of health information, **including demographic information** collected from an individual", that is created or received by a provider, health plan, employer or clearinghouse, relates to health, care or payment as above, **and** "(i) that identifies the individual; or (ii) with respect to which there is a reasonable basis to believe the information can be used to identify the individual." | ✅ | [45 CFR 160.103](https://www.ecfr.gov/current/title-45/section-160.103) |
| 1.11.1.3 | **PHI** is "individually identifiable health information" that is transmitted or maintained by electronic media or "in any other form or medium". Four things are excluded: FERPA education records, records described at 20 U.S.C. 1232g(a)(4)(B)(iv), "employment records held by a covered entity in its role as employer", and information about a person "deceased for more than 50 years". **ePHI** is the electronic subset. | ✅ | [45 CFR 160.103](https://www.ecfr.gov/current/title-45/section-160.103); HHS summary 📖 [Privacy Rule summary](https://www.hhs.gov/hipaa/for-professionals/privacy/laws-regulations/index.html) (403, not read) |
| 1.11.1.4 | **Covered entity** means "(1) A health plan. (2) A health care clearinghouse. (3) A health care provider who transmits any health information in electronic form in connection with a transaction covered by this subchapter." A health plan includes "a health insurance issuer". | ✅ | [45 CFR 160.103](https://www.ecfr.gov/current/title-45/section-160.103); 📖 [HHS covered entities](https://www.hhs.gov/hipaa/for-professionals/covered-entities/index.html) (403) |
| 1.11.1.5 | A **business associate** is a person who, on behalf of a covered entity, "creates, receives, maintains, or transmits protected health information" for a regulated function, "**including claims processing or administration, data analysis, processing or administration** … billing, benefit management". The term also covers "a subcontractor that creates, receives, maintains, or transmits protected health information on behalf of the business associate." | ✅ | [45 CFR 160.103](https://www.ecfr.gov/current/title-45/section-160.103) |
| 1.11.1.6 | **Payment** includes "adjudication or subrogation of health benefit claims", "billing, claims management, collection activities … and related health care data processing", and "review of health care services with respect to medical necessity, coverage under a health plan". | ✅ | [45 CFR 164.501](https://www.ecfr.gov/current/title-45/section-164.501) |
| 1.11.1.7 | **De-identified** information is not individually identifiable, so it is not PHI. Under the safe-harbor method it counts as de-identified only if 18 identifier types are removed, including names, address parts smaller than a state, dates other than the year, phone and email, "(G) Social security numbers", "(H) Medical record numbers", "(I) Health plan beneficiary numbers", "(J) Account numbers", "(K) Certificate/license numbers", URLs, **IP addresses**, full-face photos, and "(R) Any other unique identifying number, characteristic, or code". The covered entity must also have no "actual knowledge" that the rest could identify the person. (The other method is an expert determination; not read in detail.) | ✅ | [45 CFR 164.514(a)–(b)](https://www.ecfr.gov/current/title-45/section-164.514); 📖 [HHS de-identification guidance](https://www.hhs.gov/hipaa/for-professionals/special-topics/de-identification/index.html) (403) |
| 1.11.1.8 | **Minimum necessary:** when using or disclosing PHI, a covered entity or business associate "must make reasonable efforts to limit protected health information to the minimum necessary to accomplish the intended purpose". | ✅ | [45 CFR 164.502(b)](https://www.ecfr.gov/current/title-45/section-164.502) |
| 1.11.1.9 | **PII** is not a HIPAA term: the seven HIPAA sections downloaded contain no occurrence of "personally identifiable" (**local check**: `grep -c -i`, 0 in each). The US federal definition (OMB Circular A-130, used in NIST SP 800-53 Rev. 5) is "information that can be used to distinguish or trace an individual's identity, either alone or when combined with other information that is linked or linkable to a specific individual". NIST SP 800-122 lists medical, educational, financial and employment information as examples of linked information. | ✅ | [NIST CSRC glossary: PII](https://csrc.nist.gov/glossary/term/personally_identifiable_information) |
| 1.11.1.10 | **PHI vs PII (inference from 1.11.1.1–1.11.1.9):** PII is defined by **identifiability alone**. PHI needs **three things together**: identifiable, about health, care or payment for care, and created or received by "a health care provider, health plan, employer, or health care clearinghouse" (the IIHI list). It is regulated when held by a covered entity, or by a business associate on its behalf. Note that "health information" also lists a "life insurer", but IIHI does not. So most PHI is PII, but most PII is not PHI. An identifier such as an ID number or a bank account number becomes part of PHI when it sits in the same record as health or claim information held for a covered entity. | ⚠️ inference (no source states this comparison; derived from the definitions above) | — |
| 1.11.1.11 | **Does HIPAA apply to Papaya at all?** HIPAA's definitions refer to US law: a "health insurance issuer" must be "licensed to engage in the business of insurance in a **State**". Papaya serves insurers "across SEA and Asia" (`work/00-challenge.md`). Whether any Papaya tenant is a HIPAA covered entity, and so whether Papaya is a business associate, is a **legal question I cannot answer**. Two text points matter for that question. First, IIHI does not list a life insurer (1.11.1.10). Second, "health plan" excludes "excepted benefits" (160.103, Health plan (2)(i)). Both are relevant if a partner is a life insurer or the data comes from Underwriting. This file follows the brief, which lists HIPAA as a compliance requirement, and treats Papaya as a business associate of its insurer clients: claims processing on their behalf matches 1.11.1.5. | ✅ (definition text) / ⚠️ (applicability: needs Papaya legal) | [45 CFR 160.103](https://www.ecfr.gov/current/title-45/section-160.103) |
| 1.11.1.12 | **Regional law**: the brief says insurer partners are "across SEA and Asia", so several countries' laws may apply. Vietnam is only an example, because the owner and the framing use "CCCD". For Vietnam, I could not find and read an official government source this session for how local law classifies health data, national ID and bank data. Secondary sources (law-firm and advisory sites) say Vietnam's Personal Data Protection Law (No. 91/2025/QH15) took effect on 2026-01-01, with Decree 356/2025/NĐ-CP replacing Decree 13/2023/NĐ-CP, and that health data and some financial data are "sensitive personal data". **Not verified. Do not use it in `docs/` until it is read in the official text** (Topic 5). | ⚠️ (secondary sources only) | e.g. [EY legal alert, Decree 356/2025](https://www.ey.com/vi_vn/technical/tax/tax-and-law-updates/nghi-dinh-so-356-2025-nd-cp-quy-dinh-chi-tiet-mot-so-dieu-va-bien-phap-thi-hanh-luat-bao-ve-du-lieu-ca-nhan) (not official) |

#### 1.11.2 Which group each Papaya data type falls into

This applies 1.11.1 to the data the brief names. The legal text is ✅; **applying it to Papaya is
my inference (⚠️)**, because I have not seen Papaya's schemas or contracts. It assumes the HIPAA
framing of 1.11.1.11.

| Data (code from `work/01-problem-framing.md`) | Group | Why (rule) |
|---|---|---|
| Medical records, medical documents (MED) | **PHI** | Relates to "physical or mental health or condition" and identifies the member (1.11.1.1–1.11.1.3) |
| Diagnoses (MED) | **PHI** | Same rule as medical records |
| Claim history (MED) | **PHI**, even without a diagnosis | Claims are "payment for the provision of health care" (1.11.1.1, 1.11.1.6) |
| National ID / CCCD (NID) | **PII** on its own. **Part of PHI** when it is in a member or claim record | An identifying number. Safe harbor lists "(R) any other unique identifying number" (1.11.1.7); "(G) SSN" is the US equivalent |
| Bank account (BANK) | **PII** (financial) on its own. **Part of PHI** when it is the payout account of a claim | "(J) Account numbers" is a listed identifier (1.11.1.7), and claim payout is payment for care (1.11.1.6) |
| Policy and member numbers | **Part of PHI** in claim context | "(I) Health plan beneficiary numbers" (1.11.1.7) |
| Same data, de-identified by safe harbor | **Not PHI** | 1.11.1.7. Under local law it may still be personal data (1.11.1.12, ⚠️) |
| Infrastructure metadata (resource names, metrics, config without customer values) | **Neither** | Provided it is not linked to health or claim information. The 18 identifiers are a de-identification test for health information, not a test for non-health data, so an IP address alone in an infra log is not PHI. **Deliberate safety margin:** treat IP addresses, URLs containing claim or member IDs, and object keys that contain names or ID numbers as PHI when they can be linked to a claim (1.11.1.7) |

**Practical consequence (inference ⚠️):**
- Claim records combine MED with NID and BANK, so any production store or stream that carries claim
  data should be treated as PHI-bearing as a whole: Aurora claim tables, the claim-documents S3
  bucket, and the queues and logs of claim services.
- Separating PII from PHI field by field is not a safe basis for agent access.

#### 1.11.3 Conditions for a model provider (or any vendor) to process PHI

| # | Finding | Marker | Source |
|---|---|---|---|
| 1.11.3.1 | A covered entity may let a business associate "create, receive, maintain, or transmit" PHI only after it "obtains satisfactory assurance that the business associate will appropriately safeguard the information". A business associate may do the same with a **subcontractor**, after it obtains the same assurances. The assurances "must be documented through a written contract or other written agreement or arrangement" (the BAA). The Security Rule has the same requirement for ePHI. | ✅ | [45 CFR 164.502(e)](https://www.ecfr.gov/current/title-45/section-164.502), [164.308(b)](https://www.ecfr.gov/current/title-45/section-164.308), [164.314(a)](https://www.ecfr.gov/current/title-45/section-164.314) |
| 1.11.3.2 | Required BAA content includes these duties. The vendor must: not use or disclose PHI beyond the contract; "use appropriate safeguards and comply, where applicable, with subpart C" (Security Rule); report any use or disclosure not provided for, including breaches, and (Security Rule) "any security incident of which it becomes aware"; flow the same terms down to its subcontractors; and return or destroy PHI at termination "if feasible". | ✅ | [45 CFR 164.504(e)(2)](https://www.ecfr.gov/current/title-45/section-164.504), [164.314(a)(2)](https://www.ecfr.gov/current/title-45/section-164.314) |
| 1.11.3.3 | **Application to Papaya (inference):** if Papaya is a business associate of its insurers (1.11.1.11), any model provider that receives PHI from a Papaya agent is Papaya's **subcontractor**. Papaya then needs a BAA with that provider, and must also check that its own BAAs with insurers allow the subcontracting. | ⚠️ inference from 1.11.3.1 | — |
| 1.11.3.4 | **Anthropic BAA scope:** it covers "HIPAA-ready services, such as use of our first-party API, Claude in Microsoft Foundry, or Enterprise plans". "Standard Claude Enterprise plans do not include BAA coverage without action from a Primary Owner." The authoritative list of Eligible Services is the Implementation Guide on the Anthropic Trust Center (not opened). **The Team plan is not mentioned**, so treat Team as not covered (⚠️, confirm with Anthropic). | ✅ (article) / ⚠️ (Team) | [Anthropic: BAA for commercial customers](https://privacy.claude.com/en/articles/8114513-business-associate-agreements-baa-for-commercial-customers) (page shows "Updated over a week ago", no date) |
| 1.11.3.5 | **Claude Code under the Anthropic BAA:** terminal and Code tab (local mode) are covered **with the HIPAA configuration** only "when members sign in with their Claude Enterprise account and Claude Code connects directly to Anthropic". With a Console API key, Claude Code is covered only "when the Claude Console organization has zero data retention (ZDR) enabled", and then it is "Covered through ZDR, not through the HIPAA configuration". **Without ZDR, an API-key session is not covered.** hipaa-setup adds that these sessions "belong to a Claude Console organization, which has its own agreement and settings". This matters for CI agents on API keys (1.7.6). The VS Code and JetBrains extensions are **not** covered. Claude Code through Bedrock, Google Cloud's Agent Platform, Foundry, Claude Platform on AWS or a Claude apps gateway is **not eligible** for the HIPAA configuration. Claude Code **cloud sessions** (web, Desktop, `claude --cloud`) are "Not covered under BAA". For connectors: "Your BAA doesn't cover any of them, even after an Owner turns them on". Local MCP servers, skills and plugins are also not covered. | ✅ | [Anthropic BAA article](https://privacy.claude.com/en/articles/8114513-business-associate-agreements-baa-for-commercial-customers), [hipaa-setup](https://code.claude.com/docs/en/hipaa-setup) |
| 1.11.3.6 | The HIPAA configuration "doesn't remove cloud provider or GitHub credentials". Data an agent sends to GitHub or another service is **not covered** by the Anthropic BAA. | ✅ | [hipaa-setup](https://code.claude.com/docs/en/hipaa-setup) |
| 1.11.3.7 | **AWS:** Amazon Bedrock, CloudWatch Logs, S3, Aurora and Lambda are on the HIPAA eligible services list. ECS, EC2, SNS, SQS and Step Functions are listed too. PHI may be used in them only after "entering into an AWS business associate agreement" (page last updated 2026-10-15). The page adds that customers "still must configure these services consistent with HIPAA requirements". ✅: the **Anthropic** BAA does **not** cover Claude Code through Bedrock (1.11.3.5). ⚠️ not verified: whether an AWS BAA covers the whole data flow of a Claude Code session that uses Bedrock. Also unknown whether Papaya has an AWS BAA. | ✅ (list, Anthropic exclusion) / ⚠️ (AWS coverage of Claude Code, Papaya status) | [AWS HIPAA eligible services reference](https://aws.amazon.com/compliance/hipaa-eligible-services-reference/) |
| 1.11.3.8 | **GCP (Vertex AI, Gemini):** not researched this session. | ⚠️ | — (Topic 5) |
| 1.11.3.8b | **CI with Anthropic workload identity federation (1.7.6):** hipaa-setup lists "A Claude Console API key or federation credentials" as **not eligible** for the HIPAA configuration ("These sessions belong to a Claude Console organization, which has its own agreement and settings"). The BAA article does not say whether federation sessions are covered through ZDR (⚠️). Under the owner decision, CI agents do not touch PHI, so this blocks nothing. | ✅ (hipaa-setup) / ⚠️ (ZDR coverage) | [hipaa-setup](https://code.claude.com/docs/en/hipaa-setup) |
| 1.11.3.9 | **Relation to the owner decision (inference):** under the owner's default, PHI never reaches the agent, so none of 1.11.3.3–1.11.3.7 is needed for the DevSecOps agent. `work/01-problem-framing.md` GĐ-9 allows case-by-case approved reads of real data with "BAA/DPA". If such a read could include PHI sent to Claude, it needs a covered route. Per 1.11.3.4–1.11.3.7 the routes are: (a) Enterprise + HIPAA configuration, with direct connection to Anthropic; (b) a first-party API / Console org with a BAA, where Claude Code is covered only through ZDR (1.11.3.5), and Covered Models are unavailable under ZDR unless Anthropic authorizes it (1.11.3.10); (c) Bedrock + an AWS BAA (⚠️ unverified for Claude Code). The current **Team** plan is not mentioned in the BAA article, so it is not confirmed as covered (⚠️, ask Anthropic). The owner decision names (a) as a separate environment. GĐ-9 and its consequences should be checked against this when the design is written. | ⚠️ inference | — |
| 1.11.3.10 | **ZDR vs Covered Models:** "Covered Models require 30-day data retention and aren't available with zero data retention (ZDR) enabled", unless "Anthropic has expressly authorized it for your organization". | ✅ | [Anthropic BAA article](https://privacy.claude.com/en/articles/8114513-business-associate-agreements-baa-for-commercial-customers) |
| 1.11.3.11 | **BAA scope limits:** "the BAA only covers the single organization that accepted it". The article says the BAA "excludes features such as Claude Console, Cowork in the cloud, or features currently in beta". The same article lists Console-API-key sessions with ZDR as covered (1.11.3.5). So the two statements look contradictory within the source. My reading is that "Claude Console" here means the Console product UI, not API use under ZDR; ⚠️ confirm with Anthropic. API features not covered: Batch API, Files API, Skills API, Code Execution, Web Fetch. This supports the owner's "separate environment": a BAA org is its own boundary. The client-side controls it would need: `requiredMinimumVersion` (1.1.13), `allowedProviders` (1.1.15), and `forceLoginOrgUUID`. hipaa-setup says that with `forceLoginOrgUUID` set, Claude Code "refuses sessions that authenticate with `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, or `apiKeyHelper`", but it "checks only claude.ai sign-ins". | ✅ (quotes) / ⚠️ (reading of "Claude Console") | [Anthropic BAA article](https://privacy.claude.com/en/articles/8114513-business-associate-agreements-baa-for-commercial-customers), [hipaa-setup](https://code.claude.com/docs/en/hipaa-setup) |

#### 1.11.4 Paths by which PHI can reach a DevSecOps agent's context (to handle in Phase 4)

**This is my analysis, not quoted from any document.** It lists paths to close or control, so that
"PHI never reaches the agent" holds. "Context" includes anything the agent reads: tool output, files,
fetched pages, MCP results, images. Anything in context is sent to the model provider and saved in
the local session transcript (`~/.claude*/projects/…/*.jsonl`, **local check** on this machine).
Controls are only candidates; they are designed in Phase 4.

| # | Path | How it gets into context | Why PHI is likely | Candidate controls (Phase 4) |
|---|---|---|---|---|
| L1 | **Prod logs:** CloudWatch Logs from Lambda and ECS, k0s pod logs, GCP Cloud Logging | Agent runs `aws logs`, `kubectl logs`, or reads a log MCP during debug or incident | Request payloads, exception messages with record values, document-extraction output; IPs and URLs become PHI when linked to a claim | Log redaction at source; agent role reads metrics and redacted log groups only; separate log group for raw payloads with no agent access |
| L2 | **Database queries:** Aurora prod or replicas | `psql` or a DB MCP; `SELECT *` while debugging; error messages and slow-query or `pg_stat_statements` text with literals | Claim tables hold MED + NID + BANK | No DB credentials for the agent; a schema-only or masked view role; reads of real data only through the GĐ-9 exception |
| L3 | **S3:** claim documents, exports, backups | `aws s3 cp/ls`; reading a file to "check format" | Medical documents and ID scans; **object keys** may contain names or ID numbers | Deny `s3:GetObject` on PHI buckets for agent roles; consider whether `ListBucket` exposes keys |
| L4 | **Message and workflow payloads:** SQS/DLQ, SNS, Step Functions execution history | Inspecting a DLQ or execution input/output during an incident | Payloads carry claim data; Step Functions stores input/output in history | Same as L3 for `sqs:ReceiveMessage` and `states:GetExecutionHistory`; payloads carry references, not data |
| L5 | **Tickets and chat:** Linear, Slack (incl. via MCP connectors) | Agent reads an issue or thread linked from a task | Support escalations paste claim details and screenshots | Ticket hygiene rule (no PHI in tickets); scope or deny those MCP connectors; redaction bot |
| L6 | **Partner and member uploaded documents** while debugging prod AI agents (A7b in problem framing) | Engineer gives the agent a failing document to reproduce a bug | The document **is** PHI, and is also an injection vector | Reproduce with synthetic documents; a de-identification step before any document reaches the coding agent |
| L7 | **Non-prod data that is not synthetic** | Agent works freely in dev/staging (GĐ-14) | If a prod copy or dump exists in staging, PHI is there | Enforce GĐ-14: no prod → non-prod copies; scan non-prod stores |
| L8 | **Repo content:** fixtures, seed files, sample documents, notebooks committed from real data | Agent reads the repo (always) | Engineers copy "a real example" into tests | Secret/PII scanning in CI and pre-commit; review rule for fixtures |
| L9 | **CI output:** GitHub Actions logs and artifacts from jobs that touch real data | Agent reads CI logs to fix a failing job | Test or migration output that prints rows | No real data in CI; log masking |
| L10 | **What humans paste:** text, screenshots or files pasted into the chat by the engineer | Direct input | Copying from an admin console or a customer email | Training and a clear rule; a `UserPromptSubmit` hook pattern check (weak, advisory) |
| L11 | **Prod shell access:** `kubectl exec`, ECS Exec, SSM on EC2 | Agent runs commands inside a prod workload | Env vars, mounted files and local caches hold data or DB credentials | No exec rights for agent roles in prod |
| L12 | **Fetched web content:** internal dashboards and admin UIs reachable from the laptop | WebFetch or browser tools | Admin pages show member records | Network or domain allowlist; deny fetch to internal admin hosts |
| L13 | **GCP data stores** that feed Vertex AI / Gemini: GCS buckets, datasets, Vertex request/response logging | `gcloud`/`gsutil` or a GCP MCP while debugging the AI pipeline | Medical documents are sent to GCP for processing (A4/A13 in problem framing) | Same model as L3 on the GCP side: no data-plane read for agent identities; GCP BAA status ⚠️ (1.11.3.8) |
| L14 | **Prod AI agent traces:** prompt/response logs, traces and evaluation sets of claim assessment, extraction and FWA agents (OpenAI, Vertex, Claude) | Agent reads traces to debug a model or prompt regression | Prompts and outputs contain the claim and document content | Traces stored as PHI with restricted access; debug with redacted or synthetic traces |
| L15 | **Secondary copies on AWS:** CloudTrail data events, S3 access logs, Athena or CloudWatch Logs Insights results, Aurora snapshots and exports | Queries run for audit or incident analysis; restoring a snapshot to inspect it | Data events and query results can include object keys and record values; AWS MCP Server events copy tool output (2.5.5); snapshots are full copies | Treat these stores as PHI-bearing; no snapshot restore or export rights for agent roles |
| L16 | **Lambda payload replay:** test events, `aws lambda invoke`, replaying a failed event | Agent copies a real event to reproduce a bug | The event is the real claim payload | Replay only with synthetic or redacted events; no `lambda:InvokeFunction` on prod for agent roles |
| L17 | **Automated alerts in Slack** that embed raw log lines or payloads | Agent reads an alert channel or thread via MCP | Alert bots paste the failing record | Alerts carry IDs and links, not payloads (ties to P6) |

**Where PHI goes next once it is in context (analysis).** The agent can write it to places that
last longer than the session:
- auto-memory and `CLAUDE.md` files: local, the organization's responsibility, and they can end up
  committed to git;
- commits, PR descriptions and code comments;
- Linear comments and Slack messages;
- CI logs.

GitHub, Linear, Slack and CI are third parties, outside the Anthropic BAA.

hipaa-setup says of data sent to GitHub or other services: "Your BAA with Anthropic doesn't cover
the data it sends there" (1.11.3.6). So a leak into context is not only a model-provider issue; it
can turn into a persistent copy. Phase 4 should cover these outflows as well as the inflows above.

Cross-cutting point (inference): every path above depends on **what the agent's identity is allowed
to read**. So the strongest single control for the owner decision is an agent identity with **no
data-plane read on PHI stores**: IAM, DB roles and k0s RBAC (Topics 2–3). Redaction and rules on
the Claude Code side are the second layer, consistent with 1.8 #1.

---

## Topic 2 — AWS: identity, guardrails, temporary access, audit

Accessed 2026-11-08. All AWS pages below were downloaded in full as the raw Markdown that
docs.aws.amazon.com serves (`<page>.md`, HTTP 200, **local check**) and read from those copies.
Links point to the `.html` version of the same page.

Prefixes used in the Source column:
- IC = `https://docs.aws.amazon.com/singlesignon/latest/userguide/`
- ORG = `https://docs.aws.amazon.com/organizations/latest/userguide/`
- IAM = `https://docs.aws.amazon.com/IAM/latest/UserGuide/`
- CT = `https://docs.aws.amazon.com/awscloudtrail/latest/userguide/`

Context from `work/01-problem-framing.md`:
- GĐ-2: prod and non-prod are separate accounts in AWS Organizations, and sign-in goes through IAM
  Identity Center.
- GĐ-8: every prod change is approved before it is applied, including during incidents.
- GĐ-9: by default the agent reads no real data in prod.

### 2.1 IAM Identity Center and permission sets

| # | Finding | Marker | Source |
|---|---|---|---|
| 2.1.1 | A permission set "is a template that you create and maintain that defines a collection of one or more IAM policies". When it is assigned, Identity Center "creates corresponding IAM Identity Center-controlled IAM roles in each account" and keeps them updated when the permission set changes. | ✅ | [IC permissionsetsconcept](https://docs.aws.amazon.com/singlesignon/latest/userguide/permissionsetsconcept.html) |
| 2.1.2 | A permission set can contain AWS managed policies, customer managed policies, inline policies and job-function policies, plus an AWS managed or customer managed policy as a **permissions boundary**. A customer managed policy must already exist "with the same name and path in each AWS account" where the permission set is assigned. | ✅ | [IC permissionsetcustom](https://docs.aws.amazon.com/singlesignon/latest/userguide/permissionsetcustom.html) |
| 2.1.3 | The provisioned role is named `AWSReservedSSO_<permission-set-name>_<unique-suffix>`, under path `aws-reserved/sso.amazonaws.com/…`. If all assignments in an account are deleted, the role is deleted. A new assignment creates a role **with a different suffix**, which breaks policies that reference the old ARN (KMS key policies and the EKS `aws-auth` ConfigMap are the examples given). | ✅ | [IC referencingpermissionsets](https://docs.aws.amazon.com/singlesignon/latest/userguide/referencingpermissionsets.html) |
| 2.1.4 | **Permission-set session duration** (the role session in the account): default 1 hour, minimum 1 hour, maximum 12 hours. "By default, IAM roles generated by IAM Identity Center for permission sets can only be assumed by IAM Identity Center users." | ✅ | [IC howtosessionduration](https://docs.aws.amazon.com/singlesignon/latest/userguide/howtosessionduration.html) |
| 2.1.5 | **Access portal session** ("user interactive session"): default 8 hours, configurable from 15 minutes to 90 days. "Changes to session duration apply only to new sessions." With an external IdP, the duration is the shorter of this setting and the SAML `SessionNotOnOrAfter`, if the IdP sends it. Two qualifiers:<br>- "If the session duration of your IdP is longer than the one set in IAM Identity Center, your users can start a new IAM Identity Center session without re-entering their credentials." So this setting alone does not force a re-login.<br>- With AWS Managed Microsoft AD, the session is capped at 10 hours (Kerberos ticket lifetime). | ✅ | [IC user-interactive-sessions](https://docs.aws.amazon.com/singlesignon/latest/userguide/user-interactive-sessions.html), [IC user-session-duration-prereqs-considerations](https://docs.aws.amazon.com/singlesignon/latest/userguide/user-session-duration-prereqs-considerations.html) |
| 2.1.6 | The two durations stack: "if you refresh your permission set just before the IAM Identity Center session is set to expire and the session duration is set to 20 hours while the permission set duration is set to 12 hours, the AWS CLI session runs for the maximum of 20 hours plus 12 hours for a total of 32 hours." | ✅ | [IC user-session-duration-prereqs-considerations](https://docs.aws.amazon.com/singlesignon/latest/userguide/user-session-duration-prereqs-considerations.html) |
| 2.1.7 | **MFA:** if an external IdP is the identity source, the MFA settings section is unavailable: "Your external IdP manages MFA settings". The IAM key `aws:MultiFactorAuthPresent` "is not present for federated identities". The IAM condition-keys page adds that, to enforce MFA for Identity Center identities, "you can enable attributes for access control to pass a SAML assertion claim with the authentication method from your identity provider". This applies when an external SAML IdP is used. | ✅ | [IC mfa-getting-started](https://docs.aws.amazon.com/singlesignon/latest/userguide/mfa-getting-started.html), [IAM condition keys: aws:MultiFactorAuthPresent](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html#condition-keys-multifactorauthpresent) |
| 2.1.8 | **Attributes for access control (ABAC):** user attributes from the Identity Center directory, or from SAML assertions as `https://aws.amazon.com/SAML/Attributes/AccessControl:{TagKey}`, become session tags that policies can test. If both sources set the same attribute, the directory mapping wins. | ✅ | [IC attributesforaccesscontrol](https://docs.aws.amazon.com/singlesignon/latest/userguide/attributesforaccesscontrol.html) |
| 2.1.9 | **Delegated administration:** most Identity Center admin tasks can move to a member account. "A permission set used for access to the management account can only be modified by an IAM Identity Center administrator from the management account." The docs recommend assigning **users, not groups**, to management-account permission sets. | ✅ | [IC delegated-admin](https://docs.aws.amazon.com/singlesignon/latest/userguide/delegated-admin.html) |
| 2.1.10 | **Account access manager** (in IAM): assigns **existing IAM roles** to Identity Center users and groups. It offers what permission sets do not: custom trust policies, role tags, session tags, role paths, and "IdP-asserted claims as trust policy conditions". CLI access is through `aws login`, and it has its own API namespace, `account-access`. The page does not describe source identity or limits. | ✅ (what the page says) / ⚠️ (details not on the page) | [IAM account-access-manager](https://docs.aws.amazon.com/IAM/latest/UserGuide/account-access-manager.html) |
| 2.1.11 | The docs recommend an **emergency access** configuration: direct SAML federation from the IdP to IAM roles in each account. It is for use when Identity Center is disrupted, and should be built and tested **before** it is needed. | ✅ | [IC emergency-access](https://docs.aws.amazon.com/singlesignon/latest/userguide/emergency-access.html) |

### 2.2 Credentials on the engineer's laptop (where the agent runs)

| # | Finding | Marker | Source |
|---|---|---|---|
| 2.2.1 | `aws configure sso` / `aws sso login`: from AWS CLI 2.22.0 the default is PKCE, which needs a browser on the same device; `--use-device-code` selects device authorization. With the recommended `[sso-session]` configuration, "The authentication token is cached to disk under the `sso/cache` directory with a filename based on the session name". The legacy configuration uses `~/.aws/sso/cache`, keyed by `sso_start_url`. The roles are chosen per profile, and the `[sso-session]` section carries `sso_registration_scopes = sso:account:access`. "As long as you are signed in to IAM Identity Center and those cached credentials are not expired, the AWS CLI automatically renews expired AWS credentials when needed." | ✅ | [AWS CLI: cli-configure-sso](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html) |
| 2.2.2 | **Inference backed by docs:** any process running as the engineer's OS user can use that cache, and that includes a Claude Code Bash command. For the length of the portal session (2.1.5) it gets fresh role credentials without a human step. One portal session reaches **every** account and role assigned to the user, not only the profile in use. The docs support this in three places: the revocation Deny "blocks the user's actions even if they use their active AWS access portal session to navigate to different accounts and assume different roles"; a disabled user with a live portal session "can continue to assume new roles until you remove their access"; and the CLI wizard lists all roles ("There are 2 roles available to you."). Only one detail is still to test: that profiles sharing one `sso-session` reuse the single cached token. | ✅ (quotes) / ⚠️ (token reuse detail) | [IC prereqs-revoking-user-permissions](https://docs.aws.amazon.com/singlesignon/latest/userguide/prereqs-revoking-user-permissions.html), [IC revoke-user-permissions](https://docs.aws.amazon.com/singlesignon/latest/userguide/revoke-user-permissions.html), [AWS CLI: cli-configure-sso](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html) |
| 2.2.3 | **Application ID** (`sdk_ua_app_id` / `AWS_SDK_UA_APP_ID`) is a free-form string of up to 50 characters, set by the client, that identifies "which source application made a set of calls". The page does not say where it appears (for example in CloudTrail `userAgent`). It is **set by the client**, so it is a hint, not evidence. | ✅ (page) / ⚠️ (CloudTrail visibility) | [SDK reference: feature-appid](https://docs.aws.amazon.com/sdkref/latest/guide/feature-appid.html) |
| 2.2.4 | **AWS MCP Server** (Agent Toolkit for AWS) is "a managed remote MCP server". AWS recommends it over the older local `aws-api-mcp-server` / `aws-knowledge-mcp-server`. There are two auth options: **OAuth** (browser sign-in via AWS Sign-In), and **SigV4** through the local "MCP Proxy for AWS" using AWS CLI credentials. The docs recommend SigV4 ("Use this option if you use terminal or IDE-based coding agents (such as Claude Code, Kiro, and Codex)"), but they also list "Claude Code CLI" as an OAuth client. "Multi-profile switching for cross-account workflows is not supported with OAuth." Read-only mode ("hide write-capable tools from the agent entirely") is available with SigV4. **Inference (⚠️):** read-only mode is a setting of the local proxy, so the agent could change it; it is not a control. API tools include `aws___run_script`, which "execute[s] Python code in a sandboxed environment with AWS API access". | ✅ | [Agent Toolkit: getting-started-aws-mcp-server](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/getting-started-aws-mcp-server.html), [understanding-mcp-server-tools](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/understanding-mcp-server-tools.html) |
| 2.2.5 | **Server-set context keys for agent traffic:**<br>- How it works: the AWS MCP Server "does not define its own IAM actions". It authenticates the request with the caller's credentials, adds `aws:ViaAWSMCPService` (Boolean, `true` for any request through an AWS managed MCP server) and `aws:CalledViaAWSMCP` (e.g. `aws-mcp.amazonaws.com`, `eks-mcp.amazonaws.com`, `ecs-mcp.amazonaws.com`), and forwards the request. The target service then authorizes it with the caller's own policies.<br>- Where the keys work: in IAM policies **and SCPs**. Documented examples: "Deny all actions through any AWS managed MCP server", and "Deny destructive actions through AWS MCP Server".<br>- On direct calls, the IAM condition-keys page says `aws:CalledViaAWSMCP` is "not present when the principal makes the call directly". For `aws:ViaAWSMCPService`, the same page says it "returns `false` when the principal makes the call directly", yet its Availability line says it "is included in the request context when an AWS MCP server makes a request". A policy must handle both cases, for example with `BoolIfExists` or `Null` (⚠️ untested).<br>- OAuth sessions also carry `aws:SignInSessionArn` (2.5.5). | ✅ | [Agent Toolkit: security_iam_service-with-iam](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/security_iam_service-with-iam.html), [security_iam_id-based-policy-examples](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/security_iam_id-based-policy-examples.html), [IAM condition keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html) |

### 2.3 AWS Organizations: SCPs and RCPs

| # | Finding | Marker | Source |
|---|---|---|---|
| 2.3.1 | SCPs set "the maximum available permissions for the IAM users and IAM roles in your organization"; they grant nothing. They require "all features" enabled. | ✅ | [ORG orgs_manage_policies_scps](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html) |
| 2.3.2 | **What SCPs do not restrict** (from the list "Tasks and entities not restricted by SCPs"): "Any action performed by the management account"; "Any action performed using permissions that are attached to a service-linked role". Separately, the page says "SCPs don't affect resource-based policies directly" and do not apply to principals outside the organization. So a bucket policy that grants access to an outside account is not limited by an SCP (my paraphrase of that sentence). SCPs **do** restrict the member account's root user and apply to delegated-admin member accounts. | ✅ | [ORG orgs_manage_policies_scps](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html) |
| 2.3.3 | When a permissions boundary and an SCP are both present, "the boundary, the SCP, and the identity-based policy must all allow the action". | ✅ | [ORG orgs_manage_policies_scps](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html) |
| 2.3.4 | **Limits (hard):** maximum SCP size **10,240 characters**, maximum RCP size 5,120. At most **10 SCPs** attached directly to the root, to an OU or to an account, and at least 1. At most 5 RCPs. "All policy limits are hard limits." The count is per attachment point and covers only direct attachments: "Policies that affect an OU or account by inheritance do not count against these limits." | ✅ | [ORG orgs_reference_limits](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_reference_limits.html) |
| 2.3.4b | **SCP evaluation:**<br>- "Any account has only those permissions permitted by every parent above it."<br>- "For a service to be accessible, there must be an explicit allow at every level from the root down to the account."<br>- "A Deny-only SCP at the root therefore blocks every service unless an explicit Allow covers it."<br>- So the usual pattern is deny-list SCPs layered on the default `FullAWSAccess` (inference from the limits page: it occupies one of the 10 direct-attachment slots until it is replaced), or explicit allow-lists. A Deny at any level wins. | ✅ | [ORG orgs_manage_policies_scps_evaluation](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps_evaluation.html), [ORG orgs_manage_policies_scps](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html) |
| 2.3.5 | AWS "strongly recommends" testing SCPs before attaching them to the root, for example by moving accounts into a test OU one at a time. Disabling the SCP policy type detaches every SCP, and the attachments "aren't automatically recoverable". | ✅ | [ORG orgs_manage_policies_scps](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html) |
| 2.3.6 | **RCPs** cap what is allowed **on resources** in member accounts, mainly against principals outside the organization ("Use an RCP when you need to restrict IAM principals that are external to your organization"). Supported services include `s3`, `sqs`, `kms`, `secretsmanager`, `logs`, `sts`, `dynamodb`, `ecr`, `codebuild`. **Not in the list:** RDS/Aurora, Lambda, SNS, Step Functions, ECS, EC2. RCPs do not apply to the management account, service-linked roles, or AWS managed KMS keys. | ✅ | [ORG orgs_manage_policies_rcps](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_rcps.html) |
| 2.3.7 | **Management account:** AWS recommends limiting who can access it, keeping workloads and data out of it ("SCPs do not apply to the management account"), and delegating administration to member accounts. | ✅ | [ORG orgs_best-practices_mgmt-acct](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_best-practices_mgmt-acct.html) |
| 2.3.8 | Condition keys that exist and are useful in SCPs (each confirmed present in the global keys page): `aws:PrincipalArn`, `aws:PrincipalTag/*`, `aws:PrincipalOrgID`, `aws:ResourceOrgID`, `aws:SourceIdentity`, `aws:CalledVia`, `aws:ViaAWSService`, `aws:RequestedRegion`, `aws:SourceIp`, `aws:SourceVpce`, `aws:TokenIssueTime`, `identitystore:UserId`. Semantics are per key and must be checked when a policy is written. Example: `aws:CalledVia` is absent when a service acts through a service role. | ✅ (keys exist) | [IAM reference_policies_condition-keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html) |

### 2.4 Temporary (just-in-time) access and revocation

| # | Finding | Marker | Source |
|---|---|---|---|
| 2.4.1 | AWS describes temporary elevated access as a way "to request, approve, and track the use of a permission to perform a specific task during a specified time". For it, Identity Center "integrates with the solutions from AWS Security Competency partners": **Apono, CyberArk Secure Cloud Access, Okta Access Requests, Tenable**. The page describes **no native AWS request/approve feature**, and it does not mention any AWS-built or sample solution. | ✅ | [IC temporary-elevated-access](https://docs.aws.amazon.com/singlesignon/latest/userguide/temporary-elevated-access.html) |
| 2.4.1b | **TEAM** (Temporary Elevated Access Management) is an open-source **sample** described on the AWS Security Blog (2023-06-08), not a supported AWS service. After approval, its workflow "creates a temporary account assignment", and when access ends it "automatically deletes the temporary account assignment". The approval records live in the TEAM application. The blog states: "Each CloudTrail event contains the unique identifier of the user who performed the action". This is a blog, not the user guide, so it is 📖-strength for that claim. | ✅ (blog read) | [AWS Security Blog: Temporary elevated access management with IAM Identity Center](https://aws.amazon.com/blogs/security/temporary-elevated-access-management-with-iam-identity-center/) |
| 2.4.2 | Assignments are API objects: `CreateAccountAssignment` and `DeleteAccountAssignment` exist and are logged in CloudTrail (`sso.amazonaws.com`). **Inference:** a home-built JIT flow can create an assignment after approval and delete it when time is up, but this only stops **new** role sessions (2.4.4). | ✅ (APIs) / ⚠️ (design) | [IC sso-info-in-cloudtrail](https://docs.aws.amazon.com/singlesignon/latest/userguide/sso-info-in-cloudtrail.html) |
| 2.4.3 | Ending a user's portal session: "Ending an active session for an IAM Identity Center user **doesn't end any active IAM role sessions** in the AWS Management Console or AWS CLI." | ✅ | [IC end-active-sessions](https://docs.aws.amazon.com/singlesignon/latest/userguide/end-active-sessions.html) |
| 2.4.4 | **Documented revocation procedure:** pre-deploy an SCP Deny with a placeholder `identitystore:userId`. To revoke, put the user's ID in it, remove their permission-set assignments **and** their account-access-manager role assignments, disable them in the IdP, end their sessions, and disable them in Identity Center. The ID must stay in the Deny for **at least 12 hours**, "otherwise, the user with an active IAM role session will have restored actions". Order matters: if the user is disabled **before** their session is stopped, the console can no longer stop it. | ✅ | [IC revoke-user-permissions](https://docs.aws.amazon.com/singlesignon/latest/userguide/revoke-user-permissions.html), [IC prereqs-revoking-user-permissions](https://docs.aws.amazon.com/singlesignon/latest/userguide/prereqs-revoking-user-permissions.html) |
| 2.4.5 | `identitystore:UserId` "is included when the caller of the request is a user in IAM Identity Center". The docs prefer it to `aws:userId`, which "can change if the user's username or email address changes". | ✅ | [IAM condition keys: identitystore:UserId](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html#condition-keys-identity-store-user-id), [IC prereqs-revoking-user-permissions](https://docs.aws.amazon.com/singlesignon/latest/userguide/prereqs-revoking-user-permissions.html) |
| 2.4.6 | IAM's "revoke active sessions" button does not apply to permission-set roles: "You can't edit roles in IAM that were created from IAM Identity Center permission sets. You must revoke the active permission set session for a user in IAM Identity Center." The page also shows a Deny policy, attached to a role, on `aws:TokenIssueTime` earlier than a chosen time; it revokes that role's sessions issued before then. **Inference (⚠️):** the same condition in an SCP would be an org-wide kill switch. But it would also deny Lambda, ECS and pipeline roles until they refresh their credentials, so it would need careful scoping, for example by `aws:PrincipalArn`. | ✅ / ⚠️ (SCP use) | [IAM id_roles_use_revoke-sessions](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_revoke-sessions.html) |

### 2.5 Who did it: identity in CloudTrail

| # | Finding | Marker | Source |
|---|---|---|---|
| 2.5.1 | For Identity Center's own events (sign-in, portal, CLI login), the user is identified by `userId` and `identityStoreArn` in `userIdentity.onBehalfOf`. The `userIdentity` type is `IdentityCenterUser` or `Unknown`, and workflows "should accept both". "The `userName` and `principalId` fields under the `userIdentity` element are no longer available." The docs give two ways to get the username: look it up in the directory (`identitystore describe-user`), or read the `UserName` that Identity Center emits under `additionalEventData` in sign-in events. | ✅ | [IC sso-cloudtrail-use-cases](https://docs.aws.amazon.com/singlesignon/latest/userguide/sso-cloudtrail-use-cases.html), [CT cloudtrail-event-reference-user-identity](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html) |
| 2.5.2 | The portal API events include `ListAccounts`, `ListAccountRoles`, `GetRoleCredentials` and `Logout`; "Using the AWS CLI can lead to the emission of CloudTrail events" from both public and non-public portal operations. | ✅ | [IC sso-info-in-cloudtrail](https://docs.aws.amazon.com/singlesignon/latest/userguide/sso-info-in-cloudtrail.html) |
| 2.5.3 | **Partly resolved, by inference from docs:** how a call made *with a permission-set role* in a member account (for example `ecs:UpdateService` in prod) names the human in CloudTrail. The chain of evidence:<br>- For SAML-federated and assumed-role principals, `aws:userid` is `role-id:caller-specified-role-name`.<br>- CloudTrail's `principalId` for temporary credentials "includes the session name".<br>- For Identity Center users, `aws:userId` "can change if the user's username or email address changes".<br>- Together: the role session name is derived from the Identity Center username or email, and it appears in `userIdentity.principalId` / `arn`.<br>Two consequences:<br>- It is **not a stable audit key**, because it changes when the username changes.<br>- Whether `onBehalfOf.userId` also appears on these member-account events is **not stated** anywhere (test on a sandbox account).<br>The TEAM blog (2.4.1b) says CloudTrail events carry "the unique identifier of the user". | ✅ (each quote) / ⚠️ (the combined inference; `onBehalfOf` in member accounts) | [IAM reference_policies_variables](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html), [CT user identity](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html), [IC prereqs-revoking-user-permissions](https://docs.aws.amazon.com/singlesignon/latest/userguide/prereqs-revoking-user-permissions.html) |
| 2.5.4 | **Source identity:** an administrator can require roles to be assumed with a `sourceIdentity`. It "cannot be changed during the role session", it persists through role chaining, and it is logged in `sessionContext`. Caveats: "AWS doesn't control the value of the source identity". The docs say "you must choose an attribute that you want your users or IdP to provide" and "you must ensure that you can control how those values are provided". **Asserted by the IdP**, the value is trustworthy; **supplied by the caller**, it is only a hint. Setting it needs `sts:SetSourceIdentity` in the role trust policy. It is "not captured by CloudTrail when an AWS service or service-linked role carries out an action on behalf of" a workforce identity. The pages read do not say whether permission-set roles, whose trust policy Identity Center manages, can require it. | ✅ / ⚠️ (permission sets) | [IAM id_credentials_temp_control-access_monitor](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_control-access_monitor.html), [CT user identity](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html) |
| 2.5.5 | **AWS MCP Server in CloudTrail:**<br>- "All AWS MCP Server actions for authenticated tools are logged by CloudTrail". An example is the `CallReadWriteTool` action, whose event includes an "Exact copy of MCP request params" **and** `responseElements.content[].text`, the tool output.<br>- The sample event has `"eventCategory": "Data"` and `"eventType": "AwsMcpEvent"`. Data events are off by default (2.6.3), and the CloudTrail data-event resource table (read today) has no `aws-mcp` resource type. Yet the MCP page also says the events appear in Event history, which shows only management events (2.6.1). **The docs are inconsistent here. Whether a normal trail records these events, and with which selector, is unverified (⚠️).**<br>- With OAuth, Sign-In also logs `AuthorizeOAuth2Access` and `CreateOAuth2Token`, including the OAuth client ID and the sign-in session ARN. API calls made with OAuth tokens carry `aws:SignInSessionArn` "to correlate API activity with the originating OAuth sign-in session".<br>- **PHI note (inference):** request params **and the tool output** are copied into the event, so CloudTrail can hold the data the agent read (1.11, 1.11.4 L15). | ✅ / ⚠️ (default logging, PHI note) | [Agent Toolkit: logging-using-cloudtrail](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/logging-using-cloudtrail.html), [IAM condition keys: aws:SignInSessionArn](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html#condition-keys-signinsessionarn) |

### 2.6 CloudTrail as the audit store

| # | Finding | Marker | Source |
|---|---|---|---|
| 2.6.1 | **Event history** is on by default: "the past 90 days of **management** events in an AWS Region". It shows no data events. A trail or an event data store is needed for an ongoing record. | ✅ | [CT view-cloudtrail-events](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html) |
| 2.6.2 | An **organization trail**, created from the management account or a CloudTrail delegated administrator, logs the management account and all member accounts. Member-account users "do not have sufficient permissions to delete organization trails, turn logging on or off, change what types of events are logged". New accounts are added automatically. | ✅ | [CT creating-trail-organization](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/creating-trail-organization.html) |
| 2.6.3 | **Data events are off by default** and cost extra ("By default, trails and event data stores do not log data events. Additional charges apply"). Advanced event selectors can filter by resource and `eventName`. Resource types relevant to Papaya include `AWS::S3::Object`, `AWS::Lambda::Function` (Invoke), `AWS::SQS::Queue`, `AWS::SNS::Topic`, `AWS::StepFunctions::StateMachine`, `AWS::SSM::ManagedNode`, and `AWS::RDS::DBCluster`. The last one covers **RDS Data API only**. | ✅ | [CT logging-data-events-with-cloudtrail](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-data-events-with-cloudtrail.html) |
| 2.6.4 | **Log file integrity validation:** SHA-256 hashes plus hourly digest files signed with SHA-256 with RSA, which make it "computationally infeasible to modify, delete or forge CloudTrail log files without detection". Validation can also "assert positively that no log files were delivered … during a given period". | ✅ | [CT cloudtrail-log-file-validation-intro](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html) |
| 2.6.5 | Preventive best practices: a **separate log archive account** with a dedicated S3 bucket, SSE-KMS, least-privilege bucket policy with `aws:SourceArn`, and MFA delete on the log bucket. MFA delete cannot be combined with lifecycle configurations. **Retention:** "The CloudTrail trail default is to store log files indefinitely" in the bucket; lifecycle rules are how to expire them. So a retention period and MFA delete need a deliberate choice. | ✅ | [CT best-practices-security](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/best-practices-security.html) |
| 2.6.6 | **CloudTrail Lake "will no longer be open to new customers starting May 31, 2026."** Existing customers continue. As of the access date (2026-11-08), a design must not assume Papaya can adopt it, unless Papaya already uses it (⚠️ unknown). | ✅ | [CT cloudtrail-lake](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake.html) |

### 2.7 Audit gaps below the AWS API: Aurora

| # | Finding | Marker | Source |
|---|---|---|---|
| 2.7.1 | SQL sent over a normal PostgreSQL connection is **not** an AWS API call. CloudTrail data events for RDS cover only the Data API (2.6.3). So `SELECT`/`UPDATE` run by a person or an agent through `psql` leaves no CloudTrail record. | ✅ (Data API scope) / ⚠️ inference (no page states the negative) | [CT data events](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-data-events-with-cloudtrail.html) |
| 2.7.2 | **Database Activity Streams (Aurora PostgreSQL):** a near-real-time activity stream pushed to Kinesis, always encrypted with KMS. Separation from DBAs needs configuration: "you can control administrator access to data streams by configuring the Database Activity Streams feature. DBAs don't have access to the collection, transmission, storage, and processing of the streams".<br>- **Asynchronous mode:** records "might have been lost" during errors.<br>- **Synchronous mode:** the session waits until the record is durable, but "if the event can't be made durable for some reason, the database session returns to normal activities", and an RDS event says records might be lost.<br>- **Both modes:** loss is signalled by RDS events, which need an alert.<br>The rest of this row: It must be stopped before a major version upgrade. Supported PostgreSQL instance classes are listed (r4–r8g, r6id, x2g); **db.serverless is not listed** (⚠️: confirm Serverless v2 support if Papaya uses it). Kinesis is charged. | ✅ / ⚠️ (Serverless v2) | [Aurora DBActivityStreams](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/DBActivityStreams.html) |
| 2.7.3 | **Inference:** an activity stream records SQL statements, and literals in them can carry PHI (1.11). The audit stream is then itself a PHI-bearing store (add to 1.11.4 L15). `pgaudit` is the in-engine alternative; **not researched this session** (⚠️). | ⚠️ inference | — |

### 2.8 IAM Access Analyzer (policy checks usable in CI)

| # | Finding | Marker | Source |
|---|---|---|---|
| 2.8.1 | Custom policy checks: `check-no-new-access` (does the new version grant more than the old?), `check-access-not-granted` (does it grant listed actions?), `check-no-public-access`. Each check is charged. | ✅ | [IAM access-analyzer-custom-policy-checks](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-custom-policy-checks.html) |

### 2.9 What this means for Papaya (inferences — to be used in the design)

These are my conclusions from the findings above, not documented facts:

1. **On a laptop, an agent that calls the AWS CLI/SDK directly is indistinguishable from the
   engineer.**
   - **Why:** it uses the same SSO cache, and that cache reaches every role assigned to the
     engineer (2.2.1, 2.2.2). App ID is a client hint (2.2.3). Source identity is trustworthy only
     when the IdP asserts it (2.5.4).
   - **Consequence:** a separate "agent" permission set alone does not separate the two. The
     agent can still use the engineer's other roles from the same cache.
   - **The one native, server-set signal is the AWS MCP Server** (2.2.4, 2.2.5). Calls through it
     carry `aws:ViaAWSMCPService` / `aws:CalledViaAWSMCP`, usable in SCPs. They are absent (or
     false) on direct calls (2.2.5). So the signal is a control only if the agent **cannot make
     direct calls at all**.
   - **Untested design idea, not in the docs (⚠️):** an agent-only role that denies requests not
     made through MCP. AWS documents only the reverse ("deny when via MCP"). The idea helps only if
     the agent cannot reach the engineer's other credentials:
     - **With SigV4,** the local proxy reads the AWS CLI credentials as the same OS user, so this
       needs the proxy outside the agent's sandbox (1.6).
     - **With OAuth,** the MCP path itself needs no AWS CLI credentials. But the MCP client still
       holds the OAuth token, and the agent must still be kept away from the engineer's own SSO
       cache (⚠️). There is also no multi-profile.

     Without that condition, a separate role adds no control. Also to test: whether
     `aws___run_script` and `aws___get_presigned_url` downloads carry the keys. A presigned-URL
     download is made directly by the client.
   - **The decisive layer remains no standing prod-write assignment for humans** (#2). Then
     nothing running on the laptop can write to prod outside an approved, time-boxed window.
     **Inside that window,** any process on the laptop can use the grant. This is a residual risk
     to state openly.
2. **Changing prod: the default path is a pipeline; human write access is the exception, via JIT.**
   - **Default path:** humans hold no prod-write rights. Changes go through CI with a deploy role.
     The named-human approval happens at the CI gate (GitHub Environments, Topic 3).
   - **JIT, for the rest:** when a human needs write access (manual operations, incidents), it
     comes from a JIT assignment. AWS has no native request/approve feature (2.4.1). The options:
     - a partner product (2.4.1);
     - the TEAM sample (2.4.1b);
     - a small home-built flow on `CreateAccountAssignment` / `DeleteAccountAssignment` (2.4.2).
   - **Audit evidence:** CloudTrail records the **grant**, and its caller is the automation role.
     It does **not** record the approver. The approver's identity lives in the approval system
     (GitHub, Linear, the partner tool, TEAM). It must be linked to the grant, for example by
     request ID, and kept as audit evidence (⚠️ design).
   - **Incidents:** under GĐ-8 the incident path is the same flow with a fast approver, not a
     bypass.
   - **Outage path:** the emergency direct-federation path (2.1.11) is for an Identity Center
     outage, and needs its own approval and alerting.
3. **Revocation is slow by design.**
   - Role sessions outlive portal sessions and assignments (2.4.3). IAM's revoke button does not
     apply to permission-set roles (2.4.6).
   - Prod permission sets should use the **1-hour minimum** session duration (2.1.4).
   - Pre-deploy the `identitystore:userId` Deny SCP on the prod OU (2.4.4), and keep the
     `aws:TokenIssueTime` Deny as an org-wide kill switch (2.4.6). This is an inference (⚠️):
     scope it by `aws:PrincipalArn` so that workload roles are not hit.
   - Set the portal session length deliberately (2.1.5, 2.1.6), including the IdP session,
     which can silently extend it.
4. **SCPs are the guardrail the agent cannot edit, but only in member accounts.** Examples:
   - protect the org trail and the log archive (2.6.2);
   - deny region drift;
   - deny data-plane reads on PHI buckets and queues, except for the application roles **and**
     the approved JIT read path that GĐ-9 allows (`aws:PrincipalArn`; tenant scoping via ABAC
     session tags, 2.1.8). This supports 1.11.4 L3–L4;
   - deny destructive actions when `aws:ViaAWSMCPService` is true (2.2.5). On its own this is
     bypassed by direct CLI calls (#1), so it is a second layer, not a control.

   Constraints:
   - Keep everything out of the management account (2.3.2, 2.3.7).
   - Deny-list SCPs sit on `FullAWSAccess` (2.3.4b).
   - Limits are 10 direct attachments per target and 10,240 characters each (2.3.4).
   - RCPs add an outside-the-org boundary for S3, SQS, KMS, Secrets Manager and Logs, but not for
     Aurora, Lambda or SNS (2.3.6).
5. **Audit trail for Compliance:**
   - **Trail:** an organization trail to a separate log-archive account, with integrity validation
     and a locked-down bucket (2.6.2, 2.6.4, 2.6.5).
   - **Retention:** decide it explicitly. The default is indefinite, and MFA delete excludes
     lifecycle rules (2.6.5).
   - **Data events:** only where they matter, because of cost (2.6.3): PHI buckets, prod Lambda
     invoke, prod SQS.
   - **No CloudTrail Lake** (2.6.6).
   - **Who did it:** use `onBehalfOf.userId` in CloudTrail where present. Otherwise use the
     session name plus a lookup in the directory (⚠️, 2.5.3). The session name changes when the
     username changes, so it is not a stable key. (`identitystore:UserId` is a policy condition
     key, not a CloudTrail field.)
   - **MCP events:** do not assume AWS MCP Server events are in the trail until the selector
     question is answered (2.5.5).
   - **Aurora:** SQL is invisible to CloudTrail (2.7.1). Use Database Activity Streams or pgaudit,
     alert on the RDS events about lost records, and treat that stream as PHI (2.7.2, 2.7.3).
   - **Same gap for shell sessions:** ECS Exec and SSM shell sessions likely have the same issue
     (⚠️ not researched, 2.10).
6. **Policy changes in Pulumi PRs can be checked mechanically.** `check-no-new-access` in CI makes
   "this PR widens IAM" a visible, reviewable fact (2.8.1; ties to Topics 3–4).

### 2.10 Open items (Topic 2)

- [ ] ⚠️ Does `onBehalfOf.userId` appear on member-account events made with a permission-set role,
      and what exactly is the session name (2.5.3)? Test on a sandbox account.
- [ ] ⚠️ Do profiles sharing one `sso-session` reuse the single cached token (2.2.2)? Test.
- [ ] ⚠️ Agent-only role that denies non-MCP calls (2.9 #1): which condition operator
      (`BoolIfExists` / `Null`), whether `aws___run_script` and presigned-URL downloads carry the
      keys, and whether the proxy can be kept outside the agent's sandbox. Test.
- [ ] ⚠️ Are AWS MCP Server events (`eventCategory: Data`) recorded by a normal trail, and with
      which event selector (2.5.5)?
- [ ] ⚠️ Can permission-set roles (or account-access-manager roles) require `sts:SetSourceIdentity`
      (2.5.4, 2.1.10)?
- [ ] ⚠️ Does Papaya use an external IdP (MFA and session length then live there, 2.1.5, 2.1.7),
      Aurora Serverless v2 (2.7.2), or CloudTrail Lake already (2.6.6)?
- [ ] ⚠️ Not researched: `pgaudit` on Aurora PostgreSQL; Athena over CloudTrail in S3; ECS Exec and
      SSM Session Manager logging of commands; S3 Object Lock for the CloudTrail bucket; whether
      App ID shows in CloudTrail `userAgent`.

### 2.11 Review log (Topic 2)

- **Round 1 (2026-11-08)**, independent reviewer subagent. Sources: the raw AWS pages, plus
  pages it fetched itself (IAM policy variables, the TEAM blog).
  - Result: 1 HIGH, 5 MEDIUM, 8 LOW, 7 coverage gaps.
  - I re-checked the HIGH, the MEDIUM items and the main gaps against the sources (MCP condition
    keys and the Agent Toolkit pages, SCP evaluation, IAM revoke page, retention sentence, CLI
    cache wording, TEAM blog). All were accepted.
  - The HIGH: 2.9 #2 claimed CloudTrail logs the approver. It does not; only the grant is
    logged, by the automation role.
  - The MEDIUM fixes:
    - 2.9 #2 reframed: the pipeline is the default path, JIT is for human access;
    - 2.2.2 backed by docs;
    - 2.5.3 partly resolved;
    - 2.9 #1 rewritten with the MCP keys and the limits of a separate agent role;
    - 2.7.2 qualifiers.
  - Added from the gaps: AWS MCP Server (2.2.4, 2.2.5, 2.5.5), SCP evaluation (2.3.4b), TEAM
    (2.4.1b), IAM revoke and `aws:TokenIssueTime` (2.4.6), and CloudTrail retention (2.6.5).
    ECS Exec and SSM logging went to open items.
- **Round 2 (2026-11-08)**, same reviewer:
  - Round 1: 17 findings FIXED; 1 PARTLY (F5); 2 moved to open items.
  - New: 0 HIGH, 3 MEDIUM, 6 LOW. I verified the MEDIUM items against the raw pages: the sample
    MCP event is `eventCategory: Data` and includes `responseElements`, and OAuth lists Claude Code
    CLI. All were accepted and fixed:
    - 2.9 #1: the MCP-only role is now an untested idea, with its preconditions stated;
    - 2.5.5: MCP events are data events, and default logging is unverified;
    - tool output in CloudTrail, also added to 1.11.4 L15;
    - LOW: 2.2.4 wording and the read-only caveat, the 2.2.5 key presence quotes, the 2.3.4b
      inference label, the 2.4.6 SCP kill-switch caveat, the 2.9 #4 caveat, and 2.9 #5 field vs
      key.
- **Round 3 (2026-11-08)**, same reviewer:
  - Round 2: 8 findings FIXED, 1 PARTLY.
  - New: 0 HIGH, 0 MEDIUM, 2 LOW (OAuth wording in 2.9 #1; the kill-switch caveat in 2.9 #3).
    Both fixed, together with one quote fix in 2.2.5.
  - **Topic 2 closed** (no HIGH/MEDIUM).

---

## Topic 3 — GitHub: OIDC, Environments, rulesets, CODEOWNERS, self-approval

Accessed 2026-11-08. GitHub docs pages were downloaded as Markdown through
`https://docs.github.com/api/article/body?pathname=/en/<path>` (HTTP 200, **local check**) and
read from those copies. That API drops the "available in plans" banner, so plan statements were
read from the HTML page of the same article (**local check**). Links point to
`https://docs.github.com/en/<path>`.

Context:
- The brief says only "a single monorepo on GitHub". **Papaya's GitHub plan is unknown.**
- `work/01-problem-framing.md` GĐ-5 assumed, unverified, that the plan supports environment
  required reviewers on private repos. 3.1.2 shows that this holds **only on GitHub Enterprise**.

### 3.1 Environments and deployment protection rules

| # | Finding | Marker | Source |
|---|---|---|---|
| 3.1.1 | Required reviewers: "up to six users or teams"; "Only one of the required reviewers needs to approve the job". Optional "prevent self-reviews": "users who initiate a deployment cannot approve the deployment job, even if they are a required reviewer". | ✅ | [deployments-and-environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments) |
| 3.1.2 | **Plan limits:**<br>- Free, Pro and Team plans: required reviewers, wait timers, admin-bypass control and custom deployment protection rules are **"only available for public repositories"**. Each feature carries its own note to that effect.<br>- **Team, private repos:** environments, environment secrets and **deployment branch/tag restrictions** are available.<br>- ⇒ On Team, a private monorepo **cannot use environment approval gates**. | ✅ | [deployments-and-environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments), [manage-environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments) |
| 3.1.3 | Deployment branches and tags: "No restriction", "Protected branches only", or "Selected branches and tags". The rule "is matched against the `GITHUB_REF` of the workflow run". Adding `refs/pull/*/merge` "would also allow workflows triggered by `pull_request` events to deploy". | ✅ | [deployments-and-environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments) |
| 3.1.4 | "By default, administrators can bypass the protection rules and force deployments". An environment can be configured to disallow this. A bypass is possible only while a job is "Pending". On Team private repos the setting is unavailable, and the branch restriction is the only environment protection. "To configure an environment in an organization repository, you must have `admin` access", so admins can change it. Whether they can also *bypass* it at run time is not stated (⚠️).<br>**Audit coverage of environment changes:**<br>- `environment.update_protection_rule` is described as "A GitHub Actions deployment protection rule was updated **via the API**".<br>- No event was found in the pages read for changes to the deployment-branch policy, or for changes made in the UI (⚠️).<br>- `environment.delete` and `environment.remove_protection_rule` exist.<br>- "Running a workflow that references an environment that does not exist will create an environment with the referenced name." **Inference (⚠️):** if `production` is deleted, the next workflow that references it recreates it **without protection**. The OIDC `sub` is still `environment:production`, so the AWS trust still accepts it. | ✅ / ⚠️ (run-time bypass, missing events, recreation) | [deployments-and-environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments), [review-deployments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments), [manage-environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments), [audit-log-events](https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/audit-log-events-for-your-organization) |
| 3.1.5 | Environment secrets: a job that needs approval "cannot access environment secrets until one of the required reviewers approves it". On **self-hosted runners**, jobs "are not run in an isolated container, even if they use environments", so environment secrets there should be treated like repository secrets. | ✅ | [deployments-and-environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments) |
| 3.1.6 | Custom deployment protection rules, which are GitHub Apps that gate with external systems such as ServiceNow, are "currently in public preview". At most 6 rules can be enabled per environment. | ✅ | [deployments-and-environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments) |

### 3.2 Rulesets, branch protection, CODEOWNERS

| # | Finding | Marker | Source |
|---|---|---|---|
| 3.2.1 | **Plans:**<br>- **Rulesets:** "available in public repositories with GitHub Free … and in public and private repositories with GitHub Pro, GitHub Team, and GitHub Enterprise Cloud". There can be up to 75 per repository and 75 organization-wide. **The same page contradicts itself** about organization-level rulesets. Line 7 says rulesets apply "to a repository or to multiple repositories in an organization for customers on GitHub Team and GitHub Enterprise plans". A later line says org-level targeting is for "organizations on the GitHub Enterprise plan" (⚠️ for Team).<br>- **Push rulesets:** "available for the GitHub Team plan in internal and private repositories".<br>- **Protected branches and code owners:** available in private repositories on Pro, Team and Enterprise. | ✅ / ⚠️ (org-level on Team) | [about-rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets), [available-rules-for-rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets), [about-protected-branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches), [about-code-owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners) |
| 3.2.2 | Rulesets layer: "if multiple rulesets target the same branch … the most restrictive version of the rule applies", and they also layer with branch protection rules. "Anyone with read access to a repository can view its active rulesets", including auditors. Bypass can be granted to roles, teams or GitHub Apps. The bypass list is opt-in: eligible entries such as "Repository admins, organization owners" must be added. This differs from branch protection, which exempts admins by default (3.2.6). A ruleset can be set to "Disabled", and admins or custom roles with "edit repository rules" manage rules. Inference (⚠️): those people can therefore edit or disable a ruleset, and nothing in the pages read prevents it. Edits are logged as `repository_ruleset.update` ("A repository ruleset was edited"). | ✅ / ⚠️ (inference) | [about-rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets), [creating-rulesets-for-a-repository](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository), [available-rules-for-rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) |
| 3.2.3 | **Rule "Require a pull request before merging"**, with these options:<br>- a number of approvals;<br>- dismiss stale approvals when the diff changes;<br>- require code-owner review;<br>- restrict who can dismiss reviews;<br>- **"require an approval from someone other than the last person to push"**;<br>- require conversation resolution;<br>- a required merge method.<br>The docs add: "If you are concerned about pull requests being 'hijacked' (where unapproved content is added to approved pull requests), it is safer to dismiss stale reviews." | ✅ | [available-rules-for-rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) |
| 3.2.4 | **Path-based "Required reviewers"** inside that rule: "require review or approval from specific teams when a pull request changes certain files or directories". Up to 15 teams, 0–10 approvals per team, `.gitignore`-style patterns, and the team needs write access. Inference: this fits a monorepo, for example by requiring 2 approvals from a platform team on `infra/**`. | ✅ / ⚠️ (example) | [available-rules-for-rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) |
| 3.2.5 | Other rules relevant here: "Require deployments to succeed before merging", require status checks (note: "Any person or integration with write permissions to a repository can set the state of any status check …; you can select an app as the expected source"), require signed commits, block force pushes, and push rules "Restrict file paths" (200 entries). | ✅ | [available-rules-for-rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) |
| 3.2.6 | Branch protection: "By default, the restrictions of a branch protection rule don't apply to people with admin permissions". "Do not allow bypassing the above settings" applies them to admins as well. An admin override is logged as `protected_branch.policy_override`. | ✅ | [about-protected-branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches), [audit-log-events](https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/audit-log-events-for-your-organization) |
| 3.2.7 | **CODEOWNERS:**<br>- The file is read from `.github/`, the root or `docs/`, **on the base branch** of the PR.<br>- Owners "must have write permissions".<br>- "If code has multiple owners, an approval from *any* of the code owners will be sufficient".<br>- **Silent failures:** "If any line in your CODEOWNERS file contains invalid syntax, that line will be skipped". A user or team that does not exist or lacks access means "a code owner will not be assigned". A file over 3 MB "will not be loaded".<br>- Errors are listed by a REST endpoint. | ✅ | [about-code-owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners), [available-rules-for-rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) |
| 3.2.8 | The Actions security guide recommends putting `.github/workflows` under CODEOWNERS "so that any proposed changes to these files will first require approval from a designated reviewer". | ✅ | [secure-use](https://docs.github.com/en/actions/reference/security/secure-use) |

### 3.3 Stopping a PR author from approving their own change

| # | Finding | Marker | Source |
|---|---|---|---|
| 3.3.1 | "Pull request authors cannot approve their own pull requests. You will also not be able to approve a pull request that was raised by GitHub Copilot if it was you who assigned Copilot to the issue to which the pull request relates." Also, "Approvals by GitHub Copilot" appear in the list "even though GitHub Copilot reviews do not count" toward merge requirements. | ✅ | [approving-a-pull-request-with-required-reviews](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/approving-a-pull-request-with-required-reviews) |
| 3.3.2 | Rulesets have an "Additional approval for unattributed Copilot pull requests" setting (public preview, on by default). It adds one more required approval when Copilot opens a PR "under its own app identity instead of on behalf of a person". The reason given: "Requiring one approval usually means two people are involved … That assumption doesn't hold" for agent-authored PRs. **It applies to Copilot only.** No equivalent is documented for other GitHub Apps, such as the Claude GitHub App. | ✅ | [available-rules-for-rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) |
| 3.3.3 | **"Allow GitHub Actions to create and approve pull requests"** is a repository and organization setting that controls whether `GITHUB_TOKEN` can create and approve PRs. The docs call allowing it "a security risk if the pull request is merged without proper oversight". Changes are audited as `org.set_workflow_permission_can_approve_pr` and `repo.set_workflow_permission_can_approve_pr`. | ✅ | [managing-github-actions-settings-for-a-repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository), [secure-use](https://docs.github.com/en/actions/reference/security/secure-use), [audit-log-events](https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/audit-log-events-for-your-organization) |
| 3.3.4 | **Inference — the agent loophole.** "Author" means the GitHub account that opened the PR.<br>- **Claude Code on a laptop** that opens the PR with the engineer's own `gh` login: the engineer is the author and cannot approve it (3.3.1). A second human is needed. This case is covered.<br>- **Claude GitHub App / `claude-code-action`:** if the app opens the PR, the author is the app (how the action attributes PRs is an open item, 3.7). The engineer who triggered it is then **not** blocked from approving, because GitHub's protection covers Copilot only (3.3.2). One approval could then mean zero independent reviewers.<br>- **Mitigations to evaluate:**<br>  - require 2 approvals on protected branches;<br>  - path-based required reviewers (3.2.4);<br>  - "approval from someone other than the last person to push" (3.2.3), which does not help when the app is the last pusher and the triggering engineer approves;<br>  - a required status check that fails when the approver is the person who triggered the agent run, and that maps the app PR to that person (⚠️ design). The check's **expected source must be pinned to a specific app** (3.2.5). Otherwise any job with `statuses: write`, including the agent's job, can set it to pass. | ⚠️ inference | — |

### 3.4 OIDC federation to AWS and GCP

| # | Finding | Marker | Source |
|---|---|---|---|
| 3.4.1 | OIDC lets workflows access AWS and GCP "without needing to store the AWS credentials as long-lived GitHub secrets". Provider URL `https://token.actions.githubusercontent.com`. Audience `sts.amazonaws.com` with `aws-actions/configure-aws-credentials`. On GCP: a Workload Identity Pool, attribute mapping plus conditions, a service account with `roles/iam.workloadIdentityUser`, and `google-github-actions/auth`. | ✅ | [oidc-in-aws](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws), [oidc-in-google-cloud-platform](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-google-cloud-platform) |
| 3.4.2 | "You **must** define at least one condition, so that untrusted repositories can't request access tokens". AWS IAM "recommends that users evaluate the IAM condition key, `token.actions.githubusercontent.com:sub`". Dependabot jobs carry `event_name` = `dynamic`; "if … your cloud provider supports conditions on `event_name`, allow only the event names expected". AWS does not support custom claims (3.4.5), so on AWS this can only be done through `sub` customisation. | ✅ | [oidc-in-aws](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws), [oidc reference](https://docs.github.com/en/actions/reference/security/oidc) |
| 3.4.3 | **`sub` formats:**<br>- With an environment: `repo:ORG/REPO:environment:NAME`. Otherwise: `…:ref:refs/heads/BRANCH`, `…:ref:refs/tags/TAG`, or `…:pull_request`.<br>- "If you use a workflow with an environment, the `sub` field must reference the environment name".<br>- **Inference:** with the default `sub` format, the environment form contains **neither the branch nor the event or workflow**. Which branches may use the role is then enforced only by the environment's deployment-branch rule (3.1.3), not by AWS. The `sub` can be customised to add more (3.4.5). | ✅ / ⚠️ (inference) | [oidc reference: example subject claims](https://docs.github.com/en/actions/reference/security/oidc#example-subject-claims), [oidc-in-aws](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws) |
| 3.4.4 | **Immutable subject claims:** "repositories created after July 15, 2026 now use an immutable default subject format that includes both the owner ID and repository ID", for example `repo:octo-org@123456/octo-repo@456789:ref:refs/heads/main`. Older repositories keep the old format "unless you opt in". Renames and transfers after that date move to the new format. **Trust policies must match the format in use.** | ✅ | [oidc reference: immutable subject claims](https://docs.github.com/en/actions/reference/security/oidc#immutable-subject-claims) |
| 3.4.5 | The subject can be customised per org or repo with `include_claim_keys`, for example to require `job_workflow_ref`, so that only a specific **reusable workflow** at a specific ref can get the role (`repo:…:environment:prod:job_workflow_ref:…`). "Support for custom claims for OIDC is unavailable in AWS". For such clouds the reusable-workflow page says: "For clouds that only support the standard claims (`aud` and `sub`), you can use the API to customize the `sub` claim to include `job_workflow_ref`." A repository administrator can reset the customisation to `use_default` through the REST API. The pages read do not state which plans include subject customisation (⚠️). | ✅ / ⚠️ (plan) | [oidc reference: customizing the subject claims](https://docs.github.com/en/actions/reference/security/oidc#customizing-the-subject-claims-for-an-organization-or-repository), [oidc-with-reusable-workflows](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-with-reusable-workflows), [oidc-in-aws](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws) |
| 3.4.5b | **GCP side:**<br>- Google requires more than GitHub's "at least one condition": "To help protect against spoofing threats, you must use an attribute condition that restricts access to tokens issued by your GitHub organization".<br>- GitHub: "Support for custom claims is currently available for Google Cloud Platform and HashiCorp Vault". Inference (⚠️): so on GCP, attribute conditions can test `job_workflow_ref`, `ref` or `event_name` directly, without customising `sub`. No page read says this in so many words.<br>- In a token from a reusable workflow, `ref` and `workflow` describe the **caller**, and `job_workflow_ref` describes the **called** workflow.<br>- `principalSet` direct access, without a service account, and conditions on immutable IDs were not read in detail (📖). | ✅ / 📖 / ⚠️ (inference) | [Google Cloud: workload-identity-federation-with-deployment-pipelines](https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines), [oidc-with-reusable-workflows](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-with-reusable-workflows) |
| 3.4.5c | **`GITHUB_REF` per trigger**, which is what the environment branch rule matches (3.1.3):<br>- `issue_comment`, `schedule`, `workflow_run`: "Default branch".<br>- `pull_request_target`: "runs in the context of the default branch of the base repository".<br>- `workflow_dispatch`: "Branch or tag that received dispatch".<br>- `merge_group` (merge queue): the merge group ref.<br>**Inference:** any workflow file on `main` that references `environment: production` passes a "main only" rule **whatever its trigger**. That includes an `issue_comment`-triggered agent workflow, or a `pull_request_target` workflow that checks out PR code. A dispatch from a non-main branch is blocked, but a dispatch on `main` that takes a ref or SHA input can still deploy unmerged code. | ✅ / ⚠️ (inference) | [events-that-trigger-workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows) |
| 3.4.6 | Requesting a token needs `permissions: id-token: write` on the job or workflow. It "only enables fetching and setting the OIDC token; it does not grant write access to other resources". | ✅ | [oidc reference: workflow permissions](https://docs.github.com/en/actions/reference/security/oidc#workflow-permissions-for-the-requesting-the-oidc-token) |

### 3.5 Runners, tokens, third-party actions, audit

| # | Finding | Marker | Source |
|---|---|---|---|
| 3.5.1 | **GitHub-hosted runners:** "The Linux and macOS virtual machines both run using passwordless `sudo`". Each runner, except single-CPU ones, "is a new virtual machine". The Actions security guide calls them "ephemeral and clean isolated virtual machines". **Inference (⚠️), answering Topic 1 open item 1.9 / 1.8 #3:** if the agent has shell access (Bash not restricted), a step running it on a standard Linux GitHub-hosted runner can rewrite `/etc/claude-code/managed-settings.json` with `sudo`. A policy file written by an earlier step in the same job is then **not** tamper-proof against the agent step. Single-CPU runners are "hosted in a container on a shared VM", and the page does not say whether they have sudo. | ✅ (sudo, VM) / ⚠️ (inference) | [github-hosted-runners: administrative privileges](https://docs.github.com/en/actions/reference/runners/github-hosted-runners#administrative-privileges), [secure-use](https://docs.github.com/en/actions/reference/security/secure-use) |
| 3.5.2 | **Self-hosted runners:** "do not have guarantees around running in ephemeral clean virtual machines, and can be persistently compromised by untrusted code". Anyone who can open a PR in a private repo "generally those with read access" can compromise them. Runner groups limit which repositories can use them. Just-in-time runners exist (not read in detail, 📖). | ✅ | [secure-use: hardening for self-hosted runners](https://docs.github.com/en/actions/reference/security/secure-use) |
| 3.5.3 | `GITHUB_TOKEN` is a GitHub App installation token "limited to the repository that contains your workflow". It lives at most 6 hours on hosted runners. The default org or repository setting is either "permissive" (read and write for all) or "restricted" (read for `contents` and `packages`). Per-job `permissions:` narrows it. | ✅ | [github_token](https://docs.github.com/en/actions/concepts/security/github_token), [disabling-or-limiting-github-actions-for-your-organization](https://docs.github.com/en/organizations/managing-organization-settings/disabling-or-limiting-github-actions-for-your-organization) |
| 3.5.3b | **Repository secrets:** "Any user with write access to your repository has read access to all secrets configured in your repository". | ✅ | [secure-use](https://docs.github.com/en/actions/reference/security/secure-use) |
| 3.5.4 | `pull_request_target` and `workflow_run` "are privileged" and "may have repository write access and access to referenced secrets". They must not check out untrusted code. | ✅ | [secure-use: untrusted code checkout](https://docs.github.com/en/actions/reference/security/secure-use) |
| 3.5.5 | **Third-party actions:** a compromised action "would have access to all secrets configured on your repository". The strongest measure is a **workflow dependency lockfile** (`.github/workflows/actions.lock`, generated by `gh actions-lock`). It "pins a commit SHA to every action … including transitive dependencies" but does not pin reusable workflows. The alternative is full-SHA pinning. There is an org policy "Require actions to be pinned to a full-length commit SHA", and locked dependencies satisfy it. | ✅ | [secure-use: third-party actions](https://docs.github.com/en/actions/reference/security/secure-use), [workflow-dependency-lockfiles](https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles), [disabling-or-limiting-github-actions-for-your-organization](https://docs.github.com/en/organizations/managing-organization-settings/disabling-or-limiting-github-actions-for-your-organization) |
| 3.5.6 | **Org audit log:**<br>- It covers "the last 180 days", and "only owners can access" it.<br>- Events include `workflows.approve_workflow_job` (a deployment approval), `environment.update_protection_rule`, `repository_ruleset.create/update/destroy`, `protected_branch.policy_override`, and `org.update_actions_secret`.<br>- Many events carry an `actor_is_agent` field. **Its meaning is not defined** in the pages read (⚠️).<br>- The log can be exported as JSON or CSV, within documented "Export limits". Streaming was not researched (⚠️). | ✅ / ⚠️ (`actor_is_agent`, streaming) | [secure-use](https://docs.github.com/en/actions/reference/security/secure-use), [reviewing-the-audit-log-for-your-organization](https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization), [audit-log-events](https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/audit-log-events-for-your-organization) |

### 3.6 What this means for Papaya (inferences — to be used in the design)

These are my conclusions from the findings above, not documented facts:

1. **The GitHub plan decides where the "named human approved it" gate can sit.**
   - **On Enterprise Cloud:** a `production` environment with required reviewers, prevent
     self-review, no admin bypass, and deployment branches = `main` (3.1.1–3.1.4). The approval
     is per deployment job and logged as `workflows.approve_workflow_job` (3.5.6).
   - **On Team:** environments have **no approval gate** on a private repo (3.1.2). The gate must
     be the **PR merge to `main`**, enforced by:
     - rulesets: PR required, ≥1–2 approvals, code-owner review, path-based team reviewers for
       `infra/**` and `.github/**`, dismiss stale approvals, last-push approval, an empty bypass
       list (3.2.2–3.2.4);
     - the `production` environment restricted to `main` (3.1.3).
   - **Prerequisite on both plans: the branch rule alone does not mean "only merged, approved
     code reaches prod".** Every workflow on `main` passes a "main only" rule, whatever its trigger
     (3.4.5c). So all of the following must also hold:
     - only reviewed deploy workflows may reference `production`, enforced by CODEOWNERS on
       `.github/workflows` and a CI check;
     - deploy workflows take no ref or SHA input, and deploy the commit they run on;
     - no `production` job runs on `issue_comment`, `pull_request_target` or `workflow_run`.
       A `schedule` deploy of the current `main` commit is acceptable only if it deploys that
       commit and takes no input;
     - preferably, the `sub` claim is pinned to the reusable deploy workflow (`job_workflow_ref`,
       3.4.5).

     Under these conditions, merge approval equals deploy approval on Team.
   - **Admins remain a gap.** Admins and holders of "edit repository rules" can edit rulesets,
     environments and the OIDC `sub` customisation. This is mostly logged, not prevented (3.1.4,
     3.2.2, 3.4.5). So: few admins, periodic access review, and alerts on `repository_ruleset.update`,
     `environment.update_protection_rule`, `environment.remove_protection_rule`,
     `environment.delete` and `protected_branch.policy_override`.
   - **UI changes to the branch policy may not be audited** (⚠️, 3.1.4). A deleted
     `production` environment is likely recreated without protection by the next workflow
     that references it. The deletion itself is logged (⚠️ inference, 3.1.4). So a scheduled
     job should also compare the live environment configuration with the expected one, as
     drift detection (⚠️: the REST endpoint was not researched).
   - **GĐ-5 holds only on Enterprise.** It should go back to the framing as a correction and an
     open question for Papaya.
2. **OIDC trust must pin the repository, the gate and, where possible, the workflow** (3.4.2–3.4.5c):
   - **AWS:** prod roles trust only `repo:<org>/<repo>:environment:production`, in the repo's
     `sub` format (3.4.4). Ideally a customised `sub` includes `job_workflow_ref`, because AWS
     cannot test other claims (3.4.5).
   - **GCP:** the attribute condition must restrict to the GitHub organization (required by
     Google). It can also test `job_workflow_ref`, `ref` and `event_name` directly (3.4.5b).
   - **Non-prod:** roles trust a separate environment.
   - **Secrets:** prod credentials never live in repository secrets, because anyone with write
     access can read those (3.5.3b). This removes the long-lived AWS keys from the brief (P5).
3. **Agent-authored PRs need one more rule than human PRs** (3.3.4). Opening PRs with the
   engineer's own identity keeps GitHub's built-in author rule. App-authored PRs need 2 approvals
   or a custom check whose source app is pinned. "Allow GitHub Actions to create and approve pull
   requests" stays **off** (3.3.3).
4. **CI agents and policy files:** on standard GitHub-hosted runners, an agent with shell access
   has root, so Claude Code managed settings written in the job are advisory (3.5.1, closes the
   Topic 1 question). The real limits for a CI agent are:
   - the job's `GITHUB_TOKEN` permissions (3.5.3);
   - **no** `environment: production` in any agent workflow, so it gets no prod OIDC trust
     (3.4.5c);
   - the base-branch config restore in `claude-code-action` (1.7.9).

   Self-hosted runners would allow a root-owned policy, but bring persistence risks (3.5.2).
5. **Supply chain of CI itself:**
   - Workflow lockfile or SHA pinning, enforced by org policy (3.5.5).
   - CODEOWNERS on `.github/` (3.2.8), plus CI validation of the CODEOWNERS file, because invalid
     lines fail silently (3.2.7).
   - Restricted default `GITHUB_TOKEN` (3.5.3); no `pull_request_target` with checkout (3.5.4).
6. **Audit retention gap:** the org audit log keeps 180 days (3.5.6). ISO 27001 and HIPAA evidence
   needs longer, so it must be exported periodically (JSON or CSV, within the export limits, ✅)
   or streamed (⚠️ not researched; may be Enterprise-only).

### 3.7 Open items (Topic 3)

#### Giả định của owner (2026-11-08)

**These are design assumptions set by the repo owner, not facts about Papaya.** The owner has no
access to Papaya's systems. Recorded verbatim, as written by the owner in the session of
2026-11-08:

> 1. Gói GitHub: giả định Papaya dùng gói Team (không phải Enterprise).
> 2. Format `sub` của OIDC: giả định repo dùng format mới (có ID). Mình không biết ngày tạo repo thật của Papaya.
> 3. Claude GitHub App: mình chưa biết nó ghi tác giả PR và commit thế nào. Giả định xấu nhất: tác giả PR là app, người gọi agent vẫn tự duyệt được. Thiết kế không được dựa vào hành vi mặc định của app.
> 4. Merge queue : Giả định là có sử dụng merge queue, thiết kế cần chạy được với merge queue thì chỉ ghi rõ cần thêm gì, đừng đổi giả định.

**Owner decision on the A1/A4 conflict (2026-11-08), verbatim:**

> Giữ Team và bỏ merge queue.

So the design assumes **Team and no merge queue**. A4 is superseded. Its row below is kept only
as a reference for a possible later move to Enterprise Cloud; the design does not use it.

**Consequences for the design.** These are my inferences from 3.1–3.6, unless a source is given.
The "cheap to cover the other case" lines do not change the assumptions.

| Assumption | Consequence for the design | Cheap to cover the other case |
|---|---|---|
| A1 — GitHub **Team** | Environment approval gates are unavailable on the private monorepo (3.1.2). **The approval gate is the PR merge to `main`, enforced by rulesets** (3.2.1–3.2.4): PR required, approvals, code-owner review, path-based team reviewers for `infra/**` and `.github/**`, dismiss stale approvals, approval after the last push, and an empty bypass list. The `production` environment is restricted to `main` (3.1.3). All the prerequisites in 3.6 #1 apply: only reviewed deploy workflows reference `production`, deploys take no ref input, and no privileged triggers are used. Admin edits are logged, not prevented. Drift detection is needed (3.1.4, 3.6 #1). | Create the `production` environment now, with the branch restriction. If Papaya moves to Enterprise Cloud, add required reviewers, prevent self-review, and disallow admin bypass on that environment. This is a settings change only; the workflows and the OIDC trust stay the same (inference). |
| A2 — immutable `sub` (with IDs) | AWS and GCP trust conditions must match `repo:<owner>@<owner-id>/<repo>@<repo-id>:environment:production` (inference from the documented `ref` examples), with placeholders in `examples/` (3.4.4). If the `sub` is customised with `job_workflow_ref` (3.4.5), the IDs stay in the `repo` segment and cannot be removed (3.4.4, oidc reference). | The org or repo can **opt in** to immutable subject claims (3.4.4). Opting in makes A2 true regardless of the repo's creation date. Accepting the old format as well would bring back the namespace-recycling risk, so it is not recommended. |
| A3 — worst case: the app is the PR author, and the person who triggered the agent can approve | The built-in "authors cannot approve" rule cannot be relied on (3.3.1, 3.3.4). Protected branches need **2 approvals**, at least on paths an agent can change, **or** a required status check whose **expected source app is pinned** (3.2.5, 3.3.4). The check fails when the approver is the person who triggered the agent run. "Allow GitHub Actions to create and approve pull requests" stays off (3.3.3), but that setting covers only `GITHUB_TOKEN`, not the Claude App's own token. **Worst case also covers the app approving:** whether an approval from a GitHub App counts toward required approvals is open (⚠️; only Copilot's is documented not to count, 3.3.1). The pinned check must therefore confirm **at least one approval from a human other than the person who triggered the agent**, rather than count approvals. Where configurable, the app gets no permission to approve PRs. Agent workflows never reference `production` (3.6 #4). | These rules still hold, and cost little, if the app turns out to attribute PRs to the human. |
| A4 — merge queue in use (**superseded 2026-11-08: no merge queue**; reference only) | Workflows that report required checks **must also trigger on `merge_group`**: "You **must** use the `merge_group` event to trigger your GitHub Actions workflow when a pull request is added to a merge queue" ([managing-a-merge-queue](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue), ✅). `merge_group` runs carry the merge-group ref (3.4.5c), so a `production` environment restricted to `main` does not serve them. That is the intended result, **provided the environment uses "Selected branches" with exactly `main`**: queue branches are named `gh-readonly-queue/main/…`, and "Protected branches only" or a broad pattern may behave differently (⚠️). Queue runs are CI only, and the deploy runs on `main` after the queue merges. PRs must pass the required protections before a user "can add the pull request to the queue" (same page, ✅). **What must be added for the gate:**<br>- (a) the A3 self-approval check, and every gate check, must also run on `merge_group` and evaluate **each PR in the group**. This means mapping the group back to its PRs and approvers (⚠️ design).<br>- (b) enable "Only merge non-failing pull requests". When it is off, "Pull requests that have failed required checks can be added to a group as long as the last pull request in the group has passed" (same page, ✅). That would let a PR that failed the self-approval check through.<br>- (c) turn on the "Require merge queue" setting. The queue page says it is "configured under branch protection rules or rulesets" ([about-protected-branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches), [managing-a-merge-queue](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue), ✅).<br>**Audit evidence:** with a queue, the queue performs the merge, so the "merged by" actor may not be the approver (⚠️ not verified). Evidence for Compliance should come from the review approvals and the add-to-queue event. ⚠️ Also not verified: that the queue's merge to `main` triggers `push` workflows as a normal merge does. | Adding `merge_group` triggers does no harm in a repo without a queue. |

**Conflict between A1 and A4. Resolved 2026-11-08 by the owner: keep Team, drop the merge queue.**
- The merge queue page says: "Pull request merge queues are available in any public repository
  owned by an organization, or in private repositories owned by organizations using GitHub
  Enterprise Cloud" (plan banner of
  [managing-a-merge-queue](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue),
  ✅).
- So on the **Team** plan, a **private** monorepo cannot use a merge queue. A1 and A4 cannot both
  hold.
- The design above works under either one, because nothing in it depends on the queue. The only
  difference is whether `merge_group` triggers are needed.

**Questions to ask Papaya if there is a chance** (the open items below remain open; the owner's
assumptions do not answer them):

- [ ] ⚠️ **Papaya's GitHub plan** (Team vs Enterprise Cloud). It decides 3.6 #1. *Design
      assumption: Team (A1); GĐ-5 updated accordingly on 2026-11-08.*
- [ ] ⚠️ On Team private repos, can admins bypass the environment branch restriction at run
      time, and is a UI change to the branch policy audited (3.1.4)? Are org-level rulesets available on Team (3.2.1, the docs contradict
      each other)?
- [ ] ⚠️ Which plans allow OIDC subject customisation (3.4.5), and whether Papaya's monorepo uses
      the old or the immutable `sub` format (3.4.4). *Design assumption: immutable (A2).*
- [ ] ⚠️ Audit-log streaming and its plan; meaning of `actor_is_agent` (3.5.6).
- [ ] ⚠️ How the Claude GitHub App attributes PRs and commits, whether the triggering human is
      recorded anywhere usable for a self-approval check, and whether an approval from a GitHub
      App counts toward required approvals (Copilot's does not, 3.3.1) (3.3.4). *Design
      assumption: worst case (A3).*
- [ ] ⚠️ Does Papaya use a merge queue? (`merge_group` runs carry the merge-group ref, 3.4.5c.)
      *Design assumption: no merge queue (owner decision 2026-11-08, A4 superseded).*
- [ ] ⚠️ Does sudo exist on single-CPU hosted runners (3.5.1)?

### 3.8 Review log (Topic 3)

- **Round 1 (2026-11-08)**, independent reviewer subagent. It checked every quote and plan banner
  against the GitHub pages, and fetched more pages itself (creating rulesets, OIDC with reusable
  workflows, merge queue, Google's WIF for deployment pipelines).
  - Result: 1 HIGH, 3 MEDIUM, 10 LOW, 6 coverage gaps.
  - I re-checked the HIGH and the MEDIUM items against the raw pages: the `GITHUB_REF` table, the
    `pull_request_target` context, the status-check source, Google's "must use an attribute
    condition", and "custom claims … available for Google Cloud". All were accepted.
  - The HIGH: "only merged, approved code can get prod credentials" ignored privileged triggers
    on `main`. Fixed with 3.4.5c and the prerequisites in 3.6 #1.
  - The MEDIUM fixes: a pinned status-check source (3.3.4), the admin edit gap (3.2.2, 3.6 #1),
    and the GCP row (3.4.5b).
  - All LOW items and the gaps are fixed or moved to 3.7.
- **Round 2 (2026-11-08)**, same reviewer:
  - Round 1: 13 findings FIXED, 1 PARTLY.
  - New: 0 HIGH, 1 MEDIUM, 4 LOW. I verified the MEDIUM against the raw pages:
    `environment.update_protection_rule` is "via the API" only, and a missing environment is
    recreated when a workflow references it.
  - Fixed:
    - 3.1.4: audit coverage and the recreation risk;
    - 3.6 #1: alerts plus a drift check;
    - 3.2.2: source and inference label;
    - 3.4.5b: inference label;
    - repository secrets moved to their own row, 3.5.3b;
    - `schedule` added to the trigger list.
- **Round 3 (2026-11-08)**, same reviewer:
  - Round 2: 5/5 FIXED.
  - New: 0 HIGH, 0 MEDIUM, 3 LOW (wording in 3.6 #1, the unresearched REST drift check, the
    3.4.5b marker). All fixed.
  - **Topic 3 closed** (no HIGH/MEDIUM).
- **Owner assumptions (2026-11-08):** the repo owner (the user) set four design assumptions for the
  3.7 questions: Team plan, immutable `sub`, worst-case app authorship, merge queue in use.
  - They are recorded verbatim in 3.7 and marked as assumptions, not facts about Papaya.
  - I added their design consequences, with "cheap to cover the other case" notes.
  - I read the merge queue plan banner (✅). It shows that A1 and A4 conflict for a private repo.
    The conflict is flagged for the owner; neither assumption was changed.
  - No conclusion in 3.1–3.6 is made wrong by the assumptions; 3.1–3.6 are unchanged.
  - GĐ-5 in `work/01-problem-framing.md` was updated to the Team assumption.
  - Review (fresh independent reviewer subagent): 0 HIGH, 2 MEDIUM, 5 LOW. Both MEDIUM items were
    verified against the merge queue page and accepted:
    - A4: gate checks must run per PR on `merge_group`, enable "Only merge non-failing pull
      requests", and the "Require merge queue" rule;
    - A3: the worst case includes the app's own approval being counted, so the check verifies a
      human approver other than the triggering person.
  - LOW items fixed: the A2 inference label, the A4 "Selected branches: `main`" note and the
    merged-by caveat, the GĐ-5 inference label, and the open-item status.
  - The reviewer also suggested adding "(done)" to 3.6 #1. **Not applied**, because the owner said
    not to modify 3.1–3.6. The 3.6 #1 conclusion is still correct; its action (correct GĐ-5) is
    now done.
  - Round 2: all findings FIXED (L2 deliberately not applied); 1 new LOW (source for "Require
    merge queue"), fixed. 0 HIGH/MEDIUM: closed.
- **Formatting fix (2026-11-08):** 17 table rows in Topics 2–3 had cells spread over several lines,
  which breaks Markdown tables. The lines were joined with `<br>`. Check: Topic 2, normalised for
  `<br>` and whitespace, is text-identical to commit `b61a0cf`. No wording changed.
- **Owner decision (2026-11-08):** on the A1/A4 conflict, the owner (the user) chose "Giữ Team và
  bỏ merge queue". It is recorded verbatim in 3.7. A4 is marked superseded, and its row is kept as
  reference only. GĐ-5's note was updated.
