# EFC-C v2.1: Degree-Heterogeneity Entropy-Gradient Predictions for Cognitive States

## A Bridge-Anchored, Layer-Separated, Validity-Bounded Framework

**Morten Magnusson**
Symbiose Research, Sandnes, Norway
ORCID: 0009-0002-4860-5095

Research Note v2.1 — April 2026
DOI: [10.6084/m9.figshare.32091700](https://doi.org/10.6084/m9.figshare.32091700) (versioned update to v2.0)

---

## Abstract

This revision of EFC-C replaces the Fiedler-eigenvalue formulation (Bridge B1*) used in v2.0 with the empirically-supported degree-heterogeneity formulation (Bridge B1**) from the Cross-Domain Bridge Equations paper (Magnusson 2026a, DOI 31940547 v0.2, Section 3.4). The centrifugal entropy score κ = ⟨S_hub⟩/⟨S_periph⟩ is predicted from the structural hub-to-periphery degree ratio D_ratio = ⟨k_hub⟩/⟨k_periph⟩ via the power-law relation κ = C_eff · D_ratio^γ, where C_eff is fixed prior to neural data analysis via regime transformation of the cosmological constant C = k/a_G, and γ ≈ 0.55 is the one empirical fit parameter (constrained to 0.5 ≤ γ ≤ 0.6 across HCP datasets). Degree heterogeneity accounts for 94% of the cross-subject variance in κ (Magnusson 2026b, DOI 31940370); λ2 does not (r ≈ 0.16, p = 0.70). Predictions are separated into Layer A (topological: invariant under cross-domain anchor C_eff) and Layer B (absolute scale: conditional on C_eff). If Bridge validity criteria are not satisfied in the cognitive regime, C_eff reverts to an empirical fit parameter and Layer B degrades gracefully; Layer A is unaffected. We specify exact datasets, an autocorrelation-based empirical protocol for the secondary τ_c correction, and propagated-uncertainty falsification thresholds per layer.

**Keywords:** neural entropy, connectome degree heterogeneity, hub topology, Bridge equations, dissipative gradient-flow, psychiatric biomarkers, resting-state fMRI, cross-domain parameter transfer.

**Epistemic status:** Revision (v2.1) of v2.0 structural formulation. No original empirical analysis. Predictions are prospective, falsifiable, and conditional on stated regime validity.

**Key change from v2.0:** The Q1 prediction is no longer κ = C/(1 + λ2τ_c). It is now driven by degree heterogeneity H (see Section 2). Readers familiar with v2.0 should read Sections 2 and 3 before consulting the prediction tables.

---

## 1 Introduction and Rationale for v2.1

### 1.1 What changed since v2.0

Version 2.0 of this note (published as DOI 32091700, April 2026) grounded the centrifugal entropy score prediction on Bridge B1*, which used the Fiedler eigenvalue λ2 of the normalized structural Laplacian as the driver of the entropy gradient. Subsequent empirical work (Magnusson 2026b, DOI 31940370: Local Degree Heterogeneity Predicts Functional Variability Gradients) demonstrated that the hub-to-periphery degree ratio, not the algebraic connectivity, is the primary structural driver of neural entropy gradients. The Bridge Equations paper (Magnusson 2026a, DOI 31940547 v0.2) accordingly revised B1* to B1** (degree-heterogeneity formulation).

This revision (v2.1) brings EFC-C into alignment with the current Bridge formulation and, as a side effect, removes a significant source of parametric degeneracy.

### 1.2 Two structural changes with three consequences

Two changes drive this revision:

1. The Q1 prediction is re-anchored on H rather than λ2.
2. Predictions are separated into two layers based on whether they depend on the cross-domain invariant C (Layer B) or only on structural deltas within the cognitive regime (Layer A).

The three consequences are: (i) the τ_c degeneracy that dominated v2.0's Q1 prediction is reduced to a secondary correction; (ii) Layer A predictions survive independently of the cross-domain anchor hypothesis; (iii) the paper no longer over-claims "parameter-free" inference.

### 1.3 What this revision does and does not claim

**Core claim:** The central claim of EFC-C v2.1 is independent of cross-domain transfer: it is the existence of a one-parameter power-law coupling between hub-to-periphery degree heterogeneity and entropy gradients in brain networks (κ = C_eff · D_ratio^γ). All Layer A predictions stand or fall with this network-level scaling law alone. The cross-domain interpretation of C_eff via Bridge B1** is an additional, separable hypothesis that is tested independently via Layer B.

**Claims:**
- κ and D_ratio are both hub-to-periphery ratios and should scale together as a power law with exponent γ ∈ [0.5, 0.6].
- Layer A (topological) predictions are testable without committing to cross-domain C_eff.
- Layer B (absolute-scale) predictions are testable conditional on Bridge validity in the target regime.

**Does not claim:**
- Universal applicability of a galactic constant to neural tissue.
- That inference is "parameter-free" — there is one empirical fit parameter (γ); C_eff is fixed but transferred from a different regime.
- Any mechanistic causal link between cosmology and cognition.

---

## 2 Bridge B1**: The Degree-Heterogeneity Formulation

### 2.1 Structural observables

For a brain parcellated into N regions {R_i} with weighted structural adjacency W:

- **Hub set (R_hub):** top 10% of nodes by weighted degree k_i = Σ_j W_ij.
- **Periphery set (R_periph):** bottom 30% of nodes by weighted degree.
- **Hub-to-periphery degree ratio:**

D_ratio = ⟨k_hub⟩ / ⟨k_periph⟩

The entropy observable κ is unchanged from v2.0:

κ = ⟨S_hub⟩ / ⟨S_periph⟩

where S_i is the local multiscale sample entropy of the BOLD signal at parcel i (see Section 4). Both κ and D_ratio share the same hub/periphery partition: this topological alignment is what B1* lacked, since λ2 is a whole-graph scalar with no partition structure.

### 2.2 Bridge B1**: the power-law prediction

From the Bridge paper (Magnusson 2026a, Sec 3.4.2, Eqs. 7–9), Bridge B1** gives:

κ = C_eff · D_ratio^γ

where:
- γ ≈ 0.55 (empirical, constrained to 0.50 ≤ γ ≤ 0.60 across HCP subjects; this is the one fit parameter of the model),
- C_eff is the regime-transformed cross-domain constant:

C_eff = κ_reg · C = κ_reg · (k / a_G)

with C = k/a_G the cosmological constant from Spor 1 (SPARC fit) and κ_reg the RCMP regime-transformation factor from cosmological L3 to cognitive L1.

Empirically, C_eff ≈ 1.9–2.2 across HCP datasets (group-level: ∼ 1.93; individual-level: ∼ 2.23; within 1σ).

### 2.3 Methodological lock on C_eff

C_eff is fixed prior to any neural dataset analysis via Eq. 4 using cosmological C from the pre-registered SPARC fit (Magnusson 2026f, DOI 31301953) and the RCMP regime-transformation factor κ_reg from the L3→L1 cortex-regime mapping (Bridge paper Sec 2.3). C_eff is not re-estimated, tuned, or fit to any neural dataset at any stage of analysis. The one remaining free parameter is γ, which is estimated once from a single HCP reference sample and held fixed across all downstream tests.

### 2.4 Why this helps: three technical benefits over B1*

1. **Topological alignment:** predictor (D_ratio) and observable (κ) share the hub/periphery partition; prediction errors cannot be absorbed by partition choice.

2. **τ_c demoted to secondary correction:** the power-law in Eq. 3 contains no explicit τ_c; any residual timescale effect enters only as a correction O(τ_c/τ_H), measured per subject (Section 4).

3. **Empirical grounding:** in the original κ paper (Magnusson 2026b, Table 6 and Sec 3.4), D_ratio explains 94% of inter-subject variance in κ at the individual-subject level using the FC-CV proxy (r² = 0.94, p < 0.001). λ2 does not (r = 0.16, p = 0.70). Extension of this association to the MSE proxy used here is a primary validation target of v2.1; the sign and approximate magnitude are expected but not assumed.

### 2.5 Regime-consistency (RCMP) grounding

Bridge B1** uses a driver-proximal observable within the neural regime: D_ratio is an L1-level (directly observable) structural feature of the cortex regime, not an L3-level (theoretical-construct) spectral quantity. The failure of B1* under RCMP analysis (Bridge paper Sec 3.4.1) is attributed precisely to the use of λ2, which lives at the wrong epistemic layer for the cortex regime (High-S, R2). B1** corrects this. RCMP (Magnusson 2026g, DOI 31222900) is therefore integrated as the regime-layer foundation of B1**, not invoked as a separate methodological shield.

---

## 3 Layer-Separated Predictions

### 3.1 Motivation

The cross-domain invariant C_eff is transferred from galactic dynamics (SPARC fit; Spor 1). Whether this transfer is valid in the cognitive regime is an open question addressed by Bridge validity criteria (Section 5). To isolate predictions that survive if the transfer fails, we separate into:

- **Layer A (topological):** depends only on differences in structural observables within the cognitive regime. Invariant under choice of C_eff.
- **Layer B (absolute-scale):** depends on C_eff and therefore on Bridge validity.

### 3.2 Layer A: Topological predictions

These survive even if cross-domain C_eff-transfer is invalid. Layer A can be tested using only community-standard tools (degree ratio, sample entropy) and published datasets: it does not require any Magnusson publication as prerequisite.

**Prediction A1 (structural-entropic coupling):**

Δ log κ = γ · Δ log D_ratio + ε

In log-space, differences in κ scale linearly with differences in D_ratio with slope γ ∈ [0.5, 0.6]. Across subjects or between diagnostic groups, the slope is predicted; the intercept (log C_eff) is absorbed.

**Falsification A1:** If fitted slope γ̂ lies outside [0.3, 0.8] (generous ±2σ EBE-bounded interval) for n ≥ 30 pooled subjects, or if Pearson r(log κ, log D_ratio) < 0.50, the structural-entropic coupling is falsified.

**Prediction A2 (anterior-posterior asymmetry in schizophrenia):**

α_AP^scz > α_AP^healthy

where α_AP = ⟨S_anterior_hub⟩/⟨S_posterior_hub⟩. Driven by preferential frontotemporal degree reduction.

**Prediction A3 (posterior asymmetry in MDD):**

α_AP^mdd < α_AP^healthy

Driven by diffuse global efficiency reduction with posterior emphasis.

**Falsification A2–A3:** If α_AP does not discriminate schizophrenia from MDD with AUC ≥ 0.60 on n ≥ 15/group, the topological prediction is falsified.

### 3.3 Layer B: Absolute-scale predictions

These hold conditional on Bridge validity in the cognitive regime.

**Prediction B1 (healthy baseline κ):** With C_eff = 2.0 ± 0.15 (regime-transformed cosmological; Bridge Eq. 9), γ = 0.55±0.05 (empirical fit), and typical HCP D_ratio = 1.2±0.15 (top 10% / bottom 30% partition with log-degree proxy):

κ_healthy = C_eff · D_ratio^γ ≈ 2.0 · 1.2^0.55 ≈ 2.2

Propagated uncertainty (first-order Gaussian error propagation over C_eff, γ, D_ratio):

κ_healthy ∈ [1.7, 2.6] (95% EBE-bounded interval)

**Falsification B1:** If group-mean κ_obs on n ≥ 20 HCP subjects lies outside [1.7, 2.6], the absolute-scale prediction is falsified. This interval reflects EBE-bounded uncertainty under entropy-constrained inference, not aggressive ±3σ confidence as in v2.0. Derivation of interval: see Appendix A of Bridge paper (DOI 31940547 v0.2) for full error-propagation table; summary here uses linearized propagation.

**Prediction B2 (critical threshold for conscious state):** At severely disrupted D_ratio ≲ 0.9 (degree hierarchy collapse), the model predicts κ_crit ≲ 1.9 and convergence toward κ → 1 in the fully-disrupted limit.

**Falsification B2:** If patients with confirmed disorders of consciousness (UWS/VS) show κ_obs > 2.0 with maintained degree heterogeneity (D_ratio > 1.15), the threshold prediction is falsified.

---

## 4 Methods

### 4.1 Datasets

| Dataset | Population | n target | Modalities | Access |
|---------|-----------|----------|------------|--------|
| HCP 1200 | Healthy adults | 50 | Structural (DTI) + rs-fMRI | ConnectomeDB |
| OpenNeuro ds000030 | Schizophrenia + healthy | 50+50 | Structural + rs-fMRI | OpenNeuro |
| OpenNeuro ds000171 | MDD + healthy | 20+20 | rs-fMRI | OpenNeuro |

### 4.2 Computing D_ratio from structural connectomes

1. Construct W from probabilistic tractography (HCP MMP1.0, 360 parcels).
2. Compute weighted degree k_i = Σ_j W_ij per parcel.
3. Define hub set (top 10% k_i) and periphery set (bottom 30% k_i).
4. Compute D_ratio = ⟨k_hub⟩/⟨k_periph⟩.

**Threshold robustness:** The observable κ is stable under variation of the hub (5%–20%) and periphery (20%–40%) percentile thresholds: κ > 1 for all 30 tested combinations, with CV = 1.7% (structural proxy) and 3.2% (FC-based proxy) in the reference dataset (Magnusson 2026b, Table 6). Invariance of the fitted exponent γ under the same threshold grid is a secondary falsification target of v2.1 and is included in the pre-registered pipeline.

### 4.3 Entropy proxy

Unchanged from v2.0: multiscale sample entropy at scales 4–6 on ICA-FIX-denoised BOLD, averaged to give S_i per parcel.

### 4.4 Empirical τ_c protocol (new in v2.1)

Where τ_c-corrections are relevant (Layer B only, second-order), we estimate τ_c per subject from the BOLD time series rather than import it from literature. Protocol:

1. For each parcel i, compute the integrated autocorrelation time τ_ac,i of the BOLD signal via the Sokal-window estimator.
2. Take τ_c^subj = median_i(τ_ac,i) across parcels as the subject-specific redistribution timescale.
3. Report inter-subject variance in τ_c^subj as a covariate in Layer B analyses.

This converts τ_c from a "free knob" into a measured covariate. Residual τ_c variance enters Layer B falsification bounds but cannot be used post-hoc to rescue failed predictions.

### 4.5 Statistical analysis

**Layer A tests (primary):**
- Log-log regression: log κ = log C_eff + γ · log D_ratio; report γ̂ with 95% bootstrap CI.
- Correlation: Pearson r(log κ, log D_ratio) across pooled groups.
- ROC: α_AP as classifier, schizophrenia vs. MDD.

**Layer B tests (conditional):**
- Group-mean κ_obs vs. predicted interval [1.7, 2.6].
- Threshold test: κ_obs vs. 1.9 in DoC patients at collapsed D_ratio.

**Pre-registration:** Analysis code deposited at github.com/symbiose-research/efc-c-validation prior to data access. Pipeline modules: connectome_dratio.py, entropy_mse.py, tau_c_acf.py, layer_analysis.py.

---

## 5 Validity Criteria for Cross-Domain Transfer

### 5.1 The fallback clause

If Bridge validity criteria (Magnusson 2026a, DOI 31940547 v0.2, Section 4) are not satisfied in the cognitive regime, the cross-domain invariant C_eff reverts to an empirical fit parameter. In that case:

- Layer A predictions remain as stated.
- Layer B predictions degrade to empirical calibrations, not parameter-free transfers.
- The paper's contribution reduces from "cross-domain consistency test" to "network-constrained entropy-gradient model", which is itself a legitimate contribution.

This fallback clause is the central design commitment of v2.1: the paper does not stand or fall with the cross-domain hypothesis. It is robust at Layer A and conditional at Layer B.

### 5.2 Relation to Entropy-Bounded Empiricism (EBE)

The framework is consistent with Entropy-Bounded Empiricism (Magnusson 2026c, DOI 31222903), which establishes that inference in entropy-constrained systems must carry explicit validity bounds. The Layer A/B separation is the EBE-compliant presentation of EFC-C's prediction structure.

---

## 6 Relation to Existing Frameworks

### 6.1 Bridge B2 and RLHF (Spor 3)

Bridge B2 (Magnusson 2026a) maps the neural entropy structure onto reinforcement-learning-from-human-feedback reward-landscape curvature ∇²R. A formal isomorphism between RLHF and thermodynamic entropy minimisation has been presented (Magnusson 2026d, DOI 31940535). Empirical validation of Bridge B2 in RLHF systems would provide independent support for the unified dissipative gradient-flow dynamics underlying the EFC-C predictions here, without requiring additional neural data. The two tracks function as independent empirical anchors for the same law.

### 6.2 Civilization-scale application: Homo Fluxus

At the civilization level, the same unified dynamics are applied in the Homo Fluxus framework (Magnusson 2026e, DOI 31940604), which includes a DSM-reframing module for psychiatric categories via entropy-gradient dynamics. EFC-C's Layer A predictions (A2, A3) are consistent with the civilization-scale DSM-reframe but do not depend on it. Homo Fluxus is cited here as a parallel, broader-scale instantiation of the Bridge framework, not as a premise.

### 6.3 Prior cognitive frameworks

The Entropic Brain Hypothesis (Carhart-Harris et al. 2014) established entropy magnitude as an index of conscious state. The Free Energy Principle (Friston 2010) casts cognition as variational free-energy minimisation. EFC-C is consistent with both: it captures the topology of the entropy field (where EBH captures magnitude) and instantiates Helmholtz gradient-flow (where FEP instantiates variational inference).

---

## 7 Limitations

1. **Cross-domain C is not validated in the cognitive regime.** Layer B predictions are conditional on Bridge validity; the fallback clause in Section 5 is the explicit commitment that this is not a free pass.

2. **γ is an empirical fit parameter and its cross-cohort stability is not yet established.** Although C_eff is fixed prior to neural analysis, the exponent γ in Eq. 3 is estimated from an HCP reference sample. The model is not parameter-free; it has one free parameter per cross-domain invariant. Stability of γ across independent cohorts (OpenNeuro ds000030, ds000171, HCP-Aging) is a primary falsification target of v2.1: if γ̂ varies by more than ±0.15 across cohorts fitted independently, the model loses universality and the cross-domain interpretation of C_eff is not supported. Invariance of γ under hub/periphery threshold variation (within the 30-combination grid of §4) is a parallel secondary test.

3. **MSE is a statistical, not thermodynamic, entropy proxy.** Sample entropy indexes signal complexity, not thermodynamic entropy production. Robustness checks with LZC and permutation entropy are included in the pre-registered pipeline.

4. **Hub/periphery thresholds (10%/30%) are conventional.** Sensitivity analyses at 5–15% / 20–40% are included.

5. **Cross-sectional design.** Longitudinal predictions deferred to v3.0.

6. **The Bridge paper itself is recent and its cross-domain scope is not yet externally validated.** EFC-C v2.1 constitutes, in part, a test of Bridge B1**'s scope. This circular-programme risk is acknowledged and the Layer A/B separation is designed to contain it.

---

## 8 Summary of Predictions and Falsification

| Layer | Code | Prediction | Observable | Falsification |
|-------|------|-----------|-----------|---------------|
| A | A1 | Δ log κ = γ · Δ log D_ratio, γ ∈ [0.5,0.6] | Slope fit, log-log | γ̂ ∉ [0.3,0.8] or r < 0.50 (n ≥ 30) |
| A | A2 | α_AP^scz > α_AP^healthy | Anterior/posterior hub entropy | AUC < 0.60 (n ≥ 15/group) |
| A | A3 | α_AP^mdd < α_AP^healthy | Anterior/posterior hub entropy | AUC < 0.60 (n ≥ 15/group) |
| B | B1 | κ_healthy ∈ [1.7, 2.6] | κ from HCP | Group mean outside interval (n ≥ 20) |
| B | B2 | κ_DoC ≲ 1.9 at D_ratio ≲ 0.9 | κ in UWS/VS | κ > 2.0 with D_ratio > 1.15 |

**Layer interpretation:** If all Layer A predictions survive but Layer B fails, the paper demonstrates a network-constrained entropy-gradient law independent of cross-domain C. If Layer B also survives, the paper additionally supports Bridge validity in the cognitive regime. If Layer A fails, the core model is wrong regardless of cross-domain considerations.

---

## 9 Reproducibility

All parameter values and their sources:

- **C_eff = 2.0 ± 0.15:** regime-transformed from cosmological C = k/a_G (Magnusson 2026f, DOI 31301953) via RCMP L3→L1 factor (Bridge paper Sec 2.3). Fixed prior to neural analysis.
- **γ = 0.55 ± 0.05:** empirical fit parameter, estimated once from HCP reference sample (Magnusson 2026b, DOI 31940370) and held fixed.
- **D_ratio baseline:** ∼ 1.2 (typical HCP value, top 10% / bottom 30% partition, log-degree proxy; subject-specific variance reported).
- **τ_c:** measured per subject (Section 4), not imported.

**Total free parameters fit to neural data:** one (γ).

---

## References

[1] Magnusson, M. (2026a). Cross-Domain Bridge Equations for the EFC Framework. Research Note v0.2. DOI: 10.6084/m9.figshare.31940547

[2] Magnusson, M. (2026b). Local Degree Heterogeneity Predicts Functional Variability Gradients in the Human Connectome. DOI: 10.6084/m9.figshare.31940370

[3] Magnusson, M. (2026c). Entropy-Bounded Empiricism: Core Principles. DOI: 10.6084/m9.figshare.31222903

[4] Magnusson, M. (2026d). Reinforcement Learning from Human Feedback as Thermodynamic Entropy Minimisation: A Formal Isomorphism. DOI: 10.6084/m9.figshare.31940535

[5] Magnusson, M. (2026e). Homo Fluxus: A Civilization Map Through Energy-Flow Cosmology. DOI: 10.6084/m9.figshare.31940604

[6] Magnusson, M. (2026f). Energy-Flow Cosmology: Empirical Validation of the EFC Screening Model Against the Radial Acceleration Relation. DOI: 10.6084/m9.figshare.31301953

[7] Magnusson, M. (2026g). The Regime-Consistent Measurement Principle (RCMP): A Methodological Framework for Multi-Scale Physics. DOI: 10.6084/m9.figshare.31222900

[8] Magnusson, M. (2026h). EFC-C v2.0: Quantitative Entropy-Gradient Predictions for Cognitive States (superseded). DOI: 10.6084/m9.figshare.32091700 v1

[9] Carhart-Harris, R.L. et al. (2014). The entropic brain: a theory of conscious states informed by neuroimaging research with psychedelic drugs. Front. Hum. Neurosci. 8, 20.

[10] Carhart-Harris, R.L. (2018). The entropic brain — revisited. Neuropharmacology 142, 167–178.

[11] Friston, K. (2010). The free-energy principle: a unified brain theory? Nat. Rev. Neurosci. 11, 127–138.

[12] Gu, S. et al. (2015). Controllability of structural brain networks. Nat. Commun. 6, 8414.

[13] Sanz-Leon, P. et al. (2015). Mathematical framework for large-scale brain network modelling in The Virtual Brain. NeuroImage 111, 385–430.

[14] Robinson, P.A. et al. (2016). Determination of effective brain connectivity from activity correlations. Phys. Rev. E 90, 012707.

[15] Rosas, F.E. et al. (2023). A whole-brain model of the neural entropy increase elicited by psychedelic drugs. Sci. Rep. 13, 6615.
