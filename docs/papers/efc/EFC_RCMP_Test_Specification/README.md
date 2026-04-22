# EFC-ΛCDM Comparative Test Specification v1.1: Pre-Registered Implementation Protocol for DES Y6 and KiDS Legacy Cosmic Shear

## AI-Friendly Package

- **DOI:** [10.6084/m9.figshare.32080083](https://doi.org/10.6084/m9.figshare.32080083)
- **Version:** v1.1
- **Author:** Morten Magnusson (ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095))
- **Date:** 2026-04-21
- **License:** CC-BY-4.0

---

## Overview

Pre-registered, content-hash–locked methodology specifying a three-stage, falsifiable comparative test of Energy-Flow Cosmology (EFC) versus ΛCDM using Stage-III cosmic shear. It defines the phenomenological EFC extensions (µ, Σ), fixed gates and scales, priors, scan procedures, nuisance handling, scale cuts, reporting outputs, and binding stopping/falsification rules for DES Y6 and KiDS Legacy pipelines.

## Key Result

This paper provides a sealed, reproducible test protocol (not results) for comparing EFC against ΛCDM on DES Y6 and KiDS Legacy cosmic shear, including fixed gates, priors, grid scans, MCMC, and binding stopping/falsification rules.

## Sealed Predictions

| ID | Prediction | Falsifiable by |
|---|---|---|
| SP1 | EFC predicts the preferred phenomenological quadrant A_\mu < 0 and A_\Sigma > 0 when tested on Stage-III cosmic shear with the locked gate parameters (a_t=0.7, \delta a=0.08, k_c=0.05 h/Mpc). | Full DES Y6 and KiDS Legacy likelihood analyses showing statistically significant preference for A_\mu \ge 0 and/or A_\Sigma \le 0. |
| SP2 | At A_\mu = A_\Sigma = 0 the EFC phenomenological model reduces identically to ΛCDM, matching forward-model outputs (ξ±, C_\ell^{\kappa\kappa}, f(z), \sigma_8) within ≤0.01% numerical precision. | Pixel-level equivalence check in the likelihood pipeline; any measurable deviation indicates an implementation error and invalidates the run. |
| SP3 | A background-fixed fast-scan around the ΛCDM best-fit should exhibit a measurable response in DES Y6 ξ±(θ) along the EFC-like direction if the data are sensitive to the (A_\mu, A_\Sigma) perturbations. | Fast-scan grid returning |Δχ^2_best-fit| < 1 with negligible gradient at the origin, implying sub-sensitivity at this stage (protocol stop condition). |
| SP4 | Optional VariantH slip test with Σ = 1 − (µ − 1) (α = 1 locked) provides a one-parameter EFC extension expected to prefer A_\mu < 0 if EFC-like perturbations are supported. | 1D VariantH scan and MCMC preferring A_\mu \ge 0 or yielding no improvement relative to ΛCDM under fiducial cuts. |
