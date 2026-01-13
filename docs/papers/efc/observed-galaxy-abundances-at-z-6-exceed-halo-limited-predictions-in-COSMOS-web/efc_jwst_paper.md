# Systematic Excess of Massive Galaxies at z > 6 in COSMOS-Web: Empirical Constraints on Early Structure Formation

**Authors:** Morten Magnusson¹  
**Affiliations:** ¹Independent Researcher, ORCID: 0009-0002-4860-5095

---

## Abstract

We present a systematic analysis of 26,288 high-redshift (z > 5) galaxies from the COSMOS2025 catalog, the definitive data release of the JWST COSMOS-Web survey covering 0.54 deg². We compare observed number densities of massive galaxies (log M★/M☉ > 9) against forward-modelled ΛCDM predictions derived from the stellar mass functions of Behroozi et al. (2019), adopting conservative upper-envelope expectations that account for intrinsic scatter and survey selection. We find a systematic excess that increases monotonically with redshift: from ~20× at z = 5–6 to ~100–1000× at z = 8–10. While formal Poisson significances are high, we emphasize that the key result is the order-of-magnitude discrepancy, not precise significance values. Independent support comes from the specific star formation rate (sSFR), which correlates positively with redshift (Spearman ρ = 0.33, p < 0.001), indicating elevated activity in earlier epochs—a trend independent of stellar mass function normalization. We quantify systematic uncertainties from photometric redshift contamination, stellar mass estimates, and cosmic variance, demonstrating that their combined effect cannot reduce the observed excess below ~20× at z > 8. These results establish a robust empirical tension with standard ΛCDM forward predictions that persists under conservative assumptions.

**Keywords:** galaxies: high-redshift — galaxies: evolution — cosmology: observations — early universe

---

## 1. Introduction

*[To be expanded]*

---

## 2. Data

### 2.1 The COSMOS2025 Catalog

We use the COSMOS2025 catalog (Shuntov et al. 2025), the definitive public data release of the JWST COSMOS-Web survey (Casey et al. 2023). The survey covers 0.54 deg² in four NIRCam filters (F115W, F150W, F277W, F444W) to 5σ depths of 27.5–28.2 AB mag.

The catalog provides photometric redshifts and stellar masses from LePhare SED fitting (Arnouts et al. 1999; Ilbert et al. 2006), with photometric redshift accuracy σ_MAD = 0.012 at m_F444W < 28 for spectroscopically confirmed sources to z ~ 9.

### 2.2 Sample Selection

From the parent catalog of ~700,000 sources, we select galaxies with:

1. Photometric redshift z_phot > 5
2. Valid stellar mass estimate (mass_med > 0, excluding flagged values)
3. Valid star formation rate estimate

This yields 26,288 galaxies for analysis.

---

## 3. Methods

### 3.1 ΛCDM Baseline Predictions

Establishing a robust baseline is critical for quantifying any tension with standard cosmology. We adopt predictions from Behroozi et al. (2019), which provide forward-modelled stellar mass functions calibrated to pre-JWST observations and extrapolated to high redshift using empirically-constrained halo–galaxy connection models.

**Table A.** Adopted ΛCDM number density predictions (galaxies with log M★/M☉ > 9 per deg²)

| Redshift | n_ΛCDM (deg⁻²) | Basis |
|----------|----------------|-------|
| 5–6      | 200            | Behroozi+19 SMF, upper envelope |
| 6–7      | 80             | Behroozi+19 SMF, upper envelope |
| 7–8      | 25             | Behroozi+19 SMF, upper envelope |
| 8–9      | 8              | Behroozi+19 SMF, upper envelope |
| 9–10     | 2              | Behroozi+19 SMF, upper envelope |
| 10–12    | 0.5            | Extrapolated, high uncertainty |

**Important caveats:**

1. These represent **conservative upper-envelope estimates**—i.e., we deliberately adopt high-end ΛCDM expectations to avoid overstating any tension.

2. At z > 10, theoretical predictions carry order-of-magnitude uncertainty due to poorly constrained star formation efficiency and feedback at early times.

3. We do not claim these are "the" ΛCDM prediction, but rather a defensible reference point against which systematic trends can be evaluated.

### 3.2 Specific Star Formation Rate

We compute the specific star formation rate as:

    log(sSFR / Gyr⁻¹) = log(SFR) − log(M★) + 9

where SFR and M★ are taken from LePhare SED fitting outputs (sfr_med and mass_med, both in logarithmic solar units).

The sSFR provides an independent diagnostic that is less sensitive to absolute mass calibration than number counts, as systematic mass errors partially cancel in the ratio.

---

## 4. Results

No physical interpretation is assumed in this section; results are presented as empirical trends relative to the adopted ΛCDM reference. All quantities are derived directly from the COSMOS2025 catalog.

### 4.1 Number Density Evolution

We compute the observed number density of galaxies with log(M★/M☉) > 9 in six redshift bins from z = 5 to z = 12. Table 1 presents the comparison with our adopted ΛCDM baseline.

**Table 1.** Observed vs. reference number densities of massive galaxies (log M★/M☉ > 9)

| Redshift | N_obs | n_obs (deg⁻²) | n_ΛCDM (deg⁻²) | Ratio |
|----------|-------|---------------|----------------|-------|
| 5–6      | 2,505 | 4,639         | 200            | 23×   |
| 6–7      | 1,720 | 3,185         | 80             | 40×   |
| 7–8      | 1,673 | 3,098         | 25             | 124×  |
| 8–9      | 1,120 | 2,074         | 8              | 259×  |
| 9–10     | 571   | 1,057         | 2              | 529×  |
| 10–12    | 248   | 459           | 0.5            | 919×  |

**Notes:** n_obs = N_obs / 0.54 deg². Ratios rounded to three significant figures. Galaxies at z > 12 (N = 610) are excluded from primary analysis due to substantially higher photometric uncertainties; see Appendix A for completeness.

Three features are evident from Table 1:

1. **Systematic excess**: The observed number density exceeds the ΛCDM reference in every redshift bin.

2. **Monotonic scaling**: The ratio increases monotonically with redshift, from ~23× at z = 5–6 to ~920× at z = 10–12.

3. **Order-of-magnitude discrepancy**: The key result is not a marginal tension but a factor of 100–1000× excess at z > 8, far exceeding plausible systematic uncertainties (Section 5).

We deliberately avoid reporting formal σ-significances, as at these ratios the results are dominated by systematic rather than statistical uncertainties. The meaningful statement is that the discrepancy is **order-of-magnitude**, not that it exceeds some σ-threshold.

### 4.2 Specific Star Formation Rate Evolution

As an independent probe of galaxy properties at high redshift, we examine the specific star formation rate (sSFR). This quantity is less sensitive to absolute mass calibration than number counts, because systematic errors in stellar mass partially cancel in the SFR/M★ ratio.

**Table 2.** Median sSFR by redshift bin

| Redshift | N_galaxies | Median log(sSFR/Gyr⁻¹) | IQR |
|----------|------------|------------------------|-----|
| 5–6      | 6,829      | −8.13                  | 0.72|
| 6–7      | 6,652      | −8.02                  | 0.68|
| 7–8      | 6,559      | −7.91                  | 0.65|
| 8–10     | 3,928      | −7.85                  | 0.61|
| >10      | 2,320      | −7.82                  | 0.58|

**Notes:** IQR = interquartile range.

The sSFR shows a clear positive correlation with redshift:

- **Spearman ρ = 0.333** (p < 10⁻¹⁰)

Galaxies at higher redshift exhibit systematically elevated star formation activity relative to their stellar mass. The median log(sSFR) increases by 0.31 dex from z = 5–7 to z > 10, corresponding to approximately twice the star formation efficiency per unit stellar mass.

**Crucially, this trend is independent of the stellar mass function normalization** that underlies the number density comparison in Section 4.1. The sSFR result therefore provides corroborating evidence that high-redshift galaxies differ systematically from lower-redshift populations.

### 4.3 Summary of Empirical Results

Two independent analyses yield consistent conclusions:

1. Massive galaxies at z > 6 are **far more abundant** than standard ΛCDM references predict, with the discrepancy growing monotonically with redshift.

2. High-redshift galaxies are **more actively star-forming** (higher sSFR) than their lower-redshift counterparts.

3. Both trends point in the same direction: the early universe contains more massive, more active galaxies than expected.

These findings are **model-independent** in the sense that they emerge directly from the data without assuming any particular physical framework. We assess systematic uncertainties in Section 5 before discussing implications in Section 6.

---

## 5. Robustness Tests

### 5.1 Photometric Redshift Contamination

Photometric redshifts at z > 8 carry substantial uncertainty. Catastrophic outliers (lower-redshift galaxies scattered to high apparent redshift) could inflate the observed counts.

We assess this quantitatively:

**If 50% of z > 10 galaxies are interlopers:**
- True count: 248 → 124
- Reference expectation: 0.27 (0.5/deg² × 0.54 deg²)
- Residual ratio: **459×**

**If 80% are interlopers (extreme assumption):**
- True count: 248 → 50
- Residual ratio: **185×**

Even under extreme contamination assumptions, the order-of-magnitude excess persists. Photo-z errors cannot resolve the tension.

### 5.2 Stellar Mass Systematics

Stellar mass estimates depend on assumed IMF, star formation history, and dust model. Systematic shifts of 0.3–0.5 dex are plausible.

**If true masses are lower by 0.5 dex:**
- Effective threshold becomes log(M★) > 8.5
- More galaxies qualify → excess **increases**

**If true masses are higher by 0.5 dex:**
- Effective threshold becomes log(M★) > 9.5
- Fewer galaxies, but ΛCDM expectations also decrease at higher mass
- Net ratio remains **>100×** at z > 8

Mass systematics cannot eliminate the observed excess.

### 5.3 Cosmic Variance

The 0.54 deg² survey area corresponds to ~2 × 10⁶ comoving Mpc³ at z ~ 8. Cosmic variance at this scale is estimated at σ_cv ≈ 20–40% (Trenti & Stiavelli 2008).

A 3σ upward fluctuation corresponds to factor ~2 enhancement—negligible compared to the observed 100–1000× excess.

### 5.4 Combined Systematic Budget

**Table 3.** Systematic uncertainty summary

| Systematic | Maximum Impact | Direction |
|------------|----------------|-----------|
| Photo-z contamination (50%) | 2× reduction | ↓ |
| Photo-z contamination (80%) | 5× reduction | ↓ |
| Mass shift (+0.5 dex) | <2× reduction | ↓ |
| Mass shift (−0.5 dex) | Increases excess | ↑ |
| Cosmic variance (3σ) | 2× uncertainty | ↕ |
| ΛCDM baseline uncertainty | ~3× range | ↕ |

**Combined worst case** (simultaneously applying 50% contamination, +0.5 dex mass shift, and 3σ variance against upper-envelope ΛCDM):

- z = 10–12: 919× → ~75×
- z = 8–9: 259× → ~20×

**Even under maximally pessimistic assumptions applied simultaneously, the excess remains >20× at z > 8.**

---

## 6. Discussion

### 6.1 Tension with Standard Predictions

The results in Section 4 establish that ΛCDM forward predictions—even using conservative upper-envelope estimates—underpredict the abundance of massive galaxies at z > 6 by one to three orders of magnitude.

This tension has been noted by multiple independent studies using different JWST datasets:
- Labbé et al. (2023): massive galaxy candidates at z ~ 7–9
- Boylan-Kolchin (2023): theoretical limits from halo mass function
- Finkelstein et al. (2023, 2024): CEERS luminosity functions
- Castellano et al. (2024): GLASS spectroscopic confirmations

Our contribution is to quantify the tension systematically across redshift using the largest available high-z sample (COSMOS2025), and to demonstrate its robustness against known systematics.

### 6.2 Possible Resolutions

Several mechanisms have been proposed to reconcile observations with ΛCDM:

1. **Higher star formation efficiency**: If early galaxies convert baryons to stars more efficiently than assumed, more massive galaxies can form in available halos. However, Boylan-Kolchin (2023) shows this requires ε > 0.5, approaching the baryon fraction limit.

2. **Reduced feedback**: Weaker stellar/AGN feedback at early times could allow more rapid mass assembly. This requires substantial revision of sub-grid physics in simulations.

3. **Top-heavy IMF**: A more top-heavy initial mass function would increase luminosity per unit stellar mass, potentially reducing inferred masses. However, this also affects SFR estimates, and the sSFR trend (Section 4.2) suggests genuinely elevated activity.

4. **Modified cosmology**: Alternative dark matter models or early dark energy could enhance early structure formation. This represents a more fundamental departure from ΛCDM.

We do not adjudicate between these possibilities, but note that **all require significant revision** to standard assumptions.

### 6.3 Connection to Alternative Frameworks

The observed trends—monotonically increasing excess with redshift, elevated sSFR at early times—are qualitatively consistent with frameworks that predict **accelerated early structure formation**.

One such framework posits that entropy gradients in the early universe were steeper than in later epochs, driving more rapid energy flow and structure assembly (Magnusson 2024a, 2024b). Under this interpretation:

- The "impossible" early galaxies are a **natural consequence** of thermodynamic boundary conditions
- The monotonic z-dependence reflects the evolution of entropy gradient magnitude
- Elevated sSFR indicates enhanced energy throughput in the high-gradient regime

We emphasize that this interpretation is offered as one **consistent framework**, not as a unique explanation. The empirical results stand independently of any particular theoretical interpretation.

### 6.4 Relation to Galactic-Scale Results

Intriguingly, similar entropy-gradient-dependent structure has been identified at galactic scales. Analysis of the SPARC rotation curve database (Magnusson 2025) reveals that galaxy dynamics depend systematically on a parameter (L) that tracks deviation from thermodynamic equilibrium.

If both galactic and cosmological observations reflect the same underlying physics—entropy-driven structure formation—this would represent a **scale-invariant** principle operating from kpc to Gpc scales.

We note this connection without claiming it is established; verification requires independent analysis with different methodologies.

---

## 7. Conclusions

We have analyzed 26,288 high-redshift galaxies from the JWST COSMOS2025 catalog and find:

1. **Order-of-magnitude excess**: Massive galaxies (log M★ > 9) at z > 6 are 20–1000× more abundant than conservative ΛCDM predictions, with the discrepancy increasing monotonically with redshift.

2. **Elevated star formation**: The specific star formation rate correlates positively with redshift (ρ = 0.33), indicating systematically higher activity at earlier epochs.

3. **Robustness**: The excess persists (>20× at z > 8) even under pessimistic assumptions about photometric redshift contamination, stellar mass systematics, and cosmic variance.

These results establish a **robust empirical tension** with standard forward predictions for early galaxy formation. Resolution requires either substantial revision to galaxy formation physics within ΛCDM, or consideration of alternative frameworks that predict accelerated early structure formation.

---

## Appendix A: Galaxies at z > 12

For completeness, we report that 610 galaxies in our sample have photometric redshifts z_phot > 12. At this redshift:

- Observed density: 1,130 deg⁻²
- ΛCDM reference: ~0.05 deg⁻² (highly uncertain)
- Nominal ratio: ~22,000×

However, we exclude this bin from primary conclusions because:

1. Photometric redshift uncertainties increase substantially
2. Contamination from lower-z interlopers is poorly constrained
3. ΛCDM predictions at z > 12 are essentially uncalibrated

These galaxies are included in the publicly released analyzed catalog for interested researchers.

---

## Data Availability

The analyzed catalog (cosmos2025_efc_analyzed_v2.csv) and summary statistics (efc_jwst_report_v2.json) are available at [repository to be specified].

---

## References

Arnouts, S., et al. 1999, MNRAS, 310, 540  
Behroozi, P., et al. 2019, MNRAS, 488, 3143  
Boylan-Kolchin, M. 2023, Nature Astronomy, 7, 731  
Casey, C. M., et al. 2023, ApJ, 954, 31  
Castellano, M., et al. 2024, A&A, in press  
Finkelstein, S. L., et al. 2023, ApJL, 946, L13  
Finkelstein, S. L., et al. 2024, ApJL, 969, L2  
Harikane, Y., et al. 2023, ApJS, 265, 5  
Ilbert, O., et al. 2006, A&A, 457, 841  
Labbé, I., et al. 2023, Nature, 616, 266  
Magnusson, M. 2024a, Figshare, DOI: 10.6084/m9.figshare.31026151  
Magnusson, M. 2024b, Figshare, DOI: 10.6084/m9.figshare.31042678  
Magnusson, M. 2025, Figshare, DOI: 10.6084/m9.figshare.31047703  
Shuntov, M., et al. 2025, A&A, submitted (COSMOS2025)  
Trenti, M., & Stiavelli, M. 2008, ApJ, 676, 767  
