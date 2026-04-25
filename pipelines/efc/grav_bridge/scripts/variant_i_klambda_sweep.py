#!/usr/bin/env python3
"""
EFCVariantI k_Λ Sweep — Morten's Vei 1 (Grid, not MCMC)

Q: "Finnes det en projeksjon (k_Λ) hvor GRAV (C=2.32) og fσ8-data er kompatible?"

Procedure (no free parameters, pure grid):
    For each k_Λ ∈ grid:
        Fix C = 2.32, Ω_m = 0.3, σ_8 = 0.81, k_eff = 0.1 h/Mpc
        Compute log L (LCDM at C=1) and log L (GRAV at C=2.32) under same k_Λ
        Δχ² ≡ 2·(log L_LCDM − log L_GRAV)

Interpretation (Morten's lock):
    A) Δχ² always high                  → real tension between GRAV and cosmo
    B) Minimum at specific k_Λ          → scale-coupling issue, not theory

Grid (Morten): [0.005, 0.01, 0.02, 0.05, 0.1]
Extended for shape visibility: [0.003, 0.005, 0.008, 0.01, 0.015, 0.02, 0.03, 0.05, 0.08, 0.1, 0.15, 0.2]

Output:
    outputs/grav_bridge/klambda_sweep_<timestamp>.json
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from efc_grav_bridge import EFCVariantI  # noqa: E402
from efc_grav_bridge import EFCGrowth  # noqa: E402
from efc_grav_bridge import GrowthModule  # noqa: E402


# ─── Fixed physics (Morten's lock) ──────────────────────────────
OMEGA_M_FIX = 0.30
SIGMA8_FIX = 0.81
H0_FIX = 70.0
K_EFF = 0.1
C_GRAV = 2.32

DATA_PATH = REPO_ROOT / "data" / "fs8_extended.csv"
OUT_DIR = REPO_ROOT / "outputs"

# ─── k_Λ grid (Morten's 5 + extended interpolation) ─────────────
K_LAMBDA_GRID = [
    0.003, 0.005, 0.008, 0.01, 0.015, 0.02,
    0.03, 0.05, 0.08, 0.1, 0.15, 0.2,
]


def build_module(k_lambda: float) -> GrowthModule:
    """Instantiate EFCVariantI with given k_Λ, load data."""
    model = EFCVariantI(k_lambda=k_lambda, k_eff=K_EFF)
    engine = EFCGrowth(cosmology=model)
    module = GrowthModule(engine=engine)
    module.load_data(data_path=str(DATA_PATH))
    return module


def eval_point(module: GrowthModule, C: float) -> float:
    """Evaluate log L at fixed (Ω_m, σ8, H0) with given C."""
    params = {
        "Omega_m": OMEGA_M_FIX,
        "H0": H0_FIX,
        "sigma8": SIGMA8_FIX,
        "alpha_cosmo": 0.0,
        "C": float(C),
    }
    return float(module.log_likelihood(params))


def g_eff_at_a1(k_lambda: float, C: float = C_GRAV) -> float:
    """Diagnostic: G_eff(a=1, k_eff, k_Λ) / G."""
    screen = 1.0 / (1.0 + (K_EFF / k_lambda) ** 2)
    gate_a1 = 1.0 / (1.0 + np.exp(-(1.0 - 0.5) / 0.1))  # gate at a=1
    return 1.0 + (C ** 2 - 1.0) * gate_a1 * screen


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")

    print("=" * 80)
    print(" EFCVariantI k_Λ Sweep (Vei 1: grid, no MCMC)")
    print("=" * 80)
    print(f"\nFixed: Ω_m={OMEGA_M_FIX}, σ_8={SIGMA8_FIX}, H0={H0_FIX}, k_eff={K_EFF} h/Mpc")
    print(f"C_GRAV = {C_GRAV} (KT2 prior, frozen)")
    print(f"Grid: {len(K_LAMBDA_GRID)} k_Λ values from {K_LAMBDA_GRID[0]} to {K_LAMBDA_GRID[-1]}\n")

    print(f"{'k_Λ':>8} {'screen(k_eff)':>14} {'G_eff(a=1)/G':>14} "
          f"{'logL(C=1)':>12} {'logL(C=2.32)':>14} {'Δχ²':>10}")
    print("-" * 80)

    results = []
    for k_lambda in K_LAMBDA_GRID:
        module = build_module(k_lambda)
        ll_lcdm = eval_point(module, C=1.0)
        ll_grav = eval_point(module, C=C_GRAV)
        # Δχ² = 2 * (logL_best - logL_test). For Gaussian likelihood this is
        # a relative fit-quality measure: positive → GRAV worse than LCDM.
        delta_chi2 = 2.0 * (ll_lcdm - ll_grav)
        screen = 1.0 / (1.0 + (K_EFF / k_lambda) ** 2)
        geff = g_eff_at_a1(k_lambda, C=C_GRAV)

        results.append({
            "k_lambda": k_lambda,
            "screen_at_k_eff": round(screen, 6),
            "g_eff_at_a1": round(geff, 4),
            "log_likelihood_C_1": round(ll_lcdm, 4),
            "log_likelihood_C_2p32": round(ll_grav, 4),
            "delta_chi2": round(delta_chi2, 4),
        })

        print(f"{k_lambda:>8.4f} {screen:>14.6f} {geff:>14.4f} "
              f"{ll_lcdm:>12.4f} {ll_grav:>14.4f} {delta_chi2:>10.4f}")

    # ── Find minimum ─────────────────────────────────────────
    delta_chi2_arr = np.array([r["delta_chi2"] for r in results])
    k_lambda_arr = np.array([r["k_lambda"] for r in results])
    i_min = int(np.argmin(delta_chi2_arr))
    k_min = k_lambda_arr[i_min]
    chi2_min = delta_chi2_arr[i_min]

    # Is it a genuine interior minimum, or monotonic?
    is_interior = 0 < i_min < len(results) - 1
    if is_interior:
        left = delta_chi2_arr[i_min - 1]
        right = delta_chi2_arr[i_min + 1]
        # Interior if both neighbors are larger (with some tolerance)
        is_interior = left > chi2_min + 0.5 and right > chi2_min + 0.5

    # ── Verdict ──────────────────────────────────────────────
    max_chi2 = float(np.max(delta_chi2_arr))
    min_chi2 = float(np.min(delta_chi2_arr))
    print("\n" + "=" * 80)
    print(f" Minimum Δχ² = {min_chi2:.3f} at k_Λ = {k_min}")
    print(f" Maximum Δχ² = {max_chi2:.3f}")
    print(f" Range       = {max_chi2 - min_chi2:.3f}")

    if is_interior and chi2_min < 4.0:
        verdict = f"INTERIOR_MIN_COMPATIBLE  — minimum at k_Λ={k_min}, Δχ²={chi2_min:.2f} (< 2σ)"
    elif is_interior and chi2_min < 9.0:
        verdict = f"INTERIOR_MIN_TENSION     — minimum at k_Λ={k_min}, Δχ²={chi2_min:.2f} (moderate tension)"
    elif is_interior:
        verdict = f"INTERIOR_MIN_REJECTED    — minimum at k_Λ={k_min}, Δχ²={chi2_min:.2f} (still >3σ)"
    elif i_min == 0:
        verdict = "MONOTONIC_LOW_K_BEST     — Δχ² decreases as k_Λ → 0 (null-test limit, untestable)"
    else:
        verdict = "MONOTONIC_HIGH_K_BEST    — Δχ² decreases as k_Λ → ∞ (unphysical)"

    print(f"\n >>> VERDICT: {verdict} <<<")
    print("=" * 80)

    # ── Save ────────────────────────────────────────────────
    summary = {
        "config": {
            "model": "EFCVariantI",
            "procedure": "k_lambda_sweep_fixed_params",
            "C_GRAV": C_GRAV,
            "Omega_m_fixed": OMEGA_M_FIX,
            "sigma8_fixed": SIGMA8_FIX,
            "H0_fixed": H0_FIX,
            "k_eff_fixed": K_EFF,
            "gate": {"a_t": 0.5, "delta_a": 0.1},
        },
        "data": {
            "path": str(DATA_PATH.relative_to(REPO_ROOT)),
            "covariance": "BOSS_DR12_3x3_plus_diagonal",
        },
        "grid": K_LAMBDA_GRID,
        "results": results,
        "minimum": {
            "k_lambda": float(k_min),
            "delta_chi2": float(chi2_min),
            "interior": bool(is_interior),
        },
        "max_delta_chi2": max_chi2,
        "verdict": verdict,
    }

    out_path = OUT_DIR / f"klambda_sweep_{ts}.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
