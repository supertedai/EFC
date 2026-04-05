# EFC-C: A Thermodynamic Framework for Cognitive Entropy and Psychiatric Biomarkers

**Author:** Morten Magnusson  
**Affiliation:** Symbiose Research, Sandnes, Norway  
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)  
**DOI:** [10.6084/m9.figshare.31940505](https://doi.org/10.6084/m9.figshare.31940505)  
**Date:** March 31, 2026 (Research Note v0.1)

## Summary

EFC-C (Energy-Flow Cosmology – Cognition) models the brain as an open thermodynamic system governed by entropy-gradient dynamics. Unlike the Entropic Brain Hypothesis (EBH), which indexes conscious states by entropy *magnitude* alone, EFC-C predicts the *topological structure* of entropy gradients across cortical networks.

## Three Falsifiable Predictions

| # | Prediction | Consistency |
|---|-----------|-------------|
| P1 | Hub-to-periphery entropy gradient (centrifugal, maximal at DMN) | Consistent with fMRI (Lempel-Ziv, MSE at coarse scales) |
| P2 | Disorder-specific gradient inversions (schizophrenia: anterior excess; MDD: posterior bias) | Consistent with EEG MFE literature |
| P3 | Entropy threshold S_dot* for productive cognition | Consistent with disorders-of-consciousness research |

## Key Distinction from EBH

EBH is the scalar projection of the more complete EFC-C tensor field. EFC-C adds gradient direction and topology as measurable quantities.

## File Structure

```
├── README.md               # This file
├── index.json              # Machine-readable index
├── schema.json             # Validation schema
├── metadata.json           # Structured metadata
├── efc_cognition.jsonld    # JSON-LD linked data
├── citations.bib           # BibTeX references
├── src/
│   ├── __init__.py
│   └── efc_cognition.py    # Python implementation
├── data/
│   └── framework.json      # Predictions, comparisons, parameters
└── examples/
    └── demo_efc_c.py       # Executable demonstration
```
