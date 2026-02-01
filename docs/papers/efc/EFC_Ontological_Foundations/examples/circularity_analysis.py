#!/usr/bin/env python3
"""
EFC Ontological Foundations - Circularity Analysis Example

Demonstrates the circularity testing of the three hypotheses.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from circularity_tester import CircularityTester, Definition
from hypothesis_analyzer import HypothesisAnalyzer, HypothesisID, compare_hypotheses
from ontology_model import CoPrimaryModel, create_standard_model


def main():
    """Run circularity analysis examples."""
    print("=" * 60)
    print("EFC Ontological Foundations - Circularity Analysis")
    print("=" * 60)
    print()

    # Example 1: Basic Circularity Test
    print("Example 1: Basic Circularity Test")
    print("-" * 40)

    tester = CircularityTester()

    # Add definitions that form a cycle
    tester.add_definition(Definition(
        concept="energy_flow",
        definition="Directed transfer of energy",
        requires=["energy", "direction"]
    ))
    tester.add_definition(Definition(
        concept="direction",
        definition="Arrow of time from entropy increase",
        requires=["entropy", "time"]
    ))
    tester.add_definition(Definition(
        concept="entropy",
        definition="Measure of energy dispersal",
        requires=["energy"]
    ))

    result = tester.test("energy_flow", "entropy")
    print(f"Testing: energy_flow ↔ entropy")
    print(f"  Circular: {result.is_circular}")
    print(f"  Explanation: {result.explanation}")
    print()

    # Example 2: Analyze All Hypotheses
    print("Example 2: Hypothesis Analysis")
    print("-" * 40)

    analyzer = HypothesisAnalyzer()

    for h_id in HypothesisID:
        result = analyzer.analyze(h_id)
        status = "✓" if result.passes_circularity_test else "✗"
        print(f"{status} {h_id.value}: {result.name}")
        if result.failure_reason:
            print(f"    Reason: {result.failure_reason}")
    print()

    # Example 3: Compare Hypotheses
    print("Example 3: Full Comparison")
    print("-" * 40)
    print(compare_hypotheses())
    print()

    # Example 4: Co-Primary Model
    print("Example 4: Co-Primary Model")
    print("-" * 40)

    model = create_standard_model()
    print(model.summary())


if __name__ == "__main__":
    main()
