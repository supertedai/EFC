# Cosmological Growth Constraints — Quick Start Guide

## 5-Minute Overview

**Problem**: Modified gravity models that enhance gravity at large scales risk producing too much structure (σ₈ >> 0.8). Does the discrete entropic gravity operator survive this test?

**Answer**: Yes — but *only* with Λ-locking. Any sub-Hubble transition scale produces catastrophic overgrowth.

## The Key Idea

```
    Scale-dependent G_eff(k)
    ─────────────────────────

    G_eff(k)       (C² − 1)
    ──────── = 1 + ─────────────
       G          1 + (k/k_Λ)²

    k << k_Λ  →  G_eff/G = C² ≈ 5.38  (full enhancement)
    k >> k_Λ  →  G_eff/G = 1          (Newtonian, screened)

    ┌─────────────────────────────────────────────┐
    │  Scenario A (Λ-locked):                     │
    │    k_Λ = 0.0014 h/Mpc  (L = 4.4 Gpc)       │
    │    → All structure scales screened           │
    │    → σ₈ = 0.814  ✓                          │
    │                                              │
    │  Scenario B (10 Mpc):                        │
    │    k_L = 0.1 h/Mpc                           │
    │    → Enhancement active on growth scales     │
    │    → σ₈ = 367  ✗ (×452 overgrowth)          │
    │                                              │
    │  Scenario C (1 Mpc):                         │
    │    k_L = 1.0 h/Mpc                           │
    │    → Enhancement deep into nonlinear regime  │
    │    → σ₈ = 24,098  ✗ (×29,714 overgrowth)    │
    └─────────────────────────────────────────────┘
```

## Quick Calculation

```python
import math

C = 2.32  # discrete renormalization prefactor

# Lorentzian G_eff(k)/G
def geff_ratio(k, k_transition):
    return 1.0 + (C**2 - 1) / (1.0 + (k / k_transition)**2)

# Scenario A: Λ-locked (super-Hubble)
k_lambda = 0.0014  # h/Mpc
print("Scenario A (Λ-locked):")
print(f"  k = 0.01 h/Mpc: G_eff/G = {geff_ratio(0.01, k_lambda):.4f}")
print(f"  k = 0.1  h/Mpc: G_eff/G = {geff_ratio(0.1, k_lambda):.4f}")
# → All structure scales have G_eff/G ≈ 1

# Scenario B: 10 Mpc
k_10mpc = 0.1  # h/Mpc
print("\nScenario B (10 Mpc):")
print(f"  k = 0.01 h/Mpc: G_eff/G = {geff_ratio(0.01, k_10mpc):.4f}")
print(f"  k = 0.1  h/Mpc: G_eff/G = {geff_ratio(0.1, k_10mpc):.4f}")
# → Enhancement active → explosive growth
```

## Why Λ-Locking Works

The screening length from Λ:
```
L_Λ = 1/√Λ ≈ 4.4 Gpc ≈ H₀⁻¹
```

Structure formation operates at:
```
k ≳ 0.01 h/Mpc  (scales ≲ 600 Mpc)
```

Since k_Λ = 0.0014 h/Mpc << 0.01 h/Mpc, **all structure scales are screened**.

This is not a coincidence or tuning — it follows directly from Λ ∝ H₀².

## The Sharp Dichotomy

| Transition scale | σ₈ | Verdict |
|-----------------|-----|---------|
| L_Λ ~ 4.4 Gpc (Λ-locked) | 0.814 | Safe (0.4% excess) |
| 10 Mpc | 367 | Catastrophic |
| 1 Mpc | 24,098 | Catastrophic |

There is no middle ground. The transition must be at or above the Hubble scale.

## Next Steps

1. Read the full paper: `Cosmological_Growth_Constraints_...pdf`
2. Run `examples/run_scenarios.py` to reproduce the results table
3. Explore `src/geff_coupling.py` for the Lorentzian G_eff model
4. Check `data/scenario_results.json` for all numerical results

## Citation

```bibtex
@article{magnusson2026cosmogrowth,
  author = {Magnusson, Morten},
  title  = {Cosmological Growth Constraints on Λ-Locked Discrete Entropic Gravity},
  year   = {2026}
}
```
