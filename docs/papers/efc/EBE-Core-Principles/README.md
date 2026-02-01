# Entropy-Bounded Empiricism: Core Principles

**A Regime-Based Epistemic Framework for Measurement Interpretation in Emergent Systems**

[![DOI](https://img.shields.io/badge/DOI-10.6084/m9.figshare.31222903-blue)](https://doi.org/10.6084/m9.figshare.31222903)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## Overview

Entropy-Bounded Empiricism (EBE) is a regime-based epistemic framework for interpreting measurements in systems governed by entropy gradients and energy flow. EBE introduces two orthogonal classification axes that together define the epistemic validity of any scientific claim.

### Core Insight

> **What we can know depends on where we measure.**

### The Two Axes

1. **S-Axis (Physical Regime)** - Classification by entropy state
2. **L-Axis (Epistemic Layer)** - Classification by assumption load

### The Problem EBE Solves

Scientific models succeed or fail within specific regimes. When models are applied outside these regimes:
- Interpretive errors accumulate
- Measurements become proxies for proxies
- Theoretical constructs detach from empirical grounding

EBE makes regime boundaries explicit and defines clear rules for when measurements can validly inform theory.

## Repository Structure

```
EBE-Core-Principles/
├── README.md                    # This file
├── QUICKSTART.md               # Getting started guide
├── MANIFEST.md                 # Complete file listing
├── LICENSE                     # CC BY 4.0
├── CITATION.cff                # Citation metadata
├── index.json                  # Machine-readable index
├── EBE.jsonld                  # Schema.org metadata
├── schema.json                 # JSON Schema definition
├── citations.bib               # BibTeX references
├── EBE_Core_Principles_*.pdf   # Authoritative document
├── docs/
│   ├── s-axis-regimes.md       # Physical regime hierarchy
│   ├── l-axis-layers.md        # Epistemic layer hierarchy
│   └── rcmp-protocol.md        # Measurement protocol
├── src/
│   ├── __init__.py
│   ├── s_axis_classifier.py    # S-axis regime classification
│   ├── l_axis_tagger.py        # L-axis layer tagging
│   └── ebe_validator.py        # EBE compliance validation
├── data/
│   ├── s_axis_regimes.json     # S-axis definitions
│   ├── l_axis_layers.json      # L-axis definitions
│   └── rcmp_mapping.json       # RCMP validity mapping
└── examples/
    └── ebe_classification_example.py
```

## The S-Axis: Physical Regime Hierarchy

The S-axis classifies physical regimes by their dominant entropy character:

| Regime | S Range | Physical Character | Dominant Description |
|--------|---------|-------------------|---------------------|
| Low-S | S → 0 | Field/statistical ensemble | Spectral analysis, field theory |
| Mid-S | S ∼ 0.5 | Structure/relational dynamics | Response functions, correlations |
| High-S | S → 1 | Local complexity/thermodynamic | Energy flows, entropy production |

### S-Axis Regime Classification

$$\mathcal{S}: S \in [0, 1] \longrightarrow \{\text{Low-}S, \text{Mid-}S, \text{High-}S\}$$

## The L-Axis: Epistemic Layer Hierarchy

The L-axis classifies claims by epistemic strength:

| Layer | Type | Role |
|-------|------|------|
| L₀ | Raw data | Direct instrumental output; minimal assumptions |
| L₁ | Calibrated observables | Corrected for known systematics |
| L₂ | Derived quantities | Physical parameters computed from L₁ |
| L₃ | Theoretical constructs | Model-dependent interpretation |

### Layer Transparency Axiom

All interpretive chains must be explicitly traceable:

$$L_0 \xrightarrow{\text{calibration}} L_1 \xrightarrow{\text{derivation}} L_2 \xrightarrow{\text{modeling}} L_3$$

## RCMP: Regime-Consistent Measurement Protocol

The RCMP defines valid mappings between S-axis and L-axis:

$$\text{RCMP}(S) = \min\{L : L \text{ is driver-near in regime } S\}$$

| S-Regime | Valid Primary L-Level |
|----------|----------------------|
| Field regime (Low-S) | L₁–L₂ |
| Structure regime (Mid-S) | L₂ |
| Complexity regime (High-S) | L₁–L₂ (locally) |

## The Regime-Gating Principle

> **A model is epistemically valid only within the regime where its primary variables are driver-near.**

$$\text{Validity}(M) = \{S : \text{primary variables of } M \text{ are driver-near in } S\}$$

This transforms model conflicts into regime boundary questions.

## Quick Start

```python
from src.s_axis_classifier import SAxisClassifier
from src.l_axis_tagger import LAxisTagger
from src.ebe_validator import EBEValidator

# Initialize classifiers
s_classifier = SAxisClassifier()
l_tagger = LAxisTagger()
validator = EBEValidator()

# Classify a measurement
measurement = {
    "type": "rotation_velocity",
    "value": 125.3,
    "entropy_state": 0.6
}

# Get S-axis regime
s_regime = s_classifier.classify(measurement["entropy_state"])
print(f"S-Regime: {s_regime}")  # Mid-S (Structure regime)

# Get L-axis layer
l_layer = l_tagger.tag(measurement["type"])
print(f"L-Layer: {l_layer}")  # L1 (Calibrated observable)

# Validate EBE compliance
result = validator.validate(s_regime, l_layer)
print(f"Valid interpretation: {result.is_valid}")
```

## EBE Core Statement

> **Physical validity depends on regime (S), epistemic strength depends on layer (L), and correct interpretation requires regime-consistent mapping between them (RCMP).**

$$\text{Valid Interpretation} \Longleftrightarrow \text{RCMP}(S) \leq L \leq L_3$$

## Applications Beyond Cosmology

EBE generalizes to any system governed by entropy gradients:

| Domain | EBE Application |
|--------|-----------------|
| Biology | Metabolic regimes, morphogenesis |
| Neuroscience | Neural dynamics, consciousness studies |
| Ecology | Ecosystem stability, trophic cascades |
| Economics | Market regimes, complexity economics |
| Technology | AI systems, network dynamics |

## Related Work

- **L0-L3 Regime Architecture** ([DOI: 10.6084/m9.figshare.31112536](https://doi.org/10.6084/m9.figshare.31112536))
- **RCMP Framework** ([DOI: 10.6084/m9.figshare.31222900](https://doi.org/10.6084/m9.figshare.31222900))
- **Energy-Flow Cosmology** ([DOI: 10.6084/m9.figshare.27315821](https://doi.org/10.6084/m9.figshare.27315821))

## Citation

```bibtex
@techreport{magnusson2026ebe,
  author = {Magnusson, Morten},
  title = {Entropy-Bounded Empiricism: Core Principles},
  subtitle = {A Regime-Based Epistemic Framework for Measurement Interpretation in Emergent Systems},
  year = {2026},
  month = {January},
  institution = {Independent Researcher},
  doi = {10.6084/m9.figshare.31222903},
  url = {https://doi.org/10.6084/m9.figshare.31222903},
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
