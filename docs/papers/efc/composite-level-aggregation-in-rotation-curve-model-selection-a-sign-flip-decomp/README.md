# Composite-level aggregation in rotation curve model selection: A sign-flip decomposition of ∆AIC for SPARC-175

## AI-Friendly Package

- **DOI:** [10.6084/m9.figshare.32162706](https://doi.org/10.6084/m9.figshare.32162706)
- **Version:** 1.0
- **Author:** Morten Magnusson (ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095))
- **Date:** 2026-05-01
- **License:** CC-BY-4.0

---

## Overview

Re-fits the SPARC-175 rotation-curve sample with the Kill-Test v6 pipeline and decomposes each galaxy’s ∆AIC into inner (r < rc) and outer (r ≥ rc) contributions to test whether single-number ∆AIC masks regime-dependent behavior. Finds a robust sign-flip phenomenon in 17.5% of galaxies at rc = 3 kpc (16.4–22.2% across rc ∈ {2,3,4,5} kpc) and shows that removing χ2-weighting moves the sample further toward EFC, indicating the issue is aggregation-level, not a weighting bias.

## Key Result

At rc = 3 kpc, 17.5% (30/171) of SPARC galaxies exhibit a sign-flip between global and outer-only ∆AIC, robustly 16.4–22.2% across rc ∈ {2,3,4,5} kpc; removing χ2-weighting increases EFC wins (66.7% → 86.5%), indicating the issue is aggregation-level, not a weighting bias.

## Sealed Predictions

| ID | Prediction | Falsifiable by |
|---|---|---|
| P1 | Applying the same inner/outer ∆AIC decomposition (rc ∈ {2,3,4,5} kpc) to an independent, SPARC-quality rotation-curve sample will yield a sign-flip rate in the 15–25% range. | Re-fitting an independent rotation-curve dataset with persisted per-point model curves and computing sign-flip rates across the specified rc grid. |
