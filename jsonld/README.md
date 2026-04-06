# EFC JSON-LD Semantic Metadata

This directory contains 59 JSON-LD files providing semantic metadata for Energy-Flow Cosmology (EFC) research outputs. Each file follows the Schema.org vocabulary with EFC-specific extensions, enabling linked-data discoverability by search engines, AI agents, and knowledge graphs.

**Author:** Morten Magnusson (ORCID [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)), Symbiose Research, Sandnes, Norway
**License:** CC-BY-4.0

## Schema Pattern

Every JSON-LD file in this directory follows a consistent structure:

```json
{
  "@context": "https://schema.org",
  "@type": "CreativeWork",
  "identifier": "efc-<slug>",
  "name": "Human-readable title",
  "description": "Brief summary of the resource",
  "file": "docs/papers/efc/<path-to-source>"
}
```

- **`@context`** -- Always `https://schema.org`, establishing the base vocabulary.
- **`@type`** -- Typically `CreativeWork`, representing a paper, specification, or dataset.
- **`identifier`** -- A unique slug matching the filename (without `.jsonld`).
- **`name`** -- The display title of the resource.
- **`description`** -- A brief description of what the resource covers.
- **`file`** -- Relative path to the source document within the EFC repository.

This pattern makes each file both human-readable and machine-parseable, functioning as a lightweight catalog entry for its corresponding research artifact.

## Usage for AI Agents

To discover and index EFC content programmatically:

```python
import json
from pathlib import Path

# Load all EFC metadata
jsonld_dir = Path("jsonld")
catalog = []
for f in jsonld_dir.glob("*.jsonld"):
    with open(f) as fh:
        catalog.append(json.load(fh))

# Find papers about entropy
entropy_papers = [
    item for item in catalog
    if "entropy" in item.get("name", "").lower()
]
```

To embed in HTML for search engine discovery:

```html
<script type="application/ld+json">
  { "@context": "https://schema.org", "@type": "CreativeWork", ... }
</script>
```

## File Catalog

### Index and Master Files

| File | Description |
|------|-------------|
| `efc-index.jsonld` | Root index of the EFC paper collection |
| `efc-master.jsonld` | Master specification pointer |
| `efc-master-v1.jsonld` | Master specification v1 pointer |
| `efc-master-specification.jsonld` | Full master specification metadata |
| `efc-master-specification-v1-archive.jsonld` | Archived v1 master specification |
| `efc-formal-spec.jsonld` | Formal specification (compact) |
| `efc-formal-specification.jsonld` | Formal specification (full) |

### Core Framework Papers

| File | Description |
|------|-------------|
| `efc-energy-flow-as-the-fundamental-dynamic-of-the-universe.jsonld` | Core claim: energy flow as fundamental universal dynamic |
| `efc-hypothesis-universe-as-an-energy-driven-system.jsonld` | Universe as energy-driven system hypothesis |
| `efc-hypothesis-universe-as-energy-driven-system.jsonld` | Energy-driven system hypothesis (alternate) |
| `efc-hypothesis-interrelation-between-energy-and-entropy.jsonld` | Energy-entropy interrelation hypothesis |
| `efc-hypothesis-interrelation-energy-entropy.jsonld` | Energy-entropy interrelation (compact) |
| `efc-field-equations-for-entropy-driven-spacetime.jsonld` | Field equations for entropy-driven spacetime |
| `efc-mathematical-framework-for-energy-flow-in-space-time.jsonld` | Mathematical framework for energy-flow spacetime |

### Versioned Editions

| File | Description |
|------|-------------|
| `efc-v1-2-foundational-framework.jsonld` | EFC v1.2 foundational framework |
| `efc-v2-1-complete-edition.jsonld` | EFC v2.1 complete edition |
| `efc-v2-1-modular-synthesis.jsonld` | EFC v2.1 modular synthesis |
| `efc-v2-2-cross-field-integration-summary.jsonld` | EFC v2.2 cross-field integration summary |

### Entropy and Cosmic Evolution

| File | Description |
|------|-------------|
| `efc-can-entropy-drive-cosmic-evolution.jsonld` | Whether entropy drives cosmic evolution |
| `efc-introduction-to-entropy-in-cosmic-evolution.jsonld` | Introduction to entropy in cosmic evolution |
| `efc-observational-evidence-for-entropy-in-cosmic-evolution.jsonld` | Observational evidence for entropy in evolution |
| `efc-observational-evidence-entropy-cosmic-evolution.jsonld` | Entropy-evolution evidence (compact) |
| `efc-unresolved-questions-and-challenges-entropy.jsonld` | Unresolved entropy questions |
| `efc-integrated-hypothesis-time-and-entropy.jsonld` | Integrated time-entropy hypothesis |
| `efc-integrated-hypothesis-time-entropy.jsonld` | Time-entropy hypothesis (compact) |
| `efc-dynamic-balance-entropy-order-and-chaos.jsonld` | Dynamic balance: entropy, order, and chaos |

### Energy Flow and Spacetime

| File | Description |
|------|-------------|
| `efc-introduction-to-energy-flow-in-space-time.jsonld` | Introduction to energy flow in spacetime |
| `efc-how-energy-flow-sustains-spacetime.jsonld` | How energy flow sustains spacetime |
| `efc-how-energy-flow-sustain-spacetime.jsonld` | Energy flow sustaining spacetime (alternate) |
| `efc-flow-entropy-and-spacetime-distortion-in-cosmological-clusters.jsonld` | Flow, entropy, and spacetime distortion in clusters |
| `efc-can-energy-flow-be-observed-in-galactic-clusters.jsonld` | Observing energy flow in galactic clusters |

### Specific Topics

| File | Description |
|------|-------------|
| `efc-the-thermodynamic-bridge-between-gr-and-qft.jsonld` | Thermodynamic bridge between GR and QFT |
| `efc-thermodynamic-bridge-gr-qft.jsonld` | GR-QFT bridge (compact) |
| `efc-light-speed-as-a-regulator-of-energy-flow-in-the-universe.jsonld` | Light speed as energy-flow regulator |
| `efc-subhypothesis-light-speed-limit.jsonld` | Sub-hypothesis on light speed limit |
| `efc-why-is-light-speed-a-cosmic-limit.jsonld` | Why light speed is a cosmic limit |
| `efc-is-consciousness-linked-to-entropy.jsonld` | Consciousness and entropy linkage |
| `efc-what-happens-at-the-universes-extremes.jsonld` | Physics at the universe's extremes |
| `efc-what-is-the-connection-between-energy-flow-and-the-now.jsonld` | Energy flow and the present moment |
| `efc-how-does-balance-shape-universal-structures.jsonld` | Balance shaping universal structures |
| `efc-a-deep-dive-into-the-halo-concept.jsonld` | Deep dive into the halo concept |
| `efc-cmb-thermodynamic-gradient.jsonld` | CMB thermodynamic gradient analysis |
| `efc-the-energy-flow-interface.jsonld` | The energy-flow interface |
| `efc-observational-evidence-for-energy-flow.jsonld` | Observational evidence for energy flow |
| `efc-applications-and-implications.jsonld` | EFC applications and implications |

### Grid and Higgs Framework

| File | Description |
|------|-------------|
| `efc-grid-higgs-framework.jsonld` | EFC grid-Higgs framework |
| `efc-grid-higgs-paradigm-shift.jsonld` | Grid-Higgs paradigm shift |
| `efc-grid-model-entropic-dynamics.jsonld` | Grid model for entropic dynamics |
| `efc-grid-model-for-entropic-dynamics.jsonld` | Grid model entropic dynamics (full) |

### AI and Workflow

| File | Description |
|------|-------------|
| `ai-workflow-framework-energy-flow-cosmology.jsonld` | AI workflow framework for EFC |
| `efc-ai-augmented-scientific-workflow-framework.jsonld` | AI-augmented scientific workflow |
| `efc-adaptive-learning-system-complete-integration.jsonld` | Adaptive learning system integration |
| `efc-meta-learning-layer-9-kryssvaliderings-mesh-dokumentasjon.jsonld` | Meta-learning layer 9 cross-validation mesh |
| `gnn-augmented-efc-theory-development.jsonld` | GNN-augmented EFC theory development |
| `efc-meta-universe.jsonld` | EFC meta-universe metadata |

### API, Papers, and Provenance

| File | Description |
|------|-------------|
| `energy-flow-cosmology-api-v1.jsonld` | EFC API v1 specification |
| `efc-papers-energy-flow-cosmology.jsonld` | EFC papers collection metadata |
| `efc-technical-documentation-energy-flow-in-space-time.jsonld` | Technical documentation index |
| `auth-layer-origin-provenance-and-structural-signature-of-energy-flow-cosmology.jsonld` | Origin provenance and structural signature |

## Related Directories

- `/integrations/mcp/` -- MCP server that consumes these metadata files
- `/integrations/wp/schemas/` -- WordPress structured data schemas
- `/meta/` -- Meta-architecture with corresponding `index.jsonld` files per subdirectory
