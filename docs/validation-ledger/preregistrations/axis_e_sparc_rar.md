# Preregistration proposal — Axis 1: the E(g) exponent (linear vs square-root BE screening)

**Status:** `proposed — awaiting author freeze` (not executed, not fitted, not published)
**DOI under test:** 10.6084/m9.figshare.31941465 (KC1), 10.6084/m9.figshare.31878760, 10.6084/m9.figshare.31878334, 10.6084/m9.figshare.31942821
**Related register:** `docs/validation-ledger/data/form_status_register.json`

## 1. What is being discriminated

The published corpus carries two competing Bose–Einstein screening exponents for the same
gravitational response:

- **Linear:** μ(g) = 1/(exp(g/a₀) − 1) — argument exponent α = 1.
- **Square-root:** μ(g) = 1/(exp(√(g/a₀)) − 1) — argument exponent α = 1/2, derived from
  E ∝ √g in 31878334, 31878760, 31941465.

These are **competing forms for the same observable**, not two regimes of one law, unless a
regime mapping is supplied. No source supplies one. This test decides between them on a single
frozen observable, with no post hoc model selection.

## 2. Hypothesis under test

**H1 (square-root):** the RAR is better described by the √(g/a₀) exponent, i.e. the argument
exponent is 1/2.
**H0 (null for this axis):** the linear g/a₀ exponent describes the RAR at least as well.

The test is **two-sided** in reporting: it reports the likelihood comparison, not a
pre-committed winner.

## 3. Frozen observable

μ(g) = g_obs / g_bar as a function of g_bar (the Radial Acceleration Relation, RAR), evaluated
over the deep-MOND and transition regimes.

## 4. Measurement chain (raw data → instrument → measurer → target → proxy)

| Layer | Content |
|---|---|
| Raw data | galaxy line-of-sight rotation velocities; photometry and gas maps for the baryonic mass model |
| Instrument | rotation-curve spectroscopy (velocities); photometry/stellar-population synthesis + gas kinematics (baryonic mass) |
| Measurer | (a) g_obs from the rotation curve at each radius; (b) g_bar from the baryonic mass model via Newtonian gravity |
| Target | the screening exponent α in the BE argument |
| Proxy chain | velocities → baryonic mass model → g_bar, g_obs → μ(g) → BE-exponent likelihood |

## 5. What is frozen vs what is a declared nuisance

**Frozen before any fit:**

- **a₀ — but WHICH a₀ is author-gated.** Three candidate values are in circulation and must be
  fixed to exactly one before the test is valid:
  - `1.2e-10 m/s²` — the value in the papers' code and index.json (MOND scale).
  - `6.5e-10 m/s²` — absent from every paper `index.json`; appears in `framework_atlas.jsonld`,
    the EFC-VAL-2026-006 atlas seed, and a test comment (plus unrelated high-z data files),
    so it is not a canonical paper a₀.
  - `a₀,eff = C²·a₀ ≈ 5.4·a₀` (C ≈ 2.32) — derived in 31348411 and 31348417.
  - **Decision required:** name the canonical a₀ (proposal: `1.2e-10 m/s²`, with `a₀,eff`
    stated separately). The preregistration is INVALID until this is fixed.
- **The two competing forms** — both are fully specified; no form is added or altered after
  data are seen.
- **The observable and its definition** (μ = g_obs/g_bar, RAR).

**Declared nuisance parameters (pre-declared priors/spread required, not fitted freely):**

- **Baryonic M/L ratio** — this is the dominant paradigm leak. It must be frozen from an
  independent source OR given a pre-declared prior. **Decision required.**
- Distance, inclination, gas-mass model.

**A retrodiction with an unfrozen M/L is a fit, not a test.** This document will not claim
"paradigm-free"; it claims **lean** (see §7).

## 6. Protocol discipline

- a₀ locked from a named value before any likelihood is computed; no free re-fit of a₀.
- Same likelihood, same nuisance treatment, same sample for both exponents.
- No model selection after inspecting residuals.
- Pre-declared **holdout** rule (train/holdout split or leave-one-out cross-validation)
  specified before the fit.

## 7. Self-inclusion matrix

| Field | Value |
|---|---|
| raw data | galaxy kinematics + baryonic photometry/gas |
| instrument | spectroscopy + photometry |
| measurer | g_obs, g_bar estimators |
| target | BE exponent α |
| proxy | RAR μ(g) |
| paradigm content | **lean** — lower ΛCDM dependence than σ₈/fσ₈, but M/L, distance, and the baryonic mass model are model-laden, NOT paradigm-free |
| holdout | required, pre-declared |
| falsifier | see §8 |

## 8. Falsifier and threshold

The square-root form is **rejected** if a pre-specified likelihood comparison (ΔlnL or
equivalent, computed with identical nuisance treatment) favors the linear form beyond the
pre-declared threshold, OR if the square-root form fails a pre-declared goodness-of-fit
criterion. The threshold and statistic are fixed before the fit, not after.

## 9. What this test does NOT decide

- It does not measure the BE occupation number directly; it tests a galactic proxy.
- It does not test Γ(ρ) (the density form) — that is a separate axis.
- It does not decide η_grav = motor-lag (the F5 open mapping).

## 10. Compute-gate note

Whether a frozen-a₀ retrodiction fits inside the existing `sparc_nuts` allowlisted mode is
**an author decision, not an assumption here.** The `.14` queue (`/opt/hermes-opus/efc-arbeid/koe.py`)
currently exposes only `{steg, kjeder}` for `sparc_nuts` and rejects unknown fields. A frozen-a₀
retrodiction therefore either needs a new human-authorized allowlist entry
(e.g. `sparc_retrodiction_frozen_a0`) or a field extension to the queue contract. This document
registers the intent; it does not authorize any `.14` run.

## 11. Open author decisions (blocking)

1. Canonical a₀ value (confirm `1.2e-10`; state `a₀,eff` separately).
2. How M/L is frozen (independent source vs pre-declared prior).
3. Whether this axis runs first, or in parallel with Axis 2.
