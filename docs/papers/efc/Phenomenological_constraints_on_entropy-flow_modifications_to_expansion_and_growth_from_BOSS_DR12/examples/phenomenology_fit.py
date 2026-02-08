#!/usr/bin/env python3
"""
Example: EFC Phenomenological Model Analysis

Demonstrates the key results from the BOSS DR12 analysis:
1. Anti-correlation between expansion and growth modifications
2. BAO-RSD sign conflict (S8 tension in EFC parameter space)
3. Gravitational slip prediction η = 1

Reference: Magnusson (2026), doi:10.6084/m9.figshare.31243828
"""

import numpy as np
import sys
sys.path.insert(0, '..')
from src.efc_phenomenology import EFCPhenomenology, LCDM_BEST_FIT, EFC_BEST_FIT


def main():
    print("=" * 70)
    print("EFC Phenomenological Constraints from BOSS DR12")
    print("=" * 70)

    # 1. Compare ΛCDM and EFC best-fits
    print("\n1. BEST-FIT PARAMETERS")
    print("-" * 50)
    print(f"{'Parameter':<15} {'ΛCDM':>12} {'EFC':>12}")
    print("-" * 50)
    print(f"{'H₀ [km/s/Mpc]':<15} {LCDM_BEST_FIT.H0:>12.2f} {EFC_BEST_FIT.H0:>12.2f}")
    print(f"{'Ωm':<15} {LCDM_BEST_FIT.Omega_m:>12.3f} {EFC_BEST_FIT.Omega_m:>12.3f}")
    print(f"{'σ8':<15} {LCDM_BEST_FIT.sigma8:>12.3f} {EFC_BEST_FIT.sigma8:>12.3f}")
    print(f"{'α_L2':<15} {LCDM_BEST_FIT.alpha_L2:>12.3f} {EFC_BEST_FIT.alpha_L2:>12.3f}")
    print(f"{'χ²':<15} {'7.29':>12} {'4.28':>12}")
    print(f"{'dof':<15} {'6':>12} {'5':>12}")

    # 2. Demonstrate anti-correlation signature
    print("\n2. EFC ANTI-CORRELATION SIGNATURE")
    print("-" * 50)
    print("Key insight: g_D(z) > 0 and g_growth(z) < 0 for all z > 0")
    print("So positive α_L2 increases distances BUT suppresses growth!")
    print()

    model = EFC_BEST_FIT
    z_values = [0.38, 0.51, 0.61]  # BOSS redshifts

    print(f"{'z':<6} {'g_D(z)':<12} {'g_growth(z)':<14} {'Effect on D_M':<16} {'Effect on fσ8':<14}")
    print("-" * 60)

    for z in z_values:
        g_D = model.g_D(z)
        g_growth = model.g_growth(z)
        DM_change = model.alpha_L2 * g_D * 100
        fs8_change = model.alpha_L2 * g_growth * 100

        print(f"{z:<6.2f} {g_D:<12.4f} {g_growth:<14.4f} {DM_change:>+.1f}%{'':<10} {fs8_change:>+.1f}%")

    # 3. Show BAO-RSD tension
    print("\n3. BAO-RSD SIGN CONFLICT (S8 TENSION)")
    print("-" * 50)
    print("BAO-only:  α_L2 = +0.28 ± 0.18  (prefers positive)")
    print("RSD-only:  α_L2 ≈ -1.4         (prefers negative)")
    print("Joint:     α_L2 = +0.34 ± 0.16  (compromise)")
    print()
    print("Interpretation: Data simultaneously prefer:")
    print("  - Faster expansion (larger D_M, higher H₀)")
    print("  - Stronger clustering (higher fσ8)")
    print("This is the S8 tension expressed in EFC parameter space!")

    # 4. Compute observables at BOSS redshifts
    print("\n4. OBSERVABLES AT BOSS REDSHIFTS")
    print("-" * 50)

    print(f"\n{'z':<6} {'D_M^ΛCDM':<12} {'D_M^EFC':<12} {'Δ%':<8}")
    print("-" * 40)
    for z in z_values:
        DM_L = LCDM_BEST_FIT.DM_LCDM(z)
        DM_E = EFC_BEST_FIT.DM_EFC(z)
        pct = (DM_E/DM_L - 1) * 100
        print(f"{z:<6.2f} {DM_L:<12.1f} {DM_E:<12.1f} {pct:>+.2f}%")

    print(f"\n{'z':<6} {'fσ8^ΛCDM':<12} {'fσ8^EFC':<12} {'Δ%':<8}")
    print("-" * 40)
    for z in z_values:
        fs8_L = LCDM_BEST_FIT.fsigma8_LCDM(z)
        fs8_E = EFC_BEST_FIT.fsigma8_EFC(z)
        pct = (fs8_E/fs8_L - 1) * 100
        print(f"{z:<6.2f} {fs8_L:<12.4f} {fs8_E:<12.4f} {pct:>+.2f}%")

    # 5. Falsifiable prediction
    print("\n5. FALSIFIABLE PREDICTION: GRAVITATIONAL SLIP")
    print("-" * 50)
    print("EFC predicts: η ≡ Φ/Ψ = 1 (no gravitational slip)")
    print()
    print("This distinguishes EFC from:")
    print("  - Scalar-tensor theories: η ≠ 1")
    print("  - f(R) gravity: η ≠ 1")
    print()
    print("Testable with:")
    print("  - Euclid: σ(η) ≈ ±0.03 at z ~ 0.5-1.5")
    print("  - Euclid + Rubin: σ(η) ≈ ±0.01")
    print()
    print("Detection of η ≠ 1 would FALSIFY EFC!")

    # 6. Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"""
Result: α_L2 = 0.34 ± 0.16 (1σ)
        Δχ² = 3.01 → 1.7σ preference for EFC

Status: Suggestive but not statistically significant
        ΛCDM excluded at 1σ, included at 2σ

Key insight: The BAO-RSD sign conflict IS the S8 tension,
             recast in EFC parameter space.

Next steps: Await Stage IV surveys (Euclid, Rubin) for
            - Tighter α_L2 constraints
            - Gravitational slip test (η = 1?)
""")


if __name__ == '__main__':
    main()
