# Triangulation Test for Thermodynamic-Lensing Coupling

**AI-friendly package for**: "A Triangulation Test for Possible Thermodynamic Contributions to Gravitational Lensing in Galaxy Clusters"

**Author**: Morten Magnusson
**Date**: February 2026
**DOI**: [10.6084/m9.figshare.31267297](https://doi.org/10.6084/m9.figshare.31267297)

## Overview

This paper introduces a **triangulation methodology** to test whether gravitational lensing in galaxy clusters exhibits residual structure correlated with ICM thermodynamics beyond what is expected from mass alone.

## The Three Independent Observables

### Observable 1: Lensing Mass (Geometric)
```
M_lens(<r) = π r² Σ_crit κ̄(<r)
```
- From weak lensing shear and strong lensing multiple images
- Measures total projected mass through photon deflection

### Observable 2: Hydrostatic Mass (Dynamic)
```
M_HSE(<r) = -(kT r)/(μ m_p G) × [d ln n_e/d ln r + d ln T/d ln r]
```
- From X-ray temperature T(r) and density n_e(r) profiles
- Assumes spherical hydrostatic equilibrium

### Observable 3: Entropy Gradient (Thermodynamic)
```
K(r) = T(r) n_e(r)^(-2/3)    [ICM entropy]
|∇K(r)| ≈ |dK/dr|            [entropy gradient]
```
- Marks sites of irreversible thermodynamic processes (shocks, mixing)

## The Triangulation Test

**Mass Residual**:
```
R(r) = M_lens(r) - M_HSE(r)
```

**Core Test**: Correlation between R(r) and |∇K(r)|

| Hypothesis | Expected ρ | Interpretation |
|------------|------------|----------------|
| ΛCDM (null) | ρ ≈ 0 | R from non-thermal pressure, no systematic correlation |
| Thermodynamic coupling | ρ > 0 | If κ ∝ ∇²K, then R ∝ \|∇K\| |

## Pilot Results

| Cluster | Type | Pearson ρ | Spearman ρ | p-value | Result |
|---------|------|-----------|------------|---------|--------|
| Bullet Cluster | Merging | -0.129 | -0.179 | 0.21 | Not significant |
| Abell 1835 | Relaxed | -0.052 | -0.147 | 0.70 | Not significant |

**Interpretation**: No statistically significant correlation detected, consistent with sensitivity limits for %-level effects.

## Consistency Requirements

Any phenomenological coupling κ ~ κ_GR + α∇²K must satisfy:

| Test | Observable | Data | Status |
|------|------------|------|--------|
| Achromaticity | κ(λ) | H0LiCOW | ✓ Consistent |
| CMB spectrum | Δy, Δμ | FIRAS | △ Assumed |
| WEP | ε | LLR+MICROSCOPE | △ Assumed |
| BBN | N_eff | Planck+D/H | △ Assumed |
| Time delays | τ(λ) | TDCOSMO | ✓ Consistent |
| Void lensing | κ_void | DES Y3 | △ Intriguing |

## Detection Thresholds

For N = 57 radial bins (single cluster):
- Need ρ ≈ 0.25 for p < 0.05 significance
- Expected signal ρ ~ 0.1-0.2 is under-powered

**Scaling to larger samples**:
| Clusters | N_eff | Detectable ρ at 3σ |
|----------|-------|-------------------|
| 10 | 570 | ~0.08 |
| 20 | 1140 | ~0.06 |
| 50 | 2850 | ~0.04 |

## Speculative Prediction: Line-of-Sight Redshift

If thermodynamic coupling exists, absorption systems passing through cluster ICM could show:
```
Δz_LOS ~ 10⁻⁶ to 10⁻⁵
```
- Independent of photon frequency
- Correlated spatially with entropy structure
- Detectable by stacking cluster-quasar sightlines

## Quick Start

```python
from triangulation_test import TriangulationAnalysis

# Initialize with cluster data
analysis = TriangulationAnalysis(
    r_bins,      # Radial bins [kpc]
    M_lens,      # Lensing mass profile [M_sun]
    M_HSE,       # Hydrostatic mass profile [M_sun]
    K_profile    # Entropy profile [keV cm²]
)

# Compute mass residual and entropy gradient
R_norm = analysis.compute_residual()
grad_K = analysis.compute_entropy_gradient()

# Run correlation test
results = analysis.correlation_test()
print(f"Pearson ρ = {results['pearson_rho']:.3f}")
print(f"p-value = {results['p_value']:.3f}")
```

## Key Equations Summary

| Quantity | Formula |
|----------|---------|
| Lensing mass | M_lens = πr²Σ_crit κ̄ |
| HSE mass | M_HSE = -(kTr)/(μm_pG)[d ln n_e/d ln r + d ln T/d ln r] |
| Entropy | K = T n_e^(-2/3) |
| Mass residual | R(r) = M_lens(r) - M_HSE(r) |
| Normalized residual | R_norm = R/M_lens |
| Test statistic | t = ρ√[(N-2)/(1-ρ²)] |

## What This Work Does NOT Claim

- Does NOT present evidence for modified gravity
- Does NOT claim detection of thermodynamic-lensing coupling
- Pilot results are consistent with null hypothesis (ΛCDM)
- Establishes methodology for future high-precision tests

## Citation

```bibtex
@article{magnusson2026triangulation,
  title={A Triangulation Test for Possible Thermodynamic Contributions
         to Gravitational Lensing in Galaxy Clusters},
  author={Magnusson, Morten},
  journal={MNRAS},
  volume={000},
  pages={1--7},
  year={2026},
  doi={10.6084/m9.figshare.31267297}
}
```

## License

CC-BY-4.0
