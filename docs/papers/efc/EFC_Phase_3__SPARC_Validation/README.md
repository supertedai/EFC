# EFC Phase 3: SPARC Validation

## AI-Friendly Package

**DOI**: [10.6084/m9.figshare.31224397](https://doi.org/10.6084/m9.figshare.31224397)
**Version**: 1.0
**Author**: Morten Magnusson (ORCID: 0009-0002-4860-5095)
**Date**: February 2026
**License**: CC-BY-4.0

## Overview

This paper performs an **empirical test** of Energy-Flow Cosmology against the Radial Acceleration Relation (RAR) using the SPARC database.

**Key Result**: EFC's screening form fits SPARC data with k = 0.415 ± 0.029, yielding a cross-scale consistency parameter C = k/a_G = 4.4 ± 0.6.

## Data

- **Source**: SPARC database (Lelli et al. 2016)
- **Galaxies**: 174 (after quality cuts Q ≤ 2, inclination > 30°)
- **Data points**: 3264 radial measurements
- **Observables**: g_obs (observed), g_bar (baryonic)

## The EFC Screening Form

### Gravitational Enhancement
```
μ = (1 + g†/g_bar)^k
```
where:
- **μ** = g_obs / g_bar (enhancement factor)
- **g†** = transition acceleration scale
- **k** = screening exponent = a_G × C

### Log-Linear Form (fitted)
```
ln μ = k × ln(1 + g†/g_bar)
```

## Key Results

| Parameter | Value | Source |
|-----------|-------|--------|
| k (screening exponent) | 0.415 ± 0.029 | SPARC fit |
| g† (transition scale) | (2.51 ± 0.60) × 10⁻¹⁰ m/s² | SPARC fit |
| σ_int (intrinsic scatter) | 0.33 in ln μ (≈ 0.14 dex) | SPARC fit |
| a_G (universal coupling) | 0.094 ± 0.01 | H₀ analysis |
| **C = k/a_G (phase-gain)** | **4.4 ± 0.6** | Derived |

## Physical Interpretation

### The Phase-Gain Parameter C

C connects galactic and cosmological scales:
- **Cosmological**: ΔΦ_cosmo ≈ 1.7 (background → structure transition)
- **Galactic**: ΔΦ_gal = C × ln(1 + g†/g_bar) varies with position

| Location | g_bar/g† | ΔΦ_gal |
|----------|----------|--------|
| Transition zone | 1.0 | ~3.1 |
| Outer disk | 0.1 | ~10.6 |

**Regime mismatch factor**: ΔΦ_gal / ΔΦ_cosmo ~ 2–6

### Comparison with MOND

| Framework | Form | Scale |
|-----------|------|-------|
| MOND | μ = x/(1+x), x = g/a₀ | a₀ = 1.2 × 10⁻¹⁰ m/s² |
| EFC | μ = (1 + g†/g)^k | g† = 2.5 × 10⁻¹⁰ m/s² |

The different scales arise from different functional forms.

## Method

### Maximum Likelihood with Intrinsic Scatter
```
ln L = -½ Σᵢ [(yᵢ - k ln(1 + g†/g_bar,i))² / (σ²_y,i + σ²_int) + ln(σ²_y,i + σ²_int)]
```

### Bootstrap Uncertainty
- 500 iterations
- Galaxy-level resampling (preserves intra-galaxy correlations)
- k range: 0.38–0.45
- g† range: (2.0–3.0) × 10⁻¹⁰ m/s²

## Package Contents

```
├── README.md                 # This file
├── CITATION.cff             # Citation metadata
├── LICENSE                  # CC-BY-4.0
├── index.json               # Machine-readable metadata
│
├── src/
│   ├── __init__.py
│   ├── screening_model.py    # EFC screening form
│   ├── likelihood.py         # MLE with intrinsic scatter
│   ├── bootstrap.py          # Bootstrap resampling
│   └── cross_scale.py        # C = k/a_G calculation
│
├── data/
│   ├── fit_results.json      # Canonical fit parameters
│   └── parameters.json       # Framework parameters
│
└── examples/
    └── sparc_analysis.py     # Demonstration
```

## Quick Usage

```python
from src.screening_model import EFCScreening
from src.cross_scale import compute_phase_gain

# Create screening model with fitted parameters
model = EFCScreening(k=0.415, g_dagger=2.51e-10)

# Compute enhancement at a given g_bar
g_bar = 1e-10  # m/s²
mu = model.enhancement(g_bar)
print(f"μ = {mu:.3f}")  # Enhancement factor

# Compute phase-gain parameter
aG = 0.094
C = compute_phase_gain(k=0.415, aG=aG)
print(f"C = {C:.1f}")  # 4.4
```

## Cross-Scale Consistency

This paper establishes that:

1. **EFC screening form fits SPARC RAR** (σ_int ≈ 0.14 dex)
2. **k ≈ 0.42 from galaxies**
3. **a_G ≈ 0.094 from H₀ tension** (independent!)
4. **C = k/a_G ≈ 4.4** connects the two scales

This is a **consistency check**, not a prediction. A parameter-free prediction requires deriving g† and C from Core Lock first principles.

## Epistemic Status

**Layer A**: Empirical fit to observational data.

- Establishes RAR compatibility
- Does NOT yet derive g† or C from first principles
- Cross-scale consistency achieved

## Related EFC Papers

- [H₀-RAR Unification](../Unified_Origin_of_the_Radial_Acceleration_Relation_and_the_Hubble_Tension_via_Entropic_Gravity_Modification/) - Source of a_G = 0.094
- [Hubble Tension Regime Mismatch](../The_Hubble_Tension_as_Regime_Mismatch/) - Regime interpretation
- [Core Lock](../Core-Lock/) - Mathematical foundation

## Citation

```bibtex
@article{magnusson2026sparc,
  author = {Magnusson, Morten},
  title = {EFC Phase 3: SPARC Validation},
  subtitle = {Empirical Test of Energy-Flow Cosmology Against the RAR},
  year = {2026},
  doi = {10.6084/m9.figshare.31224397}
}
```
