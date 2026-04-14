# Energy-Flow Cosmology: Regime-Transition Fit to DESI DR2 BAO

## AI-Friendly Package

- **DOI:** [10.6084/m9.figshare.31230703](https://doi.org/10.6084/m9.figshare.31230703)
- **Version:** 1.0
- **Author:** Morten Magnusson (ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095))
- **Date:** 2026-02-02
- **License:** CC-BY-4.0

---

## Overview

Validates a minimal Energy-Flow Cosmology (EFC) regime-transition parameterization against DESI DR2 BAO using a transparent manual likelihood and a covariance-aware conditional hold-out test. The model modifies E^2(z) by a tanh transition modulated by (1+z)^{-1}, achieves a large Δχ^2 = −22.01 improvement over ΛCDM for two extra parameters, and remains consistent with Pantheon+ SNe (after M-marginalization) and cosmic chronometers. Combined BAO+CC information criteria favor the EFC transition model (ΔBIC ≈ −14.5).

## Key Result

DESI DR2 BAO strongly favor an EFC tanh-transition at z_L1L2 ≈ 1 with coupling α_L2 ≈ 0.045, yielding Δχ^2 = −22.01 for two extra parameters and surviving a covariance-aware conditional hold-out (Δχ^2_h|t = −18.65), while Pantheon+ and H(z) chronometers remain consistent.

## Sealed Predictions

| ID | Prediction | Falsifiable by |
|---|---|---|
| P1 | Independent BAO compilations (e.g., DESI DR3/DR4, BOSS/eBOSS reanalyses) fit with the same two-parameter EFC model (Δz = 0.3, Planck 2018 priors) will prefer a single transition near z_L1L2 = 1.0 ± 0.2 with a positive coupling 0.03 ≤ α_L2 ≤ 0.06 and yield ΔBIC ≤ −6 relative to ΛCDM. | Re-fitting future or independent BAO datasets with identical likelihood and priors; failure to achieve ΔBIC ≤ −6 or preference for α_L2 ≈ 0 within uncertainties falsifies this prediction. |
| P2 | After analytic M-marginalization, the supernova distance-modulus residual shape relative to ΛCDM, Δμ_shape(z), remains |Δμ_shape(z)| < 0.002 mag over 0.01 < z < 2.3 for the EFC best-fit parameters. | A Pantheon+-like reanalysis with full covariance showing |Δμ_shape(z)| ≥ 0.002 mag over any contiguous Δz ≥ 0.3 interval. |
