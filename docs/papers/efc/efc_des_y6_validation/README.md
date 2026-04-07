# EFC Lensing Validation Update: DES Year 6 Is Consistent With S₈ Suppression Prediction

**Author:** Morten Magnusson (ORCID: 0009-0002-4860-5095)
**Document ID:** EFC-VAL-2026-002
**DOI:** [10.6084/m9.figshare.31951992](https://doi.org/10.6084/m9.figshare.31951992)
**Date:** April 7, 2026
**License:** CC-BY 4.0

## Key Result

The DES Y6 lensing-to-CMB S₈ ratio **0.944 ± 0.018** agrees with the EFC pre-registered prediction
**0.95 ± 0.03** to within **0.3σ**. This is a **PASS** of the P3 lensing consistency test.

| Quantity | Value | Source |
|---|---|---|
| S₈ (DES Y6, 3×2pt) | 0.789 ± 0.012 | arXiv:2601.14559 |
| S₈ (CMB 2026, Planck+ACT+SPT) | 0.836 ± 0.012 | Qu et al. 2026 |
| Observed ratio | 0.944 ± 0.018 | This work |
| EFC prediction | 0.95 ± 0.03 | Magnusson 2026a |
| Agreement | within 0.2–0.3σ | PASS |

## Why This Matters

- **Pre-registered**: Prediction (DOI 10.6084/m9.figshare.31188193) and pass criterion
  (ratio ∈ [0.90, 1.00]) were deposited prior to DES Y6 release (Jan 21, 2026).
- **Cross-scale consistency**: Ties galactic SPARC fits (k = 0.415 ± 0.05) to cosmological
  weak lensing — same parameter, two scales.
- **Mechanism for S₈ tension**: EFC density-dependent screening Σ_EFC ≈ 0.95 reproduces
  the observed lensing suppression without invoking massive neutrinos or new dark sector.

## Pre-Registered Pass/Fail Criteria

- **PASS**: S₈ˡᵉⁿˢ / S₈ᶜᴹᴮ ∈ [0.90, 1.00]
- **FAIL**: η ≠ 1 at > 3σ (E_G statistic or equivalent)

Observed 0.944 falls inside the PASS window.

## Limitations (See §5 of paper)

1. **1D test** — single-number compression of Σ(k, z); needs full Cℓ comparison.
2. **Not unique** — massive ν, f(R), decaying DM, baryonic feedback can also produce suppression.
3. **DES vs KiDS divergence** — KiDS Legacy gives S₈ ≈ 0.82 (< 1σ from CMB).
4. **η = 1 untested here** — A3 ansatz still requires direct E_G validation.
5. **k = 0.415 from SPARC** — strength (no fine-tuning) but inherits SPARC systematics.

## Updated Validation Status (April 2026)

| Test | Prediction | Observed | Status |
|---|---|---|---|
| P1: Closure g† = cH₀/e | 2.5 × 10⁻¹⁰ m/s² | 2.51 ± 0.60 | Consistent |
| P2: Cross-scale C stability | C ≈ 4.4 | — | Untested |
| **P3: Lensing S₈ ratio** | **0.95 ± 0.03** | **0.944 ± 0.018** | **PASS** |
| A3: η = 1 | η = 1 | — | Not tested |

## File Manifest

| File | Purpose |
|---|---|
| `efc_des_y6_validation.pdf` | Source preprint (8 pages) |
| `README.md` | This document |
| `index.json` | Machine-readable index |
| `metadata.json` | Schema.org metadata + EFC context |
| `schema.json` | JSON Schema for validation |
| `efc_des_y6_validation.jsonld` | JSON-LD linked data |
| `citations.bib` | BibTeX references |
| `src/__init__.py` | Python module exports |
| `src/des_y6_validation.py` | Reproducible computation classes |
| `data/des_y6_data.json` | Numerical data (DES Y6, CMB, EFC prediction) |
| `examples/demo.py` | End-to-end demo with assertions |

## Next Steps

1. **Oct 2026** — Euclid DR1 cosmology release (independent S₈ at comparable precision).
2. **Hierarchical SPARC** — direct test of P2 (C stability across galaxy subsamples).
3. **E_G statistic** — direct test of η = 1 via galaxy-galaxy lensing + RSD.
