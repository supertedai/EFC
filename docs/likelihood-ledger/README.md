# EFC Likelihood Ledger

Per-test pipeline declaration: which likelihood, which covariance, which priors,
which codebase. Closes the **Dataset → Likelihood** gap identified in the
2026-04-23 system audit.

Sibling of `validation-ledger/`. Validation Ledger records *what was tested
and how it scored*; Likelihood Ledger records *how the score was computed*.

## Files

| File | Format | Description |
|------|--------|-------------|
| `index.md` | Markdown | Human-readable likelihood pipeline registry |
| `index.jsonld` | JSON-LD | Schema.org metadata (Dataset) |
| `schema.json` | JSON Schema | Schema for `data/likelihoods.json` |
| `data/likelihoods.json` | JSON | Master data file: one entry per test_id |

## Linking convention

Each entry MUST reference an existing `test_id` from
`validation-ledger/data/tests.json`. Sync script (TBD) refuses orphan entries.

```
validation-ledger/tests.json   →   test_id
likelihood-ledger/likelihoods.json  →  test_id (FK)  +  pipeline declaration
```

## Status

DRAFT — skeleton only. Schema and one worked example. Bulk population
deferred until structure is approved.
