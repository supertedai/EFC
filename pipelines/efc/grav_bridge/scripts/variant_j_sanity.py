#!/usr/bin/env python3
"""
EFCVariantJ Sanity + Response Tests — Friction-channel coupling.

Runs four tests:
  A) β = 0   → must match FlatLCDM within ~1e-10 (numerical identity)
  B) β = +1  → late-time growth suppressed → fσ8 ↓ at low z, γ ↑
  C) β = -1  → late-time growth enhanced  → fσ8 ↑ at low z, γ ↓
  D) Profile dump across β ∈ {-1, -0.5, 0, 0.5, 1}

Exit code 0 only if A, B, C all pass.

Usage:
    python3 scripts/grav_bridge/variant_j_sanity.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from efc_grav_bridge import FlatLCDM, EFCVariantJ  # noqa: E402
from efc_grav_bridge import EFCGrowth  # noqa: E402


Z_TEST = np.array([0.02, 0.15, 0.38, 0.51, 0.61, 0.77, 0.85, 1.0])

PARAMS_BASE = {
    "Omega_m": 0.3,
    "H0": 70.0,
    "sigma8": 0.81,
    "alpha_cosmo": 0.0,
}


def approx_gamma(z_arr: np.ndarray, fs8_arr: np.ndarray, Om: float = 0.3) -> float:
    i0 = int(np.argmin(z_arr))
    f0 = fs8_arr[i0] / PARAMS_BASE["sigma8"]
    if Om <= 0 or f0 <= 0:
        return float("nan")
    return float(np.log(f0) / np.log(Om))


def main() -> int:
    print("=" * 72)
    print(" EFCVariantJ Sanity + Response Tests — Friction-channel coupling")
    print("=" * 72)

    growth_lcdm = EFCGrowth(cosmology=FlatLCDM())
    growth_j = EFCGrowth(cosmology=EFCVariantJ())

    # ─── TEST A: β=0 identity ────────────────────────────────
    print("\n[TEST A]  β = 0.0  →  must match FlatLCDM")
    params_b0 = {**PARAMS_BASE, "beta": 0.0}
    fs8_lcdm = growth_lcdm.compute(PARAMS_BASE, Z_TEST)
    fs8_b0 = growth_j.compute(params_b0, Z_TEST)
    max_diff = float(np.max(np.abs(fs8_lcdm - fs8_b0)))
    rel_diff = max_diff / float(np.max(np.abs(fs8_lcdm)))
    print(f"  max |Δ fσ8|    = {max_diff:.3e}")
    print(f"  max relative Δ = {rel_diff:.3e}")
    test_a_pass = max_diff < 1e-10
    print(f"  result: {'PASS' if test_a_pass else 'FAIL'}")

    # ─── TEST B: β=+1 suppression ────────────────────────────
    # Extra drag → late-time growth suppressed → fσ8 at low z lower than LCDM
    # But due to D(a=1) normalization, high-z ratio may flip — check low-z only.
    print("\n[TEST B]  β = +1.0  →  late growth suppressed (fσ8 ↓ at low z, γ ↑)")
    params_bp1 = {**PARAMS_BASE, "beta": +1.0}
    fs8_bp1 = growth_j.compute(params_bp1, Z_TEST)
    ratio = fs8_bp1 / fs8_lcdm
    z_low_mask = Z_TEST < 0.3
    ratio_low_z = ratio[z_low_mask]
    low_z_suppressed = bool(np.all(ratio_low_z < 1.0))
    print(f"  ratio min / mean / max = {ratio.min():.4f} / {ratio.mean():.4f} / {ratio.max():.4f}")
    print(f"  all z < 0.3 have fσ8(β=+1) < fσ8(LCDM): {low_z_suppressed}")
    gamma_lcdm = approx_gamma(Z_TEST, fs8_lcdm)
    gamma_bp1 = approx_gamma(Z_TEST, fs8_bp1)
    print(f"  γ(LCDM) ≈ {gamma_lcdm:.4f}    γ(β=+1) ≈ {gamma_bp1:.4f}    Δγ = {gamma_bp1 - gamma_lcdm:+.4f}")
    test_b_pass = low_z_suppressed and (gamma_bp1 > gamma_lcdm)
    print(f"  result: {'PASS' if test_b_pass else 'FAIL'}")

    # ─── TEST C: β=-1 enhancement ────────────────────────────
    print("\n[TEST C]  β = -1.0  →  late growth enhanced (fσ8 ↑ at low z, γ ↓)")
    params_bm1 = {**PARAMS_BASE, "beta": -1.0}
    fs8_bm1 = growth_j.compute(params_bm1, Z_TEST)
    ratio = fs8_bm1 / fs8_lcdm
    ratio_low_z = ratio[z_low_mask]
    low_z_enhanced = bool(np.all(ratio_low_z > 1.0))
    print(f"  ratio min / mean / max = {ratio.min():.4f} / {ratio.mean():.4f} / {ratio.max():.4f}")
    print(f"  all z < 0.3 have fσ8(β=-1) > fσ8(LCDM): {low_z_enhanced}")
    gamma_bm1 = approx_gamma(Z_TEST, fs8_bm1)
    print(f"  γ(LCDM) ≈ {gamma_lcdm:.4f}    γ(β=-1) ≈ {gamma_bm1:.4f}    Δγ = {gamma_bm1 - gamma_lcdm:+.4f}")
    test_c_pass = low_z_enhanced and (gamma_bm1 < gamma_lcdm)
    print(f"  result: {'PASS' if test_c_pass else 'FAIL'}")

    # ─── TEST D: β profile dump ──────────────────────────────
    print("\n[TEST D]  β profile across {-1, -0.5, 0, 0.5, 1} — fσ8 at key z")
    print(f"  {'β':>6} | {'z=0.02':>8} {'z=0.38':>8} {'z=0.61':>8} {'z=1.0':>8} | {'γ_proxy':>8}")
    for beta_val in [-1.0, -0.5, 0.0, 0.5, 1.0]:
        params = {**PARAMS_BASE, "beta": beta_val}
        fs8 = growth_j.compute(params, Z_TEST)
        gamma = approx_gamma(Z_TEST, fs8)
        print(f"  {beta_val:>+6.2f} | {fs8[0]:>8.4f} {fs8[2]:>8.4f} {fs8[4]:>8.4f} {fs8[7]:>8.4f} | {gamma:>8.4f}")

    # ─── Summary ──────────────────────────────────────────────
    print("\n" + "=" * 72)
    print(f" SUMMARY  Test A (β=0 identity):      {'PASS' if test_a_pass else 'FAIL'}")
    print(f"          Test B (β=+1 suppression):  {'PASS' if test_b_pass else 'FAIL'}")
    print(f"          Test C (β=-1 enhancement):  {'PASS' if test_c_pass else 'FAIL'}")
    print("=" * 72)

    return 0 if (test_a_pass and test_b_pass and test_c_pass) else 1


if __name__ == "__main__":
    sys.exit(main())
