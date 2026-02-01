"""
Hypothesis Analyzer Implementation

Analyzes the three ontological hypotheses (H1, H2, H3) for
consistency and circularity.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .circularity_tester import CircularityTester, Definition, CircularityResult


class HypothesisID(Enum):
    """The three hypotheses."""
    H1 = "H1"  # Energy-Flow Primacy
    H2 = "H2"  # Entropy Primacy
    H3 = "H3"  # Co-Primary Structure


@dataclass
class Hypothesis:
    """An ontological hypothesis."""
    id: HypothesisID
    name: str
    description: str
    primacy_claim: str
    definitions: list[Definition]


@dataclass
class AnalysisResult:
    """Result of hypothesis analysis."""
    hypothesis: HypothesisID
    name: str
    passes_circularity_test: bool
    circularity_results: list[CircularityResult]
    failure_reason: Optional[str]
    summary: str


class HypothesisAnalyzer:
    """
    Analyzer for the three ontological hypotheses.

    H1: Energy-Flow Primacy - Energy-flow is fundamental, entropy emerges
    H2: Entropy Primacy - Entropy is fundamental, energy-flow emerges
    H3: Co-Primary Structure - Both emerge from pre-geometric potential

    Example:
        analyzer = HypothesisAnalyzer()
        result = analyzer.analyze(HypothesisID.H1)
        print(f"H1 passes: {result.passes_circularity_test}")
    """

    HYPOTHESES = {
        HypothesisID.H1: Hypothesis(
            id=HypothesisID.H1,
            name="Energy-Flow Primacy",
            description="Energy-flow is the fundamental concept; entropy emerges from it",
            primacy_claim="energy_flow",
            definitions=[
                Definition(
                    concept="energy_flow",
                    definition="Directed transfer of energy through spacetime",
                    requires=["energy", "direction", "spacetime"]
                ),
                Definition(
                    concept="direction",
                    definition="Determined by the arrow of time / entropy increase",
                    requires=["time", "entropy"]
                ),
                Definition(
                    concept="entropy",
                    definition="Measure of energy dispersal",
                    requires=["energy", "probability"]
                ),
            ]
        ),
        HypothesisID.H2: Hypothesis(
            id=HypothesisID.H2,
            name="Entropy Primacy",
            description="Entropy is the fundamental concept; energy-flow emerges from it",
            primacy_claim="entropy",
            definitions=[
                Definition(
                    concept="entropy",
                    definition="Fundamental measure of microstates",
                    requires=["microstates", "probability"]
                ),
                Definition(
                    concept="microstates",
                    definition="Possible configurations of energy",
                    requires=["energy", "configuration"]
                ),
                Definition(
                    concept="energy",
                    definition="Capacity to do work, drive change",
                    requires=["work", "change"]
                ),
                Definition(
                    concept="change",
                    definition="Transition between states with different entropy",
                    requires=["entropy", "time"]
                ),
            ]
        ),
        HypothesisID.H3: Hypothesis(
            id=HypothesisID.H3,
            name="Co-Primary Structure",
            description="EF and S emerge together from pre-geometric potential",
            primacy_claim="pre_geometric_potential",
            definitions=[
                Definition(
                    concept="pre_geometric_potential",
                    definition="Undifferentiated substrate before Planck scale",
                    requires=[]  # No prior concepts needed
                ),
                Definition(
                    concept="differentiation",
                    definition="Process by which distinct aspects emerge",
                    requires=["pre_geometric_potential"]
                ),
                Definition(
                    concept="energy_flow",
                    definition="One aspect of differentiated potential",
                    requires=["differentiation"]
                ),
                Definition(
                    concept="entropy",
                    definition="Other aspect of differentiated potential",
                    requires=["differentiation"]
                ),
            ]
        ),
    }

    def __init__(self):
        """Initialize the analyzer."""
        pass

    def analyze(self, hypothesis_id: HypothesisID) -> AnalysisResult:
        """
        Analyze a hypothesis for circularity.

        Args:
            hypothesis_id: Which hypothesis to analyze

        Returns:
            AnalysisResult with detailed analysis
        """
        hypothesis = self.HYPOTHESES[hypothesis_id]

        # Build circularity tester
        tester = CircularityTester()
        for defn in hypothesis.definitions:
            tester.add_definition(defn)

        # Test for circularity
        circular_results = tester.test_all()

        passes = len(circular_results) == 0

        if not passes:
            failure_reason = "; ".join(
                f"{r.concept_a} ↔ {r.concept_b}"
                for r in circular_results
            )
        else:
            failure_reason = None

        # Build summary
        summary = self._build_summary(hypothesis, passes, circular_results)

        return AnalysisResult(
            hypothesis=hypothesis_id,
            name=hypothesis.name,
            passes_circularity_test=passes,
            circularity_results=circular_results,
            failure_reason=failure_reason,
            summary=summary,
        )

    def analyze_all(self) -> dict[HypothesisID, AnalysisResult]:
        """
        Analyze all three hypotheses.

        Returns:
            Dict mapping hypothesis ID to analysis result
        """
        return {
            h_id: self.analyze(h_id)
            for h_id in HypothesisID
        }

    def _build_summary(
        self,
        hypothesis: Hypothesis,
        passes: bool,
        circular: list[CircularityResult]
    ) -> str:
        """Build human-readable summary."""
        status = "PASSES" if passes else "FAILS"

        lines = [
            f"Hypothesis {hypothesis.id.value}: {hypothesis.name}",
            f"Status: {status}",
            f"",
            f"Primacy claim: {hypothesis.primacy_claim}",
            f"Description: {hypothesis.description}",
            f"",
            f"Definitions:",
        ]

        for defn in hypothesis.definitions:
            req_str = ", ".join(defn.requires) if defn.requires else "(none)"
            lines.append(f"  {defn.concept}: requires [{req_str}]")

        if circular:
            lines.append("")
            lines.append("Circular dependencies found:")
            for r in circular:
                lines.append(f"  {r.concept_a} ↔ {r.concept_b}")

        return "\n".join(lines)


def compare_hypotheses() -> str:
    """
    Compare all three hypotheses and return summary.

    Returns:
        Formatted comparison string
    """
    analyzer = HypothesisAnalyzer()
    results = analyzer.analyze_all()

    lines = [
        "=" * 60,
        "Ontological Hypothesis Comparison",
        "=" * 60,
        "",
    ]

    for h_id in HypothesisID:
        result = results[h_id]
        status = "✓ PASSES" if result.passes_circularity_test else "✗ FAILS"
        lines.append(f"{h_id.value} ({result.name}): {status}")
        if result.failure_reason:
            lines.append(f"    Reason: {result.failure_reason}")

    lines.append("")
    lines.append("Conclusion: Only H3 (Co-Primary Structure) passes the circularity test")

    return "\n".join(lines)
