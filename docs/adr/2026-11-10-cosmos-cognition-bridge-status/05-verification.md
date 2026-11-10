# 05 — Verification

**Status: PENDING → filled with observed output during implementation.**
A gate is only green when the command and its output are recorded here; intentions are not
verification.

## Commands and expected readbacks

### V1 — Baseline (before edit)

```
cd /opt/agent-work/EFC/.worktrees/t_1610348d
/opt/venvs/t_123ed6d9/bin/python -m pytest tests/ -q --ignore=tests/test_growth_friction.py
/opt/venvs/t_123ed6d9/bin/python scripts/maintenance/efc_bro_synk.py --sjekk
/opt/venvs/t_123ed6d9/bin/python scripts/maintenance/efc_schema_check.py
```

Expected/observed: 1310 passed, exit 0; `ingen avvik`, rc=0; `OK — 4 schema/instance
pair(s) …`, rc=0.

### V2 — RED (test written, change not yet made)

```
/opt/venvs/t_123ed6d9/bin/python -m pytest tests/test_atlas_bro_status.py -q
```

Expected: failures on the provenance/revision assertions, **not** on import/collection.

### V3 — JSON-LD validity and schema conformance (immediately after the edit)

```
python -c 'json.load(...)'                                  # parses
jsonschema.validate(instance, regime_node.schema.json)       # C10 contract
```

Expected: parses; validates; `additionalProperties: false` satisfied.

### V4 — Format guard (the sync's own invariant)

```
/opt/venvs/t_123ed6d9/bin/python scripts/maintenance/efc_bro_synk.py --sjekk
```

Expected: `ingen avvik mellom motor og atlas`, rc=0 (this is also the format guard — the
file must be byte-identical to the declared writer format).

### V5 — GREEN

```
/opt/venvs/t_123ed6d9/bin/python -m pytest tests/test_atlas_bro_status.py -q
```

Expected: all pass.

### V6 — Generated artifacts fresh

```
/opt/venvs/t_123ed6d9/bin/python scripts/maintenance/efc_atlas_generator.py
/opt/venvs/t_123ed6d9/bin/python scripts/maintenance/doi_coverage_register.py
git diff --stat
```

Expected: `data.mjs` / `INDEKS.md` unchanged; the three `doi_coverage_*.json` change only in
`in_atlas_literal_url` for four DOIs, with `disposition` unchanged and the pending backlog
at 60.

### V7 — Full required suite

```
/opt/venvs/t_123ed6d9/bin/python -m pytest tests/ -q --ignore=tests/test_growth_friction.py
```

Expected: 1311 passed (baseline 1310 + the new test), 0 failed.

### V8 — Repository gates

```
statement_graph_check.py · validate_repo.py · validate_ownership.py
efc_page_consistency.py · efc_narrative_consistency.py
efc_navbar_sync.py --check · efc_spraakvakt.py · efc_schema_check.py
efc_maintain.py (if it reports drift, report it — do not silently "fix" unrelated items)
```

Expected: 0 hard errors each.

### V9 — Determinism of the changelog projection

```
changelog_projeksjon.py   (twice; second run byte-identical)
```

### V10 — Atlas generator determinism

```
efc_atlas_generator.py twice → sha256sum docs/efc-atlas/atlas/data.mjs identical
```

### V11 — Remote readback (after push)

```
gh pr view <n> --repo supertedai/EFC --json headRefOid,baseRefName,state,statusCheckRollup,reviewDecision
```

Expected: head = the local HEAD, base = `main`, state `OPEN`, checks reported individually.

## Results (observed, 2026-11-10)

Ran in `/opt/agent-work/EFC/.worktrees/t_1610348d`, branch `wt/t_1610348d`.

| Step | Command | Observed |
|---|---|---|
| V1 | `pytest tests/ -q --ignore=tests/test_growth_friction.py` | **1310 passed**, 1 warning, 117.94s, exit 0 |
| V1 | `efc_bro_synk.py --sjekk` | `ingen avvik mellom motor og atlas`, rc=0 |
| V1 | `efc_schema_check.py` | `OK — 4 schema/instance pair(s) valid and closed, 2 instanceless schema(s) valid, 4 schema-only valid and closed`, rc=0 |
| V2 | `pytest tests/test_atlas_bro_status.py -q` (before the bank edit) | **4 failed, 3 passed** — failures on `test_both_proposals_are_in_provenance_as_dois`, `…conclusion_as_not_established`, `…limits_from_inside_the_proposals`, `…v2_0_v2_1_discrepancy…`; no import/collection error. The 3 passing were the invariants that must *already* hold: status `hypotese`/`proxy`, no affirmative establishment, no node/relation added |
| V3 | `jsonschema.validate(instance, regime_node.schema.json)` | `VALID against regime_node.schema.json (2020-12, closed)` |
| V4 | `efc_bro_synk.py --sjekk` | `ingen avvik`, rc=0 (writer format preserved; the edit script refuses to write a non-round-tripping file) |
| V5 | `pytest tests/test_atlas_bro_status.py -q` | **7 passed** |
| V5′ | RED/GREEN re-proved with the final test: baseline bank swapped in, re-run, edited bank restored | **4 failed / 3 passed** then **7 passed**; bank byte-identical to the edited copy (`cmp`) |
| V6 | `efc_atlas_generator.py` | `data.mjs written: 159493 bytes`; **no diff** in `data.mjs` / `INDEKS.md` — the generator surfaces neither `revisjon` nor `kilder`, exactly as predicted |
| V6 | `doi_coverage_register.py` | `atlas union 24 literal URLs; … missing-from-atlas 60` (was 20 / 60). Diff: `atlas_union_literal_urls` 20→24; **four** rows `in_atlas_literal_url` false→true, all with `class: changelog`, `disposition: changelog_only` **unchanged**; `doi_coverage_pending.json` changed **only** in `input_digest`, `count` stayed **60**, `31289806` still queued |
| V6 | `efc_ontology.py` | `OK — … 355 terms declared, 511 JSON-LD documents scanned`. Regenerated: `usedAsProperty` for `hentet`/`ref` 193→195 and for `type` 201→203 — the two new provenance entries, nothing else |
| V7 | `pytest tests/ -q --ignore=…` (edited bank, **uncommitted**) | 1315 passed, **2 failed** — `test_atlas_buss.py::test_the_build_reads_the_measurement_and_never_writes_it` and `test_atlas_feltvekt.py::test_the_measurement_leaves_the_bank_alone`, both reporting `M schema/regime_nodes.jsonld` from `git status`. These are **working-tree-cleanliness guards**, not content checks |
| V7′ | same two tests after the commit | **3 passed** (the two, plus `test_efc_ontology`) — confirms the diagnosis |
| V8 | `validate_repo.py` | `repo-contract: 0 errors` |
| V8 | `validate_ownership.py` | `ownership: 0 files without an owner` (the new `docs/adr/**` is covered by the `docs/**` component) |
| V8 | `efc_schema_check.py`, `efc_ontology.py`, `efc_bro_synk.py --sjekk` | rc=0 each |
| V8 | `efc_page_consistency.py` | `all invariants hold` |
| V8 | `efc_narrative_consistency.py` | `OK — 0 warning(s)` |
| V8 | `efc_navbar_sync.py --check` | `all 13 pages have canonical navbar` |
| V8 | `efc_spraakvakt.py` | `OK: no new Norwegian in the guarded paths` |
| V8 | `statement_graph_check.py` | rc=0 (INFO-only `anchor_queue` lines, unchanged) |
| V9 | `changelog_projeksjon.py` ×3 | run 1: `1 new changes projected` (my commit, `categories: {ledger_data: 3}`); run 2 after committing the projection: `no new commits since last projection`; run 3: idempotent. `merge-base --is-ancestor <last_processed_sha> HEAD` → **YES** (the trap the skill names was checked, not assumed). `3509f30d` in the window is a changelog side-effect commit and is excluded by design — verified by its diff (only the two changelog files) |
| V10 | `efc_atlas_generator.py` (determinism) | second run produced no diff; `docs/efc-atlas/atlas/data.mjs` unchanged from `origin/main` |
| V11 | `gh pr view …` | see `08-closeout.md` |

### Final required suite (post-commit)

```
/opt/venvs/t_123ed6d9/bin/python -m pytest tests/ -q --ignore=tests/test_growth_friction.py
→ 1317 passed, 1 warning in 109.66s   (exit 0)
```

1317 = 1310 baseline + 7 new tests. **0 failed.**

