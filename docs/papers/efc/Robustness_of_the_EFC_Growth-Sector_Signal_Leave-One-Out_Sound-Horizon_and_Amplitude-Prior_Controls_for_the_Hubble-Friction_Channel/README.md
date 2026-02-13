# Robustness of the EFC Growth-Sector Signal

Leave-One-Out, Sound-Horizon, and Amplitude-Prior Controls for the Hubble-Friction Channel.

**DOI:** 10.6084/m9.figshare.31332730

**Date:** February 2026

## Summary

A joint Bayesian fit to 14 BAO distance measurements and 7 fσ₈ growth-rate data points yields **α = −1.00 ± 0.46 (2.20σ)** under the N2a nuisance configuration. Three independent robustness controls all pass:

1. **N1 (Sound-horizon independence):** α insensitive to r_d within Planck posterior — PASSED
2. **N2 (Amplitude-prior control):** Signal strengthens under tight prior (1.7σ → 2.2σ) — PASSED
3. **T7 (Leave-one-out):** 7/7 pass, α ∈ [−1.11, −0.88] — PASSED

The ~2σ hint for late-time growth suppression is not an artefact.

## Contents

| File | Description |
|------|-------------|
| `EFC_Growth_Sector_Robustness_DOI_31332730.pdf` | Authoritative PDF (5 pages) |
| `index.json` | Machine-readable metadata, LOO data, fσ₈ compilation |
| `schema.json` | JSON Schema validation |
| `EFC-Growth-Sector-Robustness.jsonld` | JSON-LD semantic metadata |
| `metadata.json` | Comprehensive project metadata |
| `citations.bib` | BibTeX references |
| `README.md` | This file |

## Data

### BAO (14 points)
D_M/r_d and D_H/r_d from 6dFGS, SDSS MGS, BOSS DR12, eBOSS LRG/QSO/ELG, Ly-α (z = 0.106–2.334).

### fσ₈ (7 points)

| Survey | z | fσ₈ | σ |
|--------|---|------|---|
| 6dFGS | 0.02 | 0.360 | 0.040 |
| SDSS MGS | 0.15 | 0.490 | 0.055 |
| BOSS DR12 | 0.38 | 0.430 | 0.054 |
| BOSS DR12 | 0.51 | 0.452 | 0.057 |
| BOSS DR12 | 0.61 | 0.457 | 0.052 |
| VIPERS | 0.77 | 0.420 | 0.060 |
| FastSound | 0.85 | 0.380 | 0.080 |

## Leave-One-Out Results

| Drop | z | α ± σ | |α|/σ | ΔAIC | Pass |
|------|---|-------|------|------|------|
| [0] | 0.02 | −0.88 ± 0.48 | 1.84 | −1.59 | Yes |
| [1] | 0.15 | −1.11 ± 0.46 | 2.42 | −3.97 | Yes |
| [2] | 0.38 | −0.98 ± 0.46 | 2.12 | −2.58 | Yes |
| [3] | 0.51 | −1.03 ± 0.47 | 2.22 | −2.97 | Yes |
| [4] | 0.61 | −1.04 ± 0.48 | 2.19 | −3.20 | Yes |
| [5] | 0.77 | −1.00 ± 0.47 | 2.12 | −2.70 | Yes |
| [6] | 0.85 | −0.97 ± 0.46 | 2.09 | −2.54 | Yes |

**Robustness score: 7/7 (100%)**

## Caveats

- 2.20σ is sub-detection-threshold (p ≈ 0.028, below 3σ evidence)
- ΔBIC = −0.91: Bayesian penalty nearly cancels χ² improvement
- Data consistent with α ≠ 0 but do not demand it

## Degeneracy Structure

- r(α, Ω_m) ≈ +0.59 — geometric degeneracy
- r(α, σ₈) ≈ −0.27 — growth suppression trades off against lower σ₈

## Citation

```bibtex
@misc{magnusson2026robustness,
  author = {Magnusson, Morten},
  title  = {Robustness of the EFC Growth-Sector Signal},
  year   = {2026},
  doi    = {10.6084/m9.figshare.31332730}
}
```

Version: 1.0
