"""
Reproduce the six-probe kill-test verdict table and cobaya aggregate.

Usage:
    python examples/run_kill_tests.py

Expected output: six probe rows, verdict summary, non-rejectability pass,
and aggregate cobaya statistics (4/4 runs with Delta chi^2 <= 0).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path so 'src' can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.kill_test_suite import (  # noqa: E402
    run_all_probes,
    verdict_summary,
    passes_non_rejectability,
)
from src.cobaya_minimize import (  # noqa: E402
    COBAYA_RUNS,
    SECTOR_DECOMPOSITION,
    aggregate_runs,
    delta_chi2,
)


def main() -> None:
    print("=" * 72)
    print("EFC vs LCDM Kill-Test v6 — six-probe verdict")
    print("=" * 72)
    print()

    probes = run_all_probes()
    for p in probes:
        print(p.as_row())
    print()

    print(f"Verdict summary: {verdict_summary(probes)}")
    nr = passes_non_rejectability()
    print(f"Non-rejectability test: {'PASS (EFC survives)' if nr else 'FAIL'}")
    print()

    print("=" * 72)
    print("Cobaya minimize aggregate (Table 5)")
    print("=" * 72)
    agg = aggregate_runs()
    for k, v in agg.items():
        print(f"  {k}: {v}")
    print()

    print("Sector decomposition (K0, m^2 run — Table 6):")
    print(f"  Sum of Delta chi^2 = {delta_chi2():+.3f}")
    print()

    # Final verdict line
    if nr and agg["all_efc_preferred"]:
        print(">>> Stage: Non-rejectable model — EFC survives kill-test <<<")
    else:
        print(">>> WARNING: verdict unexpected; please rerun <<<")


if __name__ == "__main__":
    main()
