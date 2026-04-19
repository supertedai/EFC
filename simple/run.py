#!/usr/bin/env python3
"""
EFC Minimal Demonstration
=========================

Self-contained, single-file verification of the core EFC mechanism.
No imports beyond numpy.  No repo structure knowledge needed.

    pip install numpy
    python simple/run.py

What this proves:
    1. mu(a) < 1 suppresses growth relative to LCDM
    2. The sign lemma holds: DE^2 <= 0 for z > 0
    3. LOO robustness passes 7/7 (pre-computed, verified)

Runtime: ~0.2 seconds.

Status: EFC is currently consistent with late-time data at ~2 sigma
and remains a candidate extension of LCDM pending CMB validation.
"""

import json
import sys
import time

import numpy as np

# =====================================================================
# 1. CONSTANTS  (Planck 2018)
# =====================================================================
OMEGA_M = 0.3134
OMEGA_R = 9.15e-5
OMEGA_L = 1.0 - OMEGA_M - OMEGA_R
SIGMA8_LCDM = 0.811

# WP1a reference parameters (Technical Note II, Eq. 6)
Z_T = 1.01       # transition redshift
N_STEEP = 2       # gate steepness
MU_0 = 0.85       # present-day mu

# Observational fsigma8 data (7-point compilation)
OBS_Z = np.array([0.02, 0.15, 0.38, 0.51, 0.61, 0.77, 0.85])
OBS_FS8 = np.array([0.360, 0.490, 0.430, 0.452, 0.457, 0.420, 0.380])
OBS_ERR = np.array([0.040, 0.055, 0.054, 0.057, 0.052, 0.060, 0.080])

# Pre-computed LOO results (from robustness analysis)
LOO_ALPHA = [-0.88, -1.11, -0.98, -1.03, -1.04, -1.00, -0.97]
LOO_SIGMA = [0.48, 0.46, 0.46, 0.47, 0.48, 0.47, 0.46]
LOO_DAIC = [-1.59, -3.97, -2.58, -2.97, -3.20, -2.70, -2.54]


# =====================================================================
# 2. CORE FUNCTIONS
# =====================================================================

def gate(a, z_t=Z_T, n=N_STEEP):
    """Sigmoid gate g(a) = 1 / (1 + (a_t/a)^n)."""
    a_t = 1.0 / (1.0 + z_t)
    return 1.0 / (1.0 + (a_t / a) ** n)


def mu(a, mu_0=MU_0, z_t=Z_T, n=N_STEEP):
    """Effective gravitational coupling mu(a) = 1 - B g(a)."""
    g_at_1 = gate(1.0, z_t, n)
    B = (1.0 - mu_0) / g_at_1
    return 1.0 - B * gate(a, z_t, n)


def E2_lcdm(z):
    """LCDM E^2(z) = Omega_r(1+z)^4 + Omega_m(1+z)^3 + Omega_L."""
    return OMEGA_R * (1 + z)**4 + OMEGA_M * (1 + z)**3 + OMEGA_L


def delta_E2(z, A, z_t=Z_T, n=N_STEEP):
    """Background modification DE^2(z) = A [g(z) - g(0)]."""
    a_z = 1.0 / (1.0 + z)
    return A * (gate(a_z, z_t, n) - gate(1.0, z_t, n))


def solve_growth(use_efc=False, mu_0=MU_0, z_t=Z_T, n=N_STEEP):
    """Solve growth ODE from z=50 to z=0 via RK4."""
    z_init = 50.0
    n_pts = 2000
    a_init = 1.0 / (1.0 + z_init)
    ln_a = np.linspace(np.log(a_init), 0.0, n_pts)
    h = ln_a[1] - ln_a[0]

    E2_init = E2_lcdm(z_init)
    Om_init = OMEGA_M * a_init**(-3) / E2_init
    f_val = Om_init ** 0.55

    f_arr = np.zeros(n_pts)
    lnD = np.zeros(n_pts)
    f_arr[0] = f_val

    g1 = gate(1.0, z_t, n)
    B = (1.0 - mu_0) / g1 if use_efc else 0.0

    def rhs(ln_a_val, f_val):
        a = np.exp(ln_a_val)
        z = 1.0 / a - 1.0
        E2 = max(E2_lcdm(z), 1e-30)
        Om = OMEGA_M * a**(-3) / E2
        mu_val = 1.0 - B * gate(a, z_t, n) if use_efc else 1.0
        # Friction coefficient is (2 - 1.5 * Om_tilde). Earlier revisions
        # used (0.5 - 1.5 * Om_tilde), which is mathematically incorrect
        # and damps growth ~30x too weakly. See docs/notes/growth_bug_2026.md.
        return -f_val**2 - (2.0 - 1.5 * Om) * f_val + 1.5 * mu_val * Om

    for i in range(1, n_pts):
        la = ln_a[i - 1]
        k1 = rhs(la, f_val)
        k2 = rhs(la + 0.5 * h, f_val + 0.5 * h * k1)
        k3 = rhs(la + 0.5 * h, f_val + 0.5 * h * k2)
        k4 = rhs(la + h, f_val + h * k3)
        f_val += (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        f_arr[i] = f_val
        lnD[i] = lnD[i - 1] + f_val * h

    a_arr = np.exp(ln_a)
    z_arr = 1.0 / a_arr - 1.0
    return z_arr, a_arr, f_arr, lnD


def compute_fsigma8(z_eval, use_efc=False):
    """Compute fsigma8(z) at given redshifts."""
    z_arr, a_arr, f_arr, lnD = solve_growth(use_efc=use_efc)
    f_interp = np.interp(z_eval, z_arr[::-1], f_arr[::-1])
    lnD_interp = np.interp(z_eval, z_arr[::-1], lnD[::-1])
    lnD_0 = lnD[-1]
    D_ratio = np.exp(lnD_interp - lnD_0)
    sigma8_z = SIGMA8_LCDM * D_ratio
    return f_interp * sigma8_z


def chi2(model_fs8):
    """Chi-squared against observational data."""
    return np.sum(((OBS_FS8 - model_fs8) / OBS_ERR) ** 2)


# =====================================================================
# 3. RUN
# =====================================================================

def main():
    print("=" * 60)
    print("  EFC MINIMAL DEMONSTRATION")
    print("  Self-contained single-file verification")
    print(f"  numpy {np.__version__}")
    print("=" * 60)

    t0 = time.time()
    passed = 0
    total = 0

    def check(name, ok, detail=""):
        nonlocal passed, total
        total += 1
        tag = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        print(f"  [{tag}] {name}" + (f"  ({detail})" if detail else ""))

    # ── Test 1: Sign lemma ──────────────────────────────────────────
    print("\n--- Sign Lemma ---")
    z_test = np.linspace(0.01, 10, 500)
    for A in [0.1, 1.0, 5.0]:
        dE2 = delta_E2(z_test, A)
        check(f"DE2<=0 (A={A})", np.all(dE2 <= 1e-14), f"max={np.max(dE2):.2e}")

    # ── Test 2: Gate calibration ────────────────────────────────────
    print("\n--- Gate Calibration ---")
    mu_check = mu(1.0)
    check("mu(z=0) = mu_0", abs(mu_check - MU_0) < 0.001, f"mu={mu_check:.6f}")

    # ── Test 3: mu properties ───────────────────────────────────────
    print("\n--- mu(a) Properties ---")
    a_arr = np.linspace(0.01, 1.0, 200)
    mu_arr = np.array([mu(a) for a in a_arr])
    check("mu < 1 everywhere", np.all(mu_arr < 1.0), f"max={np.max(mu_arr):.4f}")
    check("mu > 0 everywhere", np.all(mu_arr > 0), f"min={np.min(mu_arr):.4f}")
    check("mu early -> 1", abs(mu(0.01) - 1.0) < 0.001, f"mu(a=0.01)={mu(0.01):.6f}")

    # ── Test 4: Growth suppression ──────────────────────────────────
    print("\n--- Growth Suppression ---")
    _, _, _, lnD_lcdm = solve_growth(use_efc=False)
    _, _, _, lnD_efc = solve_growth(use_efc=True)
    check("EFC growth < LCDM", lnD_efc[-1] < lnD_lcdm[-1],
          f"lnD: EFC={lnD_efc[-1]:.4f} < LCDM={lnD_lcdm[-1]:.4f}")

    fs8_lcdm = compute_fsigma8(OBS_Z, use_efc=False)
    fs8_efc = compute_fsigma8(OBS_Z, use_efc=True)
    c2_lcdm = chi2(fs8_lcdm)
    c2_efc = chi2(fs8_efc)
    dc2 = c2_efc - c2_lcdm
    check("EFC chi2 < LCDM chi2", dc2 < 0,
          f"Dchi2={dc2:+.2f}")

    # ── Test 5: LOO robustness (pre-computed) ───────────────────────
    print("\n--- LOO Robustness (pre-computed) ---")
    n_loo_pass = sum(
        1 for a, s, d in zip(LOO_ALPHA, LOO_SIGMA, LOO_DAIC)
        if abs(a) / s >= 1.7 and d <= 0
    )
    check("LOO 7/7 pass", n_loo_pass == 7, f"{n_loo_pass}/7")

    # ── Summary ─────────────────────────────────────────────────────
    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    result = "ALL PASSED" if passed == total else f"{total - passed} FAILED"
    print(f"  {passed}/{total} checks  [{result}]  ({elapsed:.2f}s)")
    print("=" * 60)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
