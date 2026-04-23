# EFC Evaluation Ledger

Global decision rule + total score function. Closes the **"missing closure"**
gap from the 2026-04-23 system audit: the system stops at per-test results
without producing a global verdict.

Sibling of `validation-ledger/` and `likelihood-ledger/`.

- Validation Ledger: *what was tested, what came out*
- Likelihood Ledger: *how the score was computed*
- **Evaluation Ledger: how scores combine into a global verdict + thresholds**

## Files

| File | Format | Description |
|------|--------|-------------|
| `index.md` | Markdown | Decision rules, weights, thresholds, score function definition |
| `index.jsonld` | JSON-LD | Schema.org metadata (Dataset) |
| `schema.json` | JSON Schema | Schema for `data/evaluation.json` |
| `data/evaluation.json` | JSON | Weights, thresholds, current global score |
| `data/atlas-link.json` | JSON | **READ-ONLY reference** to Atlas viability map (does not modify Atlas) |

## Atlas safety

This ledger **references** the Atlas via `data/atlas-link.json` only.
It MUST NOT modify Atlas structure. Any field marked `atlas_ref` is a
pointer; the source of truth stays in Atlas.

## Status

DRAFT — skeleton only. Numerical weights deliberately empty pending
maintainer decision.
