# CMB Thermodynamic Interpretation

A compatibility and null-test framework under entropy-constrained structure formation within Energy-Flow Cosmology (EFC).

## Overview

This paper tests consistency between Energy-Flow Cosmology (EFC) and Cosmic Microwave Background (CMB) observables. JWST observations constrain the entropy profile S(z), which is then tested against CMB constraints without parameter fitting.

## Core Principle

```
JWST -> S(z) -> CMB consequences
```

- Causal ordering enforced
- No parameter fitting permitted
- No circular inference

## Compatibility Constraints

| Observable | Value | Requirement |
|------------|-------|-------------|
| theta_s | 100.09 +/- 0.30 arcmin | Within uncertainty |
| Peak ratio R | ~0.42 | Within 2-sigma |
| Damping l_D | Silk form | Standard form |
| TE/EE | Positive | Sign preserved |

## Prediction Zones

- A_L < 1.0 (smoother halos)
- ISW phase shift 0.01-0.1 rad at l > 1000
- C_l^{phi phi} z-dependent at high l

## Null Tests (Falsifiable)

1. Peak position: theta_s within 0.5% or falsified
2. Damping: l_D within 5% or falsified
3. Lensing: A_L >= 1.0 at high significance means falsified

## EFC Parameters

| Parameter | Definition | Constraint Source |
|-----------|------------|-------------------|
| S_0 | Entropy at z = 0 | SPARC rotation curves |
| S_eq | Entropy at matter-radiation equality | CMB peak structure |
| alpha_S | Entropy coupling strength | JWST sSFR correlation |
| n_S | Entropy profile exponent | Cross-scale consistency |

## Files

```
CMB-Thermodynamic-Interpretation/
  README.md                      # This file
  index.json                     # Machine-readable index
  schema.json                    # JSON Schema validation
  metadata.json                  # Structured metadata
  cmb_thermodynamic.jsonld       # JSON-LD linked data
  citations.bib                  # BibTeX references
  src/__init__.py                # Package imports
  src/cmb_thermodynamic.py       # Python implementation
  data/cmb_thermodynamic_data.json  # Structured data
  examples/demo_cmb_thermodynamic.py # Executable demo
```

## Empirical Basis

JWST/COSMOS-Web galaxy excess at high redshift:

| z | vs LCDM | vs Halo Limit | Status |
|---|---------|---------------|--------|
| 5-6 | 23x | 3.1x | Within baryonic physics |
| 7-8 | 124x | 7.7x | Exceeds standard models |
| 8-9 | 259x | 10.4x | Exceeds epsilon=1 limit |
| 9-10 | 529x | 10.6x | Exceeds epsilon=1 limit |

Statistical significance: chi-squared = 47.3, df = 4, p < 10^-9

## Citation

```bibtex
@misc{magnusson2026cmb,
  author = {Magnusson, Morten},
  title  = {CMB Thermodynamic Interpretation: A compatibility and null-test framework},
  year   = {2026},
  doi    = {10.6084/m9.figshare.31064929}
}
```

## License

CC-BY-4.0

## Author

Morten Magnusson
Symbiose Research, Sandnes, Norway
ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)
