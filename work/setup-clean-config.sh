#!/usr/bin/env bash
# Build a clean Claude Code config directory for this challenge.
# Why: session transcripts are submitted unedited and contain the system prompt,
# which lists every loaded rule, skill, plugin and claude.ai connector. The default
# ~/.claude on this machine pulls skills/plugins/connectors from the owner's
# employer claude.ai account. This directory keeps only the DevOps kit.
#
# Run it yourself (the coding agent was not allowed to: installing hooks and
# permission rules is classified as a security-weakening action):
#   bash work/setup-clean-config.sh
# Then start sessions with:
#   CLAUDE_CONFIG_DIR="$HOME/.claude-papaya" claude
# The first start asks you to log in again: credentials live inside the config dir.
set -euo pipefail

CFG="$HOME/.claude-papaya"
KIT="$HOME/devops-ai-kit"

mkdir -p "$CFG"

# 1. DevOps kit (rules, hooks, skills, agents, permission deny/ask/allow rules). Honors CLAUDE_CONFIG_DIR.
CLAUDE_CONFIG_DIR="$CFG" "$KIT/install.sh" --lang vi --env DEVOPS_KIT_BLOCK_PROD=0

# 2. Personal global instructions (reviewed: no org, customer or secret data).
cp "$HOME/.claude/CLAUDE.md" "$CFG/CLAUDE.md"

# 3. Retention, privacy and permission-mode settings.
python3 -I - "$CFG/settings.json" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d["$schema"] = "https://json.schemastore.org/claude-code-settings.json"
d["cleanupPeriodDays"] = 365            # keep transcripts; default is 30 days
d["syncClaudeAiSkills"] = False         # do not load skills from the claude.ai account
d["syncClaudeAiPlugins"] = False        # do not load plugins from the claude.ai account
d["disableClaudeAiConnectors"] = True   # do not fetch claude.ai MCP connectors
d.setdefault("permissions", {})["defaultMode"] = "default"  # keep permission prompts on
d["model"] = "fable"
d["effortLevel"] = "xhigh"
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
print("settings.json updated:", sorted(k for k in d if k != "permissions"))
PY

# 4. Re-check that nothing from the employer account leaked into the new directory.
echo -n "leak re-check (expect 0): "
grep -rIoE 'sun-asterisk|Sun\*|Apollo|ShopSense|DocMind|tekai' "$CFG" | wc -l

echo "Done. Start with: CLAUDE_CONFIG_DIR=$CFG claude"
