# LCDM as a Special Case of Energy-Flow Cosmology

**Full title:** LCDM as a Special Case of Energy-Flow Cosmology: Regime Structure, Empirical Confrontation, and the Limits of Background-Level Testing

**Author:** Morten Magnusson
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)
**Affiliation:** Symbiose Research, Sandnes, Norway
**Date:** April 6, 2026 -- v1.0
**DOI:** [10.6084/m9.figshare.31943361](https://doi.org/10.6084/m9.figshare.31943361)
**License:** CC-BY-4.0

## Abstract

Energy-Flow Cosmology (EFC) treats the universe as a continuous energy-flow system governed by entropy gradients, in which gravitational dynamics, structure formation, and regime transitions emerge from a single variational action. This paper demonstrates that the standard LCDM model arises as the *special-case limit* of EFC in the linear, homogeneous, high-density regime (L0/L1), analogous to the ideal gas law emerging from statistical mechanics. The EFC relativistic action structurally reduces to Friedmann-Poisson dynamics when the stiffness response K(rho) tends to infinity, the transition function T(a) tends to zero, and the gradient coordinate xi is much greater than one. DESI DR2 multi-probe analysis confirms this limit empirically: alpha = -0.14 +/- 0.21 (0.65 sigma from null), with Delta-AIC = +1.59 favouring LCDM in the background sector.

Beyond L0/L1, EFC produces testable predictions that LCDM does not: a narrow perturbation-sector survival valley (mu approximately 0.94, Sigma approximately 1.05, eta approximately 1.10), SPARC rotation-curve fits from a single screening parameter (k = 0.415 +/- 0.029) without dark matter, a void ISW sign-flip for deep voids (delta less than approximately -0.8), and a regime transition mu < 1 to mu > 1 from the same action. The validation ledger (v3.7, 204 publications, 100 registered tests) documents five historical falsifications, sealed blind predictions, and pre-registered falsification conditions. This consolidation paper brings together 14 months of systematic development, pipeline confrontation, and transparent failure documentation into a single reference.

## Core Equations

1. **Regime driver (Eq. 1):** chi = ell |grad S| / S_*
2. **Constitutive law (Eq. 2):** E_f = -kappa(chi) grad S
3. **Modified Poisson (Eq. 3):** nabla^2 Phi = 4 pi G_N mu(chi,k,z) rho_m delta
4. **Effective coupling (Eq. 4):** mu(chi,k,z) = 1 + epsilon(k) F(chi)
5. **Relativistic action (Eq. 5):** S_EFC = integral d^4x sqrt(-g) [F(phi)R/2 - K(rho)(nabla phi)^2/2 - V(phi) + lambda C[phi, nabla phi]] + S_m

## LCDM Reduction (Eq. 6)

K(rho) -> infinity, T(a) -> 0, xi >> 1 implies mu, Sigma, eta -> 1 implies Friedmann + Poisson

Three physical conditions (high density, early time, strong acceleration) collapse all EFC modifications to zero, recovering standard LCDM identically.

## Regime Structure (Table 1)

| Regime | Physical Domain | LCDM Status | EFC Prediction |
|--------|----------------|-------------|----------------|
| L0 | Global background (FLRW, H(z)) | Exact effective description | Suppressed by design: T(a) -> 0 |
| L1 | Linear perturbations (BAO, f sigma_8) | Excellent fit | Survival valley: mu ~ 0.94, Sigma ~ 1.05 |
| L2 | Non-linear structure (haloes, clusters) | Requires DM particle (undetected) | Emergent MOND-like; mu > 1 |
| L3 | Local dynamics (Solar System) | Exact via G_N | Theta(rho) -> 0: GR recovery |

## DESI DR2 Result

- Background coupling: alpha = -0.14 +/- 0.21 (0.65 sigma)
- Delta-AIC = +1.59 (LCDM preferred)
- Pre-DR2 alpha approximately -0.67 collapsed to approximately 0 under DR2 precision
- Seven robustness diagnostics (N1-N7) plus variant gravity (VG) test

## Gas-Law Analogy (Table 5)

The ideal gas law is to thermodynamics what LCDM is to cosmology: a correct and useful special case valid in one regime, embedded within a richer structure that becomes necessary when the system moves outside that regime.

## File Manifest

| File | Description |
|------|-------------|
| README.md | This documentation |
| index.json | Machine-readable structured index |
| schema.json | JSON Schema for package validation |
| metadata.json | Full metadata with EFC context |
| LCDM-special-case.jsonld | JSON-LD linked data descriptor |
| citations.bib | BibTeX references (27 entries) |
| src/lcdm_special_case.py | Python reference implementation |
| src/__init__.py | Package initialisation |
| data/lcdm_special_case_data.json | All tables, parameters, diagnostics |
| examples/demo_lcdm_special_case.py | Six demonstration scripts |

## Citation

```bibtex
@misc{magnusson2026lcdmspecialcase,
  author = {Magnusson, Morten},
  title = {{$\Lambda$CDM} as a Special Case of Energy-Flow Cosmology: Regime Structure, Empirical Confrontation, and the Limits of Background-Level Testing},
  year = {2026},
  publisher = {Figshare},
  doi = {10.6084/m9.figshare.31943361},
  url = {https://doi.org/10.6084/m9.figshare.31943361}
}
```
