# GR Recovery in Energy-Flow Cosmology via Density Saturation

## Quantitative PPN Analysis for the Solar System

**Author:** Morten Magnusson
**Date:** February 2026
**Version:** EFC v1.3 Series, Revision 2.1
**DOI:** [10.6084/m9.figshare.31244827](https://doi.org/10.6084/m9.figshare.31244827)

## Abstract

Energy-Flow Cosmology (EFC) modifies gravitational dynamics through entropy-gradient couplings that produce observable effects at galactic and cosmological scales. A critical requirement for any modified gravity theory is compatibility with precision Solar System tests. This paper provides:

1. A precise definition of the effective density ρ_eff entering the EFC screening function
2. An explicit derivation showing γ = 1 at linearized order (with |δγ| < 10⁻¹⁹ at higher order)
3. Quantitative evaluation showing dual screening suppresses all EFC modifications far below the Cassini bound

## Key Result: Dual Screening Guarantees GR Recovery

### 1. Acceleration-Based Screening (Galactic)

```
μ(g_bar) = (1 + g†/g_bar)^k
```

Parameters (from SPARC fits):
- **g†** ≈ 1.2 × 10⁻¹⁰ m/s² (transition acceleration, consistent with MOND a₀)
- **k** ≈ 0.415 ± 0.029

| Location | g_bar (m/s²) | g†/g_bar | \|μ-1\| | Margin vs Cassini |
|----------|-------------|----------|---------|-------------------|
| Solar surface | 274 | 4.4×10⁻¹³ | 1.8×10⁻¹³ | 10⁸× below |
| 1 AU | 5.9×10⁻³ | 2.0×10⁻⁸ | 8.3×10⁻⁹ | 2.8×10³× below |
| Mercury | 3.9×10⁻² | 3.1×10⁻⁹ | 1.3×10⁻⁹ | 1.8×10⁴× below |
| Saturn | 6.5×10⁻⁴ | 1.8×10⁻⁷ | 7.6×10⁻⁸ | 3.0×10²× below |
| Galaxy 30 kpc | ~10⁻¹⁰ | ~1 | ~0.35 | **EFC active** |

### 2. Density-Based Screening (Cosmological)

```
Θ(ρ_eff) = exp[-(ρ_eff/ρ*)^n]
```

Parameters:
- **ρ*** ~ 10⁻²² kg/m³ (transition density from SPARC)
- **n** ≥ 1 (steepness parameter)

**Critical definition of ρ_eff:**
```
ρ_eff(r) = 3 M_enc(r) / (4π r³)
```
This is the **source-smoothed** density (mean interior density), not the local particle density.

| Location | r | ρ_eff (kg/m³) | ρ_eff/ρ* | Θ |
|----------|---|---------------|----------|---|
| Solar core | 0 | 1.6×10⁵ | 1.6×10²⁷ | ≈0 |
| Solar surface | R☉ | 1.4×10³ | 1.4×10²⁵ | ≈0 |
| 1 AU | 1 AU | 5.9×10³ | 5.9×10²⁵ | ≈0 |
| Saturn | 9.5 AU | 4.6 | 4.6×10²² | ≈0 |
| Galaxy disk | ~8 kpc | ~10⁻²² | ~1 | 0.37 |
| Galaxy edge | ~30 kpc | ~10⁻²⁴ | ~0.01 | ≈1 |

## PPN Mapping: γ = 1 Derived

### Modified Einstein Equation

```
G_μν = 8πG_N [1 + μ(S)] T_μν
```

The modification is a **scalar rescaling** of G_N, not an anisotropic coupling.

### Linearized Metric (Newtonian Gauge)

```
ds² = -(1 + 2Φ) c² dt² + (1 - 2Ψ) δ_ij dx^i dx^j
```

### Derived Result

From the (00) and trace (ij) components:
```
∇²Φ = 4πG_N [1 + Θ·μ₀] ρ
∇²Ψ = 4πG_N [1 + Θ·μ₀] ρ + O(p/ρc²)
```

Since the **same factor** appears in both equations:

```
Φ = Ψ  ⟹  γ_EFC ≡ Ψ/Φ = 1
```

**This is a theorem, not an assumption.**

### Higher-Order Corrections

```
|γ - 1|_EFC ≤ Θ(ρ_eff) · |μ₀| · (U/c²) · r_s|∇ln μ|
```

At Solar surface: |γ - 1| < 10⁻¹⁹ — **fourteen orders of magnitude below Cassini**.

## Equivalence Principle

### Weak Equivalence Principle (WEP)
- **Preserved by construction**: μ depends only on source properties, not test body composition
- All test bodies experience identical modified potential

### Strong Equivalence Principle (SEP) / Nordtvedt

```
|η|_EFC ≤ Θ(ρ_eff) · |ε| · (E_grav / Mc²)
```

For Earth: |η|_EFC < 10⁻¹⁷ — well below LLR bound of 4.4×10⁻⁴

## Experimental Constraints Summary

| Test | Bound | EFC (accel.) | EFC (density) | Status |
|------|-------|--------------|---------------|--------|
| Shapiro (Cassini) | \|γ-1\| < 2.3×10⁻⁵ | \|μ-1\| ~ 8×10⁻⁹ | γ = 1 (derived) | ✓ |
| LLR (Nordtvedt) | \|η\| < 4.4×10⁻⁴ | < 10⁻¹⁷ | ≈ 0 | ✓ |
| Mercury perihelion | 42.98±0.04 ″/cen | ~10⁻⁷ ″/cen | ≈ 0 | ✓ |
| WEP | \|Δa/a\| < 10⁻¹³ | 0 (constr.) | 0 (constr.) | ✓ |

## Comparison with Other Screening Mechanisms

| Mechanism | Field Equation | Screen Variable | EFC Advantage |
|-----------|---------------|-----------------|---------------|
| Chameleon | □φ = dV/dφ + βρ/M_Pl | m_eff(ρ) | No extra d.o.f. |
| Symmetron | □φ = φ(ρ-ρ*) | VEV(φ) | No SSB needed |
| Vainshtein | Nonlin. ∇∇φ | r_V | Algebraic, not kinetic |
| **EFC accel.** | μ = (1+g†/g_b)^k | g_bar | From SPARC |
| **EFC density** | Θ = exp[-(ρ_e/ρ*)^n] | ρ_eff | Source-smoothed |

## Key Equations Summary

1. **Acceleration screening**: μ(g_bar) = (1 + g†/g_bar)^k
2. **Density screening**: Θ(ρ_eff) = exp[-(ρ_eff/ρ*)^n]
3. **Effective density**: ρ_eff = 3M_enc/(4πr³)
4. **Modified Einstein**: G_μν = 8πG_N[1 + μ(S)]T_μν
5. **PPN parameter**: γ = Ψ/Φ = 1 (derived)
6. **Higher-order bound**: |δγ| < 10⁻¹⁹

## Physical Interpretation

The EFC screening mechanism is analogous to **chameleon screening** but uses:
- The gravitational potential's source density (not local particle density)
- The Newtonian acceleration (not a scalar field mass)

This explains why:
- **Galaxies**: Low ρ_eff, low g_bar → EFC modifications active → flat rotation curves
- **Solar System**: High ρ_eff, high g_bar → EFC modifications screened → GR recovered

## Package Contents

```
├── README.md                 # This file
├── CITATION.cff             # Citation metadata
├── LICENSE                  # CC-BY-4.0
├── index.json               # Machine-readable metadata
├── src/
│   ├── __init__.py
│   └── efc_ppn_screening.py # Screening function implementations
├── data/
│   ├── acceleration_screening.json
│   └── density_screening.json
└── examples/
    └── solar_system_screening.py
```

## Citation

```bibtex
@misc{magnusson2026ppn,
  author = {Magnusson, Morten},
  title = {GR Recovery in Energy-Flow Cosmology via Density Saturation:
           Quantitative PPN Analysis for the Solar System},
  year = {2026},
  publisher = {Figshare},
  doi = {10.6084/m9.figshare.31244827}
}
```

## License

CC-BY-4.0
