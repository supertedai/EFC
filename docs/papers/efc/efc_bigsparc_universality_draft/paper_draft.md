# Multi-component Energy-Flow Cosmology Universality on the BIG-SPARC 438-Galaxy Corpus

**Morten Magnusson** — ORCID 0009-0002-4860-5095
Energy-Flow Cosmology Initiative, Bergen, Norway
Draft: 2026-04-17. DOI: pending.

---

## Abstract

We extend Energy-Flow Cosmology (EFC) Kill-Test v6 Universality from SPARC-175 (DOI 10.6084/m9.figshare.32029704; 60.2% win-rate vs MOND, single-component) to the BIG-SPARC 438-galaxy corpus (arXiv:2411.13329). The pipeline freezes (K₀, m²) at their SPARC-175 posteriors and adds an explicit multi-component decomposition (disc stars, bulge, gas, screening envelope). We pre-register the falsification thresholds: win-rate ≥ 55%, α within 3σ of the SPARC-175 posterior envelope, regime-fraction KS-distance p > 0.01. The paper is a draft pending the pipeline re-run; all hyperparameters and kill-thresholds are committed prior to data contact.

## 1. Motivation

The EFC MCMC inference daemon reports cycle status `STOPPED_DEGENERACY_PERSISTS` with α = −0.141 ± 0.208 (0.68σ) and ΔAIC = 1.595 on the single-component SPARC-175 fit. The five nested models N1, N2, n3, n5 and d2 have all collapsed — single-component EFC has exhausted its information content on 175 galaxies. The natural question the single-component closure leaves open is whether multi-component decomposition on a 2.5× larger sample (BIG-SPARC 438) recovers the win-rate without retuning.

## 2. Data

| Source | Content | DOI / Ref |
|---|---|---|
| SPARC-175 baseline | 175 rotation curves, regime-classified L0–L3 | DOI 10.6084/m9.figshare.32029704 |
| BIG-SPARC 438 | Expanded catalog, 438 galaxies, THINGS+LITTLE THINGS+SPARC+WALLABY-DR2 | arXiv:2411.13329 |
| Pipeline code | `sparc175_killtest_universality.py`, seed=42, differential_evolution | SPARC-175 package (18 963 bytes) |

## 3. Method

1. Load BIG-SPARC 438 rotation curves (public-release format).
2. Apply the identical masking used on SPARC-175 (quality-tier ≥ 2, distance uncertainty < 20%).
3. For each galaxy, fit four models with identical χ² definition:
   - EFC single-component (baseline)
   - EFC multi-component (disc + bulge + gas + screening)
   - MOND-simple (competitor)
   - NFW (cosmological prior on concentration)
4. Record per-galaxy χ²_red, AIC, BIC, and regime-class.
5. Freeze (K₀, m²) = SPARC-175 posterior median; no retuning.

## 4. Pre-registered Kill Criteria

Primary kill-triggers (committed before data contact):

| # | Threshold | Outcome if triggered |
|---|---|---|
| K1 | EFC-multi win-rate < 50% on 438 galaxies | Falsifies universality claim |
| K2 | α posterior shift > 3σ from SPARC-175 | Falsifies no-retuning commitment |
| K3 | Regime-fraction KS p < 0.01 vs SPARC-175 | Falsifies scale-invariance hypothesis |
| K4 | ΔAIC(EFC-multi vs EFC-single) < 0 on > 30% of galaxies | Multi-component addition is unjustified |

## 5. Expected Outcomes (model-independent)

The draft is intentionally agnostic on the expected win-rate; the SPARC-175 result of 60.2% provides a Bayesian prior centred at the single-component baseline. The multi-component extension is expected to move the regime boundaries but not the baseline α, which is a structural property of the EFC T(S) susceptibility.

## 6. Relation to Other EFC Programmes

This paper is the galactic-sector counterpart to the sealed freeze_20260218 DESI DR2 predictions (DOI 10.6084/m9.figshare.32013156): both take the SPARC-175 / sealed-DESI posteriors as frozen priors and ask whether the next wave of public data corroborates them. A win-rate collapse here but DESI DR2 confirmation would falsify the scale-invariance claim; simultaneous collapse of both would falsify the framework at the regime-transition level.

## 7. Open Items

- Pipeline re-run on BIG-SPARC 438 (estimated 2–4 h on single node with seed=42)
- Multi-component implementation: the SPARC-175 pipeline currently calls a single-component screening envelope; the multi-component extension re-uses `horndeski_consistency.py` from the EFC perturbation-sector package
- AIC/BIC tables and regime histograms will replace this section on pipeline completion

## Acknowledgements

Uses only DOI-anchored EFC data from the Symbiose RAG store as of 2026-04-17. No external collaborations required for pipeline execution.
