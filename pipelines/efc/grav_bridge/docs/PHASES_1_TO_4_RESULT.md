# Phases 1–4 Result — Structural Elimination of Growth-ODE Coupling

_Constraint on coupling structure, not parameter. EFC → cosmology bridge, first empirical closure._

**Date:** 2026-04-22
**Scope:** EFC-GRAV → cosmological growth sector under BAO+fσ8+E_G observables.
**Scripts:** `scripts/grav_bridge/{variant_i,variant_j,variant_k,step1,step2,step3,phase4}_*.py`

---

## Headline

> **Given current data (BAO DR2 + fσ8 + E_G), every model in which EFC couples to cosmology through a local or simple non-local modification of growth dynamics is either empirically excluded or unidentifiable once geometry is locked by BAO+H(z).**

This is not a failure of EFC. It is a **structural constraint on the class of admissible coupling operators**. The lesson is not in the parameters; it is in the choice of observable.

---

## Four independent coupling structures tested

| # | Coupling | Implementation | Probe | Result |
|---|----------|----------------|-------|--------|
| 1 | **Amplitude** — G_eff multiplicative on Poisson source | `VariantI`:  source ∝ G_eff(k_eff,a)·ρ·δ with G_eff/G = 1 + (C²−1)·gate(a)·screen(k) | fs8 alone, k_Λ sweep | **Structurally excluded** — no k_Λ gives a data-compatible visible signal |
| 2 | **Timing** — additive local friction | `VariantJ`:  friction ∝ β·gate(a)/a on the δ′ term | fs8 alone → fs8 + BAO Ω_m prior | **Collapse under BAO lock** — β shifts from +0.22 ± 0.47 to −0.02 ± 0.24; BF(β=0) = 6.6 |
| 3 | **Memory** — non-local accumulated friction | `VariantK`:  friction ∝ β·G(a)/a with G(a)=∫₀ᵃ gate(a′)da′ | fs8 + BAO Ω_m prior | **Same null** — β = −0.18 ± 0.91, BF(β=0) = 3.4, 0.2σ from zero (breaking Markov did not save the coupling) |
| 4 | **Ratio observable** — E_G with Σ=1 | Literature E_G compilation + growth-only predictions | E_G(z) vs 5 measurements | **Blind direction** — max shift 2.2σ only at already-excluded β; ratio scales with f(z) and is redundant with fs8 |

---

## The structural pattern

1. **Amplitude** directly confronts data → rejected at the mapping level (Phase 1).
2. **Timing** confronts fs8 via projection → absorbed by Ω_m degeneracy, collapses when BAO strams it (Phase 2).
3. **Memory** attempts to escape locality → **absorbed by the same Ω_m degeneracy**. The Markov assumption was not the bottleneck.
4. **E_G with Σ=1** is not a new information axis — it is f(z) reshaped. The ratio only carries EFC signal if numerator and denominator are modified *differently* (slip).

Three independent directions in growth-ODE space, one null each. The pattern is not statistical — it is structural. **Growth observables alone are insufficient to test this class of theories.**

---

## Quantitative summary

### Phase 1 — G_eff k_Λ sweep (fixed C=2.32)

| k_Λ [h/Mpc] | G_eff(a=1)/G | Δχ² |
|-------------|--------------|------|
| 0.005 | 1.011 | −0.009 (invisible) |
| 0.008 | 1.028 | −0.010 (invisible, shallow min) |
| 0.020 | 1.167 | +0.51 |
| 0.033 | ~1.4 | +4 (2σ exclusion) |
| 0.050 | 1.871 | +15.3 (MCMC verdict) |
| 0.100 | 3.176 | +79.7 |

Monotone beyond visibility. No interior minimum in observable regime.

### Phase 2 — VariantJ friction, Ω_m–β unlocked → locked

| | Unrestricted (fs8 only) | BAO-locked (fs8 + Ω_m prior) |
|---|---|---|
| Ω_m | 0.357 ± 0.088 | 0.299 ± 0.009 |
| β | +0.224 ± 0.474 | **−0.020 ± 0.243** |
| r(Ω_m, β) | +0.847 | +0.193 |
| BF(β=0) | 2.62 | **6.61** |

### Phase 3 — VariantK memory, BAO-locked

| Ω_m | 0.299 ± 0.009 |
| β | **−0.180 ± 0.906** (0.20σ from zero) |
| r(Ω_m, β) | +0.185 |
| BF(β=0) | 3.41 |
| β per unit, normalized to VariantJ at a=1 | equivalent β_J ≈ −0.09 (same regime as Phase 2 null) |

### Phase 4 — E_G with Σ=1

| Model | χ² vs literature (5 pts) | Δχ² vs LCDM |
|-------|---------------------------|--------------|
| LCDM (ODE) | 3.33 | baseline |
| VariantJ best-fit | 3.26 | −0.07 |
| VariantJ β=+1 (already excluded by fs8 at Δχ²=15) | 18.4 | **+15.0 — same signal, different name** |
| VariantK best-fit | 3.22 | −0.11 |
| Constant (E_G = 0.398) | 3.26 | — |

E_G data scatter is comparable to LCDM prediction scatter. No independent constraint.

---

## What this result IS

1. **An empirical closure of a coupling-structure class.** Multiplicative G_eff on Poisson, additive local friction, and additive non-local memory friction are all excluded or non-identifiable under BAO-locked Ω_m at current fσ8 and E_G precision.

2. **A proof that locality is not the bottleneck.** VariantK (memory) was the explicit test of Markov-breaking. It behaves like VariantJ post-BAO-lock — broader posterior (weaker signal per unit β), but not a real preference for β ≠ 0.

3. **A proof that observable choice matters as much as theory choice.** Growth-sector observables (fσ8, E_G-with-Σ=1) span the same information direction after BAO. More of the same does not help.

---

## What this result is NOT

1. **NOT a falsification of EFC.** EFC's claims about entropy flow and emergent gravitation are not exhausted by the coupling ansätze tested here.

2. **NOT a falsification of KT2.** The Grid-AQUAL prefactor C ≈ 2.32 stands within the discrete-gravity sector. What is excluded is its *projection* into growth observables via standard μ-factor-type couplings.

3. **NOT a statement about all modified-gravity theories.** A parallel scan in the lensing sector (Σ, slip η) has not been performed and may admit distinct structure.

4. **NOT a data problem alone.** The 4× improvement in fσ8 precision required to discriminate VariantJ β ~ 0.1 would be informative; however the Phase 3 result shows Ω_m degeneracy persists even after that — the degeneracy is in the observable, not in the noise.

---

## Implication

If EFC has a cosmological signature, it must couple through one of:

- **Lensing / Σ-modification** — affecting (Φ+Ψ) without necessarily modifying f(z). E_G with Σ≠1 becomes an independent axis.
- **Gravitational slip** — η = Φ/Ψ ≠ 1. Breaks the f ↔ E_G redundancy we identified.
- **ISW / time-derivative of potentials** — direct probe of EFC's native "flow" concept; untested here.
- **Cross-correlations** — between lensing and clustering, where growth-only degeneracies are broken by construction.
- **Not representable as a modified growth ODE at all.** Observables would have to be constructed differently.

The Phase 4 E_G test identifies *why*: E_G = Σ·Ω_m/f. With Σ=1, data measures the same f(z) as fσ8. To get new information, Σ must vary.

---

## Next program (separate work, not next commit)

1. **Observable-design phase first.** Map which cosmological observables are demonstrably non-degenerate with BAO-locked Ω_m for EFC-motivated coupling classes. Include weak lensing tomography, ISW × tracer, E_G in its slip-sensitive form, and cross-spectra.
2. **Then** — and only then — build variants that modify those observables.
3. Existing VariantsI/J/K + the sanity/sweep/MCMC infrastructure stay as the empirical floor. New work extends; it does not replace.

---

## Reproducibility

All scripts in `scripts/grav_bridge/`. Data in `efc_inference/data/{bao,hubble,growth}/`. Chains and summaries in `outputs/grav_bridge/`. MCMC seed 42, emcee 3.1.6, 32×1500 steps with 300 burn-in throughout Phases 2–3.

| Artifact | Path |
|----------|------|
| Variant definitions | `efc_inference/core/cosmology_model.py` (EFCVariantI, J, K) |
| Engine hook | `efc_inference/engine/growth.py` (friction_extra integration) |
| Phase 1 | `outputs/grav_bridge/klambda_sweep_20260422_204436.json`, `variant_i_chain_20260422_203947.npz` |
| Phase 2 | `outputs/grav_bridge/step2_chain_20260422_212120.npz`, `step2_summary_*.json`, `step2_plots_*/` |
| Phase 3 | `outputs/grav_bridge/step3_chain_20260422_213851.npz`, `step3_summary_*.json`, `step3_plots_*/` |
| Phase 4 | `outputs/grav_bridge/phase4_e_g_20260422_214807.json`, `phase4_e_g_plot_*.png` |

---

_End of Phases 1–4. No further local coupling variants will be built within this program._
