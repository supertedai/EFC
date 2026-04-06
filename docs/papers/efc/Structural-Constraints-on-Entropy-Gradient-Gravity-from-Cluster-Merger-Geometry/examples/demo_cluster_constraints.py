#!/usr/bin/env python3
"""Demo: Structural Constraints on Entropy-Gradient Gravity.

Shows how local couplings are falsified and non-local coupling
parameters are constrained using cluster merger geometry.

Author: Morten Magnusson (ORCID 0009-0002-4860-5095)
License: CC-BY-4.0
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cluster_merger_constraints import (
    ClusterMerger,
    NonLocalCoupling,
    ConstraintResult,
)


def main():
    print("=" * 65)
    print("EFC -- Cluster Merger Constraints: Demo")
    print("=" * 65)

    # Define clusters
    bullet = ClusterMerger("Bullet", M_total=15.0, R_core=250.0,
                           v_merger=4700.0, separation=720.0)
    macs = ClusterMerger("MACS J0025", M_total=8.0, R_core=150.0,
                         v_merger=3000.0, separation=400.0)
    abell = ClusterMerger("Abell 520", M_total=12.0, R_core=200.0,
                          v_merger=2500.0, separation=600.0)

    clusters = [bullet, macs, abell]

    print("\n--- Cluster Properties ---")
    print(f"{'Cluster':<15} {'M (1e14)':>10} {'R_core':>8} {'v_m':>8} {'t_cross':>10}")
    print("-" * 55)
    for c in clusters:
        print(f"{c.name:<15} {c.M_total:10.1f} {c.R_core:8.0f} "
              f"{c.v_merger:8.0f} {c.crossing_time():10.1f} Myr")

    # Non-local coupling model
    coupling = NonLocalCoupling(L0=200.0, w=20.0, eta=66.2)
    print(f"\nCoupling model: {coupling}")

    # BC-001: Local coupling falsification
    print("\n--- BC-001: Local Coupling Test ---")
    bc001 = coupling.test_local_coupling()
    print(f"Result: {bc001}")
    print(f"Detail: {bc001.description}")

    # BC-002: Non-local coupling test
    print("\n--- BC-002: Non-Local Coupling Test ---")
    for c in clusters:
        bc002 = coupling.test_nonlocal_coupling(c)
        print(f"{c.name:<15} {bc002}")

    # BC-003: Predictions
    print("\n--- BC-003: Predicted w values ---")
    print(f"{'Cluster':<15} {'w_pred':>8}")
    print("-" * 25)
    for c in clusters:
        t_cross = c.crossing_time()
        w_pred = coupling.predict_w(c.M_total, t_cross)
        print(f"{c.name:<15} {w_pred:8.1f}")

    # Kernel values
    print("\n--- Smoothing Kernel ---")
    for r in [0, 50, 100, 200, 500]:
        K = coupling.kernel(float(r))
        enh = coupling.effective_enhancement(float(r), rho_gradient=0.01)
        print(f"r={r:4d} kpc:  K={K:.6f}  mu={enh:.4f}")

    # Verification
    print("\n--- Verification ---")
    assert not bc001.passed, "BC-001 must fail (local coupling falsified)"
    assert bc001.value == 0.0, "Zero passes for local coupling"

    bc002_bullet = coupling.test_nonlocal_coupling(bullet)
    assert bc002_bullet.passed, "Non-local coupling should pass for Bullet"

    assert coupling.kernel(0.0) > coupling.kernel(200.0), \
        "Kernel must decrease with radius"
    assert coupling.effective_enhancement(0.0, 0.01) > 1.0, \
        "Enhancement must exceed 1"

    assert bullet.crossing_time() > 0, "Crossing time must be positive"
    assert bullet.mass_ratio() > 0, "Mass ratio must be positive"

    print("All checks passed.")
    print("=" * 65)


if __name__ == "__main__":
    main()
