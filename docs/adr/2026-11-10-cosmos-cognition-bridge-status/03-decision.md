# 03 — Decision

**Status: DECIDED** (design) — implementation status is tracked in `08-closeout.md`.

## Decision

Enrich the existing node `efc.lag_c0` in `schema/regime_nodes.jsonld` with (1) two DOI
entries in `ontology.proveniens.kilder` and (2) one dated `revisjon` entry. Add one
regression test. Add no node, no relation, no status, no metric.

## Exact design

### 1. `ontology.proveniens.kilder` — append two entries

```json
{"type": "doi", "ref": "10.6084/m9.figshare.31940547", "hentet": "2026-11-10"},
{"type": "doi", "ref": "10.6084/m9.figshare.31969983", "hentet": "2026-11-10"}
```

Appended **after** the existing three entries; the existing entries, the `begrensning`
clause ("DOI establishes identity and persistence, not truth") and `fullstendig: true` are
left byte-identical. `ontology.source` (free text) and `ontology.assumes` are **not**
touched: they name the node's constitutive sources, not the bridge-status record.

Why these two and not five: these are the two documents that *propose* the bridge — the
thing the card authorizes recording. The counter-sources are cited in `revisjon` instead
(see §2 and `02-options.md` §F for why `31289806`'s DOI string is deliberately kept out of
the bank).

### 2. `revisjon` — append exactly one entry, dated `2026-11-10`

Required content, all traceable to `01-context.md`:

1. That two **formal/model-based proposals** exist, naming both DOIs.
2. Their **internal limits**: B1/B2 hold at equilibrium level and Tcog is not independently
   measured (so Eq. 13 is a consistency relation); the `δS/δρ ↔ transfer entropy`
   identification is "an ansatz, not a derivation"; γ is unconstrained and must come from
   data; the propofol material "does not yet constitute a direct test of the full model".
3. The **calibrated conclusion**: empirical/causal cosmology-to-cognition validation is
   **not established**.
4. The **earlier counter-evidence**: EFC-C v0.1 (`31940505`) stated that the bridge "has not
   yet been derived"; the field-resonance note
   (`docs/papers/efc/EFC-C_Consciousness_Field_Resonance/`, 2026-02-08) calls the
   cosmological correspondence "not identity … the same class of thermodynamic arc" and its
   own effect "a candidate hypothesis, not a confirmed effect", with empirical content in
   propofol-EEG only.
5. The **unresolved discrepancy** for `32091700`: DataCite title says **v2.0**, the local
   `index.json` and `figshare/doi-map.json` say **v2.1** — recorded as a discrepancy, not
   resolved.
6. That the node's **status is unchanged** (`hypotese` / `proxy`).

Language: English (the two existing entries are English; the repo's language gate does not
scan `schema/`, but consistency is the reason, not the gate).

### 3. Regression test — `tests/test_atlas_bro_status.py`

Pins, and must fail before the change:

- `efc.lag_c0.epistemikk.sannhetsstatus == "hypotese"` and `evidensstatus == "proxy"`.
- both proposal DOIs present in `ontology.proveniens.kilder` with `type == "doi"`.
- exactly one `revisjon` entry dated `2026-11-10`, containing: both DOIs, the word
  `ansatz`, `gamma`/`γ` unconstrained, `not established`, and `v2.0`+`v2.1`+`discrepan`.
- no affirmative establishment language anywhere in the node
  (`\bconfirms?\b`, `\bproves?\b`, `\bvalidates?\b`, and a causal-establishment regex) —
  while `not established` is still present.
- structure preserved: `len(nodes) == 126`, `len(relations) == 86`, and **no** relation has
  `efc.lag_c0` as subject or object.

### 4. Derived artifacts

- Regenerate `docs/efc-atlas/atlas/data.mjs` + `docs/efc-atlas/INDEKS.md` (required by
  `test_efc_atlas_generator.py`). Expected diff: none (measured: neither `revisjon` nor
  `kilder` is surfaced).
- Regenerate the three `docs/validation-ledger/data/doi_coverage_*.json` (required by
  `test_generated_files_match_build`). Expected diff: four DOIs gain
  `in_atlas_literal_url: true`; `disposition` unchanged (`changelog_only`); the pending
  backlog stays at 60. Any deviation from that expectation is a finding, not a detail.
- Run and commit the changelog projection if `docs/validation-ledger/**` makes the commit
  public-relevant.

## Conditions of the decision

- If the schema rejects the edit (`additionalProperties: false`), stop and report — do not
  extend the schema.
- If the coverage registers move in a way not predicted above (especially if the pending
  backlog *loses* an item), stop and report before committing.
- If any existing test outside the added one goes red, treat as regression.

## Provenance of this decision

Morten's card mandate (`t_1610348d`); schema and convention files measured in
`01-context.md`; primary sources re-read from `docs/papers/efc/` with DataCite confirmation
via `efc_doi`. Independence: the *change* is not self-approved — review is `06-review.md`.
