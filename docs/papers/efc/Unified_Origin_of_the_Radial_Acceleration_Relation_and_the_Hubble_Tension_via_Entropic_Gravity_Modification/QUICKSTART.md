# H₀-RAR Unification - Quick Start Guide

## 5-Minute Overview

**Problem**: Two major anomalies in astrophysics:
1. Hubble tension (H₀: 67.4 vs 73.0 km/s/Mpc)
2. Galaxy rotation curves (MOND/RAR phenomenology)

**Solution**: Both arise from the same mechanism—entropy-driven gravity modification.

## The Key Insight

```
                    Entropy-Driven Gravity Modification
                                 ↓
            ┌────────────────────┴────────────────────┐
            ↓                                         ↓
    Cosmological Scale                         Galactic Scale
    (Hubble Tension)                          (RAR/MOND)
            ↓                                         ↓
    a_H₀ = 0.047                              a_G = 0.107
            ↓                                         ↓
            └────────→ a_H₀ = ½ a_G ←────────────────┘
                      (Friedmann Constraint)
```

## Quick Calculation

```python
import math

# MOND interpolation at transition zone (g_bar/a₀ = 5)
mu = 5 / (1 + 5)  # = 0.833
mu_inv = 1 / mu   # = 1.20

# Phase difference (from entropy mapping)
delta_phi = 1.71

# Gravitational coupling from MOND
aG = math.log(mu_inv) / delta_phi  # = 0.107

# Friedmann constraint: a_H₀ = ½ a_G
aH0 = aG / 2  # = 0.0535

# Predict H₀
H0_cmb = 67.4  # km/s/Mpc (Planck)
H0_pred = H0_cmb * math.exp(aH0 * delta_phi)
print(f"Predicted H₀: {H0_pred:.1f} km/s/Mpc")  # 73.9

# Compare to observed
H0_obs = 73.0  # km/s/Mpc (SH0ES)
deviation = abs(H0_pred - H0_obs) / H0_obs * 100
print(f"Deviation: {deviation:.1f}%")  # 1.2%
```

## Key Equations

### 1. Entropy Mapping
```
S(z) = ½[1 - tanh((ln(1+z) - ln(4))/0.5)]
```
- z = 0 (today): S ≈ 0.996
- z = 1100 (CMB): S ≈ 0

### 2. Phase Difference
```
ΔΦ = Φ(S_today) - Φ(S_CMB) ≈ 1.71
```

### 3. Effective Gravity
```
G_eff = G₀ exp(a_G · ΔΦ)
```

### 4. The Friedmann Factor (NOT fitted!)
```
a_H₀ = ½ a_G
```
This ½ comes from H² ∝ G_eff, not from fitting.

## Why This Works

| Scale | Observable | Driver | Enhancement |
|-------|------------|--------|-------------|
| Galactic | Rotation curves | g_bar ≈ 5a₀ | ~20% |
| Cosmological | H₀ | Same a_G | ~9% (via Friedmann) |

The cosmic web resides in the MOND transition zone, so both scales feel the same gravitational enhancement.

## Falsification Test

If a_G from detailed SPARC rotation curve fits yields something very different from 0.1, the framework fails.

Current status:
- a_G from H₀ tension: 0.094
- a_G from MOND (g/a₀=5): 0.107
- Agreement: 14% (encouraging but needs direct fit)

## Next Steps

1. Read the full paper: `Unified_Origin_...pdf`
2. Run `examples/h0_prediction.py`
3. Explore `src/unification.py` for full analysis
4. Check `data/mond_table.json` for interpolation values

## Citation

```bibtex
@article{magnusson2026h0unification,
  author = {Magnusson, Morten},
  title = {Unified Origin of the RAR and Hubble Tension},
  year = {2026},
  doi = {10.6084/m9.figshare.31223908}
}
```
