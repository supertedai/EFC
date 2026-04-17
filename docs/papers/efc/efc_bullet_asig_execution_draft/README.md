# Execution of the Pre-Registered A_sig Shock-Front Test on JWST Bullet-Cluster Reconstructions (DRAFT)

**Status:** DRAFT — PIEMD null baseline executed; A_sig on Cha2025 free-form κ pending.
**Author:** Morten Magnusson (ORCID: 0009-0002-4860-5095)
**Date drafted:** 2026-04-17
**License:** CC-BY-4.0
**Predecessor DOI:** [10.6084/m9.figshare.31963668](https://doi.org/10.6084/m9.figshare.31963668) (v3.11, EFC-VAL-2026-004)

## Overview

Executes the pre-registered A_sig shock-front asymmetry operator on the Cha et al. 2025 JWST Bullet-Cluster mass reconstruction (146 strong-lensing constraints, 398 WL sources/arcmin², MARS algorithm; DOI 10.3847/2041-8213/ad8f3e, arXiv:2503.21870). The operator

> A_sig = ⟨κ⟩_front − ⟨κ⟩_back

is evaluated on convergence residuals δκ = κ_obs − κ_density, with geometry, strip width, and density model frozen per the pre-registration in DOI 10.6084/m9.figshare.31963668 §4. The PIEMD null baseline was reported (A_sig ≈ −6.9×10⁻⁴, p = 0.98); this paper reports the free-form follow-up.

## Key Numbers (from predecessor DOI)

- M₂₀₀ᶜ (main) = 15.11^{+2.48}_{−2.10} × 10¹⁴ M☉
- M₂₀₀ᶜ (sub) = 1.49^{+0.32}_{−0.26} × 10¹⁴ M☉
- Merger ratio: ~10:1 (minor merger, Cho et al. 2025, arXiv:2512.03150)
- SIDM bound: σ/m < 0.5 cm²/g (tightened by Cha2025)
- EFC regime-transition: μ_cluster ≈ 1.1, Σ_cluster ≈ 1.2

## Sealed Predictions (from v3.11)

| ID | Prediction | Kill if |
|---|---|---|
| P1 | μ_cluster stays ≤ 1.2 under relativistic EFC solution on Cho2025 profile | Inferred mass discrepancy requires μ > 1.2 |
| P2 | A_sig ≠ 0 aligned with Chandra shock front after subtracting density-only model | A_sig ≈ 0 at high significance on Cha2025 free-form κ |

## Data Sources (DOI-anchored)

- **EFC pre-registration:** DOI 10.6084/m9.figshare.31963668 (bullet_cluster_efc/ v3.11)
- **External κ-map:** DOI 10.3847/2041-8213/ad8f3e (Cha et al. 2025, 146 SL + 398 WL/arcmin²)
- **Spectroscopic anchor:** arXiv:2601.22245 (Rihtaršič et al. 2026, 135 multiple images, 27 systems, zspec 0.9–6.7)
- **Merger geometry:** arXiv:2512.03150 (Cho et al. 2025, 10:1 mass ratio)
- **Chandra shock:** 500 ks exposure (Russell et al. 2010/2012/2022)
- **EFC directional-residuals package:** `docs/papers/efc/Directional_Lensing_Residuals/` (no DOI issued; δκ_EFC = μ₀ · (ΔS/S_max) · κ_local)

## Status

- PIEMD baseline: **executed, null reported** (A_sig ≈ −6.9×10⁻⁴, p=0.98)
- Free-form A_sig on Cha2025 MARS κ-map: **pending** (WCS coregistration + strip evaluation)
- Abell 2146 double-shock cross-check: planned
