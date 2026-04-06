#!/usr/bin/env python3
"""Demo: Why Is Light Speed a Cosmic Limit?

Shows how the speed of light emerges as the maximum entropy transport
rate in the EFC flow field.

Author: Morten Magnusson (ORCID 0009-0002-4860-5095)
License: CC-BY-4.0
"""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.light_speed_limit import LightSpeedLimit, EntropyFlowField, PropagationBound


def main():
    print("=" * 60)
    print("EFC -- Why Is Light Speed a Cosmic Limit?: Demo")
    print("=" * 60)

    model = LightSpeedLimit(c=1.0)
    bound = PropagationBound()

    # Show entropy cost divergence
    print(f"\n{'v/c':>6}  {'gamma':>10}  {'dS/dv':>12}  {'causal':>8}")
    print("-" * 42)
    velocities = [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99, 0.999]
    for v in velocities:
        gamma = bound.lorentz_factor(v)
        cost = model.entropy_speed_relation(v)
        causal = model.is_causal(v)
        print(f"{v:6.3f}  {gamma:10.3f}  {cost:12.1f}  {str(causal):>8}")

    # Massless vs massive particles
    print("\n--- Particle speeds ---")
    v_photon = model.effective_speed(energy=1.0, rest_mass=0.0)
    v_massive = model.effective_speed(energy=10.0, rest_mass=1.0)
    print(f"Photon (m=0, E=1):    v = {v_photon:.4f} c")
    print(f"Massive (m=1, E=10):  v = {v_massive:.4f} c")

    # Flow field checks
    print("\n--- Flow field ---")
    subluminal = EntropyFlowField(flow_rate=0.8, direction=(1.0, 0.0, 0.0))
    superluminal = EntropyFlowField(flow_rate=1.5, direction=(0.0, 1.0, 0.0))
    print(f"Subluminal field:   {subluminal.is_subluminal()}")
    print(f"Superluminal field: {superluminal.is_subluminal()}")

    # Verification
    print("\n--- Verification ---")
    assert v_photon == 1.0, "Photon must travel at c"
    assert v_massive < 1.0, "Massive particle must be subluminal"
    assert subluminal.is_subluminal(), "Should be subluminal"
    assert not superluminal.is_subluminal(), "Should be superluminal"
    assert bound.v_max() == 1.0, "Max propagation speed must be c"
    assert model.entropy_speed_relation(0.99) > model.entropy_speed_relation(0.5), \
        "Entropy cost must increase with speed"
    assert model.is_causal(0.99), "v < c must be causal"

    td = bound.time_dilation(0.9, 1.0)
    assert td > 1.0, "Time dilation must exceed 1 for moving observer"

    print("All checks passed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
