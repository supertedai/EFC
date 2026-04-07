"""Demo: reproduce P3 lensing consistency test from EFC-VAL-2026-002.

Run:  python examples/demo.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src import P3LensingTest, current_ledger


def main() -> None:
    test = P3LensingTest()
    obs = test.observed_ratio()
    status = test.evaluate()

    print("=== EFC P3 Lensing Test — DES Y6 vs CMB 2026 ===")
    print(f"S8 (DES Y6)    : {test.des.S8.value:.3f} ± {test.des.S8.uncertainty:.3f}")
    print(f"S8 (CMB 2026)  : {test.cmb.S8.value:.3f} ± {test.cmb.S8.uncertainty:.3f}")
    print(f"Observed ratio : {obs.value:.3f} ± {obs.uncertainty:.3f}")
    print(f"EFC prediction : {test.efc.ratio.value:.3f} ± {test.efc.ratio.uncertainty:.3f}")
    print(f"Agreement      : {status.sigma:.2f} sigma")
    print(f"Status         : {'PASS' if status.passed else 'FAIL'}  ({status.note})")

    # Pre-registered assertions
    assert abs(obs.value - 0.944) < 0.001, "ratio mismatch"
    assert 0.015 < obs.uncertainty < 0.020, "uncertainty mismatch"
    assert status.passed, "P3 should PASS for DES Y6"
    assert status.sigma < 1.0, "agreement should be sub-sigma"

    print("\n=== Validation Ledger (April 2026) ===")
    for row in current_ledger():
        obs_str = row.observed if row.observed else "—"
        print(f"  {row.test}: {row.name:30s} pred={row.prediction:20s} obs={obs_str:20s} {row.status}")

    print("\nAll assertions passed.")


if __name__ == "__main__":
    main()
