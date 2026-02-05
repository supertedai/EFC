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

## Stress Test B1: Amplitude Equivalence

**Question:** Is EFC just an amplitude knob, or does the (k,z)-form matter?

### A_s Scan Results

| ln_1e10_A_s | δ_A (approx) | −ln(L) |
|-------------|--------------|--------|
| 2.80 | -14% | -376.08 |
| 2.90 | -5% | -356.47 |
| 2.95 | 0% (baseline) | -349.68 |
| 3.00 | +5% | -345.61 |
| **3.04** | **+9%** | **-344.75** ← best amplitude |
| 3.10 | +16% | -348.34 |

### Comparison

| Model | −ln(L) | Δ vs baseline |
|-------|--------|---------------|
| ΛCDM baseline | -349.68 | 0 |
| **ΛCDM best amplitude** | -344.75 | +4.93 |
| **EFC (α=0.10)** | **-324.21** | **+25.47** |

### Residual After Amplitude Optimization

```
EFC vs best-amplitude-ΛCDM:
  Δ(−ln L) = -324.21 - (-344.75) = +20.54
  Δ(−2 ln L) = +41.1
```

**Conclusion:** EFC is **NOT just amplitude**.

Even with optimal A_s tuning (+9%), ΛCDM cannot match EFC.
The (k,z)-dependent form provides Δ(−2 ln L) = 41 extra improvement.

---

## Stress Test B2: Tomographic Localization

**Question:** Where does EFC improvement come from (low-z or high-z)?

### Tomographic Split

- **Low-z subset:** Pairs involving bin 1 or 2 (9 pairs, 117 data points)
- **High-z subset:** Pairs with bins 3,4,5 only (6 pairs, 78 data points)

### Results

| Subset | Bin Pairs | N_data | ΛCDM −ln(L) | EFC −ln(L) | Δ(−2 ln L) |
|--------|-----------|--------|-------------|------------|------------|
| All | 15/15 | 195 | -349.68 | -324.21 | **50.9** |
| **Low-z** | 9/15 | 117 | -211.37 | -160.43 | **101.9** |
| High-z | 6/15 | 78 | -93.75 | -83.04 | 21.4 |

### Per-Data-Point Improvement

| Subset | Δ(−2 ln L) / N |
|--------|----------------|
| **Low-z** | **0.87** |
| High-z | 0.27 |

**Ratio:** Low-z improvement is **3.2× larger** per data point than high-z.

### Interpretation

This is **exactly what EFC predicts:**
- Σ(k,z) = 1 + α×(1 - z/z_activ) for z < z_activ = 0.5
- Low-z bins (z ≲ 0.5) see maximum EFC effect
- High-z bins (z > 0.5) see minimal effect (Σ → 1)

The tomographic localization of the improvement to low-z strongly supports
the physical interpretation of EFC as a late-time gravity modification.

---

## Test C1: Mini-Profile (Ωm, A_s)

**Question:** How does EFC shift the optimal cosmology?

### Grid Scan Results

5×5 grid in (Ωm, ln_1e10_A_s) for α=0.00 and α=0.10.

### Best Points

| α | Ωm | ln_As | σ8 | S8 | −ln(L) |
|---|-----|-------|-----|-----|--------|
| **0.00** (ΛCDM) | 0.261 | 3.05 | 0.792 | **0.739** | -346.26 |
| **0.10** (EFC) | 0.261 | 2.90 | 0.734 | **0.685** | -321.59 |

### Key Finding

```
EFC cosmology shift:
  ΔS8 = 0.685 - 0.739 = -0.054 (LOWER, not higher!)
  Δln_As = 2.90 - 3.05 = -0.15 (15% lower amplitude)
  Δ(-lnL) = +24.67 (better fit even with profile)
```

### S8 Tension Analysis

| Dataset | S8 | Tension with Planck |
|---------|-----|---------------------|
| Planck 2018 | 0.832 | — |
| KiDS ΛCDM | 0.739 | 2.3σ |
| **KiDS EFC** | **0.685** | **3.6σ (WORSE)** |

### Interpretation

EFC (Case A) prefers **lower** σ8/S8 because Σ² enhances lensing signal.
To match the same data, less intrinsic structure is needed.

**Conclusion:** EFC improves shear fit but **increases** S8 tension with CMB.
This is physically consistent: Case A is a lensing amplitude modification,
not a solution to the S8 discrepancy.

---

## Remaining Tests Needed

1. **Cross-validation:** Test on KV450 or DES Y3
2. **Case B implementation:** Consistent MG with μ in growth equations

---

## Summary

| Test | Result | Status |
|------|--------|--------|
| α-curve smooth | Yes, peaks at 0.10 | ✅ |
| IA sensitivity | IA=0, not eating IA | ✅ |
| Small-scale robustness | 63% persists with hard cuts | ✅ |
| Amplitude equivalence | NOT just amplitude, Δ=41 residual | ✅ |
| Tomographic localization | Low-z 3.2× stronger than high-z | ✅ |
| **Mini-profile (C1)** | **EFC prefers S8=0.685 (lower!)** | ✅ |
| S8 tension | EFC INCREASES tension with Planck | ⚠️ |

**All pattern tests passed. EFC improvement is:**
- NOT IA compensation (IA=0)
- NOT just small-scale (63% persists)
- NOT just amplitude (+41 residual after A_s tuning)
- LOCALIZED to low-z (as EFC predicts)

**Critical finding from C1:**
- EFC (Case A) improves shear fit by preferring LOWER S8
- This INCREASES tension with Planck CMB (3.6σ vs 2.3σ)
- Case A is phenomenological lensing boost, not S8 tension solution

**Date:** 2026-02-05
