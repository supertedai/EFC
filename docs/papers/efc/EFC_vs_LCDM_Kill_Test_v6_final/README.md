# EFC vs ΛCDM: Complete Kill-Test (v6 final)

## AI-Friendly Package

**DOI**: [10.6084/m9.figshare.31964847](https://doi.org/10.6084/m9.figshare.31964847)
**Version**: 6.0 (final)
**Author**: Morten Magnusson (ORCID: 0009-0002-4860-5095)
**Date**: April 8, 2026
**License**: CC-BY-4.0

## Overview

A **comprehensive kill-test** of Energy-Flow Cosmology (EFC) against ΛCDM across six
independent probes spanning galactic to cosmological scales. Starting from a single
action with two field parameters `(K0, m²)`, EFC produces
`μ = 0.94, η = 1.23, Σ = 1.05` from *one mechanism* — stiffness and slip are not
independent.

Cobaya minimize runs against Planck 2018 (`plik_lite` TTTEEE + lowl + lensing), BAO,
and Pantheon+ consistently return **Δχ² ≤ 0 in the EFC direction** across all four
dataset/parametrization combinations. The same parameter values
`(K0 ≈ 1.55–1.68, m² ≈ 0.0032–0.0038)` reproduce the correct `(μ, Σ)` independently of
starting point.

**Headline result**: EFC cannot be rejected on current data. Full MCMC with Bayes
evidence is the remaining definitive test.

## Session Corrections (v6 merge of v2, v4 + April 8 cobaya runs)

1. CMB primary treated as EFC test ⇒ L0, α_S → 0, neutral by construction
2. A_L anomaly mis-assigned to L0 ⇒ corrected to L2 (lensing at z ~ 0.5–3)
3. K(ρ) bridge without screening: K̄ = 643 (413× gap) ⇒ fixed with Θ(ρ)
4. Full-strength δλ: η = 2.34 ⇒ V'' counter-term reduces to f = 0.15
5. A_lens-only cobaya ⇒ replaced with full `plik_lite` + explicit `K0/m²` run
6. Σ → 1 without `plik_lite` ⇒ confirmed: slip signal lives in high-ℓ TT+TE+EE

## Regime Architecture

| Regime | Redshift | Coupling | Physics |
|--------|----------|----------|---------|
| L0 | z > 1100 | α_S → 0 | Standard GR + Standard Model |
| L1 | 30 < z < 1100 | linear growth | post-recombination |
| L2 | 0.5 < z < 30 | α_L2 ≠ 0 | late-time modification |
| L3 | z ~ 0 | full entropy-flow | galactic / local |

## Core Equations

### 1. K(ρ) Bridge (Stiffness)
```
μ(k) = 1 / (1 + R(k))
R(k) = K0 · Θ(ρ) · (Γ'φ̇)² · a⁴ / (M_Pl² · F · k⁴)
Θ(ρ) = exp(−(ρ/ρ*)²)
```
Setting `μ(k = 0.05 h/Mpc) = 0.94` yields `K0 = 1.66`.
The same `K0` controls flat rotation curves at L3 (Θ ≈ 1 at both cosmological and dwarf-galaxy outer densities).

### 2. Gravitational Slip from δλ
```
δλ = (V''/a²)·δφ − (K·k²/a²)·δφ + ...
f = 1 − V''(φ̄) / (K(ρ̄) · k²/a²)
```
With `m² = 0.0035`: `f = 0.15 ⇒ η = 1.23 ⇒ Σ = 1.05`.
At full strength (`f = 1`): `η = 2.34` (excluded).
Viable window `f ∈ [0.12, 0.18]` (25% wide) is not fine-tuned.

### 3. Predictive Chain
```
K0 = 1.66  ─R∝k⁻⁴─────────────→  μ = 0.94         (stiffness)
m² = 0.0035 ─f=1−V''/Kk²────────→  f = 0.15 → η = 1.23 → Σ = 1.05  (slip)
```
Plus: `Θ → 0` (GR in Solar System); `c_T = c` (GW170817 safe); σ₈ suppressed −1.4%
(CAMB verified).

## Probe Results (6 probes)

| # | Probe | Regime | EFC | ΛCDM | ΔAIC | Verdict |
|---|-------|--------|-----|------|------|---------|
| 1 | DDO 154 rotation curve | L3 / FLOW | χ²_red = 0.05 | χ²_red = 2.71 | **+35.4** | **decisive for EFC** |
| 2 | Multi-component SPARC refit | L3 | 100% success | 5% success | ΔAIC = −126 (NGC 7331) | **EFC** |
| 3 | Bullet Cluster | L2→L3 | χ²_red = 0.46 | χ²_red = 0.55 | +0.6 | tied |
| 4 | CMB Primary | L0 | identical to ΛCDM | baseline | 0 | neutral by construction |
| 5 | A_L lensing (μ,Σ) | L2 | Δχ² = −0.45 | baseline | — | **EFC** |
| 6 | Cobaya minimize (full chain) | L2 | Δχ² = −0.30 to −0.81 | baseline | — | **EFC** |

## Cobaya Minimize Results (all four runs)

| Run | Dataset | Parameters | Δχ² | Engine |
|-----|---------|-----------|-----|--------|
| MGCAMB | plik_lite + lowl + lensing (free cosmo) | μ₀, Σ₀ | **−0.45** | direct eval |
| A_lens proxy | plik_lite + lowl + lensing (fixed cosmo) | A_lens | **−0.81** | cobaya minimize |
| A_lens free | plik_lite + lowl + lensing (free cosmo) | A_lens | **−0.70** | cobaya minimize |
| K0, m² | lowl + lensing + BAO + Pantheon+ | K0, m² | **−0.30** | cobaya bobyqa |

All runs: CAMB 1.6.6, cobaya 3.6.2. **All four return Δχ² ≤ 0** — direction stable
across dataset combinations and parametrizations.

## Sector Decomposition (K0/m² run)

| Sector | ΛCDM χ² | EFC χ² | Δχ² |
|--------|---------|--------|-----|
| lowl TT | 20.130 | 19.941 | −0.189 |
| lowl EE | 395.831 | 395.761 | −0.070 |
| Lensing | 9.547 | 9.218 | **−0.329** |
| BAO | 13.216 | 13.037 | **−0.179** |
| Pantheon+ | 1405.744 | 1406.212 | +0.468 |
| **Total** | **1844.468** | **1844.168** | **−0.300** |

Lensing and BAO favour EFC. Pantheon+ marginally favours GR
(cost of ΔH₀ = +0.90 km/s/Mpc — pointing toward the Hubble tension).

## Parameters at Minimum

| Parameter | Ref v5 | ΛCDM | EFC | Δ |
|-----------|--------|------|-----|----|
| K0 | 1.66 | — | 1.552 | −6% |
| m² | 0.0035 | — | 0.00318 | −9% |
| μ₀ | 0.940 | 1.000 | 0.9437 | −0.056 |
| Σ₀ | 1.050 | 1.000 | 1.069 | +0.069 |
| A_lens | 1.036 | 1.000 | 1.143 | +0.143 |
| H₀ (km/s/Mpc) | — | 67.89 | 68.79 | **+0.90** |
| σ₈ | — | 0.811 | 0.797 | −0.014 |
| Ω_m | — | 0.302 | 0.299 | −0.003 |

K0 and m² are 6–9% below v5 reference but produce μ₀ = 0.944 and Σ₀ = 1.069, inside
the sweet-spot window `[0.93, 0.96] × [1.03, 1.07]`.

## Slip Calibration Scan

| f | η | Σ | Δχ² (est.) | Status |
|---|---|---|------------|--------|
| 0.00 | 1.04 | 0.96 | +30 | Excluded |
| 0.12 | 1.20 | 1.03 | +4 | Entering window |
| **0.15** | **1.23** | **1.05** | **−0.45** | **Sweet spot** |
| 0.18 | 1.27 | 1.07 | +0.5 | Edge of window |
| 1.00 | 2.34 | 1.57 | ≫ 0 | Excluded |

## Two Separate Signals

EFC contains two signals with distinct dataset requirements:

- **μ-signal (K0)**: activated by BAO, lensing, growth-rate data.
  Stable `K0 ≈ 1.55–1.68` with or without `plik_lite`.
- **Σ-signal (m²)**: activated by high-ℓ TT+TE+EE.
  Without `plik_lite`, `Σ → 1` (no likelihood gradient).
  Data constraint, not model failure.

## Parameter Structure (Occam)

| Type | ΛCDM | EFC |
|------|------|-----|
| Baseline cosmological | H₀, Ω_b, Ω_cdm, A_s, n_s, τ (6) | H₀, Ω_b, A_s, n_s, τ (5) |
| Model-specific | Ω_Λ (flatness) | K0, m² (2) |
| Per-galaxy | M₂₀₀, c per galaxy (+2) | none (0) |
| **Global total** | **6** | **7 (+1)** |

**One extra global parameter; per-galaxy halo fitting eliminated entirely.**

## μ(k) Table — GR Recovery at Local Scales

| k [h/Mpc] | Θ | R(k) | μ(k) | Scale |
|-----------|---|------|------|-------|
| 0.001 | 1.000 | 0.064 | 0.940 | Super-horizon |
| 0.050 | 1.000 | 0.064 | **0.940** | **CMB lensing (anchor)** |
| 0.100 | 1.000 | 0.004 | 0.996 | BAO/LSS |
| 5.0 | 0.087 | 6 × 10⁻¹¹ | 1.000 | Galactic |
| 50 | 0.000 | 0 | 1.000 | Solar System |

With `K0 = 1.66`. **GR recovered at galactic and solar-system scales** via `Θ(ρ) → 0`.

## Package Contents

```
EFC_vs_LCDM_Kill_Test_v6_final/
├── README.md                          # This file
├── QUICKSTART.md                      # 5-minute introduction
├── MANIFEST.md                        # File listing with descriptions
├── CITATION.cff                       # Citation metadata
├── index.json                         # Machine-readable metadata
├── EFCvsLCDMKillTest.jsonld           # Schema.org semantic data
├── schema.json                        # JSON Schema for validation
├── citations.bib                      # BibTeX references
├── *.pdf                              # Original paper
│
├── data/
│   ├── parameters.json                # K0, m², sweet-spot window, ρ*, etc.
│   ├── cobaya_runs.json               # All four cobaya minimize runs
│   ├── sector_decomposition.json      # Per-sector Δχ²
│   ├── probe_results.json             # 6 probes with verdicts
│   └── mu_k_table.json                # μ(k) at K0 = 1.66
│
├── src/
│   ├── __init__.py
│   ├── k_rho_bridge.py                # K(ρ) bridge, Θ(ρ), μ(k)
│   ├── gravitational_slip.py          # f, η, Σ from δλ counter-term
│   ├── kill_test_suite.py             # Six-probe kill-test runner
│   └── cobaya_minimize.py             # Δχ² aggregator for all runs
│
└── examples/
    ├── run_kill_tests.py              # Reproduce verdict of all six probes
    └── slip_window_scan.py            # Reproduce f∈[0.12,0.18] sweet spot
```

## Quick Usage

```python
from src.k_rho_bridge import KRhoBridge
from src.gravitational_slip import GravSlip

# K(ρ) bridge
bridge = KRhoBridge(K0=1.66)
print(bridge.mu_k(k=0.05))   # 0.940 (CMB lensing anchor)
print(bridge.mu_k(k=5.0))    # 1.000 (galactic — GR recovered)

# Gravitational slip
slip = GravSlip(m2=0.0035)
print(slip.eta)              # 1.23
print(slip.Sigma)             # 1.05
print(slip.f)                 # 0.15 (sweet spot)
```

## Epistemic Status

**Layer B (technical construction)** → **Layer C** (empirically testable via full MCMC).

- **What EFC is**: a minimal, testable extension of GR; a real competitor to ΛCDM
  that cannot be rejected on current data, with `Δχ² ≤ 0` across all tested dataset
  combinations, and whose parameter shifts (`H₀ ↑, Ω_m ↓, σ₈ ↓`) point toward known
  cosmological tensions as a **consequence** of the theory, not a fit target.
- **What EFC is not**: proven correct; decisively better than ΛCDM by Bayesian standards;
  tested with a full posterior.

## Open Questions

1. **Full MCMC posterior**. Sample `(K0, m², H0, Ω_b, Ω_cdm, A_s, n_s, τ)` against
   `plik_lite + lowl + lensing + BAO + Pantheon+`. Cobaya yaml ready; requires ≥ 16 GB RAM.
2. ~~**175-galaxy universality**. Multi-component refit on 5 of 175 SPARC galaxies.
   Extension with single `(K0, m²)` tests universality.~~
   → **Partially resolved (2026-04-11)**: single-component extension to all 175 SPARC
   galaxies gives an EFC win rate of **60.2 %** (42.1 % EFC_decisive), median ΔAIC =
   +6.21, Mann-Whitney p ≈ 0 between FLOW and LATENT regimes, and ρ(ΔAIC, v_max) =
   0.11 (no mass bias). Cherry-picking objection against probe-2 is refuted. See
   [`../Kill-Test v6 Universality_SPARC175/`](../Kill-Test%20v6%20Universality_SPARC175/).
   Full multi-component universality with fixed `(K0, m²)` across all galaxies is
   still open.
3. **Physical origin of m²**. `m² ≈ 0.0032–0.0038` (`m/H₀ ≈ 0.06`) is analogous to Λ.
   Derivation from inflation or stability conditions is open.
4. **A_lens/Σ₀ degeneracy**. A proper MGCAMB run with `(μ₀, Σ₀)` as primary MG
   parameters will disentangle the partial degeneracy in the bobyqa run.

## Falsification Criteria

1. Full MCMC returning `Δχ² > 0` with `Bayes factor > 3` against EFC → **reject**
2. Any cobaya run returning `Δχ² > 0` in EFC direction → already **passed** (4/4)
3. μ(k) at `k = 5 h/Mpc` deviating from 1 by more than 10⁻⁴ → fails Solar System
4. η outside `[1.20, 1.27]` at `m² = 0.0035` → fails slip calibration
5. Σ signal absent from high-ℓ TT+TE+EE after plik_lite inclusion → **resolved**

## Related EFC Papers

- [EFC Relativistic Action](../EFC_Relativistic_Action_Field_Equations_Perturbation_Theory_and_Extraction/) — Action, field equations, perturbation theory (DOI: 10.6084/m9.figshare.31876324)
- [Systematic Localization](../Systematic_Localization_of_Late-Time_Cosmological_Signals_in_Modified_Gravity_CMB_Survival_the-Lensing_Barrier/) — CMB survival & lensing barrier (DOI: 10.6084/m9.figshare.31368433)
- [EFC H0-S8 Tensions](../EFC-H0-S8-Tensions/) — Cosmological tensions programme
- [Discrete Entropic Gravity](../Discrete_Entropic_Gravity_on_a_Cubic_Graph_Emergent_Newton_and_MOND_Regimes_with_Λ-Locked_Screening/) — Graph-AQUAL operator (DOI: 10.6084/m9.figshare.31348411)
- [Bullet Cluster EFC](../bullet_cluster_efc/) — Cluster confrontation
- [SPARC 175](../Comprehensive-analysis-of-175-SPARC-galaxies-demonstrating-regime-dependent-validity-in-rotation-curve-modeling/) — Rotation curve database
- [**Kill-Test v6 Universality (SPARC 175)**](../Kill-Test%20v6%20Universality_SPARC175/) — **Probe-2 universality extension to all 175 galaxies; cherry-picking objection refuted (2026-04-11)**
- [Regime Transition Test](../Consistency_of_Scale_Dependent_Gravitational_Response_in_EFC_Numerical_Regime_Transition_Test/) — L1→L2 μ(k,a) consistency

## Citation

```bibtex
@article{magnusson2026efckilltest,
  author  = {Magnusson, Morten},
  title   = {{EFC} vs {$\Lambda$CDM}: Complete Kill-Test --
             From Rotation Curves to Planck: A Consistent
             Low-Dimensional Alternative},
  year    = {2026},
  note    = {Session Technical Note v6 (final)},
  doi     = {10.6084/m9.figshare.31964847}
}
```
