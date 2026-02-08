# EBE Core Principles - Package Manifest

## Package Information

| Field | Value |
|-------|-------|
| Package ID | `ebe-core-principles` |
| Version | 1.0 |
| License | CC-BY-4.0 |
| DOI | 10.6084/m9.figshare.31222903 |

## File Structure

```
EBE-Core-Principles/
├── README.md                    # Package overview
├── QUICKSTART.md               # 5-minute introduction
├── MANIFEST.md                 # This file
├── CITATION.cff                # Citation metadata
├── LICENSE                     # CC-BY-4.0 license
├── index.json                  # Machine-readable metadata
├── EBE.jsonld                  # Schema.org semantic data
├── schema.json                 # JSON Schema for validation
├── citations.bib               # BibTeX references
├── EBE_Core_Principles_v1_0-1.pdf  # Original paper
│
├── docs/
│   ├── s_axis.md               # S-axis detailed documentation
│   ├── l_axis.md               # L-axis detailed documentation
│   ├── regime_gating.md        # Regime-gating principle
│   └── integration.md          # Integration with other papers
│
├── src/
│   ├── __init__.py
│   ├── ebe_classifier.py       # Main classification engine
│   ├── s_axis.py               # S-axis implementation
│   ├── l_axis.py               # L-axis implementation
│   └── regime_gating.py        # Regime transfer validation
│
├── data/
│   ├── s_regimes.json          # S-axis regime definitions
│   ├── l_layers.json           # L-axis layer definitions
│   └── examples.json           # Example classifications
│
└── examples/
    ├── basic_classification.py  # Simple usage example
    └── cross_regime_analysis.py # Multi-regime example
```

## File Descriptions

### Root Files

| File | Purpose | Format |
|------|---------|--------|
| `README.md` | Comprehensive overview | Markdown |
| `QUICKSTART.md` | Quick introduction | Markdown |
| `CITATION.cff` | Citation metadata | YAML |
| `index.json` | Package metadata | JSON |
| `EBE.jsonld` | Semantic web data | JSON-LD |
| `schema.json` | Data validation | JSON Schema |

### Documentation (`docs/`)

| File | Content |
|------|---------|
| `s_axis.md` | Physical regime hierarchy (Low-S, Mid-S, High-S) |
| `l_axis.md` | Epistemic layer hierarchy (L0-L3) |
| `regime_gating.md` | When claims can transfer between regimes |
| `integration.md` | How EBE connects to RCMP, Core Lock |

### Source Code (`src/`)

| File | Exports |
|------|---------|
| `ebe_classifier.py` | `EBEClassifier`, `ClassificationResult` |
| `s_axis.py` | `SAxis`, `SRegime` |
| `l_axis.py` | `LAxis`, `LLayer` |
| `regime_gating.py` | `RegimeGate`, `TransferValidator` |

### Data (`data/`)

| File | Content |
|------|---------|
| `s_regimes.json` | S-axis regime specifications |
| `l_layers.json` | L-axis layer specifications |
| `examples.json` | Example measurement classifications |

## Dependencies

### Python Requirements
- Python >= 3.8
- No external dependencies (stdlib only)

### Related Packages
- `rcmp` - Operationalizes EBE principles
- `core-lock` - Mathematical engine

## Versioning

This package follows semantic versioning:
- MAJOR: Breaking changes to API or concepts
- MINOR: New features, backward compatible
- PATCH: Bug fixes, documentation updates
