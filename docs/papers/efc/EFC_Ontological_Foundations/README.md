# EFC Ontological Foundations v1.0

**The Co-Primary Structure: Energy-Flow and Entropy as Differentiated Aspects of Pre-Geometric Potential**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

**Epistemic Status:** Layer C (Methodological). Coherence argument, not empirical claim. Provides logical foundation for EFC architecture.

## Overview

This document establishes the ontological foundations for Energy-Flow Cosmology (EFC). Through cross-domain coherence analysis, we identify the **co-primary structure** as the most logically consistent foundation.

### Core Resolution

> **Energy-flow (EF) and entropy (S) are not separate primordial entities. They are differentiated aspects of a single pre-geometric potential that differentiates at the Planck transition.**

This resolves the circularity problem inherent in monistic ontologies.

## Repository Structure

```
EFC_Ontological_Foundations/
├── README.md                    # This file
├── QUICKSTART.md               # Getting started guide
├── MANIFEST.md                 # Complete file listing
├── LICENSE                     # CC BY 4.0
├── CITATION.cff                # Citation metadata
├── index.json                  # Machine-readable index
├── Ontology.jsonld             # Schema.org metadata
├── schema.json                 # JSON Schema definition
├── citations.bib               # BibTeX references
├── EFC_Ontological_Foundations_*.pdf  # Authoritative document
├── docs/
│   ├── circularity-problem.md  # The monistic trap
│   ├── co-primary-resolution.md # The co-primary structure
│   └── efc-integration.md      # Integration with EFC
├── src/
│   ├── __init__.py
│   ├── ontology_checker.py     # Ontological consistency checker
│   └── phase_tracker.py        # Pre/Post-Planck phase tracking
└── data/
    ├── ontological_hypotheses.json
    └── framework_compatibility.json
```

## The Circularity Problem

Any emergent cosmology faces: **What is ontologically primary?**

### The Monistic Trap

**Energy-Flow Primacy (H1):**
- If energy-flow is primary: What flows, and through what medium, before structure exists?
- Flow presupposes substrate and directionality
- Without spacetime, these concepts become circular

**Entropy Primacy (H2):**
- If entropy is primary: Entropy of what? What states are being counted?
- Entropy is defined over microstates
- Without structure, there are no microstates

**Both monistic positions generate hidden circularity.**

## Cross-Domain Evidence

| Framework | Key Insight | Implication for EFC |
|-----------|-------------|---------------------|
| Wheeler (1989) | "It from Bit"—information is fundamental | Information/entropy has ontological weight |
| Verlinde (2010) | Gravity emerges from entropy gradients | Entropy can drive dynamics without being prior |
| Prigogine (1977) | Dissipative structures emerge from energy flow | Flow creates structure; structure enables flow |
| Holographic Principle | Information on boundaries encodes bulk | Spacetime may be emergent |
| Pre-Planck Physics | Below Planck scale, spacetime dissolves | "State" and "process" may be emergent |

**Pattern:** The most successful approaches treat information/entropy and dynamics/flow as **co-arising**.

## The Co-Primary Resolution

### Core Proposal

> Energy-flow (EF) and entropy (S) are two aspects of a single, undifferentiated pre-geometric potential that differentiates at the Planck transition.

Neither EF nor S is temporally or ontologically prior. The question "which came first?" is ill-posed.

### The Three Phases

| Phase | Characterization | Ontological Status |
|-------|------------------|-------------------|
| **Pre-Planck** | t < t_Planck. No spacetime. EF and S undifferentiated | Distinctions not applicable |
| **Planck Transition** | Symmetry breaking. Differentiation emerges | S = "what IS", EF = "what DOES" |
| **Post-Planck** | Standard physics. Grid emerges. Structure forms | EFC phenomenology applies |

### Comparison of Hypotheses

| Criterion | EF-Primary (H1) | S-Primary (H2) | Co-Primary (H3) |
|-----------|-----------------|----------------|-----------------|
| Circularity | FAILS | FAILS | **PASSES** |
| Pre-Planck coherence | FAILS | FAILS | **PASSES** |
| Wheeler compatibility | Partial | Strong | **Strong** |
| Verlinde compatibility | Partial | Strong | **Strong** |
| Prigogine compatibility | Strong | Partial | **Strong** |
| EFC integration | Partial | Partial | **Complete** |

## Integration with EFC Architecture

### Core Lock (Dynamical Engine)
The RG-flow parameter f(S) describes the **mechanism of differentiation**. The constant beta-function uniquely determines exponential relaxation from undifferentiated to differentiated regimes.

### EBE (Epistemic Framework)
The S-axis is **ontologically grounded**. Regime boundaries reflect the degree of S-EF differentiation.

### RCMP (Measurement Protocol)
Driver-proximity is explained by the degree of S-EF differentiation. In regimes where differentiation is incomplete, standard measurement assumptions break down.

### EFC Phenomenology
Emergent time, structure formation, and regime-dependent physics all follow from the S-EF interplay in post-Planck space.

## Quick Start

```python
from src.ontology_checker import OntologyChecker
from src.phase_tracker import PhaseTracker

# Check ontological consistency
checker = OntologyChecker()

# Test monistic hypotheses
h1_result = checker.test_hypothesis("EF_primary")
h2_result = checker.test_hypothesis("S_primary")
h3_result = checker.test_hypothesis("co_primary")

print(f"H1 (EF-primary): {h1_result.circularity_free}")  # False
print(f"H2 (S-primary): {h2_result.circularity_free}")   # False
print(f"H3 (Co-primary): {h3_result.circularity_free}")  # True

# Track phase transitions
tracker = PhaseTracker()
phase = tracker.identify_phase(t_ratio=0.5)  # t/t_Planck
print(f"Phase: {phase}")  # "planck_transition"

# Check EFC integration
integration = checker.test_efc_compatibility("co_primary")
print(f"Core Lock compatible: {integration.core_lock}")
print(f"EBE compatible: {integration.ebe}")
print(f"RCMP compatible: {integration.rcmp}")
```

## What This Document Claims

- ✓ The co-primary structure is the most logically coherent ontology for EFC
- ✓ It integrates consistently with all EFC sub-frameworks
- ✓ It aligns with established theoretical frameworks (Wheeler, Verlinde, Prigogine)

## What This Document Does NOT Claim

- ✗ This is not an empirical claim (pre-Planck physics is beyond direct observation)
- ✗ This does not provide a concrete microphysical mechanism
- ✗ The "undifferentiated potential" is a conceptual placeholder

## EFC Architecture Layers

This document establishes **Layer 0** of the EFC architecture:

| Layer | Component | Role |
|-------|-----------|------|
| 0 | **Ontological Foundations** | Co-primary structure (this document) |
| 1 | Core Lock | Dynamical engine |
| 2 | EBE | Epistemic framework |
| 3 | RCMP | Measurement protocol |
| 4 | EFC Phenomenology | Observable predictions |

## Related Work

- **EBE Core Principles** ([DOI: 10.6084/m9.figshare.31222903](https://doi.org/10.6084/m9.figshare.31222903))
- **Core Lock** ([DOI: 10.6084/m9.figshare.31223503](https://doi.org/10.6084/m9.figshare.31223503))
- **Energy-Flow Cosmology** ([DOI: 10.6084/m9.figshare.27315821](https://doi.org/10.6084/m9.figshare.27315821))

## Citation

```bibtex
@techreport{magnusson2026ontology,
  author = {Magnusson, Morten},
  title = {EFC Ontological Foundations v1.0: The Co-Primary Structure},
  subtitle = {Energy-Flow and Entropy as Differentiated Aspects of Pre-Geometric Potential},
  year = {2026},
  month = {February},
  institution = {Independent Researcher},
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
