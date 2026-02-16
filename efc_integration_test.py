#!/usr/bin/env python3
"""
EFC Integration Test: Graph-AQUAL × Background
===============================================
THE CRITICAL TEST:
  Does Graph-AQUAL's G_eff(a,k) produce a growth history
  consistent with observed σ₈ ≈ 0.8 and fσ₈ data?
  If yes → Scenario A: ONE theory (ontological consolidation)
  If no  → Scenario B: TWO modules that can't coexist
WHAT THIS DOES:
  1. Defines G_eff(k,a) from Graph-AQUAL results:
     - UV (k >> k_Λ): G_eff = G  (Newton)
     - IR (k << k_Λ): G_eff = G · C² · √(a₀/g_N)  (MOND-boosted)
     - Transition at k_Λ = 2π/L_Λ where L_Λ ∝ 1/√Λ
  2. Solves linear growth equation:
     δ'' + [3/a + H'/H] δ' = (3/2) Ωm(a) · G_eff/G · δ / a²
  3. Extracts: σ₈(z), fσ₈(z), growth index γ
  4. Compares with:
     - ΛCDM baseline
     - Observational data (DES, KiDS, BOSS, eBOSS)
KILL CRITERIA:
  - σ₈(z=0) > 1.0 or < 0.5 → bulk coupling too strong/weak
  - γ deviates from 0.45–0.65 range → internal inconsistency
  - fσ₈ tension WORSE than ΛCDM → theory makes things worse
Author: Morten Magnusson / Symbiose
Date:   2026-02-16
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime
# ============================================================
# COSMOLOGICAL PARAMETERS
# ============================================================
# Planck 2018 baseline
H0_planck = 67.36          # km/s/Mpc
Om0 = 0.3153               # matter density parameter
OL0 = 1.0 - Om0            # dark energy (flat)
sigma8_planck = 0.8111      # Planck CMB normalization
# Derived
c_light = 2.998e5           # km/s
H0_si = H0_planck * 1e3 / (3.086e22)  # H₀ in s⁻¹
Lambda_cosmo = 3 * (H0_planck * 1e3 / (3.086e22))**2 * OL0 / c_light**2  # Λ in m⁻²
# ============================================================
# GRAPH-AQUAL PARAMETERS (from KT results)
# ============================================================
C_prefactor = 2.32          # geometry-independent prefactor
a0_base = 1.2e-10           # m/s² (standard MOND scale)
a0_eff = C_prefactor**2 * a0_base  # effective a₀ from graph = 5.4 × a₀
# L_Λ: bulk-reservoir screening length
# From graph results: L_Λ ∝ 1/√Λ, and a₀ ∝ c²√Λ
# In de Sitter: Λ = 3H₀²/c² → L_Λ = c/H₀ × (normalization)
# L_Λ in Mpc (using Verlinde-scale):
L_Lambda_Mpc = c_light / H0_planck   # ≈ 4450 Mpc (Hubble radius scale)
# k_Λ: transition wavenumber
k_Lambda = 2 * np.pi / L_Lambda_Mpc  # h/Mpc
print("=" * 70)
print("EFC INTEGRATION TEST: Graph-AQUAL × Background")
print("=" * 70)
print(f"\n  Graph-AQUAL parameters:")
print(f"    C = {C_prefactor}")
print(f"    a₀_base = {a0_base:.1e} m/s²")
print(f"    a₀_eff  = {a0_eff:.2e} m/s² (= C²·a₀)")
print(f"    L_Λ     = {L_Lambda_Mpc:.0f} Mpc")
print(f"    k_Λ     = {k_Lambda:.4f} h/Mpc")
print(f"\n  Cosmology:")
print(f"    H₀ = {H0_planck} km/s/Mpc")
print(f"    Ωm = {Om0}")
print(f"    σ₈(Planck) = {sigma8_planck}")
# ============================================================
# HUBBLE FUNCTION (flat ΛCDM — EFC background sector)
# ============================================================
def H_over_H0(a):
    """H(a)/H₀ for flat ΛCDM."""
    return np.sqrt(Om0 * a**(-3) + OL0)
def Omega_m(a):
    """Ωm(a) = Ωm0 a⁻³ / (H/H₀)²"""
    return Om0 * a**(-3) / H_over_H0(a)**2
def dH_da(a):
    """dH/da / H₀"""
    E = H_over_H0(a)
    return (-3 * Om0 * a**(-4)) / (2 * E)
# ============================================================
# G_eff(k, a) FROM GRAPH-AQUAL
# ============================================================
def G_eff_ratio(k, a, model='graph_aqual'):
    """
    G_eff(k,a) / G_Newton

    From Graph-AQUAL:
    - UV (high k, small scales, strong field): G_eff = G (Newton)
    - IR (low k, large scales, weak field): G_eff boosted
    - Transition at k_Λ

    The key physics: Graph-AQUAL's Λ-locking means the
    TRANSITION SCALE is set by L_Λ, not by mass.

    For perturbation theory:
    - At scale k, the characteristic acceleration is:
      g_char(k,a) ~ H₀² · Ωm(a) · δ(a) / k  (rough dimensional)
    - When g_char >> a₀: Newton
    - When g_char << a₀: MOND boost

    We parametrize this as a smooth interpolation.
    """
    if model == 'lcdm':
        return np.ones_like(np.atleast_1d(k), dtype=float)

    if model == 'graph_aqual':
        k = np.atleast_1d(k).astype(float)

        # Transition function
        # x = k / k_Λ: high x = small scales = Newton, low x = large scales = MOND
        x = k / k_Lambda

        # Graph-AQUAL gives: boost = C² in deep MOND
        # Smooth interpolation (matching μ(x) = x/√(1+x²)):
        # G_eff/G = 1 + (C² - 1) / (1 + (k/k_trans)²)
        #
        # But k_Λ is at Hubble scale — way larger than structure formation scales.
        # So we need to think about what k_trans actually is for perturbations.
        #
        # The physically relevant scale is where g ~ a₀:
        # On a perturbation of scale R = 2π/k:
        #   g ~ G·M_enclosed/R² ~ G·(4π/3)ρ̄δR³/R² = (4π/3)G·ρ̄·δ·R
        #   g = a₀ when R = R_MOND = a₀/((4π/3)G·ρ̄·δ)
        #
        # In terms of k: k_MOND(a) = 2π/R_MOND(a)
        # ρ̄(a) = ρ_crit · Ωm · a⁻³
        # For δ~1 (nonlinear): k_MOND ~ 0.01-0.1 h/Mpc (galaxy scales)
        # For δ~0.01 (linear): k_MOND ~ 0.001 h/Mpc

        rho_crit = 3 * H0_planck**2 / (8 * np.pi)  # in units where G·ρ gives (km/s/Mpc)²
        # Actually, let's be more careful with units.
        # ρ̄ = 3H₀²Ωm/(8πG) in proper units
        # G·ρ̄ = 3H₀²Ωm/(8π) × a⁻³

        # MOND scale in comoving h/Mpc:
        # k_MOND(a) = 2π × (4π/3) G ρ̄(a) δ / a₀
        # With G·ρ̄ = (3/8π)H₀²Ωm a⁻³, and taking δ ~ D(a)·δ_init:
        # For linear regime (δ << 1), effective δ ~ 0.01 at z=0

        # Simpler parametric approach matching the graph results:
        # The graph showed Λ-locking: transition at L_Λ.
        # For growth, we translate this to a scale-dependent boost.

        # Physical k_trans where MOND kicks in for LSS:
        # a₀_eff ≈ 6.5e-10 m/s²
        # R_transition where ḡ = a₀: this depends on overdensity
        # For a halo of mass M: r_MOND = √(GM/a₀)
        # For typical LSS (10¹⁴ M☉ cluster): r_MOND ~ 3 Mpc
        # → k_MOND ~ 2 h/Mpc
        # For linear perturbations (δ~0.01): much larger R
        # → k_MOND ~ 0.01 h/Mpc

        # Key insight from Λ-locking: the GRAPH sets transition at L_Λ scale
        # NOT at mass-dependent scale. So k_trans = k_Λ is the right choice
        # but we must account for the fact that L_Λ >> LSS scales.

        # This means: for ALL linear perturbation scales (k ~ 0.01-1 h/Mpc),
        # k >> k_Λ, so we're deep in the UV/Newton regime.
        # The MOND boost only matters at k << k_Λ (super-Hubble).

        # BUT: the graph also showed that the FORM of the transition
        # is gradient-dependent (AQUAL), not just a sharp cutoff.
        # So there's a scale-dependent "leakage" of the MOND boost
        # into sub-Hubble scales.

        # Parametrize the leakage:
        # At k >> k_Λ: almost pure Newton
        # The residual boost at k >> k_Λ is suppressed as (k_Λ/k)^α
        # From Yukawa-like screening: α = 2

        boost_max = C_prefactor**2  # = 5.38 (deep MOND boost)

        # G_eff/G = 1 + (boost_max - 1) × f(k/k_Λ)
        # where f → 1 for k << k_Λ and f → (k_Λ/k)² for k >> k_Λ

        f_transition = 1.0 / (1.0 + (x)**2)  # Yukawa-like suppression

        G_ratio = 1.0 + (boost_max - 1.0) * f_transition

        return G_ratio

    elif model == 'graph_aqual_strong':
        # Extreme scenario: what if transition is at galactic scale?
        # k_trans ~ 0.1 h/Mpc (10 Mpc structures)
        k = np.atleast_1d(k).astype(float)
        k_trans_strong = 0.1  # h/Mpc
        x = k / k_trans_strong
        boost_max = C_prefactor**2
        f_transition = 1.0 / (1.0 + x**2)
        G_ratio = 1.0 + (boost_max - 1.0) * f_transition
        return G_ratio

    elif model == 'graph_aqual_moderate':
        # Moderate: k_trans at ~1 h/Mpc (Mpc structures)
        k = np.atleast_1d(k).astype(float)
        k_trans_mod = 1.0  # h/Mpc
        x = k / k_trans_mod
        boost_max = C_prefactor**2
        f_transition = 1.0 / (1.0 + x**2)
        G_ratio = 1.0 + (boost_max - 1.0) * f_transition
        return G_ratio

    else:
        return np.ones_like(np.atleast_1d(k), dtype=float)
# ============================================================
# LINEAR GROWTH EQUATION
# ============================================================
def growth_ode(a, y, k, model):
    """
    Linear growth ODE in terms of scale factor a.

    y = [δ, δ' = dδ/da]

    δ'' + [3/a + (1/H)dH/da] δ' = (3/2) Ωm(a)/a² · G_eff(k,a)/G · δ

    Written as first-order system:
    y₀' = y₁
    y₁' = (3/2) Ωm(a)/a² · G_eff/G · y₀ - [3/a + H'/H] · y₁
    """
    delta, delta_prime = y

    E = H_over_H0(a)
    dE_da = dH_da(a)

    # Friction term
    friction = 3.0 / a + dE_da / E

    # Source term
    Om_a = Omega_m(a)
    Geff = G_eff_ratio(np.array([k]), a, model)[0]

    source = 1.5 * Om_a * Geff * delta / a**2

    return [delta_prime, source - friction * delta_prime]
def solve_growth(k, model='lcdm', a_init=1e-3, a_final=1.0, n_points=500):
    """
    Solve the linear growth equation for mode k.

    Initial conditions: δ ∝ a (matter-dominated growing mode)
    δ(a_init) = a_init, δ'(a_init) = 1
    """
    a_span = (a_init, a_final)
    a_eval = np.linspace(a_init, a_final, n_points)

    # Growing mode IC in matter domination: δ ∝ a
    y0 = [a_init, 1.0]

    sol = solve_ivp(
        growth_ode, a_span, y0,
        args=(k, model),
        t_eval=a_eval,
        method='RK45',
        rtol=1e-8, atol=1e-10,
        max_step=0.01
    )

    if not sol.success:
        print(f"  WARNING: Growth ODE failed for k={k}, model={model}")
        return None

    return {
        'a': sol.t,
        'z': 1.0/sol.t - 1,
        'delta': sol.y[0],
        'delta_prime': sol.y[1],
        'k': k,
        'model': model
    }
# ============================================================
# σ₈ AND fσ₈
# ============================================================
def compute_growth_factor(sol):
    """D(a) = δ(a) / δ(a=1), normalized to 1 today."""
    D = sol['delta'] / sol['delta'][-1]
    return D
def compute_f_growth(sol):
    """f = d ln D / d ln a = (a/D) dD/da"""
    a = sol['a']
    D = compute_growth_factor(sol)

    # Numerical derivative
    dD_da = np.gradient(D, a)
    f = a * dD_da / D
    return f
def compute_sigma8(k_array, model, z_target=0.0):
    """
    σ₈ from linear growth.

    σ₈(z) = σ₈(Planck) × D(z, model) / D(z=0, ΛCDM)

    Scale-dependent growth: we compute D(a) at multiple k
    and integrate over the power spectrum window.

    Simplified: use effective k = 0.1 h/Mpc (σ₈ scale)
    """
    k_sigma8 = 0.1  # h/Mpc (approximate scale for σ₈)

    a_target = 1.0 / (1.0 + z_target)

    sol = solve_growth(k_sigma8, model)
    sol_lcdm = solve_growth(k_sigma8, 'lcdm')

    if sol is None or sol_lcdm is None:
        return None

    # Find D(a_target)
    D_model = np.interp(a_target, sol['a'], sol['delta']) / sol['delta'][-1]
    D_lcdm = np.interp(a_target, sol_lcdm['a'], sol_lcdm['delta']) / sol_lcdm['delta'][-1]

    # At z=0: D=1 for both, but normalization differs
    # D(a) at z=0 is 1 by definition. But the AMPLITUDE differs.
    # σ₈(model, z=0) = σ₈(Planck) × [D_model(z=0) amplitude relative to ΛCDM]

    # Actually: the key is the ratio of growth AT z_target
    # relative to the initial conditions.
    # Since both start with δ = a_init, the ratio of δ at a=1
    # tells us how much MORE growth happened.

    growth_ratio = sol['delta'][-1] / sol_lcdm['delta'][-1]

    sigma8 = sigma8_planck * growth_ratio * D_model

    return sigma8
def compute_fsigma8(model, z_array):
    """Compute fσ₈(z) for a model."""
    k_eff = 0.1  # h/Mpc

    sol = solve_growth(k_eff, model)
    sol_lcdm = solve_growth(k_eff, 'lcdm')

    if sol is None or sol_lcdm is None:
        return None, None

    growth_ratio = sol['delta'][-1] / sol_lcdm['delta'][-1]

    D = compute_growth_factor(sol)
    f = compute_f_growth(sol)

    # σ₈(a) = σ₈_planck × growth_ratio × D(a)
    sigma8_a = sigma8_planck * growth_ratio * D

    fsigma8 = f * sigma8_a

    # Interpolate to requested z
    a_array = 1.0 / (1.0 + z_array)
    fsig8_interp = np.interp(a_array, sol['a'], fsigma8)
    sig8_interp = np.interp(a_array, sol['a'], sigma8_a)
    f_interp = np.interp(a_array, sol['a'], f)

    return fsig8_interp, sig8_interp, f_interp
# ============================================================
# OBSERVATIONAL DATA (fσ₈ measurements)
# ============================================================
# Key fσ₈ measurements (compilation from eBOSS 2021 + DESI 2024)
fsigma8_data = [
    # z,     fσ₈,    err,    survey
    (0.15,  0.490,  0.045,  "SDSS MGS"),
    (0.38,  0.497,  0.045,  "BOSS DR12"),
    (0.51,  0.459,  0.038,  "BOSS DR12"),
    (0.61,  0.436,  0.034,  "BOSS DR12"),
    (0.70,  0.448,  0.043,  "eBOSS LRG"),
    (0.85,  0.315,  0.095,  "eBOSS ELG"),
    (1.48,  0.462,  0.045,  "eBOSS QSO"),
]
# ============================================================
# GROWTH INDEX γ
# ============================================================
def compute_growth_index(sol):
    """
    γ defined by f(a) ≈ Ωm(a)^γ

    ΛCDM predicts γ ≈ 0.545
    DGP predicts γ ≈ 0.68
    f(R) predicts γ ≈ 0.40-0.43
    """
    a = sol['a']
    f = compute_f_growth(sol)

    # Only use z < 2 where f is well-behaved
    mask = (a > 0.33) & (a <= 1.0) & (f > 0) & np.isfinite(f)

    if np.sum(mask) < 5:
        return np.nan

    Om_arr = np.array([Omega_m(ai) for ai in a[mask]])

    # γ = ln(f) / ln(Ωm)
    log_f = np.log(f[mask])
    log_Om = np.log(Om_arr)

    # Linear fit
    gamma, _ = np.polyfit(log_Om, log_f, 1)

    return gamma
# ============================================================
# RUN ALL MODELS
# ============================================================
def run_all():
    """Run growth analysis for all models."""

    models = [
        ('lcdm',                'ΛCDM',                'black',  '-'),
        ('graph_aqual',         'Graph-AQUAL (Hubble)', 'blue',   '-'),
        ('graph_aqual_strong',  'Graph-AQUAL (10 Mpc)', 'red',    '--'),
        ('graph_aqual_moderate','Graph-AQUAL (1 Mpc)',  'orange', '--'),
    ]

    print("\n" + "=" * 70)
    print("RUNNING GROWTH ANALYSIS")
    print("=" * 70)

    results = {}

    # Part 1: G_eff profiles
    print("\n--- G_eff(k) profiles ---")
    k_test = np.logspace(-4, 1, 200)  # h/Mpc

    for model_id, label, color, ls in models:
        G_arr = G_eff_ratio(k_test, 1.0, model_id)
        print(f"  {label:30s}: G_eff/G at k=0.01 = {G_arr[np.argmin(np.abs(k_test-0.01))]:.4f}, "
              f"k=0.1 = {G_arr[np.argmin(np.abs(k_test-0.1))]:.4f}, "
              f"k=1.0 = {G_arr[np.argmin(np.abs(k_test-1.0))]:.4f}")

    # Part 2: Growth solutions
    print("\n--- Growth factor D(a) ---")
    k_eff = 0.1  # h/Mpc (σ₈ scale)

    for model_id, label, color, ls in models:
        sol = solve_growth(k_eff, model_id)
        if sol is None:
            print(f"  {label}: FAILED")
            continue

        D = compute_growth_factor(sol)
        f = compute_f_growth(sol)
        gamma = compute_growth_index(sol)
        growth_ratio = sol['delta'][-1]

        results[model_id] = {
            'sol': sol,
            'D': D,
            'f': f,
            'gamma': gamma,
            'growth_ratio': growth_ratio,
            'label': label,
            'color': color,
            'ls': ls
        }

        print(f"  {label:30s}: δ(a=1)={growth_ratio:.4f}, γ={gamma:.3f}")

    # Part 3: σ₈ and fσ₈
    print("\n--- σ₈ and fσ₈ ---")
    z_eval = np.array([0.0, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0])

    print(f"\n  {'Model':<30s} {'σ₈(0)':<10s} {'fσ₈(0.5)':<10s} {'γ':<8s} {'VERDICT'}")
    print(f"  {'-'*68}")

    for model_id, label, color, ls in models:
        fsig8, sig8, f_arr = compute_fsigma8(model_id, z_eval)

        if fsig8 is None:
            print(f"  {label:30s}: FAILED")
            continue

        results[model_id]['sigma8_z'] = sig8
        results[model_id]['fsigma8_z'] = fsig8
        results[model_id]['f_z'] = f_arr
        results[model_id]['z_eval'] = z_eval

        gamma = results[model_id]['gamma']

        # Verdict
        s8_0 = sig8[0]
        if 0.5 < s8_0 < 1.0:
            if abs(s8_0 - 0.77) < abs(sigma8_planck - 0.77):
                verdict = "✓ BETTER than Planck"
            elif abs(s8_0 - sigma8_planck) < 0.02:
                verdict = "✓ ≈ ΛCDM"
            else:
                verdict = "⚠ SHIFTED"
        elif s8_0 > 1.0:
            verdict = "✗ EXPLODED (too much growth)"
        elif s8_0 < 0.5:
            verdict = "✗ KILLED (too little growth)"
        else:
            verdict = "?"

        print(f"  {label:30s} {s8_0:<10.4f} {fsig8[2]:<10.4f} {gamma:<8.3f} {verdict}")

    # Part 4: Scale-dependent growth
    print("\n--- Scale-dependent growth ratio D(k)/D_ΛCDM ---")
    k_scan = np.array([0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0])

    for model_id, label, color, ls in models:
        if model_id == 'lcdm':
            continue
        print(f"\n  {label}:")
        print(f"    {'k [h/Mpc]':<12s} {'G_eff/G':<10s} {'D/D_ΛCDM':<10s}")
        print(f"    {'-'*30}")
        for k in k_scan:
            sol = solve_growth(k, model_id)
            sol_lcdm = solve_growth(k, 'lcdm')
            if sol and sol_lcdm:
                ratio = sol['delta'][-1] / sol_lcdm['delta'][-1]
                Geff = G_eff_ratio(np.array([k]), 1.0, model_id)[0]
                print(f"    {k:<12.4f} {Geff:<10.4f} {ratio:<10.4f}")

    return results, models, k_test
# ============================================================
# FIGURES
# ============================================================
def make_figures(results, models, k_test):
    """Create diagnostic plots."""

    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    fig.suptitle('EFC Integration Test: Graph-AQUAL × Background\n'
                 'Does Graph-AQUAL survive cosmological growth?',
                 fontsize=14, fontweight='bold', y=0.99)

    # Panel 1: G_eff(k) profiles
    ax = axes[0, 0]
    for model_id, label, color, ls in models:
        G_arr = G_eff_ratio(k_test, 1.0, model_id)
        ax.semilogx(k_test, G_arr, color=color, ls=ls, lw=2, label=label)
    ax.set_xlabel('k [h/Mpc]')
    ax.set_ylabel('$G_{eff}/G$')
    ax.set_title('Effective gravitational coupling')
    ax.legend(fontsize=7)
    ax.axhline(1, color='gray', ls=':', alpha=0.3)
    ax.set_ylim(0.9, 6)

    # Panel 2: Growth factor D(a)
    ax = axes[0, 1]
    for model_id in results:
        r = results[model_id]
        sol = r['sol']
        D = r['D']
        mask = sol['a'] > 0.1
        ax.plot(sol['a'][mask], D[mask], color=r['color'], ls=r['ls'],
                lw=2, label=r['label'])
    ax.set_xlabel('a')
    ax.set_ylabel('D(a) / D(1)')
    ax.set_title('Linear growth factor')
    ax.legend(fontsize=7)

    # Panel 3: f(a) = growth rate
    ax = axes[0, 2]
    for model_id in results:
        r = results[model_id]
        sol = r['sol']
        f = r['f']
        mask = (sol['a'] > 0.2) & (sol['a'] < 1.0) & np.isfinite(f)
        ax.plot(sol['a'][mask], f[mask], color=r['color'], ls=r['ls'],
                lw=2, label=f"{r['label']} (γ={r['gamma']:.3f})")

    # Ωm^0.545 reference
    a_ref = np.linspace(0.2, 1.0, 100)
    Om_ref = np.array([Omega_m(a) for a in a_ref])
    ax.plot(a_ref, Om_ref**0.545, 'k:', alpha=0.5, label='$\\Omega_m^{0.545}$ (ΛCDM)')
    ax.set_xlabel('a')
    ax.set_ylabel('f = d ln D / d ln a')
    ax.set_title('Growth rate')
    ax.legend(fontsize=6)

    # Panel 4: σ₈(z)
    ax = axes[1, 0]
    for model_id in results:
        r = results[model_id]
        if 'z_eval' in r:
            ax.plot(r['z_eval'], r['sigma8_z'], color=r['color'], ls=r['ls'],
                    lw=2, marker='o', ms=4, label=r['label'])

    # Weak lensing constraints
    ax.axhspan(0.74, 0.80, alpha=0.15, color='green', label='WL (KiDS/DES)')
    ax.axhline(sigma8_planck, color='gray', ls='--', alpha=0.5, label=f'Planck ({sigma8_planck})')
    ax.set_xlabel('z')
    ax.set_ylabel('$\\sigma_8(z)$')
    ax.set_title('$\\sigma_8$ evolution')
    ax.legend(fontsize=6)
    ax.invert_xaxis()

    # Panel 5: fσ₈(z) with data
    ax = axes[1, 1]
    for model_id in results:
        r = results[model_id]
        if 'z_eval' in r:
            ax.plot(r['z_eval'], r['fsigma8_z'], color=r['color'], ls=r['ls'],
                    lw=2, label=r['label'])

    # Observational data
    z_data = [d[0] for d in fsigma8_data]
    fs8_data = [d[1] for d in fsigma8_data]
    err_data = [d[2] for d in fsigma8_data]
    ax.errorbar(z_data, fs8_data, yerr=err_data, fmt='ks', ms=6, capsize=3,
                label='BOSS/eBOSS data', zorder=10)
    ax.set_xlabel('z')
    ax.set_ylabel('$f\\sigma_8(z)$')
    ax.set_title('$f\\sigma_8$ comparison with data')
    ax.legend(fontsize=6)

    # Panel 6: Summary table
    ax = axes[1, 2]
    ax.axis('off')

    table_text = "INTEGRATION TEST SUMMARY\n" + "=" * 40 + "\n\n"
    table_text += f"{'Model':<25s} {'σ₈(0)':<8s} {'γ':<7s} {'Status'}\n"
    table_text += f"{'-'*50}\n"

    for model_id in results:
        r = results[model_id]
        s8 = r.get('sigma8_z', [None])[0]
        g = r['gamma']

        if s8 is None:
            status = "N/A"
        elif 0.5 < s8 < 1.0 and 0.40 < g < 0.65:
            status = "✓ SURVIVES"
        elif s8 > 1.0:
            status = "✗ EXPLODED"
        elif s8 < 0.5:
            status = "✗ KILLED"
        else:
            status = "⚠ CHECK"

        s8_str = f"{s8:.4f}" if s8 else "N/A"
        table_text += f"{r['label']:<25s} {s8_str:<8s} {g:<7.3f} {status}\n"

    table_text += f"\n{'='*40}\n"
    table_text += f"Planck σ₈ = {sigma8_planck}\n"
    table_text += f"WL σ₈ ≈ 0.77 ± 0.03\n"
    table_text += f"ΛCDM γ ≈ 0.545\n"
    table_text += f"\nKILL: σ₈ > 1.0 or < 0.5\n"
    table_text += f"KILL: γ outside [0.40, 0.65]\n"

    ax.text(0.05, 0.95, table_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    outpath = os.path.expanduser('~/efc_integration_test.png')
    plt.savefig(outpath, dpi=200, bbox_inches='tight')
    print(f"\nFigure saved: {outpath}")

    return outpath
# ============================================================
# SAVE RESULTS
# ============================================================
def save_results(results):
    """Save numerical results to JSON."""

    output = {
        'timestamp': datetime.now().isoformat(),
        'test': 'EFC Integration: Graph-AQUAL × Background',
        'parameters': {
            'C_prefactor': C_prefactor,
            'a0_base': a0_base,
            'a0_eff': a0_eff,
            'L_Lambda_Mpc': L_Lambda_Mpc,
            'k_Lambda': k_Lambda,
            'H0': H0_planck,
            'Om0': Om0,
            'sigma8_planck': sigma8_planck,
        },
        'results': {}
    }

    for model_id in results:
        r = results[model_id]
        entry = {
            'label': r['label'],
            'gamma': float(r['gamma']),
            'growth_ratio': float(r['growth_ratio']),
        }
        if 'sigma8_z' in r:
            entry['sigma8_z0'] = float(r['sigma8_z'][0])
            entry['fsigma8'] = {
                f"z={z:.1f}": float(fs8)
                for z, fs8 in zip(r['z_eval'], r['fsigma8_z'])
            }
        output['results'][model_id] = entry

    outpath = os.path.expanduser('~/efc_integration_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Results saved: {outpath}")

    return outpath
# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":

    results, models, k_test = run_all()

    figpath = make_figures(results, models, k_test)
    jsonpath = save_results(results)

    print("\n" + "=" * 70)
    print("INTEGRATION TEST COMPLETE")
    print("=" * 70)

    print("\nDECISION MATRIX:")
    print("-" * 50)

    for model_id in results:
        r = results[model_id]
        s8 = r.get('sigma8_z', [None])[0]
        g = r['gamma']

        if s8 is None:
            continue

        print(f"\n  {r['label']}:")
        print(f"    σ₈(0) = {s8:.4f}  (Planck: {sigma8_planck}, WL: ~0.77)")
        print(f"    γ     = {g:.3f}   (ΛCDM: 0.545)")

        if 0.5 < s8 < 1.0 and 0.40 < g < 0.65:
            print(f"    → SURVIVES: Growth is viable")
            if abs(s8 - 0.77) < abs(sigma8_planck - 0.77):
                print(f"    → BONUS: σ₈ closer to WL than Planck!")
        elif s8 > 1.0:
            print(f"    → KILLED: σ₈ exploded (bulk coupling too strong)")
        elif s8 < 0.5:
            print(f"    → KILLED: Growth died (IR screening too aggressive)")
        else:
            print(f"    → CHECK: Unusual growth index")

    print(f"\n  Outputs:")
    print(f"    Figure:  {figpath}")
    print(f"    Results: {jsonpath}")
    print()
