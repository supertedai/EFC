"""demo_sparc175_elimination.py

Demonstration of the hybrid model vs pure multiplicative models
from Magnusson (2026) 'Sparc175 Elimination'.

Generates a synthetic FLOW-regime galaxy and compares predictions.
"""
import numpy as np
import sys

try:
    from sparc175_elimination import (
        V_baryonic, g_from_V, mu_bose_einstein, mu_screening,
        V2_hybrid, V2_cored, chi2_per_galaxy, delta_aic,
        SCREENING_K, UPSILON_DISK, UPSILON_BUL, SIGMA_FLOOR
    )
except ImportError:
    sys.exit("Place sparc175_elimination.py in the same directory or PYTHONPATH.")

# ------------------------------------------------------------------
# 1.  Synthetic FLOW-regime galaxy (low-acceleration, gas-dominated)
# ------------------------------------------------------------------
np.random.seed(42)
N = 40
r = np.linspace(1.0, 25.0, N)          # kpc

# Baryonic components (gas-dominated → V_gas >> V_disk)
V_gas  = 55.0 * np.sqrt(r / (r + 3.0))
V_disk = 20.0 * np.exp(-r / 12.0) * np.sqrt(r / (r + 2.0))
V_bul  = np.zeros_like(r)

Vbar = V_baryonic(V_gas, V_disk, V_bul)
g_bar = g_from_V(Vbar, r)

# "True" observed curve: hybrid with known A_gal
A_gal_true = 800.0   # km^2/s^2
g_dagger   = 1.0e-10 # m/s^2
r0_global  = 3.5     # kpc

V2_true = V2_hybrid(r, Vbar, g_dagger, r0_global, A_gal_true, k=SCREENING_K)
V_obs = np.sqrt(np.maximum(V2_true, 0.0)) + np.random.normal(0, 2.0, N)
sigma_V = np.full(N, 3.0)  # km/s

# ------------------------------------------------------------------
# 2.  Fit pure screening model (zero per-galaxy freedom)
# ------------------------------------------------------------------
mu_sc = mu_screening(g_bar, g_dagger, k=SCREENING_K)
V2_screen = Vbar**2 * mu_sc
chi2_screen = chi2_per_galaxy(V_obs, V2_screen, sigma_V)
chi2_screen_dof = chi2_screen / N

# ------------------------------------------------------------------
# 3.  Fit hybrid model: grid-search over A_gal (1 free param)
# ------------------------------------------------------------------
A_grid = np.linspace(-500, 2000, 2000)
best_chi2 = 1e30
best_A = 0.0
for A in A_grid:
    V2h = V2_hybrid(r, Vbar, g_dagger, r0_global, A)
    c2 = chi2_per_galaxy(V_obs, V2h, sigma_V)
    if c2 < best_chi2:
        best_chi2, best_A = c2, A

chi2_hybrid_dof = best_chi2 / (N - 1)

# ------------------------------------------------------------------
# 4.  NFW-like reference (2-param cored halo for simplicity)
# ------------------------------------------------------------------
best_chi2_nfw = 1e30
for V0 in np.linspace(10, 120, 200):
    for rc in np.linspace(0.5, 15.0, 100):
        V2n = Vbar**2 + V2_cored(r, V0, rc)
        c2 = chi2_per_galaxy(V_obs, V2n, sigma_V)
        if c2 < best_chi2_nfw:
            best_chi2_nfw = c2

chi2_nfw_dof = best_chi2_nfw / (N - 2)

# ------------------------------------------------------------------
# 5.  Report
# ------------------------------------------------------------------
print("="*60)
print("Sparc175 Elimination — Demo on synthetic FLOW galaxy")
print("="*60)
print(f"  N data points        : {N}")
print(f"  True A_gal           : {A_gal_true:.1f}  km²/s²")
print(f"  Recovered A_gal      : {best_A:.1f}  km²/s²")
print()
print(f"  Screening (0 free)   : chi²/dof = {chi2_screen_dof:.2f}")
print(f"  Hybrid    (1 free)   : chi²/dof = {chi2_hybrid_dof:.2f}")
print(f"  Cored halo(2 free)   : chi²/dof = {chi2_nfw_dof:.2f}")
print()
d_aic = delta_aic(best_chi2, best_chi2_nfw, k_model=1, k_ref=2, n=N)
print(f"  Delta AIC (hybrid vs halo) = {d_aic:.1f}")
if abs(d_aic) < 10:
    print("  → Models are comparable (|ΔAIC| < 10)")
elif d_aic < -10:
    print("  → Hybrid decisively better")
else:
    print("  → Halo decisively better")

# ------------------------------------------------------------------
# 6.  Optional plot
# ------------------------------------------------------------------
try:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(r, V_obs, yerr=sigma_V, fmt='ko', ms=3, label='V_obs (synthetic)')
    ax.plot(r, Vbar, 'b--', label='V_bar')
    ax.plot(r, np.sqrt(np.maximum(V2_screen, 0)), 'r-',
            label=f'Screening (χ²/dof={chi2_screen_dof:.1f})')
    V2_best = V2_hybrid(r, Vbar, g_dagger, r0_global, best_A)
    ax.plot(r, np.sqrt(np.maximum(V2_best, 0)), 'g-', lw=2,
            label=f'Hybrid A={best_A:.0f} (χ²/dof={chi2_hybrid_dof:.2f})')
    ax.set_xlabel('r  [kpc]')
    ax.set_ylabel('V  [km/s]')
    ax.set_title('Sparc175 Elimination: Synthetic FLOW Galaxy')
    ax.legend(fontsize=9)
    ax.set_ylim(0, None)
    plt.tight_layout()
    plt.savefig('demo_sparc175.png', dpi=150)
    plt.show()
    print("\nPlot saved to demo_sparc175.png")
except ImportError:
    print("\nmatplotlib not found — skipping plot.")
