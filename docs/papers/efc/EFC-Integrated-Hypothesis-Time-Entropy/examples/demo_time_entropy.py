#!/usr/bin/env python3
"""Demonstration: EFC Integrated Hypothesis -- Time and Entropy.

Shows:
  1. Temporal gradient and tick rates
  2. Causal chain construction and verification
  3. Time emergence simulation
  4. Time dilation from grid resistance

Author: Morten Magnusson, ORCID 0009-0002-4860-5095
License: CC-BY-4.0
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from time_entropy import (
    EntropyState,
    TemporalGradient,
    CausalChain,
    TimeEntropyModel,
)


def demo_temporal_gradient():
    """1. Temporal gradient and tick rates."""
    print("=" * 60)
    print("1. TEMPORAL GRADIENT AND TICK RATES")
    print("   tau_dot = |dS/dt| / (1 + R)")
    print("=" * 60)

    for dS_dt in [0.5, 1.0, 5.0, 10.0]:
        for R in [0.0, 0.01, 0.1, 1.0]:
            tg = TemporalGradient(dS_dt=dS_dt, grid_resistance=R)
            print(f"  dS/dt={dS_dt:5.1f}  R={R:<5}  "
                  f"tick={tg.effective_tick_rate():.4f}  "
                  f"arrow={tg.arrow_of_time():+d}")


def demo_causal_chain():
    """2. Causal chain verification."""
    print("\n" + "=" * 60)
    print("2. CAUSAL CHAIN CONSTRUCTION AND VERIFICATION")
    print("=" * 60)

    # Valid chain (monotonic increase)
    chain = CausalChain()
    for i in range(6):
        chain.add_state(EntropyState(entropy=1.0 + i * 0.5,
                                     temperature=3000.0, time_label=float(i)))
    print(f"\n  Valid chain:")
    print(f"    Length:    {len(chain.states)}")
    print(f"    Causal:   {chain.is_causal()}")
    print(f"    Delta S:  {chain.total_entropy_change():.2f}")
    print(f"    Avg rate: {chain.average_rate():.3f}")

    # Invalid chain (causality violation)
    bad_chain = CausalChain()
    for s in [1.0, 1.5, 2.0, 1.8, 2.5, 3.0]:
        bad_chain.add_state(EntropyState(entropy=s, temperature=3000.0,
                                         time_label=float(len(bad_chain.states))))
    print(f"\n  Chain with violation:")
    print(f"    Causal:     {bad_chain.is_causal()}")
    print(f"    Violations: {bad_chain.causality_violations()}")


def demo_time_emergence():
    """3. Time emergence simulation."""
    print("\n" + "=" * 60)
    print("3. TIME EMERGENCE SIMULATION")
    print("=" * 60)

    model = TimeEntropyModel(grid_resistance=0.01)
    print(f"\n{model.summary()}\n")

    results = model.simulate_time_emergence(
        s_initial=1.0, ds_dt=2.0, t_initial=0.0, n_steps=6, dt=1.0,
    )

    print(f"  {'Step':>4}  {'t_coord':>8}  {'S':>8}  "
          f"{'tick':>8}  {'tau':>10}  {'arrow':>5}")
    print("  " + "-" * 50)
    for r in results:
        print(f"  {r['step']:4d}  {r['coordinate_time']:8.2f}  "
              f"{r['entropy']:8.3f}  {r['tick_rate']:8.4f}  "
              f"{r['proper_time']:10.4f}  {r['arrow']:+5d}")


def demo_time_dilation():
    """4. Time dilation from grid resistance."""
    print("\n" + "=" * 60)
    print("4. TIME DILATION FROM GRID RESISTANCE")
    print("=" * 60)

    dS_dt = 5.0
    ref = TemporalGradient(dS_dt=dS_dt, grid_resistance=0.0)
    ref_rate = ref.effective_tick_rate()

    print(f"\n  Reference: dS/dt = {dS_dt}, R = 0 -> tick = {ref_rate:.4f}")
    print()

    for R in [0.0, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]:
        tg = TemporalGradient(dS_dt=dS_dt, grid_resistance=R)
        gamma = tg.time_dilation_factor(ref_rate)
        print(f"  R = {R:<5}  tick = {tg.effective_tick_rate():.4f}  "
              f"gamma = {gamma:.4f}")


if __name__ == "__main__":
    print("EFC Integrated Hypothesis: Time and Entropy")
    print("Magnusson (2026)")
    print()

    demo_temporal_gradient()
    demo_causal_chain()
    demo_time_emergence()
    demo_time_dilation()

    print("\n" + "=" * 60)
    print("All demonstrations completed successfully.")
    print("=" * 60)
