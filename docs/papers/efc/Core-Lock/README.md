# EBE Core Lock v1.0

**The S-Dynamic Foundation: Mathematical Engine for Entropy-Bounded Empiricism**

[![DOI](https://img.shields.io/badge/DOI-10.6084/m9.figshare.31223503-blue)](https://doi.org/10.6084/m9.figshare.31223503)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

**Epistemic Status:** Layer B (Hypothetical). Mathematical engine compatible with current null results; predictive at correlation level.

## Overview

Core Lock specifies the dynamical mechanism underlying Entropy-Bounded Empiricism (EBE). The model defines a running parameter f(S) with constant negative beta function, uniquely selecting an exponential form. Physical observables project via accumulated phase Φ(S).

### Key Prediction

> **The primary testable signature lies in correlations between running constants rather than their individual amplitudes.**

$$\frac{d \ln v}{d \ln c} = \frac{a_v}{a_c} = \text{constant}$$

## Repository Structure

```
Core-Lock/
├── README.md                    # This file
├── QUICKSTART.md               # Getting started guide
├── MANIFEST.md                 # Complete file listing
├── LICENSE                     # CC BY 4.0
├── CITATION.cff                # Citation metadata
├── index.json                  # Machine-readable index
├── CoreLock.jsonld             # Schema.org metadata
├── schema.json                 # JSON Schema definition
├── citations.bib               # BibTeX references
├── Core_Lock.pdf               # Authoritative document
├── *.png                       # Simulation figures
├── docs/
│   ├── grid-state-function.md  # f(S) specification
│   ├── beta-constraint.md      # Beta function derivation
│   └── falsification.md        # Testable predictions
├── src/
│   ├── __init__.py
│   ├── grid_state.py           # Grid state function f(S)
│   ├── phase_accumulator.py    # Running phase Φ(S)
│   ├── projection_laws.py      # Observable projections
│   └── correlation_test.py     # Correlation signature test
├── data/
│   ├── core_lock_params.json   # Model parameters
│   └── empirical_constraints.json # Observational bounds
└── examples/
    └── core_lock_simulation.py
```

## Hierarchical Framework Relationship

| Layer | Framework | Role |
|-------|-----------|------|
| Dynamical Foundation | **Core Lock** | Mathematical engine (this document) |
| Epistemic Framework | EBE | Classification of regimes and claims |
| Measurement Protocol | RCMP | Rules for regime-consistent interpretation |

## Core Lock Specification

### The Grid State Function f(S)

The fundamental driver is the Grid State Function f(S), describing the effective stiffness of the vacuum grid as a function of entropy state S.

### The Beta-Constraint

The beta function is constant:

$$\beta_f(S) \equiv \frac{d \ln f}{dS} = -\frac{1}{\Delta S}$$

This constraint yields the unique solution:

$$\boxed{f(S) = f_0 \exp\left(-\frac{S}{\Delta S}\right)}$$

### Conservation Law: Information Length

The Running Phase Φ(S) represents accumulated information length:

$$\Phi(S) = \int_0^S \frac{dS'}{f(S')} = \frac{\Delta S}{f_0}\left[\exp\left(\frac{S}{\Delta S}\right) - 1\right]$$

The total information length is an invariant:

$$\mathcal{I} = \Phi(S_1) = \text{constant}$$

### Projection Laws

Physical parameters project via Φ:

$$\ln\left(\frac{X}{X_0}\right) = a_X \cdot \Phi(S)$$

where $a_X$ is the coupling coefficient for parameter X.

## Falsification Criterion

### The Proxy-Independent Test

Combining projections for two parameters, the hidden phase cancels:

$$\frac{d \ln v}{d \ln c} = \frac{a_v}{a_c} = \text{constant}$$

**Primary signature:** The test is not whether individual constants vary, but whether any detected variations show **correlated behavior with constant log-log slope**.

### Empirical Constraints

| Observable | Redshift | Limit | Implied |a| bound |
|------------|----------|-------|---------|
| Δα/α (quasar) | z ∼ 3 | < 10⁻⁵ | < 5 × 10⁻⁵ |
| Δμ/μ (H₂) | z ∼ 2–3 | < 10⁻⁵ | < 5 × 10⁻⁵ |
| Δα/α (methanol) | z ∼ 0.89 | < 10⁻⁷ | < 10⁻⁶ |
| Δα/α (JWST) | z ∼ 3–10 | < 10⁻⁴ | < 2 × 10⁻⁴ |

### Viable Scenarios

1. **Weak coupling:** If |a| < 10⁻⁶, individual variations fall below detection, but correlation signature remains testable
2. **Alternative S-mapping:** If S(z) grows slower than ln(1+z), observable variation concentrates at z ≫ 10

## Quick Start

```python
from src.grid_state import GridStateFunction
from src.phase_accumulator import PhaseAccumulator
from src.projection_laws import ProjectionLaw
from src.correlation_test import CorrelationTest

# Initialize Core Lock model
f = GridStateFunction(f0=1.0, delta_S=0.5)
phi = PhaseAccumulator(f)

# Compute phase at entropy state S
S = 0.7
phase = phi.compute(S)
print(f"Φ({S}) = {phase:.4f}")

# Project observable
proj = ProjectionLaw(coupling=1e-6)
delta_X = proj.project(phase)
print(f"δX/X = {delta_X:.2e}")

# Test correlation signature
test = CorrelationTest()
result = test.check_slope_stability(
    variations_1=[1e-6, 2e-6, 3e-6],
    variations_2=[0.5e-6, 1e-6, 1.5e-6]
)
print(f"Constant slope: {result.is_constant}")
print(f"Slope ratio: {result.slope_ratio:.2f}")
```

## What Core Lock Is

- ✓ Mathematically consistent internal structure
- ✓ Compatible with EBE regime architecture and RCMP methodology
- ✓ Provides falsifiable correlation signature
- ✓ Unfalsified by current null results on varying constants

## What Core Lock Is Not

- ✗ Not empirically established
- ✗ Not a prediction of large variations at low redshift
- ✗ Not a specification of which observables are projections of Φ(S)

## Open Questions

1. **Operational definition of S:** What physical quantity does S correspond to?
2. **Physical basis for coupling coefficients:** Why should |a| be small?
3. **S(z) mapping:** The relationship between entropy parameter and redshift

## Related Work

- **EBE Core Principles** ([DOI: 10.6084/m9.figshare.31222903](https://doi.org/10.6084/m9.figshare.31222903))
- **RCMP Framework** ([DOI: 10.6084/m9.figshare.31222900](https://doi.org/10.6084/m9.figshare.31222900))

## Citation

```bibtex
@techreport{magnusson2026corelock,
  author = {Magnusson, Morten},
  title = {EBE Core Lock v1.0: The S-Dynamic Foundation},
  subtitle = {Mathematical Engine for Entropy-Bounded Empiricism},
  year = {2026},
  month = {February},
  institution = {Independent Researcher},
  doi = {10.6084/m9.figshare.31223503},
  url = {https://doi.org/10.6084/m9.figshare.31223503},
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
