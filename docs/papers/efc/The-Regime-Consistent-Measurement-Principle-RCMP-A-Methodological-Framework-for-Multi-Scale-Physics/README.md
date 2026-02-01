# The Regime-Consistent Measurement Principle (RCMP)

**A Methodological Framework for Multi-Scale Physics**

[![DOI](https://img.shields.io/badge/DOI-10.6084/m9.figshare.31222900-blue)](https://doi.org/10.6084/m9.figshare.31222900)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## Overview

The Regime-Consistent Measurement Principle (RCMP) is a methodological framework designed to prevent interpretive errors when measurements span multiple physical regimes. The principle ensures that observables are interpreted through the most appropriate variables within their operative regime.

### Core Principle

> **An observable must be interpreted through the variable most directly coupled to the physical driver in the phenomenon's operative regime. Cross-regime mappings require explicit transformation and uncertainty propagation.**

### The Problem

Modern physics increasingly confronts phenomena spanning multiple regimes:
- Quantum to classical scales
- Laboratory to cosmological distances
- High to low acceleration environments

Without explicit regime tracking, apparent disagreements between frameworks may reflect **methodological artifacts** rather than physical differences.

### The Solution

RCMP provides five core principles:
1. **Driver Proximity** - Choose the most directly coupled observable
2. **Regime Tagging** - Label each measurement with its dominant regime (L0-L3)
3. **Proxy Accounting** - Document the full transformation chain with uncertainties
4. **Coordinate Humility** - Recognize that coordinate choice is not epistemically neutral
5. **Cross-Validation** - Test consistency across independent proxy chains

## Repository Structure

```
RCMP/
├── README.md                    # This file
├── QUICKSTART.md               # Getting started guide
├── MANIFEST.md                 # Complete file listing
├── LICENSE                     # CC BY 4.0
├── CITATION.cff                # Citation metadata
├── index.json                  # Machine-readable index
├── RCMP.jsonld                 # Schema.org metadata
├── schema.json                 # JSON Schema definition
├── citations.bib               # BibTeX references
├── The_Regime_Consistent_*.pdf # Authoritative document
├── docs/
│   ├── RCMP-framework.md       # Complete framework description
│   ├── epistemic-layers.md     # L0-L3 layer documentation
│   └── application-galaxy.md   # Galaxy rotation curve example
├── src/
│   ├── __init__.py
│   ├── rcmp_validator.py       # RCMP validation implementation
│   ├── regime_tagger.py        # Regime classification
│   ├── proxy_chain.py          # Proxy chain documentation
│   └── uncertainty_propagator.py # Uncertainty handling
├── data/
│   ├── epistemic_layers.json   # L0-L3 definitions
│   ├── validation_checklist.json # RCMP checklist
│   └── galaxy_example.json     # Example application data
└── examples/
    └── rcmp_galaxy_analysis.py # Worked example
```

## Epistemic Layer Structure (L0-L3)

| Layer | Description | Example (Galaxy Dynamics) |
|-------|-------------|---------------------------|
| L0 | Direct measurement | Spectral line velocity |
| L1 | Calibrated observable | Rotation velocity V(R) |
| L2 | Derived quantity | Centripetal acceleration g_obs |
| L3 | Theoretical construct | Dark matter density profile |

## Key Concepts

### Primary Variable Selection

$$V^* = \arg\min_i d(V_i, D | R)$$

Where:
- $V_i$ = candidate interpretive variables
- $D$ = physical driver in regime $R$
- $d(V_i, D | R)$ = epistemic distance

### Transformation Requirement

For any variable $V_j \neq V^*$, interpretation requires:
- Explicit transformation $T_{*j}: V^* \to V_j$
- Propagated uncertainty $\sigma_{\text{total}} = \sqrt{\sigma_O^2 + \sigma_{T_{*j}}^2}$

### RCMP Validation Checklist

| Item | Requirement |
|------|-------------|
| Driver identified | Physical driver explicit for each regime |
| Regime tagged | Each data point labeled with dominant regime |
| Proxy chain documented | Full transformation sequence recorded |
| Uncertainties propagated | Each transformation adds to error budget |
| Cross-validation performed | Multiple proxy chains compared |

## Quick Start

```python
from src.rcmp_validator import RCMPValidator
from src.regime_tagger import RegimeTagger
from src.proxy_chain import ProxyChain

# Initialize RCMP validator
validator = RCMPValidator()

# Define your measurement context
measurement = {
    "observable": "rotation_velocity",
    "regime": "low_acceleration",
    "driver": "gravitational_response"
}

# Tag the regime
tagger = RegimeTagger()
regime_info = tagger.classify(measurement)

# Document proxy chain
chain = ProxyChain()
chain.add_step("spectral_velocity", "L0", sigma=0.01)
chain.add_step("rotation_velocity", "L1", sigma=0.02)
chain.add_step("centripetal_acceleration", "L2", sigma=0.05)

# Validate RCMP compliance
result = validator.validate(measurement, chain)
print(f"RCMP Valid: {result.is_valid}")
print(f"Total uncertainty: {chain.total_uncertainty()}")
```

## Application Example: Galaxy Rotation Curves

RCMP-guided analysis of the SPARC dataset reveals:

| Finding | Per-Point | Per-Galaxy |
|---------|-----------|------------|
| Dwarf vs spiral scatter | 1.27× higher (p=0.02) | Identical (p=0.47) |
| Interpretation | Intra-galaxy variability | No class-level offset |

This resolves the apparent paradox: dwarf galaxies show more internal variability, but their median response follows the same universal law as spirals.

## Related Work

This framework integrates with:

- **L0-L3 Regime Architecture** ([DOI: 10.6084/m9.figshare.31112536](https://doi.org/10.6084/m9.figshare.31112536))
- **Validity-Aware AI** ([DOI: 10.6084/m9.figshare.31122970](https://doi.org/10.6084/m9.figshare.31122970))
- **Entropy-Bounded Empiricism** (EFC Framework)

## Citation

```bibtex
@techreport{magnusson2026rcmp,
  author = {Magnusson, Morten},
  title = {The Regime-Consistent Measurement Principle (RCMP): A Methodological Framework for Multi-Scale Physics},
  year = {2026},
  month = {January},
  institution = {Independent Researcher},
  doi = {10.6084/m9.figshare.31222900},
  url = {https://doi.org/10.6084/m9.figshare.31222900},
  version = {1.0}
}
```

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Author

**Morten Magnusson**
Independent Researcher, Norway
ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)

---

*Part of the Energy-Flow Cosmology (EFC) research program.*
