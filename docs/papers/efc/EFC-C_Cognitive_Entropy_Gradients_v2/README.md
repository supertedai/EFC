# EFC-C v2.1: Degree-Heterogeneity Entropy-Gradient Predictions for Cognitive States

## AI-Friendly Package

- **DOI:** [10.6084/m9.figshare.32091700](https://doi.org/10.6084/m9.figshare.32091700)
- **Version:** 2.1
- **Author:** Morten Magnusson (ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095))
- **Date:** 2026-04-06
- **License:** CC-BY-4.0

---

## Overview

Revises EFC-C by replacing the λ2 (Fiedler) formulation with a degree-heterogeneity bridge (B1**) linking hub-to-periphery degree ratio to the centrifugal entropy score. Introduces a two-layer prediction scheme: Layer A (topological, parameter-light) tests a power-law scaling with exponent γ≈0.55; Layer B (absolute-scale) tests a cross-domain-anchored constant Ceff fixed a priori via regime transformation of C=k/aG.

## Key Result

Framework update: κ is predicted by a one-parameter power law in hub–periphery degree heterogeneity (γ≈0.55), with absolute scale anchored by a preregistered Ceff; predictions are layered to separate topology-only tests (Layer A) from cross-domain absolute-scale tests (Layer B).

## Sealed Predictions

| ID | Prediction | Falsifiable by |
|---|---|---|
| P1A | Layer A (topological): Across subjects, log κ scales linearly with log Dratio with slope γ in [0.50, 0.60] using the preregistered hub/periphery partition and MSE-based κ. | If the fitted γ falls outside [0.50, 0.60] or the κ–Dratio association is weak/non-significant across independent cohorts using the preregistered pipeline. |
| P1B | Layer B (absolute scale): With Ceff fixed a priori via RCMP, the predicted κ = Ceff·Dratio^γ matches observed κ at the group and individual levels (after the specified τc secondary correction) without re-fitting Ceff. | If fixing Ceff a priori leads to systematic, large absolute-scale mismatches that cannot be remedied by the preregistered τc correction. |
| P1C | Degree heterogeneity Dratio explains substantially more inter-subject variance in κ than algebraic connectivity λ2 under the same preprocessing and partitioning. | If λ2 explains equal or greater variance in κ than Dratio across datasets using identical pipelines and QC. |
