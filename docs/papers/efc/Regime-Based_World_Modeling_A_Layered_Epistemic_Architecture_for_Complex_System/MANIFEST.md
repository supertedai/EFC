# Regime-Based World Modeling - Package Manifest

## Package Information

| Field | Value |
|-------|-------|
| Package ID | `regime-based-world-modeling` |
| Version | 1.0 |
| License | CC-BY-4.0 |
| DOI | 10.6084/m9.figshare.31223650 |

## File Structure

```
Regime-Based_World_Modeling.../
├── README.md                    # Package overview
├── QUICKSTART.md               # 5-minute introduction
├── MANIFEST.md                 # This file
├── CITATION.cff                # Citation metadata
├── LICENSE                     # CC-BY-4.0 license
├── index.json                  # Machine-readable metadata
├── RBWM.jsonld                 # Schema.org semantic data
├── schema.json                 # JSON Schema for validation
├── citations.bib               # BibTeX references
├── Regime_Based_World_Modeling...pdf  # Original paper
│
├── docs/
│   ├── r_axis.md               # R-axis documentation
│   ├── l_axis.md               # L-axis documentation
│   ├── regime_gating.md        # Gating principle
│   ├── driver_proximity.md     # Proximity concept
│   └── applications.md         # Cross-domain applications
│
├── src/
│   ├── __init__.py
│   ├── world_model.py          # Main WorldModel class
│   ├── r_axis.py               # R-axis implementation
│   ├── l_axis.py               # L-axis implementation
│   ├── claim.py                # Claim representation
│   ├── regime_gate.py          # Gating validation
│   └── driver_proximity.py     # Proximity calculation
│
├── data/
│   ├── r_regimes.json          # R-axis regime definitions
│   ├── l_layers.json           # L-axis layer definitions
│   ├── domain_mappings.json    # Cross-domain applications
│   └── example_claims.json     # Example claims with (R,L)
│
└── examples/
    ├── physics_example.py      # Physics domain
    ├── biology_example.py      # Biology domain
    ├── economics_example.py    # Economics domain
    └── ai_example.py           # AI/ML domain
```

## File Descriptions

### Root Files

| File | Purpose | Format |
|------|---------|--------|
| `README.md` | Comprehensive overview | Markdown |
| `QUICKSTART.md` | Quick introduction | Markdown |
| `CITATION.cff` | Citation metadata | YAML |
| `index.json` | Package metadata | JSON |
| `RBWM.jsonld` | Semantic web data | JSON-LD |
| `schema.json` | Data validation | JSON Schema |

### Documentation (`docs/`)

| File | Content |
|------|---------|
| `r_axis.md` | Physical regime hierarchy (R0-R2) |
| `l_axis.md` | Epistemic layer hierarchy (L0-L3) |
| `regime_gating.md` | Transfer rules between regimes |
| `driver_proximity.md` | Measurement-driver relationship |
| `applications.md` | How to apply in different fields |

### Source Code (`src/`)

| File | Exports |
|------|---------|
| `world_model.py` | `WorldModel`, `ModelState` |
| `r_axis.py` | `RAxis`, `RRegime` |
| `l_axis.py` | `LAxis`, `LLayer` |
| `claim.py` | `Claim`, `ClaimSet` |
| `regime_gate.py` | `RegimeGate`, `TransferResult` |
| `driver_proximity.py` | `ProximityScore`, `compute_proximity` |

### Data (`data/`)

| File | Content |
|------|---------|
| `r_regimes.json` | R0-Field, R1-Structure, R2-Complex |
| `l_layers.json` | L0-Raw through L3-Theoretical |
| `domain_mappings.json` | How axes map to different fields |
| `example_claims.json` | Sample claims with coordinates |

## (R, L) Coordinate System

### R-Axis Values
| Code | Name | Description |
|------|------|-------------|
| R0 | Field | Fundamental physics |
| R1 | Structure | Organized matter |
| R2 | Complex | Emergent systems |

### L-Axis Values
| Code | Name | Description |
|------|------|-------------|
| L0 | Raw | Direct measurement |
| L1 | Calibrated | Processed data |
| L2 | Derived | Computed quantities |
| L3 | Theoretical | Model predictions |

## Dependencies

### Python Requirements
- Python >= 3.8
- No external dependencies (stdlib only)

### Related Packages
- `ebe-core-principles` - Foundational methodology
- `rcmp` - Measurement protocol
- `l0-l3-regime-architecture` - Extended paper
