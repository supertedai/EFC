#!/usr/bin/env python3
"""
EFCVariantJ β Sweep — Phase 2 Step 1

Q: "Does the friction-channel coupling admit a data-compatible β ≠ 0?"

Procedure (grid, no MCMC):
    For each β ∈ grid:
        Fix Ω_m = 0.30, σ_8 = 0.81, H0 = 70, gate frozen (a_t=0.5, δ_a=0.1)
        Compute log L (LCDM at β=0) and log L (friction model at β)
        Δχ² ≡ 2·(log L_LCDM − log L_β)

Interpretation:
    A) Δχ² minimum exactly at β=0     → LCDM preferred, friction channel dead
    B) Δχ² minimum at β ≠ 0 (non-trivial) → DATA PREFERS friction coupling
    C) Δχ² flat                       → data cannot constrain β (unlikely given β effect size)

Grid: [-2.0, -1.5, -1.0, -0.75, -0.5, -0.3, -0.2, -0.1, -0.05,
        0.0, +0.05, +0.1, +0.2, +0.3, +0.5, +0.75, +1.0, +1.5, +2.0]

Output:
    outputs/grav_bridge/beta_sweep_<timestamp>.json
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

from efc_grav_bridge import EFCVariantJ  # noqa: E402
from efc_grav_bridge import EFCGrowth  # noqa: E402
from efc_grav_bridge import GrowthModule  # noqa: E402


OMEGA_M_FIX = 0.30
SIGMA8_FIX = 0.81
H0_FIX = 70.0

DATA_PATH = REPO_ROOT / "data" / "fs8_extended.csv"
OUT_DIR = REPO_ROOT / "outputs"

BETA_GRID = [
    -2.0, -1.5, -1.0, -0.75, -0.5, -0.3, -0.2, -0.1, -0.05,
    0.0,
    +0.05, +0.1, +0.2, +0.3, +0.5, +0.75, +1.0, +1.5, +2.0,
]


def build_module() -> GrowthModule:
    model = EFCVariantJ()
    engine = EFCGrowth(cosmology=model)
    module = GrowthModule(engine=engine)
    module.load_data(data_path=str(DATA_PATH))
    return module


def eval_point(module: GrowthModule, beta: float) -> float:
    params = {
        "Omega_m": OMEGA_M_FIX,
        "H0": H0_FIX,
        "sigma8": SIGMA8_FIX,
        "alpha_cosmo": 0.0,
        "beta": float(beta),
    }
    return float(module.log_likelihood(params))


def verdict(beta_min: float, chi2_min: float, chi2_at_0: float,
            is_interior: bool) -> str:
    dchi2_vs_lcdm = chi2_min - chi2_at_0  # negative if β≠0 better than β=0
    # Since chi2_at_0 is the LCDM reference (Δχ²=0 by construction)
    # and chi2_min could be negative (β improves over LCDM)
    if abs(beta_min) < 0.01:
        return "LCDM_PREFERRED           — β = 0 is best fit (friction channel not activated)"
    if dchi2_vs_lcdm < -1.0 and is_interior:
        if dchi2_vs_lcdm < -4.0:
            return f"DATA_PREFERS_BETA={beta_min:+.3f}  — Δχ² improves by {-dchi2_vs_lcdm:.2f} vs LCDM (>2σ)"
        return f"WEAK_PREFERENCE_BETA={beta_min:+.3f} — Δχ² improves by {-dchi2_vs_lcdm:.2f} vs LCDM"
    return f"NO_PREFERENCE_FOR_BETA   — min at β={beta_min:+.3f} not significantly better than LCDM"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")

    print("=" * 80)
    print(" EFCVariantJ β Sweep (Phase 2 Step 1: friction-channel)")
    print("=" * 80)
    print(f"\nFixed: Ω_m={OMEGA_M_FIX}, σ_8={SIGMA8_FIX}, H0={H0_FIX}")
    print(f"Gate: a_t=0.5, δ_a=0.1 (frozen)")
    print(f"Grid: {len(BETA_GRID)} β values from {BETA_GRID[0]} to {BETA_GRID[-1]}\n")

    module = build_module()

    # LCDM anchor (β=0, should be log L_LCDM exactly)
    ll_lcdm = eval_point(module, beta=0.0)
    print(f"LCDM anchor: log L (β=0) = {ll_lcdm:.4f}\n")

    print(f"{'β':>8} {'log L':>12} {'Δχ² vs LCDM':>14}")
    print("-" * 40)

    results = []
    for beta in BETA_GRID:
        ll = eval_point(module, beta=beta)
        delta_chi2 = 2.0 * (ll_lcdm - ll)
        results.append({
            "beta": beta,
            "log_likelihood": round(ll, 4),
            "delta_chi2": round(delta_chi2, 4),
        })
        marker = "  ← β=0" if beta == 0.0 else ""
        print(f"{beta:>+8.3f} {ll:>12.4f} {delta_chi2:>+14.4f}{marker}")

    delta_chi2_arr = np.array([r["delta_chi2"] for r in results])
    beta_arr = np.array([r["beta"] for r in results])
    i_min = int(np.argmin(delta_chi2_arr))
    beta_min = beta_arr[i_min]
    chi2_min = delta_chi2_arr[i_min]
    chi2_at_0 = delta_chi2_arr[np.argmin(np.abs(beta_arr))]

    # Interior minimum check
    is_interior = 0 < i_min < len(results) - 1
    if is_interior:
        left = delta_chi2_arr[i_min - 1]
        right = delta_chi2_arr[i_min + 1]
        is_interior = left > chi2_min - 0.01 and right > chi2_min - 0.01

    max_chi2 = float(np.max(delta_chi2_arr))

    print("\n" + "=" * 80)
    print(f" Minimum Δχ² = {chi2_min:+.3f} at β = {beta_min:+.3f}")
    print(f" Δχ² at β=0  = {chi2_at_0:+.3f} (LCDM reference)")
    print(f" Max Δχ²     = {max_chi2:.3f}")

    v = verdict(beta_min, chi2_min, chi2_at_0, is_interior)
    print(f"\n >>> VERDICT: {v} <<<")
    print("=" * 80)

    summary = {
        "config": {
            "model": "EFCVariantJ",
            "procedure": "beta_sweep_fixed_params",
            "Omega_m_fixed": OMEGA_M_FIX,
            "sigma8_fixed": SIGMA8_FIX,
            "H0_fixed": H0_FIX,
            "gate": {"a_t": 0.5, "delta_a": 0.1},
        },
        "data": {
            "path": str(DATA_PATH.relative_to(REPO_ROOT)),
            "covariance": "BOSS_DR12_3x3_plus_diagonal",
        },
        "lcdm_anchor_log_likelihood": round(ll_lcdm, 4),
        "grid": BETA_GRID,
        "results": results,
        "minimum": {
            "beta": float(beta_min),
            "delta_chi2": float(chi2_min),
            "interior": bool(is_interior),
        },
        "max_delta_chi2": max_chi2,
        "verdict": v,
    }

    out_path = OUT_DIR / f"beta_sweep_{ts}.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
