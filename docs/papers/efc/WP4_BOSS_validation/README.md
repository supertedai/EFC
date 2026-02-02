# Independent Validation of Energy-Flow Cosmology BAO Predictions

## Cross-Survey Transfer from DESI DR2 to BOSS DR12

**Author:** Morten Magnusson
**Affiliation:** Symbiose Research, Sandnes, Norway
**Date:** February 2, 2026
**DOI:** [10.6084/m9.figshare.31231522](https://doi.org/10.6084/m9.figshare.31231522)

---

## Abstract

We present an independent validation of Energy-Flow Cosmology (EFC) using Baryon Acoustic Oscillation (BAO) measurements from BOSS DR12, testing parameter transfer from DESI DR2. Using canonical regime gating where z < z_L1L2 activates the L2 modification, we find that DESI best-fit parameters (z_L1L2 = 1.01, α_L2 = 0.045) reduce the BOSS χ² from 20.83 to 13.06 (Δχ² = −7.77) without refitting. This improvement is robust: it persists under diagonal covariance (Δχ² = −4.24), and eigenmode analysis confirms that gains arise primarily from strongly-penalized modes rather than covariance exploitation.

---

## Key Results

### Transfer Test (No Refit)

| Model | χ² | Notes |
|-------|-----|-------|
| ΛCDM | 20.83 | Baseline |
| EFC (DESI params) | 13.06 | z_L1L2 = 1.01, α_L2 = 0.045 |
| **Δχ²** | **−7.77** | **Transfer supported** |

### Best-Fit Parameters

| Dataset | N | k_eff | z_L1L2 | α_L2 | ΔAIC_c | ΔBIC |
|---------|---|-------|--------|------|--------|------|
| BOSS | 6 | 1 | > 0.6* | 0.036 | −6.4 | −7.6 |
| BOSS+eBOSS | 14 | 2 | 1.60 | 0.036 | −19.3 | −19.1 |
| DESI DR2 | 13 | 2 | 1.01 | 0.045 | ~−1 | −1.0 |

*Lower bound only; likelihood flat for z_L1L2 > 0.6

### Robustness Diagnostics

- **Diagonal covariance:** Δχ² = −4.24 (improvement persists)
- **Eigenmode analysis:** Gains from strongly-penalized modes (Δχ² = −5.50)
- **Whitened residual w₅:** Dominant improvement (Δχ² = −11.39)

---

## EFC Model

### Hubble Rate Modification

```
H_EFC(z) = H_ΛCDM(z) × [1 + α_L2 · Θ(z)]
```

### Regime Gating Function

```
Θ(z) = ½ × [1 + tanh((z_L1L2 − z) / Δz)]
```

With transition width Δz = 0.05.

### Regime Interpretation

- **z < z_L1L2:** Θ ≈ 1 → L2 regime active (~4-5% H(z) enhancement)
- **z > z_L1L2:** Θ ≈ 0 → L1 (ΛCDM) regime

---

## Data Sources

### BOSS DR12 Consensus BAO
- **Observables:** D_M/r_s and D_H/r_s
- **Effective redshifts:** z_eff = 0.38, 0.51, 0.61
- **Data points:** N = 6
- **Full 6×6 correlation matrix employed**
- **Reference:** Alam et al. (2017), MNRAS 470, 2617

### eBOSS Extension
- **Tracers:** LRG, ELG, QSO, Lyα
- **Combined BOSS+eBOSS:** N = 14 data points
- **Reference:** Alam et al. (2021), Phys. Rev. D 103, 083533

### Baseline Cosmology (Planck 2018)
- H₀ = 67.4 km/s/Mpc
- Ω_m = 0.315
- r_s = 147.09 Mpc

---

## Methodology

### Transfer Test Protocol

1. Compute χ²_ΛCDM on BOSS using standard cosmology
2. Compute χ²_EFC on BOSS using DESI parameters (z_L1L2 = 1.01, α_L2 = 0.045)
3. Report Δχ² = χ²_EFC − χ²_ΛCDM

**Key feature:** No parameters fitted (k_eff = 0), making Δχ² the relevant statistic.

### Covariance Diagnostics

1. **Whitening:** Transform residuals via Cholesky decomposition C = LL^T
2. **Eigenmode:** Decompose C = U diag(λ) U^T and compute mode contributions
3. **Robustness:** Interpolate C(ρ) = (1−ρ)diag(C) + ρC for ρ ∈ [0, 1]

---

## Physical Implications

If EFC interpretation is correct:

- **Hubble rate enhancement:** ~4-5% at z ≲ 1 relative to ΛCDM
- **Hubble tension:** Potential partial resolution
- **Dark energy:** Implications for equation of state inference
- **Structure growth:** Effects at low redshift

---

## Conclusions

1. **Transfer supported:** DESI parameters improve BOSS χ² by 7.77 without refitting
2. **Robustness confirmed:** Improvement persists under diagonal covariance and arises from strongly-penalized eigenmodes
3. **α_L2 consistent:** Both surveys find α_L2 ≈ 0.035-0.045
4. **Complementary constraints:** DESI constrains z_L1L2; BOSS confirms α_L2

---

## Quick Start

```python
from src.efc_boss_transfer import EFCTransferTest

# Initialize with DESI parameters
test = EFCTransferTest(z_L1L2=1.01, alpha_L2=0.045)

# Run transfer test on BOSS data
results = test.transfer_test()
print(f"Δχ² = {results['delta_chi2']:.2f}")  # -7.77

# Robustness check with diagonal covariance
robust = test.robustness_sweep()
```

---

## References

1. M. Magnusson, "Energy-Flow Cosmology: Theoretical Foundations and DESI DR2 BAO Constraints," Symbiose Technical Report (2026). DOI:10.6084/m9.figshare.31231522

2. S. Alam et al. [BOSS Collaboration], "The clustering of galaxies in the completed SDSS-III Baryon Oscillation Spectroscopic Survey," MNRAS 470, 2617 (2017) [arXiv:1607.03155]

3. S. Alam et al. [eBOSS Collaboration], "Completed SDSS-IV extended Baryon Oscillation Spectroscopic Survey," Phys. Rev. D 103, 083533 (2021) [arXiv:2007.08991]

4. N. Aghanim et al. [Planck Collaboration], "Planck 2018 results. VI. Cosmological parameters," A&A 641, A6 (2020) [arXiv:1807.06209]

---

## License

This work is licensed under [CC-BY-4.0](LICENSE).
