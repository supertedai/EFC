# Phenomenological Constraints on Entropy-Flow Modifications to Expansion and Growth from BOSS DR12

**Author:** Morten Magnusson
**Date:** February 2026
**DOI:** [10.6084/m9.figshare.31243828](https://doi.org/10.6084/m9.figshare.31243828)

## Overview

This paper presents a single-parameter phenomenological extension of ΛCDM motivated by Energy-Flow Cosmology (EFC), constraining entropy-flow modifications to both background expansion and linear growth using BOSS DR12 consensus data with the full 9×9 covariance matrix.

## Key Innovation

**Single parameter governs both expansion and growth with opposite signs:**
- Positive α_L2 → increases comoving distance D_M (objects appear farther)
- Positive α_L2 → suppresses growth rate fσ8 (less structure)

This anti-correlation is a distinctive EFC signature not found in generic w₀wₐ parametrizations.

## Model Equations

### Background Expansion
```
D_M^EFC(z) = D_M^ΛCDM(z) × [1 + α_L2 × g_D(z)]
H^EFC(z) = H^ΛCDM(z) × [1 + α_L2 × g_H(z)]
```

### Coupling Functions
```
g_D(z) = (1 - Ωm(z))/(1+z) × ln(1+z)

g_H(z) = -(1 - Ωm(z))/(1+z) × [1 - ln(1+z)] × [1 + 3Ωm(z) - 3Ωm(1+z)³/E²(z)]

g_growth(z) = -[1 - Ωm(z)]^(3/2) × ln(1+z) / (1+z)^(1/2)
```

where Ωm(z) = Ωm(1+z)³/E²(z)

### Growth Rate
```
fσ8^EFC(z) = fσ8^ΛCDM(z) × [1 + α_L2 × g_growth(z)]
```

**Critical feature:** g_growth(z) < 0 for all z > 0, while g_D(z) > 0.

## Key Results

### Best-Fit Parameters

| Parameter | ΛCDM | EFC |
|-----------|------|-----|
| H₀ [km/s/Mpc] | 66.57 | 69.65 |
| Ωm | 0.359 | 0.347 |
| σ8 | 0.667 | 0.669 |
| α_L2 | 0 (fixed) | +0.353 |
| χ² | 7.29 | 4.28 |
| dof | 6 | 5 |

### Constraint on α_L2
```
α_L2 = 0.34 +0.16/-0.16 (1σ)
     = [-0.02, +0.71] (2σ)
```

- Δχ² = 3.01 → 1.7σ preference for EFC
- ΛCDM (α_L2 = 0) excluded at 1σ, included at 2σ

### BAO-RSD Sign Conflict

| Dataset | Preferred α_L2 |
|---------|----------------|
| BAO-only | +0.28 ± 0.18 |
| RSD-only | ≈ -1.4 (large uncertainty) |
| Joint | +0.34 ± 0.16 |

This sign conflict reflects the S8 tension recast in EFC parameter space.

## Falsifiable Predictions

### 1. Gravitational Slip
```
η ≡ Φ/Ψ = 1 (no gravitational slip)
```

This distinguishes EFC from scalar-tensor and f(R) theories which predict η ≠ 1.

**Testable with:** Euclid (±0.03 at 1σ), Euclid+Rubin (±0.01)

### 2. Convergence Test
BAO-inferred and growth-inferred α_L2 should converge to a single consistent value as precision improves.

### 3. H₀ Prediction
EFC shifts H₀ from 66.6 → 69.7 km/s/Mpc. If true value > 72 km/s/Mpc, EFC alone is insufficient.

## Physical Interpretation

The anti-correlation between expansion and growth is motivated by EFC:
- Entropy gradients that accelerate expansion simultaneously suppress gravitational clustering
- Provides "entropy pressure" that counteracts collapse
- Naturally accommodates S8 tension if α_L2 > 0

## Data

- **Dataset:** BOSS DR12 consensus (Alam et al. 2017)
- **Observables:** D_M(z), H(z), fσ8(z) at z_eff = 0.38, 0.51, 0.61
- **Covariance:** Full 9×9 matrix including all cross-correlations
- **Fiducial r_s:** 147.78 Mpc

## Package Contents

```
├── README.md                 # This file
├── CITATION.cff              # Citation metadata
├── LICENSE                   # CC-BY-4.0
├── index.json                # Machine-readable metadata
├── src/
│   ├── __init__.py
│   └── efc_phenomenology.py  # Model implementation
├── data/
│   ├── boss_dr12_consensus.json  # BOSS DR12 measurements
│   └── fit_results.json      # Best-fit parameters
└── examples/
    └── phenomenology_fit.py  # Usage demonstration
```

## Quick Start

```python
from src.efc_phenomenology import EFCPhenomenology

# Initialize model
model = EFCPhenomenology(
    H0=69.65,      # km/s/Mpc
    Omega_m=0.347,
    sigma8=0.669,
    alpha_L2=0.353
)

# Compute observables at z = 0.51
z = 0.51
DM = model.DM_EFC(z)      # Comoving distance
H = model.H_EFC(z)        # Hubble parameter
fsigma8 = model.fsigma8_EFC(z)  # Growth rate

# Get coupling functions
g_D = model.g_D(z)        # > 0
g_growth = model.g_growth(z)  # < 0 (opposite sign!)
```

## Citation

```bibtex
@misc{magnusson2026phenomenological,
  author = {Magnusson, Morten},
  title = {Phenomenological constraints on entropy-flow modifications
           to expansion and growth from {BOSS DR12}},
  year = {2026},
  doi = {10.6084/m9.figshare.31243828}
}
```

## References

1. Alam, S., et al. (BOSS), MNRAS 470, 2617 (2017)
2. Magnusson, M. "EFC Foundational Framework," doi:10.6084/m9.figshare.30563738
3. Planck Collaboration, A&A 641, A6 (2020)
