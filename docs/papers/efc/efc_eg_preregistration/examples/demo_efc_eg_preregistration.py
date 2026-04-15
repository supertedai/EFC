"""demo_efc_eg_preregistration.py

Demonstrates the EFC EG pre-registration prediction, scans the
survival valley, and optionally produces a diagnostic plot.

Usage:
    python demo_efc_eg_preregistration.py
"""

import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

from efc_eg_preregistration import (
    MU0, SIGMA0, ETA0, MU_RANGE, SIGMA_RANGE,
    EG_RATIO_CENTRAL, EG_RATIO_SIGMA,
    KC_EG_PASS_LO, KC_EG_PASS_HI, ZEFF,
    eg_ratio_efc, eg_ratio_mg, eg_gr,
    eg_ratio_uncertainty, evaluate_pass_fail,
    omega_m_z, growth_rate_gr,
)


def main() -> None:
    omega_m0 = 0.315  # Planck 2018

    print("=" * 62)
    print("  EFC EG Pre-Registration  —  Reference Calculation")
    print("=" * 62)

    # ---- 1. Central prediction -------------------------------------------
    ratio_central = eg_ratio_efc()
    print(f"\n[Eq. 7]  EG^EFC / EG^GR  = {ratio_central:.4f}")
    print(f"         Paper value      = {EG_RATIO_CENTRAL} ± {EG_RATIO_SIGMA}")
    print(f"         Frozen params    : mu0={MU0}, Sigma0={SIGMA0}, eta0={ETA0}")

    # ---- 2. GR baseline --------------------------------------------------
    eg_gr_val = eg_gr(omega_m0, ZEFF)
    f_gr = growth_rate_gr(omega_m0, ZEFF)
    om_z = omega_m_z(omega_m0, ZEFF)
    print(f"\n[GR baseline at z_eff={ZEFF}]")
    print(f"  Omega_m(z)  = {om_z:.4f}")
    print(f"  f(z)        = {f_gr:.4f}")
    print(f"  EG^GR       = {eg_gr_val:.4f}")

    eg_efc_abs = eg_gr_val * ratio_central
    print(f"  EG^EFC      = {eg_efc_abs:.4f}")

    # ---- 3. Survival-valley scan -----------------------------------------
    print("\n[Survival valley scan]")
    mu_arr = np.linspace(MU_RANGE[0], MU_RANGE[1], 50)
    sigma_arr = np.linspace(SIGMA_RANGE[0], SIGMA_RANGE[1], 50)
    MU, SIG = np.meshgrid(mu_arr, sigma_arr)
    RATIO = SIG / MU

    mc_mean, mc_std = eg_ratio_uncertainty(n_samples=100_000)
    print(f"  MC mean = {mc_mean:.4f},  MC std = {mc_std:.4f}")
    print(f"  Grid min = {RATIO.min():.4f},  max = {RATIO.max():.4f}")

    # ---- 4. Redshift dependence ------------------------------------------
    print("\n[Redshift dependence of EG^GR]")
    zs = np.array([0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
    for z in zs:
        eg_val = eg_gr(omega_m0, z)
        eg_efc_val = eg_val * ratio_central
        print(f"  z={z:.1f}:  EG^GR={eg_val:.4f}   EG^EFC={eg_efc_val:.4f}")

    # ---- 5. Pass / fail demonstration ------------------------------------
    print("\n[Pass/Fail criterion application]")
    test_cases = [
        (1.09, 0.04, "mock consistent"),
        (1.00, 0.02, "mock GR-like"),
        (1.20, 0.05, "mock high"),
        (1.086, 0.03, "exact EFC"),
    ]
    for val, sig, label in test_cases:
        res = evaluate_pass_fail(val, sig)
        print(f"  {label:20s}:  ratio={val:.3f} ± {sig:.3f}  => {res['status']}")

    # ---- 6. Optional plot ------------------------------------------------
    if HAS_MPL:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Panel A: survival-valley contour
        ax = axes[0]
        cf = ax.contourf(MU, SIG, RATIO, levels=20, cmap="RdYlBu_r")
        ax.contour(MU, SIG, RATIO, levels=[KC_EG_PASS_LO, EG_RATIO_CENTRAL, KC_EG_PASS_HI],
                   colors=["green", "black", "green"], linewidths=[1.5, 2, 1.5],
                   linestyles=["--", "-", "--"])
        ax.plot(MU0, SIGMA0, "k*", markersize=14, label="Central EFC")
        ax.set_xlabel(r"$\mu$")
        ax.set_ylabel(r"$\Sigma$")
        ax.set_title(r"$E_G^{\rm EFC}/E_G^{\rm GR}$ in survival valley")
        ax.legend()
        plt.colorbar(cf, ax=ax, label=r"$E_G$ ratio")

        # Panel B: EG vs redshift
        ax = axes[1]
        z_fine = np.linspace(0.1, 1.2, 200)
        eg_gr_arr = np.array([eg_gr(omega_m0, z) for z in z_fine])
        eg_efc_arr = eg_gr_arr * ratio_central
        ax.fill_between(z_fine, eg_efc_arr * (1 - EG_RATIO_SIGMA / ratio_central),
                         eg_efc_arr * (1 + EG_RATIO_SIGMA / ratio_central),
                         alpha=0.3, color="C1", label="EFC ±1σ")
        ax.plot(z_fine, eg_gr_arr, "k-", lw=2, label=r"$\Lambda$CDM (GR)")
        ax.plot(z_fine, eg_efc_arr, "C1-", lw=2, label="EFC")
        ax.axvline(ZEFF, ls=":", color="grey", label=f"$z_{{\\rm eff}}={ZEFF}$")
        ax.set_xlabel("Redshift $z$")
        ax.set_ylabel(r"$E_G(z)$")
        ax.set_title(r"$E_G$ prediction: EFC vs $\Lambda$CDM")
        ax.legend(fontsize=9)

        plt.tight_layout()
        fname = "efc_eg_prediction.png"
        fig.savefig(fname, dpi=150)
        print(f"\nPlot saved to {fname}")
    else:
        print("\n(matplotlib not available — skipping plot)")

    print("\nDone.")


if __name__ == "__main__":
    main()
