# Validity-Aware AI: An Entropy-Bounded Architecture for Regime-Sensitive Inference

## A. Entropy, Validity, and Regimes

**Extending L0–L3 Regime Architecture to Knowledge-Graph Inference**

*DOI: 10.6084/m9.figshare.31122970*

*Building on: Magnusson, M. (2026). L0–L3 Regime Architecture in Entropy-Bounded Empiricism. DOI: 10.6084/m9.figshare.31112536*

---

## A.1 Introduction

The L0–L3 regime architecture establishes a foundational principle: **inference is valid only within the regime where data and dynamics remain consistent**. This principle was developed in the context of Energy-Flow Cosmology (EFC) and validated against 175 galaxy rotation curves (SPARC175), where regime-dependent model validity was demonstrated with p < 0.0001.

This section extends the framework to **knowledge-graph-based AI systems**, demonstrating that the same epistemological constraints apply to inference over structured information. The core insight is:

> **Model validity is a function of measurable entropy in the knowledge structure, not of model complexity or training volume.**

---

## A.2 Entropy in Knowledge Graphs

### A.2.1 Definition

For a knowledge graph G = (V, E) where V is a set of nodes (concepts, facts, entities) and E is a set of edges (relationships), we define **graph entropy** as:

$$\mathcal{H}(G) = \mathcal{H}_V + \mathcal{H}_E + \mathcal{H}_{VE}$$

Where:

**Node entropy** (uncertainty in concept definitions):
$$\mathcal{H}_V = -\sum_{v \in V} p(v) \log p(v)$$

**Edge entropy** (uncertainty in relationships):
$$\mathcal{H}_E = -\sum_{e \in E} p(e) \log p(e)$$

**Structural entropy** (uncertainty in graph topology):
$$\mathcal{H}_{VE} = -\sum_{(v,e) \in G} p(v,e) \log p(v|e)$$

### A.2.2 Interpretation

- **Low entropy** (ℋ(G) → 0): The graph represents a well-defined, internally consistent domain. Relationships are unambiguous. Inference is reliable.

- **High entropy** (ℋ(G) → 1): The graph contains contradictions, contested relationships, or domains where multiple incompatible models coexist. Inference becomes unreliable.

**Note on scaling**: ℋ(G) is normalized relative to domain baseline. Thresholds (θ) are calibrated per domain, not universal constants. A medical knowledge graph may have different baseline entropy than a product catalog—what matters is deviation from stable operating range, not absolute value.

### A.2.3 Practical Measurement

In operational systems (e.g., Symbiosis architecture), entropy can be estimated through:

1. **Edge variance**: Standard deviation of confidence scores across edges of the same type
2. **Node disagreement**: Number of conflicting properties or definitions per concept
3. **Model disagreement**: Divergence between predictions from different embedded models
4. **Temporal instability**: Rate of change in graph structure over time

---

## A.3 Regime Definitions for Knowledge Graphs

The L0–L3 architecture maps directly to knowledge-graph-based inference:

### L0 — Latent (Configuration Space)

The graph contains **potential structure** but no active inference dynamics.

- Graph exists as schema or template
- No queries are being processed
- Relationships are defined but not traversed
- **Inference validity**: None (system inactive)

### L1 — Stable Active (Predictable Inference)

The graph operates in a **low-entropy, well-defined domain**.

- Relationships are consistent and uncontested
- Historical patterns reliably predict current queries
- Linear approximations and cached inferences remain valid
- **Inference validity**: High confidence, reliable extrapolation within domain

**Example**: Querying a product catalog with fixed relationships (product → category → price)

### L2 — Complex Active (Non-Linear Dynamics)

The graph contains **contested relationships, emerging patterns, or cross-domain tensions**.

- Multiple valid interpretations coexist
- Local sensitivity: small changes in input produce large changes in output
- Historical models begin to diverge from observed patterns
- **Inference validity**: Requires explicit uncertainty quantification; point estimates unreliable

**Example**: Querying scientific literature where competing theories explain the same phenomenon

### L3 — Residual (Structure Without Process)

The graph contains **historical structure** but active dynamics have ceased.

- Information is frozen; no new edges or updates
- Queries return historical snapshots, not current state
- Structure preserves what was, not what is
- **Inference validity**: Historical reconstruction only; active prediction invalid

**Operational mode**: L3 is not "do nothing"—it is **retrieval without projection**. The system can still answer "what did we know then?" but must refuse "what should we expect now?" This read-only epistemic mode preserves value while preventing invalid extrapolation.

**Example**: A deprecated knowledge base from a discontinued project

---

## A.4 The Regime Transition Function

### A.4.1 L1 → L2 Transition

The critical transition for AI safety occurs when a knowledge domain **exits the stable regime**:

$$L1 \rightarrow L2 \quad \text{when} \quad \mathcal{H}(G) > \theta_{\text{critical}}$$

Where θ_critical is a domain-dependent threshold. 

**Phase-extended transition**: This crossing is not instantaneous. The uncertainty regime grows before collapse becomes observable. A system may operate in a **transition zone** where L1 inference is degrading but L2 protocols have not yet engaged. Detecting this zone—not just the boundary—is critical for early warning.

This transition is characterized by:

1. **Edge variance exceeds baseline**: Confidence scores on relationships diverge
2. **Model disagreement emerges**: Different inference paths produce contradictory results
3. **Temporal instability increases**: Graph structure changes faster than models can adapt

### A.4.2 Detection Algorithm (Pseudocode)

```python
def detect_regime_transition(graph, query_context):
    """
    Detect whether inference should proceed in L1 or L2 mode.
    Returns regime classification and confidence.
    """
    # Measure local entropy around query
    subgraph = extract_relevant_subgraph(graph, query_context)
    
    H_nodes = compute_node_entropy(subgraph)
    H_edges = compute_edge_entropy(subgraph)
    H_structural = compute_structural_entropy(subgraph)
    
    H_total = H_nodes + H_edges + H_structural
    
    # Check for regime indicators
    edge_variance = compute_edge_variance(subgraph)
    model_disagreement = compute_model_disagreement(subgraph, query_context)
    temporal_drift = compute_temporal_drift(subgraph)
    
    # Regime classification
    if H_total < THETA_L1_UPPER and edge_variance < VARIANCE_THRESHOLD:
        return Regime.L1, confidence=1.0 - H_total
    
    elif H_total < THETA_L2_UPPER:
        return Regime.L2, confidence=estimate_l2_confidence(H_total, model_disagreement)
    
    else:
        return Regime.L3_WARNING, confidence=0.0  # Approaching collapse
```

### A.4.3 System Response by Regime

| Regime | System Behavior | Output Characteristics |
|--------|-----------------|----------------------|
| L1 | Standard inference | Point estimates, high confidence |
| L2 | Uncertainty-aware inference | Probability distributions, explicit caveats |
| L2→L3 boundary | Inference degradation | Refusal to generate point estimates, explicit collapse warning |
| L3 | Historical retrieval only | No predictive claims, archival mode |

---

## A.5 Why This Matters for AI

### A.5.1 The Problem with Current Systems

Standard LLMs and RAG systems are **epistemically blind**:

- They generate outputs regardless of domain entropy
- They compensate for uncertainty with **more text, more coherence, more confident rhetoric**
- They have no mechanism to detect regime boundaries
- They cannot degrade their own epistemic status

This is the operational definition of **hallucination**: generating high-confidence outputs in high-entropy domains.

### A.5.2 The EBE Solution

Entropy-Bounded Empiricism provides a structural alternative:

1. **Pre-inference entropy measurement**: Before generating any output, measure ℋ(G) in the relevant subgraph
2. **Regime classification**: Determine whether the query falls in L1, L2, or L3
3. **Response modulation**: Adjust output format, confidence, and caveats based on regime
4. **Collapse detection**: Refuse to generate point estimates when approaching L2→L3 boundary

### A.5.3 The Core Claim

> A system that does not know where it fails is more dangerous than a system that fails often.

The goal is not to eliminate failure. The goal is to make failure **detectable and predictable**.

---

## A.6 Relation to Existing Work

### A.6.1 Builds On

- **L0–L3 Regime Architecture** (Magnusson 2026): Foundational regime definitions and transition logic
- **Symbiosis Architecture** (Magnusson 2025): Graph-vector hybrid memory for long-horizon reasoning
- **SPARC175 Validation** (EBE-SPARC175): Statistical demonstration of regime-dependent validity

### A.6.2 Extends Beyond

This section introduces:

1. **Formal entropy definitions** for knowledge graphs (not physical systems)
2. **Detection algorithm** for regime transitions in inference
3. **System response protocol** linking entropy to output behavior

### A.6.3 Does Not Claim

- Universal applicability without domain calibration
- Automatic threshold determination (θ_critical requires empirical tuning)
- Replacement of domain expertise (EBE constrains inference, does not replace understanding)

---

## A.7 Summary

Section A establishes the **mathematical and epistemological foundation** for regime-aware AI:

1. **Entropy in knowledge graphs** is measurable through node, edge, and structural components
2. **L0–L3 regimes** map directly to inference validity in AI systems
3. **Regime transitions** are detectable through entropy thresholds and model disagreement
4. **System response** must change based on regime—this is not optional, it is epistemically required

The following sections (B, C) show how this foundation translates into:
- **B**: Concrete architecture (Regime-Aware RAG)
- **C**: Broader implications (Beyond the Black Box)

---

## References

Magnusson, M. (2026). L0–L3 Regime Architecture in Entropy-Bounded Empiricism. Figshare. https://doi.org/10.6084/m9.figshare.31112536

Magnusson, M. (2025). Symbiosis: A Human–AI Co-Reflection Architecture Using Graph–Vector Memory for Long-Horizon Thinking. Figshare. https://doi.org/10.6084/m9.figshare.30773684

Magnusson, M. (2026). Entropy-Bounded Empiricism: SPARC175 Complete Documentation. GitHub/EFC.

---

*Section A of: "Validity-Aware AI: An Entropy-Bounded Architecture for Regime-Sensitive Inference" (DOI: 10.6084/m9.figshare.31122970)*
