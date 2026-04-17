# EFC Perturbation Sector vs DES Y6 3×2pt + Cosmic Shear (DRAFT)

**Status:** DRAFT — engine exists (package `efc_perturbation_sector`), DES Y6 confrontation pending.
**Author:** Morten Magnusson (ORCID: 0009-0002-4860-5095)
**Date drafted:** 2026-04-17
**License:** CC-BY-4.0
**Anchor package:** `docs/papers/efc/efc_perturbation_sector/` (generated 2026-04-17, no DOI yet)
**Related closed gap DOI:** [10.6084/m9.figshare.32011407](https://doi.org/10.6084/m9.figshare.32011407) — Bellini–Sawicki α-function mapping

## Overview

Applies the EFC perturbation-sector engine (`efc_perturbation_engine.py`, `horndeski_consistency.py`, `lensing.py`, `sigma_eff_crossover.pdf`) to DES Y6 3×2pt (arXiv:2601.14559, S₈ = 0.789 ± 0.012) and DES Y6 cosmic shear (arXiv:2602.10065, S₈ = 0.798 NLA). Freezes the (B₀, M₀) parametrisation from the Euclid-DR1 sealed prediction (DOI 10.6084/m9.figshare.31990053), reports μ(z), Σ(z), η(z) on the DES Y6 covariance matrix, and tests EFC's prediction of μ < 1, Σ > 1 at z ≈ 0.5.

## Key Baseline (DOI-anchored)

From the Bellini–Sawicki α-mapping (DOI 32011407, CLOSED gap):
- α_T = 0
- α_M ∝ S(a)
- α_B ∝ dS/d ln a
- Stiffness response R(k, z) identified

From the Euclid-DR1 sealed prediction (DOI 31990053, FROZEN):
- B₀ = 0.02
- M₀ = 0.06
- μ(z ≈ 0.5) ≈ 0.925
- Σ(z ≈ 0.5) ≈ 1.05
- η(z ≈ 0.5) ≥ 1.2

## Known Issue (Symbiose Learning Insight, 2026-04-17T19:23:45)

- `inference_shear_kids1000`: χ²_red = **10.39** (FAIL, threshold 5.0)
- 1 EFC module flagged for attention
- Confidence = 0.7
- Recommendation: engine recalibration prior to DES Y6 confrontation

This insight was recorded **today** by the EFC research pipeline. The KiDS-1000 failure must be resolved (or formally escalated) before DES Y6 is tested, otherwise the perturbation-sector engine cannot be trusted to produce falsifiable predictions.

## Sealed Predictions (to be frozen at engine-commit time)

| ID | Prediction | Kill if |
|---|---|---|
| P1 | μ(z=0.5) < 1 on DES Y6 3×2pt | μ ≥ 1 at 3σ |
| P2 | Σ(z=0.5) ≥ 1 on DES Y6 cosmic shear | Σ < 1 at 3σ |
| P3 | η(z=0.5) ≈ 1.1 ± 0.1 | |η − 1| > 0.3 at 3σ |
| P4 | χ²_red on DES Y6 covariance < 2.0 | χ²_red > 5.0 (engine quality gate) |

## Data Sources

- **EFC engine:** `efc_perturbation_sector` package (Python, 2026-04-17 generated, pending DOI)
- **Closed gap:** DOI 32011407 (Bellini–Sawicki α-mapping)
- **Sealed DR1 prediction:** DOI 31990053 (B₀=0.02, M₀=0.06 frozen)
- **External triggers:** arXiv:2601.14559, arXiv:2602.10065
- **KiDS-Legacy baseline for cross-check:** arXiv:2503.19441, arXiv:2503.19442 (S₈ = 0.81 ± 0.02)

## Pre-conditions for publication

1. Resolve `inference_shear_kids1000` χ²_red = 10.39 (engine bug or model tension)
2. Freeze (B₀, M₀) = (0.02, 0.06) as inherited from DOI 31990053
3. Apply engine to DES Y6 covariance (public release)
4. Report μ, Σ, η on DES Y6 z-bins
