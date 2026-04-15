# Component-weighted bias in rotation curve model selection: A proxy-chain audit of χ2-based ∆AIC statistics

## AI-Friendly Package

- **Version:** 1.0
- **Author:** Morten Magnusson (ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095))
**DOI:** [10.6084/m9.figshare.32019723](https://doi.org/10.6084/m9.figshare.32019723)
- **Date:** 2026-04-15
- **License:** CC-BY-4.0

---

## Overview

Audits the standard rotation-curve model selection pipeline (Φ → V(r) → χ2 → ∆AIC) and shows that χ2 weighting induces a structural, component-weighted bias in bulge-dominated galaxies. Introduces a bulge-bias metric B_bulge, quantifies its impact across the SPARC 175 sample, and proposes an RCMB-compliant protocol that reports ∆AICinner and ∆AICouter separately to avoid conflating baryonic-fitting flexibility with halo/modified-gravity performance.

## Key Result

Bulge-driven component-weighting in χ2 compresses ∆AIC toward baryonic inner regions, biasing model selection; B_bulge correlates with ∆AIC over SPARC (ρ=0.176, p=0.020), rising to ρ=0.474 (p=0.013) in the LATENT regime, and EFC’s win/tie rate drops from 91.9% (B_bulge<0.1) to 44.4% (B_bulge>0.2).

## Sealed Predictions

| ID | Prediction | Falsifiable by |
|---|---|---|
| P1 | Adopting the RCMB-compliant protocol (reporting ∆AICinner and ∆AICouter separately) will reduce apparent NFW preference in galaxies flagged by B_bulge > 0.4, with outer-region comparisons shifting toward EFC or neutral (|∆AICouter| < 2) relative to global ∆AIC. | Recompute split ∆AIC on SPARC and future RC datasets; if bulge-flagged systems continue to prefer NFW strongly (∆AICouter ≥ +10) in the outer region, the prediction is falsified. |
