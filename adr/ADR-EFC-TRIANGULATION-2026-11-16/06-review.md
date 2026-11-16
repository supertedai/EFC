# Review

Independent panel verdicts (both model-foreign to the caller, direct API, verified).

## Panel 1 — gpt-5.6-luna (openai route, verified)
**VERDICT: BLOCK · CONFIDENCE: 0.96**

## Panel 2 — deepseek-v4-pro (escalation, deepseek route, verified)
**VERDICT: BLOCK · CONFIDENCE: 0.84**

## Convergent findings (both panels independently agree)
1. **Independence definition is circular / soft.** "Different data" and "time separation" are not anchored to external provenance — an internal system can self-generate a derived dataset or self-seal-then-self-confirm and launder it as independence.
2. **L0–L5 conflates four dimensions** (verification vs source-count vs conflict vs required action); a linear scale mixes them and "2 sources" is not a safe universal threshold.
3. **Escalation boundary unsafe** — false auto-accept via correlated sources, deterministic-but-wrong L0 (parser bug / stale resolver), conflict precedence ambiguity, and Type A/B misclassification.
4. **Source-list rule is cosmetic** — it does not validate that listed sources are external, independent, or non-derived.

## Arbitration (my disposition)
All four findings **accepted** — the panels are correct, and the holes are real. One additional point (deepseek-v4-pro): "deterministic does not mean correct" — even L0 needs byte/hash provenance, not unconditional trust. Accepted.

The decision in `03-decision.md` is revised to: (1) external-origin as the *primary* independence condition with a provenance DAG + common-ancestor checks, temporal separation demoted to an anti-hindsight control; (2) separated axes instead of one ordinal ladder; (3) strict escalation conditions with conflict precedence and deterministic (not LLM) Type A/B classification; (4) structured, validated provenance as the source record, not a bare citation list.
