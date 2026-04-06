# EFC-C v2.0: Quantitative Entropy-Gradient Predictions for Cognitive States

A connectome-constrained framework with falsifiable diagnostic signatures.

Track 2: Neural Entropy

## Overview

This paper presents a revised and quantified version of Energy-Flow Cosmology--Cognition (EFC-C), a thermodynamic framework for neural entropy gradients. The central observable is the centrifugal entropy score kappa = mean(S_hub) / mean(S_periph), derived from the EFC cross-domain Bridge B1* equation without fitting parameters to neural data.

## Key Equation

```
kappa_healthy = C / (1 + lambda_2(W) * tau_c)
```

Where:
- C = k / a_G = 4.4 +/- 0.6 (fixed from SPARC galactic fit)
- lambda_2(W) = Fiedler eigenvalue of the normalized graph Laplacian
- tau_c = L_parcel^2 / D_eff ~ 3.5 s (cortical entropy redistribution timescale)

## Predictions

| Code | Prediction | Falsification |
|------|-----------|---------------|
| Q1 | kappa_healthy ~ 1.6 | r < 0.30 (n >= 20) or abs(z) > 3 |
| Q2a | alpha_AP_scz > alpha_AP_healthy | p > 0.05, n >= 15/group |
| Q2b | alpha_AP_mdd < alpha_AP_healthy | p > 0.05, n >= 15/group |
| Q2c | Delta_kappa correlates with Delta_lambda_2 | r < 0.25, n >= 30 |
| Q3 | kappa < 0.73 in disorders of consciousness | kappa_DoC > 0.73 |

## Files

```
EFC-C_Cognitive_Entropy_Gradients_v2/
  README.md                        # This file
  index.json                       # Machine-readable index
  schema.json                      # JSON Schema validation
  metadata.json                    # Structured metadata
  efc_c_v2.jsonld                  # JSON-LD linked data
  citations.bib                    # BibTeX references
  src/__init__.py                  # Package imports
  src/cognitive_entropy.py         # Python implementation
  data/cognitive_entropy_data.json # Structured data
  examples/demo_cognitive_entropy.py # Executable demo
```

## Citation

```bibtex
@misc{magnusson2026efcc_v2,
  author = {Magnusson, Morten},
  title  = {EFC-C v2.0: Quantitative Entropy-Gradient Predictions for Cognitive States},
  year   = {2026}
}
```

## License

CC-BY-4.0

## Author

Morten Magnusson
Symbiose Research, Sandnes, Norway
ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)
