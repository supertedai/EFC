# Density-Dependent Gravitational Coupling Predicts ISW Sign-Flip in Deep Voids

**DOI:** [10.6084/m9.figshare.31942677](https://doi.org/10.6084/m9.figshare.31942677)  
**Author:** Morten Magnusson (ORCID: 0009-0002-4860-5095)  
**Framework:** Energy-Flow Cosmology (EFC) v3.7  
**License:** CC-BY-4.0

## Summary

EFC's density-dependent gravitational coupling mu(rho) produces a non-linear
ISW (Rees-Sciama) contribution with **opposite sign** to the standard linear
ISW effect in cosmic voids. The standard ISW makes cold spots from voids
(Phi_dot < 0). In EFC, the additional term delta * d_mu/dt is positive in voids,
partially cancelling or reversing the signal. For deep voids (delta < -0.8),
the net ISW signal **flips sign** -- a void produces a hot spot instead of
the expected cold spot.

## Key Results

- **ISW decomposition:** dPhi/dt = mu * (d_delta/dt) + delta * (d_mu/dt)
  - First term: standard linear ISW (cold spot in voids)
  - Second term: Rees-Sciama from d_mu/dρ > 0 (hot spot in voids)
- **Sign robustness:** RS term sign follows from d_mu/d_rho > 0,
  a structural consequence of Gamma(rho) from BE statistics
- **Amplitude ratio:** A_total = Delta_T_EFC / Delta_T_LCDM
  - delta = -0.3: A_total = +0.93 (7% correction)
  - delta = -0.7: A_total = +0.19 (81% cancellation)
  - delta = -0.8: A_total = -0.83 (sign flip!)
  - delta = -0.9: A_total = -4.88 (strong hot spot)
- **Sign-flip threshold:** A_total crosses zero near delta ~ -0.7
- **ISW excess:** EFC predicts A < 1 in deep voids; observed excess (A ~ 5)
  likely from systematics

## Predictions

- **P1:** Depth-dependent ISW turnover in void-CMB stacking (BOSS DR12/DESI)
- **P2:** Scale dependence — sign-flip at shallower |delta| for larger voids
- **P3:** Redshift evolution — RS/ISW ratio increases at lower z
- **Falsification:** If void ISW increases monotonically with |delta|

## AI-Friendly Package

```
void_isw_signflip_v2.1_final/
├── README.md                # This file
├── index.json               # Machine-readable index
├── schema.json              # Validation schema
├── metadata.json            # Structured metadata
├── void_isw.jsonld           # JSON-LD linked data
├── citations.bib            # BibTeX references
├── src/
│   ├── __init__.py          # Package init
│   └── void_isw.py          # Core implementation
├── data/
│   └── void_isw_data.json   # Parameters and results (Table 1)
└── examples/
    └── demo_void_isw.py     # Executable demo
```

## Quick Start

```python
from src.void_isw import (
    ISWDecomposition, ReesSciamaTerm, AmplitudeRatio,
    VoidProfile, SignFlipAnalysis, Predictions
)

# Compute ISW decomposition for a void
isw = ISWDecomposition()
result = isw.compute(delta=-0.5, z=0.5)

# Find sign-flip threshold
analysis = SignFlipAnalysis()
delta_flip = analysis.find_sign_flip()
```

## Related Papers

- [EFC Relativistic Action](../EFC_Relativistic_Action/) (DOI: 31876324) -- Source action
- [Regime Transition Test](../Consistency_of_Scale_Dependent_Gravitational_Response_in_EFC_Numerical_Regime_Transition_Test/) (DOI: 31941543)
- [Grid Microphysics to RAR](../From_Grid_Microphysics_to_the_Radial_Acceleration/) (DOI: 31878760)
