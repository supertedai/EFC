#!/usr/bin/env python3
"""Demonstration: EFC Cross-Domain Bridge Equations.

Reproduces key results from Magnusson (2026):
  DOI: 10.6084/m9.figshare.31940547

Shows:
  1. Unified gradient-flow dynamics (Eq. 2)
  2. Bridge B1: cosmology -> neural coupling (Eq. 5)
  3. Bridge B1** (revised): degree-heterogeneity (Eq. 7)
  4. Bridge B2: neural -> RLHF (Eq. 10-14)
  5. Cross-domain predictions (P4**, P5, P6)
  6. Observable dictionary (Table 1)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bridge_equations import (
    UnifiedGradientFlow,
    BridgeB1Cosmology2Neural,
    BridgeB1StarStar,
    BridgeB2Neural2RLHF,
    CrossDomainPredictions,
    ObservableDictionary,
    K_EFC,
    A_G,
    C_CROSS,
)


def demo_unified_dynamics():
    """1. Unified gradient-flow dynamics."""
    print("=" * 65)
    print("1. UNIFIED GRADIENT-FLOW DYNAMICS (Eq. 2)")
    print("   dF/dt = -integral |nabla s_dot|^2 dV + B")
    print("=" * 65)

    scenarios = [
        ("Strongly dissipative", [1.0, 2.0, 0.5, 1.5], 0.1),
        ("Marginal stability", [0.3, 0.2, 0.1], 0.59),
        ("Boundary-dominated", [0.1, 0.05], 0.5),
    ]

    for name, grads, B in scenarios:
        gf = UnifiedGradientFlow(grad_s_dot_squared=grads, boundary_flux=B)
        print(f"\n  {name}:")
        print(f"    Dissipation = {gf.volume_dissipation():.3f}")
        print(f"    Boundary B  = {B:.3f}")
        print(f"    dF/dt       = {gf.dF_dt():.3f}")
        print(f"    Stable (Lyapunov): {gf.is_stable()}")
        print(f"    Stability margin:  {gf.stability_margin():.3f}")


def demo_bridge_b1():
    """2. Bridge B1: cosmology -> neural coupling."""
    print("\n" + "=" * 65)
    print("2. BRIDGE B1: COSMOLOGY -> NEURAL (Eq. 5)")
    print("   s_dot_i = alpha_N * g_eff * sigma_syn * Gamma")
    print("=" * 65)

    b1 = BridgeB1Cosmology2Neural()
    print(f"\n  EFC parameters: k = {K_EFC}, a_G = {A_G}")
    print(f"  L_cortex = {b1.l_cortex} m")
    print(f"  alpha_N = k / (a_G * L^3) = {b1.alpha_n:.1f} K bit^-1 m^2 s^-1")

    print(f"\n  Neural entropy-production rates by region:")
    regions = [
        ("Prefrontal (high g_eff)", 500.0, 50.0, 1.2, 1e6),
        ("Motor cortex (moderate)", 100.0, 50.0, 0.8, 5e5),
        ("Primary visual (low)", 20.0, 50.0, 0.5, 2e5),
    ]

    for name, grad_phi, c_m, sigma, gamma in regions:
        g_eff = b1.effective_gradient(grad_phi, c_m)
        s_dot = b1.entropy_production_rate(g_eff, sigma, gamma)
        print(f"    {name}:")
        print(f"      g_eff = {g_eff:.4f} m^-1, s_dot = {s_dot:.2f} K/(m^3 s)")


def demo_bridge_b1_star_star():
    """3. Bridge B1** (revised): degree heterogeneity."""
    print("\n" + "=" * 65)
    print("3. BRIDGE B1** (REVISED): DEGREE HETEROGENEITY (Eq. 7)")
    print("   eta = C_eff / D_ratio^gamma")
    print("=" * 65)

    print(f"\n  Cross-scale constant C = k/a_G = {C_CROSS:.2f}")

    scenarios = [
        ("HCP group-level", 45.0, 12.0, 0.5, 0.55),
        ("HCP individual", 50.0, 10.0, 0.5, 0.55),
        ("Homogeneous network", 25.0, 25.0, 0.5, 0.55),
        ("Strong heterogeneity", 60.0, 8.0, 0.5, 0.55),
    ]

    print(f"\n  {'Scenario':>25s}  {'D_ratio':>8s}  {'C_eff':>6s}  {'eta':>8s}")
    print("  " + "-" * 52)

    for name, k_hub, k_per, kappa, gamma in scenarios:
        b1ss = BridgeB1StarStar(k_hub, k_per, kappa, gamma)
        print(f"  {name:>25s}  {b1ss.d_ratio:8.2f}  {b1ss.c_eff:6.2f}  "
              f"{b1ss.eta_predicted():8.4f}")

    # Falsification test
    b1ss = BridgeB1StarStar(45.0, 12.0, 0.5, 0.55)
    result = b1ss.is_falsified(eta_obs=1.95, sigma=0.3, n_subjects=25)
    print(f"\n  Falsification test (HCP group, n=25):")
    print(f"    eta_predicted = {result['eta_predicted']:.4f}")
    print(f"    eta_observed  = {result['eta_observed']:.4f}")
    print(f"    z-score       = {result['z_score']:.2f}")
    print(f"    Falsified: {result['falsified']}")

    # Limit case
    print(f"\n  Limit D_ratio -> 1: eta -> C_eff = {b1ss.limit_homogeneous():.4f}")
    print("  -> Recovers cosmological gradient-amplification factor")


def demo_bridge_b2():
    """4. Bridge B2: neural -> RLHF."""
    print("\n" + "=" * 65)
    print("4. BRIDGE B2: NEURAL -> RLHF (Eq. 10-14)")
    print("   nabla S_neural <-> nabla^2 R(s,a)")
    print("=" * 65)

    # Hypothetical fMRI-derived parameters
    scenarios = [
        ("Low I_net (sparse)", 0.05, 10.0),
        ("Moderate I_net", 0.05, 50.0),
        ("High I_net (dense)", 0.05, 200.0),
    ]

    print(f"\n  {'Scenario':>25s}  {'S*_neural':>10s}  {'I_net':>8s}  "
          f"{'T_cog':>8s}  {'beta_KL':>8s}")
    print("  " + "-" * 64)

    for name, s_star, i_net in scenarios:
        b2 = BridgeB2Neural2RLHF(s_star, i_net)
        print(f"  {name:>25s}  {s_star:10.4f}  {i_net:8.1f}  "
              f"{b2.t_cog:8.5f}  {b2.beta_kl_predicted:8.1f}")

    # P5 validation
    b2 = BridgeB2Neural2RLHF(0.05, 50.0)
    p5 = b2.validate_p5(beta_kl_observed=1050.0, tolerance=0.2)
    print(f"\n  P5 validation (I_net=50, beta_KL_obs=1050):")
    print(f"    T_cog         = {p5['t_cog']:.6f}")
    print(f"    beta_KL pred  = {p5['beta_kl_predicted']:.1f}")
    print(f"    beta_KL obs   = {p5['beta_kl_observed']:.1f}")
    print(f"    Consistent: {p5['consistent']}")


def demo_cross_domain_predictions():
    """5. Cross-domain predictions."""
    print("\n" + "=" * 65)
    print("5. CROSS-DOMAIN PREDICTIONS (P4**, P5, P6)")
    print("=" * 65)

    # P4**
    p4 = CrossDomainPredictions.p4_star_star(45.0, 12.0)
    print(f"\n  P4** (degree-heterogeneity -> entropy ratio):")
    print(f"    D_ratio      = {p4['d_ratio']:.2f}")
    print(f"    C_eff        = {p4['c_eff']:.4f}")
    print(f"    eta_predicted = {p4['eta_predicted']:.4f}")
    print(f"    Test: {p4['test']}")

    # P5
    p5 = CrossDomainPredictions.p5(0.05, 50.0)
    print(f"\n  P5 (T_cog calibrates beta_KL):")
    print(f"    T_cog          = {p5['t_cog']:.6f}")
    print(f"    beta_KL pred   = {p5['beta_kl_predicted']:.1f}")
    print(f"    Test: {p5['test']}")

    # P6
    p6 = CrossDomainPredictions.p6()
    print(f"\n  P6 (entropy topology <-> reward curvature):")
    print(f"    Mapping: {p6['mapping']}")
    print(f"    Test: {p6['test']}")


def demo_observable_dictionary():
    """6. Observable dictionary."""
    print("\n" + "=" * 65)
    print("6. OBSERVABLE DICTIONARY (Table 1)")
    print("=" * 65)
    print()
    ObservableDictionary.print_table()


if __name__ == "__main__":
    print("EFC Cross-Domain Bridge Equations")
    print("Magnusson (2026) — DOI: 10.6084/m9.figshare.31940547")
    print()

    demo_unified_dynamics()
    demo_bridge_b1()
    demo_bridge_b1_star_star()
    demo_bridge_b2()
    demo_cross_domain_predictions()
    demo_observable_dictionary()

    print("\n" + "=" * 65)
    print("All demonstrations completed successfully.")
    print("Key result: Three EFC tracks unified via gradient-flow dynamics")
    print("=" * 65)
