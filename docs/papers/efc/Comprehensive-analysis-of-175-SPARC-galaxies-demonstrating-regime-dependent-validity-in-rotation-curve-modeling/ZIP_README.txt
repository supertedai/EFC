╔═══════════════════════════════════════════════════════════════════╗
║                   SPARC175 COMPLETE PACKAGE                       ║
║                   Regime-Dependent Validity                       ║
║                          Analysis                                 ║
╚═══════════════════════════════════════════════════════════════════╝

DOI: 10.6084/m9.figshare.31045126
Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
Date: January 11, 2026
License: CC-BY 4.0
Version: 1.0

═══════════════════════════════════════════════════════════════════

WHAT'S IN THIS ZIP
══════════════════

This package contains the complete analysis of 175 SPARC galaxies
demonstrating regime-dependent validity in rotation curve modeling.

📄 MAIN DOCUMENTS (start here!)
   • SPARC175_COMPLETE_PAPER.pdf - Full paper
   • README.md - Quick start guide
   • SPARC175_SUMMARY.md - Executive summary

📊 DATA FILES (data/)
   • sparc175_qc.json - Quality control log
   • sparc175_clean.json - Clean dataset (175 galaxies)
   • sparc175_fits.json - All fit results
   • sparc175_classified.json - Regime classifications
   • sparc175_statistics.json - Summary statistics

📈 FIGURES (figures/)
   • sparc175_regime_distribution.png
   • sparc175_aic_vs_latent.png
   • sparc175_success_by_bins.png

🐍 SCRIPTS (scripts/)
   • Complete Python pipeline for reproduction
   • All 5 analysis stages (QC → Documentation)

📋 METADATA
   • index.json - Machine-readable index
   • schema.json - Data validation schema
   • minimal_spec.tex - Mathematical specification
   • index.tex - LaTeX navigation

═══════════════════════════════════════════════════════════════════

QUICK START
═══════════

1. EXTRACT ZIP
   unzip SPARC175_COMPLETE_PACKAGE.zip

2. READ PAPER
   Open: SPARC175_COMPLETE_PAPER.pdf

3. EXPLORE DATA
   Any JSON viewer can open data/*.json files

4. VIEW FIGURES
   Open figures/*.png in any image viewer

5. REPRODUCE ANALYSIS (optional)
   pip install numpy scipy matplotlib
   cd scripts/
   python sparc175_hybrid.py         # Day 1: QC
   python sparc175_day2_fit.py       # Day 2: Fitting
   python sparc175_day3_classify.py  # Day 3: Classification
   python sparc175_day4_visualize.py # Day 4: Figures
   python sparc175_day5_document.py  # Day 5: Summary

═══════════════════════════════════════════════════════════════════

KEY RESULTS
═══════════

✓ Sample: 175 SPARC galaxies
✓ FLOW regime: 62 galaxies (35%) → 100% EFC success
✓ TRANSITION: 86 galaxies (49%) → Mixed dynamics
✓ LATENT regime: 27 galaxies (15%) → ~4% EFC success
✓ Statistical significance: p < 0.0001 (Mann-Whitney U)

CONCLUSION: Regime-dependent validity is real and significant!

═══════════════════════════════════════════════════════════════════

FILE STRUCTURE
══════════════

SPARC175_COMPLETE_PACKAGE/
├── README.md                     ← Start here!
├── SPARC175_COMPLETE_PAPER.pdf   ← Full paper
├── SPARC175_SUMMARY.md           ← Quick summary
├── COMPLETE_PACKAGE_LIST.txt     ← Full file list
├── data/
│   ├── sparc175_qc.json
│   ├── sparc175_clean.json
│   ├── sparc175_fits.json
│   ├── sparc175_classified.json
│   └── sparc175_statistics.json
├── figures/
│   ├── sparc175_regime_distribution.png
│   ├── sparc175_aic_vs_latent.png
│   └── sparc175_success_by_bins.png
└── scripts/
    ├── sparc175_hybrid.py (Day 1)
    ├── sparc175_day2_fit.py
    ├── sparc175_day3_classify.py
    ├── sparc175_day4_visualize.py
    └── sparc175_day5_document.py

═══════════════════════════════════════════════════════════════════

CITATION
════════

BibTeX:
@article{magnusson2026sparc175,
  title={Regime-Dependent Validity in Galaxy Rotation Curve 
         Modeling: Comprehensive Analysis of 175 SPARC Galaxies},
  author={Magnusson, Morten},
  journal={Figshare Preprint},
  year={2026},
  doi={10.6084/m9.figshare.31045126}
}

Plain text:
Magnusson, M. (2026). Regime-Dependent Validity in Galaxy 
Rotation Curve Modeling: Comprehensive Analysis of 175 SPARC 
Galaxies. Figshare. DOI: 10.6084/m9.figshare.31045126

═══════════════════════════════════════════════════════════════════

REPRODUCIBILITY
════════════════

✓ All analysis is deterministic
✓ Fixed random seeds (seed=42)
✓ No manual parameter tuning
✓ Complete code provided
✓ Explicit optimizer settings

Given the same SPARC data → same results guaranteed!

═══════════════════════════════════════════════════════════════════

CONTACT
═══════

Morten Magnusson
Email: morten@magnusson.as
Web: https://energyflow-cosmology.com/
ORCID: 0009-0002-4860-5095

═══════════════════════════════════════════════════════════════════

LICENSE
═══════

Creative Commons Attribution 4.0 International (CC-BY 4.0)

You are free to:
• Share — copy and redistribute
• Adapt — remix, transform, build upon

Under the terms:
• Attribution — cite the original work

═══════════════════════════════════════════════════════════════════

RELATED WORK
════════════

• N=20 Pilot Study: DOI 10.6084/m9.figshare.31007248
• EFC Framework: https://energyflow-cosmology.com/
• SPARC Database: Lelli et al. (2016), AJ, 152, 157

═══════════════════════════════════════════════════════════════════

THANK YOU FOR YOUR INTEREST!
═════════════════════════════

Questions? Contact: morten@magnusson.as

Visit: https://energyflow-cosmology.com/

╔═══════════════════════════════════════════════════════════════════╗
║  "Science advances when we map the boundaries of our theories,   ║
║           not when we pretend they have none."                    ║
╚═══════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════

GITHUB REPOSITORY
═════════════════

Primary repository: https://github.com/supertedai/EFC

All data, code, and documentation are maintained on GitHub:
• Complete analysis pipeline
• Development history
• Issue tracking
• Collaboration tools

Clone the repository:
git clone https://github.com/supertedai/EFC.git

