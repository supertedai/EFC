"""
Minimal reproducer: run the PIEMD A_sig 2D baseline and print results.

Note: the placeholder halos in src/asig_2d_piemd.py do NOT numerically
reproduce the paper's A_sig = -6.9e-4, p = 0.98 balance (which requires
the Rihtarsic et al. 2026 Table 4 best-fit parameters). They demonstrate
the mechanism of the A_sig operator only.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from asig_2d_piemd import run_baseline  # noqa: E402

if __name__ == "__main__":
    result = run_baseline(n_bootstrap=5000, verbose=False)
    print(f"A_sig baseline      = {result['asig_baseline']:+.3e}")
    print(f"kappa_front mean    = {result['kappa_front_mean']:+.4f}")
    print(f"kappa_back  mean    = {result['kappa_back_mean']:+.4f}")
    print(f"bootstrap p-value   = {result['bootstrap_p_value']:.3f}")
    print(f"A_sig / sigma_null  = {result['asig_over_sigma_null']:+.3f}")
    print()
    print("NOTE:", result["note"])
    print()
    print("Published baseline (EFC-VAL-2026-004): A_sig = -6.9e-4, p = 0.98")
    print("  (requires Rihtarsic et al. 2026 Table 4 best-fit parameters)")
