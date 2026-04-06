# Toward a Quantitative c_eff(a): Parameterization, Constraints, and Degeneracy-Breaking Tests

Effective speed of sound parameterization within Energy-Flow Cosmology (EFC).

## Overview

This paper introduces a quantitative parameterization of the effective cosmological propagation speed c_eff(a) within the EFC framework. If the vacuum sector that governs H(a) also modifies the medium properties, a weak state-dependence of c_eff follows as a consistency requirement.

## Key Equation

```
c_eff(a) = c_0 * [1 + epsilon * beta * T(a)]
```

Where:
- c_0 = laboratory speed of light (unchanged locally)
- beta = 0.08 (background coupling amplitude from BAO+RSD)
- T(a) = EFC transition function, normalized to peak at unity (z_peak = 0.441)
- epsilon = dimensionless coupling strength (one free parameter, range 0.01-0.1)

## Two Implementations

1. **Case (i): Metric VSL** -- c_eff enters as modified conformal structure. CDDR preserved. Degenerate with H(z) modification.
2. **Case (ii): Optical-medium** -- c_eff enters as refractive index n(a) = c_0/c_eff(a). CDDR can be violated with sign change near z ~ 0.44.

## Degeneracy-Breaking Tests

| Test | Description | Applies to |
|------|-------------|------------|
| Test 1: CDDR | Sign-change near z~0.44 | Case ii only |
| Test 2: ISW kernel | Second-order probe at l < 60 | Both |
| Test 3: beta-split | Distance vs growth beta comparison | Both |
| Test 4: Sirens | GW vs EM distance comparison | Both |

## Falsification Criteria

| ID | Condition | Meaning |
|----|-----------|---------|
| F-ceff-1 | CDDR violation inconsistent with T(z) | c_eff not grid-driven |
| F-ceff-2 | beta_BAO = beta_RSD to < 1% | epsilon ~ 0 |
| F-ceff-3 | CDDR monotonic (no sign change) | Not EFC-type |
| F-ceff-4 | Local lab c variation | EFC predicts no local effect |
| F-ceff-5 | D_L^GW = D_L^EM to sub-percent | No EM-specific modification |
| F-ceff-6 | Case ii but eta=1 to < 0.5% | Case ii ruled out |

## Files

```
c_eff_parameterization/
  README.md                       # This file
  index.json                      # Machine-readable index
  schema.json                     # JSON Schema validation
  metadata.json                   # Structured metadata
  c_eff.jsonld                    # JSON-LD linked data
  citations.bib                   # BibTeX references
  src/__init__.py                 # Package imports
  src/c_eff.py                    # Python implementation
  data/c_eff_data.json            # Structured data
  examples/demo_c_eff.py          # Executable demo
```

## Citation

```bibtex
@misc{magnusson2026ceff,
  author = {Magnusson, Morten},
  title  = {Toward a Quantitative c_eff(a): Parameterization, Constraints, and Degeneracy-Breaking Tests},
  year   = {2026},
  doi    = {10.6084/m9.figshare.31305421}
}
```

## License

CC-BY-4.0

## Author

Morten Magnusson
Symbiose Research, Sandnes, Norway
ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)
