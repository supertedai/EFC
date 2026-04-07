"""Reproduce WP4 transfer-test result. Run: python examples/demo.py"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src import (
    EFCRegimeGate, WP4_RESULT, ROBUSTNESS_SWEEP, WHITENED_COMPONENTS, BEST_FITS, H_efc,
)


def main() -> None:
    gate = EFCRegimeGate()
    print(f"=== WP4 EFC Regime Gate ===")
    print(f"z_L1L2 = {gate.z_L1L2}, alpha_L2 = {gate.alpha_L2}")
    print(f"H factor at z=0.5  : {gate.factor(0.5):.4f}")
    print(f"H factor at z=1.5  : {gate.factor(1.5):.4f}")
    assert abs(gate.factor(0.5) - (1 + 0.045) ** 0.5) < 1e-9
    assert gate.factor(1.5) == 1.0  # gate off above z_L1L2

    print("\n=== Transfer Test (DESI -> BOSS, no refit) ===")
    print(f"chi2(LCDM) = {WP4_RESULT.chi2_LCDM:.2f}")
    print(f"chi2(EFC)  = {WP4_RESULT.chi2_EFC:.2f}")
    print(f"Δχ²        = {WP4_RESULT.delta_chi2:.2f}  k_eff = {WP4_RESULT.k_eff}")
    assert abs(WP4_RESULT.delta_chi2 - (-7.77)) < 1e-6
    assert WP4_RESULT.efc_wins
    assert WP4_RESULT.k_eff == 0

    print("\n=== Whitened components ===")
    total_L = total_E = 0.0
    for label, cL, cE in WHITENED_COMPONENTS:
        total_L += cL; total_E += cE
        print(f"  {label}: ΛCDM={cL:6.2f}  EFC={cE:6.2f}  Δ={cE-cL:+6.2f}")
    print(f"  total: ΛCDM={total_L:.2f} EFC={total_E:.2f} Δ={total_E-total_L:+.2f}")
    assert abs(total_L - 20.82) < 0.05 and abs(total_E - 13.07) < 0.05

    print("\n=== Robustness sweep C(ρ) ===")
    for rho, cL, cE in ROBUSTNESS_SWEEP:
        d = cE - cL
        print(f"  ρ={rho:.2f}  ΛCDM={cL:6.2f}  EFC={cE:6.2f}  Δχ²={d:+6.2f}  EFC wins: {d<0}")
        assert d < 0  # EFC wins at every covariance level

    print("\n=== Best-fit reference ===")
    for bf in BEST_FITS:
        print(f"  {bf.dataset:12s} N={bf.N:2d} k={bf.k_eff} z_L1L2={bf.z_L1L2} α={bf.alpha_L2} ΔAICc={bf.dAICc} ΔBIC={bf.dBIC}")

    print("\nAll assertions passed.")


if __name__ == "__main__":
    main()
