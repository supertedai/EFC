#!/usr/bin/env python3
"""
Demo: Print EFC Validation Ledger statistics and kill-test status.

Reference: Magnusson (2026), doi:10.6084/m9.figshare.31970904
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from validation_checker import (
    ValidationTest,
    classify_status,
    check_kill_criterion_1,
    check_kill_criterion_2,
    check_kill_criterion_3,
    check_kill_criterion_4,
    check_kill_criterion_5,
    confirmation_level,
    TIER_LABELS,
)


def main():
    print("=" * 65)
    print("EFC White Paper Part 3 — Validation Ledger Summary")
    print("=" * 65)

    # --- Ledger statistics ---
    print("\n--- Ledger Statistics (Table 1) ---")
    print(f"  Total registered tests:  102")
    print(f"  Pass:                     66")
    print(f"  Partial:                   5")
    print(f"  Collapsed:                 3")
    print(f"  Failed:                   17")
    print(f"  Falsified (w/ successor):  5")

    print("\n--- Tier Classification ---")
    for tier, label in TIER_LABELS.items():
        print(f"  {tier}: {label}")

    # --- Sealed predictions ---
    print("\n--- Sealed Blind Predictions ---")
    print("  Prediction 1 (Freeze v1, 2026-02-18):")
    print("    alpha_L2 = -0.689")
    print("    f*sigma_8 crossover at z = 2.042")
    print("    Hash: 7a850cfa58477701...")
    print("  Prediction 2 (Freeze v2, 2026-02-21):")
    print("    alpha_L2 = -0.702")
    print("    Hash: dbccda150abca0e7...")

    # --- Signal summary ---
    print("\n--- Current Signal ---")
    alpha_L2 = -1.00
    alpha_err = 0.46
    sigma = abs(alpha_L2) / alpha_err
    level = confirmation_level(sigma)
    print(f"  alpha_L2 = {alpha_L2:.2f} +/- {alpha_err:.2f}")
    print(f"  Significance: {sigma:.2f} sigma")
    print(f"  Delta_AIC = -2.91")
    print(f"  LOO: 7/7 folds pass")
    print(f"  Confirmation level: {level}")

    # --- Kill criteria (current status) ---
    print("\n--- Kill Criteria (Stage-IV) ---")
    kc1 = check_kill_criterion_1(alpha_L2, alpha_err)
    print(f"  KC1 (Growth absent):     {'TRIGGERED' if kc1.triggered else 'Not triggered'}")
    # KC2-5: no Stage-IV data yet
    print(f"  KC2 (f*sigma_8 traj.):   Awaiting DESI DR2")
    print(f"  KC3 (S_8 -> LCDM):       Awaiting Stage-IV joint")
    print(f"  KC4 (No slip):           Awaiting Euclid")
    print(f"  KC5 (No dynamical DE):   Awaiting Euclid")

    # --- Confirmation roadmap ---
    print("\n--- Confirmation Roadmap ---")
    print(f"  {'Level':<20} {'Threshold':<15} {'Channel':<25} {'Survey':<15} {'Timeline'}")
    roadmap = [
        ("Hint (current)", "2.20 sigma", "f*sigma_8 LOO", "DESI+BOSS", "2026"),
        ("Suggestive", "3 sigma joint", "f*sigma_8 + S_8", "+DES+KiDS", "2027"),
        ("Evidence", "3.5 sigma", "mu-Sigma + f*sigma_8", "+Euclid Y1", "2028"),
        ("Detection", "5 sigma", "All channels", "Euclid+Rubin", "2030+"),
    ]
    for level_name, thresh, chan, survey, timeline in roadmap:
        print(f"  {level_name:<20} {thresh:<15} {chan:<25} {survey:<15} {timeline}")


if __name__ == "__main__":
    main()
