# Decision (revised after second opinion)

Build a triangulation / cross-check layer. Core invariant, sharpened by the panel review: **a claim is auto-accepted only when its evidence is external-origin, disjoint-provenance, and independently agreeing; internal self-agreement — including self-generated data, self-sealed-then-self-confirmed predictions, or same-model/codebase/organization agreement — never raises confidence.**

## Separated axes (replaces the single L0–L5 ladder)

A claim is described by independent fields, not one ordinal level:

| Field | Values |
|---|---|
| `mechanical_status` | verified / failed / n/a (deterministic check, with byte/hash provenance) |
| `support_status` | unsupported / single / replicated / contradicted |
| `independence_status` | independent / correlated / unknown |
| `claim_risk` | low / medium / high |
| `action` | record / auto-accept / escalate / owner-gate |

## Independence — external-origin, machine-checkable

A source is **independent** only when ALL of:
1. **External origin** — a stable external identity (DOI / arXiv / external team). System-derived output (internal model, derived dataset, self-generated prediction) is categorically excluded from evidence.
2. **Provenance record** — data lineage, code lineage, citation lineage, author/organization, retrieval timestamp.
3. **Disjoint provenance (common-ancestor check)** — no shared upstream dataset, paper, code, model, funding, or author with the claim's other sources.

Temporal separation is an **anti-hindsight control** (a bonus on top of external origin), never a standalone independence criterion.

## Action policy

- **auto-accept** only when `independence_status == independent` AND `support_status == replicated` (≥2 disjoint external sources) AND `claim_risk == low` AND `mechanical_status == verified`.
- **escalate** when `independence_status ∈ {correlated, unknown}` OR `support_status == contradicted` (any material conflict takes precedence) OR `claim_risk ∈ {medium, high}`.
- **owner-gate** always for falsify / canonize / publish (irreversible), regardless of other fields.
- **Type A vs Type B classification is deterministic or owner-gated, never LLM-assigned** — a scientific claim cannot be laundered into the mechanical lane.

## Confidence is computed, not claimed — and the source record is structured provenance

Each claim's record is append-only and contains, per source: stable external ID/DOI, retrieval timestamp, the exact passage/result supporting the claim, provenance/lineage, common-ancestor status, and any negative/contradictory evidence searched for. Confidence is recomputed when a source, provenance edge, or contradiction changes. A record with a missing, duplicate, correlated, or non-external source is rejected — the rule is substantive, not a bare citation list.

## Scope boundary (unchanged)
This layer governs confidence and escalation of claims. It does **not** remove the publish / mint / merge / falsification-verdict human gates. It is read-only with respect to existing claims.
