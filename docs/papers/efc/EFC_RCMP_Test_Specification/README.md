# EFC-ΛCDM Comparative Test Specification v1.1

## AI-Friendly Package

- **DOI:** [10.6084/m9.figshare.32080083](https://doi.org/10.6084/m9.figshare.32080083)
- **Version:** 1.1
- **Author:** Morten Magnusson (ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095))
- **Date:** 2026-04-21
- **License:** CC-BY-4.0

---

## Overview

Pre-registered, content-hash–locked protocol specifying a three-stage comparative test of Energy-Flow Cosmology (EFC) against ΛCDM on Stage-III cosmic shear data. It defines the EFC phenomenological extensions (µ, Σ), locked gate parameters, priors, scale cuts, and reporting requirements, with pixel-level verification and binding stopping/falsification rules. The specification targets DES Y6 as the primary dataset with KiDS Legacy for cross-pipeline validation using MGCAMB/MGCLASS within Cobaya or CosmoSIS.

## Key Result

Pre-registered test protocol; no empirical results are reported in this specification.

## Sealed Predictions

| ID | Prediction | Falsifiable by |
|---|---|---|
| SP1 | EFC prefers the sign quadrant A_μ < 0 and A_Σ > 0 when confronted with Stage-III cosmic shear data (DES Y6; cross-checked with KiDS Legacy). | DES Y6 fast-scan (grid over A_μ, A_Σ) and full-likelihood MCMC posteriors excluding the A_μ<0, A_Σ>0 quadrant. |
| SP2 | Setting A_μ = A_Σ = 0 or forcing g(a) → 0 (via a_t ≫ 1 or very small δa) recovers ΛCDM predictions for ξ±, C_ℓ^{\kappa\kappa}, f(z), and σ_8 to within ≤ 0.01% numerical precision. | Pixel-level forward-model verification prior to analysis. |
| SP3 | Under the VariantH slip constraint (Σ − 1) = − (μ − 1) (α = 1 locked), a one-parameter EFC extension along A_μ ∈ [−0.12, 0.0] yields any improvement localized near the EFC-predicted sign. | 1D VariantH scan of χ²(A_μ) showing no improvement or preference away from A_μ < 0. |
