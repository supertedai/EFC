# 00 — Charter: record the cosmology–cognition bridge as a proposal, not a result

- **Change id:** `2026-11-10-cosmos-cognition-bridge-status`
- **Kanban:** `t_1610348d` (board `energy-flow-cosmology`), run 836
- **Owner (decides):** Morten Magnusson — human gate. Landing is his word alone.
- **Implementer:** `researcher`
- **Independent review:** a distinct reviewer session (see `06-review.md`)
- **Tier:** material (public atlas bank, generated registers, tests). Not critical: no
  schema migration, no permission, no scheduler, no irreversible effect.

## Request

Morten authorizes a controlled, reviewable EFC-atlas change that preserves a verified
finding for later work by Morten and Opus:

> formal/model-based bridge proposals between EFC cosmology and cognition exist;
> empirical/causal cosmology-to-cognition validation is **not** established.

The change authorizes research, an isolated implementation, tests, independent review and
a PR to `supertedai/EFC`. It does **not** authorize merging or landing.

## Scope — in

1. `schema/regime_nodes.jsonld`, node `efc.lag_c0`:
   - `ontology.proveniens.kilder`: add the two proposal DOIs as `type: "doi"` entries.
   - `revisjon`: append one dated entry recording the proposals, their internal limits,
     the earlier counter-evidence, and the unresolved v2.0/v2.1 discrepancy.
2. One regression test pinning the calibrated claim and the preserved epistemic limits.
3. Regenerated derived registers where the canonical generators demand it, and the
   changelog projection if the touched paths are public-relevant.
4. This ADR package.

## Scope — out

- No new node, relation/edge, predicate, status or metric.
- No change to `epistemikk` (`sannhetsstatus` stays `hypotese`, `evidensstatus` stays
  `proxy`).
- No public HTML hand-edit, no schema migration, no unrelated atlas cleanup.
- No claim that EFC is a universal physical ontology; no inference about Opus's
  phenomenal consciousness or ASI; no raw-paper/abstract ingestion.
- No merge, no publish, no deploy, no DOI operation.

## Exit criterion

The atlas bank records both proposal DOIs in provenance and a revision entry that states
the calibrated conclusion and its limits; nothing in the node asserts empirical or causal
establishment; the node count (126) and relation count (86) are unchanged; the required
suite is green; an independent reviewer has dispositioned the change; a PR is open with
exact head/base/checks read back — and **not merged**.

## Status vocabulary used in this package

`proposed` → `implemented` → `reviewed` → `published` (branch pushed / PR open) →
`verified` (readback). Merge/landing is a separate, human-owned state and is not claimed
here.
