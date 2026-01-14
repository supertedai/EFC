# CMB Thermodynamic Interpretation

A compatibility and null-test framework under entropy-constrained structure formation.

## Overview

This framework tests consistency between Energy-Flow Cosmology (EFC) and Cosmic Microwave Background (CMB) observables. JWST observations constrain the entropy profile S(z), which is then tested against CMB constraints without parameter fitting.

## Core Principle

```
JWST → S(z) → CMB consequences
```

- Causal ordering enforced
- No parameter fitting permitted
- No circular inference

## Framework Structure

### Compatibility Constraints (Must Hold)
| Observable | Value | Requirement |
|------------|-------|-------------|
| theta_s | 100.09 ± 0.30 arcmin | Within uncertainty |
| Peak ratio R | ~0.42 | Within 2σ |
| Damping l_D | Silk form | Standard form |
| TE/EE | Positive | Sign preserved |

### Prediction Zones (May Deviate)
- A_L < 1.0 (smoother halos)
- ISW phase shift 0.01-0.1 rad at l > 1000
- C_l^φφ z-dependent at high l

### Null Tests (Falsifiable)
1. Peak position: theta_s within 0.5% → else falsified
2. Damping: l_D within 5% → else falsified
3. Lensing: A_L >= 1.0 at high significance → falsified

## EFC Parameters

| Parameter | Definition | Constraint Source |
|-----------|------------|-------------------|
| S_0 | Entropy at z = 0 | SPARC rotation curves |
| S_eq | Entropy at matter-radiation eq | CMB peak structure |
| alpha_S | Entropy coupling strength | JWST sSFR correlation |
| n_S | Entropy profile exponent | Cross-scale consistency |

## Files

```
CMB-Thermodynamic-Interpretation/
├── README.md                           # This file
├── CMB_Thermodynamic_Interpretation.pdf # Main document (6 pages)
├── figure1_causal_flow.svg             # Causal flow diagram
├── meta.json                           # Machine-readable metadata
├── schema.jsonld                       # JSON-LD structured data
├── index.yaml                          # Document index
└── CITATION.cff                        # Citation metadata
```

## Empirical Basis

JWST/COSMOS-Web galaxy excess at high redshift:

| z | vs ΛCDM | vs Halo Limit | Status |
|---|---------|---------------|--------|
| 5-6 | 23× | 3.1× | Within baryonic physics |
| 7-8 | 124× | 7.7× | Exceeds standard models |
| 8-9 | 259× | 10.4× | Exceeds ε = 1 limit |
| 9-10 | 529× | 10.6× | Exceeds ε = 1 limit |

Statistical significance: χ² = 47.3, df = 4, p < 10⁻⁹

## Related Work

- [COSMOS-Web Galaxy Excess](https://doi.org/10.6084/m9.figshare.31059964)
- [Regime-Dependent Breakdown](https://doi.org/10.6084/m9.figshare.31061665)
- [EFC Structure Formation](https://doi.org/10.6084/m9.figshare.31064929)

## Citation

```bibtex
@misc{magnusson2026cmb,
  author = {Magnusson, Morten},
  title = {CMB Thermodynamic Interpretation: A compatibility and null-test framework},
  year = {2026},
  publisher = {Energy-Flow Cosmology Initiative},
  url = {https://doi.org/10.6084/m9.figshare.31064929}
}
```

## License

CC BY 4.0

## Author

Morten Magnusson  
Energy-Flow Cosmology Initiative  
ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)
