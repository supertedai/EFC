# Energy-Flow Cosmology (EFC)

A unified thermodynamic framework where energy flows along entropy gradients, generating spacetime structure, galactic dynamics, and consciousness.

[![DOI](https://img.shields.io/badge/DOI-10.6084%2Fm9.figshare.30656828-blue)](https://doi.org/10.6084/m9.figshare.30656828)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0002--4860--5095-green)](https://orcid.org/0009-0002-4860-5095)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## The Core Idea

> **"Energy flows along entropy gradients."**

This single principle explains:
- **Galactic rotation curves** without dark matter particles
- **Cosmic acceleration** without dark energy as a substance
- **Structure formation** through thermodynamic self-organization
- **Consciousness** as resonance in non-equilibrium energy fields

## Ecosystem

| Surface | Description |
|---------|-------------|
| [energyflow-cosmology.com](https://energyflow-cosmology.com/) | Public theory website |
| [magnusson.as](https://www.magnusson.as/) | Personal hypothesis platform |
| [This Repository](https://github.com/supertedai/EFC) | Technical implementation |
| [Figshare](https://figshare.com/authors/Morten_Magnusson/18515981) | Peer-reviewed publications |
| [ORCID](https://orcid.org/0009-0002-4860-5095) | Academic identity |

## Repository Structure

```
EFC/
├── auth/           # Origin & provenance (START HERE)
├── theory/         # Formal mathematics (LaTeX)
│   └── formal/     # S, D, R, H, C0 models
├── schema/         # Ontology & semantic definitions
├── methodology/    # Research process framework
├── meta/           # Meta-cognition layer
├── meta-graph/     # Graph representation
├── docs/           # Papers & publications
│   ├── papers/     # Research papers with DOIs
│   ├── notebooks/  # Jupyter notebooks
│   └── figures/    # Visualizations
├── src/            # Python implementation
├── api/            # Semantic REST API
├── jsonld/         # JSON-LD semantic files
├── figshare/       # DOI mappings & sync
├── integrations/   # External systems
│   ├── mcp/        # AI Agent MCP Server
│   └── wp/         # WordPress integration
└── scripts/        # Utility scripts
```

## For AI Agents

See [`llms.txt`](./llms.txt) for navigation instructions and [`AGENTS.md`](./AGENTS.md) for detailed integration guide.

### MCP Server

The repository includes an MCP (Model Context Protocol) server for AI agent management:

```bash
cd integrations/mcp
pip install -r requirements.txt
python efc_mcp_server.py
```

Capabilities:
- Website posting (energyflow-cosmology.com, magnusson.as)
- Figshare publication management
- Repository validation and synchronization

## Key Publications

| Paper | DOI |
|-------|-----|
| EFC v2.2: Cross-Field Integration | [10.6084/m9.figshare.30530156](https://doi.org/10.6084/m9.figshare.30530156) |
| EFC v1.2: Foundational Framework | [10.6084/m9.figshare.30563738](https://doi.org/10.6084/m9.figshare.30563738) |
| Formal Master Specification | [10.6084/m9.figshare.30630500](https://doi.org/10.6084/m9.figshare.30630500) |
| AUTH Layer (Provenance) | [10.6084/m9.figshare.30656828](https://doi.org/10.6084/m9.figshare.30656828) |
| Symbiosis Architecture | [10.6084/m9.figshare.30773684](https://doi.org/10.6084/m9.figshare.30773684) |

## Modular Theory

EFC consists of interconnected models:

| Model | Domain | Description |
|-------|--------|-------------|
| **EFC-S** | Structure | Halo model, thermodynamic boundaries |
| **EFC-D** | Dynamics | Energy flow field equations |
| **EFC-R** | Rotation | Galaxy rotation curves |
| **EFC-H** | Halos | Entropy halo profiles |
| **EFC-C0** | Cognition | Consciousness-entropy coupling |

## Quick Start

### Read the Theory
```bash
# Start with the formal specification
open theory/formal/efc-formal-spec/index.tex

# Or the synthesis paper
open docs/papers/efc/EFC-v2.1-Complete-Edition/EFC-v2.1-Complete-Edition.pdf
```

### Run the Code
```python
from src.efc.core.efc_core import EFCModel

model = EFCModel()
result = model.compute_rotation_curve(galaxy_params)
```

### Use the API
```python
import json
with open('api/v1/concepts.json') as f:
    concepts = json.load(f)
```

## Citation

```bibtex
@misc{magnusson2025efc,
  author       = {Magnusson, Morten},
  title        = {Energy-Flow Cosmology (EFC)},
  year         = {2025},
  doi          = {10.6084/m9.figshare.30656828},
  url          = {https://github.com/supertedai/EFC},
  note         = {ORCID: 0009-0002-4860-5095}
}
```

Or use the [CITATION.cff](./CITATION.cff) file for automatic citation.

## Author

**Morten Magnusson**
- ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)
- Website: [magnusson.as](https://www.magnusson.as/)
- Project: [energyflow-cosmology.com](https://energyflow-cosmology.com/)

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

*"Energy flows along entropy gradients—this is the fundamental dynamic of the Universe."*
