# EFC Gradient-Coupled Grid Action

**DOI:** [10.6084/m9.figshare.31941465](https://doi.org/10.6084/m9.figshare.31941465)  
**Author:** Morten Magnusson (ORCID: 0009-0002-4860-5095)  
**Framework:** Energy-Flow Cosmology (EFC) v3.7  
**License:** CC-BY-4.0

## Summary

This paper derives the EFC screening relation E ∝ √g from a minimal three-term
Lagrangian (the "grid action" S_grid). The action consists of:

1. **Kinetic term:** ½ m_eff (∂_t ξ)²
2. **Bare elastic term:** ½ κ₀ (∇ξ)²
3. **Gradient coupling:** ½ α |∇Φ| (∇ξ)²

The Euler-Lagrange equation yields an effective stiffness κ_eff(x) = κ₀ + α g(x),
producing a local dispersion relation ω² = κ_eff/m_eff · k². In the gravitational
regime (αg ≫ κ₀), Theorem 1 shows E = ℏω ∝ √g, recovering the RAR-like screening
relation from first principles.

## Key Results

- **Theorem 1:** E ∝ √g in the αg ≫ κ₀ regime (Eq. 8)
- **Operator uniqueness:** Table 1 eliminates 4 alternative couplings (C1-C4);
  only C5 = |∇Φ| survives dimensional, symmetry, and locality constraints
- **Three regimes:** bare elastic (κ₀ ≫ αg), gravitational (αg ≫ κ₀),
  transition (αg ~ κ₀) with crossover at g_cross = κ₀/α
- **Bosonic quantisation:** Standard Fock space, Bose-Einstein thermal occupation
- **Complete chain:** S_grid → Euler-Lagrange → WKB → E ∝ √g → BE → μ(g)
- **Predictions:** P1 (bare stiffness bound κ₀/(αa₀) ≪ 1),
  P2 (dispersion signature at sub-kpc scales)

## AI-Friendly Package

```
EFC_Gradient_Coupled_Grid_Action/
├── README.md              # This file
├── index.json             # Machine-readable index
├── schema.json            # Validation schema
├── metadata.json          # Structured metadata
├── grid_action.jsonld     # JSON-LD linked data
├── citations.bib          # BibTeX references
├── src/
│   ├── __init__.py        # Package init
│   └── grid_action.py     # Core implementation
├── data/
│   └── grid_action_data.json  # Parameters and results
└── examples/
    └── demo_grid_action.py    # Executable demo
```

## Quick Start

```python
from src.grid_action import (
    GridAction, EffectiveStiffness, DispersionRelation,
    GradientCouplingTheorem, OperatorElimination, RegimeAnalysis,
    BosonicQuantisation, FalsifiablePredictions
)

# Build the three-term Lagrangian
action = GridAction(m_eff=1.0, kappa_0=1e-12, alpha=1.0)
L = action.lagrangian(dxi_dt=0.1, grad_xi=0.05, g_local=1e-10)

# Verify E ∝ √g theorem
theorem = GradientCouplingTheorem(alpha=1.0, m_eff=1.0)
E = theorem.energy(g=1e-10, k=1.0)

# Check operator uniqueness
elim = OperatorElimination()
survivors = elim.evaluate_all()
```

## Related Papers

- [Grid Microphysics to RAR](../Grid_Microphysics_to_RAR/) (DOI: 31878760) — Bose-Einstein RAR derivation
- [Covariant EFT](../Covariant_EFT_for_Energy_Flow_Cosmology/) (DOI: 31878334) — Covariant effective field theory
- [EFC Screening Model](../Energy-Flow_Cosmology_Empirical_Validation_of_the_EFC_Screening_Model_Track_1/) (DOI: 31940469) — Empirical validation (k=0.415)
