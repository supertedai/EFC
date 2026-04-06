"""
CEM -- Consciousness Ego Mirror model.

Models consciousness, ego, and reflection as a feedback structure
within the energy-entropy field.  The mirror metaphor captures how
self-awareness reflects and modulates the local entropy state,
creating a coupled dynamical system between observer and field.

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
License: CC-BY-4.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class AwarenessLevel(Enum):
    """Levels of conscious awareness in the CEM model."""
    UNCONSCIOUS = "unconscious"
    SUBCONSCIOUS = "subconscious"
    CONSCIOUS = "conscious"
    REFLECTIVE = "reflective"
    META_REFLECTIVE = "meta_reflective"


@dataclass
class EgoState:
    """Represents the ego state at a given moment.

    The ego mediates between raw consciousness and the external
    entropy field, acting as a filter/amplifier.

    Attributes:
        identity_coherence: How coherent the ego's self-model is (0-1).
        entropy_coupling: Strength of coupling to the local entropy field (0-1).
        reflection_depth: Number of recursive self-reflection layers.
        awareness: Current awareness level.
        timestamp: Simulation timestep.
    """
    identity_coherence: float = 0.5
    entropy_coupling: float = 0.3
    reflection_depth: int = 0
    awareness: AwarenessLevel = AwarenessLevel.CONSCIOUS
    timestamp: int = 0

    @property
    def mirror_fidelity(self) -> float:
        """How accurately the ego mirrors the entropy field.

        Computed as the product of identity coherence and entropy coupling,
        modulated by reflection depth.
        """
        depth_factor = 1.0 - math.exp(-0.5 * self.reflection_depth)
        return self.identity_coherence * self.entropy_coupling * (0.5 + 0.5 * depth_factor)


@dataclass
class ReflectionFeedback:
    """One cycle of the consciousness-ego-mirror feedback loop.

    Attributes:
        cycle: Cycle number.
        S_input: Entropy input from the field.
        ego_response: The ego's modulated response.
        mirror_output: What is reflected back to the field.
        awareness_level: Awareness during this cycle.
    """
    cycle: int
    S_input: float
    ego_response: float
    mirror_output: float
    awareness_level: AwarenessLevel


class ConsciousnessEgoMirror:
    """The CEM feedback system.

    Models the coupled dynamics between consciousness (observer),
    ego (mediator), and the entropy field (mirror).

    The core feedback equation is:
        S_reflected = alpha * ego.mirror_fidelity * S_field + (1 - alpha) * S_baseline

    where alpha is the coupling strength between the observer
    and the entropy field.

    Attributes:
        ego: Current ego state.
        alpha: Observer-field coupling strength.
        S_baseline: Baseline entropy when decoupled.
        history: Record of all feedback cycles.
    """

    def __init__(
        self,
        alpha: float = 0.5,
        S_baseline: float = 0.5,
        ego: Optional[EgoState] = None,
    ):
        self.alpha = max(0.0, min(1.0, alpha))
        self.S_baseline = S_baseline
        self.ego = ego or EgoState()
        self.history: List[ReflectionFeedback] = []
        self._cycle: int = 0

    def mirror_entropy(self, S_field: float) -> float:
        """Compute the reflected entropy through the ego mirror.

        Args:
            S_field: Current entropy value of the external field.

        Returns:
            The mirrored (reflected) entropy value.
        """
        fidelity = self.ego.mirror_fidelity
        return self.alpha * fidelity * S_field + (1.0 - self.alpha) * self.S_baseline

    def feedback_cycle(self, S_field: float) -> ReflectionFeedback:
        """Execute one full feedback cycle.

        The field entropy is reflected through the ego mirror, producing
        a modulated output that feeds back into the field.

        Args:
            S_field: Input field entropy.

        Returns:
            The ReflectionFeedback for this cycle.
        """
        self._cycle += 1
        self.ego.timestamp = self._cycle

        # Ego response: modulated by awareness level
        awareness_weights = {
            AwarenessLevel.UNCONSCIOUS: 0.1,
            AwarenessLevel.SUBCONSCIOUS: 0.3,
            AwarenessLevel.CONSCIOUS: 0.5,
            AwarenessLevel.REFLECTIVE: 0.7,
            AwarenessLevel.META_REFLECTIVE: 0.9,
        }
        awareness_weight = awareness_weights.get(self.ego.awareness, 0.5)
        ego_response = awareness_weight * S_field

        # Mirror output
        mirror_output = self.mirror_entropy(S_field)

        fb = ReflectionFeedback(
            cycle=self._cycle,
            S_input=S_field,
            ego_response=ego_response,
            mirror_output=mirror_output,
            awareness_level=self.ego.awareness,
        )
        self.history.append(fb)
        return fb

    def deepen_reflection(self) -> None:
        """Increase the ego's reflection depth by one layer."""
        self.ego.reflection_depth += 1
        # Awareness escalates with depth
        levels = list(AwarenessLevel)
        idx = levels.index(self.ego.awareness)
        if idx < len(levels) - 1:
            self.ego.awareness = levels[idx + 1]

    def run_simulation(self, S_field_sequence: List[float]) -> List[ReflectionFeedback]:
        """Run a sequence of feedback cycles.

        Args:
            S_field_sequence: Sequence of field entropy values.

        Returns:
            List of ReflectionFeedback entries.
        """
        results = []
        for S in S_field_sequence:
            fb = self.feedback_cycle(S)
            results.append(fb)
        return results

    def coherence_trajectory(self) -> List[Tuple[int, float]]:
        """Return the mirror fidelity over time from the history."""
        trajectory = []
        for fb in self.history:
            fidelity = fb.mirror_output / fb.S_input if fb.S_input > 0 else 0
            trajectory.append((fb.cycle, fidelity))
        return trajectory

    def summary(self) -> Dict:
        """Return a summary of the CEM system state."""
        return {
            "alpha": self.alpha,
            "S_baseline": self.S_baseline,
            "ego_coherence": self.ego.identity_coherence,
            "ego_coupling": self.ego.entropy_coupling,
            "reflection_depth": self.ego.reflection_depth,
            "awareness": self.ego.awareness.value,
            "mirror_fidelity": self.ego.mirror_fidelity,
            "cycles_completed": len(self.history),
        }


if __name__ == "__main__":
    cem = ConsciousnessEgoMirror(alpha=0.6)
    fb = cem.feedback_cycle(0.5)
    assert 0 <= fb.mirror_output <= 1
    cem.deepen_reflection()
    assert cem.ego.reflection_depth == 1
    print("CEM module OK")
