"""demo_efc_redshift_decomposition.py

Demonstrates the three-window EFC redshift decomposition.
Generates a comparison plot (if matplotlib available) showing
how EFC predictions deviate from LCDM for each observational window.
"""
import numpy as np

from efc_redshift_decomposition import (
    A_G, A_H0, A_C, MOND_RATIO,
    s_eff, integrand_F, redshift_integral, redshift_lcdm,
    t_cmb_efc, cddr_eta, s_z_consistency, c_eff,
)

# ---- redshift grid --------------------------------------------------------
z = np.linspace(0.01, 4.0, 200)

# ---- Window 1: Thermal  T_CMB(z) -----------------------------------------
T_lcdm = 2.7255 * (1.0 + z)
T_efc_mild = t_cmb_efc(z, delta_s=0.5)   # mild EFC correction
T_efc_strong = t_cmb_efc(z, delta_s=2.0) # stronger correction

print("=== Window 1: Thermal T_CMB(z) ===")
print(f"  z=2  LCDM: {2.7255*3:.4f} K")
print(f"  z=2  EFC(delta_s=0.5): {t_cmb_efc(np.array([2.0]), delta_s=0.5)[0]:.4f} K")
print(f"  z=2  EFC(delta_s=2.0): {t_cmb_efc(np.array([2.0]), delta_s=2.0)[0]:.4f} K")

# ---- Window 2: Geometric  CDDR  eta(z) -----------------------------------
eta_lcdm = np.ones_like(z)
eta_efc1 = cddr_eta(z, epsilon=0.05, beta=0.5)
eta_efc2 = cddr_eta(z, epsilon=0.10, beta=1.0)

print("\n=== Window 2: Geometric CDDR eta(z) ===")
print(f"  z=1  LCDM: eta=1.000")
print(f"  z=1  EFC(eps=0.05,beta=0.5): {cddr_eta(np.array([1.0]), epsilon=0.05, beta=0.5)[0]:.6f}")
print(f"  z=1  EFC(eps=0.10,beta=1.0): {cddr_eta(np.array([1.0]), epsilon=0.10, beta=1.0)[0]:.6f}")

# ---- Window 3: Structural  S(z) ------------------------------------------
S_flat = np.ones_like(z)  # LCDM-like (no structure evolution)
S_efc = s_z_consistency(z, a_g=A_G, s0=1.0)

print("\n=== Window 3: Structural S(z) ===")
print(f"  z=3  LCDM: S=1.000")
print(f"  z=3  EFC:  S={s_z_consistency(np.array([3.0]))[0]:.4f}")

# ---- Line-integral demo ---------------------------------------------------
print("\n=== Full line-integral (Eq 1) ===")
N = 1000
lam = np.linspace(0, 1, N)
a_emit = 0.5  # corresponds to z~1
alpha_bg = np.full(N, np.log(1.0 / a_emit))  # LCDM background

# Construct a toy S_eff profile with a gradient bump
s_flow = np.ones(N)
s_lat = 0.3 * np.exp(-((lam - 0.5) / 0.1) ** 2)  # structure bump
xi_val = 0.4
seff_profile = s_eff(s_flow, s_lat, xi=xi_val)
k_grad = np.gradient(seff_profile, lam)

ln1z_efc = redshift_integral(lam, alpha_bg, seff_profile, k_grad, a_g=A_G)
ln1z_lcdm = redshift_integral(lam, alpha_bg, seff_profile, np.zeros(N), a_g=A_G)
z_efc = np.exp(ln1z_efc) - 1.0
z_lcdm_val = np.exp(ln1z_lcdm) - 1.0
print(f"  z_LCDM (grad=0): {z_lcdm_val:.6f}")
print(f"  z_EFC  (with structure): {z_efc:.6f}")
print(f"  Delta z / z_LCDM: {(z_efc - z_lcdm_val)/z_lcdm_val*100:.4f} %")

# ---- Regime projections summary -------------------------------------------
print(f"\n=== Regime projections (Table 1) ===")
print(f"  a_G   = {A_G}")
print(f"  a_H0  = a_G/2 = {A_H0}")
print(f"  a_c   = a_G/4 = {A_C}")
print(f"  MOND g/a0 ratio ~ {MOND_RATIO} (open tension)")
print(f"  C_eff(k=0.1) = {c_eff(np.array([0.1]))[0]:.4f}")

# ---- Optional plot --------------------------------------------------------
try:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    # W1
    ax = axes[0]
    ax.plot(z, T_lcdm, 'k-', label=r'$\Lambda$CDM')
    ax.plot(z, T_efc_mild, 'b--', label=r'EFC $\delta_S=0.5$')
    ax.plot(z, T_efc_strong, 'r:', label=r'EFC $\delta_S=2.0$')
    ax.set_xlabel('z'); ax.set_ylabel(r'$T_{CMB}$ [K]')
    ax.set_title('Window 1: Thermal'); ax.legend()

    # W2
    ax = axes[1]
    ax.axhline(1.0, color='k', label=r'$\Lambda$CDM')
    ax.plot(z, eta_efc1, 'b--', label=r'$\epsilon=0.05,\beta=0.5$')
    ax.plot(z, eta_efc2, 'r:', label=r'$\epsilon=0.10,\beta=1.0$')
    ax.set_xlabel('z'); ax.set_ylabel(r'$\eta(z)$')
    ax.set_title('Window 2: Geometric CDDR'); ax.legend()

    # W3
    ax = axes[2]
    ax.axhline(1.0, color='k', label=r'$\Lambda$CDM')
    ax.plot(z, S_efc, 'b--', label=f'EFC $a_G={A_G}$')
    ax.set_xlabel('z'); ax.set_ylabel('S(z)')
    ax.set_title('Window 3: Structural'); ax.legend()

    plt.tight_layout()
    plt.savefig('efc_three_windows.png', dpi=150)
    print("\nPlot saved to efc_three_windows.png")
    plt.show()
except ImportError:
    print("\nmatplotlib not available – skipping plot.")
