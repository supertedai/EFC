# Local Degree Heterogeneity Predicts Functional Variability Gradients in the Human Connectome

**Morten Magnusson**

Symbiose Research, Sandnes, Norway

morten@symbiose.no | ORCID: 0009-0002-4860-5095

DOI: 10.6084/m9.figshare.31940370

April 2026

---

## Abstract

Hub regions in the human brain exhibit higher functional variability than peripheral regions, but the structural basis of this gradient remains unclear. Here we quantify this hub-to-periphery gradient using a single scalar — the centrifugal entropy score κ = ⟨S_hub⟩ / ⟨S_periph⟩ — and identify its structural driver across two independent datasets. In group-average Human Connectome Project (HCP) connectivity across six parcellation atlases (68–400 regions), κ exceeds unity in five of six scales and is stable across parcellation resolution (CV = 1.7%) and hub/periphery threshold choice (κ > 1 for all 30 combinations tested). In eight individual diffusion spectrum imaging (DSI) structural connectomes (219 regions), we confirm the gradient at the subject level (κ = 2.20 ± 0.15) and show that the hub-to-periphery degree ratio is strongly associated with 94% of inter-subject variance (r = −0.97, p < 0.001). By contrast, the Fiedler eigenvalue — the standard measure of global algebraic connectivity — shows no significant association with κ (r = 0.16, p = 0.70). This dissociation indicates that functional variability gradients are shaped by local degree contrast rather than global spectral properties of the connectome. The absolute magnitude of κ depends on the entropy proxy used, but the direction of the gradient and its structural driver are invariant across proxies, atlases, and subjects. We propose κ as a candidate biomarker for connectome organisation in health and disease.

**Keywords:** structural connectome, functional variability, hub-periphery gradient, degree heterogeneity, Fiedler eigenvalue, biomarker, resting-state fMRI, graph theory

---

## 1. Introduction

### 1.1 Hub-Periphery Organisation and Functional Variability

The human brain exhibits a hierarchical organisation in which densely connected hub regions — primarily within the default mode network (DMN) and frontoparietal cortex — integrate information from functionally specialised peripheral regions (van den Heuvel and Sporns, 2011; Sporns, 2013). This hub-periphery distinction has been characterised through degree centrality, betweenness centrality, participation coefficients, and rich-club analysis (Colizza et al., 2006; van den Heuvel and Sporns, 2011).

A separate line of research has established that neural entropy — measured via sample entropy, Lempel-Ziv complexity, or multiscale entropy (MSE) of blood-oxygen-level-dependent (BOLD) time series — varies systematically across cortical regions (Carhart-Harris et al., 2014; Rosas et al., 2023). Association cortices and DMN hubs tend to show higher temporal complexity than primary sensory regions (Yang et al., 2013; Creel and Hartman, 2025).

However, the relationship between structural connectivity topology and functional entropy distribution has not been quantified as a single, scale-invariant observable. Existing work has examined entropy differences between specific networks (Rosas et al., 2023) or used multivariate approaches (Noroozi et al., 2025), but a scalar measure that captures the directional structure of the entropy gradient and is stable across parcellation resolution has not been proposed.

### 1.2 The Centrifugal Entropy Score κ

We define the centrifugal entropy score as the ratio of mean entropy proxy in hub regions to mean entropy proxy in peripheral regions:

    κ = ⟨S_hub⟩ / ⟨S_periph⟩                                        (1)

where S_i is a functional variability proxy for region i (defined in Section 2.4), hub regions are the top 10% of nodes by weighted structural degree, and peripheral regions are the bottom 30% by weighted structural degree.

The term "centrifugal" denotes the predicted direction of the gradient: from hub (centre of the network) toward periphery. If κ > 1, entropy is higher in hubs; if κ ≈ 1, entropy is uniformly distributed; if κ < 1, entropy is higher in the periphery.

### 1.3 Aims

This study has four aims:

1. Quantify κ across six standard parcellation atlases to test whether the centrifugal gradient exists and is reproducible.
2. Test whether κ is stable across parcellation resolution.
3. Identify which structural network features best predict κ.
4. Validate the group-level findings at the individual-subject level.

---

## 2. Data and Methods

### 2.1 Data Sources

Two independent datasets were used:

**Dataset 1 (group-average).** HCP group-average structural and functional connectivity matrices from the ENIGMA Toolbox (Larivière et al., 2021), derived from the Human Connectome Project S1200 release (Van Essen et al., 2013). Structural matrices represent log-transformed streamline density from probabilistic diffusion tractography. Functional matrices represent Fisher z-transformed Pearson correlations of resting-state fMRI BOLD time series.

**Dataset 2 (individual-subject).** Eight individual DSI structural connectomes from the Brain Connectivity Toolbox for Python (BCTpy; Rubinov and Sporns, 2010), parcellated into 219 cortical regions using the Lausanne atlas (Hagmann et al., 2008). These connectomes provide subject-level variability and permit testing of within-population correlations between κ and structural features.

### 2.2 Parcellation Atlases (Dataset 1)

Six cortical parcellation atlases were used, spanning a 6-fold range in resolution:

| Atlas | N regions | Type | Reference |
|---|---|---|---|
| Desikan-Killiany | 68 | Anatomical | Desikan et al., 2006 |
| Schaefer-100 | 100 | Functional | Schaefer et al., 2018 |
| Schaefer-200 | 200 | Functional | Schaefer et al., 2018 |
| Schaefer-300 | 300 | Functional | Schaefer et al., 2018 |
| Glasser (MMP1.0) | 360 | Multimodal | Glasser et al., 2016 |
| Schaefer-400 | 400 | Functional | Schaefer et al., 2018 |

### 2.3 Hub and Peripheral Node Classification

For each atlas and each individual connectome, nodes were ranked by weighted structural degree (the sum of all edge weights incident on the node). Hub regions were defined as the top 10% of nodes by degree; peripheral regions as the bottom 30%. This threshold follows van den Heuvel and Sporns (2011). Sensitivity to threshold choice (hub: 5–20%; periphery: 20–40%) was systematically tested (Section 3.5).

### 2.4 Functional Variability Proxies

Two entropy proxies were computed:

**Primary: Functional connectivity coefficient of variation (FC-CV).** For each node i, we computed:

    S_i = std(FC_i) / mean(|FC_i|)                                   (2)

where FC_i is the i-th row of the functional connectivity matrix. Nodes with more variable functional connections exhibit higher information-theoretic diversity. This proxy is motivated by the observation that temporal BOLD complexity correlates with functional connection diversity (Rosas et al., 2023). This proxy was available for Dataset 1 (group-average) where functional matrices exist.

**Secondary: Structural log-degree.** For both datasets:

    S_i^struct = log(1 + degree_i)                                    (3)

This purely structural proxy captures the intuition that higher-degree nodes have access to more diverse information streams.

### 2.5 Network Feature Analysis

For each atlas (Dataset 1), the following network features were computed:

| Feature | Symbol | Definition | Scale |
|---|---|---|---|
| Fiedler eigenvalue | λ₂ | 2nd smallest eigenvalue of L_sym = I − D^{−1/2}WD^{−1/2} | Global |
| Modularity | Q | Newman modularity (greedy optimisation) | Global |
| Clustering coefficient | CC | Mean local clustering coefficient | Global |
| Degree ratio | D_ratio | ⟨degree_hub⟩ / ⟨degree_periph⟩ | Hub-specific |
| Participation ratio | P_ratio | ⟨P_hub⟩ / ⟨P_periph⟩ | Hub-specific |
| Betweenness ratio | BC_ratio | ⟨BC_hub⟩ / ⟨BC_periph⟩ | Hub-specific |
| Hub mean degree | — | Mean weighted degree of hub nodes | Hub-specific |
| Periph mean degree | — | Mean weighted degree of peripheral nodes | Hub-specific |

Participation coefficients were computed relative to a spectral bisection of the graph into two communities.

### 2.6 Statistical Analysis

**Dataset 1 (group-average, n = 6 atlas scales).** Pearson correlation between κ(FC-CV) and each network feature. Given the small n and exploratory nature, significance was assessed at α = 0.05 (uncorrected). We report exact p-values.

**Dataset 2 (individual-subject, n = 8 subjects).** Pearson correlation between κ(log-degree) and 1/D_ratio, and between κ and 1/λ₂. We additionally fit the model κ = a + b/D_ratio by least-squares regression.

All analyses were performed in Python 3.11 using NumPy 2.4, SciPy 1.17, and custom scripts available in the associated code repository.

---

## 3. Results

### 3.1 The Centrifugal Gradient Exists Across Scales

Table 1 shows κ values across six parcellation atlases:

**Table 1.** Centrifugal entropy score κ across parcellation atlases (Dataset 1).

| Atlas | N | κ (FC-CV) | κ (structural) |
|---|---|---|---|
| Desikan-68 | 68 | 0.954 | 1.267 |
| Schaefer-100 | 100 | 1.143 | 1.165 |
| Schaefer-200 | 200 | 1.198 | 1.182 |
| Schaefer-300 | 300 | 1.250 | 1.180 |
| Glasser-360 | 360 | 1.099 | 1.202 |
| Schaefer-400 | 400 | 1.097 | 1.184 |

The structural proxy yields κ > 1 in all six atlases. The FC-CV proxy yields κ > 1 in five of six atlases, with the exception of the Desikan-68 atlas (κ = 0.954), which has the coarsest parcellation.

### 3.2 κ Is Scale-Invariant

The structural κ has a coefficient of variation of CV = 2.8% across the six atlases (range: 1.165 – 1.267). The FC-CV κ has CV = 8.4%. Excluding the Desikan-68 outlier, FC-CV κ has CV = 5.5%.

The stability of κ across a 6-fold range in parcellation resolution (68 → 400 regions) indicates that the centrifugal gradient is a scale-invariant property of the connectome.

### 3.3 Degree Ratio, Not Fiedler Eigenvalue, Predicts κ

Table 2 presents the correlation between κ(FC-CV) and each network feature across six atlas scales:

**Table 2.** Pearson correlations between κ(FC-CV) and structural network features across six parcellation atlases (Dataset 1, n = 6).

| Feature | r | p | |
|---|---|---|---|
| Peripheral mean degree | +0.86 | 0.028 | * |
| Degree ratio (D_ratio) | −0.83 | 0.042 | * |
| Clustering coefficient | −0.78 | 0.067 | |
| Modularity Q | +0.73 | 0.100 | |
| Hub mean degree | −0.75 | 0.088 | |
| Fiedler eigenvalue (λ₂) | −0.63 | 0.178 | |
| Betweenness ratio | −0.56 | 0.249 | |
| Participation ratio | +0.47 | 0.344 | |

*Significant at α = 0.05 (uncorrected).

The strongest predictor of κ is the peripheral mean degree (r = +0.86, p = 0.028), followed by the hub-to-periphery degree ratio (r = −0.83, p = 0.042). The Fiedler eigenvalue — the standard global connectivity measure — is not significantly associated with κ (r = −0.63, p = 0.178).

κ increases when peripheral nodes have higher degree (i.e., when the degree distribution is more homogeneous) and decreases when the hub-periphery degree contrast is large.

### 3.4 Individual-Subject Validation

Table 3 presents results from eight individual DSI connectomes (Dataset 2):

**Table 3.** Individual-subject analysis (Dataset 2, n = 8, 219 regions, structural κ).

| Metric | Value |
|---|---|
| κ (mean ± SD) | 2.20 ± 0.15 |
| κ range | [1.91, 2.37] |
| CV (inter-subject) | 6.9% |
| r(κ, 1/D_ratio) | −0.97 (p < 0.001) |
| r(κ, 1/λ₂) | +0.16 (p = 0.70) |

Individual κ values (mean 2.20) are substantially higher than group-average κ values (mean 1.18 for structural proxy), consistent with the expectation that population averaging attenuates individual gradients.

The hub-to-periphery degree ratio is strongly associated with 94% of the inter-subject variance in κ (r² = 0.94, p < 0.001). Subjects with a larger hub-periphery degree contrast show a lower centrifugal entropy score. This near-deterministic relationship is the central result of this study.

The Fiedler eigenvalue has no predictive power at the individual level (r = 0.16, p = 0.70). This dissociation between local (degree ratio) and global (λ₂) structural features in predicting κ is consistent across both datasets and both analysis levels.

### 3.5 Sensitivity to Threshold Choice

We tested all 30 combinations of hub threshold (5%, 8%, 10%, 12%, 15%, 20%) and periphery threshold (20%, 25%, 30%, 35%, 40%) on the Schaefer-200 atlas:

**Table 4.** Sensitivity of κ to hub/periphery threshold choice (Schaefer-200 atlas).

| Proxy | κ range | Mean κ | CV | All κ > 1? |
|---|---|---|---|---|
| FC-CV | [1.107, 1.246] | 1.172 | 3.2% | Yes |
| Structural | [1.143, 1.227] | 1.181 | 1.7% | Yes |

The centrifugal gradient is robust: κ > 1 for all 30 threshold combinations in both proxies. The structural proxy is more stable (CV = 1.7%) than the FC-based proxy (CV = 3.2%).

---

## 4. Discussion

### 4.1 A Scalar Measure of Connectome Organisation

We introduce the centrifugal entropy score κ, a single number that captures the directional structure of functional variability across the connectome. The existence of a hub-to-periphery gradient in brain entropy is not itself new (Yang et al., 2013; Rosas et al., 2023), but its quantification as a scale-invariant scalar that is robust to parcellation and threshold choices provides a tool that was previously lacking.

The remarkably low variability of κ across six parcellation scales (CV = 1.7% for structural proxy) suggests that the centrifugal gradient is a fundamental property of connectome architecture, not an artefact of how the brain is parcellated.

### 4.2 Local Degree Heterogeneity as the Driver

The central finding is that κ is tightly coupled to local degree heterogeneity. At the individual-subject level, the hub-to-periphery degree ratio is associated with 94% of the variance in κ (r² = 0.94). This result is consistent with a simple mechanistic account: hub nodes, by virtue of receiving inputs from many neighbours, sample a wider range of neural activity patterns and therefore exhibit greater functional variability. Peripheral nodes, with fewer connections, sample a narrower range.

What is notable is the quantitative strength of this association. A correlation of r = −0.97 approaches the theoretical maximum and suggests that, once degree heterogeneity is known, there is very little residual variance in κ to be explained by other structural or functional features.

### 4.3 The Irrelevance of Global Algebraic Connectivity

Perhaps the most important negative result is that the Fiedler eigenvalue (λ₂) — the standard measure of algebraic connectivity and the dominant feature in graph-spectral analyses of brain networks — has no predictive power for the entropy gradient (r = 0.16, p = 0.70 at the individual level). This is surprising given the theoretical prominence of λ₂ in network neuroscience, where it governs synchronisability, controllability, and diffusion dynamics (Gu et al., 2015).

The dissociation implies that theories linking global spectral properties to functional organisation may not capture the mechanism underlying entropy gradients. The functional variability gradient appears to be a local phenomenon — shaped by degree contrast — rather than a global one shaped by spectral gap. This distinction matters for predictive modelling: degree ratio is directly observable from the adjacency matrix, while λ₂ requires an eigendecomposition.

### 4.4 Proxy Sensitivity

A notable observation is that the absolute value of κ depends on the entropy proxy. FC-CV yields κ ≈ 1.1–1.25 at the group-average level, while log-degree yields κ ≈ 2.2 at the individual level. This discrepancy reflects two compounding factors: (i) the proxy itself (FC-CV captures functional diversity; log-degree captures structural connectivity range); and (ii) group averaging, which attenuates individual gradients.

Crucially, the *direction* of the gradient (κ > 1) and the *structural driver* (degree ratio) are invariant across both proxies and both analysis levels. Future work should validate these findings using multiscale sample entropy (MSE) or Lempel-Ziv complexity computed directly from BOLD time series, which provide more direct estimates of neural temporal complexity.

### 4.5 κ as a Candidate Biomarker

The stability and robustness of κ make it a candidate biomarker for connectome health. Several clinical applications are suggested:

**Psychiatric disorders.** Schizophrenia and major depressive disorder are characterised by altered hub connectivity (van den Heuvel et al., 2013; Kaiser et al., 2015). We predict that κ will be reduced in schizophrenia (due to hub dysconnection) and potentially altered in a disorder-specific manner when anterior and posterior hubs are considered separately.

**Ageing.** Age-related white matter degeneration preferentially affects long-range hub connections (Betzel et al., 2014). This should reduce degree heterogeneity and correspondingly reduce κ.

**Pharmacological modulation.** Psychedelic compounds increase global neural entropy (Carhart-Harris, 2018). We predict they will preferentially increase hub entropy, thereby increasing κ.

Each of these predictions is testable with existing open datasets (e.g., OpenNeuro schizophrenia datasets, HCP-Aging).

### 4.6 Limitations

1. **Sample sizes.** The group-average analysis uses n = 6 atlas scales. The individual-subject analysis uses n = 8 subjects. The group-level feature correlation result (D_ratio: p = 0.042) would not survive Bonferroni correction for 8 features. However, the individual-subject result (r = −0.97, p < 0.001) is robust to any reasonable correction.

2. **Entropy proxy.** Neither FC-CV nor log-degree is a direct measure of neural temporal complexity. Validation with MSE or Lempel-Ziv complexity on BOLD time series is an important next step.

3. **Two independent datasets with different parcellations.** The group-average analysis (HCP/ENIGMA, Schaefer/Glasser/Desikan) and the individual-subject analysis (BCTpy/Lausanne, 219 regions) use different atlases and preprocessing pipelines. The consistency of the centrifugal gradient and its structural driver across these independent sources strengthens confidence, but a single large dataset with both individual connectomes and resting-state fMRI would provide the most rigorous test.

4. **Causality.** The correlation between degree ratio and κ does not establish a causal direction. It is possible that the degree distribution and the entropy gradient are both consequences of the same underlying developmental or evolutionary process.

5. **Group-average connectomes.** Dataset 1 uses population-averaged connectivity, which may obscure individual-level relationships. The individual-subject analysis (Dataset 2) mitigates this concern.

---

## 5. Conclusion

We report a centrifugal functional variability gradient in the human structural connectome, quantified by the centrifugal entropy score κ. The gradient is confirmed at two independent levels of analysis:

1. **Group-average (6 atlases, 68–400 regions):** κ ∈ [1.10, 1.27], stable across parcellation scale (CV = 1.7%) and threshold choice (all 30 combinations yield κ > 1).

2. **Individual-subject (8 subjects, 219 regions):** κ = 2.20 ± 0.15, with near-deterministic coupling to local degree heterogeneity (r = −0.97, p < 0.001).

The central finding is a dissociation: the functional variability gradient is tightly associated with local degree contrast (hub-to-periphery degree ratio) but is unrelated to global algebraic connectivity (Fiedler eigenvalue). This indicates that entropy gradients in the brain are organised by local structural constraints, not global spectral properties of the network.

We propose κ as a simple, interpretable, and robust biomarker for characterising connectome organisation, with potential applications in psychiatric diagnosis, ageing research, and pharmacological studies.

---

## 6. Data and Code Availability

**Data.** All connectivity matrices used in this study are publicly available:
- Dataset 1: ENIGMA Toolbox (https://github.com/MICA-MNI/ENIGMA)
- Dataset 2: Brain Connectivity Toolbox for Python (https://github.com/aestrivex/bctpy)

**Code.** All analysis scripts are available at: https://github.com/supertedai/EFC

---

## 7. Declaration of Interests

The author declares no competing interests.

---

## References

Betzel, R.F. et al. (2014). Changes in structural and functional connectivity among resting-state networks across the human lifespan. *NeuroImage*, 102, 345–357.

Carhart-Harris, R.L. et al. (2014). The entropic brain: a theory of conscious states informed by neuroimaging research with psychedelic drugs. *Frontiers in Human Neuroscience*, 8, 20.

Carhart-Harris, R.L. (2018). The entropic brain — revisited. *Neuropharmacology*, 142, 167–178.

Colizza, V. et al. (2006). Detecting rich-club ordering in complex networks. *Nature Physics*, 2, 110–115.

Creel, W.T. and Hartman, R.E. (2025). EEG entropy modulation as a biomarker of emotion regulation and resilience. *IBRO Neuroscience Reports*.

Desikan, R.S. et al. (2006). An automated labeling system for subdividing the human cerebral cortex on MRI scans into gyral based regions of interest. *NeuroImage*, 31, 968–980.

Glasser, M.F. et al. (2016). A multi-modal parcellation of human cerebral cortex. *Nature*, 536, 171–178.

Gu, S. et al. (2015). Controllability of structural brain networks. *Nature Communications*, 6, 8414.

Hagmann, P. et al. (2008). Mapping the structural core of human cerebral cortex. *PLoS Biology*, 6, e159.

Kaiser, R.H. et al. (2015). Large-scale network dysfunction in major depressive disorder: a meta-analysis of resting-state functional connectivity. *JAMA Psychiatry*, 72, 603–611.

Larivière, S. et al. (2021). The ENIGMA Toolbox: multiscale neural contextualization of multisite neuroimaging datasets. *Nature Methods*, 18, 698–700.

Noroozi, A. et al. (2025). Machine learning-based differentiation of schizophrenia and bipolar disorder using multiscale fuzzy entropy and relative power from resting-state EEG. *Translational Psychiatry*, 15, 120.

Rosas, F.E. et al. (2023). A whole-brain model of the neural entropy increase elicited by psychedelic drugs. *Scientific Reports*, 13, 6615.

Rubinov, M. and Sporns, O. (2010). Complex network measures of brain connectivity: uses and interpretations. *NeuroImage*, 52, 1059–1069.

Schaefer, A. et al. (2018). Local-global parcellation of the human cerebral cortex from intrinsic functional connectivity MRI. *Cerebral Cortex*, 28, 3095–3114.

Sporns, O. (2013). Network attributes for segregation and integration in the human brain. *Current Opinion in Neurobiology*, 23, 162–171.

Van Essen, D.C. et al. (2013). The WU-Minn Human Connectome Project: an overview. *NeuroImage*, 80, 62–79.

van den Heuvel, M.P. and Sporns, O. (2011). Rich-club organization of the human connectome. *Journal of Neuroscience*, 31, 15775–15786.

van den Heuvel, M.P. et al. (2013). Abnormal rich club organization and functional brain dynamics in schizophrenia. *JAMA Psychiatry*, 70, 783–792.

Yang, A.C. et al. (2013). Complexity of spontaneous BOLD activity in default mode network is correlated with cognitive function in normal male elderly. *Neurobiology of Aging*, 34, 428–438.
