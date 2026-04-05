# EFC-C v2.0: Quantitative Entropy-Gradient Predictions for Cognitive States

## A Connectome-Constrained Framework with Falsifiable Diagnostic Signatures

**Morten Magnusson**
Symbiose Research, Sandnes, Norway
ORCID: 0009-0002-4860-5095

Research Note v2.0 — April 2026
DOI: [pending]

---

## Abstract

We present a revised and quantified version of Energy-Flow Cosmology–Cognition
(EFC-C), a thermodynamic framework for neural entropy gradients. Where the
original EFC-C (v0.1) offered qualitative consistency with published findings, this
revision introduces three formal, falsifiable predictions grounded in a single
dimensionless observable: the centrifugal entropy score kappa = <S_hub> / <S_periph>.
Using the Bridge B1* equation from the EFC cross-domain framework, we derive
kappa_healthy = C / (1 + lambda_2 * tau_c), where C = 4.4 +/- 0.6 is fixed from
galactic dynamics (SPARC, Spor 1), lambda_2 is the Fiedler eigenvalue of the
structural connectome, and tau_c is the cortical entropy redistribution timescale.
We extend this to psychiatric populations by predicting that disorder-specific
changes in kappa are governed by changes in the structural connectome's algebraic
connectivity (Delta_lambda_2). We specify exact datasets (HCP, OpenNeuro),
analysis pipelines, and falsification thresholds. No parameters are fit to neural
data.

**Keywords:** neural entropy, connectome topology, Fiedler eigenvalue, psychiatric
biomarkers, entropy gradient, resting-state fMRI, schizophrenia, depression

**Epistemic status:** Quantitative predictions derived from cross-domain parameter
transfer. No original data analysis included. All predictions are prospective and
falsifiable.

---

## 1. Introduction

### 1.1 The Problem with Scalar Entropy

The Entropic Brain Hypothesis (EBH; Carhart-Harris et al. 2014) established that
the *magnitude* of neural entropy indexes conscious state richness: psychedelic states
show elevated entropy; disorders of consciousness show reduced entropy. This has
substantial empirical support (Carhart-Harris 2018; Rosas et al. 2023).

However, scalar entropy is insufficient as a diagnostic tool. Two patients can have
identical total brain entropy yet radically different cognitive states, because the
*spatial distribution* of entropy across cortical networks differs. Depression and
schizophrenia may both show altered entropy, but the *topology* of that alteration
is distinct.

### 1.2 What This Paper Adds

We introduce a single quantitative observable — the **centrifugal entropy score**
kappa — that captures the *directional structure* of entropy flow across the
connectome. We derive kappa from the EFC cross-domain framework using parameters
fixed entirely from galactic dynamics, making this a parameter-free prediction for
neural data.

We then extend kappa to psychiatric populations, predicting that diagnosis-specific
changes in kappa are governed by measurable changes in structural connectivity.

### 1.3 What This Paper Does NOT Claim

- We do not claim the brain and the cosmos are "the same system"
- We do not claim a causal mechanism linking gravitational and neural dynamics
- We claim only that both systems belong to the same *mathematical class* of
  dissipative gradient-flow systems, and that a dimensionless parameter (C = k/a_G)
  derived from one domain generates testable predictions in the other

---

## 2. The Centrifugal Entropy Score

### 2.1 Definition

For a brain parcellated into N regions {R_i}, we define the local entropy production
proxy S_i from the resting-state fMRI BOLD time series of region i, estimated via
multiscale sample entropy (MSE) at coarse temporal scales 4-6 (see Section 4.3).

Regions are classified by structural degree:

- **Hub regions** (R_hub): top 10% of nodes by weighted degree in the structural
  connectome. These correspond approximately to default mode network (DMN) and
  frontoparietal hubs.

- **Peripheral regions** (R_periph): bottom 30% of nodes by weighted degree.
  These correspond approximately to primary sensory and motor cortex (V1, A1, S1, M1).

The centrifugal entropy score is:

```
kappa = <S_hub> / <S_periph>
```

where angle brackets denote the unweighted mean over nodes in each group.

**Interpretation:**
- kappa > 1: Centrifugal gradient (hub-to-periphery). Healthy resting state.
- kappa ~ 1: Flat entropy field. No directional structure.
- kappa < 1: Centripetal gradient (periphery-to-hub). Pathological inversion.

### 2.2 Relation to EBH

EBH predicts: higher total entropy = richer conscious state.
EFC-C predicts: kappa encodes the *topology* of that entropy.

EBH is the scalar projection of the EFC-C gradient field. The two are not
competing: EBH captures magnitude, EFC-C captures direction.

---

## 3. Quantitative Predictions

### 3.1 Prediction Q1: Healthy Resting-State kappa

From Bridge B1* (Magnusson 2026, Bridge Equations):

```
kappa_healthy = C / (1 + lambda_2(W) * tau_c)
```

where:
- C = k / a_G = 4.4 +/- 0.6 (fixed from SPARC galactic fit; Spor 1)
- lambda_2(W) = Fiedler eigenvalue of the normalized graph Laplacian
  L_sym = I - D^{-1/2} W D^{-1/2}, constructed from the structural connectome W
- tau_c = L_parcel^2 / D_eff ~ 3.5 s (range 2-5 s), where L_parcel ~ 5 mm
  (HCP MMP1.0 atlas) and D_eff ~ 3 mm/s (Sanz-Leon et al. 2015)

For published HCP values lambda_2 in [0.3, 0.8]:

| lambda_2 | tau_c | kappa_pred |
|----------|-------|------------|
| 0.3      | 2.0   | 2.75       |
| 0.5      | 3.5   | 1.60       |
| 0.8      | 5.0   | 0.88       |

**Central prediction:** For the typical HCP subject (lambda_2 ~ 0.5, tau_c ~ 3.5 s),
kappa_healthy ~ 1.6.

**No parameters are fit to neural data.** C is from galaxies. lambda_2 is from
structural connectome. tau_c is from independent neural-field modelling.

**Falsification criterion Q1:**
- If group-mean kappa_obs deviates from kappa_pred by > 3 sigma in n >= 20 HCP
  subjects, the prediction is falsified.
- If Pearson r(kappa_obs, 1/lambda_2) < 0.30 for n >= 20, the scaling law is
  falsified.

### 3.2 Prediction Q2: Disorder-Specific kappa Shifts

We extend Bridge B1* to psychiatric populations by noting that structural
connectome alterations change lambda_2. The prediction is:

```
Delta_kappa = kappa_healthy - kappa_disorder
            = C * [ 1/(1 + lambda_2_h * tau_c) - 1/(1 + lambda_2_d * tau_c) ]
```

where lambda_2_h and lambda_2_d are the Fiedler values for healthy and disordered
structural connectomes respectively, and tau_c is assumed constant across groups
(testable assumption).

**Published structural connectome findings:**

| Condition      | Known connectome change             | Predicted lambda_2 shift | Predicted kappa shift |
|---------------|-------------------------------------|--------------------------|----------------------|
| Schizophrenia | Reduced frontotemporal connectivity | lambda_2_scz < lambda_2_h | kappa_scz > kappa_h (paradoxical elevation due to reduced short-circuiting) |
| MDD           | Reduced global efficiency           | lambda_2_mdd < lambda_2_h | kappa_mdd > kappa_h (similar direction, different magnitude) |
| Healthy       | Baseline                            | lambda_2_h ~ 0.5         | kappa_h ~ 1.6       |

**Critical nuance:** Both schizophrenia and MDD show *reduced* lambda_2 (weaker
global connectivity). The B1* formula predicts this *increases* kappa (because
lower lambda_2 means less "short-circuiting" of the entropy gradient). This is
a counterintuitive but specific prediction.

However, the *topological distribution* of the entropy shift differs:
- In schizophrenia, the lambda_2 reduction is driven by frontotemporal
  dysconnection, which preferentially elevates *anterior* hub entropy
- In MDD, the reduction is more diffuse, with posterior default-mode changes

To capture this, we define the **anterior-posterior entropy asymmetry**:

```
alpha_AP = <S_anterior_hub> / <S_posterior_hub>
```

where anterior hubs = medial prefrontal, anterior cingulate, lateral prefrontal;
posterior hubs = precuneus, posterior cingulate, angular gyrus.

**Prediction Q2a (Schizophrenia):** alpha_AP_scz > alpha_AP_healthy
(anterior-dominant entropy elevation)

**Prediction Q2b (MDD):** alpha_AP_mdd < alpha_AP_healthy
(posterior-shifted entropy)

**Falsification criterion Q2:**
- If Delta_kappa and Delta_lambda_2 are uncorrelated (r < 0.25) across n >= 15
  subjects per group, the structural-entropic coupling is falsified.
- If alpha_AP does not discriminate schizophrenia from MDD (AUC < 0.60), the
  topological prediction is falsified.

### 3.3 Prediction Q3: Entropy Threshold for Cognitive Coherence

We predict a minimum entropy production rate below which coordinated cognition
degrades:

```
kappa_crit = C / (1 + lambda_2_max * tau_c_max)
```

Using the upper bounds lambda_2_max ~ 1.0 and tau_c_max ~ 5 s:

```
kappa_crit = 4.4 / (1 + 5.0) = 0.73
```

**Prediction:** When kappa_obs < 0.73, the system has lost its centrifugal gradient
structure. This corresponds to severely disrupted connectivity (high lambda_2,
indicating strong but pathological coupling) or very slow redistribution.

This maps to disorders of consciousness: vegetative state, deep anaesthesia,
and late-stage neurodegeneration.

**Falsification criterion Q3:**
- If patients with confirmed disorders of consciousness (UWS/VS) show kappa_obs
  significantly above 0.73 (i.e., maintained centrifugal gradient), the threshold
  prediction is falsified.

---

## 4. Methods: Prospective Validation Protocol

### 4.1 Datasets

| Dataset | Population | n (target) | Modalities | Access |
|---------|-----------|------------|------------|--------|
| HCP 1200 | Healthy adults | 50 | Structural (DTI) + rs-fMRI | ConnectomeDB |
| OpenNeuro ds000030 (UCLA) | Schizophrenia + healthy | 50 + 50 | Structural + rs-fMRI | OpenNeuro |
| OpenNeuro ds000171 | MDD + healthy | 20 + 20 | rs-fMRI | OpenNeuro |

### 4.2 Structural Connectome and lambda_2

1. Construct weighted adjacency matrix W from probabilistic tractography
   (streamline density between HCP MMP1.0 parcels, 360 regions).
2. Compute normalized graph Laplacian: L_sym = I - D^{-1/2} W D^{-1/2}
3. Extract lambda_2 = second-smallest eigenvalue of L_sym
4. Define hub (top 10% degree) and peripheral (bottom 30% degree) node sets

### 4.3 Entropy Proxy: Multiscale Sample Entropy

1. Extract BOLD time series per parcel (ICA-FIX denoised for HCP; standard
   preprocessing for OpenNeuro)
2. Compute multiscale sample entropy (MSE) at scales 4-6 (TR-dependent;
   for HCP 3T with TR=0.72s this captures fluctuations at ~3-4 s timescale)
3. Average MSE across scales 4-6 per parcel to obtain S_i

**Why scales 4-6:** These coarse scales isolate macroscopic dissipative dynamics
from high-frequency physiological noise (cardiac, respiratory). The timescale
(~3-4 s) matches tau_c, ensuring the entropy proxy captures the process the
model describes.

### 4.4 Statistical Analysis

**Primary test (Q1):**
- Compute kappa per HCP subject
- Test: Pearson r(kappa, 1/lambda_2) with 95% CI via bootstrap
- Secondary: Compare group mean kappa against predicted kappa(lambda_2_mean)

**Group comparison (Q2):**
- Two-sample t-test on kappa: healthy vs schizophrenia, healthy vs MDD
- Correlation: r(Delta_kappa, Delta_lambda_2) across all subjects
- ROC analysis: alpha_AP as classifier for schizophrenia vs MDD

**Threshold test (Q3):**
- If disorders-of-consciousness data available: test kappa against 0.73 threshold

### 4.5 Pre-Registration

Analysis code will be deposited at github.com/symbiose-research prior to data
access. The pipeline includes:
- connectome_lambda2.py: W -> L_sym -> lambda_2
- entropy_mse.py: BOLD -> MSE(scales 4-6) -> S_i per parcel
- kappa_analysis.py: S_i + hub/periph classification -> kappa, alpha_AP

---

## 5. Relation to Existing Frameworks

### 5.1 EBH (Carhart-Harris et al.)

EBH correctly identifies entropy magnitude as an index of conscious state. EFC-C
extends this by predicting the *spatial topology* of entropy. The centrifugal score
kappa is the quantitative realisation of this extension. EBH is not wrong — it is
incomplete.

### 5.2 Free Energy Principle (Friston)

FEP describes agents as minimising variational free energy. EFC-C describes brain
states as configurations on a Helmholtz free-energy landscape. The connection is
structural: both frameworks instantiate gradient-flow dynamics on a free-energy
functional. The distinction is that EFC-C derives specific numerical predictions
from cross-domain parameter transfer, while FEP operates within a single domain.

### 5.3 Bridge B1* (Cross-Domain)

The kappa prediction depends on C = 4.4 from galactic data. If the B1* bridge
is independently validated (P4* test in Bridge paper), this strengthens all
EFC-C predictions. If B1* is falsified, the specific numerical values of kappa
must be revised, but the *topological* predictions (Q2a, Q2b) survive because
they depend on Delta_lambda_2, not on C.

This asymmetry is important: the topological predictions are more robust than the
absolute-level predictions.

---

## 6. Limitations

1. **tau_c is semi-empirical.** The entropy redistribution timescale is estimated
   from literature (D_eff ~ 3 mm/s, L_parcel ~ 5 mm), not derived from the model.
   Variation in tau_c across subjects is a noise source.

2. **MSE as entropy proxy.** Sample entropy is a statistical measure, not a
   thermodynamic quantity. The identification S_i ~ MSE(BOLD_i) is standard in the
   field but remains a proxy. Alternative measures (LZC, permutation entropy) should
   be tested for robustness.

3. **Hub/periphery classification.** The 10%/30% thresholds are conventional. We
   will test sensitivity to threshold choice (5-15% / 20-40%) as a robustness check.

4. **No mechanistic derivation.** We do not derive *why* C from galaxies should
   predict kappa in brains. We predict *that* it does and specify how to test it.
   A mechanistic explanation (renormalisation, universal scaling) is future work.

5. **Cross-sectional design.** The proposed tests are cross-sectional. Longitudinal
   predictions (e.g., kappa changes during treatment) are deferred to v3.0.

---

## 7. Summary of Predictions and Falsification

| Code | Prediction | Observable | Falsification |
|------|-----------|-----------|---------------|
| Q1 | kappa_healthy ~ 1.6; kappa ~ 1/lambda_2 | kappa from HCP MSE + connectome | r < 0.30 (n >= 20) or abs(z) > 3 on mean |
| Q2a | alpha_AP_scz > alpha_AP_healthy | Anterior/posterior hub entropy ratio | Effect not detected (p > 0.05, n >= 15/group) |
| Q2b | alpha_AP_mdd < alpha_AP_healthy | Anterior/posterior hub entropy ratio | Effect not detected (p > 0.05, n >= 15/group) |
| Q2c | Delta_kappa correlates with Delta_lambda_2 | Cross-group structural-entropic coupling | r < 0.25 (n >= 30 pooled) |
| Q3 | kappa < 0.73 in disorders of consciousness | kappa in UWS/VS patients | kappa_DoC > 0.73 significantly |

---

## 8. Reproducibility

This note presents prospective predictions. No original data analysis is included.
All parameter values are sourced as follows:
- C = k/a_G: from Spor 1 (DOI: 10.6084/m9.figshare.31301953)
- lambda_2 ranges: from Gu et al. (2015), HCP structural connectome literature
- tau_c: from Sanz-Leon et al. (2015), Robinson et al. (2016)
- Psychiatric connectome alterations: from published meta-analyses

Analysis code will be deposited at github.com/symbiose-research/efc-c-validation
prior to data access.

---

## References

[1] Carhart-Harris, R.L. et al. (2014). The entropic brain: a theory of conscious
    states informed by neuroimaging research with psychedelic drugs. Front. Hum.
    Neurosci. 8, 20.

[2] Carhart-Harris, R.L. (2018). The entropic brain — revisited. Neuropharmacology
    142, 167-178.

[3] Rosas, F.E. et al. (2023). A whole-brain model of the neural entropy increase
    elicited by psychedelic drugs. Sci. Rep. 13, 6615.

[4] Friston, K. (2010). The free-energy principle: a unified brain theory? Nat. Rev.
    Neurosci. 11, 127-138.

[5] Gu, S. et al. (2015). Controllability of structural brain networks. Nat. Commun.
    6, 8414.

[6] Sanz-Leon, P. et al. (2015). Mathematical framework for large-scale brain network
    modelling in The Virtual Brain. NeuroImage 111, 385-430.

[7] Robinson, P.A. et al. (2016). Determination of effective brain connectivity from
    activity correlations. Phys. Rev. E 90, 012707.

[8] Noroozi, A. et al. (2025). Machine learning-based differentiation of schizophrenia
    and bipolar disorder using multiscale fuzzy entropy. Transl. Psychiatry 15, 120.

[9] Pan, S. et al. (2025). Novel EEG-based diagnostic framework for major depressive
    disorder using microstate and entropy features. Cogn. Neurodyn.

[10] Creel, W.T. & Hartman, R.E. (2025). EEG entropy modulation as a biomarker of
     emotion regulation and resilience. IBRO Neurosci. Rep.

[11] Magnusson, M. (2026). Energy-Flow Cosmology: Empirical Validation of the EFC
     Screening Model Against the Radial Acceleration Relation. Figshare.
     DOI: 10.6084/m9.figshare.31301953

[12] Magnusson, M. (2026). Cross-Domain Bridge Equations for the EFC Framework.
     Research Note v0.1.

[13] Magnusson, M. (2026). EFC-C v0.1: A Thermodynamic Framework for Cognitive
     Entropy and Psychiatric Biomarkers. Research Note v0.1.
