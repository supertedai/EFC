# EFC-C v2.1: Degree-Heterogeneity Entropy-Gradient Predictions for Cognitive States

## AI-Friendly Package

- **DOI:** [10.6084/m9.figshare.32091700](https://doi.org/10.6084/m9.figshare.32091700)
- **Version:** 2.1
- **Author:** Morten Magnusson (ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095))
- **Date:** 2026-04-01
- **License:** CC-BY-4.0

---

## Overview

Revision of the EFC-C framework re-anchoring entropy-gradient predictions from the Fiedler eigenvalue to hub-to-periphery degree heterogeneity. Introduces a one-parameter power-law κ = C_eff · D_ratio^γ with γ ≈ 0.55 and separates predictions into Layer A (topological, invariant) and Layer B (absolute-scale, conditional on cross-domain constant transfer via RCMP).

## Key Result

Replaces the λ2-based prediction with a degree-heterogeneity power-law (κ = Ceff · Dratio^γ), with γ constrained to 0.50–0.60 and Ceff fixed via RCMP; predictions are separated into Layer A (topological) and Layer B (absolute-scale).

## Sealed Predictions

| ID | Prediction | Falsifiable by |
|---|---|---|
| P1-LayerA | Across individuals, the centrifugal entropy score κ scales as a power law of the hub-to-periphery degree ratio: log κ = log Ceff + γ log Dratio with γ in [0.50, 0.60]. | Linear fit on log–log scale yields γ outside [0.50, 0.60] or cross-subject R^2 < 0.50 despite adequate SNR and matched hub/periphery partition. |
| P2-LayerB | With Ceff fixed a priori by RCMP (no re-fitting on neural data), absolute κ values predicted by κ = Ceff · Dratio^γ lie within propagated uncertainty bounds across HCP-like datasets. | Mean absolute fractional error > 0.30 across subjects or systematic bias in residuals that cannot be removed by the prespecified secondary τc correction. |
| P3-Comparator | Algebraic connectivity (λ2) does not outperform Dratio in explaining inter-subject variance in κ. | In multiple independent datasets, λ2-based models consistently achieve higher R^2 than Dratio-based models for κ prediction under identical preprocessing and partitions. |
| P4-Timescale | The τc contribution is a secondary correction O(τc/τH) that does not dominate κ variance. | After applying the prespecified autocorrelation-based protocol, τc-related terms account for >30% of explained variance or are required to rescue otherwise invalid Layer A fits. |
| P5-TopologyLock | Topological alignment holds: κ and Dratio computed with the same hub/periphery partition are robust to reasonable variations of hub/periphery thresholds. | Small, reasonable changes to hub/periphery thresholds (e.g., hubs 8–12%, periphery 25–35%) cause >25% swings in fitted γ or destroy the κ–Dratio scaling. |
