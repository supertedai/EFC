# Validity-Aware AI: An Entropy-Bounded Architecture for Regime-Sensitive Inference

## B. Regime-Aware RAG

**Architecture and Implementation Logic for Validity-Sensitive Retrieval**

*DOI: 10.6084/m9.figshare.31122970*

*Building on: Section A (Entropy, Validity, and Regimes) and Magnusson, M. (2025). Symbiosis Architecture. DOI: 10.6084/m9.figshare.30773684*

---

## B.1 Introduction

Section A established that inference validity is regime-dependent: a system operating in L1 (stable, low-entropy) can make confident predictions, while a system in L2 (complex, high-entropy) must quantify uncertainty, and a system approaching L3 must refuse predictive claims entirely.

This section shows **how to build this into a RAG architecture**.

The core architectural claim is:

> **Retrieval without regime context is epistemically irresponsible in complex domains.**

Standard RAG retrieves relevant documents and feeds them to an LLM. It does not ask: *"Is this domain stable enough for confident inference?"* Regime-Aware RAG asks this question before every generation.

---

## B.2 The Problem with Standard RAG

### B.2.1 The Standard Pipeline

A conventional RAG system operates as follows:

```
Query → Embed → Vector Search → Top-k Retrieval → LLM Generation → Output
```

This pipeline optimizes for **relevance**: finding documents that match the query semantically. It does not optimize for **validity**: whether the retrieved information supports reliable inference.

### B.2.2 What Standard RAG Cannot Do

1. **Detect contradictions**: If retrieved documents contain conflicting claims, the LLM receives both without warning
2. **Measure domain stability**: No mechanism exists to assess whether the knowledge domain is contested or settled
3. **Modulate confidence**: The LLM generates with the same rhetorical certainty regardless of underlying uncertainty
4. **Refuse gracefully**: No architectural pathway exists for "I cannot reliably answer this"

### B.2.3 The Consequence

Standard RAG compensates for epistemic uncertainty with **linguistic fluency**. When the retrieved context is contradictory or incomplete, the LLM produces:

- More text (to appear thorough)
- More hedging words (to appear cautious)
- More confident rhetoric (to appear authoritative)

This is not safety. This is **cosmetic uncertainty**—surface-level caveats that do not reflect structural epistemic limits.

---

## B.3 Regime-Aware RAG Architecture

### B.3.1 The Extended Pipeline

Regime-Aware RAG inserts an **EBE filter** between retrieval and generation:

```
Query → Embed → Vector Search → Top-k Retrieval
                                      ↓
                              Graph Enrichment (Neo4j)
                                      ↓
                              EBE Regime Filter ← ℋ(G) measurement
                                      ↓
                              Regime Classification (L1/L2/L3)
                                      ↓
                              Response Protocol Selection
                                      ↓
                              LLM Generation (regime-constrained)
                                      ↓
                              Output (with epistemic metadata)
```

### B.3.2 Component Specification

#### Vector Store (Qdrant)

- Standard semantic retrieval
- Returns top-k chunks with similarity scores
- **Extended**: Each chunk carries metadata including `confidence`, `source_authority`, `timestamp`, `contradiction_flags`

#### Knowledge Graph (Neo4j)

- Stores concepts, relationships, and their properties
- Tracks relationship confidence, provenance, and temporal validity
- **Extended**: Supports entropy queries—edge variance, node disagreement, model divergence

#### EBE Regime Filter

The core innovation. This component:

1. Extracts the **relevant subgraph** for the query
2. Computes **local entropy** ℋ(G) using metrics from A.2.3
3. Classifies the query into **L1, L2, or L3**
4. Selects the appropriate **response protocol**

#### Response Protocol Engine

Maps regime classification to output behavior:

| Regime | Protocol | LLM Constraints |
|--------|----------|-----------------|
| L1 | Standard | Full generation, confidence allowed |
| L2 | Uncertainty-aware | Must include probability estimates, cite conflicts |
| L2→L3 | Degraded | Point estimates forbidden, explicit warning required |
| L3 | Archival | Historical retrieval only, "as of [date]" framing mandatory |

---

## B.4 The EBE Filter in Detail

### B.4.1 Input

- Query vector (from embedding)
- Retrieved chunks (from vector search)
- Relevant subgraph (from Neo4j traversal)

### B.4.2 Entropy Computation

```python
def compute_regime_entropy(subgraph, retrieved_chunks):
    """
    Compute ℋ(G) for the query-relevant knowledge structure.
    Returns entropy score and component breakdown.
    """
    # Edge entropy: variance in relationship confidence
    edge_confidences = [e.confidence for e in subgraph.edges]
    H_edges = compute_variance_entropy(edge_confidences)
    
    # Node entropy: disagreement in concept definitions
    node_definitions = [n.definitions for n in subgraph.nodes]
    H_nodes = compute_definition_divergence(node_definitions)
    
    # Structural entropy: instability in graph topology
    temporal_snapshots = get_graph_history(subgraph, window=30)  # days
    H_structural = compute_topology_drift(temporal_snapshots)
    
    # Retrieval entropy: contradiction in retrieved chunks
    H_retrieval = compute_chunk_contradiction(retrieved_chunks)
    
    # Combined entropy (weighted)
    H_total = (
        W_EDGE * H_edges +
        W_NODE * H_nodes +
        W_STRUCT * H_structural +
        W_RETRIEVAL * H_retrieval
    )
    
    return {
        'total': H_total,
        'components': {
            'edge': H_edges,
            'node': H_nodes,
            'structural': H_structural,
            'retrieval': H_retrieval
        }
    }
```

### B.4.3 Regime Classification

```python
def classify_regime(entropy_result, domain_thresholds):
    """
    Map entropy to regime.
    Thresholds are domain-calibrated, not universal.
    """
    H = entropy_result['total']
    
    # Domain-specific thresholds (example: scientific literature)
    theta_L1 = domain_thresholds.get('L1_upper', 0.3)
    theta_L2 = domain_thresholds.get('L2_upper', 0.7)
    
    if H < theta_L1:
        return Regime.L1, confidence=1.0 - H
    
    elif H < theta_L2:
        # L2: compute confidence as distance from boundaries
        confidence = 1.0 - (H - theta_L1) / (theta_L2 - theta_L1)
        return Regime.L2, confidence
    
    else:
        # Approaching L3: epistemic collapse imminent
        return Regime.L3_WARNING, confidence=0.0
```

### B.4.4 Output

The EBE filter returns:

```json
{
  "regime": "L2",
  "confidence": 0.62,
  "entropy": {
    "total": 0.48,
    "components": {
      "edge": 0.35,
      "node": 0.52,
      "structural": 0.41,
      "retrieval": 0.64
    }
  },
  "warnings": [
    "High retrieval contradiction detected",
    "Node definitions show significant divergence"
  ],
  "protocol": "uncertainty_aware",
  "constraints": {
    "point_estimates": false,
    "require_citations": true,
    "require_conflict_disclosure": true,
    "confidence_ceiling": 0.7
  }
}
```

---

## B.5 Response Protocol Implementation

### B.5.1 L1 Protocol (Standard)

When ℋ(G) < θ_L1:

- LLM generates normally
- Confidence statements permitted
- No special constraints

**System prompt addition**: *None required*

### B.5.2 L2 Protocol (Uncertainty-Aware)

When θ_L1 ≤ ℋ(G) < θ_L2:

- LLM must acknowledge competing interpretations
- Point estimates must include uncertainty ranges
- Conflicting sources must be cited explicitly
- Confidence ceiling enforced (e.g., max 70%)

**System prompt addition**:
```
EPISTEMIC CONSTRAINT: This query falls in regime L2 (contested domain).
- Do not make unqualified assertions
- Present competing interpretations where they exist
- Include uncertainty estimates for any quantitative claims
- Maximum confidence level: 70%
- Cite sources that disagree with each other explicitly
```

### B.5.3 L2→L3 Protocol (Degraded)

When ℋ(G) approaches θ_L2:

- Point estimates forbidden
- Must explicitly warn user of epistemic instability
- Suggest alternative query strategies
- Offer to explain *why* confidence is low

**System prompt addition**:
```
EPISTEMIC CONSTRAINT: This query approaches regime L3 (epistemic collapse).
- Do NOT provide point estimates or confident answers
- Explain why the knowledge domain is unstable
- Offer to retrieve historical information instead
- Suggest ways the user could narrow their query
```

### B.5.4 L3 Protocol (Archival)

When ℋ(G) ≥ θ_L2 or domain is marked inactive:

- Retrieval-only mode
- All responses framed as historical
- No predictive claims permitted
- Explicit "as of [date]" framing

**System prompt addition**:
```
EPISTEMIC CONSTRAINT: This query is in regime L3 (archival mode).
- Provide only historical information
- Frame all responses as "As of [date], the knowledge base indicated..."
- Do NOT make predictions or current-state claims
- Explain that this domain is no longer actively maintained
```

---

## B.6 Hallucination Prevention

### B.6.1 The Mechanism

Standard RAG allows hallucination because it has no pre-generation validity check. The LLM receives context and generates—regardless of whether that context supports reliable inference.

Regime-Aware RAG prevents hallucination **structurally**:

1. **Before generation**: Entropy is measured, regime is classified
2. **During generation**: System prompt constrains output based on regime
3. **After generation**: Output is validated against regime constraints

Hallucination in high-entropy domains becomes a **protocol violation**, not just a quality issue.

### B.6.2 What This Does NOT Solve

Regime-Aware RAG does not prevent:

- Factual errors within L1 domains (knowledge may still be wrong)
- Subtle reasoning errors (logic can fail regardless of regime)
- Adversarial manipulation (prompt injection remains a separate problem)

It prevents: **confident outputs in uncertain domains**.

---

## B.7 Integration with Symbiosis Architecture

### B.7.1 Where EBE Fits

The Symbiosis architecture (Magnusson 2025) provides:

- **Neo4j**: Knowledge graph for structural memory
- **Qdrant**: Vector store for semantic retrieval
- **Unified API**: Abstraction layer for retrieval and logging
- **Reflection Layer**: Metacognitive tracking

Regime-Aware RAG extends this with:

- **EBE Filter**: Entropy measurement and regime classification
- **Protocol Engine**: Response constraint enforcement
- **Epistemic Metadata**: Regime classification in logs

### B.7.2 The Extended Operational Loop

```
1. Human prompt
2. Context retrieval (Qdrant + Neo4j)
3. EBE regime classification          ← NEW
4. Protocol selection                  ← NEW
5. LLM generation (regime-constrained) ← MODIFIED
6. Structured logging (with regime)    ← EXTENDED
7. Graph/vector update
8. Feedback tagging
```

The loop remains human-centered. The EBE filter does not make decisions—it provides epistemic metadata that shapes how the system responds.

---

## B.8 Implementation Considerations

### B.8.1 Threshold Calibration

Domain-specific thresholds (θ_L1, θ_L2) require empirical calibration:

1. **Baseline measurement**: Compute entropy across known-stable queries
2. **Failure analysis**: Identify queries where standard RAG produced incorrect/overconfident outputs
3. **Threshold tuning**: Adjust until regime classification matches observed validity

This is not a weakness—it is an explicit acknowledgment that epistemic boundaries are domain-dependent.

### B.8.2 Performance Overhead

The EBE filter adds latency:

- Graph traversal: ~50-200ms (depending on subgraph size)
- Entropy computation: ~10-50ms
- Protocol selection: <5ms

Total overhead: **60-250ms per query**. Acceptable for most applications; may require optimization for real-time systems.

### B.8.3 Graceful Degradation

If the EBE filter fails (Neo4j unavailable, computation timeout):

- Default to L2 protocol (conservative)
- Log the failure
- Continue with uncertainty-aware generation

The system should never fail silently into L1.

---

## B.9 Relation to Existing Approaches

### B.9.1 What This Is NOT

- **Not calibration**: We are not adjusting model confidence after training
- **Not uncertainty quantification**: We are not computing Bayesian posteriors
- **Not explainability**: We are not explaining why the model produced an output

### B.9.2 What This IS

- **Pre-generation validity assessment**: Measuring epistemic conditions before output
- **Architectural constraint**: Building validity awareness into the pipeline
- **Regime-sensitive response**: Changing output behavior based on domain state

The goal is not to make the LLM more accurate. The goal is to make the system **honest about its limits**.

---

## B.10 Summary

Section B establishes the **architectural implementation** of regime-aware inference:

1. **Standard RAG is epistemically blind**: It retrieves and generates without validity assessment
2. **The EBE filter measures entropy** in the relevant knowledge subgraph
3. **Regime classification** (L1/L2/L3) determines response protocol
4. **Response protocols constrain generation** based on epistemic conditions
5. **Hallucination becomes a protocol violation**, not just a quality issue

The following section (C) examines the broader implications: what it means to build AI systems that know where they fail.

---

## References

Magnusson, M. (2026). L0–L3 Regime Architecture in Entropy-Bounded Empiricism. Figshare. https://doi.org/10.6084/m9.figshare.31112536

Magnusson, M. (2025). Symbiosis: A Human–AI Co-Reflection Architecture Using Graph–Vector Memory for Long-Horizon Thinking. Figshare. https://doi.org/10.6084/m9.figshare.30773684

---

*Section B of: "Validity-Aware AI: An Entropy-Bounded Architecture for Regime-Sensitive Inference" (DOI: 10.6084/m9.figshare.31122970)*
