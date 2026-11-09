"""E8 managed settings (phase 1 and phase 2) and E9 plugin marketplace.

Settings: validated against the community JSON Schema from schemastore.org (not an official
Anthropic source) and checked key by key, because that schema accepts unknown keys. Keys the
schema lacks are allowed only with a documentation source. Then the design rules of framework
layers 2, 4 and 8 (D1, OD4, OD7b, OD12).

Marketplace: `claude plugin validate` (run by validate.sh) checks the manifest and fails on an
invalid entry (✅ 2.1.319), but it accepts an unpinned `github` source and a `command` source
(✅ mutation). These tests check what it does not: every external source is pinned.

Not checked: what Claude Code does with the files. Server-managed settings are edited in the
admin console; these files are the expected copy kept in git (layer 8).
"""
import json
import os
import re
import unittest

from schema_keys import unknown_keys

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")


def load(*parts):
    with open(os.path.join(ROOT, *parts)) as f:
        return json.load(f)


SCHEMA = load("schemas", "claude-code-settings.schemastore.json")
# Keys missing from the schema, each with its documentation source.
DOCUMENTED_EXTRA_KEYS = {
    "$.allowedProviders": "R1.1.15 (settings docs); also in Anthropic's settings-hipaa.json",
    "$.crossSessionInbound": "settings-reference#crosssessioninbound; in settings-hipaa.json",
    "$.syncClaudeAiPlugins": "settings-reference#syncclaudeaiplugins; in settings-hipaa.json",
    "$.syncClaudeAiSkills": "settings-reference#syncclaudeaiskills; in settings-hipaa.json",
}
# Tool names the schema's rule pattern lacks, each with its documentation source.
DOCUMENTED_EXTRA_TOOLS = {
    "SendUserFile": "tools-reference (SendUserFile row); in settings-hipaa.json",
    "Projects": "README-hipaa.md, permissions row: 'file uploads to a claude.ai project'",
}
# Lists of Anthropic's settings-hipaa.json (commit 9196319) that phase 2 keeps (README, "E8:
# deviations from the HIPAA template"); WebFetch is the one documented removal from `deny`.
TEMPLATE_DENY = [
    "Projects", "SendUserFile", "ShareOnboardingGuide", "Artifact",
    "Read(~/.ssh/**)", "Read(~/.aws/**)", "Read(~/.config/gh/**)", "Read(~/.npmrc)",
    "Read(~/.claude/.credentials.json)", "Read(~/.claude.json)", "Read(~/.claude.json.backup*)",
    "Read(~/.claude/backups/**)", "Read(~/.git-credentials)", "Read(~/.config/git/credentials)",
    "Read(~/.netrc)", "Read(~/_netrc)",
    "Edit(~/.ssh/**)", "Edit(~/.aws/**)", "Edit(~/.config/gh/**)", "Edit(~/.npmrc)",
    "Edit(~/.claude/.credentials.json)", "Edit(~/.claude.json)", "Edit(~/.claude.json.backup*)",
    "Edit(~/.claude/backups/**)", "Edit(~/.git-credentials)", "Edit(~/.config/git/credentials)",
    "Edit(~/.netrc)", "Edit(~/_netrc)",
]
TEMPLATE_CRED_FILES = ["~/.ssh", "~/.npmrc", "~/.git-credentials", "~/.config/git/credentials", "~/.netrc",
                       "~/_netrc", "~/.claude/.credentials.json", "~/.claude.json", "~/.claude.json.backup*",
                       "~/.claude/backups"]  # plus ~/.aws/credentials, covered by the whole ~/.aws
TEMPLATE_ENV_VARS = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "GITHUB_TOKEN",
                     "GH_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN", "NPM_TOKEN",
                     "NODE_AUTH_TOKEN", "YARN_NPM_AUTH_TOKEN", "YARN_NPM_AUTH_IDENT", "COREPACK_NPM_TOKEN",
                     "COREPACK_NPM_PASSWORD", "COREPACK_NPM_USERNAME", "BUN_CONFIG_TOKEN",
                     "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"]
TEMPLATE_DENY_WRITE = ["~/.ssh", "~/.npmrc", "~/.git-credentials", "~/.config/git/credentials", "~/.netrc",
                       "~/_netrc", "~/.claude/.credentials.json", "~/.claude.json", "~/.claude.json.backup*",
                       "~/.claude/backups"]  # plus ~/.aws/credentials and ~/.aws/config: whole ~/.aws
# Directories: deny rules must cover everything below them.
CRED_DIRS = {"~/.ssh", "~/.aws", "~/.config/gh", "~/.config/gcloud", "~/.kube", "~/.pulumi", "~/.claude/backups"}
# Framework layer 8, phase-1 subset of managed settings (top-level keys).
PHASE1_KEYS = {
    "requiredMinimumVersion", "permissions", "strictKnownMarketplaces", "blockedMarketplaces",
    "disableSideloadFlags", "allowManagedMcpServersOnly", "allowedMcpServers",
    "disableClaudeAiConnectors", "env",
    "autoMode",  # OD21
    "extraKnownMarketplaces",  # OD26: marketplace pinned to a release tag, auto-update off
    "enabledPlugins",  # framework §2: the internal skills load in every session, --restricted too
}
# OD26: the marketplace is pinned to one release tag (📖 R9.4.4: `ref`, no `sha` field).
MARKETPLACE = {"source": "github", "repo": "example-org/claude-plugins", "ref": "v2026.11.0"}
# OD25: hygiene against an agent approving through its engineer's login (📖 R9.4.1: valid
# patterns, not a boundary; `bash -c` or `curl` to the API are not matched).
REVIEW_DENIES = ["Bash(gh pr review *)", "Bash(gh api *reviews*)"]
# Entries use Bash rule syntax; without a trailing " *" an entry matches only the bare command
# with no arguments (📖 sandboxing#run-commands-outside-the-sandbox-with-excludedcommands).
# `sls` is the Serverless CLI's short alias, and `npx` is how the CLIs are often run from a
# repository (grading round after OD52, #8): each form needs its own rule.
CLOUD_CLIS = ["aws *", "pulumi *", "serverless *", "sls *", "npx pulumi *", "npx serverless *", "npx sls *"]
EXCLUDED_FROM_SANDBOX = CLOUD_CLIS
# The only allow rules: exact repo scripts. Read-only git, cat, grep etc. are already in Claude
# Code's built-in read-only set (📖 permissions#read-only-commands); `git log/show/diff *` rules
# would also match `--output=<path>`, which writes any file (✅ git 2.34.1).
ALLOWED = ["Bash(npm test)", "Bash(npm run lint)"]
OTEL_CONTENT_FLAGS = ["OTEL_LOG_USER_PROMPTS", "OTEL_LOG_ASSISTANT_RESPONSES", "OTEL_LOG_TOOL_DETAILS",
                      "OTEL_LOG_TOOL_CONTENT", "OTEL_LOG_RAW_API_BODIES"]


def version(v):
    return tuple(int(x) for x in v.split("."))


class SettingsCommon:
    FILE = None

    @classmethod
    def setUpClass(cls):
        cls.s = load("claude", cls.FILE)

    def test_schema_and_known_keys(self):
        import copy
        import jsonschema
        checked = copy.deepcopy(self.s)
        deny = checked["permissions"].get("deny", [])
        checked["permissions"]["deny"] = [r for r in deny if r not in DOCUMENTED_EXTRA_TOOLS]
        jsonschema.validate(checked, SCHEMA)
        self.assertEqual(unknown_keys(self.s, SCHEMA, allow=set(DOCUMENTED_EXTRA_KEYS)), [])

    def test_manual_mode_default_bypass_off_auto_kept(self):
        p = self.s["permissions"]
        self.assertEqual(p["defaultMode"], "default")             # D1: Manual by default
        self.assertEqual(p["disableBypassPermissionsMode"], "disable")
        self.assertNotIn("disableAutoMode", p)                    # D1: auto stays available

    def test_allowlist_is_exact_repo_scripts_only(self):
        allow = self.s["permissions"]["allow"]
        self.assertEqual(allow, ALLOWED)
        for rule in allow:
            with self.subTest(rule=rule):
                body = re.fullmatch(r"Bash\((.+)\)", rule).group(1)
                self.assertNotIn("*", body, "wildcards match arguments nobody reviewed")
                self.assertNotIn(body.split()[0], [e.split()[0] for e in EXCLUDED_FROM_SANDBOX])

    def test_catalogue_enforced(self):
        self.assertEqual(self.s["strictKnownMarketplaces"], [MARKETPLACE])
        [(name, entry)] = self.s["extraKnownMarketplaces"].items()
        self.assertEqual(entry, {"source": MARKETPLACE, "autoUpdate": False})  # 📖 R9.4.6
        self.assertIs(self.s["disableSideloadFlags"], True)
        self.assertIs(self.s["allowManagedMcpServersOnly"], True)
        self.assertIs(self.s["disableClaudeAiConnectors"], True)

    def test_mcp_entries_match_by_url_or_pinned_command_never_name(self):
        for e in self.s["allowedMcpServers"]:
            with self.subTest(entry=e):
                self.assertEqual(len(e), 1, "each entry has exactly one key (settings reference)")
                self.assertNotIn("serverName", e)  # "not a security control" (R1.3.3)
                if "serverCommand" in e:
                    # OD26: a local server is an immutable artifact: a container image by digest,
                    # not `npx -y pkg@x`, whose dependencies float. Exact argv (📖 R9.4.2).
                    cmd = e["serverCommand"]
                    self.assertEqual(cmd[:4], ["docker", "run", "--rm", "-i"])
                    self.assertRegex(cmd[-1], r"^[a-z0-9.-]+/[a-z0-9./-]+@sha256:[0-9a-f]{64}$")
                    self.assertEqual(len(cmd), 5, "no further arguments, mounts or env")
                else:
                    self.assertRegex(e["serverUrl"], r"^https://[a-z0-9.-]+\.[a-z]+/", "exact host")

    def test_agent_cannot_approve_through_gh(self):
        deny = self.s["permissions"]["deny"]
        for rule in REVIEW_DENIES + ["Read(~/.config/gh/**)"]:
            self.assertIn(rule, deny)

    def test_telemetry_on_without_content(self):
        env = self.s["env"]
        self.assertEqual(env["CLAUDE_CODE_ENABLE_TELEMETRY"], "1")
        for flag in OTEL_CONTENT_FLAGS:
            self.assertEqual(env[flag], "0", flag)


class Phase1Test(SettingsCommon, unittest.TestCase):
    FILE = "managed-settings.phase1.json"

    def test_only_the_phase1_subset(self):
        self.assertEqual(set(self.s), PHASE1_KEYS)  # framework layer 8; the rest is phase 2 (OD4)

    def test_version_floor(self):
        self.assertGreaterEqual(version(self.s["requiredMinimumVersion"]), version("2.1.248"))

    def test_od21_aws_reads_denied_and_allow_rules_classified(self):
        # Built-in read-only commands (cat, head, ...) run without a prompt in every mode; a Read
        # deny rule also applies to recognized cat/head/tail (📖 permissions). classifyAllShell
        # (📖, >= 2.1.193) keeps the two allow rules from skipping the auto-mode classifier.
        # OD25 adds the GitHub CLI token and the review commands from phase 1.
        self.assertEqual(self.s["permissions"]["deny"], ["Read(~/.aws/**)", "Read(~/.config/gh/**)"] + REVIEW_DENIES)
        self.assertEqual(self.s["autoMode"], {"classifyAllShell": True})

    def test_cloud_cli_prompts_until_standing_write_is_gone(self):
        # OD43: until 1.16 removes standing prod write, an engineer's SSO session can still write
        # to prod, and auto mode is allowed (D1). A content-scoped ask rule prompts in auto mode
        # too (📖 auto-mode-config, permissions.ask). WebFetch's ask waits for phase 2.
        self.assertEqual(self.s["permissions"]["ask"], [f"Bash({c})" for c in CLOUD_CLIS])


class Phase2Test(SettingsCommon, unittest.TestCase):
    FILE = "managed-settings.phase2.json"

    def test_contains_phase1(self):
        p1 = load("claude", "managed-settings.phase1.json")
        for k, v in p1.items():
            if k in ("requiredMinimumVersion", "permissions"):
                continue
            if k == "autoMode":
                self.assertLessEqual(v.items(), self.s[k].items())
                continue
            if k == "env":  # phase 2 adds the template's opt-outs; phase-1 values stay
                self.assertLessEqual(v.items(), self.s[k].items())
                continue
            self.assertEqual(self.s[k], v, k)
        self.assertEqual(self.s["permissions"]["allow"], p1["permissions"]["allow"])
        self.assertLessEqual(set(p1["permissions"]["deny"]), set(self.s["permissions"]["deny"]))
        self.assertLessEqual(set(p1["permissions"]["ask"]), set(self.s["permissions"]["ask"]))
        self.assertEqual(self.s["permissions"]["defaultMode"], p1["permissions"]["defaultMode"])
        self.assertEqual(self.s["permissions"]["disableBypassPermissionsMode"],
                         p1["permissions"]["disableBypassPermissionsMode"])

    def test_allow_rules_do_not_skip_classifier_and_defaults_pinned(self):
        # Without classifyAllShell, a command an allow rule matches skips the auto-mode classifier
        # (📖). Sandboxed commands are still auto-approved (OD12): for them the sandbox is the control.
        am = self.s["autoMode"]
        self.assertIs(am["classifyAllShell"], True)
        # Without "$defaults", a developer's own list replaces the built-in rules, the data
        # exfiltration rule included (📖 auto-mode-config)
        for section in ("environment", "soft_deny", "hard_deny", "allow"):
            if section in am or section != "allow":
                self.assertIn("$defaults", am[section], section)

    def test_template_lists_kept(self):
        p, sb = self.s["permissions"], self.s["sandbox"]
        self.assertLessEqual(set(TEMPLATE_DENY) - {"WebFetch"}, set(p["deny"]))
        files = {f["path"] for f in sb["credentials"]["files"] if f["mode"] == "deny"}
        self.assertLessEqual(set(TEMPLATE_CRED_FILES) | {"~/.aws"}, files)
        envs = {e["name"] for e in sb["credentials"]["envVars"] if e["mode"] == "deny"}
        self.assertLessEqual(set(TEMPLATE_ENV_VARS), envs)
        self.assertLessEqual(set(TEMPLATE_DENY_WRITE) | {"~/.aws"}, set(sb["filesystem"]["denyWrite"]))
        for d in CRED_DIRS:
            for tool in ("Read", "Edit"):
                self.assertIn(f"{tool}({d}/**)", p["deny"], "a directory rule must cover all of it")

    def test_unsandboxed_cli_runs_always_prompt(self):
        # Excluded commands skip the sandbox; in auto mode the classifier alone would decide.
        # A content-scoped ask rule always prompts (📖 auto-mode-config, permissions.ask).
        for e in EXCLUDED_FROM_SANDBOX:
            self.assertIn(f"Bash({e})", self.s["permissions"]["ask"])

    def test_hipaa_template_hardening_kept(self):
        s = self.s
        self.assertIs(s["forceRemoteSettingsRefresh"], True)
        self.assertEqual(s["forceLoginMethod"], "claudeai")
        self.assertEqual(s["allowedHttpHookUrls"], [])
        self.assertEqual(s["skillOverrides"], {"auto-mode-setup": "off"})
        self.assertEqual(s["cleanupPeriodDays"], 30)
        self.assertEqual(s["crossSessionInbound"], "refuse")
        self.assertIs(s["enableArtifact"], False)
        self.assertIs(s["disableRemoteControl"], True)
        self.assertIs(s["syncClaudeAiPlugins"], False)
        self.assertIs(s["syncClaudeAiSkills"], False)
        # Built-in servers are exempt from allowedMcpServers; only the denylist reaches them.
        names = {e["serverName"] for e in s["deniedMcpServers"]}
        self.assertLessEqual({"claude-in-chrome", "computer-use"}, names)
        for tool in ("Projects", "SendUserFile", "ShareOnboardingGuide", "Artifact"):
            self.assertIn(tool, s["permissions"]["deny"])

    def test_version_floor(self):
        # 2.1.285: allowedProviders; 2.1.310: allowManagedHooksOnly also blocks monitors of
        # plugins that are not force-enabled (📖 settings reference)
        self.assertGreaterEqual(version(self.s["requiredMinimumVersion"]), version("2.1.310"))

    def test_login_and_provider_locked(self):
        self.assertEqual(self.s["allowedProviders"], ["anthropic"])
        self.assertIn("forceLoginOrgUUID", self.s)

    def test_managed_only_rules_hooks_mods(self):
        self.assertIs(self.s["allowManagedPermissionRulesOnly"], True)
        self.assertIs(self.s["allowManagedHooksOnly"], True)
        opts = self.s["pluginConfigs"]["cc-plugin-sec-default@builtin"]["options"]
        self.assertIs(opts["allowManagedModsOnly"], True)  # R1.5.6

    def test_credentials_denied_and_webfetch_asks(self):
        p = self.s["permissions"]
        self.assertIn("Read(~/.aws/**)", p["deny"])
        self.assertEqual(p["ask"][0], "WebFetch")  # deliberate deviation from the HIPAA template
        self.assertNotIn("WebFetch", p["deny"])

    def test_sandbox(self):
        sb = self.s["sandbox"]
        self.assertIs(sb["enabled"], True)
        self.assertIs(sb["failIfUnavailable"], True)
        self.assertIs(sb["allowUnsandboxedCommands"], False)
        self.assertIs(sb["autoAllowBashIfSandboxed"], True)  # OD12
        self.assertEqual(sb["excludedCommands"], EXCLUDED_FROM_SANDBOX)
        for e in sb["excludedCommands"]:
            self.assertTrue(e.endswith(" *"), f"{e!r} would match only the bare command")
        self.assertIs(sb["enableWeakerNestedSandbox"], False)
        self.assertIs(sb["enableWeakerNetworkIsolation"], False)
        net = sb["network"]
        self.assertIs(net["allowManagedDomainsOnly"], True)
        self.assertIs(net["allowAllUnixSockets"], False)
        self.assertIs(net["allowLocalBinding"], False)
        self.assertIn("~/.aws", sb["filesystem"]["denyRead"])
        # It only filters allowRead (none here) and would stop blockReadsOutsideWorkingDirectories
        # from reaching sandboxed commands (📖 settings reference).
        self.assertNotIn("allowManagedReadPathsOnly", sb["filesystem"])
        self.assertNotIn("allowRead", sb["filesystem"], "would re-open part of a denied path")
        for d in net["allowedDomains"]:
            self.assertNotIn("*", d, "each allowed domain is an exfiltration path; name hosts")

    def test_sandbox_hides_every_credential_of_the_stack(self):
        # Sandboxed commands run without a prompt (OD12), so a credential the sandbox can read is
        # usable by the agent: e.g. the gh token can approve PRs as the engineer (OD5).
        sb = self.s["sandbox"]
        denied = {f["path"] for f in sb["credentials"]["files"] if f["mode"] == "deny"}
        for path in ("~/.aws", "~/.ssh", "~/.config/gh", "~/.config/gcloud", "~/.kube", "~/.pulumi",
                     "~/.docker/config.json", "~/.config/configstore/firebase-tools.json",
                     "~/.npmrc", "~/.git-credentials", "~/.config/git/credentials", "~/.netrc",
                     "~/.claude/.credentials.json", "~/.claude.json", "~/.serverlessrc"):
            with self.subTest(path=path):
                self.assertIn(path, denied)
                self.assertIn(path, sb["filesystem"]["denyWrite"])
                for tool in ("Read", "Edit"):
                    self.assertTrue(any(r.startswith(f"{tool}({path}") for r in self.s["permissions"]["deny"]))
        envs = {e["name"] for e in sb["credentials"]["envVars"] if e["mode"] == "deny"}
        self.assertLessEqual({"AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "GH_TOKEN", "GITHUB_TOKEN",
                              "PULUMI_ACCESS_TOKEN", "PULUMI_CONFIG_PASSPHRASE", "FIREBASE_TOKEN",
                              "SERVERLESS_ACCESS_KEY"}, envs)


class MarketplaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load("claude", "marketplace", ".claude-plugin", "marketplace.json")

    def test_every_external_source_is_pinned(self):
        for p in self.m["plugins"]:
            src = p["source"]
            with self.subTest(plugin=p["name"]):
                # OD26: internal plugins too. A relative "./plugins/x" source follows whatever the
                # marketplace's files are, so it is not allowed (📖 R9.4.5: `sha` pins a plugin).
                self.assertIsInstance(src, dict, "relative sources are not pinned")
                kind = src["source"]
                self.assertIn(kind, ("github", "url", "git-subdir", "npm", "archive"),
                              "command sources run code on the laptop to find the plugin")
                if kind in ("github", "url", "git-subdir"):
                    self.assertRegex(src.get("sha", ""), r"^[0-9a-f]{40}$")
                elif kind == "npm":
                    # `version` counts only when `package` has no version or URL of its own
                    # (📖 marketplace reference); a foreign registry is not reviewed.
                    self.assertRegex(src["package"], r"^(@[a-z0-9-]+/)?[a-z0-9.-]+$")
                    self.assertRegex(src.get("version", ""), r"^\d+\.\d+\.\d+$")
                    self.assertNotIn("registry", src)
                else:
                    self.assertRegex(src.get("sha256", ""), r"^[0-9a-fA-F]{64}$")

    def test_every_entry_has_a_review_record(self):
        reviews = os.listdir(os.path.join(ROOT, "claude", "marketplace", "reviews"))
        for p in self.m["plugins"]:  # internal entries included (OD26)
            with self.subTest(plugin=p["name"]):
                self.assertIn(f"{p['name']}.md", reviews)

    def test_internal_skills_and_review_record_agree(self):
        # Framework §2: every skill has a name matching its folder and a description; the review
        # record lists every skill, so a new skill cannot reach laptops unreviewed (OD26).
        base = os.path.join(ROOT, "claude", "marketplace", "plugins", "devsecops-guardrails", "skills")
        with open(os.path.join(ROOT, "claude", "marketplace", "reviews", "devsecops-guardrails.md")) as f:
            record = f.read()
        skills = sorted(os.listdir(base))
        self.assertGreaterEqual(len(skills), 4)
        for name in skills:
            with self.subTest(skill=name):
                with open(os.path.join(base, name, "SKILL.md")) as f:
                    text = f.read()
                front = text.split("---")[1]
                self.assertIn(f"name: {name}\n", front)
                self.assertRegex(front, r"description: \S")
                self.assertIn(f"`{name}`", record)
                self.assertRegex(text, r"(?i)never (approve|change production|run)|do not approve|approved by")


class ForceEnabledPluginTest(unittest.TestCase):
    """Framework §2: `--restricted` ignores user, project and local settings (✅ claude --help
    2.1.319), so the internal skills reach the incident-analysis session only if managed settings
    force-enable the plugin (📖 R1.4.2, R9.4.7: managed `enabledPlugins: true`)."""

    def test_internal_plugin_force_enabled_in_both_phases(self):
        m = load("claude", "marketplace", ".claude-plugin", "marketplace.json")
        for f in ("managed-settings.phase1.json", "managed-settings.phase2.json"):
            s = load("claude", f)
            with self.subTest(file=f):
                self.assertEqual(s["enabledPlugins"], {f"devsecops-guardrails@{m['name']}": True})


class CiAgentSettingsTest(unittest.TestCase):
    """Layer 5: the managed settings the CI review agent runs under (installed from the base
    branch, E18): no Bash, no web, no edits, no MCP server, telemetry without content."""

    def test_ci_agent_settings(self):
        s = load("claude", "ci-managed-settings.json")
        import jsonschema
        jsonschema.validate(s, load("schemas", "claude-code-settings.schemastore.json"))
        self.assertEqual(set(s["permissions"]["deny"]), {"Bash", "WebFetch", "Edit", "Write"})
        self.assertEqual(s["allowedMcpServers"], [])
        self.assertTrue(s["allowManagedMcpServersOnly"] and s["allowManagedHooksOnly"])
        for flag in ("OTEL_LOG_USER_PROMPTS", "OTEL_LOG_TOOL_DETAILS"):
            self.assertEqual(s["env"][flag], "0")


class RepoTemplatesTest(unittest.TestCase):
    """Framework §2: the shared CLAUDE.md and the PR template carry the rules the agents need."""

    def test_claude_md_template(self):
        with open(os.path.join(ROOT, "claude", "repo-templates", "CLAUDE.md")) as f:
            t = f.read()
        for needle in ("Never approve a pull request", "data-fixes/<tenant>/", "prod-change", "synthetic"):
            self.assertIn(needle, t)

    def test_pr_template_asks_about_agents_data_and_rollback(self):
        with open(os.path.join(ROOT, "github", "pull_request_template.md")) as f:
            t = f.read()
        for needle in ("Written with an agent", "Data:", "Rollback", "incident"):
            self.assertIn(needle, t)


if __name__ == "__main__":
    unittest.main()
