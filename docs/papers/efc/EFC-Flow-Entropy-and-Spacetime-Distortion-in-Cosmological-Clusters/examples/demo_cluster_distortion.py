#!/usr/bin/env python3
"""
Cluster Distortion Demo

Demonstrates spacetime distortion from entropy gradients and
energy flow in a cosmological cluster using the EFC framework.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cluster_distortion import (
    ClusterDistortion,
    EnergyFlowField,
    EntropyGradient,
    LensingProfile,
)


def main():
    print("=" * 60)
    print("EFC Cluster Distortion Demo")
    print("=" * 60)
    print()

    # Set up entropy gradient
    entropy = EntropyGradient(s_center=1.0, grad_s=0.5, scale_radius=2.0)
    print("Entropy Gradient Profile:")
    for r in [0.5, 1.0, 2.0, 5.0]:
        print(f"  S({r} Mpc) = {entropy.profile(r):.4f}  "
              f"dS/dr = {entropy.gradient_at(r):.4f}")
    print()

    # Set up energy flow field
    flow = EnergyFlowField(ef_0=10.0, decay_length=3.0)
    print("Energy Flow Field:")
    for r in [0.5, 1.0, 2.0, 5.0]:
        print(f"  Ef({r} Mpc) = {flow.density(r):.4f}")
    print()

    # Lensing profile
    lensing = LensingProfile(entropy, flow, coupling=1.0)
    print("Lensing Profile:")
    for r in [0.5, 1.0, 2.0, 5.0]:
        alpha = lensing.deflection_angle(r)
        kappa = lensing.convergence(r)
        print(f"  r={r} Mpc: deflection={alpha:.6f} rad, "
              f"convergence={kappa:.6f}")
    print()

    # Full cluster model
    model = ClusterDistortion(entropy, flow, coupling=1.0)
    print(model.summary())
    print()

    # Distortion profile
    radii = [0.5, 1.0, 2.0, 3.0, 5.0, 7.0]
    profile = model.distortion_profile(radii)
    print("Full Distortion Profile:")
    print(f"  {'r (Mpc)':>8}  {'S':>8}  {'Ef':>8}  "
          f"{'alpha':>10}  {'dT/T':>10}")
    for p in profile:
        print(f"  {p['r']:8.2f}  {p['entropy']:8.4f}  "
              f"{p['flow']:8.4f}  {p['deflection']:10.6f}  "
              f"{p['temp_asymmetry']:10.6f}")
    print()
    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
