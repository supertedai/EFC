# EFC L0-L3 Package Manifest

**Package:** efc_l0_l3_package  
**Version:** 1.0.0  
**Date:** 2026-01-21  
**Size:** ~93KB (12 files)  
**Formats:** .tar.gz (26KB), .zip (32KB)

## Contents

### Documentation (docs/)
- `ABSTRACT.md` - Quick abstract reference
- `L0_L3_Regime_Architecture.md` - Full markdown documentation
- `L0_L3_Regime_Architecture_Figshare.pdf` - Publication-ready PDF (8 pages)

### Data (data/)
- `regime_definitions.json` - Machine-readable regime specifications
- `regime_transitions.json` - Transition parameters and thresholds

### Source Code (src/)
- `regime_validator.py` - Python validation tools for regime checking

### Examples (examples/)
- `regime_examples.md` - Concrete applications across 5 domains

### Metadata
- `README.md` - Main documentation and overview
- `CITATION.cff` - Standard citation metadata
- `LICENSE` - CC BY 4.0 license text
- `QUICKSTART.md` - Installation and usage guide
- `.gitignore` - Git ignore rules

## Package Features

### For Humans
✓ Readable markdown documentation  
✓ Publication-ready PDF  
✓ Concrete examples across domains  
✓ Clear citation format  

### For AI Systems
✓ JSON-formatted regime definitions  
✓ Structured transition parameters  
✓ Python validation library  
✓ RAG-ready documentation  

### For Databases
✓ Neo4j Cypher examples  
✓ Vector database integration guide  
✓ Graph structure templates  

## Use Cases

1. **Research Reference** - Cite in EFC/EBE papers
2. **AI Knowledge Base** - Import into RAG/graph systems
3. **Validation Tool** - Check regime validity in models
4. **Educational Resource** - Teach entropy-bounded reasoning
5. **Development Template** - Extend for domain-specific regimes

## Installation

```bash
# Extract
tar -xzf efc_l0_l3_package.tar.gz
cd efc_l0_l3_package

# Read documentation
cat docs/ABSTRACT.md

# Test validator
python src/regime_validator.py
```

## Verification

### File Count
- Total files: 12
- Documentation: 3
- Data: 2
- Source: 1
- Examples: 1
- Metadata: 5

### Checksums (SHA256)
Generate with: `sha256sum efc_l0_l3_package.*`

## Compatibility

- **Python:** 3.7+
- **OS:** Linux, macOS, Windows
- **Dependencies:** None (standard library only)
- **License:** CC BY 4.0 (permissive)

## Next Steps

1. Extract package
2. Read QUICKSTART.md
3. Import JSON into your system
4. Test regime_validator.py
5. Integrate with your project

---

**DOI:** 10.6084/m9.figshare.31112536  
**Author:** Morten Magnusson  
**ORCID:** 0009-0002-4860-5095
