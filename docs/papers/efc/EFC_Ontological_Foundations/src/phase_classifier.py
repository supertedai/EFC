"""
Phase Classifier Implementation

Classifies phenomena by their ontological phase relative to
the Planck transition.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Phase(Enum):
    """Ontological phases."""
    PRE_PLANCK = "pre_planck"
    PLANCK_TRANSITION = "planck_transition"
    POST_PLANCK = "post_planck"


@dataclass
class PhaseInfo:
    """Information about a phase."""
    phase: Phase
    name: str
    description: str
    physics_applicable: bool
    observables: list[str]


@dataclass
class ClassificationResult:
    """Result of phase classification."""
    phenomenon: str
    phase: Phase
    phase_info: PhaseInfo
    reasoning: str


class PhaseClassifier:
    """
    Classifier for ontological phases.

    Phases:
    - Pre-Planck: Before differentiation, no standard physics
    - Planck Transition: The differentiation point
    - Post-Planck: Standard physics applies

    Example:
        classifier = PhaseClassifier()
        result = classifier.classify("galaxy_rotation")
        print(f"Phase: {result.phase.value}")
    """

    PHASE_DEFINITIONS = {
        Phase.PRE_PLANCK: PhaseInfo(
            phase=Phase.PRE_PLANCK,
            name="Pre-Planck Phase",
            description="Undifferentiated potential, before spacetime",
            physics_applicable=False,
            observables=[],
        ),
        Phase.PLANCK_TRANSITION: PhaseInfo(
            phase=Phase.PLANCK_TRANSITION,
            name="Planck Transition",
            description="Differentiation point, emergence of spacetime",
            physics_applicable=False,
            observables=["planck_scale_physics"],
        ),
        Phase.POST_PLANCK: PhaseInfo(
            phase=Phase.POST_PLANCK,
            name="Post-Planck Phase",
            description="Standard physics regime, EF and S differentiated",
            physics_applicable=True,
            observables=["energy", "entropy", "spacetime", "matter", "radiation"],
        ),
    }

    # Keywords for classification
    PHASE_KEYWORDS = {
        Phase.PRE_PLANCK: ["pre-geometric", "undifferentiated", "timeless", "pre-planck"],
        Phase.PLANCK_TRANSITION: ["planck", "emergence", "transition", "differentiation"],
        Phase.POST_PLANCK: ["observable", "measurement", "energy", "entropy", "spacetime",
                           "galaxy", "star", "particle", "field", "matter"],
    }

    def __init__(self):
        """Initialize the phase classifier."""
        pass

    def classify(self, phenomenon: str) -> ClassificationResult:
        """
        Classify a phenomenon by phase.

        Args:
            phenomenon: Description of the phenomenon

        Returns:
            ClassificationResult with phase assignment
        """
        phenomenon_lower = phenomenon.lower()

        # Check keywords
        for phase, keywords in self.PHASE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in phenomenon_lower:
                    return ClassificationResult(
                        phenomenon=phenomenon,
                        phase=phase,
                        phase_info=self.PHASE_DEFINITIONS[phase],
                        reasoning=f"Contains keyword '{keyword}'",
                    )

        # Default to post-Planck for unrecognized phenomena
        return ClassificationResult(
            phenomenon=phenomenon,
            phase=Phase.POST_PLANCK,
            phase_info=self.PHASE_DEFINITIONS[Phase.POST_PLANCK],
            reasoning="Default: assumed observable/physical phenomenon",
        )

    def classify_by_scale(self, length_scale: float) -> ClassificationResult:
        """
        Classify by length scale.

        Args:
            length_scale: Characteristic length in meters

        Returns:
            ClassificationResult
        """
        PLANCK_LENGTH = 1.616e-35  # meters

        if length_scale < PLANCK_LENGTH:
            phase = Phase.PRE_PLANCK
            reasoning = f"Scale {length_scale:.2e} m < Planck length"
        elif length_scale < 10 * PLANCK_LENGTH:
            phase = Phase.PLANCK_TRANSITION
            reasoning = f"Scale {length_scale:.2e} m ~ Planck length"
        else:
            phase = Phase.POST_PLANCK
            reasoning = f"Scale {length_scale:.2e} m > Planck length"

        return ClassificationResult(
            phenomenon=f"scale_{length_scale:.2e}",
            phase=phase,
            phase_info=self.PHASE_DEFINITIONS[phase],
            reasoning=reasoning,
        )

    def get_phase(self, phase: Phase) -> PhaseInfo:
        """Get information about a specific phase."""
        return self.PHASE_DEFINITIONS[phase]

    def can_apply_physics(self, phase: Phase) -> bool:
        """Check if standard physics applies in this phase."""
        return self.PHASE_DEFINITIONS[phase].physics_applicable

    def summary(self) -> str:
        """Get summary of all phases."""
        lines = ["Ontological Phases:", "=" * 40]

        for phase in Phase:
            info = self.PHASE_DEFINITIONS[phase]
            physics = "Yes" if info.physics_applicable else "No"
            lines.extend([
                f"",
                f"{phase.value}:",
                f"  Name: {info.name}",
                f"  Description: {info.description}",
                f"  Standard physics: {physics}",
            ])

        return "\n".join(lines)
