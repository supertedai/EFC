# EBE Core Lock - Package Manifest

## Package Information

| Field | Value |
|-------|-------|
| Package ID | `ebe-core-lock` |
| Version | 1.0 |
| License | CC-BY-4.0 |
| DOI | 10.6084/m9.figshare.31223503 |

## File Structure

```
Core-Lock/
├── README.md                    # Package overview
├── QUICKSTART.md               # 5-minute introduction
├── MANIFEST.md                 # This file
├── CITATION.cff                # Citation metadata
├── LICENSE                     # CC-BY-4.0 license
├── index.json                  # Machine-readable metadata
├── CoreLock.jsonld             # Schema.org semantic data
├── schema.json                 # JSON Schema for validation
├── citations.bib               # BibTeX references
├── Core_Lock.pdf               # Original paper
│
├── docs/
│   ├── beta_constraint.md      # β-function documentation
│   ├── grid_state.md           # Grid state function
│   ├── information_length.md   # Conservation law
│   └── falsification.md        # Falsification criterion
│
├── src/
│   ├── __init__.py
│   ├── grid_state_function.py  # f(S) implementation
│   ├── beta_constraint.py      # β_f(S) = -1/ΔS
│   ├── information_length.py   # Conserved quantity
│   ├── projection_laws.py      # Observable projection
│   └── simulation.py           # Numerical verification
│
├── data/
│   ├── parameters.json         # Model parameters
│   ├── test_cases.json         # Verification cases
│   └── predictions.json        # Falsifiable predictions
│
├── examples/
│   ├── basic_simulation.py     # Simple usage
│   └── correlation_test.py     # Falsification test
│
└── figures/
    ├── core_lock_survival_test.png
    └── ebe_core_lock_v1_simulation.png
```

## File Descriptions

### Root Files

| File | Purpose | Format |
|------|---------|--------|
| `README.md` | Comprehensive overview | Markdown |
| `QUICKSTART.md` | Quick introduction | Markdown |
| `CITATION.cff` | Citation metadata | YAML |
| `index.json` | Package metadata | JSON |
| `CoreLock.jsonld` | Semantic web data | JSON-LD |
| `schema.json` | Data validation | JSON Schema |

### Documentation (`docs/`)

| File | Content |
|------|---------|
| `beta_constraint.md` | The fundamental β_f(S) = -1/ΔS constraint |
| `grid_state.md` | Grid state function f(S) = f₀ exp(-S/ΔS) |
| `information_length.md` | Conserved quantity across projections |
| `falsification.md` | How to test and potentially falsify |

### Source Code (`src/`)

| File | Exports |
|------|---------|
| `grid_state_function.py` | `GridStateFunction` |
| `beta_constraint.py` | `BetaConstraint`, `verify_constraint` |
| `information_length.py` | `InformationLength`, `compute_length` |
| `projection_laws.py` | `ProjectionLaw`, `project_observable` |
| `simulation.py` | `CoreLockSimulation`, `run_verification` |

### Data (`data/`)

| File | Content |
|------|---------|
| `parameters.json` | Default ΔS and f₀ values |
| `test_cases.json` | Numerical verification cases |
| `predictions.json` | Testable predictions |

### Figures (`figures/`)

| File | Shows |
|------|-------|
| `core_lock_survival_test.png` | Survival function plot |
| `ebe_core_lock_v1_simulation.png` | Simulation results |

## Key Equations

| Name | Equation | File |
|------|----------|------|
| Beta function | β_f(S) = -1/ΔS | `beta_constraint.py` |
| Grid state | f(S) = f₀ exp(-S/ΔS) | `grid_state_function.py` |
| Phase | Φ(S) = ∫dS'/f(S') | `projection_laws.py` |
| Correlation test | d ln v / d ln c = constant | `simulation.py` |

## Dependencies

### Python Requirements
- Python >= 3.8
- numpy >= 1.20 (for simulations)
- matplotlib >= 3.0 (for plotting, optional)

### Related Packages
- `ebe-core-principles` - Theoretical foundation
- `rcmp` - Measurement protocol
