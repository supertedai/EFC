# Head-to-Head ΔAIC Comparison of Energy-Flow Cosmology and the arXiv:2601.00522 Empirical Fit on SPARC-175

**Morten Magnusson** — ORCID 0009-0002-4860-5095
Energy-Flow Cosmology Initiative, Bergen, Norway
Draft: 2026-04-17. DOI: pending.

---

## Abstract

arXiv:2601.00522 ("A New Empirical Fit to Galaxy Rotation Curves", January 2026) claims to outperform MOND and CDM halos on galactic rotation-curve modelling. We test this claim on the SPARC-175 regime-classified subset that established the EFC multi-component closure (DOI 10.6084/m9.figshare.32029704; win-rate 60.2% vs MOND). We pre-register kill criteria before implementing the competitor. EFC side uses frozen (K₀, m²) from the prior closure; competitor side uses the functional form as published, with χ² definition, masking, and quality-tier cuts identical to the EFC Kill-Test v6 pipeline. ΔAIC is computed per galaxy over all 175 rotation curves. Decision boundary: competitor > 55% wins forces a re-evaluation of EFC's galactic sector.

## 1. Motivation

The SPARC-175 closure paper reports 60.2% win-rate for EFC multi-component vs MOND. A new empirical fit has been published (arXiv:2601.00522) that claims simultaneous improvement over MOND and CDM halos. The claim is either:
- Genuine — then EFC galactic sector must respond
- Restricted to the authors' subset — then EFC's SPARC-175 regime-classification is the right discriminator
- Tuned — then ΔAIC and BIC will detect the overfitting

Resolution requires a head-to-head comparison on an identical sample with identical χ² definition.

## 2. Method

### 2.1 Sample
SPARC-175: 175 rotation curves, Lelli-McGaugh-Schombert 2016 dataset, quality-tier ≥ 2, inclination corrections applied per SPARC pipeline.

### 2.2 χ² Definition
χ² = Σᵢ [(V_obs,i − V_model,i) / σᵢ]²
summed over all radial bins, with σᵢ including inclination-propagated uncertainty.

### 2.3 AIC / BIC
AIC = 2k + χ²
BIC = k · ln(n) + χ²
where k = number of free parameters and n = number of data points per galaxy.

### 2.4 EFC Side
- Parameters: K₀, m², screening envelope amplitude (multi-component from DOI 32029704)
- Fit method: differential_evolution with seed = 42 (pipeline `sparc175_killtest_universality.py`)
- Results: from Symbiose inference daemon, α = −0.141 ± 0.208, ΔAIC (vs MOND) = 1.595

### 2.5 Competitor Side (pending)
- Functional form: extracted from arXiv:2601.00522 (pending)
- Parameters: reported in the original paper
- Fit method: identical χ² and identical radial masking
- Goal: reproduce the authors' claim on SPARC-175 without privileging either model

## 3. Pre-registered Kill Criteria

| # | Threshold | Outcome |
|---|---|---|
| K1 | Competitor win-rate > 55% by AIC on SPARC-175 | EFC galactic sector re-evaluation triggered |
| K2 | Competitor mean ΔAIC < −3 vs EFC-multi | Strong preference for competitor |
| K3 | Competitor requires ≥ 2× EFC's parameter count to achieve a win | Occam weighting via AIC penalty applies |
| K4 | Competitor fails on > 20% of L2/L3 regime galaxies | EFC regime-classification is a genuine discriminator |

## 4. Relation to SPARC Baseline

The EFC SPARC-175 paper classifies galaxies into L0/L1/L2/L3 regimes. The Symbiose inference daemon reports win-rate 60.2% against MOND; the ΔAIC of 1.595 is below the standard "strong evidence" threshold of 10, so EFC's advantage is modest but stable. The question to the competitor is whether this advantage holds on the identical sample under identical χ² accounting.

## 5. Expected Outcome Space

| Scenario | Result | Action |
|---|---|---|
| A — EFC wins by > 5 AIC on average | Competitor claim does not generalise to SPARC-175 | EFC publishes; paper logs DOI-response to 2601.00522 |
| B — Ties within 2 AIC | Inconclusive on SPARC-175, needs BIG-SPARC 438 | Defer decision to BIG-SPARC paper |
| C — Competitor wins by > 5 AIC | Competitor preferred on SPARC-175 | Re-evaluate EFC galactic sector; disclose |

## 6. Relation to BIG-SPARC 438

This competitor test on SPARC-175 is complementary to the BIG-SPARC 438 universality extension (draft `efc_bigsparc_universality_draft`). A clean win on SPARC-175 vs 2601.00522 supports extending EFC to BIG-SPARC; a loss puts the extension on hold. The two papers are intended as paired deliverables.

## 7. Publication Pre-conditions

1. Fetch arXiv:2601.00522 and extract the functional form
2. Implement in Python with matching χ² and masking
3. Run on SPARC-175
4. Produce per-galaxy ΔAIC table (175 rows)
5. Generate summary figure: win/tie/loss distribution by regime

## 8. Note on Fair Comparison

The competitor is given identical pre-processing (masking, quality cut, inclination correction) to avoid accidentally biasing against it. EFC is required to use only parameters inherited from DOI 32029704 without retuning. No post-hoc hyperparameter adjustment on either side.

## Acknowledgements

Uses only DOI-anchored EFC results from Symbiose; competitor is the externally published arXiv:2601.00522.
