# Head-to-Head ΔAIC Comparison: EFC vs Empirical Fit of arXiv:2601.00522 on SPARC-175 (DRAFT)

**Status:** DRAFT — EFC side ready, competitor implementation pending.
**Author:** Morten Magnusson (ORCID: 0009-0002-4860-5095)
**Date drafted:** 2026-04-17
**License:** CC-BY-4.0
**Anchor DOI:** [10.6084/m9.figshare.32029704](https://doi.org/10.6084/m9.figshare.32029704) — SPARC-175 multi-component closure

## Overview

Runs the competing empirical rotation-curve fit from arXiv:2601.00522 ("A New Empirical Fit to Galaxy Rotation Curves", January 2026) on the identical SPARC-175 galaxy sample, identical masking, and identical χ² definition used by EFC Kill-Test v6. Reports a galaxy-by-galaxy ΔAIC to establish which model is preferred on a per-rotation-curve basis. Uses the pre-existing EFC result (win-rate 60.2% vs MOND) as a frozen baseline and asks whether arXiv:2601.00522's claim ("outperforms MOND and CDM halos") generalises to the specific SPARC-175 regime-classified subset.

## EFC Side (DOI-anchored, ready)

- Kill-Test v6 Universality results: `results/sparc175_killtest_results.json` (118 813 B)
- ΔAIC vs latent regime: `figures/sparc175_aic_vs_latent.png`
- Regime distribution: `figures/sparc175_regime_distribution.png`
- Success by bins: `figures/sparc175_success_by_bins.png`
- Per-galaxy χ², AIC, BIC: from EFC MCMC daemon, α = −0.141 ± 0.208, ΔAIC = 1.595 (Symbiose inference status)
- Pipeline: `sparc175_killtest_universality.py` (18 963 B)

## Competitor Side (pending)

arXiv:2601.00522 provides the empirical functional form. Implementation steps:
1. Extract functional form from arXiv:2601.00522 (pending; requires paper fetch)
2. Implement in Python with matching χ² definition
3. Apply to SPARC-175 with identical masking (quality-tier ≥ 2, distance error < 20%)
4. Compute per-galaxy AIC, BIC
5. Generate per-galaxy comparison table

## Sealed Kill Criteria (committed before competitor implementation)

| # | Threshold | Outcome |
|---|---|---|
| K1 | Competitor win-rate > 55% of 175 galaxies by AIC | EFC must be re-evaluated against new empirical form |
| K2 | Competitor mean ΔAIC < −3 vs EFC-multi | Strong preference for competitor |
| K3 | Competitor requires ≥ 2× EFC's parameter count to achieve win | Occam consideration — AIC already penalises this |
| K4 | Competitor fails on > 20% of L2/L3 regime-classified galaxies | EFC regime-classification is a genuine discriminator |

## Outcome Space

| Scenario | EFC win-rate | Conclusion |
|---|---|---|
| A | > 55% | EFC retains advantage on SPARC-175 |
| B | 45–55% | Tie — claim of "outperforms" weakened |
| C | < 45% | Competitor preferred; EFC galactic-sector re-evaluation |

## Data Sources (DOI-anchored, EFC side)

- DOI 10.6084/m9.figshare.32029704 (SPARC-175 regime-dependent validity, multi-component closure)
- DOI 10.6084/m9.figshare.31047703 (SPARC175 galaxy fits, evidence-register empirical)
- DOI 10.6084/m9.figshare.31007248 (MaNGA rotation curves, cross-check)
- Kill-Test v6 pipeline (SPARC-175 package)

## Pre-conditions for publication

1. Extract and implement arXiv:2601.00522 functional form
2. Run identical χ² on SPARC-175
3. Report per-galaxy ΔAIC
4. Freeze kill criteria before data contact (done in this draft)
