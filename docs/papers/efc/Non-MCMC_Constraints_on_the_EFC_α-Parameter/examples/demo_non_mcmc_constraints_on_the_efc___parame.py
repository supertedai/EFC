"""demo_non_mcmc_constraints_on_the_efc___parame.py

Demonstration script reproducing the key results from EFC-VAL-2026-005.
Runs standalone; generates a summary plot if matplotlib is available.
"""
import numpy as np
import sys

from non_mcmc_constraints_on_the_efc___parame import (
    H_lcdm, H_efc, fsigma8_lcdm, fsigma8_efc,
    delta_chi2, delta_aic, kfold_cv, loo_cv,
    significance_sigma, tension_sigma,
    ALPHA_FS8, ALPHA_FS8_ERR, ALPHA_MCMC, ALPHA_MCMC_ERR,
    ALPHA_BLIND_PRED_1, ALPHA_BLIND_PRED_2,
    DCHI2_DESI, DCHI2_BOSS, DCHI2_CC, DAIC_FS8,
    H0_FIDUCIAL, SIGMA8_FIDUCIAL
)


def main():
    print("=" * 65)
    print("EFC-VAL-2026-005  Non-MCMC constraints on alpha — Demo")
    print("=" * 65)

    # --- Section 1: Reproduce reported significance values ---
    sig_fs8 = significance_sigma(ALPHA_FS8, ALPHA_FS8_ERR)
    sig_mcmc = significance_sigma(ALPHA_MCMC, ALPHA_MCMC_ERR)
    print(f"\n[Growth rate] alpha = {ALPHA_FS8} +/- {ALPHA_FS8_ERR}  "
          f"=> {sig_fs8:.2f} sigma  (paper: 2.20 sigma)")
    print(f"[MCMC]        alpha = {ALPHA_MCMC} +/- {ALPHA_MCMC_ERR}  "
          f"=> {sig_mcmc:.3f} sigma (paper: 0.479 sigma)")

    # --- Section 2: Tension with blind predictions ---
    for i, bp in enumerate([ALPHA_BLIND_PRED_1, ALPHA_BLIND_PRED_2], 1):
        t_fs8 = tension_sigma(ALPHA_FS8, ALPHA_FS8_ERR, bp, 0.0)
        t_mcmc = tension_sigma(ALPHA_MCMC, ALPHA_MCMC_ERR, bp, 0.0)
        print(f"\nBlind prediction {i} (alpha={bp}):")
        print(f"  fs8 tension:  {t_fs8:.2f} sigma  (paper: ~0.7 sigma)")
        print(f"  MCMC tension: {t_mcmc:.2f} sigma  (paper: ~2.8 sigma)")

    # --- Section 3: Delta-chi2 summary ---
    print("\n--- Reported Delta-chi2 values (negative = EFC preferred) ---")
    print(f"  DESI Y1 BAO:           {DCHI2_DESI:+.2f}")
    print(f"  BOSS DR12 BAO:         {DCHI2_BOSS:+.2f}")
    print(f"  Cosmic chronometers:   {DCHI2_CC:+.2f}")
    print(f"  f*sigma8 Delta-AIC:    {DAIC_FS8:+.2f}")

    # --- Section 4: Synthetic demo — generate mock fs8 data and run LOO ---
    np.random.seed(2026)
    z_mock = np.array([0.15, 0.32, 0.44, 0.60, 0.73, 0.85, 1.05])
    fs8_true = fsigma8_efc(z_mock, alpha=ALPHA_FS8)
    errors = 0.04 * np.ones_like(z_mock)
    fs8_obs = fs8_true + np.random.normal(0, errors)

    loo_wins, loo_total = loo_cv(z_mock, fs8_obs, errors,
                                  alpha=ALPHA_FS8, observable="fsigma8")
    print(f"\n--- Synthetic LOO demo ({len(z_mock)} epochs) ---")
    print(f"  LOO epochs preferring EFC: {loo_wins}/{loo_total}  "
          f"(paper: 7/7)")

    dc2 = delta_chi2(z_mock, fs8_obs, errors, ALPHA_FS8, "fsigma8")
    daic = delta_aic(dc2, k_eff_efc=1, k_eff_lcdm=0)
    print(f"  Synthetic Delta-chi2: {dc2:+.2f}")
    print(f"  Synthetic Delta-AIC:  {daic:+.2f}")

    # --- Section 5: Optional plot ---
    try:
        import matplotlib.pyplot as plt
        z_plot = np.linspace(0.01, 2.0, 200)
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        ax = axes[0]
        ax.plot(z_plot, H_lcdm(z_plot), 'k-', label=r'$\Lambda$CDM')
        ax.plot(z_plot, H_efc(z_plot, ALPHA_FS8), 'r--',
                label=rf'EFC $\alpha={ALPHA_FS8}$')
        ax.set_xlabel('z'); ax.set_ylabel('H(z) [km/s/Mpc]')
        ax.set_title('Hubble parameter'); ax.legend()

        ax = axes[1]
        ax.plot(z_plot, fsigma8_lcdm(z_plot), 'k-', label=r'$\Lambda$CDM')
        ax.plot(z_plot, fsigma8_efc(z_plot, ALPHA_FS8), 'r--',
                label=rf'EFC $\alpha={ALPHA_FS8}$')
        ax.errorbar(z_mock, fs8_obs, yerr=errors, fmt='bo', ms=5,
                    label='Mock data')
        ax.set_xlabel('z'); ax.set_ylabel(r'$f\sigma_8(z)$')
        ax.set_title('Growth rate'); ax.legend()

        plt.suptitle('EFC-VAL-2026-005: Non-MCMC constraints on α',
                     fontsize=13)
        plt.tight_layout()
        plt.savefig('efc_val_2026_005_demo.png', dpi=150)
        print("\nPlot saved: efc_val_2026_005_demo.png")
        plt.show()
    except ImportError:
        print("\n(matplotlib not available — skipping plot)")

    print("\nDone.")


if __name__ == "__main__":
    main()
