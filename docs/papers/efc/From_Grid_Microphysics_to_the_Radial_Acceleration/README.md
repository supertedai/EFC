# From Grid Microphysics to the Radial Acceleration Relation: A Minimal Gradient-Coupled Excitation Model

**Author:** Morten Magnusson  
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)  
**DOI:** [10.6084/m9.figshare.31878760](https://doi.org/10.6084/m9.figshare.31878760)  
**Date:** March 2026  
**Framework:** Energy-Flow Cosmology (EFC)

## Summary

This paper closes the microphysical gap identified in the Covariant EFT construction: a classical local Lagrangian cannot produce the Bose–Einstein form of the RAR. The solution is a minimal microscopic model where discrete degrees of freedom on a substrate (grid) have gradient-coupled excitation energy E ∝ √|∇Φ|. This single physical input, combined with Bose–Einstein statistics, reproduces the observed RAR μ(g) = 1/(exp(√(g/a₀)) − 1) with no free parameters beyond the measured scale a₀.

## Key Results

1. **Bridge established**: Grid DOF → gradient coupling → E ∝ √g → BE statistics → μ(g) → G_eff → RAR
2. **Three assumptions only**: Bosonic statistics, gradient-coupled excitation energy, single scale a₀
3. **Lattice derivation**: k_eff = g/l_g from gravitational gradient restoring force → ω ∝ √g → E ∝ √g
4. **KT3 resolution pathway**: Statistical occupation (not classical operator) should restore β = 0.5
5. **Falsification conditions**: BE form exact (not FD/Boltzmann), coupling to g (not ρ or Φ), E ∝ √g (α = 1/2 exactly)

## Three Assumptions

| # | Assumption | Content |
|---|-----------|---------|
| 1 | Bosonic statistics | Grid modes obey BE: ⟨n⟩ = 1/(exp(E/k_B T_grid) − 1) |
| 2 | Gradient-coupled energy | E(x) = ℏω₀ √(|∇Φ(x)|/g*) |
| 3 | Single scale | a₀ ≡ g* (k_B T_grid / ℏω₀)² = 1.2 × 10⁻¹⁰ m/s² |

## What This Model Does NOT Do

- No dynamics (kinematic only)
- No grid topology assumed
- No quantum field theory (BE used as input, not derived from path integral)
- No cosmological derivation (static, weak-field limit only)
- No derivation of a₀ (measured, not predicted)

## File Structure

```
├── README.md           # This file
├── index.json          # Machine-readable index
├── schema.json         # Validation schema
├── metadata.json       # Structured metadata
├── citations.bib       # BibTeX references
├── grid_microphysics.jsonld  # JSON-LD linked data
├── src/
│   ├── __init__.py
│   └── grid_microphysics.py  # Python implementation
├── data/
│   └── model.json      # Model parameters and results
└── examples/
    └── demo_bridge.py  # Executable demonstration
```
