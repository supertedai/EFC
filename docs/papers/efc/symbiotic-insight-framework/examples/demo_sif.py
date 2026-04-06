"""
Demo: Symbiotic Insight Framework (SIF).

Demonstrates high-velocity insight generation, stabilisation cycles,
cross-domain connections, and productivity metrics.

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
License: CC-BY-4.0
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sif import (
    FieldState,
    InsightField,
    StabilisationCycle,
    SymbioticInsightFramework,
)


def main():
    print("=" * 60)
    print("Symbiotic Insight Framework (SIF) - Demo")
    print("=" * 60)

    # Load example data
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "sif_data.json"
    )
    with open(data_path) as f:
        data = json.load(f)

    # 1. Create framework and generate fields from data
    print("\n--- Generate Insight Fields ---")
    sif = SymbioticInsightFramework()
    for fdata in data["example_fields"]:
        field = sif.generate_field(
            label=fdata["label"],
            domain=fdata["domain"],
            content=fdata["content"],
        )
        print(f"  [{field.domain}] {field.label}: {field.state.value}")

    # 2. Establish cross-domain connections
    print("\n--- Cross-Domain Connections ---")
    field_map = {f.label: f for f in sif.fields}
    for conn in data["cross_domain_connections"]:
        if conn[0] in field_map and conn[1] in field_map:
            field_map[conn[0]].connect(conn[1])
            field_map[conn[1]].connect(conn[0])
            print(f"  {conn[0]} <-> {conn[1]}")

    # 3. Run stabilisation cycle
    print("\n--- Stabilisation Cycle ---")
    threshold = data["stabilisation_defaults"]["coherence_threshold"]
    cycle = sif.run_stabilisation_cycle(coherence_threshold=threshold)
    print(f"  Cycle {cycle.cycle_id}: "
          f"{cycle.fields_in} in, {cycle.fields_out} stabilised, "
          f"rate={cycle.stabilisation_rate:.1%}, "
          f"mean coherence={cycle.mean_coherence:.3f}")

    # 4. Structure and preserve
    print("\n--- Structure and Preserve ---")
    n_structured = sif.structure_all()
    print(f"  Structured: {n_structured} fields")
    n_preserved = sif.preserve_all()
    print(f"  Preserved:  {n_preserved} fields")

    # 5. Field state summary
    print("\n--- Field States ---")
    for f in sif.fields:
        conn_str = f", connections={f.connections}" if f.connections else ""
        print(f"  {f.label}: {f.state.value} (coherence={f.coherence:.3f}{conn_str})")

    # 6. Framework summary
    print("\n--- Framework Summary ---")
    summary = sif.summary()
    print(f"  Total fields: {summary['total_fields']}")
    print(f"  State distribution: {summary['state_distribution']}")
    print(f"  Cycles completed: {summary['cycles_completed']}")
    print(f"  Insight velocity: {summary['insight_velocity']:.1f} fields/cycle")

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
