# EFC White Paper Series (Parts 1-4)

**Author:** Morten Magnusson (ORCID [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)) · Symbiose Research, Sandnes, Norway
**License:** CC-BY-4.0 · **Date:** April 2026

---

## Overview

The EFC White Paper series is the canonical four-part reference for Energy-Flow Cosmology.
It establishes the theoretical foundations, derives the field equations, documents the complete
validation record, and proposes the regime susceptibility function for cross-scale mapping.

## Parts

| Part | Title | DOI | Key Result |
|---|---|---|---|
| **1** | [Recovery Conditions and the LCDM Limit](White_paper_part_1_efc_recovery_limits/) | [10.6084/m9.figshare.31970886](https://doi.org/10.6084/m9.figshare.31970886) | Three independent recovery conditions; EFC contains LCDM (perturbation sector) |
| **2** | [Field Equations and Observable Mapping](White_paper_part_2_efc_field_equations_observables/) | [10.6084/m9.figshare.31970898](https://doi.org/10.6084/m9.figshare.31970898) | Entropy field S(a), coupling mu(a), growth rate f*sigma_8, response surface R(k,S) |
| **3** | [Data, Validation Ledger, and Falsification Protocol](White_paper_part_3_efc_validation_falsification/) | [10.6084/m9.figshare.31970904](https://doi.org/10.6084/m9.figshare.31970904) | 102 registered tests; 5 kill criteria; sealed blind predictions |
| **4** | [Regime Susceptibility and Cross-Scale Mapping](White_paper_part_4_efc_regime_susceptibility/) | [10.6084/m9.figshare.31970907](https://doi.org/10.6084/m9.figshare.31970907) | T(S) susceptibility function; entropic continuum; dynamical dark energy |

## Reading Order

The papers form a logical chain:

1. **Part 1** establishes that EFC reduces to LCDM/GR under three independent limits (foundation)
2. **Part 2** derives the field equations and maps them to testable observables (equations)
3. **Part 3** documents the full validation record and defines falsification criteria (evidence)
4. **Part 4** addresses the remaining cross-scale gap with the susceptibility function (extension)

## Key Numbers

- **Recovery conditions:** 3 independent sufficient conditions (Theorems 1-3)
- **Core coupling:** mu(a) = 1 + beta * S(a), beta ~ 0.16 from SPARC
- **Signal:** alpha_L2 = -1.00 +/- 0.46 (2.20 sigma, Delta_AIC = -2.91)
- **Validation:** 102 tests (66 pass, 17 failed, 5 falsified with successor)
- **Kill criteria:** 5 sharp conditions for Stage-IV surveys
- **Susceptibility:** T(S) = S_0(1-S_0)/[S(1-S)], self-regulating
- **Equation of state:** w(a) = -beta(S) * a (dynamical dark energy prediction)
- **Open problem:** Full background H(z) recovery (Level 3)

## AI-Friendly Packages

Each subdirectory contains a full 10/10 AI-friendly package with:
- `README.md` — Human-readable summary with TL;DR table
- `index.json` — Machine-readable structured metadata
- `metadata.json` — Extended metadata
- `schema.json` — JSON Schema for key data objects
- `*.jsonld` — Schema.org linked data
- `citations.bib` — BibTeX references
- `data/` — Key tables and results as JSON
- `src/` — Python implementation of core equations
- `examples/` — Demo scripts reproducing key results
