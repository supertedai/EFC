# Plan

1. **`scripts/maintenance/efc_triangulate.py`** — the layer:
   - `claim` schema: `{claim_id, statement, type (mechanical|scientific), sources: [{kind, ref, value, retrieved_at}], confidence, escalated}`.
   - `independence()` — classifies each source as independent or not per the decision.
   - `confidence()` — maps the independent-source count to L0–L4; L5 by claim kind.
   - `escalate()` — returns the escalation decision (auto-accept vs owner) from the level.
2. **`data/triangulation/<claim_id>.json`** — append-only per-claim evidence records (source list + agreement), so every confidence is auditable.
3. **Wire into component 2** (figshare-presence Pass 3): after enrichment, the new claim's relations are run through the layer; only L2/L3 relations auto-land in the draft PR's prose, L1/L4 are flagged for the owner in the PR body.
4. **Deterministic comparison first**: number-vs-number and field-vs-field checks run before any LLM-assisted comparison; LLM is used only to *propose* connections, never to *decide* agreement.

## Order
ADR + second opinion → build the layer → unit tests → wire one pilot claim (P2 fσ8 = 0.430 vs DESI/eBOSS/BOSS) → measure → PR.

## Out of scope (this ADR)
Removing publish / mint / merge / falsification-verdict gates. Multi-source *automatic retrieval* of survey data is a follow-up; the pilot uses sources already in the repo's ledger.
