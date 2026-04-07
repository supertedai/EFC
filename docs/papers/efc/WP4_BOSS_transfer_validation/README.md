# WP4 — Cross-Survey Parameter Transfer Validation: DESI DR2 → BOSS/eBOSS

**Author:** Morten Magnusson (ORCID: 0009-0002-4860-5095)
**DOI:** [10.6084/m9.figshare.31954125](https://doi.org/10.6084/m9.figshare.31954125)
**Date:** April 2026
**License:** CC-BY 4.0
**Type:** Post-hoc validation (not pre-registered)

## Key Result

EFC parameters calibrated on **DESI DR2** (z_L1L2 = 1.01, α_L2 = 0.045), applied **frozen** to BOSS DR12 BAO data, give:

| Model | χ² | Δχ² | k_eff |
|---|---|---|---|
| ΛCDM (Planck baseline) | 20.83 | — | 0 |
| **EFC (DESI parameters, no refit)** | **13.06** | **−7.77** | **0** |

**Cross-survey parameter invariance**: parameters from one survey improve fits on an independent survey *without any retuning*. This is a necessary (not sufficient) condition for physical validity.

## Model

```
H_EFC(z) = H_ΛCDM(z) · √(1 + α_L2 · Θ(z < z_L1L2))
```

Heaviside-gated late-time enhancement (~4%) of the Hubble parameter; activates below the regime transition redshift z_L1L2.

**Frozen parameters** (from DESI DR2):
- z_L1L2 = 1.01
- α_L2 = 0.045
- Baseline: H₀ = 67.4, Ωₘ = 0.315, r_s = 147.09 Mpc (Planck 2018)

## Covariance Diagnostics (the gain is real, not an artefact)

**Whitening (Cholesky)**: improvement dominated by component w₅ (Δχ² = −11.39) — the most constrained linear combination of observables.

**Eigenmode partition**:
- Strongly penalised modes (low λ): Δχ² = **−5.50 (71%)**
- Weakly penalised modes (high λ): Δχ² = −2.27 (29%)

EFC improves the *most constrained* directions in data space — the opposite of what a flexible model exploiting covariance slack would do.

**Robustness sweep** C(ρ) = (1−ρ)·diag(C) + ρ·C:

| ρ | χ²(ΛCDM) | χ²(EFC) | Δχ² |
|---|---|---|---|
| 0.00 | 16.37 | 12.13 | −4.24 |
| 0.25 | 15.27 | 10.68 | −4.59 |
| 0.50 | 14.82 | 9.87 | −4.96 |
| 0.75 | 16.52 | 10.82 | −5.70 |
| 1.00 | 20.83 | 13.06 | **−7.77** |

EFC wins at every covariance level.

## Best-Fit Reference (parameters free)

| Dataset | N | k_eff | z_L1L2 | α_L2 | ΔAICc | ΔBIC |
|---|---|---|---|---|---|---|
| BOSS | 6 | 1 | > 0.6* | 0.036 | −6.4 | −7.6 |
| BOSS+eBOSS | 14 | 2 | 1.60 | 0.036 | −19.3 | −19.1 |
| DESI DR2 | 13 | 2 | 1.01 | 0.045 | ~−1 | −1.0 |

*BOSS alone has a flat likelihood for z_L1L2 > 0.6.
**α_L2 ≈ 0.036–0.045 across independent datasets** — physical stability beyond the transfer test.

## What This Result Is / Is Not

**Is:** post-hoc validation, parameter-stability probe, covariance-aware with 3 robustness diagnostics.
**Is not:** pre-registered (unlike P3), discovery claim, proof of EFC, refutation of ΛCDM.

## Companion Test

| Test | Type | Result |
|---|---|---|
| P3 (DES Y6 lensing) | Pre-registered prediction | 0.3σ agreement (PASS) |
| **WP4 (BOSS transfer)** | Post-hoc parameter transfer | Δχ² = −7.77 |

Together: predictive accuracy (P3) + cross-survey generalisation (WP4).

## File Manifest

| File | Purpose |
|---|---|
| `WP4_BOSS_transfer_validation.pdf` | Source preprint |
| `README.md` | This document |
| `index.json` / `metadata.json` / `schema.json` | Machine-readable indices |
| `WP4_BOSS_transfer_validation.jsonld` | JSON-LD linked data |
| `citations.bib` | BibTeX |
| `src/wp4_transfer.py` | Reproducible Python implementation |
| `data/wp4_data.json` | All tables, parameters, χ² values |
| `examples/demo.py` | Tested demo |
