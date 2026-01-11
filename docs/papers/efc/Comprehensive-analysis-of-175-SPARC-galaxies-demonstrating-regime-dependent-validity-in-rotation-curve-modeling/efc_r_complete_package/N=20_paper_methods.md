# Methods Pipeline: EFC-R SPARC Analysis

## Overview
This document describes the reproducible analysis pipeline used to generate all results in this dataset.

---

## 1. Data Acquisition

### Source
- **Database:** SPARC (Spitzer Photometry and Accurate Rotation Curves)
- **Reference:** Lelli, McGaugh & Schombert (2016), AJ 152, 157
- **Access:** VizieR catalog J/AJ/152/157

### Selection Criteria
- Rotation curve with ≥8 data points
- Morphological diversity (LSB, dwarf, spiral, barred)
- Published distance and inclination corrections
- Quality flag ≥ 2 in SPARC database

### Final Sample
- N = 20 galaxies
- Distance range: 3.2 - 82.4 Mpc
- Data points per galaxy: 8 - 73

---

## 2. Data Cleaning

### Steps Applied
1. Load rotation curve (radius, V_obs, V_err)
2. Remove points with V_err > 30% of V_obs
3. Remove points with radius < 0.5 kpc (resolution limit)
4. Convert to consistent units (kpc, km/s)

### No Interpolation
- All fits performed on original data points
- No smoothing or resampling applied

---

## 3. EFC Model Fitting

### Model Form
```
V_EFC²(r) = A_Ef × (1 - exp(-r/r_entropy)) × (1 - S(r))^α

where S(r) = S₀ + (S₁ - S₀) × (1 - exp(-∇S × r))
```

### Free Parameters
| Parameter | Range | Units |
|-----------|-------|-------|
| ∇S (entropy gradient) | [0.01, 0.15] | kpc⁻¹ |
| A_Ef (amplitude) | [30, 150] | (km/s)² |
| r_entropy (scale) | [1, 25] | kpc |
| α (power index) | [0.3, 3.0] | dimensionless |

### Fixed Parameters
- S₀ = 0.05 (minimum entropy)
- S₁ = 0.95 (maximum entropy)

### Optimization
- Method: scipy.optimize.minimize (L-BFGS-B)
- Objective: χ² = Σ[(V_obs - V_model)² / V_err²]
- Convergence: |Δχ²| < 10⁻⁶

---

## 4. ΛCDM Comparison Model

### Model Form
```
V_ΛCDM²(r) = V_NFW²(r) + V_disk²(r)

V_NFW²(r) = V_200² × [ln(1+x) - x/(1+x)] / [x × f(c)]
where x = r/r_s, f(c) = ln(1+c) - c/(1+c)
```

### Free Parameters
| Parameter | Range | Units |
|-----------|-------|-------|
| V_200 | [30, 300] | km/s |
| r_s | [1, 50] | kpc |

### Fixed Parameters
- Disk contribution from SPARC photometry (3.6μm M/L)
- Concentration c = 10 (typical for ΛCDM halos)

---

## 5. Model Comparison

### Akaike Information Criterion
```
AIC = χ² + 2k

where k = number of free parameters
- EFC: k = 4
- ΛCDM: k = 2
```

### Decision Rule
```
ΔAIC = AIC_EFC - AIC_ΛCDM

ΔAIC < -2  → EFC preferred
-2 ≤ ΔAIC ≤ +2 → Models comparable
ΔAIC > +2  → ΛCDM preferred
```

---

## 6. Latent Field Proxy Construction

### Components
```
L = 0.4 × L_morphology + 0.3 × L_kinematic + 0.3 × L_residual
```

### Morphological Component (L_morphology)
- Bar strength: 0 (none) to 1 (strong bar)
- Spiral arm prominence: 0 (diffuse) to 1 (grand design)
- Source: Visual classification + literature

### Kinematic Component (L_kinematic)
- Asymmetry index from rotation curve
- Computed as: max(|V_approach - V_recede|) / V_flat

### Residual Component (L_residual)
- Systematic residual structure from EFC fit
- Computed as: (χ²_EFC - χ²_min) / χ²_min

### Normalization
- All components scaled to [0, 1]
- Final L ∈ [0, 1]

---

## 7. Statistical Tests

### Correlation Analysis
```python
from scipy.stats import spearmanr, pearsonr

rho, p_spearman = spearmanr(L_proxy, delta_AIC)
r, p_pearson = pearsonr(L_proxy, delta_AIC)
```

### Regime Comparison
```python
from scipy.stats import ttest_ind, mannwhitneyu

# Split by L threshold
low_L = delta_AIC[L_proxy < 0.4]
high_L = delta_AIC[L_proxy >= 0.5]

t_stat, p_ttest = ttest_ind(low_L, high_L)
u_stat, p_mann = mannwhitneyu(low_L, high_L)
```

### Bootstrap Analysis
```python
import numpy as np

n_bootstrap = 10000
grad_S_bootstrap = []

for i in range(n_bootstrap):
    # Resample galaxies with replacement
    idx = np.random.choice(20, 20, replace=True)
    # Refit and store gradient
    grad_S_bootstrap.append(fit_efc(data[idx]).grad_S)

mean_gradS = np.mean(grad_S_bootstrap)
std_gradS = np.std(grad_S_bootstrap)
```

---

## 8. Output Files Generated

| File | Description | Script |
|------|-------------|--------|
| sparc_20_summary.json | All fit results | main_analysis.py |
| Supplementary_Table_S1.md | Formatted table | generate_tables.py |
| figures/*.png | All visualizations | generate_figures.py |

---

## 9. Software Environment

### Python Version
- Python 3.10+

### Required Packages
```
numpy >= 1.21
scipy >= 1.7
matplotlib >= 3.5
pandas >= 1.3
```

### Installation
```bash
pip install numpy scipy matplotlib pandas
```

---

## 10. Reproducing Results

### Quick Start
```bash
# 1. Download SPARC data
python scripts/download_sparc.py

# 2. Run analysis
python scripts/main_analysis.py

# 3. Generate figures
python scripts/generate_figures.py

# 4. Generate tables
python scripts/generate_tables.py
```

### Expected Runtime
- Full analysis: ~5 minutes on standard laptop
- Per galaxy: ~15 seconds

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-06 | Initial release |

---

*This pipeline is designed for transparency and reproducibility. All random seeds are fixed for deterministic results.*
