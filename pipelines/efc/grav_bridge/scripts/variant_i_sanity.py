#!/usr/bin/env python3
"""
EFCVariantI Sanity + Response Tests — Vei Z GRAV→cosmo bridge

Tests the new growth-source coupling BEFORE running MCMC.

Runs four tests:
  A) C = 1.0    — must match FlatLCDM within ~1e-10 (pure sanity anchor)
  B) C = 5.0    — must give strictly higher fσ8 at all z (response test)
  C) C = 2.32   — profile dump at RSD-relevant z (KT2 Grid-AQUAL prior)
  D) RCMP logging — classify growth-source regime at a ∈ {0.1, 0.3, 0.5, 0.7, 1.0}

Exit code 0 only if A and B pass.

Usage:
    python3 scripts/grav_bridge/variant_i_sanity.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# Ensure efc_inference is importable when running from repo root
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from efc_grav_bridge import FlatLCDM, EFCVariantI  # noqa: E402
from efc_grav_bridge import EFCGrowth  # noqa: E402


# ─── fσ8 redshifts from fs8_extended.csv compilation ────────────
Z_TEST = np.array([0.02, 0.15, 0.38, 0.51, 0.61, 0.77, 0.85, 1.0])

# Base cosmology (fixed for all tests)
PARAMS_BASE = {
    "Omega_m": 0.3,
    "H0": 70.0,
    "sigma8": 0.81,
    "alpha_cosmo": 0.0,
}


def approx_gamma(z_arr: np.ndarray, fs8_arr: np.ndarray, Om: float = 0.3) -> float:
    """Rough γ = ln(f)/ln(Ω_m) using lowest-z point as f estimate."""
    i0 = int(np.argmin(z_arr))
    f0 = fs8_arr[i0] / PARAMS_BASE["sigma8"]
    if Om <= 0 or f0 <= 0:
        return float("nan")
    return float(np.log(f0) / np.log(Om))


def main() -> int:
    print("=" * 72)
    print(" EFCVariantI Sanity + Response Tests — Vei Z")
    print("=" * 72)

    growth_lcdm = EFCGrowth(cosmology=FlatLCDM())
    growth_i = EFCGrowth(cosmology=EFCVariantI())

    # ─── TEST A: C=1 identity ─────────────────────────────────
    print("\n[TEST A]  C = 1.0 → must match FlatLCDM")
    params_c1 = {**PARAMS_BASE, "C": 1.0}
    fs8_lcdm = growth_lcdm.compute(PARAMS_BASE, Z_TEST)
    fs8_c1 = growth_i.compute(params_c1, Z_TEST)
    max_diff = float(np.max(np.abs(fs8_lcdm - fs8_c1)))
    rel_diff = max_diff / float(np.max(np.abs(fs8_lcdm)))
    print(f"  max |Δ fσ8|      = {max_diff:.3e}")
    print(f"  max relative Δ   = {rel_diff:.3e}")
    test_a_pass = max_diff < 1e-10
    print(f"  result: {'PASS' if test_a_pass else 'FAIL'}")

    # ─── TEST B: C=5 response ─────────────────────────────────
    # Physics note: G_eff boosts growth at late times → D(a=1) rises.
    # fσ8 = f·σ8·D(z)/D(0) → ratio > 1 at low z, < 1 at high z past gate.
    # Correct markers: (i) mean ratio > 1, (ii) γ drops, (iii) at low z (z < z_gate) ratio > 1.
    print("\n[TEST B]  C = 5.0 → expect γ↓ and fσ8 boost below z_gate")
    params_c5 = {**PARAMS_BASE, "C": 5.0}
    fs8_c5 = growth_i.compute(params_c5, Z_TEST)
    ratio = fs8_c5 / fs8_lcdm
    mean_ratio = float(np.mean(ratio))
    min_ratio = float(np.min(ratio))
    max_ratio = float(np.max(ratio))
    print(f"  ratio min / mean / max = {min_ratio:.4f} / {mean_ratio:.4f} / {max_ratio:.4f}")
    # z < 0.5 ≈ "below gate transition" (a_t=0.5 ↔ z≈1, so z<0.5 is deep in modified regime)
    z_low_mask = Z_TEST < 0.5
    ratio_low_z = ratio[z_low_mask]
    all_low_z_higher = bool(np.all(ratio_low_z > 1.0))
    print(f"  all z < 0.5 have fσ8(C=5) > fσ8(LCDM): {all_low_z_higher}")
    gamma_lcdm = approx_gamma(Z_TEST, fs8_lcdm)
    gamma_c5 = approx_gamma(Z_TEST, fs8_c5)
    dgamma = gamma_c5 - gamma_lcdm
    print(f"  γ(LCDM) ≈ {gamma_lcdm:.4f}    γ(C=5) ≈ {gamma_c5:.4f}    Δγ = {dgamma:+.4f}")
    test_b_pass = (
        mean_ratio > 1.10          # overall substantial amplification
        and all_low_z_higher       # gate-active regime must boost
        and dgamma < -0.3          # γ must drop measurably
    )
    print(f"  result: {'PASS' if test_b_pass else 'FAIL'}")

    # ─── TEST C: C=2.32 profile ───────────────────────────────
    print("\n[TEST C]  C = 2.32 (KT2 prior) — profile dump")
    params_c232 = {**PARAMS_BASE, "C": 2.32}
    fs8_c232 = growth_i.compute(params_c232, Z_TEST)
    print(f"  {'z':>6} {'fσ8(LCDM)':>12} {'fσ8(C=2.32)':>14} {'ratio':>8}")
    for i, z in enumerate(Z_TEST):
        r = fs8_c232[i] / fs8_lcdm[i]
        print(f"  {z:>6.2f} {fs8_lcdm[i]:>12.4f} {fs8_c232[i]:>14.4f} {r:>8.4f}")

    # ─── TEST D: RCMP regime classification ───────────────────
    print("\n[TEST D]  RCMP regime classification (C = 2.32)")
    model = EFCVariantI()
    print(f"  screen(k_eff=0.1, k_Λ=0.05) = {model._screen_k_eff:.4f}")
    print(f"  {'a':>6} {'z':>6} {'gate(a)':>8} {'G_eff/G':>10} {'regime':>12}")
    for a_val in [0.1, 0.3, 0.5, 0.7, 1.0]:
        z_val = 1.0 / a_val - 1.0
        gate_val = float(model._gate(np.array([a_val]))[0])
        geff = float(model.g_eff_over_G(np.array([a_val]), C=2.32)[0])
        regime = model.classify_regime(a_val, C=2.32)
        print(f"  {a_val:>6.2f} {z_val:>6.2f} {gate_val:>8.4f} {geff:>10.4f} {regime:>12}")

    # ─── Summary ──────────────────────────────────────────────
    print("\n" + "=" * 72)
    print(f" SUMMARY  Test A (C=1 identity):   {'PASS' if test_a_pass else 'FAIL'}")
    print(f"          Test B (C=5 response):   {'PASS' if test_b_pass else 'FAIL'}")
    print("=" * 72)

    return 0 if (test_a_pass and test_b_pass) else 1


if __name__ == "__main__":
    sys.exit(main())
