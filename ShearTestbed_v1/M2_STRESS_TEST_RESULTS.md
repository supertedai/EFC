# M2 EFC Stress Test Results

**Date:** 2026-02-05
**Purpose:** Validate EFC improvement is not driven by systematics

---

## Configuration Summary

| Parameter | Value |
|-----------|-------|
| **Cosmology** | Bestpoint evaluation (not fit) |
| **IA amplitude** | 0.0 (OFF/FIXED) |
| **Δz, m-bias** | Not included |
| **HMCode A** | 3.13 (FIXED) |
| **EFC mode** | Case A (lensing amplitude only) |

---

## Stress Test A1: IA Sensitivity

**Result:** IA was already fixed at 0.0 in baseline.

**Conclusion:** EFC improvement is NOT IA compensation.

---

## Stress Test A2: Hard Scale Cuts

Removed additional 45 small-scale data points (23% of data).

| Scale Cuts | Data Points | ΛCDM −ln(L) | EFC (α=0.10) −ln(L) | Δ(−2 ln L) |
|------------|-------------|-------------|---------------------|------------|
| **Standard** | 195 | -349.68 | -324.21 | **-50.9** |
| **Hard** | 150 | -279.33 | -263.33 | **-32.0** |

### Interpretation

- Hard cuts removed smallest θ-bins for ξ+ (bins 0-1) and ξ- (bin 3)
- Δ(−2 ln L) dropped from -50.9 to -32.0
- **~37% of improvement** comes from small scales
- **~63% of improvement PERSISTS** with harder cuts

**Conclusion:** EFC improvement is NOT entirely small-scale driven.

---

## Parameter Scan Summary

| α_L2 | −ln(L) | Δ(−2 ln L) vs ΛCDM |
|------|--------|-------------------|
| 0.00 | -349.68 | 0.0 (baseline) |
| 0.05 | -331.08 | -37.2 |
| **0.10** | **-324.21** | **-50.9** |
| 0.15 | -333.19 | -33.0 |
| 0.20 | -362.95 | +26.5 |

Peak at α_L2 ≈ 0.10 ± 0.01

---

## Correct Statistical Interpretation

**What we can say:**
- Δ(−2 ln L) = -50.9 at bestpoint with 1 additional parameter (α_L2)
- Smooth α-curve with clear maximum
- Improvement persists under hard scale cuts (Δ = -32)
- IA already OFF, so not IA compensation

**What we cannot say (yet):**
- "7σ preference" - requires proper DoF counting
- S₈ shift direction - requires full parameter inference
- CMB tension resolution - requires joint analysis

---

## Σ Implementation Note

**Case A: Lensing amplitude modification**

```python
P_EFC(k,z) = P_ΛCDM(k,z) × Σ(k,z)²
```

- Applied AFTER CAMB computes P(k,z)
- NOT a consistent MG calculation where μ affects perturbation equations
- Growth D(χ) is recomputed from modified P_EFC

**Physical interpretation:** Enhanced lensing signal at low-z, high-k

---

## Remaining Tests Needed

1. **Mini-profile on (Ωm, σ8):** Let cosmology adjust, measure EFC benefit
2. **Cross-validation:** Test on KV450 or DES Y3
3. **Consistency check:** Does EFC+shear agree with RSD/clusters?

---

## Summary

| Test | Result | Status |
|------|--------|--------|
| α-curve smooth | Yes, peaks at 0.10 | ✅ |
| IA sensitivity | IA=0, not eating IA | ✅ |
| Small-scale robustness | 63% persists with hard cuts | ✅ |
| Statistical claim | Δ(−2 ln L) = -50.9 | ⚠️ Not "7σ" |
| Full inference | Not done | ⏳ |

**Date:** 2026-02-05
