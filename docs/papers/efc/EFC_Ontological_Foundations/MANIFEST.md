# EFC Ontological Foundations - Package Manifest

## Package Information

| Field | Value |
|-------|-------|
| Package ID | `efc-ontological-foundations` |
| Version | 1.0 |
| License | CC-BY-4.0 |
| Status | Methodological (Layer C) |

## File Structure

```
EFC_Ontological_Foundations/
├── README.md                    # Package overview
├── QUICKSTART.md               # 5-minute introduction
├── MANIFEST.md                 # This file
├── CITATION.cff                # Citation metadata
├── LICENSE                     # CC-BY-4.0 license
├── index.json                  # Machine-readable metadata
├── Ontology.jsonld             # Schema.org semantic data
├── schema.json                 # JSON Schema for validation
├── citations.bib               # BibTeX references
├── EFC_Ontological_Foundations_v1_0_2-1.pdf  # Original paper
│
├── docs/
│   ├── circularity_problem.md  # The core problem
│   ├── three_hypotheses.md     # H1, H2, H3 analysis
│   ├── co_primary_structure.md # The solution
│   ├── phases.md               # Pre/Post Planck phases
│   └── cross_domain.md         # Evidence from other fields
│
├── src/
│   ├── __init__.py
│   ├── circularity_tester.py   # Test definitions for circularity
│   ├── hypothesis_analyzer.py  # Analyze H1, H2, H3
│   ├── ontology_model.py       # Co-primary structure model
│   └── phase_classifier.py     # Classify by phase
│
├── data/
│   ├── hypotheses.json         # H1, H2, H3 specifications
│   ├── phases.json             # Phase definitions
│   ├── frameworks.json         # Referenced frameworks
│   └── circularity_tests.json  # Test case definitions
│
└── examples/
    ├── circularity_analysis.py # Analyze a hypothesis
    └── phase_classification.py # Classify phenomena by phase
```

## File Descriptions

### Root Files

| File | Purpose | Format |
|------|---------|--------|
| `README.md` | Comprehensive overview | Markdown |
| `QUICKSTART.md` | Quick introduction | Markdown |
| `CITATION.cff` | Citation metadata | YAML |
| `index.json` | Package metadata | JSON |
| `Ontology.jsonld` | Semantic web data | JSON-LD |
| `schema.json` | Data validation | JSON Schema |

### Documentation (`docs/`)

| File | Content |
|------|---------|
| `circularity_problem.md` | Why EF-first and S-first both fail |
| `three_hypotheses.md` | Detailed H1, H2, H3 analysis |
| `co_primary_structure.md` | The differentiation model |
| `phases.md` | Pre-Planck, transition, post-Planck |
| `cross_domain.md` | Wheeler, Verlinde, Prigogine, holographic |

### Source Code (`src/`)

| File | Exports |
|------|---------|
| `circularity_tester.py` | `CircularityTester`, `test_definition` |
| `hypothesis_analyzer.py` | `HypothesisAnalyzer`, `AnalysisResult` |
| `ontology_model.py` | `CoPrimaryModel`, `Differentiation` |
| `phase_classifier.py` | `PhaseClassifier`, `Phase` |

### Data (`data/`)

| File | Content |
|------|---------|
| `hypotheses.json` | H1, H2, H3 with test results |
| `phases.json` | Pre-Planck, Planck, Post-Planck |
| `frameworks.json` | Referenced theoretical frameworks |
| `circularity_tests.json` | Formal circularity test cases |

## Key Concepts

### Three Hypotheses

| ID | Name | Result |
|----|------|--------|
| H1 | Energy-Flow Primacy | Fails (circular) |
| H2 | Entropy Primacy | Fails (circular) |
| H3 | Co-Primary Structure | Passes all tests |

### Three Phases

| Phase | Description |
|-------|-------------|
| Pre-Planck | Undifferentiated potential |
| Planck Transition | Differentiation occurs |
| Post-Planck | Standard physics applies |

## Epistemic Status

**Layer C**: This is a coherence argument, not an empirical claim.

The paper:
- Identifies conceptual problems in standard formulations
- Proposes a structural resolution
- Does NOT make directly testable predictions
- Provides foundation for papers that do (Core Lock)

## Dependencies

### Python Requirements
- Python >= 3.8
- No external dependencies (stdlib only)

### Related Packages
- `core-lock` - Mathematical implementation
- `ebe-core-principles` - Methodological framework
- `energy-flow-cosmology` - Parent framework
