# BESR3: Methods Section Draft (Paper-Ready)

## 3. Entropy–Structure Correlation Analysis

### 3.1 Observable Definitions

We test whether the observed correlation between entropy profile shape and cool-core state (Cavagnolo et al. 2009; hereafter ACCEPT) is reproduced in the TNG-Cluster simulation (Nelson et al. 2024; Lehle et al. 2024).

**ACCEPT reference:** Cavagnolo et al. (2009) fit deprojected X-ray entropy profiles of 239 clusters with the model

  K(r) = K₀ + K₁₀₀ (r / 100 kpc)^α

and report a positive correlation between α and the cool-core classification metric y_CCT (the central cooling time-based cool-core indicator as defined in Cavagnolo et al. 2009): ρ(α, y_CCT) ≈ +0.36. Clusters with steeper entropy gradients (higher α) tend to have *higher* central cooling times.

**TNG-Cluster data:** We use the published supplementary catalog of Lehle et al. (2024), containing 352 massive galaxy clusters (10¹⁴ < M₅₀₀c/M☉ < 2×10¹⁵) at z = 0. The catalog provides central entropy K₀ (within 0.012 r₅₀₀c), electron density slope ne_slope (at 0.04 r₅₀₀c), central cooling time t_cool, and X-ray concentration parameters.

### 3.2 Pre-Test: Proxy-Based Analysis (Path B)

As a computationally efficient pre-test, we construct an entropy gradient proxy from catalog quantities. For an entropy profile K(r) ∝ r^α, the logarithmic entropy slope decomposes as:

  α = d ln K / d ln r = d ln T / d ln r + (2/3) × (−d ln ne / d ln r)

We define α_proxy ≡ (2/3) × ne_slope, which represents the density contribution to the entropy gradient. This is a lower bound on α under the physical expectation that temperature rises with radius in cluster cores (d ln T / d ln r ≥ 0).

**Important caveat:** α_proxy is a monotonic transformation of ne_slope only under the assumption that the temperature gradient term does not reverse the rank ordering of halos. While this is physically motivated (CC clusters have both steep density profiles and cool cores with rising temperature), it is not mathematically guaranteed without measuring T-slope halo-by-halo. We therefore treat α_proxy as a sign-robust pre-test but not a formal substitute for α_fit. The pre-test establishes whether the sign flip is robust to simple proxy scaling, but does not eliminate the possibility of rank-order changes due to T-slope variation.

We apply three statistical tests, defined before examining results:

1. **Raw Spearman correlations:** ρ(α_proxy, K₀) and ρ(α_proxy, t_cool)
2. **Partial correlations:** Controlling for log M₅₀₀c, using rank-based residualization
3. **Mass-binned analysis:** Independent Spearman ρ in four mass bins [14.0, 14.3), [14.3, 14.6), [14.6, 14.9), [14.9, 15.5)

### 3.3 Decisive Test: Full Profile Fit (Path A)

To eliminate remaining systematic ambiguities — specifically (i) T-slope variation between halos, (ii) local-vs-global slope definitions, and (iii) radius mismatch — we compute entropy profiles K(r) directly from TNG-Cluster gas particle data via the TNG API.

**Procedure (per halo):**

1. Download gas cells within r₅₀₀c of the central subhalo
2. Select non-star-forming cells with T > 10⁶ K (following Lehle et al. 2024)
3. Compute K_i = k_B T_i × n_{e,i}^{−2/3} for each cell
4. Bin mass-weighted K into 30 logarithmically spaced radial bins over [20, 400] kpc (corresponding to ≈0.01–0.3 r₅₀₀c for the median cluster in our sample)
5. Fit K(r) = K₀ + K₁₀₀ (r/100 kpc)^α via least-squares (Cavagnolo et al. 2008 model)

**Locked parameters (specified before analysis):**
- Radial center: SUBFIND-determined subhalo position (not gas particle median)
- Fit range: 20–400 kpc (physical), matching ACCEPT typical fitting range
- Minimum bin occupancy: 5 cells
- Initial α guess: 1.1 (ACCEPT median)
- Weighting: mass-weighted K in radial bins (see §3.4 for comparison with spectroscopic weighting)

Because α_fit is derived from the same functional form and radial interval used in ACCEPT, a persistent sign difference in ρ(α_fit, K₀) constitutes a definition-matched comparison between simulation and observation.

The same three-test battery (raw ρ, partial ρ, mass-binned ρ) is then applied to α_fit values.

### 3.4 Systematic Considerations

We note three irreducible differences between TNG and ACCEPT that cannot be eliminated even by matching α definitions:

1. **3D vs projected:** TNG profiles use intrinsic 3D mass-weighted quantities; ACCEPT uses deprojected X-ray spectroscopic measurements with emission weighting. This affects absolute normalization but is not expected to reverse rank-order correlations.
2. **Selection function:** ACCEPT clusters are X-ray selected and flux-limited; TNG-Cluster is mass-selected.
3. **Subgrid physics:** TNG employs specific implementations of AGN feedback, cooling, and star formation that may not capture all relevant ICM physics.

These differences mean that agreement is not guaranteed even if the same underlying physics were present; conversely, a persistent sign difference under matched α definitions indicates a structural mismatch in rank-based coupling strength that cannot be attributed solely to measurement formalism.

### 3.5 Pre-Registration of Stop/Go Criterion

To avoid post-hoc interpretation:

- **STOP** (definition artifact): ρ(α_fit, K₀) > 0 and ρ(α_fit, t_cool) > 0 — sign flip reverses when α is matched
- **GO** (real mismatch): ρ(α_fit, K₀) < 0 — sign flip survives full definition matching
- **PARTIAL**: Mixed signs between K₀ and t_cool require further investigation

---

## 4. Results

### 4.1 Pre-Test Results (Path B)

[Table 1]
| Test | ρ | p-value | N |
|------|---|---------|---|
| ρ(α_proxy, K₀) raw | −0.872 | 8×10⁻¹¹¹ | 352 |
| ρ(α_proxy, K₀) partial\|M | −0.880 | 2×10⁻¹¹⁵ | 352 |
| ρ(α_proxy, t_cool) raw | −0.878 | 7×10⁻¹¹⁴ | 352 |
| ρ(α_proxy, t_cool) partial\|M | −0.876 | 1×10⁻¹¹² | 352 |
| ACCEPT ρ(α, y_CCT) | +0.36 | — | 239 |

Mass-binned results show negative correlations in all four bins, with |ρ| > 0.74.

The pre-test establishes that the sign flip is:
- Not driven by mass confounding (partial ρ unchanged)
- Robust across the full mass range (all bins negative)
- Preserved under the (2/3) scaling of ne_slope

However, the pre-test does not rule out rank-order changes from unmeasured T-slope variation or the local-vs-global radius mismatch.

### 4.2 Decisive Test Results (Path A)

[To be filled after overnight run]

---

## 5. Discussion

### 5.1 Interpretation Framework

We frame the BESR3 result as a **diagnostic finding**:

> TNG-Cluster exhibits an extremely strong, internally consistent coupling between structural gradients and core entropy/cooling, with the opposite sign in rank-based coupling strength to that reported in ACCEPT observations.

We do *not* claim this proves missing physics. The sign flip could arise from:

(a) **Subgrid modeling:** AGN feedback in TNG may produce overly mechanical CC/NCC transitions that couple structure and entropy too tightly and in the wrong direction.

(b) **Observational systematics:** Projection effects, spectral fitting biases, or selection effects in ACCEPT could weaken or reverse the intrinsic correlation.

(c) **Missing physics:** Physical processes not captured by the TNG model (e.g., cosmic ray transport, anisotropic conduction, magnetic draping) may be required to reproduce the observed coupling.

Distinguishing between (a), (b), and (c) requires comparison with additional simulations (e.g., FLAMINGO, SIMBA) and forward-modeled mock observations of TNG-Cluster. [If interpreting in EFC context: add paragraph here.]
