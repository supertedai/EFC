# 04 · Reproduce

> How to rerun the core EFC results from a fresh clone.
> Every claim in the Validation Ledger that can be reproduced from code is wired up here.

[🏠 Home](./Home.md) · [← Papers by topic](./03-Papers-by-Topic.md) · [→ For AI agents](./05-For-AI-Agents.md)

---

## Setup (once)

```bash
git clone https://github.com/supertedai/EFC.git
cd EFC
pip install -r requirements.txt
```

Python 3.10+ recommended. Core dependencies: `numpy`, `scipy`. Pipeline-specific extras are listed in each pipeline's own `README.md`.

---

## Top-level reproduction scripts

Four single-command scripts sit at the repo root. Each emits PASS/FAIL against the Validation Ledger and writes a JSON output file with a SHA-256 content hash.

| Command | Reproduces | Output JSON |
|---|---|---|
| `python reproduce_efc.py` | EFC perturbation sector (WP1a, β = 0.187 etc.) | `reproduce_efc_output.json` |
| `python reproduce_sparc.py` | SPARC 175 rotation curve fit (EFC vs NFW) | `reproduce_sparc_output.json` |
| `python reproduce_bao.py` | Covariance-aware BAO consistency | `reproduce_bao_output.json` |
| `python reproduce_cmb_sanity.py` | CMB sanity check | `reproduce_cmb_sanity_output.json` |

Integration test (runs all four + schema checks):

```bash
python efc_integration_test.py
```

---

## Pipelines

Longer analyses with their own data dependencies live in [`/pipelines/efc/`](../../pipelines/efc/):

| Pipeline | Purpose | Entry point |
|---|---|---|
| [`euclid_dr1/`](../../pipelines/efc/euclid_dr1/) | Pre-registered Euclid DR1 predictions (hi_class + MGCAMB) | [`README.md`](../../pipelines/efc/euclid_dr1/README.md) |
| [`native_v2_graph/`](../../pipelines/efc/native_v2_graph/) | AQUAL discrete-graph gravity solver | `README.md` |
| [`nested_sampling/`](../../pipelines/efc/nested_sampling/) | Full posterior sampling | [`README.md`](../../pipelines/efc/nested_sampling/README.md) |
| [`weak_lensing_case_b/`](../../pipelines/efc/weak_lensing_case_b/) | KiDS-1000 cosmic shear analysis | [`README.md`](../../pipelines/efc/weak_lensing_case_b/README.md) |
| [`hcp_bridge_b1/`](../../pipelines/efc/hcp_bridge_b1/) | Cosmology → neural bridge (B1) | [`README.md`](../../pipelines/efc/hcp_bridge_b1/README.md) |

Read each pipeline's own README for data fetching and exact invocation.

---

## Maintenance and verification

The repo self-verifies. Run manually before committing theory/evidence changes:

```bash
python3 scripts/maintenance/efc_maintain.py
```

This chains:

- `efc_auto_metadata.py` — keep `index.json` synced
- `efc_ai_brain.py` — LLM-assisted post-processing (needs API key)
- `efc_gen_ai_friendly.py` — regenerate AI-friendly paper packages
- `efc_sync_dois.py --apply` — DOI registry sync
- `efc_verify.py` — evidence-layer discipline + drift
- `efc_ledger_impact_sync.py --apply` — Ledger gap sync
- `efc_ledger_autofill.py` — autofill empirical/sealed DOIs
- `efc_drift_detector.py --fix` — count/version drift

The same chain runs automatically on every Claude Code session (via `SessionStart` hook).

Expected clean output:

```
[efc-verify] 150 paper dirs · 0 errors · N warnings
[efc-drift] 150 papers · no drift detected
```

See [`scripts/maintenance/README.md`](../../scripts/maintenance/README.md) for the full algorithm.

---

## Deterministic seeds

All reproduction scripts pin random seeds. The canonical seed is `42`. SHA-256 hashes in each output JSON are tracked in the Ledger so drift is detectable across machines.

---

## Next

- **Where is the AI entry point?** → [05 · For AI agents](./05-For-AI-Agents.md)
- **What do all these terms mean?** → [06 · Glossary](./06-Glossary.md)
