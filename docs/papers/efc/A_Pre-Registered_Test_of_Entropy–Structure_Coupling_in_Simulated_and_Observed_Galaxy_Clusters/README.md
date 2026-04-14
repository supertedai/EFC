# A Pre-Registered Test of Entropy–Structure Coupling in Simulated and Observed Galaxy Clusters

## AI-Friendly Package

- **DOI:** [10.6084/m9.figshare.31286368](https://doi.org/10.6084/m9.figshare.31286368)
- **Version:** pre-print v1
- **Author:** Morten Magnusson (ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095))
- **Date:** 2026-02-01
- **License:** CC-BY-4.0

---

## Overview

Pre-registered analysis comparing the coupling between entropy-profile steepness and cool-core state in TNG-Cluster simulations versus the ACCEPT X-ray sample. Finds a strong negative correlation between density-slope-based entropy proxy and central entropy in TNG-Cluster, opposite in sign to the positive correlation reported in ACCEPT, and registers a decisive full-profile fit to resolve remaining systematics.

## Key Result

TNG-Cluster shows a strong negative correlation between entropy-gradient proxy and central entropy (rho = -0.872), opposite in sign to the positive coupling reported in ACCEPT (rho ~ +0.36).

## Sealed Predictions

| ID | Prediction | Falsifiable by |
|---|---|---|
| P1 | Using the pre-registered Path A full-profile fit over 20–400 kpc with the Cavagnolo model, the TNG-Cluster correlation rho(alpha_fit, K0) will be negative and significant, confirming the sign flip relative to ACCEPT. | Execute the Path A fit exactly as pre-registered; compute Spearman rho(alpha_fit, K0) over all 352 halos and test for rho >= 0 at p < 0.01. |
| P2 | The negative correlation between entropy-gradient measure and K0 in TNG-Cluster will persist within each of four mass bins spanning 10^14–10^15.5 Msun. | Recompute mass-binned Spearman correlations for alpha_fit or alpha_proxy vs K0 in the predefined four M500c bins; rejection if any bin shows rho >= 0 with p < 0.05 after multiple-testing correction. |
