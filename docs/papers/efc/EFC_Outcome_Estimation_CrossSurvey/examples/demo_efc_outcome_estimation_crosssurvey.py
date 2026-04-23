#!/usr/bin/env python
"""demo_efc_outcome_estimation_crosssurvey.py

Demonstrates the key calculations from the EFC cross-survey outcome
estimation paper (DOI: 10.6084/m9.figshare.32045592).

Runs standalone; optionally produces a summary figure.
"""
import numpy as np

from efc_outcome_estimation_crosssurvey import (
    SPARC_N, SPARC_WIN_RATE, SPARC_DECISIVE, SPARC_MARGINAL,
    THINGS_N, LITTLE_THINGS_N, WALLABY_N, TIER1_N,
    NET_SHIFT_TIER1, NET_SHIFT_WALLABY, TYPICAL_NPTS,
    K_SCREENING, K_SCREENING_ERR,
    FLOW_FRAC, TRANSITION_FRAC, LATENT_FRAC,
    wilson_ci, bic_extra_penalty, estimate_aic_win_rate,
    estimate_bic_win_rate, project_survey_counts,
    regime_fractions_consistent, overlap_test_estimate,
)

# ------------------------------------------------------------------
# 1.  Reproduce Table 3: AIC win-rate projections
# ------------------------------------------------------------------
print("=" * 65)
print("TABLE 3 REPRODUCTION — AIC Win-Rate Projections")
print("=" * 65)
surveys = [
    ("SPARC (known)", 0.0, SPARC_N, "SPARC"),
    ("THINGS",       NET_SHIFT_TIER1, THINGS_N, "THINGS"),
    ("LITTLE THINGS",NET_SHIFT_TIER1, LITTLE_THINGS_N, "LITTLE_THINGS"),
    ("WALLABY",      NET_SHIFT_WALLABY, WALLABY_N, "WALLABY"),
]

wr_aic_list, wr_bic_list, labels, sizes = [], [], [], []

for label, shift, n, key in surveys:
    wr = estimate_aic_win_rate(SPARC_WIN_RATE, shift)
    k_succ = int(round(wr * n))
    lo, hi = wilson_ci(n, k_succ)
    npts = TYPICAL_NPTS.get(key, 20)
    pen = bic_extra_penalty(npts)
    # rough BIC win rate (table 4 logic)
    counts = project_survey_counts(n, wr)
    wr_bic = estimate_bic_win_rate(wr, n, counts["decisive"],
                                    counts["marginal"], npts)
    wr_aic_list.append(wr)
    wr_bic_list.append(wr_bic)
    labels.append(label)
    sizes.append(n)
    print(f"  {label:18s}  N={n:3d}  AIC WR={wr:5.1%}  "
          f"95%CI=[{lo:.0%},{hi:.0%}]  BIC WR≈{wr_bic:.0%}  "
          f"BIC extra pen={pen:+.2f}")

# Tier-1 combined
wr_t1 = estimate_aic_win_rate(SPARC_WIN_RATE, NET_SHIFT_TIER1)
k_t1 = int(round(wr_t1 * TIER1_N))
lo_t1, hi_t1 = wilson_ci(TIER1_N, k_t1)
print(f"\n  {'Tier-1 non-SPARC':18s}  N={TIER1_N:3d}  AIC WR={wr_t1:5.1%}  "
      f"95%CI=[{lo_t1:.0%},{hi_t1:.0%}]")

# ------------------------------------------------------------------
# 2.  Overlap test (P2)
# ------------------------------------------------------------------
print("\n" + "=" * 65)
print("OVERLAP TEST (P2) — 14 shared SPARC/THINGS galaxies")
print("=" * 65)
exp = overlap_test_estimate(n_overlap=14, n_decisive=10, n_marginal=4)
print(f"  Expected consistent verdicts: {exp:.1f} / 14")
print(f"  Threshold: >= 10 / 14  →  {'LIKELY PASS' if exp >= 10 else 'AT RISK'}")

# ------------------------------------------------------------------
# 3.  Regime fraction consistency (P3)
# ------------------------------------------------------------------
print("\n" + "=" * 65)
print("REGIME FRACTION CONSISTENCY (P3)")
print("=" * 65)
print(f"  FLOW       = {FLOW_FRAC:.1%}")
print(f"  TRANSITION = {TRANSITION_FRAC:.1%}")
print(f"  LATENT     = {LATENT_FRAC:.1%}")
ok = regime_fractions_consistent(FLOW_FRAC, TRANSITION_FRAC, LATENT_FRAC)
print(f"  Self-consistent within ±15 pp: {ok}")

# ------------------------------------------------------------------
# 4.  Screening parameter
# ------------------------------------------------------------------
print("\n" + "=" * 65)
print("SCREENING PARAMETER")
print("=" * 65)
print(f"  k = {K_SCREENING} ± {K_SCREENING_ERR}")
print(f"  P5 target (BIG-SPARC): k_BIG = 0.415 ± 0.015")

# ------------------------------------------------------------------
# 5.  Optional plot
# ------------------------------------------------------------------
try:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    # Panel A: AIC vs BIC win rates
    x = np.arange(len(labels))
    w = 0.35
    axes[0].bar(x - w/2, [v*100 for v in wr_aic_list], w, label="AIC", color="#3478F6")
    axes[0].bar(x + w/2, [v*100 for v in wr_bic_list], w, label="BIC", color="#FF9500")
    axes[0].axhline(50, ls="--", color="grey", lw=0.8)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
    axes[0].set_ylabel("EFC win rate (%)")
    axes[0].set_title("Projected Win Rates")
    axes[0].legend(fontsize=8)
    axes[0].set_ylim(0, 80)

    # Panel B: Wilson CI width vs N
    ns = np.arange(20, 500)
    ci_widths = []
    for n in ns:
        k = int(round(0.58 * n))
        lo, hi = wilson_ci(int(n), k)
        ci_widths.append((hi - lo) * 100)
    axes[1].plot(ns, ci_widths, color="#3478F6")
    for n_mark, lab in [(34, "THINGS"), (26, "LT"), (60, "Tier-1"),
                         (203, "WALLABY"), (500, "BIG-SPARC")]:
        if n_mark <= 500:
            k = int(round(0.58 * n_mark))
            lo, hi = wilson_ci(n_mark, k)
            axes[1].plot(n_mark, (hi - lo)*100, "o", ms=7)
            axes[1].annotate(lab, (n_mark, (hi-lo)*100+1), fontsize=7,
                             ha="center")
    axes[1].set_xlabel("Sample size N")
    axes[1].set_ylabel("95% CI width (pp)")
    axes[1].set_title("Statistical Power")

    plt.tight_layout()
    plt.savefig("efc_crosssurvey_projections.png", dpi=150)
    print("\n  Figure saved to efc_crosssurvey_projections.png")
    plt.show()
except ImportError:
    print("\n  (matplotlib not available — skipping plot)")
