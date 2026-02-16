# Regime Structure and Entropic Flow Ontology — Package Manifest

## Package Information

| Field | Value |
|-------|-------|
| Package ID | `regime-structure-entropic-flow-ontology` |
| Version | 1.0 |
| License | CC-BY-4.0 |
| Status | Layer A (Foundational framework) |

## File Structure

```
Regime_Structure_and_Entropic_Flow_Ontology_.../
├── README.md                              # Package overview
├── QUICKSTART.md                          # 5-minute introduction
├── MANIFEST.md                            # This file
├── CITATION.cff                           # Citation metadata (CFF)
├── index.json                             # Machine-readable metadata
├── RegimeStructureEntropicFlowOntology.jsonld  # Schema.org semantic data
├── schema.json                            # JSON Schema for validation
├── citations.bib                          # BibTeX references
├── *.pdf                                  # Original paper
│
├── data/
│   ├── parameters.json                    # Physical constants and model parameters
│   ├── regime_map.json                    # Regime dominance structure and transitions
│   └── functional_sectors.json            # Three-sector decomposition
│
├── src/
│   ├── __init__.py                        # Package init
│   ├── interpolating_function.py          # μ(x) and AQUAL kinetic integrand F(x)
│   ├── discrete_functional.py             # Three-sector functional and Euler-Lagrange
│   └── regime_classifier.py               # Classify regime from (ξ, η)
│
└── examples/
    ├── classify_regimes.py                # Classify physical systems by regime
    └── functional_sectors.py              # Demonstrate sector dominance transitions
```

## Key Concepts Summary

| Concept | Description | Equation |
|---------|-------------|----------|
| Discrete entropic functional | Three-sector functional on graph | Eq. 1 |
| Gradient sector (UV) | Nearest-neighbour coupling with μ(x) | Dominant when ξ >> 1 |
| Bulk sector (IR) | Quadratic coupling to Φ_V with μ_Λ ∝ Λ | Dominant when η >> 1 |
| Source sector | Linear coupling to ρ_i | Always present |
| Interpolating function | μ(x) = x/√(1+x²) | Standard form |
| Screening scale | L_Λ = 1/√μ_Λ ~ 4.4 Gpc | Eq. 7–8 |
| Regime ratios | ξ = \|∇Φ\|/a₀, η = μ_Λ Φ/\|∇²Φ\| | Eq. 9 |

## Source Code (`src/`)

| File | Exports | Description |
|------|---------|-------------|
| `interpolating_function.py` | `mu`, `mu_derivative`, `aqual_integrand` | Standard interpolating function and AQUAL kinetic integrand |
| `discrete_functional.py` | `gradient_sector`, `bulk_sector`, `source_sector`, `total_functional`, `euler_lagrange_residual` | Three-sector decomposition with Euler-Lagrange |
| `regime_classifier.py` | `regime_ratios`, `classify_regime`, `transition_scales` | Regime classification from physical quantities |

## Data Files (`data/`)

| File | Content |
|------|---------|
| `parameters.json` | Physical constants (G, c, Λ, a₀), lattice settings, sector definitions |
| `regime_map.json` | Full regime dominance table with ξ, η conditions and transition boundaries |
| `functional_sectors.json` | Three-sector definitions with equations, limits, and physical interpretations |

## Dependencies

### Python Requirements
- Python >= 3.8
- math (standard library)

### Related Packages
- `discrete-entropic-gravity-cubic-graph` — Numerical verification (companion)
- `cosmological-growth-constraints-lambda-locked` — Cosmological stress test (companion)

## Validation Checklist

- [x] Three regimes exhaustive for all field configurations
- [x] Transitions smooth via interpolating function μ(x)
- [x] No free functions beyond μ(x) and μ_Λ ∝ Λ
- [x] L_Λ ~ 4.4 Gpc from Λ without tuning
- [x] Consistent with numerical results in companion paper [1]
- [x] Consistent with cosmological constraints in companion paper [2]
- [ ] Full derivation of temporal dynamics from functional (stated as open problem)
