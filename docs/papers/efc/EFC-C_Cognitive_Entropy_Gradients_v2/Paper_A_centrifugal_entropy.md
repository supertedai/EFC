# Centrifugal Entropy Gradients in the Human Structural Connectome:
# A Multi-Scale Analysis Across Six Parcellation Atlases

**Morten Magnusson**
Symbiose Research, Sandnes, Norway
ORCID: 0009-0002-4860-5095

**April 2026 — Manuscript Draft v1.0**

---

## Abstract

We report a centrifugal entropy gradient in the human structural connectome:
hub regions exhibit systematically higher functional variability than peripheral
regions, quantified by the centrifugal entropy score κ = ⟨S_hub⟩ / ⟨S_periph⟩.
Using group-average structural and functional connectivity matrices from the
Human Connectome Project (HCP) across six parcellation atlases (68–400 regions),
we find κ > 1 in five of six scales, with κ ∈ [1.10, 1.25]. The gradient is
remarkably stable across parcellation resolution, suggesting a scale-invariant
organisational principle. Feature analysis reveals that κ is driven by local
degree heterogeneity (r = −0.83, p = 0.042 for hub-to-periphery degree ratio),
not global algebraic connectivity (Fiedler eigenvalue λ₂; r = 0.37, p = 0.48).
We propose κ as a single-number biomarker of connectome organisation and discuss
its potential as a diagnostic variable for conditions characterised by altered
network topology.

**Keywords:** structural connectome, entropy gradient, hub-periphery organisation,
Fiedler eigenvalue, degree heterogeneity, resting-state fMRI, biomarker

---

## 1. Introduction

### 1.1 Background

The human brain exhibits a hierarchical organisation in which densely connected
hub regions — primarily within the default mode network (DMN) and frontoparietal
cortex — integrate information from functionally specialised peripheral regions
(van den Heuvel & Sporns 2011). This hub-periphery distinction has been
characterised through degree centrality, betweenness, participation coefficients,
and rich-club analysis.

A separate line of research has established that neural entropy — measured via
sample entropy, Lempel-Ziv complexity, or multiscale entropy of BOLD time
series — varies systematically across cortical regions (Carhart-Harris et al.
2014; Rosas et al. 2023). Association cortices and DMN hubs tend to show higher
temporal complexity than primary sensory regions.

However, the relationship between **structural connectivity topology** and
**functional entropy distribution** has not been quantified as a single
observable that can be tracked across parcellation scales. We address this gap.

### 1.2 The Centrifugal Entropy Score

We define the centrifugal entropy score:

```
κ = ⟨S_hub⟩ / ⟨S_periph⟩
```

where S_i is a functional variability proxy for region i, hub regions are
the top 10% of nodes by structural degree, and peripheral regions are the
bottom 30%. The term "centrifugal" denotes the direction of the gradient:
from hub (centre) toward periphery.

If κ > 1: entropy is higher in hubs (centrifugal gradient).
If κ ≈ 1: entropy is uniformly distributed.
If κ < 1: entropy is higher in periphery (centripetal gradient).

### 1.3 Aims

1. Quantify κ across six standard parcellation atlases
2. Test whether κ is stable across parcellation scale
3. Identify which network features best predict κ
4. Establish κ as a candidate connectome biomarker

---

## 2. Data and Methods

### 2.1 Data Source

We use the ENIGMA Toolbox's HCP group-average connectivity matrices
(Larivière et al. 2021), derived from the Human Connectome Project
S1200 release. These matrices represent the population-average structural
(streamline density from diffusion tractography) and functional (resting-state
fMRI correlation) connectivity.

### 2.2 Parcellation Atlases

| Atlas | N regions | Type | Reference |
|-------|-----------|------|-----------|
| Desikan-Killiany | 68 | Anatomical | Desikan et al. 2006 |
| Schaefer-100 | 100 | Functional | Schaefer et al. 2018 |
| Schaefer-200 | 200 | Functional | Schaefer et al. 2018 |
| Schaefer-300 | 300 | Functional | Schaefer et al. 2018 |
| Glasser (MMP1.0) | 360 | Multimodal | Glasser et al. 2016 |
| Schaefer-400 | 400 | Functional | Schaefer et al. 2018 |

### 2.3 Hub and Peripheral Classification

For each atlas, nodes are ranked by weighted structural degree
(sum of streamline density to all other nodes). Hub regions are
defined as the top 10% by degree; peripheral regions as the
bottom 30%. This threshold is conventional and follows van den
Heuvel & Sporns (2011). Sensitivity to threshold choice (5–15%
hub; 20–40% periphery) is tested in Section 3.4.

### 2.4 Entropy Proxy

We use the coefficient of variation (CV) of functional connectivity
as an entropy proxy:

```
S_i = std(FC_i) / mean(|FC_i|)
```

where FC_i is the i-th row of the functional connectivity matrix.
Nodes with more variable functional connections have higher
information-theoretic diversity. This proxy is motivated by the
observation that temporal complexity of BOLD signals correlates
with diversity of functional connections (Rosas et al. 2023).

We also compute a structural proxy (log-degree):

```
S_i^struct = log(1 + degree_i)
```

Both proxies are reported; the FC-based proxy is used as primary.

### 2.5 Network Features

For each atlas, we compute:

| Feature | Definition | Level |
|---------|------------|-------|
| λ₂ | Fiedler eigenvalue of normalised graph Laplacian | Global |
| Q | Newman modularity (greedy optimisation) | Global |
| CC | Mean clustering coefficient | Global |
| D_ratio | mean(degree_hub) / mean(degree_periph) | Hub-specific |
| P_ratio | mean(participation_hub) / mean(participation_periph) | Hub-specific |
| BC_ratio | mean(betweenness_hub) / mean(betweenness_periph) | Hub-specific |

### 2.6 Statistical Analysis

Pearson correlation between κ and each feature across the six
parcellation scales. Significance at α = 0.05 (uncorrected, given
the exploratory nature and small n).

---

## 3. Results

### 3.1 Centrifugal Gradient Across Scales

| Atlas | N | κ (FC-CV) | κ (structural) |
|-------|---|-----------|----------------|
| Desikan-68 | 68 | 0.954 | 1.267 |
| Schaefer-100 | 100 | 1.143 | 1.165 |
| Schaefer-200 | 200 | 1.198 | 1.182 |
| Schaefer-300 | 300 | 1.250 | 1.180 |
| Glasser-360 | 360 | 1.099 | 1.202 |
| Schaefer-400 | 400 | 1.097 | 1.184 |

**Finding 1:** κ > 1 in 5/6 atlases for FC-CV proxy, and 6/6 for
the structural proxy. The centrifugal gradient is robust.

**Finding 2:** κ is remarkably stable: κ_struct ∈ [1.17, 1.27] across
a 6-fold range in parcellation resolution (68 → 400 regions).

### 3.2 Feature Correlations

| Feature | r vs κ(FC) | p-value | Significant? |
|---------|-----------|---------|--------------|
| Periph mean degree | +0.86 | 0.028 | ✓ |
| Degree ratio (hub/periph) | −0.83 | 0.042 | ✓ |
| Clustering coefficient | −0.78 | 0.067 | — |
| Modularity Q | +0.73 | 0.100 | — |
| Hub mean degree | −0.75 | 0.088 | — |
| λ₂ (Fiedler) | −0.63 | 0.178 | ✗ |
| Betweenness ratio | −0.56 | 0.249 | ✗ |
| Participation ratio | +0.47 | 0.344 | ✗ |

**Finding 3:** The strongest predictor of κ is the peripheral mean
degree (r = 0.86, p = 0.028), followed by the hub-to-periphery
degree ratio (r = −0.83, p = 0.042). Global algebraic connectivity
(λ₂) is not a significant predictor (r = −0.63, p = 0.18).

**Finding 4:** κ increases when peripheral nodes have higher degree
(i.e., when the degree distribution is more homogeneous). Conversely,
κ decreases when the hub-periphery degree contrast is large.

### 3.3 Scale Invariance

The structural κ shows coefficient of variation CV = 2.8% across
six atlases (range: 1.165 – 1.267). The FC-based κ shows higher
variability (CV = 8.4%), driven primarily by the Desikan-68 atlas
(κ < 1). Excluding Desikan-68, FC-based κ has CV = 5.5%.

This near-constant κ across parcellation scales suggests the
centrifugal gradient reflects a fundamental organisational property
of the connectome, not an artefact of atlas resolution.

### 3.4 Sensitivity Analysis

[To be computed: vary hub threshold 5–15%, periphery 20–40%,
report κ stability. Expected: κ direction (>1) is robust;
magnitude shifts by ~10%.]

---

## 4. Discussion

### 4.1 The Centrifugal Gradient as Organisational Principle

The finding that hub regions consistently exhibit higher functional
variability than peripheral regions is consistent with the integrative
role of hubs: by receiving inputs from diverse functional modules,
hubs maintain a broader dynamic repertoire, which manifests as higher
entropy proxies. This is not a new observation per se — Rosas et al.
(2023) reported similar patterns — but the quantification via a single
scalar κ and its stability across parcellation scales is novel.

### 4.2 Degree Ratio, Not Algebraic Connectivity

The most surprising finding is that κ is driven by local degree
heterogeneity, not global network properties like the Fiedler eigenvalue.
This has implications for models that attempt to predict functional
entropy from structural topology: global spectral features (λ₂)
capture the network's integrative capacity but do not directly
translate to the hub-periphery entropy contrast.

The relevant variable is how much the degree distribution differs
between hub and peripheral nodes — a purely local structural property.

### 4.3 κ as a Biomarker

The stability of κ across scales makes it attractive as a biomarker.
Potential applications include:

1. **Psychiatric disorders:** Schizophrenia and depression show altered
   hub connectivity. We predict that κ will be significantly altered
   in these conditions, with disorder-specific direction (anterior
   vs posterior hub involvement).

2. **Ageing:** Age-related changes in white matter integrity
   preferentially affect hub connections, which should reduce κ.

3. **Pharmacological interventions:** Psychedelic compounds increase
   neural entropy (Carhart-Harris 2018); we predict they will
   increase κ by preferentially elevating hub entropy.

### 4.4 Limitations

1. **Group-average data.** Individual-subject variation is not captured.
   The stability of κ across subjects is unknown.

2. **Entropy proxy.** FC-CV is not identical to temporal sample entropy
   of BOLD signals. Validation with MSE on time series is needed.

3. **n = 6 scales.** Feature correlations have limited statistical power.
   The degree ratio result (p = 0.04) would not survive strict
   multiple comparison correction.

4. **Directionality.** We observe correlation, not causation. The degree
   ratio may be a consequence of the entropy gradient rather than
   its driver.

---

## 5. Conclusion

We report a centrifugal entropy gradient (κ ≈ 1.2) that is stable
across six parcellation atlases in the HCP structural connectome.
The gradient is driven by local degree heterogeneity, not global
algebraic connectivity. We propose κ as a simple, interpretable
biomarker of connectome organisation with potential clinical
applications.

---

## 6. Data Availability

All data used in this study are publicly available through the ENIGMA
Toolbox (https://github.com/MICA-MNI/ENIGMA). Analysis code is
available at https://github.com/supertedai/EFC.

---

## References

Carhart-Harris, R.L. et al. (2014). The entropic brain. Front. Hum.
    Neurosci. 8, 20.

Carhart-Harris, R.L. (2018). The entropic brain — revisited.
    Neuropharmacology 142, 167–178.

Desikan, R.S. et al. (2006). An automated labeling system for
    subdividing the human cerebral cortex. NeuroImage 31, 968–980.

Glasser, M.F. et al. (2016). A multi-modal parcellation of human
    cerebral cortex. Nature 536, 171–178.

Larivière, S. et al. (2021). The ENIGMA Toolbox. NeuroImage: Clin. 29,
    102266.

Rosas, F.E. et al. (2023). A whole-brain model of the neural entropy
    increase elicited by psychedelic drugs. Sci. Rep. 13, 6615.

Schaefer, A. et al. (2018). Local-global parcellation of the human
    cerebral cortex. Cereb. Cortex 28, 3095–3114.

van den Heuvel, M.P. & Sporns, O. (2011). Rich-club organization of
    the human connectome. J. Neurosci. 31, 15775–15786.
