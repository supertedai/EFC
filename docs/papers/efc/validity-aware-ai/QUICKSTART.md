# Quick Start Guide

## Validity-Aware AI: Getting Started

This guide shows how to implement regime-aware inference in your RAG system.

## Prerequisites

- Python 3.9+
- Neo4j 4.4+ (knowledge graph)
- Qdrant (vector store)
- An LLM API (OpenAI, Anthropic, etc.)

## Installation

```bash
# Clone the repository
git clone https://github.com/supertedai/validity-aware-ai.git
cd validity-aware-ai

# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

### 1. Initialize Components

```python
from src.ebe_filter import EBEFilter
from src.regime_classifier import RegimeClassifier
from src.response_protocols import ProtocolEngine

# Connect to your datastores
graph_client = Neo4jClient(uri, user, password)
vector_client = QdrantClient(host, port)

# Initialize the EBE filter
ebe_filter = EBEFilter(
    graph_client=graph_client,
    vector_client=vector_client
)

# Initialize regime classifier with domain thresholds
classifier = RegimeClassifier(
    theta_L1=0.3,  # Upper bound for L1
    theta_L2=0.7   # Upper bound for L2
)

# Initialize protocol engine
protocols = ProtocolEngine()
```

### 2. Process a Query

```python
def process_query(query: str) -> dict:
    # Step 1: Standard RAG retrieval
    query_vector = embed(query)
    retrieved_chunks = vector_client.search(query_vector, limit=10)
    
    # Step 2: Graph enrichment
    subgraph = graph_client.get_relevant_subgraph(query)
    
    # Step 3: Compute entropy (THE KEY STEP)
    entropy_result = ebe_filter.compute_entropy(
        subgraph=subgraph,
        retrieved_chunks=retrieved_chunks
    )
    
    # Step 4: Classify regime
    regime, confidence = classifier.classify(entropy_result)
    
    # Step 5: Get response protocol
    protocol = protocols.get_protocol(regime)
    
    # Step 6: Generate with constraints
    response = llm.generate(
        query=query,
        context=retrieved_chunks,
        system_prompt=protocol.system_prompt,
        constraints=protocol.constraints
    )
    
    return {
        "response": response,
        "regime": regime.name,
        "confidence": confidence,
        "entropy": entropy_result
    }
```

### 3. Response Protocols

The system automatically applies different protocols based on regime:

**L1 (Stable Domain)**
```python
# No special constraints - standard generation
response = llm.generate(query, context)
```

**L2 (Contested Domain)**
```python
# Must include uncertainty, cite conflicts
system_prompt = """
EPISTEMIC CONSTRAINT: This query falls in regime L2.
- Do not make unqualified assertions
- Present competing interpretations
- Include uncertainty estimates
- Maximum confidence level: 70%
"""
```

**L3 (Archival Mode)**
```python
# Historical only, no predictions
system_prompt = """
EPISTEMIC CONSTRAINT: This query is in regime L3.
- Provide only historical information
- Frame all responses as "As of [date]..."
- Do NOT make predictions
"""
```

## Configuration

### Domain Thresholds

Create `data/domain_thresholds.json`:

```json
{
  "default": {
    "L1_upper": 0.3,
    "L2_upper": 0.7
  },
  "medical": {
    "L1_upper": 0.2,
    "L2_upper": 0.5
  },
  "product_catalog": {
    "L1_upper": 0.4,
    "L2_upper": 0.8
  }
}
```

### Entropy Weights

Adjust component weights in `src/entropy_measures.py`:

```python
ENTROPY_WEIGHTS = {
    "edge": 0.3,
    "node": 0.25,
    "structural": 0.25,
    "retrieval": 0.2
}
```

## Integration with Existing RAG

To add regime awareness to an existing RAG system:

```python
# Your existing RAG pipeline
def existing_rag(query):
    chunks = retrieve(query)
    response = generate(query, chunks)
    return response

# Enhanced with regime awareness
def regime_aware_rag(query):
    chunks = retrieve(query)
    
    # ADD: Entropy measurement
    entropy = compute_entropy(query, chunks)
    regime = classify_regime(entropy)
    
    # ADD: Protocol selection
    protocol = get_protocol(regime)
    
    # MODIFY: Constrained generation
    response = generate(query, chunks, protocol=protocol)
    
    # ADD: Epistemic metadata
    return {
        "response": response,
        "regime": regime,
        "entropy": entropy
    }
```

## Logging and Auditing

Enable regime logging for accountability:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("regime_audit")

def log_regime_decision(query_id, entropy, regime, response):
    logger.info({
        "query_id": query_id,
        "timestamp": datetime.now().isoformat(),
        "entropy_total": entropy["total"],
        "entropy_components": entropy["components"],
        "regime": regime.name,
        "protocol_applied": regime.protocol,
        "response_length": len(response)
    })
```

## Next Steps

1. **Calibrate thresholds** for your specific domain
2. **Implement user-facing indicators** (see Section C)
3. **Set up audit logging** for accountability
4. **Run validation** on known high/low entropy queries

## Troubleshooting

**High false-positive L2 classifications?**
- Increase `theta_L1` threshold
- Check if graph has many low-confidence edges

**System defaulting to L2 too often?**
- Review entropy component weights
- Ensure graph is well-maintained

**Performance issues?**
- Cache entropy computations for stable subgraphs
- Reduce subgraph traversal depth

---

For detailed documentation, see `docs/paper_B_regime_aware_rag.md`.
