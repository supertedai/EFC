#!/usr/bin/env python3
"""
Reproduce the Kill-Test v6 Universality result in one command.

From the repository root:

    python "docs/papers/efc/Kill-Test v6 Universality_SPARC175/examples/reproduce.py"

Depends on: numpy, scipy. Runtime: ~2 minutes, single core.
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(PKG, "..", "..", ".."))

SPARC175_DIR = os.path.join(
    REPO,
    "docs",
    "papers",
    "efc",
    "Comprehensive-analysis-of-175-SPARC-galaxies-demonstrating-regime-dependent-validity-in-rotation-curve-modeling",
)
OUT_DIR = os.path.join(PKG, "data")

# Make the pipeline importable
sys.path.insert(0, os.path.join(PKG, "src"))
from sparc175_killtest_universality import run_universality_analysis  # noqa: E402


def main():
    if not os.path.isdir(SPARC175_DIR):
        print(f"ERROR: SPARC 175 paper directory not found at {SPARC175_DIR}", file=sys.stderr)
        return 1

    result = run_universality_analysis(SPARC175_DIR, OUT_DIR)

    # Print a compact headline block
    s = result["summary"]
    u = result["kill_test_v6_extension"]["extended_to_175"]
    print()
    print("=" * 60)
    print("HEADLINE")
    print("=" * 60)
    print(f"  Fitted             : {s['n_fitted']} / {s['n_galaxies_total']}")
    print(f"  EFC win rate       : {s['efc_win_rate_percent']} %")
    print(f"  EFC_decisive       : {u['efc_decisive_rate_percent']} %")
    print(f"  Median ΔAIC        : {s['median_delta_aic']}")
    print(f"  Median χ²_red EFC  : {s['median_chi2_red_efc']}")
    print(f"  Median χ²_red NFW  : {s['median_chi2_red_nfw']}")
    print(f"  Universality       : {u['universality_verdict']}")
    print(f"  Cherry-picking     : {'refuted' if u['cherry_picking_refuted'] else 'not refuted'}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
