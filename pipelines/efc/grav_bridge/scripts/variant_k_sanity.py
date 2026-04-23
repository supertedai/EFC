#!/usr/bin/env python3
"""
EFCVariantK Sanity — Non-local memory coupling.

Tests:
  A) β = 0           → identity with FlatLCDM within ~1e-10
  B) Memory kernel   → verify G(a) analytic values at key points
  C) β = +1          → late-time suppression, but milder/smoother than VariantJ
  D) β-profile       → dump fs8 predictions at β ∈ {-2, -1, -0.5, 0, 0.5, 1, 2}
  E) Compare to J    → show that at a=0.5, memory response is ~1/7 of local

Usage:
    python3 scripts/grav_bridge/variant_k_sanity.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from efc_grav_bridge import (  # noqa: E402
    FlatLCDM, EFCVariantJ, EFCVariantK,
)
from efc_grav_bridge import EFCGrowth  # noqa: E402


Z_TEST = np.array([0.02, 0.15, 0.38, 0.51, 0.61, 0.77, 0.85, 1.0])

PARAMS_BASE = {
    "Omega_m": 0.3, "H0": 70.0, "sigma8": 0.81, "alpha_cosmo": 0.0,
}


def approx_gamma(z_arr, fs8_arr, Om=0.3):
    i0 = int(np.argmin(z_arr))
    f0 = fs8_arr[i0] / PARAMS_BASE["sigma8"]
    if Om <= 0 or f0 <= 0:
        return float("nan")
    return float(np.log(f0) / np.log(Om))


def main() -> int:
    print("=" * 72)
    print(" EFCVariantK Sanity — Non-local memory coupling")
    print("=" * 72)

    model_k = EFCVariantK()
    model_j = EFCVariantJ()

    growth_lcdm = EFCGrowth(cosmology=FlatLCDM())
    growth_k = EFCGrowth(cosmology=model_k)
    growth_j = EFCGrowth(cosmology=model_j)

    # ─── TEST A: β=0 identity ───────────────────────────────
    print("\n[TEST A]  β = 0.0  →  must match FlatLCDM")
    params_b0 = {**PARAMS_BASE, "beta": 0.0}
    fs8_lcdm = growth_lcdm.compute(PARAMS_BASE, Z_TEST)
    fs8_b0 = growth_k.compute(params_b0, Z_TEST)
    max_diff = float(np.max(np.abs(fs8_lcdm - fs8_b0)))
    print(f"  max |Δ fσ8| = {max_diff:.3e}")
    test_a_pass = max_diff < 1e-10
    print(f"  result: {'PASS' if test_a_pass else 'FAIL'}")

    # ─── TEST B: Memory kernel values ───────────────────────
    print("\n[TEST B]  Memory kernel G(a) analytic verification")
    a_test = np.array([0.01, 0.1, 0.3, 0.5, 0.7, 1.0])
    G_vals = model_k._G_integral(a_test)
    gate_vals = np.array([
        1.0 / (1.0 + np.exp(-(a - 0.5) / 0.1)) for a in a_test
    ])
    print(f"  {'a':>6} {'gate(a)':>10} {'G(a)':>10} {'gate/G':>10}")
    for i, a in enumerate(a_test):
        ratio = gate_vals[i] / G_vals[i] if G_vals[i] > 1e-10 else float("inf")
        print(f"  {a:>6.2f} {gate_vals[i]:>10.5f} {G_vals[i]:>10.5f} {ratio:>10.3f}")
    # Basic sanity: monotone, G(0) ~ 0, G(1) ~ 0.5
    test_b_pass = (
        G_vals[0] < 0.001 and        # G(0.01) ≈ 0
        0.45 < G_vals[-1] < 0.55 and # G(1) ≈ 0.5
        np.all(np.diff(G_vals) > 0)  # monotone increasing
    )
    print(f"  result: {'PASS' if test_b_pass else 'FAIL'}")

    # ─── TEST C: β=+1 suppression (milder than J) ───────────
    print("\n[TEST C]  β = +1.0  →  memory-suppressed growth (milder than VariantJ)")
    params_bp1 = {**PARAMS_BASE, "beta": +1.0}
    fs8_k_bp1 = growth_k.compute(params_bp1, Z_TEST)
    fs8_j_bp1 = growth_j.compute(params_bp1, Z_TEST)
    ratio_k = fs8_k_bp1 / fs8_lcdm
    ratio_j = fs8_j_bp1 / fs8_lcdm
    z_low_mask = Z_TEST < 0.3
    k_low_suppressed = bool(np.all(ratio_k[z_low_mask] < 1.0))
    k_milder_than_j = bool(np.mean(np.abs(1 - ratio_k)) < np.mean(np.abs(1 - ratio_j)))
    print(f"  VariantK ratio min / mean / max = {ratio_k.min():.4f} / {ratio_k.mean():.4f} / {ratio_k.max():.4f}")
    print(f"  VariantJ ratio min / mean / max = {ratio_j.min():.4f} / {ratio_j.mean():.4f} / {ratio_j.max():.4f}")
    print(f"  K suppressed at z < 0.3: {k_low_suppressed}")
    print(f"  K milder response than J: {k_milder_than_j} (memory is smoother/delayed)")
    gamma_lcdm = approx_gamma(Z_TEST, fs8_lcdm)
    gamma_k = approx_gamma(Z_TEST, fs8_k_bp1)
    gamma_j = approx_gamma(Z_TEST, fs8_j_bp1)
    print(f"  γ: LCDM={gamma_lcdm:.4f}  K={gamma_k:.4f}  J={gamma_j:.4f}")
    test_c_pass = k_low_suppressed and k_milder_than_j and (gamma_k > gamma_lcdm)
    print(f"  result: {'PASS' if test_c_pass else 'FAIL'}")

    # ─── TEST D: β-profile ──────────────────────────────────
    print("\n[TEST D]  β-profile for VariantK (fs8 at key z)")
    print(f"  {'β':>6} | {'z=0.02':>8} {'z=0.38':>8} {'z=0.61':>8} {'z=1.0':>8} | {'γ_proxy':>8}")
    for beta_val in [-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0]:
        params = {**PARAMS_BASE, "beta": beta_val}
        fs8 = growth_k.compute(params, Z_TEST)
        gamma = approx_gamma(Z_TEST, fs8)
        print(f"  {beta_val:>+6.2f} | {fs8[0]:>8.4f} {fs8[2]:>8.4f} {fs8[4]:>8.4f} {fs8[7]:>8.4f} | {gamma:>8.4f}")

    # ─── TEST E: Side-by-side at a=0.5 ──────────────────────
    print("\n[TEST E]  Local vs memory response comparison at a=0.5 (z=1)")
    a_half = np.array([0.5])
    params_beta_1 = {**PARAMS_BASE, "beta": 1.0}
    fric_j = model_j.friction_extra(a_half, params_beta_1)[0]
    fric_k = model_k.friction_extra(a_half, params_beta_1)[0]
    print(f"  friction_extra(a=0.5) at β=1:")
    print(f"    VariantJ (local):  {fric_j:.5f}  (β·gate(0.5)/0.5)")
    print(f"    VariantK (memory): {fric_k:.5f}  (β·G(0.5)/0.5)")
    print(f"    ratio J/K = {fric_j / fric_k:.3f} — memory lags behind local")

    # ─── Summary ────────────────────────────────────────────
    print("\n" + "=" * 72)
    print(f" SUMMARY  Test A (β=0 identity):        {'PASS' if test_a_pass else 'FAIL'}")
    print(f"          Test B (memory kernel):       {'PASS' if test_b_pass else 'FAIL'}")
    print(f"          Test C (β=+1 memory-milder):  {'PASS' if test_c_pass else 'FAIL'}")
    print("=" * 72)

    return 0 if (test_a_pass and test_b_pass and test_c_pass) else 1


if __name__ == "__main__":
    sys.exit(main())
