# Rulesets of the plugin marketplace repository (OD26)

The marketplace repository `example-org/claude-plugins` decides what runs on every engineer's
laptop: a merged plugin change reaches all of them once the managed settings point at it. So it
gets stricter rules than the monorepo [design]:

| File | Rule |
|---|---|
| `ruleset-default-branch.json` | Every change is a PR with **two** approvals from code owners (the L3 owner team), stale approvals dismissed, approval by someone other than the last pusher, squash only, `plugin-validate` required, nobody bypasses |
| `ruleset-release-tags-immutable.json` | Release tags `v*` can never be moved or deleted, by anyone |
| `ruleset-release-tags-creation.json` | Only the L3 owner team (`actor_id` `234567` is a placeholder team ID) may create a release tag. A separate ruleset because a bypass actor bypasses every rule of its ruleset |

Managed settings pin the marketplace to one release tag (`ref`, 📖 R9.4.4: marketplace sources
take a `ref`, not a `sha`), and every plugin entry carries its own `sha` (📖 R9.4.5). A new release
is therefore three reviewed steps: plugin change (two approvals), a new tag (L3 owner team), and a
managed-settings change of `ref` (console, compared with git monthly, layer 2).

Not proven here: that GitHub enforces these rules (no repository was touched). Tag rulesets are
validated against the REST schema only.
