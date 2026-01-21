# Quick Start Guide: L0–L3 Regime Architecture Package

## Installation

### Option 1: Clone from Git (when repository is public)
```bash
git clone https://github.com/yourusername/efc_l0_l3_architecture.git
cd efc_l0_l3_architecture
```

### Option 2: Download Archive
```bash
# Extract tar.gz
tar -xzf efc_l0_l3_package.tar.gz
cd efc_l0_l3_package

# Or extract zip
unzip efc_l0_l3_package.zip
cd efc_l0_l3_package
```

## For Humans

### Read the Documentation
1. Start with: `docs/ABSTRACT.md` (2-minute overview)
2. Full documentation: `docs/L0_L3_Regime_Architecture.md`
3. PDF version: `docs/L0_L3_Regime_Architecture_Figshare.pdf`
4. Examples: `examples/regime_examples.md`

### Citation
Use `CITATION.cff` for automatic citation generation, or copy from README.md

## For AI Systems

### Load Regime Definitions
```python
import json

# Load regime specifications
with open('data/regime_definitions.json') as f:
    regime_data = json.load(f)

# Access L2 regime info
l2 = regime_data['regimes']['L2']
print(l2['name'])  # "Complex Active Regime"
print(l2['dynamics']['energy_flow'])  # "variable_high"
```

### Load Transition Definitions
```python
# Load transition specifications
with open('data/regime_transitions.json') as f:
    transition_data = json.load(f)

# Access L2→L3 transition
l2_to_l3 = transition_data['transitions']['L2_to_L3']
print(l2_to_l3['name'])  # "Deactivation"
print(l2_to_l3['characteristics'])
```

### Use Validation Tools
```python
from src.regime_validator import RegimeValidator, Regime, InferenceType

# Initialize validator
validator = RegimeValidator(
    regime_definitions_path='data/regime_definitions.json',
    transition_definitions_path='data/regime_transitions.json'
)

# Check if causal history inference is valid in L0
valid, msg = validator.validate_inference(
    Regime.L0, 
    InferenceType.CAUSAL_HISTORY
)
print(f"Valid: {valid}")
print(f"Explanation: {msg}")

# Detect regime leakage
is_leakage, msg = validator.detect_regime_leakage(
    source_regime=Regime.L1,
    target_regime=Regime.L3,
    inference_type=InferenceType.LINEAR_PREDICTION
)
print(f"Leakage detected: {is_leakage}")
print(f"Explanation: {msg}")
```

## For Graph Databases (Neo4j)

### Import Regime Structure
```cypher
// Create regime nodes
CREATE (l0:Regime {
  name: "L0",
  full_name: "Latent Regime",
  energy_flow: "none",
  entropy_production: "none"
})

CREATE (l1:Regime {
  name: "L1",
  full_name: "Stable Active Regime",
  energy_flow: "stable_low",
  entropy_production: "low"
})

CREATE (l2:Regime {
  name: "L2",
  full_name: "Complex Active Regime",
  energy_flow: "variable_high",
  entropy_production: "high"
})

CREATE (l3:Regime {
  name: "L3",
  full_name: "Residual Structure Regime",
  energy_flow: "none",
  entropy_production: "none"
})

// Create transition relationships
MATCH (l0:Regime {name: "L0"}), (l1:Regime {name: "L1"})
CREATE (l0)-[:TRANSITIONS_TO {
  name: "Activation",
  type: "phase_extended"
}]->(l1)

MATCH (l1:Regime {name: "L1"}), (l2:Regime {name: "L2"})
CREATE (l1)-[:TRANSITIONS_TO {
  name: "Complexification",
  type: "gradual"
}]->(l2)

MATCH (l2:Regime {name: "L2"}), (l3:Regime {name: "L3"})
CREATE (l2)-[:TRANSITIONS_TO {
  name: "Deactivation",
  type: "phase_extended"
}]->(l3)

MATCH (l3:Regime {name: "L3"}), (l0:Regime {name: "L0"})
CREATE (l3)-[:CYCLES_TO {
  name: "Cyclical Reset",
  type: "conceptual_cyclical"
}]->(l0)
```

## For Vector Databases (Qdrant, Pinecone, etc.)

### Index Documents
```python
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

# Read markdown documentation
with open('docs/L0_L3_Regime_Architecture.md') as f:
    full_text = f.read()

# Create embeddings (use your preferred embedding model)
# embedding = embed_text(full_text)

# Store in Qdrant
client = QdrantClient(host="localhost", port=6333)
client.create_collection(
    collection_name="efc_l0_l3",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE)
)

# Add document with metadata
client.upsert(
    collection_name="efc_l0_l3",
    points=[
        PointStruct(
            id=1,
            vector=embedding,
            payload={
                "title": "L0–L3 Regime Architecture",
                "author": "Morten Magnusson",
                "version": "1.0",
                "doi": "10.6084/m9.figshare.31112536",
                "text": full_text
            }
        )
    ]
)
```

## For RAG Systems

### Example Prompt Template
```
You are analyzing a system using the L0–L3 regime architecture from 
Energy-Flow Cosmology (EFC). The system has four regimes:

L0 (Latent): Configuration space without active dynamics
L1 (Stable Active): Low-entropy, predictable operation
L2 (Complex Active): Non-linear dynamics, structural formation
L3 (Residual): Structure without process

When analyzing [SYSTEM], identify:
1. Current regime (L0, L1, L2, or L3)
2. Key characteristics that justify this classification
3. Potential transitions and their thresholds
4. Valid inference methods for this regime
5. Warning: avoid regime leakage

Context from regime definitions:
{regime_context}
```

## Testing the Package

```bash
# Test Python validator
cd src
python regime_validator.py

# Expected output:
# === L0-L3 Regime Validator ===
# Test 1: Causal history in L0
# Valid: False
# Explanation: L0 is latent configuration without causal history
# ...
```

## Next Steps

1. **Integrate into your project**: Copy JSON files to your data directory
2. **Customize validation**: Extend `regime_validator.py` for your domain
3. **Add to knowledge base**: Import into your graph/vector database
4. **Create regime-aware prompts**: Use regime context in LLM queries
5. **Track regime transitions**: Log when systems cross regime boundaries

## Support

- **Documentation**: See `docs/` folder
- **Examples**: See `examples/regime_examples.md`
- **Citation**: See `CITATION.cff` or README.md
- **License**: CC BY 4.0 (see LICENSE file)
- **Author**: Morten Magnusson (ORCID: 0009-0002-4860-5095)

---

**Quick validation check**: Does your system have bounded energy flow, entropy gradients, and phase transitions? Then the L0–L3 architecture applies!
