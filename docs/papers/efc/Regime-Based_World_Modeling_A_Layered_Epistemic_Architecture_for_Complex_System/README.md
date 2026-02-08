# Regime-Based World Modeling (RBWM)

**A Layered Epistemic Architecture for Complex Systems**

[![DOI](https://img.shields.io/badge/DOI-10.6084/m9.figshare.31223650-blue)](https://doi.org/10.6084/m9.figshare.31223650)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## Overview

Regime-Based World Modeling (RBWM) is a meta-epistemic architecture designed to map model validity across two orthogonal axes. It addresses the persistent challenge of **regime blindness** in multi-scale modeling—the implicit assumption that variables and laws valid in one regime remain primary in another.

### Core Principle

> **The map is not the territory—but with proper coordinates, we can at least know which territory we are mapping.**

### The Problem

Current world models often suffer from:
- **Regime blindness:** Conflating variables that are causal drivers in one regime with variables that are merely statistical proxies in another
- **Regime leakage:** Models calibrated for one level of complexity invalidly extrapolated to another
- **Phantom anomalies:** Discrepancies that arise from applying the wrong regime's variables

## Repository Structure

```
Regime-Based_World_Modeling_.../
├── README.md                    # This file
├── QUICKSTART.md               # Getting started guide
├── MANIFEST.md                 # Complete file listing
├── LICENSE                     # CC BY 4.0
├── CITATION.cff                # Citation metadata
├── index.json                  # Machine-readable index
├── RBWM.jsonld                 # Schema.org metadata
├── schema.json                 # JSON Schema definition
├── citations.bib               # BibTeX references
├── Regime_Based_World_Modeling_*.pdf  # Authoritative document
├── docs/
│   ├── r-axis-regimes.md       # Regime axis documentation
│   ├── l-axis-layers.md        # Epistemic layer documentation
│   ├── regime-gating.md        # Regime-Gating Principle
│   └── applications.md         # Cross-domain applications
├── src/
│   ├── __init__.py
│   ├── coordinate_system.py    # (R, L) coordinate mapping
│   ├── regime_gating.py        # Regime-Gating validation
│   ├── validity_domain.py      # Model validity domains
│   └── conflict_resolver.py    # Model conflict resolution
├── data/
│   ├── r_axis_definitions.json # R-axis regime definitions
│   ├── l_axis_definitions.json # L-axis layer definitions
│   └── domain_examples.json    # Cross-domain examples
└── examples/
    └── rbwm_conflict_resolution.py
```

## The Two-Axis Architecture

### The Regime Axis (R)

Defines the level of emergent complexity:

| Regime | Description | Examples |
|--------|-------------|----------|
| R₀ (Field/Statistical) | Governed by statistical mechanics and field theories | CMB fluctuations, quantum states, thermodynamic ensembles |
| R₁ (Structure/Relational) | Stable structures emerge from field dynamics | Galaxies, ecosystems, neural networks, social institutions |
| R₂ (Complex Adaptive) | Feedback, learning, and self-modification | Economies, cognition, AI systems, evolutionary processes |

### The Epistemic Layer Axis (L)

Defines the assumption load of a variable:

| Layer | Type | Description |
|-------|------|-------------|
| L₀ | Raw Observation | Unprocessed sensor data |
| L₁ | Calibrated Observable | Instrument-corrected quantities |
| L₂ | Regime-Near Physics | Derived quantities proximal to causal drivers |
| L₃ | Theoretical Construct | Model-dependent entities |

## The Regime-Gating Principle (RGP)

> **A scientific claim C operating on variable V is epistemically valid only if V is "driver-proximal" within the phenomenon's operative regime R.**

### Driver Proximity

A variable V has **high driver proximity** in regime R if small changes in V produce first-order effects on the system's dynamics within that regime.

### The Regime-Consistent Measurement Principle (RCMP)

> **Interpret observables through variables nearest the physical driver in the operative regime.**

This prevents L₃ constructs from being treated as L₀ data.

## The (R, L) Coordinate System

Every scientific claim can be assigned a coordinate pair (R, L):

### Mapping Criteria

1. **Scale of the phenomenon:** What level of emergent complexity?
2. **Derivation chain:** How many inferential steps from observation?
3. **Driver proximity:** Does the variable directly cause effects in this regime?

### Resolving Model Conflicts

| Theory | Claim | Coordinates |
|--------|-------|-------------|
| ΛCDM | "Dark matter halos cause flat rotation curves" | (R₀→R₁, L₃) |
| MOND/RAR | "Modified dynamics explain rotation curves" | (R₁, L₂) |

These theories operate at **different coordinates**—comparison requires coordinate matching.

### Validity Domain

$$\mathcal{V}(M) = \{(R, L) : \text{variables of } M \text{ are driver-proximal at } (R, L)\}$$

## Applications Across Domains

### Physics
- Quantum mechanics: (R₀, L₂–L₃)
- Statistical mechanics: (R₀→R₁, L₂)
- Astrophysics: (R₁, L₁–L₃)

### Biology
- Molecular: (R₀) - Chemical kinetics
- Cellular: (R₁) - Metabolic pathways
- Organismal: (R₂) - Behavior, adaptation

### Economics
- Microeconomics: (R₁) - Individual agents
- Macroeconomics: (R₂) - Aggregate dynamics

### Artificial Intelligence
- Parameter space: (R₀, L₃)
- Representation space: (R₁, L₂)
- Behavioral space: (R₂, L₁)

## Quick Start

```python
from src.coordinate_system import RLCoordinate
from src.regime_gating import RegimeGatingValidator
from src.validity_domain import ValidityDomain
from src.conflict_resolver import ConflictResolver

# Define a claim with (R, L) coordinates
claim_A = RLCoordinate(
    name="Dark matter halo mass",
    regime="R1",
    layer="L3",
    description="NFW profile fit to rotation curve"
)

claim_B = RLCoordinate(
    name="Radial acceleration",
    regime="R1",
    layer="L2",
    description="Centripetal acceleration from velocity"
)

# Check regime-gating validity
validator = RegimeGatingValidator()
result_A = validator.check_driver_proximity(claim_A)
result_B = validator.check_driver_proximity(claim_B)

print(f"Claim A driver-proximal: {result_A.is_proximal}")  # False
print(f"Claim B driver-proximal: {result_B.is_proximal}")  # True

# Resolve apparent conflict
resolver = ConflictResolver()
resolution = resolver.compare(claim_A, claim_B)
print(f"Same coordinates: {resolution.same_coordinates}")  # False
print(f"Resolution: {resolution.explanation}")
```

## Implementation Protocol

1. **Explicit tagging:** Every model component receives an (R, L) coordinate label
2. **Transition functions:** Explicit coarse-graining when crossing regime boundaries
3. **Validity checking:** Before combining claims from different coordinates
4. **Uncertainty propagation:** Track epistemic uncertainty across transitions

## Related Work

- **EBE Core Principles** ([DOI: 10.6084/m9.figshare.31222903](https://doi.org/10.6084/m9.figshare.31222903))
- **L0-L3 Regime Architecture** ([DOI: 10.6084/m9.figshare.31112536](https://doi.org/10.6084/m9.figshare.31112536))
- **Symbiosis Architecture** ([DOI: 10.6084/m9.figshare.30773684](https://doi.org/10.6084/m9.figshare.30773684))

## Citation

```bibtex
@techreport{magnusson2026rbwm,
  author = {Magnusson, Morten},
  title = {Regime-Based World Modeling: A Layered Epistemic Architecture for Complex Systems},
  year = {2026},
  institution = {Independent Researcher},
  doi = {10.6084/m9.figshare.31223650},
  url = {https://doi.org/10.6084/m9.figshare.31223650}
}
```

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Author

**Morten Magnusson**
ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)

---

*Part of the Energy-Flow Cosmology (EFC) research program.*
