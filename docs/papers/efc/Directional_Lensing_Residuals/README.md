# Directional Lensing Residuals at Cluster Merger Shock Fronts

**Author:** Morten Magnusson
**DOI:** [10.6084/m9.figshare.31288063](https://doi.org/10.6084/m9.figshare.31288063)
**Date:** February 7, 2026
**Status:** Pre-registered pipeline, awaiting application to real data

## Abstract

Pre-registered analysis pipeline for testing whether gravitational lensing convergence (κ) at galaxy cluster merger shock fronts exhibits a directional asymmetry inconsistent with symmetric mass-only models. The primary estimator, A_sig, measures the locally-normalized excess of κ-residuals on the pre-shock (low-entropy) side relative to a rotation null model.

## Key Innovation

This test exploits the unique laboratory provided by cluster merger shock fronts:
- **Pre-shock gas**: Low entropy (upstream, undisturbed)
- **Post-shock gas**: High entropy (downstream, shock-heated)
- **EFC prediction**: Excess κ on the low-entropy side due to c_eff(S)

## Primary Estimator: A_sig

### Raw Shock Asymmetry
```
A_shock = (⟨Δκ⟩_pre - ⟨Δκ⟩_post) / σ_diff
```

Where:
- `Δκ = κ_obs - κ_model` is the lensing residual
- `σ_diff = σ_Δκ × √(1/N_pre + 1/N_post)`

### Rotation Null Model
Rotate all input maps (κ, n_e, kT) by θ = 15°, 30°, ..., 345° (23 angles) and recompute A_shock at each orientation.

### Locally-Normalized Significance
```
A_sig = [A_shock - median(A_rot)] / σ_MAD
```

Where `σ_MAD = 1.4826 × MAD[A_rot]` is the robust scatter estimate.

### Physical Content
- **A_sig > 0**: Excess κ on low-entropy (pre-shock) side → c_eff(S) signal
- **A_sig ≈ 0**: No directional preference → consistent with GR
- **A_sig < 0**: Excess κ on high-entropy side → inconsistent with both

## Mass Model

```
κ_model(r) = κ_NFW(r) + κ_gas(r)
```

Gas component with pressure proxy:
```
κ_gas(r) = [α × Σ_gas(r) + β × Σ_P(r)] / Σ_crit
```

Where:
- `Σ_gas = ∫ μ_e m_p n_e dℓ` — gas surface mass density
- `Σ_P = ∫ n_e × (kT)^{1/2} dℓ` — pressure proxy

**Anti-circularity**: Coefficients (α*, β*) fitted outside shock aperture only.

## Mock Validation Results

| Model | A_shock | A_rot median | σ_MAD | A_sig | p_rot |
|-------|---------|--------------|-------|-------|-------|
| EFC   | +6.75   | +5.38        | 7.35  | **+0.19** | 0.39 |
| ΛCDM  | -1.12   | +6.96        | 6.68  | **-1.21** | 0.65 |

**Key result**: Correct sign separation between models.

## Pre-Registered Decision Criteria

| Outcome | Criteria | Action |
|---------|----------|--------|
| **Detection** | A_sig > 3 AND p_rot < 0.05 in ≥2 clusters | Evidence for directional lensing asymmetry |
| **Marginal** | A_sig > 2 OR (A_sig > 1.5 AND r(κ,T\|n) < -0.15) | Tentative; extend to additional clusters |
| **Null** | A_sig < 2 in all clusters | Upper bound on \|Δκ/κ\| at shocks |

## G/c Degeneracy Breaking

The test distinguishes two classes of modified gravity:

| Modification | Effect | A_sig prediction |
|--------------|--------|------------------|
| **G_eff(S)** | Isotropic enhancement (gravity has no direction) | ≈ 0 |
| **c_eff(S)** | Directional enhancement (photons accumulate extra phase on low-S side) | > 0 |

## Expected Signal (Bullet Cluster)

At the bow shock (Mach ≈ 2.5):
- Temperature jump: T₂/T₁ = 2.85
- Density jump: n₂/n₁ = 2.29
- Entropy jump: S₂/S₁ ≈ 1.67

Predicted EFC signal:
```
Δκ_EFC ≈ μ₀ × (ΔS/S_max) × κ_local ≈ 0.03
```

Corresponding to Δκ/κ ≈ 15% at the shock front.

## Data Requirements

For each cluster:
1. **κ-map**: Gravitational lensing convergence (JWST weak+strong lensing)
2. **kT-map**: ICM temperature (Chandra X-ray spectral fitting)
3. **n_e-map**: Electron density (X-ray surface brightness deprojection)

### Target Clusters
- **Bullet Cluster**: JWST κ-map (Cha et al. 2025), Chandra ~500 ks
- **Abell 2146**: Double-shock system (Russell et al. 2010, 2012, 2022)

## Secondary Estimator: r(κ,T|n)

Partial correlation between Gaussian Gradient Magnitude edge amplitudes:
```
r(κ,T|n) = [r(e_κ,e_T) - r(e_κ,e_n)×r(e_T,e_n)] / √[(1-r²(e_κ,e_n))(1-r²(e_T,e_n))]
```

**Note**: This is supportive but degenerate (≈ -0.25 in both EFC and ΛCDM due to hydrodynamic coupling).

## Package Contents

```
Directional_Lensing_Residuals/
├── README.md                 # This file
├── index.json                # Machine-readable metadata
├── src/
│   └── directional_lensing.py   # Reference implementation
├── data/
│   └── mock_validation_results.json   # Mock test results
├── examples/
│   └── directional_lensing_demo.py    # Demonstration script
├── CITATION.cff              # Citation metadata
└── LICENSE                   # MIT License
```

## Quick Start

```python
from src.directional_lensing import AsigEstimator, RotationNull

# Initialize estimator
estimator = AsigEstimator(
    shock_position=r_shock,
    shock_normal=n_hat,
    strip_width=100,  # kpc
    strip_length=200  # kpc
)

# Compute A_shock
A_shock = estimator.compute_asymmetry(kappa_obs, kappa_model)

# Compute rotation null
null = RotationNull(n_angles=23, step=15)
A_rot_distribution = null.compute(kappa_obs, kappa_model, n_e, kT, estimator)

# Get A_sig
A_sig = estimator.compute_significance(A_shock, A_rot_distribution)
```

## Citation

```bibtex
@article{magnusson2026directional,
  author  = {Magnusson, Morten},
  title   = {Directional Lensing Residuals at Cluster Merger Shock Fronts},
  year    = {2026},
  month   = {February},
  doi     = {10.6084/m9.figshare.31288063}
}
```

## References

- Cha, S., Jee, M. J., et al. 2025, ApJL, 987, L15 (JWST Bullet Cluster)
- Markevitch, M. & Vikhlinin, A. 2007, Phys. Rep., 443, 1
- Russell, H. R., et al. 2010, 2012, 2022 (Abell 2146 shock fronts)
- Verlinde, E. 2016, SciPost Phys., 2, 016
