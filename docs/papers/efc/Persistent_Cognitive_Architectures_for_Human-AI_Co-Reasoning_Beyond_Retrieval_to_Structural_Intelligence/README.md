# Persistent Cognitive Architectures for Human-AI Co-Reasoning

**Beyond Retrieval to Structural Intelligence**

[![DOI](https://img.shields.io/badge/DOI-10.6084%2Fm9.figshare.31271707-blue)](https://doi.org/10.6084/m9.figshare.31271707)
[![License](https://img.shields.io/badge/License-CC--BY--4.0-green)](LICENSE)

## Overview

This package documents **Symbiose**, a cognitive architecture that combines graph-based causal reasoning, temporal pattern recognition, and proactive autonomy to enable persistent, evolving collaboration between humans and AI.

**Key Innovation**: Unlike RAG (retrieval-augmented generation) which is reactive and stateless, Symbiose enables genuine co-reasoning through:
- **Quantum Leap (QL)**: Persistent cognitive orchestration layer
- **L0–L3 Epistemic Framework**: Distinguishing facts from inferences
- **Graph-Vector Fusion**: Semantic + structural reasoning
- **Hierarchical Memory**: Cross-session pattern recognition

## The Architectural Shift

| Traditional AI | Symbiose/QL Architecture |
|----------------|--------------------------|
| Response-based | Initiative-based |
| Stateless | Persistent |
| RAG retrieval | Structural + temporal |
| Query → answer | Context → anticipation |

## Core Components

### 1. Quantum Leap (QL) Orchestration Layer

Seven integrated components:

```
┌─────────────┐    ┌─────────────┐
│   Session   │    │  Embedding  │
│   Context   │◄──►│   Scorer    │
└──────┬──────┘    └──────┬──────┘
       │                  │
       ▼                  ▼
┌─────────────┐    ┌─────────────┐
│ Graph-Vector│    │ Preference  │
│   Fusion    │◄──►│   Learn     │
└──────┬──────┘    └──────┬──────┘
       │                  │
       ▼                  ▼
┌─────────────┐    ┌─────────────┐
│  Emergent   │    │   Causal    │
│   Reason    │◄──►│ Understand  │
└──────┬──────┘    └──────┬──────┘
       │                  │
       └────────┬─────────┘
                ▼
       ┌─────────────┐
       │ Continuous  │
       │   Memory    │
       └─────────────┘
```

### 2. L0–L3 Epistemic Framework

```
┌────────────────────────────────────┐
│ L0 Canonical                       │ ◄── Ground truth, verified
│ Known with certainty               │
└───────────────┬────────────────────┘
                │ derives
                ▼
┌────────────────────────────────────┐
│ L1 Derived                         │ ◄── Logical from L0
│ True given L0 premises             │
└───────────────┬────────────────────┘
                │ supports
                ▼
┌────────────────────────────────────┐
│ L2 Supported                       │ ◄── Evidence-backed
│ Probable given evidence            │
└───────────────┬────────────────────┘
                │ infers
                ▼
┌────────────────────────────────────┐
│ L3 Inferred                        │ ◄── LLM hypothesis
│ Plausible but unverified           │
└────────────────────────────────────┘
```

### 3. Graph-Vector Fusion Algorithm

```python
def graph_vector_fusion(query, k):
    # Step 1: Vector retrieval (Qdrant)
    V = vector_search(query, k)

    # Step 2: Graph expansion (Neo4j)
    G = set()
    for chunk in V:
        concepts = extract_concepts(chunk)
        for concept in concepts:
            paths = neo4j_find_paths(query, concept, max_depth=3)
            G.update(paths)

    # Step 3: Fusion scoring
    for result in V:
        s_semantic = result.score
        s_structural = max(1/len(p) for p in G if result in p)
        result.fused_score = 0.6 * s_semantic + 0.4 * s_structural

    return sorted(V, key=lambda r: r.fused_score, reverse=True)
```

### 4. Hierarchical Memory Consolidation

```
Monthly Themes ◄─abstract─ Weekly Summaries ◄─abstract─ Daily Logs ◄─abstract─ Raw Conversations
```

## Case Study: Energy-Flow Cosmology

Symbiose was deployed for 12 months to develop EFC theory.

### System Growth

| Metric | Initial | Final |
|--------|---------|-------|
| Graph nodes | 593,000 | 602,000 |
| Causal relations | — | 2,160 |
| Synthetic insights | — | 47 |

### Temporal Pattern Emergence

- **Week 1–4**: Conceptual exploration (entropy gradients, energy flow)
- **Week 5–12**: Hypothesis generation (testable predictions)
- **Week 13–20**: Observational test design (Bullet Cluster, galaxy formation)
- **Week 21+**: Refinement based on literature review

### Evaluation Results

| Metric | Symbiose | GPT-4 (stateless) | RAG alone |
|--------|----------|-------------------|-----------|
| Causal reasoning accuracy | **94%** | 76% | 68% |
| Memory query (monthly summary) | **0.3s** | N/A | 4.2s |
| Proactive suggestion acceptance | 73.5% | N/A | N/A |

## Technology Stack

- **Graph Database**: Neo4j 5.x
- **Vector Store**: Qdrant 1.7.x
- **LLM Layer**: GPT-4o, Claude Sonnet 4.5
- **Backend**: Python 3.11, FastAPI
- **Embedding Model**: OpenAI text-embedding-3-large

## Graph Schema

**Node Types:**
- `Concept`: Ideas, entities, theories
- `Evidence`: Supporting data, observations
- `Prediction`: Testable hypotheses
- `SyntheticInsight`: LLM-generated patterns
- `Memory`: Consolidated summaries (daily/weekly/monthly)

**Relationship Types:**
- `CAUSES`: Causal relationships (confidence-weighted)
- `RELATES_TO`: Semantic associations
- `SUPPORTS`: Evidence backing claims
- `PREDICTS`: Hypothesis derivation
- `CONSOLIDATES`: Memory hierarchy

## Proactive Trigger Types

1. **Temporal**: "X days since last Y" (threshold-based)
2. **Evidence gap**: "Claim without support" (Neo4j query-based)
3. **Pattern**: "Recurring topic" (frequency-based)
4. **Causal**: "Change may affect downstream" (graph traversal-based)

## Key Distinction: This is NOT AGI

Symbiose is a **cognitive architecture for collaboration**, not artificial general intelligence:

- **Domain-bounded**: Operates within specific knowledge domains
- **Human-in-the-loop**: Requires human judgment for hypothesis formation
- **No autonomous goal-setting**: Responds to and anticipates user needs
- **Explainable by design**: All reasoning chains are traceable

## Citation

```bibtex
@article{magnusson2026symbiose,
  title={Persistent Cognitive Architectures for Human-AI Co-Reasoning:
         Beyond Retrieval to Structural Intelligence},
  author={Magnusson, Morten},
  year={2026},
  month={February},
  doi={10.6084/m9.figshare.31271707}
}
```

## License

This work is licensed under [CC-BY-4.0](LICENSE).
