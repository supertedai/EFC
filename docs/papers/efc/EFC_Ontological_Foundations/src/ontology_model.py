"""
Ontology Model Implementation

Models the co-primary structure and differentiation process.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class OntologicalStatus(Enum):
    """Status of an ontological entity."""
    UNDIFFERENTIATED = "undifferentiated"
    DIFFERENTIATING = "differentiating"
    DIFFERENTIATED = "differentiated"


@dataclass
class Aspect:
    """An aspect of the differentiated potential."""
    name: str
    description: str
    status: OntologicalStatus
    emerges_from: Optional[str] = None


@dataclass
class Differentiation:
    """The differentiation process."""
    source: str
    products: list[Aspect]
    mechanism: str
    phase: str


class CoPrimaryModel:
    """
    Model of the co-primary ontological structure.

    In this model:
    - Pre-geometric potential is the undifferentiated source
    - Energy-flow (EF) and Entropy (S) are differentiated aspects
    - Neither EF nor S is primary; both emerge together

    Example:
        model = CoPrimaryModel()
        model.differentiate()
        print(model.summary())
    """

    def __init__(self):
        """Initialize the co-primary model."""
        self.source = Aspect(
            name="pre_geometric_potential",
            description="Undifferentiated substrate before Planck transition",
            status=OntologicalStatus.UNDIFFERENTIATED,
        )

        self.energy_flow = Aspect(
            name="energy_flow",
            description="Directed aspect of differentiated potential",
            status=OntologicalStatus.UNDIFFERENTIATED,
            emerges_from="pre_geometric_potential",
        )

        self.entropy = Aspect(
            name="entropy",
            description="Statistical aspect of differentiated potential",
            status=OntologicalStatus.UNDIFFERENTIATED,
            emerges_from="pre_geometric_potential",
        )

        self.differentiation: Optional[Differentiation] = None

    def differentiate(self) -> Differentiation:
        """
        Execute the differentiation process.

        This represents the Planck transition where the undifferentiated
        potential becomes differentiated into EF and S aspects.

        Returns:
            Differentiation record
        """
        # Update status
        self.source.status = OntologicalStatus.DIFFERENTIATING
        self.energy_flow.status = OntologicalStatus.DIFFERENTIATED
        self.entropy.status = OntologicalStatus.DIFFERENTIATED

        # Create differentiation record
        self.differentiation = Differentiation(
            source="pre_geometric_potential",
            products=[self.energy_flow, self.entropy],
            mechanism="Planck-scale transition",
            phase="planck_transition",
        )

        return self.differentiation

    def is_differentiated(self) -> bool:
        """Check if differentiation has occurred."""
        return self.differentiation is not None

    def get_aspect(self, name: str) -> Optional[Aspect]:
        """Get an aspect by name."""
        aspects = {
            "pre_geometric_potential": self.source,
            "energy_flow": self.energy_flow,
            "entropy": self.entropy,
        }
        return aspects.get(name.lower())

    def verify_co_primacy(self) -> tuple[bool, str]:
        """
        Verify that the model satisfies co-primacy.

        Co-primacy means:
        1. Neither EF nor S is derived from the other
        2. Both emerge from the same source
        3. Neither is ontologically prior

        Returns:
            Tuple of (is_valid, explanation)
        """
        if not self.is_differentiated():
            return False, "Model not yet differentiated"

        # Check emergence
        ef_source = self.energy_flow.emerges_from
        s_source = self.entropy.emerges_from

        if ef_source != s_source:
            return False, "EF and S have different sources - not co-primary"

        if ef_source == "entropy" or s_source == "energy_flow":
            return False, "One aspect derives from the other - not co-primary"

        return True, "Co-primacy verified: EF and S are symmetric aspects"

    def summary(self) -> str:
        """Get human-readable summary of the model."""
        lines = [
            "Co-Primary Ontological Model",
            "=" * 40,
            "",
            f"Source: {self.source.name}",
            f"  Status: {self.source.status.value}",
            f"  Description: {self.source.description}",
            "",
            "Differentiated Aspects:",
            f"  1. {self.energy_flow.name}",
            f"     Status: {self.energy_flow.status.value}",
            f"     Emerges from: {self.energy_flow.emerges_from}",
            f"  2. {self.entropy.name}",
            f"     Status: {self.entropy.status.value}",
            f"     Emerges from: {self.entropy.emerges_from}",
        ]

        if self.differentiation:
            lines.extend([
                "",
                "Differentiation:",
                f"  Mechanism: {self.differentiation.mechanism}",
                f"  Phase: {self.differentiation.phase}",
            ])

        # Verify co-primacy
        is_valid, explanation = self.verify_co_primacy()
        lines.extend([
            "",
            f"Co-primacy: {'Verified' if is_valid else 'Not verified'}",
            f"  {explanation}",
        ])

        return "\n".join(lines)


def create_standard_model() -> CoPrimaryModel:
    """
    Create and differentiate a standard co-primary model.

    Returns:
        Differentiated CoPrimaryModel
    """
    model = CoPrimaryModel()
    model.differentiate()
    return model
