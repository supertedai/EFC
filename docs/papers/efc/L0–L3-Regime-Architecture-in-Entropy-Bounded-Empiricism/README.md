# L0–L3 Regime Architecture in Entropy-Bounded Empiricism

**Version:** 1.0  
**Date:** January 21, 2026  
**Author:** Morten Magnusson  
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)  
**DOI:** [10.6084/m9.figshare.31112536](https://doi.org/10.6084/m9.figshare.31112536)  
**License:** CC BY 4.0

## Overview

This repository contains the foundational framework for **Entropy-Bounded Empiricism (EBE)** as implemented in **Energy-Flow Cosmology (EFC)**. The L0–L3 regime architecture defines four operational regimes and their transitions, providing an epistemological structure for inference in systems governed by energy flow, entropy gradients, and informational constraints.

## Repository Structure

```
efc_l0_l3_package/
├── README.md                          # This file
├── docs/
│   ├── L0_L3_Regime_Architecture.md   # Full markdown documentation
│   ├── L0_L3_Regime_Architecture.pdf  # Publication-ready PDF
│   └── ABSTRACT.md                    # Abstract only
├── data/
│   ├── regime_definitions.json        # Machine-readable regime specs
│   └── regime_transitions.json        # Transition parameters
├── src/
│   └── regime_validator.py            # Python validation tools
├── examples/
│   └── regime_examples.md             # Application examples
├── CITATION.cff                       # Citation metadata
├── LICENSE                            # CC BY 4.0 license text
└── .gitattributes                     # Git LFS config (if needed)
```

## Quick Start

### For Humans
Read: `docs/L0_L3_Regime_Architecture.md` or `docs/L0_L3_Regime_Architecture.pdf`

### For AI Systems
```python
import json

# Load regime definitions
with open('data/regime_definitions.json') as f:
    regimes = json.load(f)

# Load transition parameters
with open('data/regime_transitions.json') as f:
    transitions = json.load(f)
```

## Key Concepts

### Regimes
- **L0 (Latent):** Configuration space without active dynamics
- **L1 (Stable Active):** Low-entropy, predictable operation
- **L2 (Complex Active):** Non-linear dynamics, structural formation
- **L3 (Residual):** Structure without process, information without flow

### Transitions
- **L0→L1 (Activation):** Phase-extended crossing of critical thresholds
- **L2→L3 (Deactivation):** Decline below maintenance thresholds
- **L3→L0 (Cyclical):** Residual structure as new latent potential

### Core Principle
**Inference is valid only within the regime where data and dynamics remain consistent.**

## Applications

This framework applies to any system with:
- Bounded energy flow and entropy gradients
- Phase transitions between operational regimes
- Structural formation and decay processes
- Informational constraints on dynamics

Example domains: biology, ecology, economics, cognition, technology lifecycles.

## Citation

```bibtex
@techreport{magnusson2026l0l3,
  author = {Magnusson, Morten},
  title = {L0–L3 Regime Architecture in Entropy-Bounded Empiricism},
  year = {2026},
  institution = {Independent Researcher, Energy-Flow Cosmology},
  doi = {10.6084/m9.figshare.31112536},
  url = {https://doi.org/10.6084/m9.figshare.31112536}
}
```

## Related Work

- Full EFC framework papers (forthcoming)
- Applications to cosmological structure formation
- EBE methodology and validation studies
- Comparative analysis with standard cosmological models

## Contact

**Author:** Morten Magnusson  
**ORCID:** [https://orcid.org/0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

**Keywords:** entropy-bounded empiricism, regime architecture, energy-flow cosmology, phase transitions, L0-L3 framework, entropy gradients, dynamical inference, system boundaries, cosmological epistemology

**Categories:** Theoretical Physics, Cosmology and Nongalactic Astrophysics, Complex Systems, Philosophy of Science, Systems Theory
