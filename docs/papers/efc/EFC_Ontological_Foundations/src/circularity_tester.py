"""
Circularity Tester Implementation

Tests definitions and hypotheses for circular dependencies.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CircularityResult:
    """Result of a circularity test."""
    concept_a: str
    concept_b: str
    is_circular: bool
    dependency_chain: list[str]
    explanation: str


@dataclass
class Definition:
    """A concept definition with its dependencies."""
    concept: str
    definition: str
    requires: list[str]  # Concepts required by this definition


class CircularityTester:
    """
    Tests for circular dependencies in concept definitions.

    A definition is circular if concept A requires concept B,
    and concept B (directly or indirectly) requires concept A.

    Example:
        tester = CircularityTester()
        tester.add_definition(Definition(
            concept="energy_flow",
            definition="Directed transfer of energy",
            requires=["energy", "direction", "time"]
        ))
        tester.add_definition(Definition(
            concept="direction",
            definition="Determined by entropy increase",
            requires=["entropy", "time"]
        ))
        result = tester.test("energy_flow", "entropy")
    """

    def __init__(self):
        """Initialize the circularity tester."""
        self.definitions: dict[str, Definition] = {}

    def add_definition(self, definition: Definition) -> None:
        """Add a definition to the tester."""
        self.definitions[definition.concept.lower()] = definition

    def get_dependencies(self, concept: str) -> list[str]:
        """Get direct dependencies of a concept."""
        defn = self.definitions.get(concept.lower())
        if defn:
            return [r.lower() for r in defn.requires]
        return []

    def find_dependency_chain(
        self,
        start: str,
        target: str,
        visited: Optional[set] = None
    ) -> Optional[list[str]]:
        """
        Find a dependency chain from start to target.

        Args:
            start: Starting concept
            target: Target concept
            visited: Set of visited concepts (for recursion)

        Returns:
            Chain of concepts if found, None otherwise
        """
        if visited is None:
            visited = set()

        start_lower = start.lower()
        target_lower = target.lower()

        if start_lower in visited:
            return None

        visited.add(start_lower)

        deps = self.get_dependencies(start_lower)

        if target_lower in deps:
            return [start_lower, target_lower]

        for dep in deps:
            chain = self.find_dependency_chain(dep, target, visited.copy())
            if chain:
                return [start_lower] + chain

        return None

    def test(self, concept_a: str, concept_b: str) -> CircularityResult:
        """
        Test if two concepts have circular dependency.

        Args:
            concept_a: First concept
            concept_b: Second concept

        Returns:
            CircularityResult with test outcome
        """
        # Check A -> B
        chain_a_to_b = self.find_dependency_chain(concept_a, concept_b)

        # Check B -> A
        chain_b_to_a = self.find_dependency_chain(concept_b, concept_a)

        is_circular = chain_a_to_b is not None and chain_b_to_a is not None

        if is_circular:
            # Combine chains to show full cycle
            full_chain = chain_a_to_b + chain_b_to_a[1:]
            explanation = (
                f"Circular dependency detected:\n"
                f"  {concept_a} → ... → {concept_b}\n"
                f"  {concept_b} → ... → {concept_a}"
            )
        else:
            full_chain = []
            if chain_a_to_b:
                explanation = f"{concept_a} depends on {concept_b}, but not vice versa"
            elif chain_b_to_a:
                explanation = f"{concept_b} depends on {concept_a}, but not vice versa"
            else:
                explanation = f"No dependency found between {concept_a} and {concept_b}"

        return CircularityResult(
            concept_a=concept_a,
            concept_b=concept_b,
            is_circular=is_circular,
            dependency_chain=full_chain,
            explanation=explanation,
        )

    def test_all(self) -> list[CircularityResult]:
        """
        Test all pairs of concepts for circularity.

        Returns:
            List of all circular dependencies found
        """
        results = []
        concepts = list(self.definitions.keys())

        for i, a in enumerate(concepts):
            for b in concepts[i + 1:]:
                result = self.test(a, b)
                if result.is_circular:
                    results.append(result)

        return results


def test_definition(
    concept: str,
    definition: str,
    requires: list[str],
    existing_definitions: dict[str, list[str]]
) -> CircularityResult:
    """
    Convenience function to test a single definition.

    Args:
        concept: The concept being defined
        definition: The definition text (for documentation)
        requires: Concepts required by this definition
        existing_definitions: Dict of concept -> requirements

    Returns:
        CircularityResult if circular dependency found with any existing
    """
    tester = CircularityTester()

    # Add existing definitions
    for c, reqs in existing_definitions.items():
        tester.add_definition(Definition(concept=c, definition="", requires=reqs))

    # Add new definition
    tester.add_definition(Definition(
        concept=concept,
        definition=definition,
        requires=requires
    ))

    # Test against all existing
    for existing in existing_definitions:
        result = tester.test(concept, existing)
        if result.is_circular:
            return result

    # No circularity found
    return CircularityResult(
        concept_a=concept,
        concept_b="(any)",
        is_circular=False,
        dependency_chain=[],
        explanation="No circular dependencies found",
    )
