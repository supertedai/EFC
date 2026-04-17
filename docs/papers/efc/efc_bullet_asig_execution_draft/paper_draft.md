# Execution of the Pre-Registered A_sig Shock-Front Test on JWST Bullet-Cluster Free-Form Reconstructions

**Morten Magnusson** — ORCID 0009-0002-4860-5095
Energy-Flow Cosmology Initiative, Bergen, Norway
Draft: 2026-04-17. DOI: pending. EFC Document ID: EFC-VAL-2026-005 (draft).

---

## Abstract

We execute the pre-registered directional-lensing-residual operator A_sig = ⟨κ⟩_front − ⟨κ⟩_back (DOI 10.6084/m9.figshare.31963668 §4) on the Cha et al. 2025 JWST mass reconstruction of the Bullet Cluster (DOI 10.3847/2041-8213/ad8f3e; 146 strong-lensing constraints, 398 weak-lensing sources arcmin⁻², MARS algorithm). The operator is applied to convergence residuals δκ = κ_obs − κ_density with geometry, strip width, and density model locked per the v3.11 pre-registration. PIEMD baseline yields a null (A_sig ≈ −6.9×10⁻⁴, p = 0.98); the free-form MARS κ-map run is the direct discriminator between EFC entropy-gradient lensing and ΛCDM particle dark matter at the shock front. No new free parameters are introduced.

## 1. Pre-registration Compliance

All analysis choices that could affect A_sig were fixed before data contact:
- Strip geometry: azimuthal wedge aligned with Chandra shock normal, width Δφ = 30° ± 5°
- Density model: NFW + PIEMD two-component profile with fixed concentration c₂₀₀ = 4
- χ² masking: |κ| < 0.05 excluded (source noise floor)
- Seed for bootstrap resampling: 42

The pre-registration is SHA-256 hashed in the v3.11 package manifest.

## 2. Data

| Component | Source | Key parameter |
|---|---|---|
| Free-form κ-map | Cha et al. 2025, MARS reconstruction | 146 SL + 398 WL sources/arcmin² |
| Parametric cross-check | Rihtaršič et al. 2026 (arXiv:2601.22245) | 135 multiple images, 27 systems, zspec 0.9–6.7 |
| Merger geometry | Cho et al. 2025 (arXiv:2512.03150) | 10:1 mass ratio, M_main = 15.1×10¹⁴ M☉ |
| Chandra shock map | Russell et al. 2010/2012/2022 | 500 ks cumulative exposure |
| EFC δκ prediction | Directional_Lensing_Residuals package | δκ_EFC = μ₀ · (ΔS/S_max) · κ_local |

## 3. Results (provisional)

### 3.1 PIEMD Baseline (already reported)
A_sig(PIEMD) = −6.9×10⁻⁴, p = 0.98 — consistent with null. This baseline establishes that a smooth parametric model introduces no spurious shock-locked asymmetry under the pre-registered geometry.

### 3.2 MARS Free-Form κ (pending)
The Cha2025 κ-map has finer substructure than the PIEMD baseline can resolve. The free-form A_sig run is in three stages:
1. WCS astrometric coregistration between Cha2025 κ and Chandra shock map (sub-arcsecond)
2. Point-source cross-correlation for alignment validation
3. Strip-wise δκ evaluation with 1000-bootstrap confidence intervals

## 4. Pre-registered Kill Criteria

| # | Threshold | Outcome |
|---|---|---|
| K1 | A_sig (MARS) within 2σ of PIEMD null | EFC prediction fails — null detection |
| K2 | A_sig (MARS) > 5σ with opposite sign to EFC δκ prediction | EFC falsified on shock-front geometry |
| K3 | A_sig (MARS) > 3σ, sign aligned with δκ_EFC = μ₀(ΔS/S_max)κ_local | EFC supported; sealed P2 confirmed |
| K4 | μ_cluster inferred > 1.2 to match Cho2025 mass discrepancy | Sealed P1 falsified |

## 5. SIDM Interpretation Under EFC Ontology

The Cha2025 SIDM bound σ/m < 0.5 cm²/g reinterprets under EFC's no-particle ontology as a constraint on the entropy-gradient coupling strength in the merger regime. The A_sig test is strictly orthogonal to this bound: it probes directional asymmetry of lensing residuals, not the dark-matter self-interaction cross-section. A null A_sig result is therefore consistent with any σ/m value; only a positive detection discriminates EFC from ΛCDM at the merger scale.

## 6. Relation to Other Sealed Predictions

This execution paper tests sealed prediction P2 from DOI 10.6084/m9.figshare.31963668. Sealed P1 (μ_cluster ≤ 1.2) requires the full relativistic EFC solution on the Cho2025 profile and is deferred to a separate paper. The Abell 2146 double-shock system (Russell et al.) provides an independent cross-check target using the same pre-registered pipeline.

## 7. Outlook

On completion of the MARS free-form run, this draft becomes `EFC-VAL-2026-005` with a new figshare DOI succeeding 31963668 v3.11. Subsequent work will apply the same pipeline to Abell 2146 (double shock) and El Gordo (asymmetric merger), providing a three-cluster ensemble test of the entropy-gradient lensing hypothesis.

## Acknowledgements

Uses DOI-anchored EFC pre-registration (31963668 v3.11) and externally published JWST/Chandra data only. No private datasets.
