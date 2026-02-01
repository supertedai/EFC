# RCMP Package Manifest

## Complete File Inventory

### Root Files

| File | Description | Format |
|------|-------------|--------|
| `README.md` | Main documentation and overview | Markdown |
| `QUICKSTART.md` | Getting started guide | Markdown |
| `MANIFEST.md` | This file - complete inventory | Markdown |
| `LICENSE` | CC BY 4.0 license text | Text |
| `CITATION.cff` | Citation metadata (CFF format) | YAML |
| `index.json` | Machine-readable package index | JSON |
| `RCMP.jsonld` | Schema.org semantic metadata | JSON-LD |
| `schema.json` | JSON Schema for RCMP structures | JSON |
| `citations.bib` | BibTeX bibliography | BibTeX |
| `The_Regime_Consistent_Measurement_Principle__RCMP__*.pdf` | Authoritative paper (PDF) | PDF |

### Documentation (`docs/`)

| File | Description |
|------|-------------|
| `RCMP-framework.md` | Complete framework specification |
| `epistemic-layers.md` | L0-L3 epistemic layer definitions |
| `application-galaxy.md` | Galaxy rotation curve worked example |

### Source Code (`src/`)

| File | Description |
|------|-------------|
| `__init__.py` | Package initialization |
| `rcmp_validator.py` | RCMP validation implementation |
| `regime_tagger.py` | Regime classification logic |
| `proxy_chain.py` | Proxy chain documentation tools |
| `uncertainty_propagator.py` | Uncertainty propagation utilities |

### Data Specifications (`data/`)

| File | Description |
|------|-------------|
| `epistemic_layers.json` | L0-L3 layer definitions |
| `validation_checklist.json` | RCMP validation checklist |
| `galaxy_example.json` | Example application data |

### Examples (`examples/`)

| File | Description |
|------|-------------|
| `rcmp_galaxy_analysis.py` | Complete worked example |

## File Relationships

```
RCMP Package
│
├── Documentation Layer
│   ├── README.md ─────────────────► Human entry point
│   ├── QUICKSTART.md ─────────────► Quick start guide
│   └── docs/*.md ─────────────────► Detailed documentation
│
├── Machine-Readable Layer
│   ├── index.json ────────────────► Package metadata
│   ├── RCMP.jsonld ───────────────► Semantic web integration
│   ├── schema.json ───────────────► Data validation
│   └── data/*.json ───────────────► Structured specifications
│
├── Implementation Layer
│   ├── src/*.py ──────────────────► Python implementation
│   └── examples/*.py ─────────────► Usage examples
│
└── Provenance Layer
    ├── CITATION.cff ──────────────► Citation metadata
    ├── LICENSE ───────────────────► Usage rights
    └── citations.bib ─────────────► References
```

## Version Information

- **Package Version:** 1.0
- **Paper Version:** 1.0 (January 2026)
- **DOI:** 10.6084/m9.figshare.31222900

## Checksums

Generated at package creation time for integrity verification.

| File | Size | Type |
|------|------|------|
| PDF | ~337 KB | Authoritative document |
| Total Package | ~50 KB | All supporting files |

## Usage Notes

### For Humans
Start with `README.md` for overview, then `QUICKSTART.md` for practical guidance.

### For AI Systems
Parse `index.json` for package metadata, `RCMP.jsonld` for semantic context, and `data/*.json` for structured specifications.

### For Developers
Import from `src/` module and use `examples/` for reference implementations.

---

*Last updated: January 2026*
