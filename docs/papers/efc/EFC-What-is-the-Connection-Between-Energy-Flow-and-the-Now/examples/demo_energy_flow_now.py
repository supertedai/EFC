#!/usr/bin/env python3
"""Demo: Energy Flow and the Now.

Shows how the Now profile emerges from the interplay of entropy
growth and energy flow in the EFC framework.

Author: Morten Magnusson (ORCID 0009-0002-4860-5095)
License: CC-BY-4.0
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.energy_flow_now import EnergyFlowNow, EntropyGradient, TemporalState


def main():
    print("=" * 60)
    print("EFC -- Energy Flow and the Now: Demo")
    print("=" * 60)

    model = EnergyFlowNow(S_max=1.0, tau=1.0)
    print(f"\nModel: {model}")

    # Compute temporal profile
    print(f"\n{'t':>6}  {'S(t)':>8}  {'dS/dt':>8}  {'Now':>10}  {'Arrow':>12}")
    print("-" * 52)
    for i in range(-5, 6):
        t = float(i)
        state = model.state_at(t)
        grad = model.gradient_at(t)
        now = model.now_profile(t)
        print(f"{t:6.1f}  {state.S:8.4f}  {grad.dS_dt:8.4f}  {now:10.4f}  {grad.arrow_direction():>12}")

    # Find peak Now
    peak_t = model.peak_now_time()
    peak_val = model.now_profile(peak_t)
    print(f"\nPeak Now at t = {peak_t:.2f} with intensity = {peak_val:.4f}")

    # Verify key properties
    print("\n--- Verification ---")
    grad_early = model.gradient_at(-10.0)
    grad_late = model.gradient_at(10.0)
    assert grad_early.arrow_direction() == "forward", "Early arrow should be forward"
    assert grad_late.arrow_direction() == "forward", "Late arrow should be forward"
    assert model.entropy(10.0) > model.entropy(-10.0), "Entropy must increase"
    assert peak_val > 0, "Peak Now must be positive"

    # Test TemporalState
    state = model.state_at(0.0)
    assert isinstance(state, TemporalState)
    assert state.now_intensity() > 0

    print("All checks passed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
