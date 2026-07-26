"""demo_efc_r_sparc.py

Demonstration of the EFC-R-SPARC framework:
  - Build a toy galaxy with exponential disk density & entropy profile
  - Compute EFC rotation curve
  - Compare pure-Newtonian, EFC, and EFC-R (with latent field)
  - Classify regime and compute latent-field proxy
  - Optionally plot results
"""
import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

from efc_r_sparc import (
    exponential_disk_density,
    entropy_profile,
    energy_flow_field,
    rotation_velocity_efc,
    rotation_velocity_efc_r,
    latent_field_proxy,
    classify_regime,
    chi_squared,
    G_SI, KPC_TO_M, SPEARMAN_RHO, SPEARMAN_P,
    LATENT_THRESHOLD, N_GALAXIES,
)


def newtonian_rotation(r_kpc, rho):
    """Simple Newtonian V_circ from spherical mass shells."""
    r_m = r_kpc * KPC_TO_M
    integrand = 4.0 * np.pi * r_m**2 * rho
    M_enc = np.cumsum(integrand * np.gradient(r_m))
    v2 = G_SI * M_enc / r_m
    return np.sqrt(np.maximum(v2, 0)) / 1e3


def main():
    # --- synthetic "observed" flat rotation curve (mimics LSB galaxy) ---
    r = np.linspace(0.5, 25.0, 100)
    v_flat = 80.0  # km/s
    v_obs = v_flat * np.tanh(r / 3.0) + np.random.default_rng(42).normal(0, 2, len(r))
    v_err = np.full_like(r, 3.0)

    # --- density and entropy ---
    Sigma0 = 2.5e-22   # kg m^-3 proxy
    Rd = 3.5            # kpc
    rho = exponential_disk_density(r, Sigma0, Rd)
    S = entropy_profile(r, S0=0.02, r_s=6.0, alpha=1.2)

    # --- velocities ---
    v_newton = newtonian_rotation(r, rho)
    v_efc = rotation_velocity_efc(r, rho, S)

    # Add a small latent field for EFC-R demo (barred spiral proxy)
    E_latent = 0.15 * Sigma0 * np.exp(-((r - 8.0)**2) / (2 * 3.0**2))
    v_efc_r = rotation_velocity_efc_r(r, rho, S, E_latent)

    # --- chi-squared ---
    chi2_newton = chi_squared(v_obs, v_newton, v_err)
    chi2_efc = chi_squared(v_obs, v_efc, v_err)
    chi2_efc_r = chi_squared(v_obs, v_efc_r, v_err)

    # --- latent proxy & regime ---
    L = latent_field_proxy(chi2_efc, chi2_newton)
    regime = classify_regime(L)

    # --- report ---
    print("="*60)
    print("EFC-R-SPARC  Demonstration")
    print("="*60)
    print(f"Radial range       : {r[0]:.1f} - {r[-1]:.1f} kpc  ({len(r)} pts)")
    print(f"Chi2 Newtonian     : {chi2_newton:.2f}")
    print(f"Chi2 EFC           : {chi2_efc:.2f}")
    print(f"Chi2 EFC-R         : {chi2_efc_r:.2f}")
    print(f"Latent proxy L     : {L:.4f}")
    print(f"Regime             : {regime}")
    print(f"Threshold used     : {LATENT_THRESHOLD}")
    print(f"\nPaper statistics (N={N_GALAXIES} SPARC galaxies):")
    print(f"  Spearman rho     = {SPEARMAN_RHO}")
    print(f"  Spearman p-value = {SPEARMAN_P}")
    print("="*60)

    # --- plot ---
    if HAS_MPL:
        fig, axes = plt.subplots(1, 2, figsize=(13, 5))

        ax = axes[0]
        ax.errorbar(r, v_obs, yerr=v_err, fmt='o', ms=3, color='grey',
                    label='Observed (synthetic)', alpha=0.6)
        ax.plot(r, v_newton, '--', label='Newtonian', lw=2)
        ax.plot(r, v_efc, '-', label='EFC', lw=2)
        ax.plot(r, v_efc_r, '-', label='EFC-R', lw=2)
        ax.set_xlabel('r  [kpc]')
        ax.set_ylabel('V_rot  [km/s]')
        ax.set_title('Rotation Curves')
        ax.legend()
        ax.set_ylim(0, None)

        ax2 = axes[1]
        E_f = energy_flow_field(rho, S)
        ax2.semilogy(r, rho, label=r'$\rho$', lw=2)
        ax2.semilogy(r, E_f, label=r'$E_f = \rho(1-S)$', lw=2)
        ax2.semilogy(r, E_latent, label=r'$E_{\rm latent}$', lw=2, ls='--')
        ax2.set_xlabel('r  [kpc]')
        ax2.set_ylabel('Energy density proxy')
        ax2.set_title('EFC-R Energy Decomposition')
        ax2.legend()

        plt.tight_layout()
        plt.savefig('efc_r_sparc_demo.png', dpi=150)
        print("\nPlot saved to efc_r_sparc_demo.png")
    else:
        print("\nMatplotlib not available; skipping plot.")


if __name__ == "__main__":
    main()
