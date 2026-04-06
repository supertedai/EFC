"""
Demo: Symbiosis Human-AI Co-Reflection Architecture.

Demonstrates knowledge graph construction, reflection loops,
hypothesis tracking, and hybrid memory retrieval.

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
License: CC-BY-4.0
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from symbiosis_architecture import (
    HybridMemory,
    HypothesisStatus,
    NodeType,
    ReflectionLoop,
    SymbiosisArchitecture,
)


def main():
    print("=" * 60)
    print("Symbiosis Co-Reflection Architecture - Demo")
    print("=" * 60)

    # Load reference data
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "symbiosis_data.json"
    )
    with open(data_path) as f:
        data = json.load(f)

    # 1. Build knowledge graph from data
    print("\n--- Build Knowledge Graph ---")
    arch = SymbiosisArchitecture()
    for node_data in data["example_graph"]["nodes"]:
        node = arch.ingest_concept(
            concept_id=node_data["id"],
            label=node_data["label"],
            content=node_data["content"],
        )
        print(f"  Added node: [{node_data['type']}] {node_data['label']}")

    for edge_data in data["example_graph"]["edges"]:
        arch.link_concepts(
            source=edge_data["source"],
            target=edge_data["target"],
            relation=edge_data["relation"],
        )
        print(f"  Linked: {edge_data['source']} --{edge_data['relation']}--> {edge_data['target']}")

    # 2. Run reflection loop
    print("\n--- Reflection Loop ---")
    for ref_data in data["example_reflections"]:
        entry = arch.reflect_on(
            trigger=ref_data["trigger"],
            content=ref_data["content"],
        )
        print(f"  Reflection #{entry.reflection_id}: [{ref_data['trigger']}] {ref_data['content'][:60]}...")

    # 3. Hypothesis tracking
    print("\n--- Hypothesis Tracking ---")
    arch.reflection.propose_hypothesis("regime_validity")
    arch.reflection.propose_hypothesis("cross_domain_ebe")
    arch.reflection.update_hypothesis("regime_validity", HypothesisStatus.SUPPORTED)
    for h_id, status in arch.reflection.hypotheses.items():
        print(f"  {h_id}: {status.value}")
    active = arch.reflection.get_active_hypotheses()
    print(f"  Active hypotheses: {active}")

    # 4. Graph queries
    print("\n--- Graph Queries ---")
    neighbors = arch.memory.get_neighbors("ebe")
    print(f"  Neighbors of 'ebe': {neighbors}")

    concepts = arch.memory.search_nodes(node_type=NodeType.CONCEPT)
    print(f"  All concepts: {[n.label for n in concepts]}")

    # 5. Architecture summary
    print("\n--- Architecture Summary ---")
    summary = arch.summary()
    print(f"  Memory: {summary['memory']}")
    print(f"  Reflections: {summary['reflections']}")
    print(f"  Active hypotheses: {summary['active_hypotheses']}")
    print(f"  Total hypotheses: {summary['total_hypotheses']}")

    # 6. Components
    print("\n--- System Components ---")
    for comp, tech in data["components"].items():
        print(f"  {comp}: {tech}")

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
