"""
Demo: CEM -- Consciousness Ego Mirror.

Demonstrates the feedback loop between consciousness, ego, and
the entropy field, including reflection deepening and simulation.

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
License: CC-BY-4.0
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cem_model import (
    AwarenessLevel,
    ConsciousnessEgoMirror,
    EgoState,
    ReflectionFeedback,
)


def main():
    print("=" * 60)
    print("CEM -- Consciousness Ego Mirror - Demo")
    print("=" * 60)

    # Load reference data
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "cem_data.json"
    )
    with open(data_path) as f:
        data = json.load(f)

    # 1. Show awareness levels
    print("\n--- Awareness Levels ---")
    for level in data["awareness_levels"]:
        print(f"  {level['level']:18s} weight={level['weight']}  {level['description']}")

    # 2. Initialise CEM
    print("\n--- Initialise CEM ---")
    params = data["default_parameters"]
    ego = EgoState(
        identity_coherence=params["identity_coherence"],
        entropy_coupling=params["entropy_coupling"],
    )
    cem = ConsciousnessEgoMirror(
        alpha=params["alpha"],
        S_baseline=params["S_baseline"],
        ego=ego,
    )
    print(f"  alpha={cem.alpha}, S_baseline={cem.S_baseline}")
    print(f"  ego coherence={ego.identity_coherence}, coupling={ego.entropy_coupling}")
    print(f"  mirror fidelity={ego.mirror_fidelity:.4f}")

    # 3. Feedback equation
    print(f"\n--- Feedback Equation ---")
    print(f"  {data['feedback_equation']}")

    # 4. Single feedback cycle
    print("\n--- Single Feedback Cycle ---")
    fb = cem.feedback_cycle(0.5)
    print(f"  S_input={fb.S_input:.3f}  ego_response={fb.ego_response:.3f}  "
          f"mirror_output={fb.mirror_output:.4f}  awareness={fb.awareness_level.value}")

    # 5. Deepen reflection
    print("\n--- Deepen Reflection ---")
    for i in range(3):
        cem.deepen_reflection()
        print(f"  Depth {cem.ego.reflection_depth}: "
              f"awareness={cem.ego.awareness.value}, "
              f"mirror_fidelity={cem.ego.mirror_fidelity:.4f}")

    # 6. Run simulation with field sequence
    print("\n--- Simulation ---")
    S_sequence = data["example_field_sequence"]
    results = cem.run_simulation(S_sequence)
    for fb in results:
        print(f"  Cycle {fb.cycle:2d}: S_in={fb.S_input:.2f}  "
              f"mirror_out={fb.mirror_output:.4f}  "
              f"awareness={fb.awareness_level.value}")

    # 7. Coherence trajectory
    print("\n--- Coherence Trajectory ---")
    trajectory = cem.coherence_trajectory()
    for cycle, fidelity in trajectory:
        bar = "#" * int(fidelity * 40)
        print(f"  Cycle {cycle:2d}: {fidelity:.4f} {bar}")

    # 8. System summary
    print("\n--- System Summary ---")
    summary = cem.summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
