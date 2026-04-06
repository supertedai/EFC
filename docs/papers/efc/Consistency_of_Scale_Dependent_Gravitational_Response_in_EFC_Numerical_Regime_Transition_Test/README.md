# Consistency of Scale-Dependent Gravitational Response in EFC: Numerical Regime Transition Test

**DOI:** [10.6084/m9.figshare.31941543](https://doi.org/10.6084/m9.figshare.31941543)  
**Author:** Morten Magnusson (ORCID: 0009-0002-4860-5095)  
**Framework:** Energy-Flow Cosmology (EFC) v3.7  
**License:** CC-BY-4.0

## Summary

First numerical consistency test of the EFC regime transition: the same
relativistic action produces mu < 1 (suppressed growth) in the linear
cosmological regime and is compatible with mu > 1 (enhanced gravity) in
the non-linear galactic regime. This is not two models -- it is two
regime-limits of one action connected through the entropy production
function Gamma(rho).

## Key Results

- **No sign-conflict:** mu(k) = (1 + eps_F) / (F(1 + R(k))) with R proportional to k^-4
  gives mu < 1 at cosmological scales and mu -> 1 at galactic scales
- **Survival valley:** mu ~ 0.94, eta ~ 1.10-1.15, Sigma > 1 at k ~ 0.05 h/Mpc
- **GR recovery:** All EFT corrections vanish at galactic scales (k >> k_c)
- **Spatiotemporal localization:** mu(k,z) confined to z < z_t ~ 1 and k < 0.1
- **Parameter robustness:** 49.6% of (K_bar, lambda_dot) space passes all constraints
- **Growth consistency:** Delta-chi^2 = -0.03 vs LCDM on BOSS DR12 f*sigma_8

## Calibrated EFT Parameters (Table 1)

| Parameter | Value | Meaning |
|-----------|-------|---------|
| alpha | 0.001 | Non-minimal coupling |
| K_bar | 643 | Kinetic stiffness |
| phi_dot_bar | 0.01 | Background field velocity |
| lambda_dot_bar | 0.049 | Flow constraint rate |

## Predictions

- **P1:** Cluster-scale transition: mu ~ 1.1, Sigma ~ 1.2 at k ~ 0.3 (testable by DES Y6, Euclid)
- **P2:** No mu > 1 in linear perturbations (falsified if linear-regime observations require mu > 1)

## AI-Friendly Package

```
Consistency_of_Scale_Dependent_.../
├── README.md              # This file
├── index.json             # Machine-readable index
├── schema.json            # Validation schema
├── metadata.json          # Structured metadata
├── regime_transition.jsonld  # JSON-LD linked data
├── citations.bib          # BibTeX references
├── src/
│   ├── __init__.py        # Package init
│   └── regime_transition.py  # Core implementation
├── data/
│   └── regime_transition_data.json  # Parameters and results
└── examples/
    └── demo_regime_transition.py    # Executable demo
```

## Quick Start

```python
from src.regime_transition import (
    EFCRegimeTransition, StiffnessResponse, SurvivalValley,
    SpatiotemporalGrid, ParameterScan, GrowthODE, Predictions
)

# Compute mu(k) across scales
model = EFCRegimeTransition()
mu = model.mu(k=0.05)        # Cosmological: ~0.94
mu = model.mu(k=10.0)        # Galactic: ~1.0

# Spatiotemporal localization
grid = SpatiotemporalGrid()
result = grid.compute(k=0.05, z=0.0)  # Full (mu, eta, Sigma)
```

## Related Papers

- [EFC Relativistic Action](../EFC_Relativistic_Action/) (DOI: 31876324) -- Source action
- [Systematic CMB Localization](../Systematic_Localization_of_Late_Time/) (DOI: 31368433) -- Survival valley
- [Grid Microphysics to RAR](../From_Grid_Microphysics_to_the_Radial_Acceleration/) (DOI: 31878760)
- [Gradient-Coupled Grid Action](../EFC_Gradient_Coupled_Grid_Action/) (DOI: 31941465)
