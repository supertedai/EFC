# Derivation of Γ(ρ) from Grid-Mode Bose-Einstein Statistics — AI-Friendly Package

**Paper**: Derivation of the Entropy Production Function Γ(ρ) from Grid-Mode Bose-Einstein Statistics
**Author**: Morten Magnusson (Independent Researcher, Sola, Norway)
**DOI**: [10.6084/m9.figshare.31942821](https://doi.org/10.6084/m9.figshare.31942821)
**Version**: 1.0 (April 2026)
**Framework**: Energy-Flow Cosmology (EFC) v3.7

## Key Result

First explicit derivation of Γ(ρ) from first principles:
- Start: von Neumann entropy S[n] = (1+n)ln(1+n) - n ln n for BE occupation
- Chain: ds/dn = x (marginal entropy = dimensionless energy), dn/dρ = -n(n+1)x/(2ρ)
- Result: Γ(ρ) ∝ ρ^(3/2) / (ρ + ρ_crit) with ρ_crit = a₀/(G_N l_g)

**Scenario B**: correct qualitative structure (vanishing at ρ=0, sub-linear growth, emergent ρ_crit) but exponent 3/2 instead of phenomenological 1. Double-counting concern (μ_BE vs Γ) resolved: μ is static occupation, Γ is dynamical rate.

## Package Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `index.json` | Machine-readable entry point |
| `schema.json` | JSON Schema for data validation |
| `metadata.json` | Dublin Core + DataCite metadata |
| `entropy_production.jsonld` | JSON-LD linked data |
| `citations.bib` | BibTeX references |
| `src/__init__.py` | Python package init |
| `src/entropy_production.py` | Core implementation |
| `data/entropy_production_data.json` | Equations, requirements, scenarios |
| `examples/demo_entropy_production.py` | Executable demonstration |

## Key Equations

- **BE occupation**: n(g) = 1/(exp(√(g/a₀)) - 1) (Eq. 1)
- **Dimensionless energy**: x(ρ) = √(βρ/a₀) (Eq. 4)
- **Marginal entropy**: ds/dn = x (key result, Eq. 11)
- **Per-mode Γ**: |Γ| = (β/(2a₀)) n(n+1) (Eq. 20)
- **Total Γ**: Γ(ρ) ∝ ρ^(3/2)/(ρ + ρ_crit) (Eq. 37-38)
- **ρ_crit**: a₀/(G_N l_g) — emergent (Eq. 33)

## Quick Start

```python
from src.entropy_production import (
    BEOccupation,
    VonNeumannEntropy,
    GammaDerivation,
    ScenarioClassification,
)

gamma = GammaDerivation()
print(f"Γ(ρ/ρ_crit=0.5) = {gamma.gamma_total(0.5):.4f}")
```

## Citation

```bibtex
@article{magnusson2026gammaderivation,
  author  = {Magnusson, Morten},
  title   = {Derivation of the Entropy Production Function Γ(ρ) from Grid-Mode Bose–Einstein Statistics},
  year    = {2026},
  doi     = {10.6084/m9.figshare.31942821}
}
```
