#!/usr/bin/env python3
"""
Evaluate the EFC Consciousness Bridge across systems and states.

Demonstrates the three-equation system from:
  Magnusson 2026, DOI 10.6084/m9.figshare.31969983

Usage:
  python examples/evaluate_bridge.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.consciousness_bridge import (
    consciousness_functional,
    kappa_hat_steady_state,
    kappa_hat_healthy,
    find_fixed_point,
    PREDICTIONS,
    K_CROSS_DOMAIN,
    K_UNCERTAINTY,
    REGIMES,
)


def main() -> None:
    gamma = 5.0  # placeholder — gamma is currently unconstrained

    print("=" * 72)
    print("EFC Consciousness Bridge — Three-Equation System Demo")
    print(f"DOI: 10.6084/m9.figshare.31969983")
    print(f"gamma = {gamma} (placeholder — unconstrained)")
    print(f"K = {K_CROSS_DOMAIN} +/- {K_UNCERTAINTY} (from SPARC, zero neural fitting)")
    print("=" * 72)

    # --- Table 5: System predictions ---
    print("\n--- Table 5: Testable Predictions ---")
    print(f"{'System':<20} {'Omega_hat':>10} {'kappa_hat':>10} {'C':>10} {'Prediction'}")
    print("-" * 72)

    for p in PREDICTIONS:
        oh = sum(p["Omega_hat"]) / 2
        kh = sum(p["kappa_hat"]) / 2
        C = consciousness_functional(oh, kh, gamma)
        print(f"{p['system']:<20} {oh:>10.3f} {kh:>10.4f} {C:>10.4f} {p['prediction']}")

    # --- Emergent anti-correlation ---
    print("\n--- Emergent Anti-Correlation (Eq. 12) ---")
    j_flow = 0.5
    mu = 1.0
    print(f"  J_flow = {j_flow}, mu = {mu}")
    for oh in [0.5, 0.6, 0.7, 0.8, 0.9]:
        kh_ss = kappa_hat_steady_state(j_flow, mu, oh)
        C = consciousness_functional(oh, kh_ss, gamma)
        print(f"  Omega_hat = {oh:.1f}  =>  kappa_hat_ss = {kh_ss:.3f}  =>  C = {C:.4f}")

    # --- Bridge B1* equation ---
    print("\n--- Bridge B1* Equation (Eq. 5) ---")
    for lam2, tau in [(0.5, 1.0), (1.0, 2.0), (2.0, 0.5), (5.0, 0.1)]:
        kh = kappa_hat_healthy(lam2, tau)
        print(f"  lambda_2(W) = {lam2:.1f}, tau_c = {tau:.1f}  =>  kappa_hat_healthy = {kh:.3f}")

    # --- Fixed-point analysis ---
    print("\n--- Fixed-Point Analysis (Eqs. 13-15) ---")
    fp = find_fixed_point(omega_hat_star=0.85, j_flow=0.5, mu=1.0, gamma=gamma)
    print(f"  Omega_hat* = {fp.omega_hat_star:.3f}")
    print(f"  kappa_hat* = {fp.kappa_hat_star:.3f}")
    print(f"  C*         = {fp.C_star:.4f}")

    # --- Regime mapping ---
    print("\n--- Regime Mapping (Table 1) ---")
    for regime, info in REGIMES.items():
        print(f"  {regime}: rho_l = {info['rho']:.0e} kg/m^3, S_l = {info['S_label']}, domain = {info['domain']}")

    # --- Disclaimer ---
    print("\n" + "=" * 72)
    print("NOTE: gamma is a placeholder. The model becomes fully predictive")
    print("once gamma is estimated from EEG/fMRI data (e.g. PCI database or")
    print("Human Connectome Project). The qualitative predictions (ordering")
    print("of C across systems) are robust to gamma > 0, but quantitative")
    print("values depend on gamma.")
    print("=" * 72)


if __name__ == "__main__":
    main()
