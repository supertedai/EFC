"""
Scan the slip-window f in [0, 1] and reproduce Table 4.

Usage:
    python examples/slip_window_scan.py

Shows that f = 0.15 hits the sweet spot (eta = 1.23, Sigma = 1.05),
that the window [0.12, 0.18] is 25% wide (not fine-tuned),
and that extremes (f = 0 or f = 1) are excluded by data.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.gravitational_slip import (  # noqa: E402
    TABLE_4,
    GravSlip,
    slip_scan,
    in_window,
    SWEET_SPOT_F,
    F_WINDOW_LOWER,
    F_WINDOW_UPPER,
)
from src.k_rho_bridge import KRhoBridge  # noqa: E402


def main() -> None:
    print("=" * 72)
    print("Gravitational slip window scan — Table 4 reproduction")
    print("=" * 72)
    print()
    print(f"Sweet spot:      f = {SWEET_SPOT_F}")
    print(f"Viable window:   f in [{F_WINDOW_LOWER}, {F_WINDOW_UPPER}]")
    print(f"Window width:    Delta f = {F_WINDOW_UPPER - F_WINDOW_LOWER:.2f} "
          f"(~25% relative, paper Section 5)")
    print()

    # Table 4 rows
    print(f"{'f':>6} {'eta':>7} {'Sigma':>7} {'Dchi2':>10}  Status")
    print("-" * 60)
    for row in TABLE_4:
        mark = "<-" if abs(row["f"] - SWEET_SPOT_F) < 1e-6 else "  "
        print(
            f"{row['f']:>6.2f} {row['eta']:>7.2f} {row['Sigma']:>7.2f} "
            f"{row['delta_chi2']:>+10.2f}  {row['status']} {mark}"
        )
    print()

    # Fine-grained scan
    print("Fine-grained scan (interpolation):")
    f_values = [0.10, 0.12, 0.13, 0.15, 0.17, 0.18, 0.20]
    for row in slip_scan(f_values):
        flag = "INSIDE" if row["in_window"] else "outside"
        print(
            f"  f = {row['f']:.2f}  eta = {row['eta']:.3f}  "
            f"Sigma = {row['Sigma']:.3f}  [{flag}]"
        )
    print()

    # Reference point using GravSlip
    slip = GravSlip(m2=0.0035)
    print(f"At reference m^2 = {slip.m2}:")
    print(f"  f      = {slip.f:.3f}")
    print(f"  eta    = {slip.eta:.3f}")
    print(f"  Sigma  = {slip.Sigma:.3f}")
    print(f"  status = {slip.status}")
    print()

    # K(rho) bridge cross-check
    print("K(rho) bridge canonical scales (with reference K0 = 1.66):")
    bridge = KRhoBridge(K0=1.66)
    for row in bridge.canonical_table():
        print(
            f"  k = {row['k_h_per_Mpc']:>7.3f} h/Mpc  "
            f"Theta = {row['theta']:.4f}  mu = {row['mu_k']:.4f}  "
            f"({row['scale']})"
        )


if __name__ == "__main__":
    main()
