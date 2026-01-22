# Manifest

## Validity-Aware AI: Complete File Listing

**Version:** 1.0  
**Date:** January 2026  
**DOI:** 10.6084/m9.figshare.31122970

---

## Documentation (`docs/`)

### Markdown (Human-readable)

| File | Description |
|------|-------------|
| `paper_A_entropy_validity_regimes.md` | Section A: Mathematical foundation, entropy definitions, L0–L3 mapping |
| `paper_B_regime_aware_rag.md` | Section B: RAG architecture, EBE filter, response protocols |
| `paper_C_beyond_the_black_box.md` | Section C: Implications, accountability, deployment standards |
| `paper_unified_architecture_statement.md` | Canonical reference for EFC/EBE/L0–L3/Validity-Aware AI integration |

### LaTeX (Publication-ready)

| File | Description |
|------|-------------|
| `validity_aware_ai_A.tex` | Section A in LaTeX format |
| `validity_aware_ai_B.tex` | Section B in LaTeX format |
| `validity_aware_ai_C.tex` | Section C in LaTeX format |
| `validity_aware_ai_unified.tex` | Unified Architecture Statement in LaTeX |

---

## Source Code (`src/`)

| File | Description |
|------|-------------|
| `ebe_filter.py` | Core EBE filter implementation |
| `entropy_measures.py` | Entropy computation (node, edge, structural, retrieval) |
| `regime_classifier.py` | L1/L2/L3 regime classification |
| `response_protocols.py` | Protocol engine and LLM constraints |

---

## Data (`data/`)

| File | Description |
|------|-------------|
| `regime_definitions.json` | Machine-readable L0–L3 specifications |
| `domain_thresholds.json` | Example threshold configurations |

---

## Examples (`examples/`)

| File | Description |
|------|-------------|
| `regime_detection_example.py` | Basic usage example |

---

## Root Files

| File | Description |
|------|-------------|
| `README.md` | Project overview and documentation |
| `QUICKSTART.md` | Getting started guide |
| `MANIFEST.md` | This file |
| `LICENSE` | CC BY 4.0 license text |
| `CITATION.cff` | Citation metadata |

---

## Dependencies

This framework is designed to integrate with:

- **Neo4j** (knowledge graph)
- **Qdrant** (vector store)
- **Any LLM API** (OpenAI, Anthropic, local models)

See `QUICKSTART.md` for installation instructions.

---

## Related Repositories

- [EFC](https://github.com/supertedai/EFC) - Energy-Flow Cosmology main repository
- [L0–L3 Regime Architecture](https://doi.org/10.6084/m9.figshare.31112536) - Foundational regime definitions
- [Symbiosis](https://doi.org/10.6084/m9.figshare.30773684) - Human–AI co-reflection architecture
