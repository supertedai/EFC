# EFC Analysis Methods

## Method 1: Perturbation-level growth analysis

1. Define gate function g(a) with transition redshift z_t and steepness n
2. Calibrate B = (1 - mu_0) / g(1; n) to fix present-day coupling
3. Solve growth ODE from z=50 to z=0 via RK4 integration
4. Compute fsigma_8(z) = f(z) * sigma_8,0 * D(z)/D(0)
5. Evaluate chi^2 against 7-point fsigma_8 compilation
6. Compare LCDM (B=0) vs EFC (B=0.187) via Dchi^2

**Code path:**
```
gate.py:calibrate_B() -> mu.py:mu_of_a() -> growth.py:solve_growth()
-> growth.py:compute_fsigma8() -> robustness.py:chi2_fsigma8()
```

**Reproduce:** `python reproduce_efc.py` (tests 4-5)

## Method 2: Leave-One-Out robustness

1. For each of 7 data points, drop one and refit alpha
2. Check: |alpha|/sigma >= 1.7 AND DAIC <= 0
3. Report pass rate (must be 7/7)

**Code path:** `robustness.py:leave_one_out_indices()`, `loo_pass_criterion()`

**Reproduce:** `python reproduce_efc.py` (test 5)

## Method 3: Background sign verification

1. Compute DE^2(z) = A [g(z) - g(0)] for z in [0, z_max]
2. Verify DE^2 <= 0 everywhere (Lemma 1)
3. Confirm E^2(z=0) = 1 (closure)

**Code path:** `background.py:verify_sign_lemma()`, `delta_E2()`

**Reproduce:** `python reproduce_efc.py` (tests 1, 6)

## Method 4: Unified multi-probe analysis

1. Combine BAO (6 pts) + SN Ia (16 pts) + RSD (11 pts) = 33 data points
2. Fit LCDM and EFC simultaneously
3. Report: chi^2_LCDM = 49.35, chi^2_EFC = 50.07, Dchi^2 = +1.72

**Code path:** Documented in `docs/papers/efc/Energy-Flow-Cosmology-Unified-Analysis-of-BAO/`
**Data:** `docs/validation-ledger/data/inference.json`

**Note:** This analysis uses external tools (cobaya) and is not included
in the minimal reproduce_efc.py script.  The result is archived in the
validation ledger.

## Method 5: SPARC rotation curve fitting

1. Load 175 SPARC galaxy rotation curves
2. Fit EFC phenomenological model: v(r) = v_flat * sqrt(1 - exp(-(r/r_turnon)^sharpness))
3. Fit NFW profile for LCDM comparison
4. Compare via AIC/BIC per galaxy
5. Report win rate and residual diagnostics

**Code path:** `src/efc/validation/sparc_io.py`, `src/efc/solver/grid_aqual_killtests.py`
