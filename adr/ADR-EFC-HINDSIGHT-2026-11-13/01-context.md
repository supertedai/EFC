# Context and evidence

## Repository and task
Task `t_c9dbf0a2` is running under faber with a pre-provisioned linked worktree `/home/morten/wt-efc-hindsight-followup`, branch `wt/efc-hindsight-followup`, based exactly on `ef687d4441d83628b827fb6c9b9d3f7c8eb61253` (`origin/main`). The worktree was clean at inspection. PR #653 is already merged; this is a separate follow-up.

## Measured API state (read-only)
- Installed package is `hindsight-client 0.10.3`; `Hindsight` exposes `get_knowledge_base_tree`, `create_knowledge_folder`, `create_knowledge_page`, not the new Pages names.
- Live EFC API OpenAPI reports server version `1.2.0`. Hindsight 1.2.1 release notes say Knowledge Pages were renamed to Pages, old names remain until 2.x; current docs show `get_page_tree`, `create_page_folder`, `create_page`.
- Current script invokes the 0.10.x names after writing config, so a renamed-only client can fail after a config mutation.
- REST config helper returns a status; caller currently requires exactly HTTP 200, then reads config back.

## Live bank state (read-only)
- Current bank missions are bank-authored and include extensive EFC-specific rules. They must not be replaced. Retain lacks the short-proper-name/external-AI attribution requirements; reflect lacks `source=figshare`/`source=ledger` preference over chat.
- Existing `epistemic_layer` describes document level (L0–L3); `evidence_layer` describes source/provenance. Existing `physical_regime` is explicitly the RCMP physical/cosmological-scale axis; new `rcmp_regime` is the L0–L3 cosmological/entropy chronology and transition vocabulary. These overlap in vocabulary but not meaning. `kill_criterion` identifies KC1–KC5; `ledger_status` captures validation status. Preserve all four additions.
- GET documents reported 5,170. First entity-list response reported total 192,268; pagination returned 192,285 rows, so no coherent snapshot or exact whole-bank candidate total is claimed. A string heuristic flagged 114,129 names as sentence-like (screening count, not semantic classification). Inspected examples include >1,000-character claim-shaped entity names. Historical whole-claim entities are confirmed.
- Reprocess explicitly deletes existing memory units before re-extracting. `UpdateMemoryRequest.entities` replaces entity links but requires text or state; changing text re-embeds and drops derived observations and links. No non-destructive bulk route is proven.

## Unknowns
No stable snapshot enumeration, deterministic entity-name mapping, exact malformed-entity count, or tested rollback for mass corrections. Do not infer these from heuristic counts.
