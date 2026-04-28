#!/usr/bin/env python
"""demo_efc_val_2026_006.py

Demonstration of the key results in EFC-VAL-2026-006.
Runs standalone; generates a summary table and an optional plot.
"""
import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

from efc_val_2026_006 import (
    DESI_DR1_DELTA_CHI2, BOSS_DR12_DELTA_CHI2,
    FS8_LOO_ALPHA_STUB, G2_PPC_PVALUE,
    binomial_bias_test, classify_result,
    growth_source_variant_h, init_walkers,
    log_prior_variant_h, ALPHA_PRIOR_NEW, MU_CLAMP_NEW,
)


def main() -> None:
    print("=" * 65)
    print("EFC-VAL-2026-006  Reference Implementation Demo")
    print("DOI: 10.6084/m9.figshare.32114530")
    print("=" * 65)

    # --- Table 2 reproduction: Re-evaluation of five VAL-005 results ---
    print("\n--- Re-evaluation of VAL-005 results under real data ---\n")
    results = [
        ("DESI Y1 Δχ²", DESI_DR1_DELTA_CHI2, 0.0),
        ("BOSS DR12 Δχ²", BOSS_DR12_DELTA_CHI2, BOSS_DR12_DELTA_CHI2),
    ]
    print(f"{'Probe':<20} {'Stub value':>12} {'Real value':>12} {'Status (real)':>16}")
    print("-" * 62)
    for name, stub_val, real_val in results:
        status = classify_result(real_val)
        print(f"{name:<20} {stub_val:>12.2f} {real_val:>12.2f} {status:>16}")
    print(f"{'fσ8 LOO α':<20} {FS8_LOO_ALPHA_STUB[0]:>+7.2f}±{FS8_LOO_ALPHA_STUB[1]:.2f}{'':>3} {'broadened':>12} {'W3 watchlist':>16}")

    # --- Binomial bias test ---
    p = binomial_bias_test()
    print(f"\nBinomial bias test (5/5 null-directed): p = {p:.5f}")

    # --- VariantH growth source curve ---
    a_grid = np.linspace(0.2, 1.0, 200)
    s0_values = [0.1, 0.0, -0.1]  # positive, null, suppression
    mu_val = 2.0

    print("\n--- VariantH growth-source S(a) = S0_bar * a^mu ---")
    print(f"    Prior on S0_bar: U{ALPHA_PRIOR_NEW}")
    print(f"    mu clamp:        {MU_CLAMP_NEW}")
    for s0 in s0_values:
        S = growth_source_variant_h(a_grid, s0, mu_val)
        tag = "enhancement" if s0 > 0 else ("null" if s0 == 0 else "suppression")
        print(f"    S0_bar={s0:+.2f} ({tag}): S(a=1)={S[-1]:+.4f}")

    # --- G2 open issue ---
    print(f"\nG2 open issue: PPC growth p-value = {G2_PPC_PVALUE}")
    print("  → Root cause unresolved; corrigendum is explicitly interim.")

    # --- Walker initialisation check ---
    p0 = init_walkers(64)
    neg_frac = np.mean(p0[:, 3] < 0)
    print(f"\nWalker init S0_bar: {neg_frac*100:.0f}% negative, "
          f"{(1-neg_frac)*100:.0f}% positive (expect ~50/50)")

    # --- Prior boundary check ---
    inside  = log_prior_variant_h(0.3)
    outside = log_prior_variant_h(0.6)
    print(f"Prior check: log_prior(0.3) = {inside}, log_prior(0.6) = {outside}")

    # --- Optional plot ---
    if HAS_MPL:
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

        # Panel 1: growth source curves
        ax = axes[0]
        for s0, ls in zip(s0_values, ["-", "--", "-."]):
            S = growth_source_variant_h(a_grid, s0, mu_val)
            label = f"$\\bar{{S}}_0 = {s0:+.1f}$"
            ax.plot(a_grid, S, ls, label=label)
        ax.axhline(0, color="grey", lw=0.5)
        ax.set_xlabel("Scale factor $a$")
        ax.set_ylabel("Growth source $S(a)$")
        ax.set_title("VariantH growth source (μ = 2)")
        ax.legend(fontsize=9)

        # Panel 2: Δχ² bar chart (stub vs real)
        ax = axes[1]
        labels = ["DESI Y1\n(stub DR1)", "DESI Y1\n(real DR2)", "BOSS DR12"]
        values = [DESI_DR1_DELTA_CHI2, 0.0, BOSS_DR12_DELTA_CHI2]
        colors = ["#d62728", "#2ca02c", "#1f77b4"]
        ax.bar(labels, values, color=colors, edgecolor="k", width=0.5)
        ax.axhline(0, color="grey", lw=0.5)
        ax.set_ylabel(r"$\Delta\chi^2$")
        ax.set_title("Stub → Real data transition")
        for i, v in enumerate(values):
            ax.text(i, v - 1.2 if v < 0 else v + 0.5, f"{v:.2f}",
                    ha="center", fontsize=9)

        fig.tight_layout()
        fig.savefig("efc_val_2026_006_demo.png", dpi=150)
        print("\nPlot saved: efc_val_2026_006_demo.png")
    else:
        print("\n(matplotlib not available — skipping plot)")

    print("\nDone.")


if __name__ == "__main__":
    main()
