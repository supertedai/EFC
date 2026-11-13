# Options considered

## SDK page operations
1. Keep only 0.10.x names — rejected: breaks with renamed-only clients.
2. Switch only to Pages names — rejected: installed 0.10.3 lacks them.
3. Resolve an explicit supported name pair for each operation before any write — selected. If neither exists, fail before config/directives/pages mutate.
4. Bypass SDK with REST calls — rejected for now; duplicates auth/serialization behavior.

## PATCH success
1. Accept only HTTP 200 — rejected: 204 is also successful and has no JSON body.
2. Accept any 2xx, then require GET/readback equality for every requested field — selected. Non-2xx or mismatch stops before directives/pages.

## Missions
1. Replace bank missions — rejected: destroys bank-authored constraints.
2. Leave missions unchanged — rejected: known requirements remain inactive.
3. Append small idempotent additions to existing retain/reflect missions, preserving exact original text; keep `--replace-missions` explicit — selected.

## Historical entities
1. Reprocess production documents — rejected: API deletes existing memory units before re-extraction; bank has 5,170 documents and a non-snapshot 192k entity listing.
2. PATCH all suspected entities — rejected: detection is heuristic, mapping is semantic, and update side effects include re-embedding/derived graph changes.
3. Keep new-retain guardrails active and open a separate owner-reviewed migration with snapshot/clone and per-memory mapping — selected. No history mutation here.

## Label semantics
Preserve all four additions. `evidence_layer` vs `epistemic_layer` is provenance vs document level; `physical_regime` vs `rcmp_regime` is scale/structure vs cosmological/entropy chronology; `kill_criterion` and `ledger_status` are test linkage vs validation status.
