# EFCLASS Technical Note II: Perturbation-Level σ₈ Suppression via μ(a) < 1

Structural limits of scale-free modifications to the gravitational source term in the growth equation. Builds on Technical Note I, which proved that background-level EFC cannot suppress σ₈.

**DOI:** 10.6084/m9.figshare.31333600

**Date:** February 13, 2026

## Summary

The perturbation channel μ(a) = 1 − B g(a) with μ < 1 weakens the gravitational source term in the growth equation. A systematic scan over gate amplitude (B) and temporal support (steepness n) at fixed μ₀ reveals:

1. **Universal factor-2:** Reducing n from 6 to 2 exactly doubles σ₈ suppression at any μ₀. This is geometric, not parametric.
2. **Structural ceiling:** Within Planck 1σ (μ₀ > 0.90), scale-free μ(a) closes at most ~43% of the S₈ gap.
3. **Reference model (WP1a):** A=0, B=0.187, n=2, z_t=1.01 → μ₀=0.85, σ₈=0.773, S₈=0.790 (73% gap closure at ~1.5σ).

## Contents

| File | Description |
|------|-------------|
| `efc_technical_note_II.pdf` | Authoritative PDF (5 pages) |
| `index.json` | Machine-readable metadata and results |
| `schema.json` | JSON Schema validation |
| `Perturbation-Level-sigma8-Suppression.jsonld` | JSON-LD semantic metadata |
| `metadata.json` | Comprehensive project metadata |
| `citations.bib` | BibTeX references |
| `README.md` | This file |

## Core Equations

- **Growth equation:** f' + f² + (1/2 − 3/2 Ω̃_m) f = 3/2 μ(a) Ω̃_m
- **μ modification:** μ(a) = 1 − B g(a), where g(a) = 1/(1 + (a_t/a)^n)
- **Calibration:** B = (1 − μ₀) / g(1; n)
- **Suppression integral:** Δσ₈ ∝ (1 − μ₀) ∫ g(a; n) d ln a

## Key Results

### Universal Factor-2

| μ₀ | Δσ₈(n=6) | Δσ₈(n=2) | Ratio |
|----|-----------|-----------|-------|
| 0.913 | −0.011 | −0.022 | 2.01 |
| 0.850 | −0.019 | −0.038 | 2.00 |
| 0.800 | −0.025 | −0.050 | 2.00 |

### S₈ Gap Closure

| μ₀ | n | σ₈ | Gap closed | Planck status |
|----|---|-----|------------|---------------|
| 0.913 | 6 | 0.800 | 21% | OK |
| 0.913 | 2 | 0.789 | 43% | OK |
| **0.850** | **2** | **0.773** | **73%** | **~1.5σ** |
| 0.800 | 2 | 0.761 | 97% | 2σ |

## Structural Conclusions

1. Background (A) and perturbation (B) channels are non-degenerate
2. Temporal support matters more than instantaneous amplitude
3. Scale-free μ(a) has a structural ceiling within Planck 1σ
4. Full resolution requires scale dependence μ(k,a) or combined channel

## Reproducibility

- **Code:** `efc_wp1_mu_only_sweep.py` (B-sweep), `efc_wp1_n_scan.py` (n-sweep)
- **Data:** BOSS DR12 RSD (3 points, full covariance, Alam+ 2017)
- **Background:** ΛCDM with Ω_m = 0.3134, H₀ = 67.4

## Citation

```bibtex
@misc{magnusson2026perturbation,
  author = {Magnusson, Morten},
  title  = {Perturbation-Level σ₈ Suppression via μ(a) < 1},
  year   = {2026},
  doi    = {10.6084/m9.figshare.31333600}
}
```

Version: 1.0
