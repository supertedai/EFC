# Structural Coherence Evaluation for Physical Theories

## A Theory-Agnostic Framework with Observation-Native Ontology and Self-Imposed Falsifiability

**Author:** Morten Magnusson
**Affiliation:** Symbiose Research, Sandnes, Norway
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)
**DOI:** [10.6084/m9.figshare.31293745](https://doi.org/10.6084/m9.figshare.31293745)
**License:** CC-BY-4.0

---

## Overview

A theory-agnostic evaluation framework for assessing structural coherence and falsifiability of physical theories. Introduces four operational principles and five structural metrics for cross-paradigm comparison without privileging any specific ontology.

---

## Four Principles

1. **Observation-Native Ontology (I):** Phenomena defined as measured observables
2. **Declared Structural Vulnerability (II):** Theories must specify forbidden patterns
3. **Priced Adaptation (III):** Survival through modification carries epistemic cost
4. **Primitive Transparency (IV):** Independent assumptions declared explicitly

## Five Metrics

1. Explanatory Compression: C = |tested phenomena| / |primitive assumptions|
2. Anomaly Burden: Mismatch Rate + Coverage Penalty
3. Model Plasticity: Variant proliferation, parameter growth, special-case rules
4. Layer Consistency: Mechanism unity, parameter coherence, transition smoothness
5. Forbidden Pattern Coverage: Effective coverage weighted by observational reach

---

## Quick Start

```python
from src.structural_coherence import SCEFramework, TheoryProfile

lcdm = TheoryProfile(name="LCDM", primitives=3, phenomena=6)
efc = TheoryProfile(name="EFC", primitives=2, phenomena=4, forbidden_patterns=5)

sce = SCEFramework()
comparison = sce.compare(lcdm, efc)
print(comparison)
```

---

## License

This work is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
