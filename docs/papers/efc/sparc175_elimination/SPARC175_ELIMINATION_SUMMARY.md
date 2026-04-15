# SPARC 175 Systematic Elimination Study

**Date:** 2026-04-15  
**Status:** Complete  
**Key result:** 1 per-galaxy parameter is necessary and sufficient

---

## Elimination Chain

| # | Model | FLOW win% | Params | Verdict |
|---|-------|-----------|--------|---------|
| 1 | μ(g) — BE exponential | 27.4% | 1 global | FALSIFIED |
| 2 | μ(g) — screening power-law | 27.4% | 1 global | FALSIFIED |
| 3 | μ(g) — regularized BE (ε, g_min, ∛) | 27-29% | 2 global | FALSIFIED |
| 4 | μ(g, ∇g) — gradient | 27.4% | 3 global | FALSIFIED (shuffle p=0.36) |
| 5 | μ(g, Σ) — surface density | 27.4% | 5 global | SPURIOUS (Σ≡g) |
| 6 | μ(g, Σ, ω) — 2-variable | 27.4% | — | NO SIGNAL |
| 7 | Additive V²_bar + V₀² | 3.2% | 1 global | CATASTROPHIC |
| 8 | Additive V²_bar + cored | 14.5% | 2 global | WORSE |
| 9 | Additive V²_bar + log | 21.0% | 2 global | WORSE |
| **10** | **Hybrid μ(g) + A_gal·f(r)** | **72.6%** | **1/galaxy** | **MATCHES NFW** |

NFW reference: ~73% FLOW win, 2 params/galaxy

## Numerics Verification

Smoothing, rebinning, and noise injection show FLOW failure is physics (max 4.5% change), not artifacts.

## Hybrid Model

```
V² = V²_bar · μ(g; g†) + A_gal · r/(r + r₀)
g† = 2.66e-10 m/s², r₀ = 2.37 kpc (global)
A_gal = free per galaxy (1 param)
```

| Regime | 0-param win% | 1-param win% | NFW (2-param) |
|--------|-------------|-------------|---------------|
| FLOW | 27.4% | **72.6%** | ref |
| TRANSITION | 23.3% | **65.1%** | ref |
| LATENT | 74.1% | **88.9%** | ref |
| **Med χ²/dof** | 9.98 | **2.71** | 2.64 |

## A_gal Properties

- **Stable:** inner/outer ρ = 0.741, sign agreement 76%
- **Robust:** LOO CV = 12%, sign flips ≈ 0%
- **Scales with dynamics:** |A_gal| vs V²_max ρ = 0.53
- **Unpredictable:** R² = 0.02 from all baryonic observables
- **Sign:** FLOW/TRANS mostly negative, LATENT mixed

## Key Physical Findings

1. a₀ converges to MOND scale naturally (1.009 × a₀_MOND)
2. LATENT dominance is robust regardless of model (74-89%)
3. Regime separation is real (Mann-Whitney p < 1e-4)
4. Neither functional form nor additional local variables fix FLOW
5. One per-galaxy degree of freedom is necessary and sufficient

## Core Conclusion

> "The failure is not in the functional form, but in the absence of
> an additional degree of freedom. Galaxy rotation curves require at
> least one galaxy-specific parameter beyond the baryonic mass
> distribution."

## Scripts

All in `scripts/`:
- `sparc175_multicomponent_killtest.py` — BE μ + NFW
- `sparc175_regularized_be.py` — 3 regularized forms
- `sparc175_screening_test.py` — power-law classification
- `sparc175_gradient_test.py` — G1 gradient test
- `sparc175_sigma_diagnostic.py` — Σ correlation check
- `sparc175_mu_g_sigma.py` — μ(g,Σ) model
- `sparc175_2var_diagnostic.py` — (Σ,ω) joint analysis
- `sparc175_additive_test.py` — additive models
- `sparc175_numerics_check.py` — numerics sanity
- `sparc175_one_param_test.py` — hybrid model
- `sparc175_agal_analysis.py` — A_gal correlations
- `sparc175_agal_stability.py` — stability tests
