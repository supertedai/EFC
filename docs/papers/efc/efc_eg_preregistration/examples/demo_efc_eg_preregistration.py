#!/usr/bin/env python
"""demo_efc_eg_preregistration.py

Demonstration script for the EFC EG pre-registration reference implementation.
Runs the key calculations and optionally produces a diagnostic figure.
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
    MU0, SIGMA0, EG_RATIO_CENTRAL, EG_RATIO_SIGMA,
    KC_EG_PASS_LO, KC_EG_PASS_HI, MU_RANGE, SIGMA_RANGE, ZEFF,
    eg_gr, eg_efc_prediction, eg_ratio_mg, survival_valley_scan,
    evaluate_pass_fail,
)


def main() -> None:
    omega_m0 = 0.3111  # Planck 2018

    # --- 1. Central prediction -------------------------------------------------
    ratio, eg_gr_val = eg_efc_prediction(mu=MU0, sigma=SIGMA0, omega_m0=omega_m0)
    eg_efc_val = ratio * eg_gr_val
    print("=" * 60)
    print("EFC EG Pre-Registration — Key Results")
    print("=" * 60)
    print(f"  Pivot redshift z_eff          = {ZEFF}")
    print(f"  mu0 = {MU0},  Sigma0 = {SIGMA0}")
    print(f"  E_G^{{GR}}(z={ZEFF})            = {eg_gr_val:.5f}")
    print(f"  E_G^{{EFC}} / E_G^{{GR}}         = {ratio:.4f}")
    print(f"  Paper prediction               = {EG_RATIO_CENTRAL} +/- {EG_RATIO_SIGMA}")
    print(f"  E_G^{{EFC}}(z={ZEFF})            = {eg_efc_val:.5f}")
    print()

    # --- 2. Survival valley scan -----------------------------------------------
    sv = survival_valley_scan(n=300, omega_m0=omega_m0)
    print("Survival-valley scan (mu in [{:.2f},{:.2f}], Sigma in [{:.2f},{:.2f}]):".format(
        *MU_RANGE, *SIGMA_RANGE))
    print(f"  mean = {sv['mean']:.4f},  std = {sv['std']:.4f}")
    print(f"  range = [{sv['min']:.4f}, {sv['max']:.4f}]")
    print()

    # --- 3. Pass / fail for hypothetical observations --------------------------
    print("Hypothetical observation scenarios:")
    scenarios = [
        ("Consistent with EFC", 1.09, 0.04),
        ("Consistent with GR",  1.00, 0.03),
        ("High outlier",        1.20, 0.05),
        ("Marginal",            1.04, 0.05),
    ]
    for label, obs_r, obs_s in scenarios:
        pf = evaluate_pass_fail(obs_r, obs_s)
        tag = "PASS" if pf["KC_EG_PASS"] else "FAIL"
        print(f"  {label:25s}  ratio={obs_r:.2f}+/-{obs_s:.2f}  => {tag}")
    print()

    # --- 4. Redshift dependence ------------------------------------------------
    zs = np.linspace(0.1, 1.5, 80)
    eg_gr_arr = np.array([eg_gr(omega_m0, z) for z in zs])
    eg_efc_arr = np.array([eg_ratio_mg(MU0, SIGMA0, omega_m0=omega_m0, z=z) * eg_gr(omega_m0, z)
                           for z in zs])

    # --- 5. Plot (optional) ----------------------------------------------------
    if HAS_MPL:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Left panel: E_G(z)
        ax = axes[0]
        ax.plot(zs, eg_gr_arr, "k--", lw=1.5, label=r"$E_G^{\rm GR}$")
        ax.plot(zs, eg_efc_arr, "C0-", lw=2, label=r"$E_G^{\rm EFC}$")
        ax.axvline(ZEFF, color="grey", ls=":", lw=0.8)
        ax.set_xlabel("Redshift $z$")
        ax.set_ylabel(r"$E_G(z)$")
        ax.legend()
        ax.set_title(r"$E_G$ vs redshift")

        # Right panel: survival valley heat-map
        ax = axes[1]
        n_grid = 200
        mus = np.linspace(MU_RANGE[0], MU_RANGE[1], n_grid)
        sigs = np.linspace(SIGMA_RANGE[0], SIGMA_RANGE[1], n_grid)
        MU, SIG = np.meshgrid(mus, sigs)
        RATIO = np.vectorize(lambda m, s: eg_ratio_mg(m, s, omega_m0=omega_m0, z=ZEFF))(MU, SIG)
        im = ax.contourf(MU, SIG, RATIO, levels=30, cmap="RdYlBu_r")
        cb = fig.colorbar(im, ax=ax)
        cb.set_label(r"$E_G^{\rm EFC}/E_G^{\rm GR}$")
        ax.plot(MU0, SIGMA0, "k*", ms=12, label="Central")
        # Pass window contours
        ax.contour(MU, SIG, RATIO, levels=[KC_EG_PASS_LO, KC_EG_PASS_HI],
                   colors="white", linewidths=1.5, linestyles="--")
        ax.set_xlabel(r"$\mu$")
        ax.set_ylabel(r"$\Sigma$")
        ax.set_title("Survival valley")
        ax.legend()

        fig.tight_layout()
        fig.savefig("efc_eg_preregistration_demo.png", dpi=150)
        print("Figure saved to efc_eg_preregistration_demo.png")
    else:
        print("(matplotlib not available — skipping plot)")

    print("\nDone.")


if __name__ == "__main__":
    main()
