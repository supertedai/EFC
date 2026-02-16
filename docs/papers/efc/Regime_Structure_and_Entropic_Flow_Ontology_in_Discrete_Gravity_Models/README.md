# Regime Structure and Entropic Flow Ontology in Discrete Gravity Models

## AI-Friendly Package

**Version**: 1.0
**Author**: Morten Magnusson (ORCID: 0009-0002-4860-5095)
**Date**: February 2026
**License**: CC-BY-4.0

## Overview

This paper formalises the **regime structure** underlying discrete entropic gravity models based on graph-defined functionals. Rather than treating gravitational dynamics as universally geometric, distinct physical behaviours emerge from **dominance transitions** between three sectors of a discrete entropic functional:

| Sector | Domain | Behaviour | Governs |
|--------|--------|-----------|---------|
| **Gradient** (UV) | Strong-field | Newtonian: g ~ r^{-2} | Local field dynamics |
| **Bulk** (IR) | Cosmological | Yukawa screening | Large-scale screening |
| **Source** | All scales | Linear coupling to ρ | Gravitational sourcing |

**Key Result**: The three gravitational regimes (UV/Newtonian, IR/MOND-like, Cosmological) are **exhaustive** and **emerge from a single functional** without separate theoretical frameworks. The cosmological constant Λ acts as a **bulk entropic capacity parameter**, simultaneously setting the local MOND transition scale a₀ and the global screening length L_Λ.

## Core Equations

### 1. Discrete Entropic Functional (Eq. 1)
```
F[Φ] = Σ_{⟨i,j⟩} κ_ij F(|Φ_i − Φ_j|/a₀)
      + Σ_i ½ μ_Λ (Φ_i − Φ_V)²
      + Σ_i λ_i ρ_i Φ_i
```
where F(x) = ∫₀ˣ y μ(y) dy is the AQUAL kinetic integrand.

### 2. Interpolating Function
```
μ(x) = x / √(1 + x²)
```

### 3. Discrete Euler–Lagrange Equation (Eq. 2)
```
Σ_{j~i} κ_ij μ(|Φ_i − Φ_j|/(a₀ a)) (Φ_j − Φ_i) − μ_Λ(Φ_i − Φ_V) = 4πGρ_i
```

### 4. Continuum Limit (Eq. 3)
```
∇·[μ(|∇Φ|/a₀) ∇Φ] − μ_Λ(Φ − Φ_V) = 4πGρ
```

### 5. UV (Newtonian) Limit — |∇Φ| >> a₀ (Eq. 4)
```
∇²Φ = 4πGρ
```

### 6. IR (MOND-like) Limit — |∇Φ| << a₀ (Eq. 5)
```
∇·(|∇Φ|/a₀ ∇Φ) = 4πGρ    →    g ∝ r⁻¹
```

### 7. Cosmological Limit — bulk dominates (Eq. 6)
```
∇²Φ − μ_Λ Φ = 4πGρ        (Yukawa-type)
```

### 8. Screening Scale (Eq. 7–8)
```
L_Λ = 1/√μ_Λ,    μ_Λ ∝ Λ    →    L_Λ ∝ Λ^{-1/2} ~ 4.4 Gpc
```

### 9. Dimensionless Regime Ratios (Eq. 9)
```
ξ = |∇Φ|/a₀,    η = μ_Λ Φ / |∇²Φ|
```

## Regime Dominance Map

| Regime | ξ | η | Behaviour |
|--------|---|---|-----------|
| UV (Newtonian) | >> 1 | << 1 | g ∝ r⁻² |
| IR (MOND-like) | << 1 | << 1 | g ∝ r⁻¹ |
| Cosmological | any | >> 1 | Yukawa screening |

**Transitions**:
- UV → IR at ξ ~ 1 (i.e., g ~ a₀)
- IR → Cosmological at η ~ 1 (i.e., scales approaching L_Λ)

## Dual Role of Λ

1. **Local**: Sets the MOND transition scale a₀ ∝ c² √Λ
2. **Global**: Sets the screening length L_Λ ∝ Λ^{-1/2} ~ H₀⁻¹

This dual role is a **structural feature** of the functional, not an imposed coincidence.

## Package Contents

```
Regime_Structure_and_Entropic_Flow_Ontology_.../
├── README.md                              # This file
├── QUICKSTART.md                          # 5-minute introduction
├── MANIFEST.md                            # File listing with descriptions
├── CITATION.cff                           # Citation metadata
├── index.json                             # Machine-readable metadata
├── RegimeStructureEntropicFlowOntology.jsonld  # Schema.org semantic data
├── schema.json                            # JSON Schema for validation
├── citations.bib                          # BibTeX references
├── *.pdf                                  # Original paper
│
├── data/
│   ├── parameters.json                    # Physical constants and model parameters
│   ├── regime_map.json                    # Regime dominance structure
│   └── functional_sectors.json            # Three-sector decomposition
│
├── src/
│   ├── __init__.py
│   ├── interpolating_function.py          # μ(x) and AQUAL kinetic integrand
│   ├── discrete_functional.py             # Three-sector functional and EL equation
│   └── regime_classifier.py               # Classify regime from (ξ, η)
│
└── examples/
    ├── classify_regimes.py                # Classify physical systems by regime
    └── functional_sectors.py              # Demonstrate sector dominance transitions
```

## Quick Usage

```python
from src.regime_classifier import classify_regime, regime_ratios
from src.interpolating_function import mu, aqual_integrand

# Classify a physical system
xi, eta = regime_ratios(grad_phi=1e-8, a0=1.2e-10, mu_lambda=1.11e-52, phi=1e5, laplacian_phi=1e-25)
regime = classify_regime(xi, eta)
print(f"  ξ = {xi:.2e}, η = {eta:.2e} → Regime: {regime}")

# Interpolating function behaviour
print(f"  μ(100)  = {mu(100):.6f}")   # → ~1 (Newtonian)
print(f"  μ(0.01) = {mu(0.01):.6f}")  # → ~0.01 (MOND)
```

## Physical Interpretation

- **No fundamental metric assumed**: The entire framework is defined on graph topology.
- **Three regimes are exhaustive**: For any field configuration, exactly one sector dominates.
- **Transitions are smooth**: Governed by the interpolating function μ(x).
- **No free functions** beyond μ(x) and the Λ-proportional bulk coupling.
- **Time is not fundamental**: The field equation is an equilibrium condition δF/δΦᵢ = 0. Temporal ordering can be interpreted as successive reconfigurations of gradient energy.

## Ontological Commitments

1. **Entropy**: Not thermodynamic entropy, but the functional capacity of the discrete network.
2. **Energy flow**: Gradient energy redistribution on the graph.
3. **Λ**: Bulk entropic capacity — the strength of anchoring to the cosmological background Φ_V.
4. **Spacetime**: Emergent from graph structure, not fundamental.

## Falsification Criteria

1. If the three regimes fail to be exhaustive for any physical configuration → **falsified**
2. If transitions require additional free functions beyond μ(x) and μ_Λ ∝ Λ → structural failure
3. If Λ cannot simultaneously set a₀ and L_Λ in a consistent manner → dual-role claim falsified
4. Numerical verification in companion papers [1, 2] must remain consistent

## Epistemic Status

**Layer A**: Foundational framework paper providing the regime-based ontology that connects the companion papers. No new phenomenology introduced.

## Related EFC Papers

- [Discrete Entropic Gravity on Cubic Graph](../Discrete_Entropic_Gravity_on_a_Cubic_Graph_Emergent_Newton_and_MOND_Regimes_with_Λ-Locked_Screening/) — Numerical verification (DOI: 10.6084/m9.figshare.31348411)
- [Cosmological Growth Constraints](../Cosmological_Growth_Constraints_on_Λ-Locked_Discrete_Entropic_Gravity/) — Cosmological stress test (DOI: 10.6084/m9.figshare.31348414)

## Citation

```bibtex
@article{magnusson2026regimestructure,
  author  = {Magnusson, Morten},
  title   = {Regime Structure and Entropic Flow Ontology
             in Discrete Gravity Models},
  year    = {2026},
  note    = {Energy-Flow Cosmology Project}
}
```
