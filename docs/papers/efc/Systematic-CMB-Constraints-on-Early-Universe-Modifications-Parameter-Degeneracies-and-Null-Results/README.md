# EFC-CMB Testing Results

## Overview

This package contains complete results from systematic testing of Energy-Flow Cosmology (EFC) mechanisms against Planck 2018 CMB data.

**DOI:** 10.6084/m9.figshare.31095466

**Date:** January 20, 2026

## Summary

Two EFC-inspired mechanisms were tested:
1. **κ̇ modification** (Thomson scattering) - REJECTED
2. **H(z) modification** (background energy density) - REJECTED (after accounting for parameter degeneracies)

## Key Finding

Initial 1D analysis suggested preference for ε ≈ +3% extra energy (Δχ² ≈ -65), but 2D parameter grid revealed this was a degeneracy artifact with h. True minimum at ε ≈ 0 (Δχ² ≈ -1).

**Lesson:** Parameter degeneracies can create false signals. Multi-dimensional analysis essential.

## Contents

### Documents
- `EFC_CMB_Testing_Results.pdf` - Complete publication-ready document
- `FINAL_ANALYSIS_1D_VS_2D.md` - Detailed comparison of 1D vs 2D results
- `CORRECTED_FINAL_SUMMARY.md` - Summary of corrected H(z) analysis

### Figures
- `kappa_sweep_final.png` - κ̇ mechanism results (Δχ² vs boost)
- `grid_2d_landscape.png` - 2D parameter space (ε vs h)
- `grid_1d_slices.png` - 1D slices through 2D space
- `efc_hz_corrected_final.png` - Corrected H(z) sweep results

### Data
All numerical results, CLASS output files, and analysis scripts available in full repository.

## Methods

**Data:** Planck 2018 TT spectrum (2507 points, ℓ = 2-2508)

**Tools:** CLASS v3.2.0 (modified), Python scientific stack

**Analysis:** 
- Amplitude marginalization
- χ² computation with Δχ² relative to baseline
- 1D parameter sweeps (7 points for κ̇, 10 for H(z))
- 2D parameter grid (77 CLASS runs: 11 ε × 7 h values)

## Results Summary

### κ̇ Mechanism
| Boost | χ²/dof | Δχ² | Result |
|-------|--------|-----|--------|
| 0% | 1.1853 | 0 | **MINIMUM** |
| ±1% | 1.1875 | +5.4 | Worse |

**Conclusion:** No preference for κ̇ modification. Standard ΛCDM preferred.

### H(z) Mechanism
| ε | h | Δχ² | Result |
|---|---|-----|--------|
| 0% | 0.6736 | 0 | Baseline |
| -0.5% | 0.6736 | -1.26 | **True minimum** |
| +3% | 0.6736 | +46 | 1D artifact |

**Conclusion:** No preference for ε ≠ 0 when h allowed to vary. Parameter degeneracy explains 1D "signal".

## EFC-R Regime Interpretation

These null results should be understood in context:

**CMB Epoch = L0-L1 Regime**
- Linear perturbations
- Radiation-dominated
- Standard physics expected to dominate

**Our Results Confirm This:**
- ΛCDM provides best fit (χ²/dof ≈ 1.2)
- No EFC modifications improve description
- This is *consistent* with EFC-R framework

**Where EFC Should Be Tested:**
- Galaxy formation (z ~ 2-6): Non-linear collapse
- Cosmic web (z ~ 0-2): Large-scale structure
- Late-time acceleration: H₀ tension, dark energy

**Key Point:** *A theory that knows where it does not apply is a stronger theory.* 

These CMB constraints help define EFC boundaries, guiding future tests toward regimes where EFC effects are predicted to matter (non-linear structure formation, not linear CMB).

## Technical Details

### CLASS Modifications

**κ̇ implementation (thermodynamics.c, line 2961):**
```c
kappa_dot *= (1.0 + boost * tanh((z - 700.0) / 200.0));
```

**H(z) implementation (background.c, line 575):**
```c
if (fabs(z - z_t) < 200) {
    double f_window = exp(-0.5 * pow((a - a_t) / Delta, 2));
    rho_EFC = epsilon * rho_tot * f_window;  // Corrected scaling
}
```

### Critical Correction

Original implementation used `ε × ρ_crit,0 × a^(-4)`, making ε relative to today's density. This created ~10^9 amplification at z~1100, leading to catastrophic fits.

Corrected version uses `ε × ρ_tot(a)`, making ε the actual fractional contribution at recombination.

## Reproducibility

All analysis is fully reproducible:
1. Planck 2018 data (publicly available)
2. Modified CLASS source code (provided)
3. Parameter sweep scripts (provided)
4. Analysis Python scripts (provided)

## Citation

If you use these results, please cite:

```
EFC-CMB Testing Results (2026)
DOI: 10.6084/m9.figshare.31095466
```

## Contact

For questions about methodology or data, please open an issue in the repository.

## License

Code: MIT License
Data: CC BY 4.0
Documentation: CC BY 4.0

## Acknowledgments

- CLASS Boltzmann code (Blas et al. 2011)
- Planck Collaboration for publicly available data
- NumPy, SciPy, Matplotlib for analysis tools
