# Component-weighted bias in rotation curve model selection: A proxy-chain audit of χ2-based ∆AIC statistics

## AI-Friendly Package

- **Version:** 1.0 (preprint; v2 with full SPARC empirical core in preparation)
- **Author:** Morten Magnusson (ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095))
**DOI:** [10.6084/m9.figshare.32019723](https://doi.org/10.6084/m9.figshare.32019723)
- **Date:** 2026-04-15
- **License:** CC-BY-4.0

---

## Overview

This paper applies the **Regime-Consistent Measurement Principle (RCMP)** —
a measurement is valid only within the regime where the instrument, the
observable, and the theory share overlapping validity domains
([RCMP framework, DOI 10.6084/m9.figshare.31222900](https://doi.org/10.6084/m9.figshare.31222900))
— to the standard rotation-curve model-selection pipeline (Φ → V(r) → χ2 → ∆AIC).

The proxy chain is shown to violate RCMP through three failure modes that
operate simultaneously on bulge-dominated systems:

1. **Regime drift.** σ_i⁻²-weighting shifts the χ² measurement epicentre
   toward small-radius, low-σ points, so the statistic no longer evaluates
   the halo regime that the comparison purports to test.
2. **Component contamination.** V_total² mixes V_bulge with V_model in
   quadrature, so χ² absorbs baryonic-fitting flexibility into what is
   reported as a halo/modified-gravity preference.
3. **Compression loss.** A single global ∆AIC compresses inner and outer
   information into one scalar, hiding regime-specific structure that an
   RCMP-compliant audit must surface.

We introduce a bulge-bias metric *B_bulge*, quantify its impact across the
SPARC 175 sample, and propose an RCMP-compliant protocol that reports
∆AIC_inner and ∆AIC_outer separately to avoid conflating baryonic-fitting
flexibility with halo / modified-gravity performance. The proxy-chain audit
is therefore not a stand-alone diagnostic but a worked application of RCMP
on a benchmark dataset (SPARC).

## Key Result

Bulge-driven component-weighting in χ2 compresses ∆AIC toward baryonic inner regions, biasing model selection; B_bulge correlates with ∆AIC over SPARC (ρ=0.176, p=0.020), rising to ρ=0.474 (p=0.013) in the LATENT regime, and EFC’s win/tie rate drops from 91.9% (B_bulge<0.1) to 44.4% (B_bulge>0.2).

## Scope and Status

- **Scope.** The critique targets the *use* of χ²-based ∆AIC under
  RCMP-violating conditions, not AIC as an information criterion. The
  inner/outer split uses r_c = 3 kpc as a dominance approximation — bulge
  dominates inner, halo dominates outer; both components contribute at all
  radii, and a sensitivity analysis over r_c ∈ [2, 5] kpc is part of v2.
- **Status (v1).** Methodology, metrics (B, B_bulge), and the RCMP-compliant
  protocol are formalised. Headline statistics (Spearman ρ, win-rate splits)
  are reported; the systematic sign-flip demonstration across the full SPARC
  sample and the r_c-sensitivity test are pending v2 (`compute_bias_metrics.py`
  on the full SPARC 175 catalogue).

## Sealed Predictions

| ID | Prediction | Falsifiable by |
|---|---|---|
| P1 | Adopting the RCMP-compliant protocol (reporting ∆AICinner and ∆AICouter separately) will reduce apparent NFW preference in galaxies flagged by B_bulge > 0.4, with outer-region comparisons shifting toward EFC or neutral (|∆AICouter| < 2) relative to global ∆AIC. | Recompute split ∆AIC on SPARC and future RC datasets; if bulge-flagged systems continue to prefer NFW strongly (∆AICouter ≥ +10) in the outer region, the prediction is falsified. |
