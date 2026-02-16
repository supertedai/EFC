# Discrete Entropic Gravity on a Cubic Graph — Quick Start Guide

## 5-Minute Overview

**Problem**: Modified gravity models typically introduce ad-hoc interpolating functions to recover MOND-like behaviour. Can MOND emerge from a purely discrete, graph-based operator?

**Answer**: Yes. A discrete AQUAL operator on a cubic lattice with Λ-locked bulk entropic coupling reproduces both Newtonian and MOND regimes — but with two quantitative departures.

## The Key Idea

```
    Cubic Graph (N³ nodes)
           │
           ▼
    AQUAL weights w_ij = μ(|∇Φ|/a₀)
           │
           ▼
    ┌──────┴──────┐
    │             │
    ▼             ▼
  Strong field   Weak field
  g ∝ r⁻²       g ∝ r⁻¹
  (Newton)       (MOND-like)
                   │
                   ▼
              BUT with C ≈ 2.32
              a₀,eff ≈ 5.4 a₀
```

The transition between regimes is set by **Λ-locking**:
```
L_Λ ∝ 1/√Λ       (screening length from cosmological constant)
a₀ = c²/L_Λ       (acceleration scale)
```

## Quick Calculation

```python
import math

# --- AQUAL interpolating function ---
def mu(x):
    """Standard interpolating function μ(x) = x/√(1+x²)"""
    return x / math.sqrt(1 + x**2)

# Strong field (x >> 1): μ → 1 (Newtonian)
print(f"μ(100) = {mu(100):.4f}")   # ≈ 1.0000

# Weak field (x << 1): μ → x (MOND)
print(f"μ(0.01) = {mu(0.01):.4f}") # ≈ 0.0100

# --- Discrete renormalization prefactor ---
C = 2.32  # converged value from N=41 lattice

# Standard MOND: g = √(a₀ g_N)
# Graph MOND:    g = C √(a₀ g_N)
# Effective:     a₀,eff = C² a₀

a0_eff_ratio = C**2
print(f"a₀,eff / a₀ = {a0_eff_ratio:.1f}")  # 5.4

# --- Λ-locked acceleration scale ---
Lambda = 1.11e-52  # m⁻² (Planck 2018)
c = 2.998e8        # m/s
a0_physical = c**2 * math.sqrt(Lambda)
print(f"a₀ = {a0_physical:.2e} m/s²")  # ~9.5e-11
```

## Five Kill Tests (Summary)

| # | Test | What it checks | Result |
|---|------|---------------|--------|
| KT1 | Newton/MOND recovery | Slopes: −2.0 and −1.0 | PASS |
| KT2 | Prefactor convergence | C → 2.32 (topology-intrinsic) | PASS |
| KT3 | Mass scaling | r_trans ∝ M^0.18 (not 0.5) | Departure |
| KT4 | Broken superposition | 13.7% nonlinear violation | PASS |
| KT5 | External field effect | Monotonic EFE present | PASS |

## What This Means

1. **C ≈ 2.32 is real** — it persists across resolutions and binning geometries. It is *not* a numerical artifact but a discrete renormalization of the infrared response.

2. **Weak mass scaling** — the transition radius depends primarily on L_Λ (the cosmological screening length), not on local mass. This is a *structural departure* from standard MOND.

3. **No catastrophic growth** — a minimal cosmological check shows σ₈ suppressed by 0.7% relative to ΛCDM, consistent with S₈ tension direction.

## Next Steps

1. Read the full paper: `Discrete_Entropic_Gravity_...pdf`
2. Run `examples/run_kill_tests.py` to reproduce kill-test logic
3. Explore `src/aqual_operator.py` for the AQUAL weights
4. Check `data/convergence_table.json` for C vs N data

## Citation

```bibtex
@article{magnusson2026discreteentropicgravity,
  author = {Magnusson, Morten},
  title  = {Discrete Entropic Gravity on a Cubic Graph},
  year   = {2026},
  doi    = {10.6084/m9.figshare.31348411}
}
```
