# Validity-Aware AI

**An Entropy-Bounded Architecture for Regime-Sensitive Inference**

[![DOI](https://img.shields.io/badge/DOI-10.6084/m9.figshare.31122970-blue)](https://doi.org/10.6084/m9.figshare.31122970)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## Overview

This repository contains the complete framework for **Validity-Aware AI**, an architectural approach that enables AI systems to recognize and report their own epistemic limits. The framework extends Entropy-Bounded Empiricism (EBE) and the L0–L3 regime architecture to knowledge-graph-based inference systems.

### Core Principle

> **No system may generate confident claims outside the regime where such claims are empirically valid.**

### The Problem

Standard LLMs and RAG systems are **epistemically blind**:
- They generate outputs regardless of domain entropy
- They compensate for uncertainty with more text and confident rhetoric
- They have no mechanism to detect regime boundaries
- They cannot degrade their own epistemic status

This is the operational definition of **hallucination**: generating high-confidence outputs in high-entropy domains.

### The Solution

Validity-Aware AI introduces:
1. **Pre-inference entropy measurement** in knowledge structures
2. **Regime classification** (L1/L2/L3) before generation
3. **Response protocols** that constrain output based on epistemic conditions
4. **Hallucination as protocol violation**, not just quality issue

## Repository Structure

```
validity-aware-ai/
├── README.md                    # This file
├── QUICKSTART.md               # Getting started guide
├── MANIFEST.md                 # Complete file listing
├── LICENSE                     # CC BY 4.0
├── CITATION.cff                # Citation metadata
├── docs/
│   ├── paper_A_entropy_validity_regimes.md
│   ├── paper_B_regime_aware_rag.md
│   ├── paper_C_beyond_the_black_box.md
│   ├── paper_unified_architecture_statement.md
│   ├── validity_aware_ai_A.tex
│   ├── validity_aware_ai_B.tex
│   ├── validity_aware_ai_C.tex
│   └── validity_aware_ai_unified.tex
├── src/
│   ├── ebe_filter.py           # EBE regime filter implementation
│   ├── entropy_measures.py     # Entropy computation functions
│   ├── regime_classifier.py    # L1/L2/L3 classification
│   └── response_protocols.py   # Protocol enforcement
├── data/
│   ├── regime_definitions.json # Machine-readable regime specs
│   └── domain_thresholds.json  # Example threshold configurations
└── examples/
    └── regime_detection_example.py
```

## Document Overview

### Section A: Entropy, Validity, and Regimes
Mathematical and epistemological foundation. Defines entropy measures for knowledge graphs and maps L0–L3 regimes to inference validity.

### Section B: Regime-Aware RAG
Architectural implementation. Shows how to insert an EBE filter between retrieval and generation in RAG systems.

### Section C: Beyond the Black Box
Broader implications. Introduces epistemic honesty as a fourth dimension of AI safety and establishes accountability structures.

### Unified Architecture Statement
Canonical reference binding EFC, EBE, L0–L3, and Validity-Aware AI into a coherent framework.

## Key Concepts

### L0–L3 Regime Architecture

| Regime | State | Inference Validity |
|--------|-------|-------------------|
| L0 | Latent | None (system inactive) |
| L1 | Stable Active | High confidence, reliable |
| L2 | Complex Active | Requires uncertainty quantification |
| L3 | Residual | Historical retrieval only |

### Graph Entropy

$$\mathcal{H}(G) = \mathcal{H}_V + \mathcal{H}_E + \mathcal{H}_{VE}$$

Where:
- $\mathcal{H}_V$ = Node entropy (concept uncertainty)
- $\mathcal{H}_E$ = Edge entropy (relationship uncertainty)
- $\mathcal{H}_{VE}$ = Structural entropy (topology uncertainty)

### Regime Transition

$$L1 \rightarrow L2 \quad \text{when} \quad \mathcal{H}(G) > \theta_{\text{critical}}$$

Thresholds are domain-calibrated, not universal constants.

## Quick Start

```python
from src.ebe_filter import EBEFilter
from src.regime_classifier import classify_regime

# Initialize filter
ebe = EBEFilter(graph_client, vector_client)

# Classify regime for a query
entropy_result = ebe.compute_entropy(query, retrieved_chunks)
regime, confidence = classify_regime(entropy_result, domain_thresholds)

# Apply appropriate protocol
if regime == Regime.L1:
    # Standard generation
    response = llm.generate(query, context)
elif regime == Regime.L2:
    # Uncertainty-aware generation
    response = llm.generate(query, context, protocol="uncertainty_aware")
else:
    # Refuse or archive mode
    response = "Cannot provide reliable answer for this query."
```

## Related Work

This framework builds on:

- **L0–L3 Regime Architecture** ([DOI: 10.6084/m9.figshare.31112536](https://doi.org/10.6084/m9.figshare.31112536))
- **Symbiosis Architecture** ([DOI: 10.6084/m9.figshare.30773684](https://doi.org/10.6084/m9.figshare.30773684))
- **EBE-SPARC175 Validation** (GitHub/EFC)

## Citation

```bibtex
@techreport{magnusson2026validityaware,
  author = {Magnusson, Morten},
  title = {Validity-Aware AI: An Entropy-Bounded Architecture for Regime-Sensitive Inference},
  year = {2026},
  institution = {Independent Researcher},
  doi = {10.6084/m9.figshare.31122970},
  url = {https://doi.org/10.6084/m9.figshare.31122970}
}
```

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Author

**Morten Magnusson**  
ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)

---

*Part of the Energy-Flow Cosmology (EFC) research program.*
