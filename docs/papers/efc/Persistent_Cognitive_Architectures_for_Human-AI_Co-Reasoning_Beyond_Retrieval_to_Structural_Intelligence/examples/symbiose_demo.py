#!/usr/bin/env python3
"""
Symbiose Cognitive Architecture - Demonstration

This script demonstrates the key concepts from:
Magnusson (2026) "Persistent Cognitive Architectures for Human-AI Co-Reasoning"
DOI: 10.6084/m9.figshare.31271707
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.symbiose_architecture import (
    GraphVectorFusion, EpistemicTagger, MemoryConsolidation, QuantumLeap,
    Source, Chunk, GraphPath, ConversationLog, EPISTEMIC_LEVELS
)


def demo_epistemic_framework():
    """
    Demonstrate the L0-L3 Epistemic Framework.

    The framework distinguishes:
    - L0 (Canonical): Ground truth, verified
    - L1 (Derived): Logical from L0
    - L2 (Supported): Evidence-backed
    - L3 (Inferred): LLM hypothesis
    """
    print("=" * 60)
    print("L0-L3 EPISTEMIC FRAMEWORK DEMONSTRATION")
    print("=" * 60)

    tagger = EpistemicTagger()

    examples = [
        {
            "response": "The EFC transition acceleration is g† = 1.2×10⁻¹⁰ m/s²",
            "sources": [Source("1", "neo4j_canonical", "EFC core constant")],
            "expected": "L0"
        },
        {
            "response": "At Solar surface, |μ-1| = 1.8×10⁻¹³ (8 orders below Cassini)",
            "sources": [
                Source("1", "neo4j_canonical", "g† value"),
                Source("2", "neo4j_derived", "screening calculation")
            ],
            "expected": "L1"
        },
        {
            "response": "BOSS DR12 shows Δχ² = -7.77 improvement for EFC",
            "sources": [
                Source("1", "rag", "BOSS DR12 paper"),
                Source("2", "neo4j_canonical", "EFC model")
            ],
            "expected": "L2"
        },
        {
            "response": "EFC entropy coupling might resolve the S8 tension",
            "sources": [Source("1", "llm", "synthesis")],
            "expected": "L3"
        }
    ]

    for ex in examples:
        result = tagger.tag_response(ex["response"], ex["sources"])
        status = "✓" if result.level.name == ex["expected"] else "✗"
        print(f"\n{status} {result.level.name} ({result.level.value})")
        print(f"  Response: {ex['response'][:60]}...")
        print(f"  Note: {result.note}")

    print("\n" + "-" * 60)
    print("Epistemic Level Definitions:")
    for level, info in EPISTEMIC_LEVELS.items():
        print(f"  {level}: {info['name']} - {info['certainty']}")


def demo_graph_vector_fusion():
    """
    Demonstrate Graph-Vector Fusion Algorithm.

    Combines:
    - Vector similarity (semantic) with weight 0.6
    - Graph path distance (structural) with weight 0.4
    """
    print("\n" + "=" * 60)
    print("GRAPH-VECTOR FUSION DEMONSTRATION")
    print("=" * 60)

    fusion = GraphVectorFusion(semantic_weight=0.6, structural_weight=0.4)

    # Simulated vector search results
    vector_results = [
        Chunk("c1", "EFC entropy-gradient coupling", score=0.92,
              concepts=["entropy", "coupling"]),
        Chunk("c2", "MOND acceleration scale a₀", score=0.85,
              concepts=["MOND", "acceleration"]),
        Chunk("c3", "Hubble tension measurement", score=0.78,
              concepts=["Hubble", "tension"]),
    ]

    # Simulated graph paths
    graph_paths = {
        "c1": [GraphPath(["query", "entropy", "EFC"], length=2)],
        "c2": [GraphPath(["query", "acceleration", "MOND", "EFC"], length=3)],
        "c3": [GraphPath(["query", "Hubble"], length=1)],  # Direct connection
    }

    print("\nBefore fusion (vector similarity only):")
    for chunk in vector_results:
        print(f"  {chunk.id}: semantic={chunk.score:.2f}")

    # Perform fusion
    ranked = fusion.fuse("EFC gravity modification", vector_results, graph_paths)

    print("\nAfter fusion (semantic + structural):")
    for chunk in ranked:
        print(f"  {chunk.id}: fused={chunk.fused_score:.3f}")

    print("\nFusion formula: score = 0.6 × semantic + 0.4 × (1/path_length)")


def demo_memory_consolidation():
    """
    Demonstrate Hierarchical Memory Consolidation.

    Shows the abstraction hierarchy:
    Raw Conversations → Daily → Weekly → Monthly
    """
    print("\n" + "=" * 60)
    print("HIERARCHICAL MEMORY CONSOLIDATION DEMONSTRATION")
    print("=" * 60)

    consolidator = MemoryConsolidation()

    # Simulated day of conversations
    conversations = [
        ConversationLog(
            "2026-02-05T09:00:00",
            ["entropy gradient", "Bullet Cluster", "EFC screening"],
            "Discussed entropy gradient effects on Bullet Cluster..."
        ),
        ConversationLog(
            "2026-02-05T14:00:00",
            ["SPARC validation", "rotation curves", "g† calibration"],
            "Reviewed SPARC175 galaxy rotation curve fits..."
        ),
        ConversationLog(
            "2026-02-05T16:30:00",
            ["entropy gradient", "Solar System", "PPN tests"],
            "Analyzed PPN parameter recovery in Solar System..."
        ),
    ]

    print("\nRaw conversations:")
    for conv in conversations:
        print(f"  {conv.timestamp}: {conv.topics}")

    # Consolidate to daily summary
    daily = consolidator.consolidate_daily(conversations)

    print(f"\nDaily consolidation ({daily.period}):")
    print(f"  Summary: {daily.summary}")
    print(f"  Key topics: {daily.key_topics}")
    print(f"  Insights: {daily.insights}")

    print("\nMemory hierarchy:")
    print("  Monthly Themes ← abstract ← Weekly Summaries ← abstract ← Daily Logs ← abstract ← Raw")


def demo_quantum_leap():
    """
    Demonstrate Quantum Leap (QL) Orchestration.

    Shows how QL coordinates:
    - Epistemic tagging
    - Preference learning
    - Proactive triggers
    """
    print("\n" + "=" * 60)
    print("QUANTUM LEAP (QL) ORCHESTRATION DEMONSTRATION")
    print("=" * 60)

    ql = QuantumLeap()

    print("\nQL Components:")
    print("  1. Session Context Tracker")
    print("  2. Embedding Relevance Scorer")
    print("  3. Graph-Vector Fusion")
    print("  4. Preference Learner")
    print("  5. Emergent Reasoning")
    print("  6. Causal Understanding")
    print("  7. Continuous Memory")

    # Demonstrate preference learning
    print("\nPreference Learning (Bayesian updates):")
    print(f"  Initial preference for 'research': {ql.preferences.get('research', 0.5):.2f}")

    ql.update_preference("research", accepted=True, context=["EFC", "validation"])
    print(f"  After accept: {ql.preferences['research']:.2f}")

    ql.update_preference("research", accepted=True, context=["SPARC", "analysis"])
    print(f"  After another accept: {ql.preferences['research']:.2f}")

    ql.update_preference("research", accepted=False, context=["unrelated"])
    print(f"  After reject: {ql.preferences['research']:.2f}")

    # Demonstrate response processing
    print("\nResponse Processing:")
    sources = [
        Source("1", "neo4j_canonical", "EFC model"),
        Source("2", "rag", "DESI DR2 paper")
    ]
    response = ql.process_response(
        "DESI DR2 BAO data shows preference for EFC transition at z≈1",
        sources
    )
    print(f"  Level: {response.level.value}")
    print(f"  Note: {response.note}")


def demo_architectural_shift():
    """
    Illustrate the architectural shift from traditional AI to Symbiose.
    """
    print("\n" + "=" * 60)
    print("ARCHITECTURAL SHIFT: TRADITIONAL → SYMBIOSE")
    print("=" * 60)

    comparison = [
        ("Response-based", "Initiative-based"),
        ("Stateless", "Persistent"),
        ("RAG retrieval", "Structural + temporal"),
        ("Query → answer", "Context → anticipation"),
    ]

    print("\n{:<25} {:<25}".format("Traditional AI", "Symbiose/QL"))
    print("-" * 50)
    for trad, symb in comparison:
        print("{:<25} {:<25}".format(trad, symb))

    print("\nKey insight: Symbiose shifts from RETRIEVAL to REASONING")
    print("  • From 'what documents match?' to 'what patterns emerge?'")


def main():
    """Run all demonstrations."""
    print("\n" + "#" * 60)
    print("# SYMBIOSE COGNITIVE ARCHITECTURE DEMONSTRATION")
    print("# From: Magnusson (2026)")
    print("# DOI: 10.6084/m9.figshare.31271707")
    print("#" * 60)

    demo_epistemic_framework()
    demo_graph_vector_fusion()
    demo_memory_consolidation()
    demo_quantum_leap()
    demo_architectural_shift()

    print("\n" + "=" * 60)
    print("IMPORTANT: This is NOT AGI")
    print("=" * 60)
    print("Symbiose is a cognitive architecture for COLLABORATION:")
    print("  • Domain-bounded (operates within specific domains)")
    print("  • Human-in-the-loop (requires human judgment)")
    print("  • No autonomous goal-setting")
    print("  • Explainable by design (traceable reasoning)")
    print("\nSymbiose AUGMENTS human cognition, it does not replace it.")


if __name__ == "__main__":
    main()
