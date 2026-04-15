#!/usr/bin/env python
"""demo_efc_rubin_dp2_preregistration.py

Demonstrate the EFC pre-registered predictions for Rubin LSST DP2.
Imports the reference module and reproduces the key results + an optional plot.
"""

import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

from efc_rubin_dp2_preregistration import (
    regime_gate, mu_func, sigma_func, eta_func,
    s8_efc, delta_s8, xi_plus_ratio, sigma_at_zeff,
    delta_cl_over_cl, is_kc4_falsified,
    S8_LCDM, S8_FALSIFICATION_THRESHOLD,
    ALPHA_MU, ALPHA_SIGMA, ETA_Z0, Z_EFF,
)


def main() -> None:
    print("=" * 60)
    print("EFC Rubin DP2 Pre-Registered Predictions  (Magnusson 2026)")
    print("=" * 60)

    # Derived coupling constants
    print(f"\nDerived alpha_mu    = {ALPHA_MU:.4f}")
    print(f"Derived alpha_Sigma = {ALPHA_SIGMA:.4f}")

    # S8
    s8 = s8_efc()
    ds8 = delta_s8()
    print(f"\nS8^efc  = {s8:.3f}   (LCDM = {S8_LCDM:.3f},  Delta = {ds8:+.3f})")

    # Sigma and xi+ ratio at z_eff
    sig, sig_err = sigma_at_zeff()
    ratio, ratio_err = xi_plus_ratio()
    print(f"Sigma(z_eff={Z_EFF}) = {sig:.3f} +/- {sig_err:.3f}")
    print(f"xi+^efc / xi+^LCDM  = {ratio:.3f} +/- {ratio_err:.3f}")
    print(f"Delta Cl/Cl          = {delta_cl_over_cl()*100:.1f}%")

    # eta, mu at z=0
    print(f"\neta(z=0)  = {float(eta_func(1.0)):.3f}  (paper: 1.10)")
    print(f"mu(z_eff) = {float(mu_func(1.0/(1+Z_EFF))):.3f}  (paper: 0.97)")

    # Falsification test examples
    print("\n--- Falsification examples ---")
    for s8_obs, s8_err in [(0.810, 0.012), (0.850, 0.015), (0.790, 0.010)]:
        flag = is_kc4_falsified(s8_obs, s8_err)
        status = "FALSIFIED" if flag else "consistent"
        print(f"  S8_obs={s8_obs:.3f}+/-{s8_err:.3f}  =>  KC4 {status}")

    # ----- Optional plot -----
    if HAS_MPL:
        a_arr = np.linspace(0.1, 1.0, 500)
        z_arr = 1.0 / a_arr - 1.0

        fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

        # Panel 1: regime gate
        axes[0].plot(a_arr, regime_gate(a_arr), "k-", lw=2)
        axes[0].axvline(0.3, ls="--", color="grey", label=r"$a_t=0.3$")
        axes[0].set_xlabel("Scale factor $a$")
        axes[0].set_ylabel(r"$G(a)$")
        axes[0].set_title("EFC Regime Gate")
        axes[0].legend()

        # Panel 2: mu, Sigma, eta vs redshift
        axes[1].plot(z_arr, mu_func(a_arr), label=r"$\mu(z)$", lw=2)
        axes[1].plot(z_arr, sigma_func(a_arr), label=r"$\Sigma(z)$", lw=2)
        axes[1].plot(z_arr, eta_func(a_arr), label=r"$\eta(z)$", lw=2)
        axes[1].axhline(1.0, ls=":", color="grey")
        axes[1].set_xlabel("Redshift $z$")
        axes[1].set_title(r"Modified-gravity functions")
        axes[1].legend()
        axes[1].invert_xaxis()

        # Panel 3: lensing enhancement Sigma^2
        sig2 = sigma_func(a_arr) ** 2
        axes[2].plot(z_arr, sig2, "C3-", lw=2)
        axes[2].axhline(1.0, ls=":", color="grey", label=r"$\Lambda$CDM")
        axes[2].axhline(1.08, ls="--", color="C0", label="EFC prediction 1.08")
        axes[2].fill_between(z_arr, 1.04, 1.12, alpha=0.15, color="C0")
        axes[2].set_xlabel("Redshift $z$")
        axes[2].set_ylabel(r"$\Sigma^2(z)$  (lensing enhancement)")
        axes[2].set_title(r"$\xi_+$ ratio EFC / $\Lambda$CDM")
        axes[2].legend()
        axes[2].invert_xaxis()

        plt.tight_layout()
        fname = "efc_rubin_dp2_predictions.png"
        plt.savefig(fname, dpi=150)
        print(f"\nPlot saved to {fname}")

    print("\nDone.")


if __name__ == "__main__":
    main()
