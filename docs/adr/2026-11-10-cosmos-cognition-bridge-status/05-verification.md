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

## Results

_To be filled with actual output. Nothing here is claimed green until it is pasted._
