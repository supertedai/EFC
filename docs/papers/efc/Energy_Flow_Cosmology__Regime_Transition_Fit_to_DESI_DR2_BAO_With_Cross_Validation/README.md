# EFC Regime-Transition Fit to DESI DR2 BAO

## AI-Friendly Package

**Version**: 1.0
**Author**: Morten Magnusson (ORCID: 0009-0002-4860-5095)
**Date**: February 2026
**License**: CC-BY-4.0

## Overview

This paper validates an EFC regime-transition parameterization against **DESI DR2 BAO** data with cross-validation against Pantheon+ supernovae and cosmic chronometers.

**Key Result**: The transition model (z_L1L2 = 1.01, α_L2 = 0.045) yields **Δχ² = -22.01** for two additional parameters, surviving rigorous conditional hold-out validation.

## The EFC Parameterization

### Modified Friedmann Equation
```
E²(z) → E²(z) × [1 + α_L2 × f(z) × Θ(z)]
```

where:
- E(z) = H(z)/H₀ (normalized Hubble parameter)
- f(z) = (1+z)⁻¹ (phenomenological coupling)
- Θ(z) = ½[1 + tanh((z_L1L2 - z)/Δz)] (smooth transition, Δz = 0.3)

### Free Parameters
| Parameter | Description | Best-fit |
|-----------|-------------|----------|
| z_L1L2 | Transition redshift | **1.01** |
| α_L2 | Energy flow coupling | **0.045** |

For α_L2 = 0, the model reduces **exactly** to ΛCDM.

## Key Results

### BAO Fit (Primary)
| Model | χ² | dof | χ²/dof |
|-------|-----|-----|--------|
| ΛCDM | 31.34 | 13 | 2.41 |
| **EFC** | **9.33** | **11** | **0.85** |

**Δχ² = -22.01** for Δk = 2 parameters

### Information Criteria
| Criterion | Value |
|-----------|-------|
| ΔAIC | **-18.01** |
| ΔBIC | **-16.88** |

### Conditional Hold-Out Validation
| Model | χ²_h|t |
|-------|--------|
| ΛCDM | 22.16 |
| EFC | 3.52 |

**Δχ²_h|t = -18.65** (survives overfitting test)

### Cross-Validation Results

| Probe | N | Δχ² | Status |
|-------|---|-----|--------|
| BAO (primary) | 13 | -22.01 | ✓ Pass |
| Hold-out (cond.) | 3 | -18.65 | ✓ Pass |
| SN shape test | 277 | — | ✓ Pass |
| CC consistency | 34 | -0.17 | ✓ Pass |
| **Combined** | **47** | **-22.17** | ✓ Pass |

## Data Sources

### DESI DR2 BAO
- 13 measurements spanning z = 0.295 to z = 2.330
- Observables: D_V/r_s, D_M/r_s, D_H/r_s
- Full 13×13 covariance matrix

### Pantheon+ Supernovae
- 277 Type Ia SNe in Hubble flow (0.01 < z < 2.3)
- Full statistical + systematic covariance
- **Result**: Statistically indistinguishable from ΛCDM (Δχ² = +0.06)
- **Shape test**: max|Δμ_shape| = 0.0018 mag (pure offset absorbed by M)

### Cosmic Chronometers
- 34 H(z) measurements (z = 0.07 to z = 1.97)
- Mean fractional uncertainty ~22%
- **Result**: Consistent with BAO best-fit (Δχ² = -0.17)

## Fixed Cosmological Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| H₀ | 67.4 km/s/Mpc | Planck 2018 |
| Ω_m | 0.3134 | Planck 2018 |
| r_d | 147.114 Mpc | Planck 2018 |

## Package Contents

```
├── README.md                 # This file
├── CITATION.cff             # Citation metadata
├── LICENSE                  # CC-BY-4.0
├── index.json               # Machine-readable metadata
│
├── src/
│   ├── __init__.py
│   ├── efc_model.py          # E²(z) modification
│   ├── likelihood.py         # BAO, SN, CC likelihoods
│   └── validation.py         # Hold-out tests
│
├── data/
│   ├── desi_dr2_bao.json     # BAO data points
│   ├── fit_results.json      # All fit results
│   └── validation_summary.json
│
└── examples/
    └── fit_analysis.py       # Demonstration
```

## Quick Usage

```python
from src.efc_model import EFCTransition

# Create model with best-fit parameters
model = EFCTransition(z_L1L2=1.01, alpha_L2=0.045)

# Compute E²(z) modification
z = 0.5
E2_ratio = model.E2_ratio(z)
print(f"E²(z={z}) modification: {E2_ratio:.4f}")
```

## Physical Interpretation

The best-fit transition redshift z_L1L2 ≈ 1 lies in the early late-time epoch where distance and H(z) measurements become sensitive to small deviations from standard expansion.

**Note**: Matter-Λ equality occurs at z ≈ 0.3 in ΛCDM. The detected transition at z ≈ 1 is **distinct** from this epoch.

## What This Analysis Establishes

1. **Large BAO improvement**: Δχ² = -22 for 2 parameters
2. **Robust against overfitting**: Conditional hold-out confirms genuine improvement
3. **SN compatibility explained**: Shape test shows EFC predicts pure distance offset
4. **No CC tension**: CC data support BAO best-fit with consistent α_L2

## Limitations

- Improvement comes almost entirely from BAO
- CC analysis uses diagonal errors (not full covariance)
- Robustness across other BAO compilations should be tested

## Related EFC Papers

- [Core Lock](../Core-Lock/) - Mathematical foundation
- [H₀-RAR Unification](../Unified_Origin_of_the_Radial_Acceleration_Relation_and_the_Hubble_Tension_via_Entropic_Gravity_Modification/) - Regime interpretation
- [SPARC Validation](../EFC_Phase_3__SPARC_Validation/) - Galactic scale test

## Citation

```bibtex
@article{magnusson2026desi,
  author = {Magnusson, Morten},
  title = {Energy-Flow Cosmology: Regime-Transition Fit to DESI DR2 BAO
           With Cross-Validation Against Pantheon+ and H(z) Chronometers},
  year = {2026},
  note = {ΔBIC = -14.5 favoring transition model}
}
```
