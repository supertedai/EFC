# Multi-component EFC Universality on BIG-SPARC 438 (DRAFT)

**Status:** DRAFT — data pending, pipeline re-run required. No DOI yet.
**Author:** Morten Magnusson (ORCID: 0009-0002-4860-5095)
**Date drafted:** 2026-04-17
**License:** CC-BY-4.0
**Predecessor DOI:** [10.6084/m9.figshare.32029704](https://doi.org/10.6084/m9.figshare.32029704) (single-component SPARC-175 closure)

## Overview

Extends the pre-registered Kill-Test v6 Universality pipeline from SPARC-175 to the BIG-SPARC 438-galaxy corpus (arXiv:2411.13329) with multi-component EFC (stars + gas + screening) under frozen hyperparameters (K₀, m², seed=42). Tests whether EFC's regime-dependent rotation-curve validity — established on SPARC-175 with 60.2% win-rate — generalises to the expanded 2.5× galaxy sample without retuning.

## Key Result (pre-commit)

Pending pipeline re-run. Expected deliverables:
- Per-galaxy χ², ΔAIC vs MOND and NFW on all 438 galaxies
- Regime-distribution histogram (L0/L1/L2/L3)
- Robustness: single-component vs multi-component ΔAIC delta

## Sealed Predictions

| ID | Prediction | Falsifiable by |
|---|---|---|
| P1 | Win-rate on BIG-SPARC 438 is ≥ 55% vs MOND under identical χ² definition and unchanged (K₀, m²) | Re-run pipeline; win-rate < 50% falsifies universality claim |
| P2 | α-parameter from joint fit remains within the SPARC-175 posterior envelope (α = −1.00 ± 0.46, from fs8_extended inference) | α shift > 3σ from SPARC-175 posterior falsifies the no-retuning claim |
| P3 | Regime fractions (L0/L1/L2/L3) on BIG-SPARC 438 are consistent with SPARC-175 distribution within Poisson noise | KS-test p < 0.01 between regime distributions falsifies scale-invariance |

## Data Sources (DOI-anchored)

- **EFC baseline:** DOI 10.6084/m9.figshare.32029704 (SPARC-175 single-component)
- **EFC regime framework:** SPARC-175 regime-dependent validity paper (directory: `Comprehensive-analysis-of-175-SPARC-galaxies-demonstrating-regime-dependent-validity-in-rotation-curve-modeling`)
- **External trigger:** arXiv:2411.13329 (BIG-SPARC 438 dataset)
- **Pipeline:** `scripts/sparc175_killtest_universality.py` (18.9 kB, locked seed=42)

## Symbiose status at draft time

- EMCEE α = −0.141 ± 0.208 (0.68σ), ΔAIC = 1.595
- Status: STOPPED_DEGENERACY_PERSISTS (single-component exhausted on SPARC-175)
- N1/N2/n3/n5/d2: COLLAPSED — multi-component extension is the natural next step
