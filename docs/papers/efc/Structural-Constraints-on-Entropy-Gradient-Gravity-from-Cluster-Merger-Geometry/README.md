# Structural Constraints on Entropy-Gradient Gravity from Cluster Merger Geometry

**Falsification of Local Couplings and Predictive Tests of Non-Local Formulations**

**Author:** Morten Magnusson  
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)  
**DOI:** [10.6084/m9.figshare.31173850](https://doi.org/10.6084/m9.figshare.31173850)  
**Type:** Reproducible Technical Constraint Study  
**Version:** 1.0.0  
**Date:** 2026-01-28  
**License:** CC-BY 4.0  

---

## Summary

This dataset provides a falsifiable test framework for entropy-gradient gravity theories (specifically Energy-Flow Cosmology, EFC) using galaxy cluster merger geometry. The work establishes:

1. **A hard constraint (BC-001):** Local entropy-gradient couplings are ruled out at cluster-merger scales
2. **Structural requirements (BC-002):** Any viable EFC-type theory must have non-local response and collisionless-component dominance  
3. **A predictive model (BC-003):** A minimal w(M,t) formulation with one global parameter
4. **Falsifiable predictions (BC-004):** Predicted parameters for MACS J0025 and Abell 520

## What This Is

- A **structural constraint study** establishing necessary conditions for entropy-based gravity
- A **reproducible pipeline** for testing gravitational theories against cluster merger geometry
- **Falsifiable predictions** ready for validation against real lensing data

## What This Is NOT

- An empirical validation against observed κ-maps (we use synthetic reconstructions)
- A complete alternative to dark matter
- A proof that EFC explains cluster dynamics

## Contents

| File | Description |
|------|-------------|
| `EFC_Bullet_Cluster_Constraint_Note.pdf` | Main technical document |
| `EFC_Bullet_Cluster_Constraint_Note.tex` | LaTeX source |
| `code/` | Complete Python pipeline (17 scripts) |
| `figures/` | All generated visualizations |
| `data/` | Synthetic test data documentation |

## Key Results

### Falsified (BC-001)
Local gradient coupling: G_eff ∝ |∇ln ρ_b|  
Result: 0/42 parameter combinations pass geometric criteria

### Required Structure (BC-002)
- Non-local scale: L₀ ~ 200 kpc (~ 0.8 × R_core)
- Component weighting: w ~ 20 (collisionless >> collisional)

### Predictions (BC-003, BC-004)
Using locked η = 66.2:

| Cluster | w_pred | L₀ (kpc) | Test Status |
|---------|--------|----------|-------------|
| Bullet | 20.0 | 200 | calibration |
| MACS J0025 | 23.9 | 120 | PASS (synthetic) |
| Abell 520 | 28.2 | 160 | PASS geometry (synthetic) |

## Reproducibility

```bash
# Install dependencies
pip install numpy scipy matplotlib astropy

# Run full test suite
cd code/
python run_all_tests.py
```

## Data Limitations

All κ-maps are **synthetic reconstructions** from published parameters (Brownstein & Moffat 2007, Bradač et al. 2006). Real FITS lensing data validation is pending.

## Citation

```bibtex
@misc{magnusson2026efc,
  author = {Magnusson, Morten},
  title = {Structural Constraints on Entropy-Gradient Gravity from Cluster Merger Geometry},
  year = {2026},
  publisher = {Figshare},
  doi = {10.6084/m9.figshare.31173850},
  url = {https://doi.org/10.6084/m9.figshare.31173850}
}
```

## Contact

Morten Magnusson — ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)

---

*This work represents methodology development, not observational confirmation. The value lies in establishing what any entropy-based gravity theory must satisfy to explain cluster mergers.*
