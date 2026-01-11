# SPARC175: Regime-Dependent Validity Analysis

**Comprehensive analysis of 175 SPARC galaxies demonstrating regime-dependent validity in rotation curve modeling**

**DOI:** 10.6084/m9.figshare.31045126  
**Author:** Morten Magnusson (ORCID: 0009-0002-4860-5095)  
**Date:** January 2026  
**License:** CC-BY 4.0

---

## Overview

This repository contains the complete analysis of 175 galaxies from the Spitzer Photometry and Accurate Rotation Curves (SPARC) database. We demonstrate that rotation curve modeling exhibits regime-dependent validity: models achieve 100% success in low-complexity systems (FLOW regime) but systematically fail in high-complexity systems (LATENT regime).

**Key Finding:** Regime separation is highly statistically significant (Mann-Whitney U test, p < 0.0001).

---

## Repository Structure

```
sparc175/
├── README.md                          # This file
├── SPARC175_COMPLETE_PAPER.md         # Main paper (Markdown)
├── SPARC175_COMPLETE_PAPER.pdf        # Main paper (PDF)
├── SPARC175_SUMMARY.md                # Executive summary
├── index.json                         # Metadata index
├── schema.json                        # Data schema definition
├── minimal_spec.tex                   # LaTeX specification
├── index.tex                          # LaTeX index
├── data/
│   ├── sparc175_qc.json              # Quality control log
│   ├── sparc175_clean.json           # Clean dataset (175 galaxies)
│   ├── sparc175_fits.json            # Fit results (all galaxies)
│   ├── sparc175_classified.json      # Regime classification
│   └── sparc175_statistics.json      # Summary statistics
├── figures/
│   ├── sparc175_regime_distribution.png
│   ├── sparc175_aic_vs_latent.png
│   └── sparc175_success_by_bins.png
└── scripts/
    ├── sparc175_day1_qc.py           # Quality control
    ├── sparc175_day2_fit.py          # Fitting pipeline
    ├── sparc175_day3_classify.py     # Classification
    ├── sparc175_day4_visualize.py    # Visualization
    └── sparc175_day5_document.py     # Documentation
```

---

## Quick Start

### View Results

1. **Read the paper:** `SPARC175_COMPLETE_PAPER.pdf`
2. **See summary:** `SPARC175_SUMMARY.md`
3. **Explore data:** Open any `.json` file in `data/`
4. **View figures:** All figures in `figures/`

### Reproduce Analysis

```bash
# Install dependencies
pip install numpy scipy matplotlib tqdm

# Run full pipeline (takes ~30 minutes)
python scripts/sparc175_day1_qc.py       # Quality control
python scripts/sparc175_day2_fit.py      # Fit all galaxies
python scripts/sparc175_day3_classify.py # Classify regimes
python scripts/sparc175_day4_visualize.py # Generate figures
python scripts/sparc175_day5_document.py  # Create summary
```

**Note:** Original SPARC data required (Lelli et al., 2016). Download from http://astroweb.cwru.edu/SPARC/

---

## Key Results

### Regime Distribution
- **FLOW regime:** 62 galaxies (35.4%) - EFC 100% success
- **TRANSITION regime:** 86 galaxies (49.1%) - Mixed dynamics
- **LATENT regime:** 27 galaxies (15.4%) - EFC ~4% success

### Statistical Significance
- **Mann-Whitney U test:** p < 0.0001 (FLOW vs LATENT separation)
- **Regimes are highly significantly distinct**

### Fit Quality
- **FLOW regime:** χ²/dof = 2.05 ± 2.82
- **LATENT regime:** χ²/dof = 297.83 ± 553.50

---

## Data Files

### sparc175_qc.json
Quality control log for all 175 galaxies:
- Data integrity checks
- Sample size validation
- Error validation
- Flagged issues

### sparc175_clean.json
Clean dataset after QC:
- Rotation curve data (r, v_obs, v_err)
- Baryonic components (v_gas, v_disk, v_bulge)
- All 175 galaxies included

### sparc175_fits.json
Fit results for all galaxies:
- EFC-fit parameters (v_flat, r_turnon, sharpness)
- ΛCDM parameters (V_200, r_s)
- χ²/dof for each model
- AIC/BIC comparison
- Residual diagnostics

### sparc175_classified.json
Regime classification:
- Latent proxy L for each galaxy
- Regime assignment (FLOW/TRANSITION/LATENT)
- Statistical metrics
- Complete results

### sparc175_statistics.json
Summary statistics:
- Regime counts and percentages
- Mean values per regime
- Statistical test results
- Key findings

---

## Figures

### Figure 1: Regime Distribution
Three-panel figure showing:
- Regime counts (bar chart)
- EFC success rate by regime
- Fit quality distribution (boxplot)

### Figure 2: ΔAIC vs Latent Proxy
Scatter plot with:
- Color-coded regimes
- Decision boundaries (ΔAIC = ±10)
- Regime separation visible

### Figure 3: Success Rate by Bins
Two-panel figure:
- EFC win rate vs complexity bins
- Sample distribution across bins

---

## Methodology

### Model: EFC-fit (Ultra-Phenomenological)

```
v(r) = v_flat × sqrt(1 - exp(-(r/r_turnon)^sharpness))
```

**Critical acknowledgment:** This is NOT physically derived. It is a flexible fitting function used solely for regime classification.

### Comparison: ΛCDM-NFW

```
v²(r) = V_200² × [ln(1+x) - x/(1+x)] / [ln(1+c) - c/(1+c)]
where x = r/r_s, c = 10
```

### Classification Criteria

- **FLOW:** ΔAIC ≤ -10 AND χ²_red < 20
- **TRANSITION:** -10 < ΔAIC < +10 OR 20 < χ²_red < 50
- **LATENT:** ΔAIC ≥ +10 OR χ²_red > 50

### Latent Proxy

```
L = 0.4 × |ρ_radial| + 0.3 × sign_rate + 0.3 × (χ²_red/10)
```

Where:
- ρ_radial: Spearman correlation (residuals vs radius)
- sign_rate: Sign changes per data point
- χ²_red/10: Normalized fit quality

---

## Reproducibility

All analysis is fully reproducible:
- ✅ Fixed random seeds (seed=42)
- ✅ Explicit optimizer settings
- ✅ No manual tuning
- ✅ Deterministic algorithms

**Given the same SPARC data, the same results will be obtained.**

---

## Citation

```bibtex
@article{magnusson2026sparc175,
  title={Regime-Dependent Validity in Galaxy Rotation Curve Modeling: Comprehensive Analysis of 175 SPARC Galaxies},
  author={Magnusson, Morten},
  journal={Figshare Preprint},
  year={2026},
  doi={10.6084/m9.figshare.31045126}
}
```

---

## Related Work

- **N=20 Pilot Study:** DOI: 10.6084/m9.figshare.31007248
- **EFC-R Framework:** https://energyflow-cosmology.com/
- **SPARC Database:** Lelli et al. (2016), AJ, 152, 157

---

## Contact

**Morten Magnusson**  
Email: morten@magnusson.as  
Web: https://energyflow-cosmology.com/  
ORCID: 0009-0002-4860-5095

---

## License

This work is licensed under Creative Commons Attribution 4.0 International (CC-BY 4.0).

You are free to:
- Share — copy and redistribute
- Adapt — remix, transform, build upon

Under the terms:
- Attribution — cite the original work
- No additional restrictions

---

## Acknowledgments

This work made use of:
- SPARC database (Lelli et al., 2016)
- Python scientific stack (NumPy, SciPy, Matplotlib)
- Differential evolution optimizer (scipy.optimize)

---

**Last updated:** January 2026  
**Version:** 1.0
