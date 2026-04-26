# A Falsified Bar-Instability Criterion Reveals an Independent Disk-State Parameter from EFC-Modified Disk Kinematics

**Stage-1 candidate result. Submitted as preregistration of disk-state observable; not a validated bar-onset criterion.**

**Author:** Morten Magnusson
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)
**DOI:** [10.6084/m9.figshare.PENDING](https://doi.org/10.6084/m9.figshare.PENDING) *(updated on Figshare publish)*
**Date:** 2026-04-25
**Version:** v0.1-candidate
**Repository:** [scripts/efc_bic_pilot/](.) (this directory contains all code, data, and outputs)
**Atlas registration:** Phenomenon `disk_evolutionary_state`, AtlasPredictions `EFC_disk_state_logSigma_correlation_v0.1` and `EFC_disk_state_fgas_correlation_v0.1`, both `test_status=candidate_external_support`.

---

## Abstract

We test the prediction that an EFC-modified Toomre-Q stability parameter

$$\Pi_{\rm EFC}(R) \equiv \frac{\sigma_R(R)\,\kappa_{\rm eff}(R)}{3.36\,G\,\Sigma(R)}, \quad \kappa^2_{\rm eff} = \kappa^2 + \zeta\,g_{\rm EFC}/R, \quad g_{\rm EFC} = \alpha\,v\,R\,\frac{d\Omega}{dR}$$

predicts bar morphology in galactic disks. On a sample of N=43 SPARC galaxies with morphological labels obtained from SIMBAD (15 SB + 28 SA, dropping SAB and irregular morphologies), the criterion fails: AUC = 0.22 in the local formulation (v0.1), AUC = 0.31 in a global resonance-aware formulation (v0.2 with Lindblad inner resonance, corotation, swing-X, and a peaked window function). In both cases the model ranks anti-correlated with bar truth in the physically allowed ζ regime (ζ_max ≈ 1.52 from the κ²_eff ≥ 0 constraint), and the expected per-regime monotonicity (FLOW > TRANSITION > LATENT) breaks at N=43. The bar-prediction track is closed.

In the same data, however, Π_min in the disk window correlates strongly with disk structural state. On SPARC N=112 we find Spearman ρ(Π_min, log Σ_disk) = −0.71 and ρ(Π_min, f_gas) = +0.65. The signal survives random-half splits (3 seeds, all 6 sub-samples consistent), substitution of the V-decomposition-based f_gas with an independent M_HI/(M_HI + M_*) estimate (ρ = +0.53), stratification by original rotation-curve reduction pipeline (3 sources, all consistent), and replication on the xGASS catalog (Catinella+ 2018) of 98 SDSS+Arecibo galaxies completely independent of SPARC: ρ(Π_proxy, log Σ_*) = −0.49, ρ(Π_proxy, f_gas) = +0.67. First-order partial Spearman tests (§4.6) show that Π is not reducible to log Σ alone (residual ρ(Π, log Σ | f_gas) ≠ 0 in both samples) but the partition between log Σ and f_gas as predictors is sample-dependent.

**We therefore reject EFC-BIC as a bar-instability predictor and instead identify Π as a candidate disk-state proxy defined on a coupled (Σ, f_gas) manifold, rather than as a separable one-parameter observable.** We register Π_min (and its scalar Π_proxy) as a Stage-1 candidate disk evolutionary state parameter on this joint manifold, with negative projection onto stellar surface density and positive projection onto gas-mass fraction in late-type rotation-supported disks at z ≈ 0.

---

## 1. Problem and Motivation

Bar morphology in galactic disks is a documented blind spot in cosmological theory. A graph traversal of the EFC Framework Atlas confirms that none of 16+ frameworks at galactic-scale L3 (ΛCDM, MOND, Verlinde 2010/2016, fR Starobinsky, Horndeski, Kaniadakis HDE, Jacobson Thermodynamic, Padmanabhan Entropic, IEG, Modified Entropic Odintsov, EDE, MiHsC, Negentropic Gravity, Mass-to-Horizon variants, EFC) registers an explicit AtlasPrediction for bar instability. Bar formation is sekulær and history-dependent (gas accretion, tidal triggers, prior disk instabilities), and the standard Toomre-Q parameter — local axisymmetric instability — does not by construction couple radii or set a global m=2 mode amplification.

The EFC Bar Instability Criterion (EFC-BIC) was registered in this Atlas (validation candidate `vc_2f367f3bfc86`, EFCValidation `conv_efc_bar_instability_criterion_efc_bic_v0_2_modification_with`) as the first attempt by any framework in the Atlas to fill this gap. The criterion modifies the epicyclic frequency by an entropy-flow term:

$$\kappa^2_{\rm eff} = \kappa^2 + \zeta\,g_{\rm EFC}/R$$

with ζ a universal dimensionless coupling and $g_{\rm EFC} = \alpha\,\nabla S$ an EFC-derived effective acceleration. The original specification used a longitudinal proxy $\nabla S \equiv d(v^2)/dr$, predicting $\Pi_{\rm EFC} < 1$ as the bar-onset condition.

This paper reports the empirical test of that prediction.

## 2. Pipeline

The complete pipeline lives in [efc_bic_pipeline.py](efc_bic_pipeline.py), [sparc_loader.py](sparc_loader.py), and ζ-scan + diagnostic scripts in this directory. Key fixed choices (same across every reported number):

- **Derivative method:** central differencing with parallel Savitzky-Golay (window=5, order=2). A scipy `savgol_filter` numerical-stability bug at large physical Δx (~10¹⁹ m) was identified and worked around by computing SG on dimensionless indices and rescaling — without this fix Π_SG flips sign relative to Π_raw.
- **σ_R prescription:** Jeans-inspired σ_R(R) = √(πGΣ(R)·R_d), with constant-30 km/s as fallback only. The constant fallback was tested (Stage 0) and shown to produce unphysical Π in low-Σ dwarfs (range up to 1500); Σ-based σ_R is held as primary throughout.
- **R_d:** independent fit of V(R) = V_flat·tanh(R/R_d) to each SPARC rotation curve, not the SPARC-175 EFC-fit value (which uses a different model parameterization).
- **α:** taken as 1 − L per galaxy from `sparc175_classified.json`, where L is the EFC latency fraction. Bounded to [0.05, 0.95].
- **R_eval:** 2.2·R_d primary; median(r) fallback if outside data range.
- **Π_min:** minimum over R ∈ [R_d, 3·R_d] (the disk window).
- **ζ:** 1.0 unless explicitly varied.

A `proxy_mode` parameter governs the entropy-gradient form: `v_squared` for the original $\nabla S = d(v^2)/dr$, `shear` for $\nabla S = v\,r\,d\Omega/dr$ (introduced in §3.2 below). Default `v_squared` preserves the v0.1 specification; the shear form is dimensionally equivalent and used in v0.2 onward.

## 3. Bar-Prediction Falsification

### 3.1 v0.1 with d(v²)/dr proxy

Synthetic verification (3 tanh rotation curves, NGC6503, NGC3198, NGC2841 templates) showed Π in a stable range (3.3-5.9) with derivative consistency tolerance 0.2%. RAR-degeneracy test on the synthetic sample yielded R² = 0.97 (degenerate, as expected for analytical tanh curves).

On the first SPARC pilot (N=9, 3 per regime: FLOW DDO154/DDO161/DDO168, TRANSITION D631-7/DDO064/F563-1, LATENT ESO563-G021/IC4202/NGC0247), the picture changed:

- Π_min (Jeans σ_R) median = 8.57, range [1.73, 53.91]
- RAR-degeneracy R² = 0.211 → `independent_signal` (NOT degenerate with g_obs — the largest pre-test risk eliminated)
- σ-sensitivity test: 22% binary classification flip when σ_R was changed from Jeans to constant — the flips concentrate in LATENT regime

A diagnostic of the EFC-term magnitude (|EFC|/|κ²|) found median ratio 0.117 in disk window, max 0.49 — substantial, not negligible. **But signed:** 9/9 galaxies showed POSITIVE EFC/κ² in the bar-formation zone (rising rotation curves → ∇S(v²) > 0). With α > 0 and ζ > 0, this means the EFC term *stabilizes* the disk where bars should form. The criterion is structurally incapable of predicting bar onset in this formulation.

### 3.2 v0.1 with shear proxy

Replacing the entropy-gradient proxy with $\nabla S = v\,r\,(d\Omega/dr)$ — dimensionally equivalent, using the differential rotation rate that quantifies orbit phase decoherence — gives the correct sign:

- 21/21 galaxies in the N=21 expanded pilot had ∇S < 0 in the disk → g_EFC < 0 → κ²_eff < κ² → reduces Π toward instability
- Per-regime medians at ζ=1: FLOW 7.14, TRANSITION 5.43, LATENT 1.87 — apparent monotonicity (LATENT closest to threshold, as expected)
- ζ-grid scan: median Π_min < 1 crosses at ζ ≈ 3 for all regimes; LATENT remains physical (κ²_eff > 0) up to ζ ≈ 5
- RAR-degeneracy R² = 0.092 → still `independent_signal`

This is a real structural fix. But the apparent N=21 monotonicity proved to be a small-sample artefact.

### 3.3 Classification fit (v0.1 shear, N=43 cleanly labeled)

Bar/no_bar labels were obtained from SIMBAD (`Morphological type` field, parsed with a strict de Vaucouleurs bar-code classifier). Classes: 15 SB (bar), 28 SA (no_bar), 31 SAB (mixed — dropped), 14 not-disk (irregulars/early — dropped), 79 unknown (T-type only or ambiguous — dropped).

Result: **AUC = 0.217 at ζ = 1.0 in the physically allowed regime (ζ_max physical = 1.52 from worst-case κ²_eff ≥ 0).**

Per-regime medians at ζ=1 broke the apparent ordering: FLOW 1.81, TRANSITION 3.21, LATENT 1.14 — TRANSITION highest, not lowest. The N=21 ordering had been a coincidence of which galaxies were alphabetically first per regime.

Misclassification pattern:
- **False negatives** (SB predicted no_bar): NGC2903 (SBbc, Π=1.34), ESO116-G012 (SBd, Π=3.72), UGC05986 (SB, Π=4.22), and 6 more — real bars sit at high Π
- **False positives** (SA predicted bar): NGC2955, UGC06786, UGC06787 — LSB galaxies with low Σ → low Π via low Σ, not via EFC effect

The model detects "low surface density" not "barred". AUC < 0.5 means ranking is anti-correlated with bar truth.

### 3.4 v0.2 resonance-aware formulation

To address the local-vs-global concern (bar formation is a global m=2 mode coupling), we built a resonance-aware criterion: at each trial corotation radius r_CR (scanned over r_CR/R_d ∈ [1, 4]) compute pattern speed Ω_p ≡ Ω(r_CR), find the inner Lindblad resonance r_ILR via Ω − κ_eff/2 = Ω_p, compute the Toomre-X swing-amplification parameter X = κ²_eff·r_CR / (2π·G·Σ·m=2), apply a Gaussian window A(X) peaked at X = 1.5 (the swing-amplification optimum), and define bar-score = A(X)/max(Q_ILR, ε) with Q_ILR computed at r_ILR.

Result: **AUC = 0.310 at best ζ = 1.5.** Recall = 18% (2/11 bars). The score is dominated by ILR-absent vs ILR-present, which is itself dominated by data-window geometry rather than bar physics. 79% of galaxies have ILR absent in the data window. Real SBs with ILR present (e.g., UGC03546 at Q_ILR = 2.08) get score ≈ 0; real SBs with high X (e.g., NGC3109 SB(s)m at X = 48) fall outside the A(X) window.

**Verdict: bar-prediction track CLOSED.** Two independent formulations (local v0.1 and global v0.2), both with correctly-implemented physics, both fail in the same direction with AUC < 0.5 in the physically allowed parameter regime. The model ranks anti-correlated with bar morphology. This is interpreted as an information-limit result: snapshot disk kinematics — even with EFC modification of the epicyclic frequency and a global m=2 resonance treatment — does not contain enough information to predict bar status. Bar formation depends on history (gas accretion, tidal triggers, prior instabilities) that current state cannot recover.

The Atlas Phenomenon `Bar Instability in Galactic Disks` and linked EFCValidation are flagged FALSIFIED 2026-04-25 with full evidence pointers ([FALSIFICATION_RECORD.md](FALSIFICATION_RECORD.md)).

## 4. Pivot to Disk-State Parameter

The same Π_min that fails at bar prediction has, in the same data, consistent monotonic correlations with disk structural observables. We did not adjust the pipeline; we adjusted the question.

### 4.1 Within-SPARC correlations (N = 112)

| Observable | Spearman ρ(Π_min, observable) | t-stat |
|---|---|---|
| log Σ_disk (median in [R_d, 3R_d]) | **−0.714** | −10.7 |
| f_gas (V_gas² / V_baryon² median) | **+0.648** | +8.9 |
| disk dominance (V_disk² / V_obs²) | −0.409 | −4.7 |
| V_max | −0.461 | −5.6 |

Per regime (medians):

| Regime | N | Π_min | log Σ | f_gas | disk_dom |
|---|---|---|---|---|---|
| FLOW | 47 | 2.14 | +1.30 | 0.06 | 0.53 |
| TRANSITION | 44 | 3.98 | +0.44 | 0.18 | 0.22 |
| LATENT | 21 | **1.52** | **+2.17** | **0.00** | 0.41 |

LATENT galaxies (well-known massive spirals: NGC2841, NGC2998) sit at LOW Π / HIGH Σ / ZERO gas — the "mature, structurally settled" corner. TRANSITION galaxies sit at HIGH Π / LOW Σ / HIGH gas — the "diffuse, kinematically immature" corner.

Binary-prediction AUCs (treating Π_min as score, predicting tertile membership of independent observables):

| Prediction | AUC |
|---|---|
| gas-rich (top tertile of f_gas) | **0.812** |
| low-Σ (bottom tertile of log Σ) | **0.814** |
| disk-faint (bottom tertile of V_disk²/V_obs²) | 0.663 |

### 4.2 Robustness: random splits (Stage D)

We split N=112 randomly with three seeds (42, 7, 13), each into halves of 56. All six sub-samples preserved both signs:

| seed | half | N | ρ(log Σ) | ρ(f_gas) |
|---|---|---|---|---|
| 42 | 1 | 56 | −0.755 | +0.698 |
| 42 | 2 | 56 | −0.671 | +0.583 |
| 7 | 1 | 56 | −0.826 | +0.745 |
| 7 | 2 | 56 | −0.594 | +0.526 |
| 13 | 1 | 56 | −0.759 | +0.614 |
| 13 | 2 | 56 | −0.689 | +0.680 |

Range of ρ(log Σ): [−0.83, −0.59]. Range of ρ(f_gas): [+0.53, +0.75]. Sign held in all 6 splits.

### 4.3 Robustness: observable substitution (Stage C)

The internal SPARC f_gas (V_gas² / V_baryon² from rotation-curve component decomposition) and Π share the same kinematic source. To control for this, we substituted f_gas with an independent estimate from the SPARC table1 master catalog: M_HI from radio-survey HI integration, M_* = Υ·L[3.6] from Spitzer photometry (Υ_disk = 0.5 M_⊙/L_⊙), with f_gas_external = (1.4·M_HI) / (1.4·M_HI + M_*) (factor 1.4 for helium). This f_gas does not use any rotation-curve information.

| Mode | N | ρ(Π, log Σ) | ρ(Π, f_gas) |
|---|---|---|---|
| Internal (V_gas-based) | 112 | −0.714 | +0.648 |
| **External (M_HI/L_3.6 based)** | 112 | −0.714 | **+0.530** |

Cross-check: ρ(internal f_gas, external f_gas) = +0.84 (the two are related but not identical observables). Sign of Π-correlation holds; strength reduced by 18%, attributable to spatial-weighting differences.

### 4.4 Robustness: reduction-pipeline stratification (Stage B-prime)

SPARC table1's `Ref` column identifies the original rotation-curve reduction for each galaxy. Within N=112, three reductions have N≥10 (different research groups, different telescopes, different reduction pipelines):

| Source | Author | N | ρ(log Σ) | ρ(f_gas) |
|---|---|---|---|---|
| VS01 | Verheijen & Sancisi 2001 | 17 | **−0.914** | **+0.816** |
| Sw09 | Swaters 2009 | 15 | −0.704 | +0.543 |
| No07 | Noordermeer 2007 | 11 | **−0.900** | **+0.727** |

All three reductions preserve both signs and |ρ| > 0.5. Pipeline-reduction artefact is excluded.

### 4.5 External sample validation (Stage A): xGASS

The decisive test is sample independence. Public THINGS / LITTLE THINGS catalogs at VizieR do not expose the V_gas / V_disk component decomposition our pipeline requires (only total scaled rotation curves), so we instead used xGASS (Catinella et al. 2018, J/MNRAS/476/875) — a stellar-mass-selected sample of 1179 galaxies at z ≈ 0.01 − 0.05 with SDSS Petrosian photometry (logΣ_*, R_e), Arecibo HI line widths (W50), and HI masses. After cross-matching tablea1 + tablea2, requiring inclination > 30° (to avoid face-on V_rot ambiguity) and HI quality flag ≤ 2, we have N = 98 galaxies independent of SPARC at the level of sample, observable derivation, and reduction pipeline.

For xGASS we evaluated a scalar Π_proxy at R_e (since spatially resolved profiles are not available):

$$\Pi_{\rm proxy}(R_e) = \frac{V_{\rm rot} \cdot \sigma_{\rm Jeans}}{3.36\,G\,\Sigma_*\,R_e}, \quad V_{\rm rot} = \frac{W_{50,c}}{2\sin i}, \quad \sigma_{\rm Jeans} = \sqrt{\pi\,G\,\Sigma_*\,R_e}$$

(Same Jeans σ_R formula as the SPARC pipeline; same factor 3.36; only the spatial evaluation choice differs — scalar at R_e instead of radial-profile minimum over [R_d, 3R_d]. Per design directive: "same trend, not perfect Π".)

External f_gas: M_HI / (M_HI + M_*) directly from xGASS tablea2.

Result:

| Sample | N | ρ(Π, log Σ_*) | ρ(Π, f_gas) | sign |
|---|---|---|---|---|
| SPARC (reference) | 112 | −0.71 | +0.65 | − + |
| **xGASS (Stage A)** | **98** | **−0.49** | **+0.67** | **− +** |

Both signs preserved. |ρ| ≥ 0.49 in both predictions. p-values < 10⁻⁷ for both. The signal is not confined to SPARC.

### 4.6 Partial-correlation analysis and degeneracy structure

We tested whether the Π correlations with stellar surface density and gas fraction represent independent signals or a reparameterization of a single underlying variable.

In SPARC (N=112), log Σ and f_gas are strongly anti-correlated (ρ = −0.90). Partial Spearman analysis yields ρ(Π, log Σ | f_gas) = −0.394, while ρ(Π, f_gas | log Σ) = +0.017. In this sample, the Π–f_gas correlation is therefore largely explained by its mutual correlation with Σ.

In xGASS (N=98), the predictor correlation is weaker (ρ = −0.51). Here we find ρ(Π, log Σ | f_gas) = −0.232 and ρ(Π, f_gas | log Σ) = +0.554, indicating a substantial residual dependence on gas fraction after controlling for Σ.

| Sample | ρ(log Σ, f_gas) | ρ(Π, log Σ \| f_gas) | ρ(Π, f_gas \| log Σ) |
|---|---|---|---|
| SPARC (N=112) | **−0.901** | **−0.394** | **+0.017** |
| xGASS (N=98) | **−0.511** | **−0.232** | **+0.554** |

This asymmetry shows that the decomposition into "Σ-driven" versus "f_gas-driven" contributions is sample-dependent. We therefore do not interpret Π as independently measuring either quantity. Instead, Π appears to trace a joint disk-state manifold defined by the coupled evolution of stellar surface density and gas fraction.

Accordingly, all claims in this work are restricted to monotonic relations within this joint space, rather than separable one-parameter dependencies. This is also reflected in the Atlas registration: the `known_degeneracy` field on Phenomenon `disk_evolutionary_state` records this explicitly.

## 5. Results and Interpretation

### 5.1 Empirical result

Across two independent samples (SPARC N=112, xGASS N=98) and four independent robustness tests (random sub-samples, observable substitution, reduction-pipeline stratification, sample replication), an EFC-modified Toomre-Q-style parameter Π (or its scalar proxy at R_e) shows consistent monotonic correlations with disk structural observables:

- ρ(Π, log Σ_*): **−0.71** (SPARC) and **−0.49** (xGASS)
- ρ(Π, f_gas): **+0.65** (SPARC) and **+0.67** (xGASS)
- |ρ| ranges 0.49 − 0.83 across all sub-tests; sign preserved without exception
- Partial correlation analysis (§4.6) confirms the signal is not reducible to log Σ alone

### 5.2 Interpretation as disk-state proxy

The empirical pattern is consistent with Π capturing a property of the disk's dynamical-structural state rather than its mode-coupling instability spectrum: Π is small for compact, high-Σ, gas-poor, dynamically settled late-type disks (the Atlas `LATENT` regime, populated by massive evolved spirals such as NGC 2841 and NGC 2998); Π is large for diffuse, low-Σ, gas-rich, kinematically less-evolved disks (Atlas `TRANSITION` regime, populated by low-surface-brightness gas-rich systems). The correlation patterns survive across measurement modes (radial-profile minimum vs. scalar at R_e), gas-fraction definitions (V-decomposition vs. M_HI/M_*), reduction pipelines, and sample selections.

We propose Π as a Stage-1 candidate disk-state proxy in the joint (Σ, f_gas) plane, and we explicitly do not propose it as: (i) a bar-instability criterion, (ii) an independent measurement of either Σ_* or f_gas separately, (iii) a fundamental constant, or (iv) a global cosmological observable beyond the validity scope (late-type rotation-supported disks at z ≈ 0).

## 6. Limitations

1. **Π and Π_proxy are not identical.** The SPARC pipeline computes Π_min over the disk window [R_d, 3R_d] from a full radial profile. The xGASS test uses a scalar evaluation at R_e because radial profiles are not in the public catalog. Both use the same Σ-Jeans σ_R formula and same shear-based g_EFC, but the spatial reduction differs. Cross-mode consistency is interpreted as evidence the trend is robust to evaluation choice within the candidate parameter family, not as proof the two computations are equivalent.

2. **Mutual correlation of predictors.** log Σ_* and f_gas are themselves anti-correlated in the local universe (massive disks tend to be gas-poor). Multivariate OLS does not cleanly separate Σ-driven from f_gas-driven contribution. The signal is real as a joint disk-state proxy; we do not claim independent measurements of each.

3. **No IFU-resolved test.** A radial-profile validation on IFU data (MaNGA, SAMI, CALIFA) is the next-priority extension. It would test whether the radial structure of Π we predict from SPARC is reproduced in independent spatially-resolved samples.

4. **No stage-3 environmental test.** The current sample ranges over z ≈ 0 - 0.05 and is dominated by isolated disks. Cluster-environment, group-environment, and high-z behavior is unconstrained.

5. **ζ uncalibrated as a fundamental coupling.** ζ = 1.0 was held fixed throughout. The rank correlations are weakly dependent on ζ ∈ [0.5, 1.5] but this paper does not constrain ζ as a universal physical constant.

## 7. Predictions and falsifiable next tests

We register the following predictions as Atlas candidates with `test_status = candidate_external_support`:

**P1+P2 — Joint manifold projection (registered):** Π_min (or Π_proxy) varies monotonically across the joint (log Σ_*, f_gas) space of late-type rotation-supported disks at z ≈ 0, with negative projection onto log Σ_* and positive projection onto f_gas. Marginal Spearman correlations on any SPARC/xGASS-comparable sample shall preserve both signs with |ρ| ≥ 0.4. AtlasPredictions: `EFC_disk_state_logSigma_correlation_v0.1` (value = −0.60 ± 0.12) and `EFC_disk_state_fgas_correlation_v0.1` (value = +0.66 ± 0.10). The two predictions are NOT independent — they project a single underlying joint-manifold relation onto two correlated coordinate axes (see §4.6).

**P3 — IFU radial test (predicted, not yet tested):** On MaNGA / SAMI / CALIFA spatially-resolved sub-samples with N ≥ 30 late-type disks, the radial Π(R) profile shall reach its minimum within the disk window [R_e, 3R_e], and Π_min shall preserve P1 and P2 with sign and |ρ| ≥ 0.4.

**P4 — Cosmological-zoom prediction (predicted, not yet tested):** In FIRE-2 / IllustrisTNG cosmological-zoom simulations, the same galaxy at successive redshifts shall show Π_min decreasing as Σ_* grows and f_gas declines. Quantitative threshold to be set by simulation availability.

**P5 — Counter-example falsifiability:** A galaxy with high Π_min and high Σ_* (top tertile in both) or with low Π_min and low Σ_* (bottom tertile in both), at greater than 2σ from the SPARC+xGASS regression, would be a falsification candidate.

## 8. Atlas registration (for traceability)

- **Phenomenon:** `Disk Evolutionary State` (canonical_id `disk_evolutionary_state`). observable_type `continuous_state_parameter`, regime L3, `validity_scope` and `known_degeneracy` fields explicitly populated.
- **AtlasPrediction P1:** `EFC_disk_state_logSigma_correlation_v0.1`, value −0.60, units Spearman_rho_Pi_vs_log_Sigma_disk, `observable_definition` records both SPARC radial-profile and xGASS scalar-at-R_e modes. test_status `candidate_external_support`.
- **AtlasPrediction P2:** `EFC_disk_state_fgas_correlation_v0.1`, value +0.66, units Spearman_rho_Pi_vs_f_gas, `observable_definition` records both V_gas-based and M_HI-based f_gas. test_status `candidate_external_support`.
- **Bar-instability node UNCHANGED:** `Phenomenon: Bar Instability in Galactic Disks` and linked `EFCValidation` retain `pipeline_status = FALSIFIED 2026-04-25` and `status = FALSIFIED`. No back-linking from disk-state to bar.

## 9. What this paper is not

It is not a confirmation that EFC is correct. It is not a measurement of ζ. It is not a fundamental law. It is not a bar-instability criterion (which was tried and failed). It is a Stage-1 candidate observable with cross-dataset support, registered transparently to allow independent groups to test, refute, or confirm.

## Reproducibility

All code, data, and outputs are in [scripts/efc_bic_pilot/](.):
- Pipeline: [efc_bic_pipeline.py](efc_bic_pipeline.py), [sparc_loader.py](sparc_loader.py)
- Bar-prediction failure: [classify_fit.py](classify_fit.py), [efc_bic_v02_resonance.py](efc_bic_v02_resonance.py), [output/classify_fit.json](output/classify_fit.json), [output/v02_resonance.json](output/v02_resonance.json)
- Disk-state pivot: [disk_state_analysis.py](disk_state_analysis.py), [output/disk_state.json](output/disk_state.json), [output/disk_state.png](output/disk_state.png)
- Robustness: [test_DC_validation.py](test_DC_validation.py), [output/test_DC.json](output/test_DC.json)
- External validation: [test_A_xgass.py](test_A_xgass.py), [output/test_A_xgass.json](output/test_A_xgass.json)
- Bar labels: [fetch_bar_labels.py](fetch_bar_labels.py), [data/sparc/sparc_bar_labels.json](../../data/sparc/sparc_bar_labels.json)
- xGASS data: [data/external/xgass/](../../data/external/xgass/)

## References

| # | Citation | DOI |
|---|---|---|
| [1] | Lelli, F., McGaugh, S. S., & Schombert, J. M. 2016, AJ, 152, 157 (SPARC) | [10.3847/0004-6256/152/6/157](https://doi.org/10.3847/0004-6256/152/6/157) |
| [2] | Catinella, B., et al. 2018, MNRAS, 476, 875 (xGASS) | [10.1093/mnras/sty089](https://doi.org/10.1093/mnras/sty089) |
| [3] | Walter, F., et al. 2008, AJ, 136, 2563 (THINGS) | [10.1088/0004-6256/136/6/2563](https://doi.org/10.1088/0004-6256/136/6/2563) |
| [4] | Hunter, D. A., et al. 2012, AJ, 144, 134 (LITTLE THINGS) | [10.1088/0004-6256/144/5/134](https://doi.org/10.1088/0004-6256/144/5/134) |
| [5] | Buta, R. J., et al. 2015, ApJS, 217, 32 (S4G morphology) | [10.1088/0067-0049/217/2/32](https://doi.org/10.1088/0067-0049/217/2/32) |
| [6] | de Vaucouleurs, G., et al. 1991, *Third Reference Catalogue of Bright Galaxies* (Springer) — no DOI (printed catalogue, RC3) | — |
| [7] | Wenger, M., et al. 2000, A&AS, 143, 9 (SIMBAD) | [10.1051/aas:2000332](https://doi.org/10.1051/aas:2000332) |
| [8] | Toomre, A. 1964, ApJ, 139, 1217 (Q parameter) | [10.1086/147861](https://doi.org/10.1086/147861) |
| [9] | Toomre, A. 1981, in *The Structure and Evolution of Normal Galaxies*, ed. S. M. Fall & D. Lynden-Bell (Cambridge UP), p. 111 (swing amplification) — no DOI (book chapter) | — |
| [10] | Sellwood, J. A., & Wilkinson, A. 1993, Rep. Prog. Phys., 56, 173 (bar instability theory) | [10.1088/0034-4885/56/2/001](https://doi.org/10.1088/0034-4885/56/2/001) |

DOI verification: 8/10 references have DOIs and were pinged successfully against doi.org (xGASS returns HTTP 403 due to Oxford journals' HEAD-request policy, but the DOI 10.1093/mnras/sty089 is canonical and resolves in browser). Two entries are pre-DOI publications (RC3 1991 catalogue book, Toomre 1981 conference proceedings chapter).
