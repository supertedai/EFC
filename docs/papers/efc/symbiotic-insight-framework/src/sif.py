"""
Symbiotic Insight Framework (SIF).

Models high-velocity, cross-domain scientific insight production as a
coupled process between a human thinker and an adaptive computational
system.  The human generates parallel conceptual fields at high speed
while the system stabilises, structures, and preserves them.

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
License: CC-BY-4.0
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class FieldState(Enum):
    """State of a conceptual insight field."""
    RAW = "raw"
    STABILISED = "stabilised"
    STRUCTURED = "structured"
    PRESERVED = "preserved"


@dataclass
class InsightField:
    """A single conceptual field generated during high-velocity reasoning.

    Attributes:
        label: Short identifier for the insight.
        domain: Scientific domain the insight belongs to.
        content: Textual description of the insight.
        state: Current stabilisation state.
        timestamp: Unix timestamp of creation.
        coherence: Coherence score (0-1) assigned during stabilisation.
        connections: Labels of connected insight fields.
    """
    label: str
    domain: str
    content: str
    state: FieldState = FieldState.RAW
    timestamp: float = field(default_factory=time.time)
    coherence: float = 0.0
    connections: List[str] = field(default_factory=list)

    def stabilise(self, coherence: float) -> None:
        """Stabilise the insight field with a coherence score.

        Args:
            coherence: Coherence metric between 0 and 1.
        """
        self.coherence = max(0.0, min(1.0, coherence))
        self.state = FieldState.STABILISED

    def structure(self) -> None:
        """Promote the field to structured state."""
        if self.state == FieldState.STABILISED:
            self.state = FieldState.STRUCTURED

    def preserve(self) -> None:
        """Promote the field to preserved (archival) state."""
        if self.state == FieldState.STRUCTURED:
            self.state = FieldState.PRESERVED

    def connect(self, other_label: str) -> None:
        """Register a cross-field connection."""
        if other_label not in self.connections:
            self.connections.append(other_label)


@dataclass
class StabilisationCycle:
    """One full cycle of insight generation and stabilisation.

    Attributes:
        cycle_id: Sequential cycle identifier.
        fields_in: Number of raw fields entering the cycle.
        fields_out: Number of stabilised fields exiting.
        mean_coherence: Average coherence across stabilised fields.
        duration_s: Cycle wall-clock duration in seconds.
    """
    cycle_id: int
    fields_in: int = 0
    fields_out: int = 0
    mean_coherence: float = 0.0
    duration_s: float = 0.0

    @property
    def stabilisation_rate(self) -> float:
        """Fraction of input fields successfully stabilised."""
        return self.fields_out / self.fields_in if self.fields_in > 0 else 0.0


class SymbioticInsightFramework:
    """Top-level framework coupling human high-velocity insight generation
    with computational stabilisation.

    The framework tracks insight fields, organises stabilisation cycles,
    and computes productivity metrics.

    Attributes:
        fields: All registered insight fields.
        cycles: Completed stabilisation cycles.
    """

    def __init__(self):
        self.fields: List[InsightField] = []
        self.cycles: List[StabilisationCycle] = []
        self._cycle_counter: int = 0

    def generate_field(self, label: str, domain: str, content: str) -> InsightField:
        """Create and register a new raw insight field.

        Args:
            label: Short identifier.
            domain: Scientific domain.
            content: Insight description.

        Returns:
            The newly created InsightField.
        """
        f = InsightField(label=label, domain=domain, content=content)
        self.fields.append(f)
        return f

    def run_stabilisation_cycle(self, coherence_threshold: float = 0.5) -> StabilisationCycle:
        """Run one stabilisation cycle on all RAW fields.

        Each raw field is assigned a coherence score based on its content
        length (a simple heuristic proxy).  Fields above the threshold
        are stabilised.

        Args:
            coherence_threshold: Minimum coherence to stabilise.

        Returns:
            The completed StabilisationCycle.
        """
        self._cycle_counter += 1
        raw_fields = [f for f in self.fields if f.state == FieldState.RAW]
        stabilised = 0
        coherences = []
        for f in raw_fields:
            # Heuristic: longer content tends to be more coherent
            c = min(1.0, len(f.content) / 200.0)
            if c >= coherence_threshold:
                f.stabilise(c)
                stabilised += 1
                coherences.append(c)
        cycle = StabilisationCycle(
            cycle_id=self._cycle_counter,
            fields_in=len(raw_fields),
            fields_out=stabilised,
            mean_coherence=(sum(coherences) / len(coherences)) if coherences else 0.0,
        )
        self.cycles.append(cycle)
        return cycle

    def structure_all(self) -> int:
        """Promote all stabilised fields to structured state.

        Returns:
            Number of fields promoted.
        """
        count = 0
        for f in self.fields:
            if f.state == FieldState.STABILISED:
                f.structure()
                count += 1
        return count

    def preserve_all(self) -> int:
        """Promote all structured fields to preserved state.

        Returns:
            Number of fields preserved.
        """
        count = 0
        for f in self.fields:
            if f.state == FieldState.STRUCTURED:
                f.preserve()
                count += 1
        return count

    def insight_velocity(self) -> float:
        """Compute the overall insight velocity (fields per cycle)."""
        if not self.cycles:
            return 0.0
        return len(self.fields) / len(self.cycles)

    def cross_domain_connections(self) -> Dict[str, List[str]]:
        """Map each field to its cross-domain connections."""
        return {f.label: f.connections for f in self.fields if f.connections}

    def summary(self) -> Dict:
        """Return a summary of the framework state."""
        state_counts = {}
        for f in self.fields:
            state_counts[f.state.value] = state_counts.get(f.state.value, 0) + 1
        return {
            "total_fields": len(self.fields),
            "state_distribution": state_counts,
            "cycles_completed": len(self.cycles),
            "insight_velocity": self.insight_velocity(),
        }


if __name__ == "__main__":
    sif = SymbioticInsightFramework()
    f1 = sif.generate_field("test", "physics", "A test insight with enough content to be coherent for stabilisation purposes in our demo run.")
    cycle = sif.run_stabilisation_cycle(0.3)
    assert cycle.fields_out == 1
    print("SIF module OK")
