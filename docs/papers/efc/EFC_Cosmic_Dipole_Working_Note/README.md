# The Cosmic Dipole Anomaly as Regime-Dependent Anisotropy in EFC

**DOI:** [10.6084/m9.figshare.31942731](https://doi.org/10.6084/m9.figshare.31942731)  
**Author:** Morten Magnusson (ORCID: 0009-0002-4860-5095)  
**Framework:** Energy-Flow Cosmology (EFC) v3.7  
**Status:** Working Note (v0.1)  
**License:** CC-BY-4.0

## Summary

The observed galaxy number count dipole is 2-3x larger than the kinematic
prediction from LCDM. This working note shows that EFC contains a natural
mechanism: isotropy is a **regime condition** (valid in L0/L1), not an
absolute postulate. Any residual large-scale entropy gradient nabla-S
imprints a preferred direction in structure growth via G_eff(S).

## Key Results

- **Isotropy as regime condition:** Valid in L0/L1, broken in L2 by spatial S(x)
- **Entropy gradient mechanism:** G_eff(n) = G_N(1 + mu_0 f'(S) nabla-S . n L_grad)
- **Dipole amplitude:** D_EFC ~ (b_eff/2) mu_0 |f'| |nabla-S| L_grad / S_bar
- **Required gradient:** ~2% entropy variation across observable volume
- **Consistency:** Compatible with CMB isotropy (10^-5 at z~1100, amplified by ~10^3)

## Predictions

- **P1:** Dipole excess grows with decreasing z (redshift dependence)
- **P2:** Directional f*sigma_8 anisotropy at ~2% level
- **P3:** Alignment with bulk flow and CMB dipole direction
- **P4:** Scale dependence — excess more pronounced for large-volume tracers

## Open Gaps

- **G1:** Origin of nabla-S (initial conditions / topology)
- **G2:** Quantitative f(S) profile at super-Hubble scales
- **G3:** Separation from kinematic contribution
- **G4:** Consistency with CMB isotropy (explicit verification)

## AI-Friendly Package

```
EFC_Cosmic_Dipole_Working_Note/
├── README.md               # This file
├── index.json              # Machine-readable index
├── schema.json             # Validation schema
├── metadata.json           # Structured metadata
├── cosmic_dipole.jsonld    # JSON-LD linked data
├── citations.bib           # BibTeX references
├── src/
│   ├── __init__.py         # Package init
│   └── cosmic_dipole.py   # Core implementation
├── data/
│   └── cosmic_dipole_data.json  # Parameters and observations
└── examples/
    └── demo_cosmic_dipole.py    # Executable demo
```

## Related Papers

- [EFC Screening Model](../Energy-Flow_Cosmology_Empirical_Validation_of_the_EFC_Screening_Model_Track_1/) (DOI: 31940469)
- [Regime Transition Test](../Consistency_of_Scale_Dependent_Gravitational_Response_in_EFC_Numerical_Regime_Transition_Test/) (DOI: 31941543)
- [Systematic CMB Localization](../Systematic_Localization_of_Late_Time/) (DOI: 31368433)
