# Decision

**Chosen:** Option B.

The lookup will distinguish the legacy contract-presence flag from an actual completed outcome. Preserve `har_oppgjoer` exactly as `bool(node.get("settlement"))`; a result-only record does not change that legacy field. Add a typed status for the reader:

- `none`: no settlement record/result;
- `pending`: the record explicitly awaits an arbiter;
- `settled`: an EFC `settlement_result` names this node, matches every available prediction/contract correlation, has a `confirmed`/`contradicted` outcome, finite `gap_sigma`, and sequence/message provenance; or a static settlement record has a non-empty correlation matching the prediction when present, a completed outcome, outcome time, settlement version, and source. A static outcome is complete only when it is `confirmed`/`contradicted` or a populated JSON object/list with no unresolved outcome markers (`unknown`, `inconclusive`, pending, or waiting states);
- `record_only`: a settlement object exists but does not carry complete outcome evidence.

Rendering must fail closed and explicitly show contract presence/absence plus `pending`, `settled`, or incomplete status. A valid result can settle a still-pending contract; otherwise an explicit wait state on a correlation-matched record takes precedence over incomplete result records. Keep the rule aligned with the existing atlas and `scripts/atlas_oppgjoer.py` result shape; do not infer a settlement from a prediction, DOI, bus count, or object existence.