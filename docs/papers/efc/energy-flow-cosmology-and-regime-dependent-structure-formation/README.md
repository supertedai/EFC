# Energy-Flow Cosmology and Regime-Dependent Structure Formation

**Paper III: A Thermodynamic Framework for Galaxy Formation Anomalies**

[![DOI](https://img.shields.io/badge/DOI-10.6084%2Fm9.figshare.31061872-blue)](https://doi.org/10.6084/m9.figshare.31061872)
[![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0002--4860--5095-green)](https://orcid.org/0009-0002-4860-5095)

## Series Context

This is **Paper III** of a three-paper empirical–synthetic sequence:

| Paper | Type | Content | DOI |
|-------|------|---------|-----|
| I | Empirical | Regime structure in SPARC rotation curves (N=175) | [10.6084/m9.figshare.31045126](https://doi.org/10.6084/m9.figshare.31045126) |
| II | Empirical | Galaxy abundance excess at z > 6 (COSMOS-Web) | TBD |
| **III** | **Interpretive** | **Physical framework consistent with I–II** | **[10.6084/m9.figshare.31061872](https://doi.org/10.6084/m9.figshare.31061872)** |

**Epistemic structure:** Papers I–II are descriptive and model-agnostic. Paper III is interpretive and physically constrained. No circularity: regimes are defined before EFC; EFC is applied afterward as an organizing framework.

## Abstract

Papers I and II of this series established empirical regime structure in two independent datasets: (I) morphology-dependent rotation curve behavior in 175 SPARC galaxies, and (II) order-of-magnitude galaxy abundance excesses at z > 6 in JWST COSMOS-Web data. This third paper introduces Energy-Flow Cosmology (EFC) as a physical framework consistent with both findings.

The core mechanism is entropy-gradient-driven energy flow, introduced through the phenomenological decomposition:

```
E_total = E_flow + E_latent
```

We show that this framework is consistent with:
- **(i)** The three-regime classification (FLOW, TRANSITION, LATENT) observed in galactic dynamics
- **(ii)** Accelerated structure formation in the early universe

The interpretation is offered as an organizing framework, not a replacement for ΛCDM.

## Key Results

### Regime Classification

| Regime | L Range | Physical Interpretation |
|--------|---------|------------------------|
| FLOW | L < 0.25 | Near-equilibrium; simple models valid |
| TRANSITION | 0.25–0.45 | Mixed dynamics |
| LATENT | L > 0.45 | Non-equilibrium dominated |

### Cross-Scale Correspondence

| Gradient | Galactic (Paper I) | Cosmological (Paper II) |
|----------|-------------------|------------------------|
| Steep | LSB: 100% success | z > 10: 1000× excess |
| Shallow | Barred: ~4% success | z < 3: ΛCDM valid |

## Testable Predictions

- **P1:** Regime classification replicates on independent samples (LITTLE THINGS, DMS)
- **P2:** Abundance excess continues monotonically to z > 15
- **P3:** Morphological complexity correlates with regime membership across datasets
- **P4:** FIRE simulation cusp-core transitions align with EFC regime boundaries

## Scope Limitation

**No claim of model replacement is made.** The framework is proposed strictly as an organizing physical interpretation consistent with the reported empirical regime structure.

## Files

```
paper3_package/
├── Paper3_EFC_Regime_Synthesis_FINAL.pdf    # Main paper
├── Paper3_EFC_Submission_Draft_v03.docx     # Editable version
├── metadata.json                             # Structured metadata
├── index.json                                # Figshare-style index
├── schema.jsonld                             # Schema.org data
├── README.md                                 # This file
├── CITATION.cff                              # Citation metadata
└── supplementary/
    └── regime_summary.json                   # Regime classification data
```

## Citation

```bibtex
@article{magnusson2026efc3,
  author  = {Magnusson, Morten},
  title   = {Energy-Flow Cosmology and Regime-Dependent Structure Formation},
  subtitle = {Paper III: A Thermodynamic Framework for Galaxy Formation Anomalies},
  year    = {2026},
  doi     = {10.6084/m9.figshare.31061872},
  url     = {https://doi.org/10.6084/m9.figshare.31061872},
  publisher = {Figshare}
}
```

## Links

- **Website:** https://energyflow-cosmology.com
- **GitHub:** https://github.com/supertedai/EFC
- **Figshare:** https://figshare.com/authors/Morten_Magnusson

## License

This work is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

---

**Author:** Morten Magnusson  
**Affiliation:** Energy-Flow Cosmology Initiative, Norway  
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)
