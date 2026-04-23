# Phase 1 Result — Multiplicative G_eff Coupling Excluded

_Internal formalization. EFC-GRAV → cosmo bridge, first empirical test._

**Date:** 2026-04-22
**Scripts:** `scripts/grav_bridge/variant_i_{sanity,mcmc,klambda_sweep}.py`
**Chain / sweep artifacts:** `outputs/grav_bridge/variant_i_chain_20260422_203947.npz`, `outputs/grav_bridge/klambda_sweep_20260422_204436.json`

---

## Headline

> **No low-pass Fourier screening of G_eff with fixed C = 2.32 yields compatibility with fσ8 for any k_Λ where the signal is observable.**

The exclusion is structural, not parametric. Amplitude-visibility and amplitude-data-compatibility are locked together by the multiplicative mapping; the projection has no free direction along which the one can be satisfied without sacrificing the other.

---

## Setup

**Model:** [`EFCVariantI`](../../efc_inference/core/cosmology_model.py) — GRAV→cosmo bridge, C as MCMC-free.

**Background:** Pure ΛCDM (α = 0, no gate in expansion).

**Growth source (modified Poisson with G_eff multiplier):**
```
source(a) = (3/2) · G_eff(k_eff, a)/G · Ω_m / (a⁵ · E²(a))

G_eff(k, a) / G = 1 + (C² − 1) · gate(a) · screen(k)
gate(a)    = 1 / (1 + exp(−(a − a_t) / δ_a))       [logistic, a_t=0.5, δ_a=0.1]
screen(k)  = 1 / (1 + (k / k_Λ)²)                  [low-pass, MOND-consistent]
```

**Frozen:** C = 2.32 (KT2 Grid-AQUAL), Ω_m = 0.30, σ_8 = 0.81, H₀ = 70, k_eff = 0.1 h/Mpc.

**Data:** `efc_inference/data/growth/fs8_extended.csv` — 7 fσ8 measurements
(6dFGS z=0.02, SDSS MGS z=0.15, BOSS DR12 z=0.38/0.51/0.61, VIPERS z=0.76, FastSound z=0.85)
with BOSS DR12 3×3 covariance (ρ≈0.48, from Gil-Marín+2020) + diagonal elsewhere.

---

## MCMC Result (reference, k_Λ = 0.05)

16 walkers × 500 steps (burn-in 100), acceptance 0.65, τ ≈ 24.

| Quantity | Value |
|----------|-------|
| Ω_m posterior | 0.300 ± 0.063 (Planck-consistent) |
| C posterior | **1.20 ± 0.47** |
| σ distance from GR (C=1.00) | **0.43** |
| σ distance from KT2 prior (C=2.32) | **2.37** |
| p(C > 2.0) | 6.6% |
| Δlog L (C=1.00 → C=2.32) at Ω_m=0.30 | **−7.66** (Δχ² ≈ +15) |

MCMC collapses C to GR. Not flat posterior, not degenerate — an active preference.

---

## k_Λ Sweep (Phase 1 core result)

Fixed-parameter grid evaluation: Ω_m = 0.30, σ_8 = 0.81, C = 2.32, k_eff = 0.1 h/Mpc.

Δχ² = 2·(log L_LCDM − log L_GRAV) — positive means GRAV worse than LCDM.

| k_Λ [h/Mpc] | screen(k_eff) | G_eff(a=1)/G | Δχ² |
|-------------|----------------|--------------|------|
| 0.003 | 0.0009 | 1.004 | −0.004 |
| 0.005 | 0.0025 | 1.011 | −0.009 |
| 0.008 | 0.0064 | 1.028 | **−0.010** (shallow min) |
| 0.010 | 0.0099 | 1.043 | +0.001 |
| 0.015 | 0.0220 | 1.096 | +0.125 |
| 0.020 | 0.0385 | 1.167 | +0.505 |
| 0.030 | 0.0826 | 1.359 | +2.656 |
| 0.050 | 0.2000 | 1.871 | **+15.32** |
| 0.080 | 0.3902 | 2.699 | +52.03 |
| 0.100 | 0.5000 | 3.176 | +79.71 |
| 0.150 | 0.6923 | 4.014 | +136.02 |
| 0.200 | 0.8000 | 4.482 | +170.71 |

**Key thresholds:**

- **Visibility floor:** G_eff/G > 1.05 corresponds to k_Λ > 0.012. Below this, signal is below RSD systematic tolerance and no data-vs-model statement can be made.
- **2σ exclusion:** Δχ² > 4 at k_Λ ≈ 0.033.
- **4σ exclusion:** Δχ² > 16 at k_Λ ≈ 0.053 (consistent with the MCMC run at k_Λ = 0.05).
- **Monotonicity above visibility:** Δχ² is strictly increasing for k_Λ ≥ 0.010. No interior minimum exists in the observable regime.

The "minimum" at k_Λ ≈ 0.008 (Δχ² = −0.010) lies entirely in the null-test regime where signal is below noise. It is not a data-compatible projection — it is the absence of a test.

---

## What this result IS

1. **A structural exclusion of a mapping class.** The multiplicative coupling
   ```
   growth_source ∝ G_eff(k, a) · ρ · δ
   ```
   under low-pass Fourier projection with fixed amplitude C = 2.32 has no valid
   free projection parameter. Visibility and rejection scale together.

2. **An empirical constraint on the GRAV→cosmo interface.** The discrete-gravity
   prefactor C, as measured in KT2 (Grid-AQUAL), cannot be imported into
   cosmological growth via the standard Poisson-side μ-factor.

3. **A real preference, not a null result.** The MCMC posterior for C actively
   concentrates near 1 (GR), with the KT2 prior excluded at 2.4σ in this
   projection. Data responds; they do not shrug.

---

## What this result is NOT

1. **NOT a falsification of EFC.** EFC as a framework makes claims about the
   relationship between entropy flow and gravity that are not exhausted by the
   G_eff multiplicative ansatz.

2. **NOT a falsification of KT2.** The GRAV-sector measurement C ≈ 2.32 stands on
   its own within the Grid-AQUAL lattice framework. What is excluded is the
   *mapping* from that local measurement into the cosmological growth equation
   via multiplicative coupling.

3. **NOT an exclusion of scalar-tensor MOND bridges in general.** Other coupling
   forms — friction-channel, time-shift, anisotropy/slip, non-local memory — are
   untested here and may admit data-compatible solutions.

4. **NOT evidence that k_Λ is "too small" or "too large".** There is no interior
   minimum. There is no direction to tune.

---

## Implication

The coupling variable must be re-derived. The assumption
```
EFC → modify G → modify Poisson source
```
is a GR-shaped inheritance that data rejects under low-pass projection.

EFC's own structure (entropy flow, grid, emergent gravitation) points to
alternative coupling forms that are neither multiplicative nor source-side:

- **Friction-channel:** modify the δ′ term in the growth ODE (Hubble-drag-like, affects *when* growth happens, not *how much*).
- **Time-shift:** regime-dependent retarding of growth, asymmetric around z ≈ 1 (which matches the asymmetry already observed in VariantI fσ8 profile).
- **Anisotropic slip (Φ ≠ Ψ):** RSD measures velocity fields, which are not the same observable as the G_eff combination.
- **Non-local / memory:** growth depending on integrated flow history over a, not instantaneous G_eff(a).

---

## Phase 2 Entry Point

Test one alternative coupling at a time. First candidate: **friction-channel.**

Hypothesis: growth modification enters through the δ′-coefficient, not the source:
```
δ'' + [3/a + E'/E + β·gate(a)/a] · δ' − (3/2)·Ω_m/(a⁵·E²) · δ = 0
```
with β as the sole free EFC parameter (β=0 → LCDM exact).

The source is unchanged; no σ_8 amplitude degeneracy is introduced. The coupling
variable is timing, not strength. Next script: `variant_j_{sanity, sweep}.py`.

---

_End Phase 1._
