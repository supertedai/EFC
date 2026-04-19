# Growth ODE Friction-Coefficient Correction and Validation-Layer Gap

**Date:** 2026-04-19
**Authors:** Morten Magnusson (Symbiose Research, Sandnes, Norway)
**Scope:** Internal technical note — correction and audit summary
**License:** CC-BY-4.0

---

## Summary

During a retrospective audit of the Energy-Flow Cosmology (EFC) perturbation
codebase, two independent findings were identified:

1. **Implementation bug.** The friction coefficient in the f-form linear
   growth ODE was written as `(1/2 − 3/2 Ω̃_m)` in three files. The correct
   coefficient is `(2 − 3/2 Ω̃_m)`. The two expressions differ by exactly
   `1.5·f`, and in the matter era (`Ω̃_m ≈ 1`) the buggy version damps
   growth ≈30× too weakly.

2. **Validation-layer tautology.** The canonical reproducer
   `reproduce_efc.py` reported 31 of 31 tests passing both before and
   after the fix, despite the underlying χ² values changing by up to two
   orders of magnitude. The existing tests asserted only *qualitative*
   properties (sign, ordering, finiteness) and could not distinguish
   "correct physics" from "internally consistent but wrong physics".

**Core results are unaffected.** All inference pipelines — the autonomous
MCMC daemon (`efc-research-daemon`, emcee), the GPU NUTS sampler
(`gpu_nuts_daemon.py`, JAX), the GRAV pipeline (`efc_grav_daemon.py`),
and the Multi-epoch Growth Rate paper — use independent second-order
`D(a)` solvers with mathematically correct friction terms. The bug was
isolated to demonstration code and one reproducer script.

---

## 1. The bug

### 1.1 Derivation of the correct coefficient

The standard linear-growth ODE in cosmic-time variables is

    D̈ + 2 H Ḋ − (3/2) Ω_m H₀² a⁻³ D = 0.

Transforming to `ln a` variables and defining `f = d ln D / d ln a` gives

    f' + f² + [2 + d ln H / d ln a] f = (3/2) Ω̃_m μ(a),

where `Ω̃_m(a) = Ω_m a⁻³ / E²(a)` and, for ΛCDM-like backgrounds,

    d ln H / d ln a = −(3/2) Ω̃_m.

Thus the friction term is `[2 + d ln H / d ln a] = (2 − 3/2 Ω̃_m)`, giving

    f' = −f² − (2 − 3/2 Ω̃_m) f + (3/2) μ(a) Ω̃_m.                (*)

### 1.2 What the code contained

Three files used `(1/2 − 3/2 Ω̃_m)` in place of `(2 − 3/2 Ω̃_m)`:

| File | Line | Role |
|------|------|------|
| `src/efc/perturbation/growth.py` | 72 | Canonical package solver, called by `reproduce_efc.py` |
| `docs/papers/efc/efc_white_paper_part_1_to_4/White_paper_part_2_efc_field_equations_observables/src/field_equations.py` | 82 | Backing code for White Paper Part 2 demo |
| `simple/run.py` | 106 | Standalone didactic reproducer |

Introduction commit: `1d2984b3` (2026-02-13), tagged as
`growth-bug-pre-fix-20260419` for reference. The bug persisted for
~2 months.

### 1.3 White Paper Part 2 — published equation

The printed version of *White Paper Part 2 — EFC Field Equations and
Observables* (figshare DOI `10.6084/m9.figshare.31970898`) contains
the incorrect coefficient in its Equation (6). The equation itself
is mathematically wrong in the typeset PDF. The code file
`field_equations.py` reproduced the printed equation faithfully —
it is not a transcription error in the code, it is the printed
equation that is incorrect.

**An erratum is warranted.** No numerical result cited in the paper
is invalidated (see §3), but a reader implementing Equation (6) as
printed would obtain incorrect growth histories. Erratum drafting
is an author-side action separate from this code fix.

---

## 2. Blast-radius audit

A full search of all Python files in both the `AGI-Test` infrastructure
repository and the `energyflow-cosmology-cosmos` paper repository
identified every call site of growth solvers. The results:

### 2.1 Unaffected (use independent, correct D-form solvers)

| Component | Solver | Friction |
|-----------|--------|----------|
| `efc_inference/engine/growth.py` (MCMC emcee pipeline) | scipy `solve_ivp`, D-form | `3/a + E'/E` ✓ |
| `runs/jax_efc_nuts.py` — 10+ variants (baseline, n3, aeff, n4, n7, grav, variant_g, variant_h) | JAX custom RK4, D-form | `3/a + dE/da/E` ✓ |
| `efc_grav/integration/efc_growth_with_graph_gate.py` | scipy `solve_ivp`, D-form with G_eff | `3/a + E'/E` ✓ |
| `Multi_epoch_Growth_Rate_Test_of_EFC/src/efc_multi_epoch_v2.py` | scipy `solve_ivp` DOP853, D-form | `(3/(2a))(1+Ω_DE)` ✓ |
| `Perturbation-Level_σ₈_Suppression_via_μ/src/sigma8_suppression.py` | Analytical, no ODE | n/a ✓ |
| `Sealed_Blind_Predictions_for_Growth_Rate_Observables_EFC_vs_LCDM/src/...` | scipy `solve_ivp`, D-form | `(3+α)/a + E'/E` ✓ |
| `efc_integration_test.py` (root) | scipy `solve_ivp`, D-form | `3/a + dE_da/E` ✓ |
| `bullet_cluster_efc/src/asig_2d_piemd.py` | 2D lensing only | no growth ODE ✓ |

Cross-validation between the independent D-form solver in
`efc_multi_epoch_v2.py` and the fixed f-form solver in
`src/efc/perturbation/growth.py` yields `np.allclose(rtol=1e-3)`
agreement across a redshift grid (max relative difference 0.046 %,
attributable entirely to a radiation term `Ω_r ≈ 9.15 × 10⁻⁵`
present only in the f-form implementation).

### 2.2 Affected (patched by this change)

| Component | Impact |
|-----------|--------|
| `src/efc/perturbation/growth.py` | Used only by `reproduce_efc.py` |
| `docs/papers/.../field_equations.py` | Used by `examples/compute_observables.py` demo |
| `simple/run.py` | Standalone demo, no downstream consumers |

### 2.3 Frozen parameters (unaffected)

The parameters archived as Ledger v3.11 canonical values —
`B_growth = 0.078`, `μ_0,growth = 0.922`, `α_L2 = 0.187`,
`wp1a_gap_closed = 75 %` — originate from analytical calibration
identities and from fits using the independent D-form solvers.
None are derivatives of `src/efc/perturbation/growth.py`.

---

## 3. The tautology — the more important finding

`reproduce_efc.py` is the canonical "single-command deterministic
reproduction" script for the EFC perturbation sector. Its existing
assertion pattern is illustrated by the growth-solver section:

```python
R.check("efc_growth_suppressed", lnD_efc < lnD_lcdm, ...)
R.check("growth_chi2_finite", np.isfinite(chi2_lcdm) and np.isfinite(chi2_efc), ...)
R.check("efc_chi2_improved", delta < 0, ...)
```

These assertions test *sign*, *ordering*, and *finiteness*. They do
not compare against any absolute reference value.

Running the buggy and fixed solvers through this harness yields:

| Metric | Pre-fix (buggy) | Post-fix (correct) | Δ |
|--------|-----------------|--------------------|-----|
| χ²_LCDM | 333.72 | 5.48 | −98.4 % |
| χ²_EFC | 303.96 | 3.23 | −98.9 % |
| Δχ² | −29.76 | −2.26 | −92.4 % |
| ln D(LCDM, a=1) | 6.4339 | 3.6717 | −42.9 % |
| ln D(EFC, a=1) | 6.3859 | 3.6230 | −43.3 % |
| Content SHA-256 | `1c28d5de…` | `51b8ae16…` | changed |
| Check count | 31 / 31 PASS | 31 / 31 PASS | **unchanged** |

A χ²_LCDM of 333.72 on seven data points corresponds to a ≈47σ
ΛCDM rejection — physically absurd. Yet the `growth_chi2_finite`
check passed because the number was finite. The `efc_chi2_improved`
check passed because `−29.76 < 0`. The `efc_growth_suppressed`
check passed because both `ln D` values were shifted by the same
factor and their ordering was preserved.

This is a textbook case of a reproducer that can verify **internal
consistency** but cannot verify **coupling to physics**. Reference
values in the ledger were generated with the same buggy code path,
so agreement between script output and reference is automatic —
regardless of whether the physics is right.

In RCMP terms: the L3 (implementation) layer was validated only
against itself, with no L0 (external reference) or L1 (independent
method) cross-check. This is a structural RCMP violation.

---

## 4. Mitigation

### 4.1 Solver fix

Line-level correction of the friction coefficient in all three
affected files, plus a new `D_ratio = D(a)/D(a=1)` field in the
`solve_growth` return dictionary to eliminate a documented footgun
where callers could mis-interpret raw `ln_D` (which stores
`ln D(a)/D(a_init)`) as `ln D(a)`.

### 4.2 Regression tests

Added `tests/test_growth_friction.py` with three tests:

- `test_friction_matches_correct_formula`: computes both candidate
  RHS values analytically and asserts the implementation matches
  the correct one, at a redshift where the bug signature is large.
- `test_lcdm_growth_matches_linder_gamma`: asserts
  `f(z=0) ≈ Ω_m^0.55` per Linder (2005). This is the
  **tautology-breaking test** — Linder's γ-parameterisation is
  an external reference independent of our code path.
- `test_solve_growth_returns_normalised_D_ratio`: invariant check
  that `D_ratio(a=1) = 1` and is monotonically increasing.

### 4.3 Reproducer hardening

Added five ranged bounds to `test_growth_relative` in
`reproduce_efc.py`:

| Bound | Catches |
|-------|---------|
| `0 < chi2_lcdm < 50` | χ² drift by > factor 2 |
| `2.5 < lnD_lcdm < 5.0` | Growth amplitude drift |
| `|Δχ²| < 10` | Unrealistic EFC-vs-ΛCDM tension |
| `|lnD_lcdm − 3.67| / 3.67 < 0.10` | Reference-anchored drift |
| `0.9 < D_efc/D_lcdm < 1.1` | Runaway / normalisation errors |

Dry-run on pre-fix values: bounds 1, 2, and 3 all fail
immediately. The bug would have been caught.

### 4.4 Design choice on tolerance

Ranged bounds were chosen over strict absolute-equality checks.
Strict bounds (e.g., `|chi2 − 5.48| < 0.1`) would catch the same
bug but would also produce false positives under legitimate numeric
drift (NumPy 1.x vs 2.x, scipy solver tolerance, radiation-term
treatment, integrator step size). Ranged bounds with ~10 % rtol
on reference values catch the class of error this audit found
without being brittle to normal environment variation.

---

## 5. What this episode teaches

The bug itself was a straightforward typographical error — a `1/2`
where a `2` should have been. Two months of production use and
31 passing tests did not expose it.

The reason they did not expose it is the more useful lesson:
reproducers that validate only intra-code consistency are not
RCMP-compliant. Every reproducer should include at least one
check anchored to an external reference (literature approximation,
independent implementation, analytical limit, survey central value).

Going forward, this note is the precedent: new validation-layer
assertions must include at least one externally-anchored bound.

---

## 6. Commit trail

```
1d2984b3   2026-02-13   Bug introduced (tagged: growth-bug-pre-fix-20260419)
540def6d   2026-04-19   Failing tests committed (xfail markers)
2737fb81   2026-04-19   Solver fix: src/efc/perturbation/growth.py:72
6a143bb7   2026-04-19   Propagation fix: field_equations.py, simple/run.py
685c1c75   2026-04-19   Reproducer hardening: 5 absolute-value bounds
```

---

## References

- Linder, E. V. (2005), *Exploring the expansion history of the
  universe*, Phys. Rev. D 72, 043529.
- Magnusson, M. (2026), *White Paper Part 2 — EFC Field Equations
  and Observables*, figshare DOI `10.6084/m9.figshare.31970898`.
  (Equation 6 — erratum pending.)
- Magnusson, M. (2026), *Multi-epoch Growth Rate Test of EFC*,
  figshare DOI `10.6084/m9.figshare.31955871`. (Independent solver,
  unaffected.)
