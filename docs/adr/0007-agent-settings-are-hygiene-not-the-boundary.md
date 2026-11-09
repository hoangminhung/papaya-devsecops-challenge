# ADR-0007: Claude Code managed settings are hygiene, not the security boundary

- **Status:** Accepted; refined after the independent review (see [ADR index](README.md), "refinements": `gh` deny rules OD25, cloud CLI `ask` rules from phase 1 OD43)
- **Date:** 2026-11-09
- **Decided by:** owner of this submission (GĐ-6, Options §0.4; D1, D3; OD4, OD7b, OD12)
- **Scope:** Claude Code on laptops (server-managed settings, Team plan) and in CI

## 1. Context

The brief names "permission prompts turned off" as a problem. It is tempting to make Claude Code
settings the main control. But server-managed settings are "a client-side control, not a security
boundary" (📖 R1.1.7), local admins can edit endpoint files (📖 R1.1.8), Bash rules are not a boundary
(📖 R1.2.6), and on laptops without MDM another login or provider skips server-managed settings
(📖 R1.1.7; ⚠️ G11).

## 2. Options considered

| Option | Pros | Cons |
|---|---|---|
| 0. Today (brief): some engineers turn prompts off; no organization policy is described (P3c) | No friction | Prompts turned off unnoticed; no evidence |
| A. Settings as the boundary (lock everything, block auto mode) | Simple story | Bypassable on laptops; high friction; people work around it |
| B. Settings as hygiene; IAM and the CI gate as the boundary | Boundary holds even if settings are bypassed | Settings give weaker guarantees than they appear to |

## 3. Decision

Option B. The boundary is IAM (ADR-0002) and the merge gate (ADR-0003). Managed settings set safe,
uniform defaults:

- `permissions.defaultMode` = `"default"` (Manual), with a read-only allowlist that excludes `aws`, `pulumi`,
  `serverless` (D1, OD7b; 📖 R6.9.3); auto mode stays available and is measured.
- `permissions.disableBypassPermissionsMode: "disable"` (📖 R1.2.2); `requiredMinimumVersion` floor (📖 R1.1.13).
- Sandbox with `~/.aws` hidden (📖 R1.6.3, R1.6.4) [design]; `aws`, `pulumi`, `serverless` in
  `sandbox.excludedCommands` [design]; `sandbox.autoAllowBashIfSandboxed` kept `true` (OD12, 📖 R5.5.5b).
- OTel exporter without prompt content (📖 R1.1.20, R5.5.4).

Outside managed settings: the `--restricted` flag (📖 R6.9.1b) in CI, set in the workflow file under
CODEOWNERS, and, as a process rule, in the incident-analysis session; a setting cannot force it
(📖 R6.9.1) (D3).

Phase 1 ships `defaultMode`, the allowlist, bypass removal, the catalogue keys, the version floor and
OTel; the rest of the baseline follows in phase 2 (OD4).

## 4. Consequences

- **Positive:** a bypassed or misconfigured agent still cannot write prod or read AWS PHI
  stores with the engineer's standing identity, once standing write is removed (PHI paths outside IAM
  are process-only, ADR-0009). Compliance gets
  one organization policy with evidence instead of personal choices.
- **Negative / trade-offs:** more prompts than auto mode; a prompt for every `aws` read. S5
  ("nobody can turn off all prompts unnoticed") is met only on laptops with MDM and reported as not
  met elsewhere (OD54).
- **Risks & how we watch them:** the auto-mode classifier missed 17 % of 52 real overeager actions
  (📖 R6.3.5); fallback to `disableAutoMode` (📖 R1.2.2) if the planted-injection test steers it (D1). The live
  settings are edited in the admin console, not by PR (📖 R1.1.5); an Owner exports them monthly and
  diffs them with git until a better method exists (G18).
  Until phase 2 there is no sandbox: `~/.aws` is readable and the network open; in auto mode the
  classifier is the only gate. `aws`, `pulumi`, `serverless` run outside the sandbox even later
  (📖 R1.6.4; ⚠️ inference): repo code that the agent can edit (Pulumi programs, Serverless
  plugins) then runs with network and `~/.aws`, and SSO-token theft remains possible; bounded by
  ADR-0002. With OD12, Manual mode does not mean a prompt for every command (📖 R5.5.5b).
- **Next steps:** phase-1 subset; planted-injection test in phase 3.

## 5. References

- Framework layer 2; layer 8 rollout; research 6.6 (D1–D3).
- Related: ADR-0002, ADR-0006.
