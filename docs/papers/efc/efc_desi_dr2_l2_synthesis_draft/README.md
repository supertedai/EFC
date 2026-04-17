# EFC L2→L3 Regime-Transition Synthesis for DESI DR2 (DRAFT)

**Status:** DRAFT — synthesis of pre-sealed + fitted DR2 responses; no new DOI yet.
**Author:** Morten Magnusson (ORCID: 0009-0002-4860-5095)
**Date drafted:** 2026-04-17
**License:** CC-BY-4.0
**Anchor DOIs:**
- [10.6084/m9.figshare.31985163](https://doi.org/10.6084/m9.figshare.31985163) — Regime-Transition fit to DESI DR2 BAO
- [10.6084/m9.figshare.32013156](https://doi.org/10.6084/m9.figshare.32013156) — Sealed freeze_20260218 blind predictions
- [10.6084/m9.figshare.31333414](https://doi.org/10.6084/m9.figshare.31333414) — Sign lemma (CLASS v3.3.4; 0/39998 sign violations)

## Overview

Synthesises the EFC response to DESI DR2 BAO (arXiv:2503.14738; w₀wₐ preferred at 3.1σ) and Nature Astronomy (DOI 10.1038/s41550-025-02669-6). Ties three existing EFC DOI artefacts into a single L2→L3 narrative: the fitted regime-transition paper (31985163), the sealed freeze_20260218 predictions (32013156), and the CLASS sign-lemma structural constraint (31333414). No new parameters; recovers the scalar-tensor interpretation of T(S) susceptibility as the cause of w(z) evolution.

## Key Numbers (DOI-anchored, sealed)

From freeze_20260218 (DOI 32013156):
| Quantity | EFC | ΛCDM | σ |
|---|---|---|---|
| D_H/r_d (z=0.7) | 19.797 | 20.719 | 2.3 |
| D_H/r_d (z=1.0) | 16.527 | 17.466 | 3.1 |
| fσ₈ (z=0.7) | 0.430 | 0.449 | 2.0 |
| fσ₈ crossover | z = 2.042 | — | — |

From EFC-BG-NoGo application log: DOI 31985163 applied 2026-04-17T00:16:31Z to the No-Go theorem package.

From Symbiose inference daemon:
- `bao_desi_y1`: Δχ² = −22.01 (EFC preferred, 5-fold CV all pass)
- `bao_boss_dr12`: Δχ² = −7.77 (EFC preferred, k_eff = 0, χ² = 2.18)
- `hz_chronometers`: Δχ² = −0.17 (sub-statistical, consistent)

## Sealed Predictions

| ID | Prediction | Kill if |
|---|---|---|
| P1 | fσ₈(z=0.7) = 0.430 ± 0.02 | DESI DR3 RSD measures > 0.449 within 1.5σ |
| P2 | D_H/r_d(z=1.0) = 16.527 | Direct DR3 LRG3 measurement > 17.466 within 2σ |
| P3 | w₀ > −1 and wₐ < 0 in EFC-effective parametrisation | DR3 joint constraint excludes this quadrant |

## Data Sources (all DOI-anchored)

- DOI 31985163 — Regime-transition fit to DESI DR2 BAO + Pantheon+ + H(z) chronometers
- DOI 32013156 — Sealed blind predictions, freeze_20260218 (hash 7a850cfa58477701)
- DOI 31333414 — CLASS sign-lemma (structural constraint)
- DOI 31026151 — H₀ tension analysis (evidence-register empirical)
- DOI 31222903 — Regime classification framework (methodological)
