# EFC Regime Transition Framework: A CMB-Consistent Approach to Late-Time Cosmology

**Author:** Morten Magnusson  
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)  
**DOI:** [10.6084/m9.figshare.31096951](https://doi.org/10.6084/m9.figshare.31096951)  
**Date:** January 20, 2026  
**License:** MIT (code), CC-BY-4.0 (documentation)

## Overview

This repository contains the complete research package for "Dynamical Regime Transitions in Cosmology: A CMB-Safe Framework", including the published paper, figures, numerical code, and full documentation.

**Key Result:** We demonstrate that regime-dependent cosmological modifications can achieve CMB safety (G_CMB ≈ 10⁻¹²) through dynamical gating rather than fine-tuning, using Landau theory for phase transitions.

## Repository Structure

```
EFC-Regime-Transition-Framework-A-CMB-Consistent-Approach-to-Late-Time-Cosmology/
├── paper/                          # Published article
│   ├── magnusson2026_efc_regime_transitions.pdf
│   └── magnusson2026_efc_regime_transitions.md
├── figures/                        # All figures from paper
│   ├── figure1_regime_transition_dynamics.png
│   └── figure2_class_integration_results.png
├── code/                          # Numerical implementation
│   ├── landau_solver.py          # RK4 integration of Landau equation
│   ├── gating_function.py        # G(z) computation
│   ├── cmb_safety_check.py       # Verification tests
│   └── plotting/                 # Figure generation scripts
├── data/                          # Numerical solutions
│   ├── gz_solution.csv           # Complete G(z) solution
│   ├── parameters.json           # Fiducial parameters
│   └── cmb_verification.csv      # CMB safety verification data
├── docs/                          # Extended documentation
│   ├── complete_documentation.md # Full 47-page technical document
│   ├── class_implementation.md   # CLASS integration guide
│   └── reproduction_guide.md     # Step-by-step instructions
├── README.md                      # This file
├── LICENSE                        # MIT license
└── CITATION.cff                   # Citation metadata
```

## Quick Start

### Requirements

- Python 3.8+
- NumPy, SciPy, Matplotlib
- CLASS v3.2.0 (optional, for Boltzmann code integration)

### Running the Code

```bash
# Clone repository
git clone [your-repo-url]
cd EFC-Regime-Transition-Framework-A-CMB-Consistent-Approach-to-Late-Time-Cosmology

# Run Landau solver
cd code
python landau_solver.py

# Generate figures
cd plotting
python generate_all_figures.py

# Verify CMB safety
python cmb_safety_check.py
```

**Expected runtime:** ~2 hours on standard workstation

## Main Results

| Parameter | Value | Interpretation |
|-----------|-------|----------------|
| G(z=1100) | 1.00×10⁻¹² | CMB safe (8 orders below threshold) |
| G(z=10) | 9.20×10⁻¹⁶ | Intermediate-z suppressed |
| G(z=2) | 0.25 | Partial late-time activation |
| G(z=0) | 0.9999 | Full activation today |

**CMB Safety Margin:** 8 orders of magnitude below 10⁻⁴ detection threshold

## Citation

If you use this work, please cite:

```bibtex
@misc{magnusson2026efc,
  author = {Magnusson, Morten},
  title = {Dynamical Regime Transitions in Cosmology: A CMB-Safe Framework},
  year = {2026},
  doi = {10.6084/m9.figshare.31096951},
  publisher = {figshare},
  note = {ORCID: 0009-0002-4860-5095}
}
```

## Key Features

✅ **CMB-safe by construction** - G_CMB ≈ 10⁻¹² from dynamics, not tuning  
✅ **Fully reproducible** - Complete code and data included  
✅ **Mathematically rigorous** - Landau theory framework  
✅ **CLASS-compatible** - Ready for Boltzmann code integration  
✅ **Open access** - MIT/CC-BY-4.0 licenses

## What This Work Shows

**This work demonstrates:**
- Regime-dependent modifications CAN be CMB-safe
- Landau theory provides natural gating mechanism
- Delayed activation (χ crosses χ_c at z≈50, effect at z<2) is physical
- Framework applicable beyond EFC (modified gravity, dark energy, etc.)

**This work does NOT claim:**
- Observational preference for EFC
- Discovery of new physics
- Solution to cosmological tensions
- That specific coupling produces observable effects

**Scientific value:** Establishes testbed for future regime-dependent theories, with honest assessment of current observability limits.

## File Descriptions

### Paper (peer-reviewed format)

- `magnusson2026_efc_regime_transitions.pdf` - Main article (15 pages, publication-ready)
- `magnusson2026_efc_regime_transitions.md` - Markdown source

### Figures (high-resolution)

- `figure1_regime_transition_dynamics.png` - Complete G(z) solution showing CMB safety
- `figure2_class_integration_results.png` - CLASS Boltzmann code verification

### Code (Python 3)

- `landau_solver.py` - 4th-order Runge-Kutta integration
- `gating_function.py` - G(φ) computation and analysis
- `cmb_safety_check.py` - Verification suite
- `plotting/` - All figure generation scripts

### Data (CSV/JSON)

- `gz_solution.csv` - Complete G(z) from z=3000 to z=0 (15,000 points)
- `parameters.json` - All fiducial parameters (Planck 2018 + regime)
- `cmb_verification.csv` - Visibility-weighted CMB safety verification

### Documentation

- `complete_documentation.md` - Full technical document (47 pages)
- `class_implementation.md` - CLASS integration guide
- `reproduction_guide.md` - Step-by-step reproduction instructions

## License

**Code:** MIT License - Free to use, modify, and distribute  
**Documentation/Paper:** CC-BY-4.0 - Free to share with attribution

See LICENSE file for details.

## Contact

**Author:** Morten Magnusson  
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)  
**Repository:** [GitHub link]  
**Issues:** Use GitHub Issues for questions or bug reports  
**Data/Code DOI:** [10.6084/m9.figshare.31096951](https://doi.org/10.6084/m9.figshare.31096951)

## Changelog

**v1.0 (2026-01-20)** - Initial public release
- Complete paper
- All figures
- Numerical code
- Full documentation
- CMB verification

## Acknowledgments

This work used:
- CLASS Boltzmann code (Blas et al. 2011)
- Planck 2018 cosmological parameters
- Python scientific stack (NumPy, SciPy, Matplotlib)

## Related Work

This framework builds on and addresses limitations of:
- Previous EFC-CMB attempts (failed due to H(z) modifications)
- Modified gravity theories (CMB compatibility challenges)
- Early dark energy proposals (fine-tuning issues)

**Next steps (future work):**
1. Derive physical χ(z) from first principles
2. Test multiple coupling channels
3. Full MCMC likelihood analysis
4. Comparison with Planck+BAO+structure growth data

---

**Last updated:** January 20, 2026  
**Version:** 1.0  
**Status:** Published and openly available
