# Diagrams

Source in Mermaid (`.mmd`), rendered to `.svg` with `mmdc` (✅ @mermaid-js/mermaid-cli 11.12.0):
`mmdc -i <name>.mmd -o <name>.svg -b white`. Each diagram shows only what the cited text says; if they
differ, the text wins.

| Diagram | Shows | Source text |
|---|---|---|
| [01-change-workflow](01-change-workflow.svg) | Risk levels, who approves which path, the merge gate, the deploy job and the risk-stop approval loop | [Framework layer 3](../docs/01-framework.md#layer-3--change-workflow-by-risk-level) |
| [02-identity-trust-boundaries](02-identity-trust-boundaries.svg) | The laptop as one trust zone (engineer and agent share the SSO cache), GitHub as the approval gate, prod roles, SCPs and the audit store | [Layer 1](../docs/01-framework.md#layer-1--identity-and-access), [layer 2](../docs/01-framework.md#layer-2--agent-runtime-controls), [layer 7](../docs/01-framework.md#layer-7--observability-audit-incident-response-and-break-glass) |
| [03-incident-lane](03-incident-lane.svg) | The 2 a.m. Lambda example: the pull-request lane with responder and on-call approver, then the JIT fallback | Layer 3 "Example: Lambda timeouts at 2 a.m.", layer 7 break-glass table |
