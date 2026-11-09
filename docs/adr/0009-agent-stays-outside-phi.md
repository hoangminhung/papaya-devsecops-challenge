# ADR-0009: The coding agent stays outside PHI; real-data reads are approved per tenant

- **Status:** Accepted
- **Date:** 2026-11-09
- **Decided by:** owner of this submission (research 1.9, 5.8 "not extended"; GĐ-9, GĐ-14)
- **Scope:** coding-agent sessions on laptops and in CI; production stores of all insurer tenants

## 1. Context

Papaya holds medical records, national IDs and bank accounts for several insurer tenants in
different countries. Claude Team is not shown as BAA-covered (⚠️ R1.11.3.4). Partner-uploaded claim
documents are both PHI and a prompt-injection vector (research 1.11.4 L6). Neither OWASP nor NIST
knows a full prevention for prompt injection (📖 R6.1.1, R6.1.2).

## 2. Options considered

| Option | Pros | Cons |
|---|---|---|
| A. Agent reads prod data freely | Fastest debugging | PHI in transcripts; injection can exfiltrate; no BAA |
| B. Agent never reads any customer data | Simplest rule | Blocks legitimate debugging of non-PHI data |
| C. Agent outside PHI; other personal data case by case under an approved, per-tenant grant | Matches the owner's boundary; debugging still possible | Process controls on some paths |

## 3. Decision

Option C.

- **PHI:** never in an agent session. A human reads in a terminal without an agent and gives the
  agent a redacted summary. A store that holds PHI counts as PHI unless the agent reads a view without
  it [design].
- **Other personal data:** readable within an approved request naming one tenant, purpose, store,
  window and agreement (BAA/DPA, partner contract) (GĐ-9); approved by an approver ≠ requester and
  co-approved by the tenant's data owner [design]; data-read role, 1 h [design]. The same request
  applies when a human reads PHI. At night the
  on-call approver approves alone and the data owner reviews the grant the next working day [design].
- **Partner documents:** reproduced with synthetic documents or de-identified first [design].
- **Non-prod:** synthetic or masked only (GĐ-14); no prod copies (S11).

This is a target, not a guarantee: "no agent in the PHI terminal" is a process rule [design] with
the same weakness as D2, since the grant is reachable from the same laptop.

## 4. Consequences

- **Positive:** "minimum necessary" (📖 R1.11.1.8) enforced by IAM for AWS stores (fully from phase 2); one record per
  exception (S9). Assumes injection succeeds and limits what it can reach.
- **Negative / trade-offs:** debugging with redacted or synthetic data; a request for each real read.
- **Risks & how we watch them:** of the 17 paths to PHI (research 1.11.4), tickets, chat, pasted text,
  admin pages, CI logs, prod AI traces and fixtures are covered by process only; k0s and GCP stores follow the same principle
  with mechanisms still open (G1, G3). Per-tenant scoping through session tags (📖 R2.1.8) is
  unresolved, because tags come from user attributes (⚠️). During a data-read window a stolen SSO
  token could open the grant (⚠️, ADR-0007). Data-plane deny actions are incomplete (⚠️ G13). Planted-injection test in
  phase 3.
- **Next steps:** non-prod data scan and the minimal real-data read flow in phase 1; data-plane SCP in
  phase 2.

## 5. References

- Framework layer 6; layer 1 (SCPs); research 1.9, 1.11.4, 5.8.
- Related: ADR-0002, ADR-0006.
