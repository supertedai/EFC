# EFC Model Comparison Ledger

Cross-model evaluation: same dataset + same likelihood, multiple models.
Closes the **External Ledger gap** from the 2026-04-23 audit (no direct
EFC vs ΛCDM vs MG comparisons in a structured form).

Sibling of `validation-ledger/`, `likelihood-ledger/`, `evaluation-ledger/`.

## Files

| File | Format | Description |
|------|--------|-------------|
| `index.md` | Markdown | Comparison protocol, model registry, current results table |
| `index.jsonld` | JSON-LD | Schema.org metadata (Dataset) |
| `schema.json` | JSON Schema | Schema for `data/comparisons.json` |
| `data/comparisons.json` | JSON | One entry per (dataset, likelihood) × {model A, model B, ...} run |
| `data/models.json` | JSON | Registered models (EFC, ΛCDM, Horndeski, f(R), DGP, ...) |

## Linking convention

Every comparison row references:
- a `likelihood_id` from `likelihood-ledger`
- ≥2 model entries from `data/models.json`

A comparison without a backing likelihood entry is rejected by the
sync script (TBD).

## Status

DRAFT — skeleton only. Model registry has placeholder entries; populate
after maintainer review.
