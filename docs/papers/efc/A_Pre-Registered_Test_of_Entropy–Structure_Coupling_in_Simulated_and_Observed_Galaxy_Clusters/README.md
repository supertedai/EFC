# A Pre-Registered Test of Entropy–Structure Coupling in Simulated and Observed Galaxy Clusters

**Author:** Morten Magnusson
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)
**Date:** February 2026
**DOI:** [10.6084/m9.figshare.31286368](https://doi.org/10.6084/m9.figshare.31286368)

## Abstract

This paper tests whether the observed positive correlation between entropy profile steepness and cool-core state reported in the ACCEPT X-ray cluster sample (ρ(α, y_CCT) ~ +0.36; Cavagnolo et al. 2009) is reproduced in the TNG-Cluster cosmological magnetohydrodynamical simulation (352 halos, 10¹⁴ < M₅₀₀c/M☉ < 2×10¹⁵ at z = 0). Using pre-registered statistical tests, we find a **strong negative correlation** ρ(n_e-slope, K₀) = -0.872 (p ~ 10⁻¹¹¹), robust against mass confounding and consistent across all four mass bins.

## Key Findings

### Sign Flip in Entropy-Structure Coupling

| Dataset | Correlation | Value | p-value |
|---------|-------------|-------|---------|
| **TNG-Cluster** | ρ(n_e-slope, K₀) | **-0.872** | ~8×10⁻¹¹¹ |
| **TNG-Cluster** | ρ(n_e-slope, t_cool) | **-0.878** | ~7×10⁻¹¹⁴ |
| **ACCEPT (observed)** | ρ(α, y_CCT) | **+0.36** | — |

The sign is **completely reversed** between simulation and observation.

### Robustness Tests

- **Mass-controlled**: ρ_partial(n_e-slope, K₀ | M) = -0.880 (p = 2×10⁻¹¹⁵)
- **Mass explains**: 0% of the correlation
- **All mass bins**: Negative correlations in all four bins

## Physical Model

### Entropy Profile (Cavagnolo et al. 2009)

```
K(r) = K₀ + K₁₀₀ × (r / 100 kpc)^α
```

Where:
- **K₀**: Central entropy (keV cm²)
- **K₁₀₀**: Entropy normalisation at 100 kpc
- **α**: Power-law index (entropy gradient steepness)

### Proxy Definition

The entropy slope decomposes as:

```
α = d ln K / d ln r = d ln T / d ln r + (2/3) × (-d ln n_e / d ln r)
```

We define the density-based proxy:

```
α_proxy = (2/3) × n_e-slope
```

This is a **lower bound** on α under the physical expectation that temperature rises with radius in cluster cores.

### Cool-Core Classification (Hudson et al. 2010)

| Class | K₀ threshold | TNG-Cluster count |
|-------|-------------|-------------------|
| SCC (Strong Cool-Core) | K₀ ≤ 22 keV cm² | 28 (8%) |
| WCC (Weak Cool-Core) | 22 < K₀ ≤ 150 | 206 (59%) |
| NCC (Non-Cool-Core) | K₀ > 150 | 118 (34%) |

## Mass-Binned Results

| Mass bin (log M) | N | ρ | p-value |
|------------------|---|---|---------|
| [14.0, 14.3) | 41 | -0.790 | 9×10⁻¹⁰ |
| [14.3, 14.6) | 118 | -0.860 | 1×10⁻³⁵ |
| [14.6, 14.9) | 121 | -0.901 | 5×10⁻⁴⁵ |
| [14.9, 15.5) | 71 | -0.897 | 4×10⁻²⁶ |
| **All (partial\|M)** | 352 | **-0.880** | 2×10⁻¹¹⁵ |

## Pre-Registered Test Design

### Two-Stage Approach

1. **Path B (Pre-test)**: Proxy-based analysis using α_proxy = (2/3) × n_e-slope
   - Computationally efficient
   - Tests sign of correlation
   - Results: Sign flip confirmed

2. **Path A (Decisive)**: Full Cavagnolo-model K(r) fit over [20, 400] kpc
   - Definition-matched comparison
   - Eliminates systematic ambiguities
   - Pre-registered, awaiting execution

### Stop/Go Criterion

- **STOP**: ρ(α_fit, K₀) > 0 → Sign flip reverses under definition matching
- **GO**: ρ(α_fit, K₀) < 0 → Sign flip survives (genuine mismatch)
- **PARTIAL**: Mixed signs require further investigation

## Interpretation Framework

If the sign flip is confirmed by Path A, three explanations must be considered:

1. **Subgrid modelling**: AGN feedback in TNG may produce overly mechanical CC/NCC transitions
2. **Observational systematics**: Projection effects or selection effects in ACCEPT
3. **Missing physics**: Cosmic ray transport, anisotropic conduction, magnetic draping

## Data Sources

- **TNG-Cluster**: 352 zoom simulations at TNG300-1 resolution (Nelson et al. 2024)
- **Lehle et al. (2024)**: Supplementary catalogue with K₀, n_e-slope, t_cool, C_phys
- **ACCEPT**: 239 Chandra clusters with deprojected entropy profiles (Cavagnolo et al. 2009)

## Package Contents

```
├── README.md                    # This file
├── index.json                   # Machine-readable metadata
├── src/
│   └── entropy_structure_coupling.py  # Reference implementation
├── data/
│   └── tng_cluster_results.json      # Correlation data and statistics
├── examples/
│   └── entropy_structure_demo.py     # Demonstration script
├── CITATION.cff                 # Citation metadata
└── LICENSE                      # MIT License
```

## Quick Start

```python
from src.entropy_structure_coupling import (
    EntropyProfileModel, CorrelationAnalysis, CoolCoreClassifier
)

# Initialize entropy profile model
model = EntropyProfileModel(K0=20.0, K100=150.0, alpha=1.1)

# Compute entropy at radius
K = model.entropy(r=100)  # keV cm²

# Correlation analysis
analysis = CorrelationAnalysis()
tng_result = analysis.tng_correlation()
# Returns: rho=-0.872, p=8e-111

# Cool-core classification
classifier = CoolCoreClassifier()
cc_class = classifier.classify(K0=15.0)  # Returns: "SCC"
```

## Key Equations

### Entropy Definition
```
K = k_B T × n_e^(-2/3)
```

### Spearman Correlation with Mass Control
```
ρ_partial(X, Y | M) = ρ(X_residual, Y_residual)
```
where residuals are computed via rank-based residualisation on log M₅₀₀c.

## References

- Cavagnolo, K. W., et al. 2009, ApJS, 182, 12 (ACCEPT)
- Hudson, D. S., et al. 2010, A&A, 513, A37 (CC classification)
- Lehle, K., et al. 2024, A&A, 687, A30 (TNG-Cluster CC properties)
- Nelson, D., et al. 2024, A&A, 686, A157 (TNG-Cluster simulation)

## License

MIT License - See LICENSE file for details.
