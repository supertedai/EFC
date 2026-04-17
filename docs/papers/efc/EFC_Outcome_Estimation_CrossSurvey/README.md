# Expected Outcomes for Energy-Flow Cosmology Cross-Survey Invariance and BIG-SPARC Tests

## AI-Friendly Package

- **DOI:** [10.6084/m9.figshare.32045592](https://doi.org/10.6084/m9.figshare.32045592)
- **Version:** 1.0
- **Author:** Morten Magnusson (ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095))
- **Date:** 2026-04-17
- **License:** CC-BY-4.0

---

## Overview

Pre-data working note estimating expected outcomes for the pre-registered Energy-Flow Cosmology (EFC) cross-survey invariance tests (P1–P8). Using the SPARC-175 Kill-Test v6 baseline and structural AIC/BIC analysis, it projects Tier-1 (THINGS, LITTLE THINGS) and Tier-2 (WALLABY DR2) win rates, overlap consistency, regime fractions, and the likely role of BIG-SPARC as the decisive tiebreaker. The most probable result is partial support (Scenario B), with modest AIC/BIC win rates and robust overlap on decisive cases.

## Key Result

Pre-data projection favors Scenario B (partial support): Tier-1 AIC WR ≈ 58% (BIC ≈ 53%), WALLABY AIC WR ≈ 43% (BIC ≈ 35%), overlap consistency 10–12/14, with decisive SPARC wins expected to remain robust; BIG-SPARC is anticipated to be the decisive tiebreaker.

## Sealed Predictions

| ID | Prediction | Falsifiable by |
|---|---|---|
| P1 | Cross-survey k invariance (proxied by Tier-1 non-SPARC AIC win rate) holds with WR > 55% and BIC remaining above 50%. | Compute WR on THINGS+LITTLE THINGS per preregistered pipeline; if AIC WR ≤ 55% or BIC WR ≤ 50% with Wilson 95% CI not overlapping thresholds, prediction fails. |
| P2 | Overlap consistency: for the 14 SPARC–THINGS galaxies, the model-preference sign and strength agree in ≥ 10/14, with decisive cases showing |ΔAIC_SP−ΔAIC_TH| < 3. | Count consistent outcomes; if < 10/14 or systematic flips of decisive cases occur, prediction fails. |
| P3 | Regime fractions (FLOW / TRANSITION / LATENT) in Tier-1 match SPARC baseline within ±15 percentage points. | Estimate regime fractions via χ2-ratio proxy; if any regime deviates by > 15 pp from SPARC baseline (41.5%, 49.1%, 9.4%), prediction fails. |
| P4 | WALLABY DR2 AIC win rate for EFC is ≥ 45%. | Compute AIC WR on WALLABY DR2; if WR < 45% with Wilson 95% CI upper bound ≤ 45%, prediction fails. |
| P5 | BIG-SPARC yields k_BIG = 0.415 ± 0.015, consistent with the SPARC baseline (k = 0.415 ± 0.029) within 3σ. | Fit k on BIG-SPARC; if |k_BIG − 0.415| > 3σ_combined, prediction fails. |
| P6 | BIG-SPARC global win rate is ≥ 50% (AIC and corroborated by BIC). | Compute AIC/BIC WR on BIG-SPARC; if both metrics yield WR < 50% with Wilson 95% CI upper ≤ 50%, prediction fails. |
| P7 | FLOW-regime galaxies in BIG-SPARC show WR ≥ 85%. | Stratify BIG-SPARC by regime; if FLOW WR < 85% with Wilson 95% CI lower < 85%, prediction fails. |
| P8 | No secondary dependence of k on galaxy properties (e.g., mass, size, gas fraction) at > 3σ significance. | Regression or hierarchical modeling on BIG-SPARC; detection of > 3σ correlation between k and secondary properties falsifies. |
