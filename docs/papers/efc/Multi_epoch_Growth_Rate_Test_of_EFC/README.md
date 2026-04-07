# Multi-epoch Growth Rate Test of EFC — AI-friendly package

**Report:** EFC-VAL-2026-003
**DOI:** [10.6084/m9.figshare.31955871](https://doi.org/10.6084/m9.figshare.31955871)
**Author:** Morten Magnusson (ORCID 0009-0002-4860-5095)
**Date:** 2026-04-07 · **License:** CC-BY-4.0

First multi-epoch test of the EFC perturbation-sector coupling using 14 fσ8(z) measurements (z = 0.067–1.491) from 6dFGS, BOSS DR12, eBOSS DR16, and DESI DR1 (full-shape + peculiar velocities).

## Result (TL;DR)

| Model | params | χ² | dof | χ²/dof |
|---|---|---|---|---|
| ΛCDM | Ωm, σ8 | 12.07 | 12 | 1.006 |
| EFC  | σ8, B, z_t (Ωm fixed) | 11.98 | 11 | 1.089 |

Δχ² = 0.10 (0.06σ), ΔAIC = −1.90 → **ΛCDM marginally preferred**. EFC is consistent (B=0 within 1σ profile) but not required by fσ8 alone. Strong Ωm–B degeneracy; cross-probe combination with BAO needed.

## Model

Linear growth ODE with regime-dependent gravitational coupling:

```
D'' + (3/(2a))[1+Ω_DE(a)] D' = (3/(2a²)) Ω_m(a) μ(a) D
μ(a) = 1 − B · T(a),   T(a) = 1 / (1 + (a_t/a)^n),  n = 2 fixed
```

## Files

- `efc_multi_epoch_note.pdf` — paper
- `index.json`, `metadata.json`, `schema.json`, `*.jsonld` — machine-readable metadata
- `data/fsigma8_compilation.csv` — 14 fσ8 measurements
- `data/efc_multi_epoch_results.json` — fit outputs
- `src/efc_multi_epoch_v2.py` — analysis script (NumPy/SciPy)
- `examples/reproduce_minimal.py` — minimal reproducer
- `citations.bib` — references

## Reproduce

```bash
python examples/reproduce_minimal.py
```

## Related

- Pilot (BOSS DR12 only): 10.6084/m9.figshare.31243828
- WP1a μ(a) reference: 10.6084/m9.figshare.31333600
- CMB+LSS localisation: 10.6084/m9.figshare.31368433
