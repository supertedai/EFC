"""demo_efc_compound_paper.py

Demonstration of EFC Parameter-Controlled Regime Transitions.
Reproduces the main results from Magnusson 2026.
"""
import numpy as np
import sys

try:
    from efc_compound_paper import (
        sigma_eff, find_crossover_z, mu_lensing, mu_growth, eta_lensing,
        gate_function, fsigma8_prediction, scan_K0, scan_amplitude,
        check_mu_consistency, bbks_transfer,
        P1_DEFAULTS, P2_DEFAULTS, P1_CROSSOVER_Z, P2_FSIGMA8_Z07,
    )
except ImportError:
    sys.path.insert(0, ".")
    from efc_compound_paper import *


def main():
    z = np.linspace(0.01, 2.0, 2000)

    # --- 1. Sigma_eff(z) profile and crossover ---
    print("=" * 60)
    print("1. Sigma_eff(z) sign-changing crossover (P1 prediction)")
    print("=" * 60)
    sig = sigma_eff(z)
    zc = find_crossover_z(z, sig)
    print(f"   Crossover redshift: z = {zc:.4f}")
    print(f"   Pre-registered target: z = {P1_CROSSOVER_Z} +/- 0.03")
    print(f"   Within tolerance: {abs(zc - P1_CROSSOVER_Z) < 0.03}")

    # --- 2. f*sigma8 prediction (P2) ---
    print(f"\n{'=' * 60}")
    print("2. f*sigma8(z=0.7) sealed prediction (P2)")
    print("=" * 60)
    fs8 = fsigma8_prediction(z=0.7)
    print(f"   f*sigma8(0.7) = {fs8:.4f}")
    print(f"   Sealed target: {P2_FSIGMA8_Z07} +/- 0.02")

    # --- 3. K0 scan: primary control parameter ---
    print(f"\n{'=' * 60}")
    print("3. K0 scan — kinetic stiffness as primary control")
    print("=" * 60)
    K0_vals = np.linspace(0.5, 4.0, 100)
    zc_K0 = scan_K0(K0_vals)
    valid = ~np.isnan(zc_K0)
    if valid.any():
        print(f"   K0 range: [{K0_vals[0]:.1f}, {K0_vals[-1]:.1f}]")
        print(f"   z_cross range: [{np.nanmin(zc_K0):.3f}, {np.nanmax(zc_K0):.3f}]")
        print(f"   Delta_z = {np.nanmax(zc_K0) - np.nanmin(zc_K0):.3f}")
        print(f"   Paper reports: Delta_z ~ 0.87")

    # --- 4. Amplitude scan ---
    print(f"\n{'=' * 60}")
    print("4. Amplitude scan — x50 rescaling of (alpha, V', gamma0)")
    print("=" * 60)
    scales = np.linspace(0.1, 5.0, 80)  # represents range within x50
    zc_amp = scan_amplitude(scales)
    valid_a = ~np.isnan(zc_amp)
    if valid_a.any():
        print(f"   Scale range: [{scales[0]:.1f}, {scales[-1]:.1f}]")
        print(f"   z_cross range: [{np.nanmin(zc_amp):.3f}, {np.nanmax(zc_amp):.3f}]")
        print(f"   Delta_z = {np.nanmax(zc_amp) - np.nanmin(zc_amp):.3f}")
        print(f"   Paper reports: Delta_z ~ 0.11")

    # --- 5. Cross-sector mu consistency ---
    print(f"\n{'=' * 60}")
    print("5. Cross-sector consistency: mu < 1 in both sectors")
    print("=" * 60)
    cons = check_mu_consistency(0.44)
    print(f"   z = {cons['z']}")
    print(f"   mu_P1 (lensing) = {cons['mu_P1_lensing']:.5f}")
    print(f"   mu_P2 (growth)  = {cons['mu_P2_growth']:.5f}")
    print(f"   Relative difference: {cons['relative_diff_pct']:.1f}%")
    print(f"   Both mu < 1 (entropic damping): {cons['both_less_than_1']}")
    print(f"   Paper reports: ~11% difference, same sign")

    # --- 6. BBKS transfer function ---
    print(f"\n{'=' * 60}")
    print("6. BBKS transfer function cross-validation")
    print("=" * 60)
    k = np.logspace(-3, 1, 500)
    T_k = bbks_transfer(k)
    print(f"   T(k=0.01) = {bbks_transfer(np.array([0.01]))[0]:.4f}")
    print(f"   T(k=0.1)  = {bbks_transfer(np.array([0.1]))[0]:.4f}")
    print(f"   T(k=1.0)  = {bbks_transfer(np.array([1.0]))[0]:.4f}")
    print(f"   Paper: sign-change robust under BBKS, shift < 0.06")

    # --- 7. Optional plot ---
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 2, figsize=(12, 9))
        fig.suptitle("EFC: Parameter-Controlled Regime Transitions", fontsize=13)

        # (a) Sigma_eff(z)
        ax = axes[0, 0]
        ax.plot(z, sig, "b-", lw=1.8, label=r"$\Sigma_{\rm eff}(z)$")
        ax.axhline(1.0, color="grey", ls="--", lw=0.8)
        ax.axvline(zc, color="r", ls=":", lw=1.2, label=f"crossover z={zc:.3f}")
        ax.set_xlabel("z"); ax.set_ylabel(r"$\Sigma_{\rm eff}$")
        ax.legend(fontsize=9); ax.set_title("(a) Lensing coupling")

        # (b) K0 scan
        ax = axes[0, 1]
        ax.plot(K0_vals[valid], zc_K0[valid], "k-", lw=1.5)
        ax.set_xlabel(r"$K_0$"); ax.set_ylabel(r"$z_{\rm cross}$")
        ax.set_title(r"(b) Crossover vs $K_0$")

        # (c) mu comparison
        ax = axes[1, 0]
        mu_p1 = mu_lensing(z)
        mu_p2 = mu_growth(z)
        ax.plot(z, mu_p1, "b-", lw=1.5, label="P1 lensing")
        ax.plot(z, mu_p2, "r--", lw=1.5, label="P2 growth")
        ax.axhline(1.0, color="grey", ls="--", lw=0.8)
        ax.set_xlabel("z"); ax.set_ylabel(r"$\mu(z)$")
        ax.legend(fontsize=9); ax.set_title(r"(c) $\mu(z)$: both sectors $<1$")

        # (d) Gate function
        ax = axes[1, 1]
        ax.plot(z, gate_function(z), "g-", lw=1.5)
        ax.axvline(P2_DEFAULTS["z_t"], color="r", ls=":", lw=1.2)
        ax.set_xlabel("z"); ax.set_ylabel(r"$\Theta(z)$")
        ax.set_title("(d) P2 gate function")

        plt.tight_layout()
        plt.savefig("efc_regime_transitions.png", dpi=150)
        print(f"\nPlot saved to efc_regime_transitions.png")
    except ImportError:
        print("\nMatplotlib not available — skipping plot.")

    print("\nDemo complete.")


if __name__ == "__main__":
    main()
