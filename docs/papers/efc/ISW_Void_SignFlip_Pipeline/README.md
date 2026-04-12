# ISW Void Sign-Flip Observational Pipeline

## AI-Friendly Package

- **DOI:** [10.6084/m9.figshare.31990212](https://doi.org/10.6084/m9.figshare.31990212)
- **Theory base:** [10.6084/m9.figshare.31942677](https://doi.org/10.6084/m9.figshare.31942677) (v2.1)
- **Version:** 1.5
- **Author:** Morten Magnusson (ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095))
- **Affiliation:** Symbiose Research, Sandnes, Norway
- **Date:** 2026-04-12
- **License:** CC-BY-4.0

---

## Overview

Complete 6-stage data pipeline for observationally testing the EFC void ISW sign-flip prediction. The pipeline confronts the theoretical prediction (v2.1) with publicly available void catalogs (DESIVAST DR1), Planck PR4 CMB temperature and lensing maps, and large-scale structure survey data.

## Key Prediction

In EFC, gravitational coupling mu depends on local density. In voids, this produces a Rees-Sciama term that opposes the standard cold ISW signal. For sufficiently deep voids (delta < delta_c ~ -0.8), the hot RS term dominates and the ISW signal flips sign.

**This is a qualitative prediction: LCDM cannot produce sign-flips at any void depth.**

## Sealed Predictions

| ID | Prediction | Kill criterion |
|----|-----------|---------------|
| P1 | Depth turnover: A_ISW peaks then flips at delta_c ~ -0.8 | No sign-flip at any delta |
| P2 | Scale: larger R_v amplifies RS, R_v > 100 h^-1 Mpc | No scale trend |
| P3 | Redshift: stronger signal at z < 0.5 | No z-evolution |

## Pipeline Stages

1. **Void catalog ingestion** -- DESIVAST DR1, quality cuts, depth/scale/redshift binning
2. **CMB map preparation** -- Planck PR4, inpainting, filtering
3. **Stacking** -- Oriented aperture photometry, compensated top-hat filter
4. **Amplitude extraction** -- A_ISW(delta) per depth bin, bootstrap errors
5. **Statistical tests** -- Sign-flip detection, depth trend, scale/redshift dependence
6. **RCMB compliance** -- Distribution, epicenter, void-finder, line-of-sight tests

## Data Sources

- DESIVAST DR1 (~1500 voids, z < 0.24)
- Planck PR4 SMICA/SEVEM/NILC/Commander (N_side = 2048)
- Planck 2018 lensing convergence map
- BOSS DR12 + DES Y3 supervoid catalogs (secondary)

## Hardware Requirements

Single workstation, ~32 GB RAM.
