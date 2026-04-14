# Directional Lensing Residuals at Cluster Merger Shock Fronts

## AI-Friendly Package

- **DOI:** [10.6084/m9.figshare.31288063](https://doi.org/10.6084/m9.figshare.31288063)
- **Version:** 1.0
- **Author:** Morten Magnusson (ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095))
- **Date:** 2026-02-07
- **License:** CC-BY-4.0

---

## Overview

Pre-registered observational pipeline to test for a directional asymmetry in lensing convergence residuals across galaxy cluster merger shock fronts. It defines a locally normalized estimator Asig using a rotation null to isolate shock-locked signals and fits a mass+gas-pressure model outside the shock aperture to avoid circularity. Mock Bullet Cluster analogues show correct sign separation between EFC-like and ΛCDM cases with zero false positives, and the pipeline is ready for JWST κ-maps combined with Chandra thermodynamics.

## Key Result

Pre-registered pipeline validated on synthetic Bullet Cluster analogues shows correct sign separation between EFC-like (positive) and ΛCDM-like (negative/null) cases with zero false positives; ready for JWST+Chandra application.

## Sealed Predictions

| ID | Prediction | Falsifiable by |
|---|---|---|
| P1 | At well-resolved merger shock fronts (e.g., Bullet Cluster, Abell 2146), the pre-shock (low-entropy) side will exhibit a positive directional convergence residual, yielding A_sig > 0 and preferably A_sig > 3 with p_rot < 0.05 when JWST κ-maps are combined with Chandra thermodynamics using the pre-registered pipeline. | Applying the pipeline to JWST κ-maps and Chandra thermodynamic maps at published shock fronts and measuring A_sig ≤ 0 or failing to reach significance (p_rot ≥ 0.05) across multiple fronts. |
