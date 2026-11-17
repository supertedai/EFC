# Decision

**Chosen:** Option B.

The lookup will distinguish the legacy contract-presence flag from an actual completed outcome. Preserve `har_oppgjoer` exactly as `bool(node.get("settlement"))`; a result-only record does not change that legacy field. Add a typed status for the reader:

- `none`: no settlement record/result;
- `pending`: the record explicitly awaits an arbiter;
- `settled`: an EFC `settlement_result` names this node, matches every available prediction/contract correlation, has a `confirmed`/`contradicted` outcome, finite `gap_sigma`, and sequence/message provenance; or a static settlement record has a non-empty correlation matching every available prediction/contract correlation, a completed outcome, outcome time, settlement version, and source. A static structured outcome must either carry a recognized terminal lifecycle value (`confirmed`, `contradicted`, or another explicitly supported terminal label) or contain named measurement/result fields. Generic wrappers alone (`value`, `data`, `result`, etc.) are not evidence. Any explicit but open, pending, unknown, or unrecognized lifecycle value (including punctuation-delimited forms such as `pending: review`) fails closed to `record_only`, even when other fields are populated;
- `record_only`: a settlement object exists but does not carry complete outcome evidence.

Rendering must fail closed and explicitly show contract presence/absence plus `pending`, `settled`, or incomplete status. A valid result can settle a still-pending contract; otherwise an explicit wait state on a correlation-matched record takes precedence over incomplete result records. Keep the rule aligned with the existing atlas and `scripts/atlas_oppgjoer.py` result shape; do not infer a settlement from a prediction, DOI, bus count, or object existence.

**Follow-up precision:** a pending `settlement_result` may override a static record only when its correlation matches every known correlation on the prediction and static contract. With no prediction, the static contract's own correlation is still binding; with no known correlation, the result is unverified rather than pending.

**Result-block consistency (2026-10-13 follow-up):** a terminal `settlement_result.outcome` (`confirmed`/`contradicted`) is insufficient by itself. The entire recursively decoded result block must have no invalid lifecycle fields and no unresolved lifecycle text anywhere in its values. A contradictory signal such as `status: pending`, `status: awaiting arbiter`, `settled: false`, `pending: true`, or nested `status: unknown` prevents a settled classification; with no independently pending static contract, the result remains `record_only`. A result whose `outcome` explicitly waits for an arbiter continues through the pending branch.