# Density of States of Gravitationally Active Grid Modes — AI-Friendly Package

**Paper**: Density of States of Gravitationally Active Grid Modes: Derivation of D_eff(ρ) and Completion of the Γ(ρ) Bridge
**Author**: Morten Magnusson (Independent Researcher, Sola, Norway)
**DOI**: [10.6084/m9.figshare.31942800](https://doi.org/10.6084/m9.figshare.31942800)
**Version**: 1.0 (April 2026)
**Framework**: Energy-Flow Cosmology (EFC) v3.7

## Key Result

Derives the effective density of gravitationally active grid modes D_eff(ρ) ∝ √(ρ/ρ_crit) from first principles (discrete lattice + Higgs-stabilised nodes + activation dynamics). Combined with per-mode BE entropy production, the microphysically derived entropy production function is:

```
Γ(ρ) = Γ₀ √(ρ/ρ_crit) / (1 + √(ρ/ρ_crit))    with ρ_crit = a₀/(G_N l_g)
```

This differs from the phenomenological ansatz ρ/(ρ + ρ_crit) but agrees to ~20% over the cosmologically relevant range. Scenario classification: **B+** (microphysically derived, correct saturation, emergent ρ_crit).

## Package Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `index.json` | Machine-readable entry point |
| `schema.json` | JSON Schema for data validation |
| `metadata.json` | Dublin Core + DataCite metadata |
| `density_of_states.jsonld` | JSON-LD linked data |
| `citations.bib` | BibTeX references |
| `src/__init__.py` | Python package init |
| `src/density_of_states.py` | Core implementation |
| `data/density_of_states_data.json` | Tables, equations, scenarios |
| `examples/demo_density_of_states.py` | Executable demonstration |

## Key Equations

- **Activation condition**: G_N ρ l_g² > σ₀ l_g → ρ > ρ_crit
- **D_eff(ρ)**: ∝ √(ρ/ρ_crit) (boundary-mode mechanism, Eq. 26)
- **ρ_crit**: a₀/(G_N l_g) — emergent from microphysics (Eq. 5)
- **Per-mode entropy**: Γ_per-mode ∝ 1/ρ at low ρ (from BE statistics)
- **ρ̇ rescue**: Γ_t ∝ ρ^(-1/2) × ρ = ρ^(1/2) (cosmological trajectory, Eq. 45)
- **Final form**: Γ(ρ) = Γ₀ √(ρ/ρ_crit) / (1 + √(ρ/ρ_crit)) (Eq. 48)

## Scenario Classification

| Scenario | Form | Status |
|----------|------|--------|
| A | ρ/(ρ + ρ_crit) — phenomenological | Target (not derived) |
| B | ρ^(3/2)/(ρ + ρ_crit) — partial | Previous |
| **B+** | **√(ρ/ρ_crit) / (1 + √(ρ/ρ_crit))** | **Derived (this paper)** |

## Quick Start

```python
from src.density_of_states import (
    GridActivation,
    DensityOfStates,
    EntropyProductionFunction,
    ScenarioComparison,
)

# Derived Γ(ρ) vs phenomenological
gamma = EntropyProductionFunction()
print(f"Γ(ρ/ρ_crit=0.1) = {gamma.gamma_derived(0.1):.4f}")
print(f"Γ_phenom(0.1)   = {gamma.gamma_phenomenological(0.1):.4f}")
```

## Citation

```bibtex
@article{magnusson2026densityofstates,
  author  = {Magnusson, Morten},
  title   = {Density of States of Gravitationally Active Grid Modes},
  year    = {2026},
  doi     = {10.6084/m9.figshare.31942800}
}
```
