# Run manifest — `deleg_99e69c41` (EFC Model Family Reconciliation, v3 re-review)

**This file is ORCHESTRATOR navigation metadata, not reviewer output.**
It contains no disposition, no claim_status, and no verdict. Those are
reviewer-authored artifacts (`verdict.json`, `claim_gate_matrix.json`,
`role_*.json`) and remain authoritative over this index.

## Identity

| Field | Value |
|---|---|
| Run ID | `deleg_99e69c41` |
| Slug / manuscript | `EFC_Model_Family_Reconciliation` |
| Snapshot | `snapshot.tex` (frozen; byte-identical to live `.tex`) |
| Snapshot SHA-256 | `99e69c41944a71c738a3d3fa9f4366d41fb51a17060e7a5e0c5cafa246150ee1` |
| Method revision | `v2` |
| Why this run exists | The live manuscript was edited after the v2 freeze (`deleg_d21ed669`), so the v2 verdict no longer bound it; the release gate correctly refused. This run re-reviews the edited text. |
| Reviewer model | rounds 1–3 authored on `gpt-5.6-luna`; the archive-completion matrix pass (`deleg_09a061ac`) ran on `gpt-6-luna` |

## What changed versus v2 (and is therefore newly under review)

1. **C13 (new):** the regime-ontology hypothesis — MOND-like and ΛCDM-like
   behaviour as candidate effective regimes of one energy-flow framework
   (corpus 31943361, 31348411, 31348417).
2. **C14 (new):** the corpus-provenance scope expansion — six primary
   Γ-response packages *plus* broader corpus, not an exclusive six set.
3. **C12 (re-worded):** the build-warning status changed (v2 said Overfull/
   float warnings; the live text now says no Overfull/Underfull/float warnings).
4. Layout/bibliography/status-word changes (tabularx tables, `\raggedbottom`,
   manual `thebibliography`, "preregistered→proposals", "registered→recorded",
   "reproducible by construction→designed for reproducible and machine-readable
   inspection"). These are not new claim content; they are re-confirmed by the
   re-read, not re-litigated.

## Provenance corrections (orchestrator envelope, NOT reviewer words)

- The initial dispatch seeded `"model": "deepseek (single model family)"` in the
  role-file templates. The delegation harness actually ran the roles on
  **`gpt-5.6-luna`** (verified from the batch header). The `model` field is
  orchestrator-owned envelope metadata, not a reviewer finding, so it was
  corrected to `gpt-5.6-luna (single model family)` across all eight role files.
  Leaving the false string would have been a provenance lie.

## Two epistemic caveats (permanent, do not elide)

1. **Same-model family, second pass.** v3 ran on the same model family as v2.
   It bought no cross-family independence. Agreement here is reading
   consistency on a second pass, never independent validation. An executed
   empirical test outranks all of it.
2. **Round 1 was partly steered.** The dispatch named specific targets
   (the a₀ freeze, the C13 falsifiability question, the siren FRW background).
   Findings are therefore partly prompted, not a fully clean blind read. The
   C13/C14 findings still converge independently with the manuscript's own
   self-description, which is the weak-relevant signal worth noting.

## Freeze status — 2026-09-25 (frozen; do not resume without new authorisation)

The archive is **complete and verified on disk**:

- Reviewer-authored artifacts present: `verdict.json` (sha `da2f07a5…`), `meta_review.json`, `synthesis.md`, `claim_gate_matrix.json`, 8 `role_*.json`, `round2_advocate.md`, `round2_attacker.md`, `claim_map.json`, `snapshot.tex`.
- `claim_gate_matrix.json` authored by role 9 (`deleg_09a061ac`, gpt-6-luna) — verified PASS: 14×10 = 140 cells, **7 satisfied / 70 open / 63 not_applicable**, hash-bound to the verdict, every satisfied cell cites a real finding_id.
- Live `.tex` is byte-identical to `snapshot.tex` (`99e69c41…`).
- Nothing is promoted: all 14 claims remain `proposed`.

**Measured gate state (terminal, correct, fail-closed):**

```
check   deleg_99e69c41  →  REFUSED: claim 'C1' has an open gate (1)
release … --confirmed-by morten  →  REFUSED: human_gate.json missing (a human must dispose; agents cannot)
```

Both refusals are the healthy terminal outputs, not bugs to route around.

**v2 → v3 matrix delta (stated, not hidden).** v2 was 31 satisfied / 35 open / 54 not_applicable; v3 is 7 / 70 / 63. The near-doubling of open gates is structural: gate 1 is open for all 14 compound claims and gate 10 for all 14, plus C13's nine opens. It reflects that v3 (with C13/C14 added) carries more genuinely-unfrozen content — not that the review degraded.

**C13 gate 5 nuance.** The single "satisfied" cell whose cited finding is `attacks`/`author-gate` (F-para-12) is defensible only on gate 5's letter — "borrowed paradigms are explicitly labelled" (that the paradigm critic can name the borrowed ΛCDM/MOND vocabulary is itself evidence of in-situ labelling). The substantive critique lives in gates 8/9, which are correctly open. Reviewer output is authority; this note records the reading, it does not rewrite it.

## Handoff

Committed to the `docs/efc-v3-review-closure` feature branch (never `main`) on 2026-09-25, per Morten's instruction to deliver the full git folder. The archive is frozen and internally consistent. The publication decision is open: `human_gate.json` (human signature, `confirmed_by: morten`, bound to `da2f07a5…`) does not exist and is not agent-authored; merge to `main`, DOI reservation, and publication remain human actions.

**Figshare status (measured 2026-09-26, via .12-vakt):** a private draft exists — `article_id 34003932`, `status: draft`, `is_public: false`, `doi: ""` (not reserved). No DOI reserved; no publish; no merge to `main`.
