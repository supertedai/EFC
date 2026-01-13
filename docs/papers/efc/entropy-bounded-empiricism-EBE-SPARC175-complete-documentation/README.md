# EBE Project Dataset Collection - README
## Entropy-Bounded Empiricism (EBE) SPARC175 Analysis

**Version:** 1.0  
**Date:** January 12, 2026  
**DOI:** 10.6084/m9.figshare.31047703  
**License:** CC-BY-4.0  
**Author:** Morten Magnusson  
**ORCID:** 0009-0002-4860-5095  
**Project:** Energy-Flow Cosmology (EFC)  

---

## ðŸ“ Dataset Overview

This collection contains all primary datasets, validation metrics, and statistical analyses for the Entropy-Bounded Empiricism (EBE) project, specifically the SPARC175 galaxy rotation curve analysis.

### Purpose
To provide complete, reproducible evidence for regime-dependent model validity in galaxy rotation curves, demonstrating that empirical science is bounded by entropy constraints (0.1 < S < 0.9).

### Framework Note
This work establishes Entropy-Bounded Empiricism (EBE) as an epistemological constraint on model validity. Energy-Flow Cosmology (EFC) is used here as a concrete test case, not as a prerequisite for the framework. The EBE framework stands independently of any specific physical theory.

---

## ðŸ“Š Files Included

### 1. **sparc175_master_dataset.csv**
**Description:** Complete dataset of 175 SPARC galaxies with regime classification and key variables.

**Columns:**
- `galaxy_id`: Unique identifier (1-175)
- `galaxy_name`: Standard astronomical name
- `regime`: Classification (FLOW, TRANSITION, LATENT)
- `L_value`: Model-blind structural proxy (0.0-1.0)
- `S_estimate`: Entropy estimate derived from L
- `N_points`: Number of data points in rotation curve (quality proxy)
- `quality_tier`: Subjective quality assessment (low/medium/high)
- `chi2_efc`: Chi-squared for Energy-Flow Cosmology model
- `chi2_lcdm`: Chi-squared for Î›CDM model
- `success_efc`: Binary success indicator (chi2 < 3)
- `success_lcdm`: Binary success indicator (chi2 < 3)
- `mass_proxy`: Log stellar mass estimate
- `distance_mpc`: Distance in megaparsecs
- `inclination_deg`: Disk inclination angle
- `notes`: Additional comments

**Sample Size:** 175 galaxies

**Regime Distribution:**
- FLOW: 62 galaxies (35.4%)
- TRANSITION: 86 galaxies (49.1%)
- LATENT: 27 galaxies (15.4%)

**Key Finding:** 100% success rate for EFC in FLOW regime (62/62 galaxies)

### 2. **regime_thresholds_validation.txt**
**Description:** Regime boundaries, statistical test results, and validation metrics.

**Contents:**
- Regime boundary definitions (L1=0.337, L2=0.427)
- Entropy boundaries (S âˆˆ [0.1, 0.9])
- Regime statistics (means, standard deviations, success rates)
- Primary validation tests (Mann-Whitney, Kruskal-Wallis, Permutation)
- CMB null test results (CRITICAL - must fail to support EBE)
- Confound analysis (quality-L correlation: Ï=-0.43)
- Sensitivity analyses (14 robustness checks)
- Replication status (N=20 pilot â†’ N=175 full)
- Cross-domain predictions (economics, biology, cognition)
- Publication metrics and data availability

**Format:** Structured text with key-value pairs

### 3. **statistical_analysis_summary.py**
**Description:** Complete statistical analysis including all tests, effect sizes, and interpretations.

**Contents:**
- Test 1: Mann-Whitney U (FLOW vs others) â†’ p<0.0001
- Test 2: Kruskal-Wallis H (3-way) â†’ p=0.012
- Test 3: Permutation test (10k iterations) â†’ p=0.016
- Test 4: CMB null test â†’ p=0.251 (PASS - as expected)
- Test 5: Quality confound analysis â†’ effect strengthens in high-quality data
- Test 6: 14 sensitivity analyses â†’ all show consistent direction
- Test 7: Temporal validation â†’ N=20 pilot replicates at N=175
- Effect size interpretation (Cliff's Î´=0.371, medium-large)
- Statistical power analysis (achieved power >0.99)
- Assumptions, limitations, and conclusions

**Format:** Python-style docstring with structured analysis

---

## ðŸ”¬ Methodology Summary

### What is L?
L is a **model-blind structural proxy** computed from the rotation curve shape BEFORE any model fitting. It quantifies the "structural entropy" or complexity of the velocity profile:
- L â‰ˆ 0: Ordered, coherent structure (low entropy)
- L â‰ˆ 0.5: Mixed structure (moderate entropy)
- L â‰ˆ 1: Disordered, fragmented structure (high entropy)

### What is S?
S is the **entropy estimate** derived from L using a calibrated relation from thermodynamic principles. It represents the degree of energy-flow fragmentation:
- S â†’ 0: Coherent flow (GR-like limit)
- S â‰ˆ 0.5: Optimal measurement regime
- S â†’ 1: Fragmented flow (QFT-like limit)

### Regime Classification
Three regimes identified empirically from SPARC data:

1. **FLOW (L < 0.337, S < 0.25)**
   - Coherent energy flow
   - EFC model succeeds 100%
   - Examples: DDO154, NGC2366, IC2574

2. **TRANSITION (0.337 â‰¤ L < 0.427, 0.25 â‰¤ S < 0.65)**
   - Mixed regime
   - Both models struggle
   - Examples: NGC5457 (M101), NGC5194 (M51)

3. **LATENT (L â‰¥ 0.427, S â‰¥ 0.65)**
   - High entropy, fragmented flow
   - Both models fail
   - Examples: NGC4594 (Sombrero), NGC4486 (M87), ellipticals

---

## âœ… Key Validation Metrics

### Primary Result
**100% success rate** for Energy-Flow Cosmology in FLOW regime (62/62 galaxies with Ï‡Â² < 3)

### Statistical Significance
- Mann-Whitney U test: **p < 0.0001** (highly significant)
- Kruskal-Wallis H test: **p = 0.012** (significant 3-way difference)
- Permutation test: **p = 0.016** (non-random structure)
- Effect size: **Cliff's Î´ = 0.371** (medium-to-large)

### Critical Validation
**CMB Null Test: p = 0.251** (PASS)
- CMB shows NO regime structure (as theoretically predicted)
- EBE framework predicts CMB should fail regime test (equilibrium Sâ‰ˆ0.5)
- This distinguishes genuine regime effect from methodological artifact

### Quality Confound
- **Correlation:** Ï(N_points, L) = -0.43 (moderate)
- **BUT:** Effect STRENGTHENS in high-quality subsample (Î´=0.69, p=0.001)
- **Interpretation:** Quality is a moderator, not pure confound
- **Pattern argues AGAINST artifact** (artifacts weaken with better data)

### Robustness
- **14 sensitivity analyses:** All show consistent directional effect
- **6 reach p<0.05:** Effect is not arbitrary-choice dependent
- **Replicates N=20â†’N=175:** Findings scale, not a statistical fluke

---

## ðŸ“ˆ Usage Examples

### Python (pandas)
```python
import pandas as pd

# Load master dataset
df = pd.read_csv('sparc175_master_dataset.csv')

# Analyze FLOW regime
flow = df[df['regime'] == 'FLOW']
print(f"FLOW success rate: {flow['success_efc'].mean()*100:.1f}%")

# Compare regimes
regime_stats = df.groupby('regime').agg({
    'chi2_efc': 'mean',
    'success_efc': 'mean',
    'L_value': 'mean',
    'S_estimate': 'mean'
})
print(regime_stats)
```

### R (tidyverse)
```r
library(tidyverse)

# Load and explore
df <- read_csv('sparc175_master_dataset.csv')

# Regime comparison
df %>%
  group_by(regime) %>%
  summarise(
    n = n(),
    mean_L = mean(L_value),
    mean_S = mean(S_estimate),
    success_rate = mean(success_efc) * 100
  )

# Quality stratification
df %>%
  mutate(quality_bin = cut(N_points, breaks=c(0,40,50,Inf))) %>%
  group_by(quality_bin, regime) %>%
  summarise(success_rate = mean(success_efc))
```

---

## ðŸ” Known Limitations

1. **Single Dataset**: Only SPARC survey analyzed (N=175)
   - **Mitigation needed:** Replicate with LITTLE THINGS, DMS surveys
   
2. **Quality Confound**: Moderate correlation Ï=-0.43 exists
   - **Counter-evidence:** Effect strengthens in high-quality data
   - **Pattern:** Inconsistent with pure artifact explanation
   
3. **L Definition Flexibility**: Multiple ways to calculate L
   - **Mitigation:** 14 sensitivity tests with alternative definitions
   - **Result:** All variants show consistent directional effect
   
4. **No Peer Review Yet**: Manuscript ready but not submitted
   - **Next step:** MNRAS submission Q1 2026
   
5. **Cross-Domain Untested**: Economics, biology, cognition predictions
   - **Status:** Conceptual stage, operationalization needed

---

## ðŸ“ Citation

If you use these datasets, please cite:

```bibtex
@misc{magnusson2026ebe,
  author = {Magnusson, Morten},
  title = {Entropy-Bounded Empiricism: Regime-Dependent Validity in Galaxy Rotation Curves},
  year = {2026},
  publisher = {Figshare},
  doi = {10.6084/m9.figshare.31047703},
  url = {https://doi.org/10.6084/m9.figshare.31047703}
}
```

---

## ðŸ”— Related Resources

- **GitHub Repository:** https://github.com/supertedai/EFC
- **EFC Website:** https://energyflow-cosmology.com
- **SPARC Database:** http://astroweb.cwru.edu/SPARC/
- **Planck CMB Data:** https://pla.esac.esa.int/

---

## ðŸ“§ Contact

**Morten Magnusson**  
Email: morten@magnusson.as  
ORCID: 0009-0002-4860-5095  
GitHub: @supertedai  

---

## ðŸ”„ Version History

- **v1.0 (2026-01-12):** Initial release
  - SPARC175 master dataset
  - Complete statistical analysis
  - Regime thresholds and validation metrics
  - Documentation and metadata

---

## ðŸ“œ License

This work is licensed under Creative Commons Attribution 4.0 International (CC-BY-4.0).

You are free to:
- Share â€” copy and redistribute the material
- Adapt â€” remix, transform, and build upon the material

Under the following terms:
- Attribution â€” You must give appropriate credit, provide a link to the license, and indicate if changes were made.

---

## ðŸ™ Acknowledgments

- SPARC collaboration for galaxy rotation curve data
- Planck collaboration for CMB data
- Energy-Flow Cosmology research community
- Magnusson`s Advanced AI Symbiosis for analytical assistance

---

**Last Updated:** January 12, 2026
