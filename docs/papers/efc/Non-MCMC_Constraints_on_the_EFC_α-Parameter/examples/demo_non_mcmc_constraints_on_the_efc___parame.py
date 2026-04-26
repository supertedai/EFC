# demo_non_mcmc_constraints_on_the_efc___parame.py
from __future__ import annotations

import json
from typing import List

import numpy as np

from non_mcmc_constraints_on_the_efc___parame import (
    paper_summary,
    combine_independent_delta_chi2,
    DELTA_CHI2_DESI_Y1,
    DELTA_CHI2_BOSS_DR12,
    DELTA_CHI2_CC_HZ,
    ALPHA_FS8_MEAN,
    ALPHA_FS8_SIGMA,
    significance_z,
    delta_aic,
)


def main() -> None:
    s = paper_summary()

    # Print core reported metrics
    print("Paper summary (EFC-VAL-2026-005):")
    print(json.dumps(s, indent=2))

    # Demonstrate combination of independent Delta chi^2 values
    deltas = [DELTA_CHI2_DESI_Y1, DELTA_CHI2_BOSS_DR12, DELTA_CHI2_CC_HZ]
    combined = combine_independent_delta_chi2(deltas)
    print(f"\nCombined Delta chi^2 (BAO + H(z)): {combined:.2f}")

    # Recompute z-score for the fs8 alpha indication
    z = significance_z(ALPHA_FS8_MEAN, ALPHA_FS8_SIGMA)
    print(f"fs8 alpha indication: alpha = {ALPHA_FS8_MEAN:.2f} ± {ALPHA_FS8_SIGMA:.2f} -> z = {z:.2f}")

    # Show how Delta AIC would be computed from chi^2 and parameter counts
    # (illustrative: here we take the BOSS case where keff=0, so Delta AIC == Delta chi^2)
    delta_aic_boss = delta_aic(chi2_model=0.0, k_model=0, chi2_reference=-DELTA_CHI2_BOSS_DR12, k_reference=0)
    print(f"Delta AIC (BOSS, keff=0): {delta_aic_boss:.2f} (equals Delta chi^2)")

    # Optional plotting (if matplotlib is available)
    try:
        import matplotlib.pyplot as plt

        labels: List[str] = ["DESI Y1 BAO", "BOSS DR12 BAO", "H(z)"]
        vals = [DELTA_CHI2_DESI_Y1, DELTA_CHI2_BOSS_DR12, DELTA_CHI2_CC_HZ]
        colors = ["tab:blue" if v < 0 else "tab:red" for v in vals]
        fig, ax = plt.subplots(figsize=(6, 3.2))
        ax.bar(labels, vals, color=colors)
        ax.axhline(0, color="k", lw=1)
        ax.set_ylabel(r"$\Delta\chi^2$ (EFC - ΛCDM)")
        ax.set_title("Non-MCMC likelihood-ratio preferences")
        for i, v in enumerate(vals):
            ax.text(i, v - (0.5 if v < 0 else 0.5), f"{v:.2f}", ha="center", va="top" if v < 0 else "bottom")
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print("matplotlib not available or failed to render plot; skipping figure.")


if __name__ == "__main__":
    main()
