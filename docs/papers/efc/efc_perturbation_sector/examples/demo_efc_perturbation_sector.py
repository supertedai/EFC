"""demo_efc_perturbation_sector.py

Demonstration script for the EFC Perturbation Sector lensing crossover
prediction.  Imports the reference module, computes Sigma_eff/Sigma_CDM
across redshift, locates the crossover, and optionally generates a
reproduction of the paper's key figure.
"""

import numpy as np

from efc_perturbation_sector import (
    sigma_eff_ratio,
    sigma_eff_ratio_efc,
    crossover_redshift,
    Z_CROSSOVER,
    TOLERANCE_BAND,
)


def main() -> None:
    # ----- Numerical results -----
    z = np.linspace(0.05, 1.5, 300)
    ratio_efc = sigma_eff_ratio_efc(z)       # full EFC (alpha=0)
    ratio_lcdm = sigma_eff_ratio(z, alpha=1.0)  # LCDM

    z_cross = crossover_redshift(alpha=0.0)
    print("EFC Lensing Crossover Prediction")
    print("=" * 40)
    print(f"Crossover redshift z_cross = {z_cross:.4f}  (paper: {Z_CROSSOVER})")
    print(f"Peak enhancement          = {(ratio_efc.max()-1)*100:+.2f}%  at z ~ {z[np.argmax(ratio_efc)]:.2f}")
    print(f"Maximum suppression       = {(ratio_efc.min()-1)*100:+.2f}%  at z ~ {z[np.argmin(ratio_efc)]:.2f}")
    print(f"Tolerance band            = +/-{TOLERANCE_BAND*100:.0f}%")
    print()

    # Print a small table
    z_table = np.array([0.2, 0.3, 0.42, 0.6, 0.8, 1.0, 1.2, 1.4])
    print(f"{'z':>6s}  {'Sigma_eff/Sigma_CDM':>20s}  {'deviation':>10s}")
    print("-" * 42)
    for zi in z_table:
        ri = sigma_eff_ratio_efc(float(zi))
        print(f"{zi:6.2f}  {ri:20.5f}  {(ri-1)*100:+10.3f}%")

    # ----- Optional plot -----
    try:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(7, 4.5))

        # Tolerance band
        ax.axhspan(1.0 - TOLERANCE_BAND, 1.0 + TOLERANCE_BAND,
                   color="gray", alpha=0.12, label=r"$\pm 2\%$ band")

        # LCDM
        ax.axhline(1.0, color="black", ls="--", lw=0.8, label=r"$\Lambda$CDM ($\alpha=1$)")

        # EFC curve
        ax.plot(z, ratio_efc, color="royalblue", lw=2.2, label="EFC $\\Sigma_{\\rm eff}(z)$")

        # Crossover marker
        ax.plot(z_cross, 1.0, "o", color="crimson", ms=8, zorder=5,
                label=f"crossover $z \\approx {z_cross:.2f}$")

        # Annotations matching the paper
        ax.annotate("enhanced\nlensing", xy=(0.18, 1.012), fontsize=9,
                    color="green", ha="center")
        ax.annotate("suppressed\nlensing", xy=(1.1, 0.984), fontsize=9,
                    color="red", ha="center")
        ax.annotate("crossover", xy=(z_cross, 1.0),
                    xytext=(z_cross + 0.15, 1.015),
                    arrowprops=dict(arrowstyle="->", color="crimson"),
                    fontsize=9, color="crimson")

        # Data-point annotations from the paper
        annots = {
            0.2: "+0.8%", 0.6: "-0.3%", 0.8: "-0.9%",
            1.0: "-1.2%", 1.2: "-1.4%", 1.4: "-1.4%",
        }
        for za, txt in annots.items():
            ra = float(sigma_eff_ratio_efc(za))
            ax.annotate(txt, xy=(za, ra), fontsize=7,
                        textcoords="offset points", xytext=(8, -2))

        ax.set_xlabel("Redshift $z$", fontsize=12)
        ax.set_ylabel(r"$\Sigma_{\rm eff}(z) / \Sigma_{\Lambda{\rm CDM}}$",
                      fontsize=12)
        ax.set_title("EFC Lensing Crossover Prediction", fontsize=13)
        ax.set_xlim(0.05, 1.55)
        ax.set_ylim(0.975, 1.035)
        ax.legend(loc="upper right", fontsize=9)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        plt.savefig("efc_lensing_crossover.png", dpi=150)
        print("\nPlot saved to efc_lensing_crossover.png")
        plt.show()

    except ImportError:
        print("\nmatplotlib not available – skipping plot.")


if __name__ == "__main__":
    main()
