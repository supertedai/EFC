"""Energy Flow as the Fundamental Dynamic of the Universe.

Core module presenting the central EFC claim: energy flow (Ef) is the
primary dynamic shaping structure, motion, and the observable universe,
rather than mass or spacetime curvature.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class EnergyFlowField:
    """The energy-flow field Ef at a point in space.

    Ef is a vector field with units W/m^2 representing the local
    energy current density that, in EFC, replaces gravitational
    potential as the fundamental quantity.
    """

    ef_x: float = 0.0  # W/m^2
    ef_y: float = 0.0
    ef_z: float = 0.0

    @property
    def magnitude(self) -> float:
        return math.sqrt(self.ef_x**2 + self.ef_y**2 + self.ef_z**2)

    @property
    def direction(self) -> tuple:
        """Unit vector of Ef, or (0,0,0) if magnitude is zero."""
        m = self.magnitude
        if m == 0:
            return (0.0, 0.0, 0.0)
        return (self.ef_x / m, self.ef_y / m, self.ef_z / m)

    def entropy_gradient_proxy(self, temperature: float) -> float:
        """Estimate entropy gradient |nabla S| ~ |Ef| / T."""
        if temperature == 0:
            return float("inf")
        return self.magnitude / temperature

    def summary(self) -> str:
        return (f"Ef = ({self.ef_x:.2e}, {self.ef_y:.2e}, {self.ef_z:.2e}) W/m^2, "
                f"|Ef| = {self.magnitude:.2e} W/m^2")


@dataclass
class EFCCorePrinciple:
    """A core principle of the Energy-Flow Cosmology framework."""

    name: str
    statement: str
    implications: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [f"Principle: {self.name}", f"  {self.statement}"]
        for imp in self.implications:
            lines.append(f"  -> {imp}")
        return "\n".join(lines)


class FundamentalDynamics:
    """Access class for the fundamental-dynamic paper's concepts.

    Presents core principles, the Ef field, and key predictions that
    distinguish EFC from standard LCDM cosmology.
    """

    def __init__(self) -> None:
        self.principles: List[EFCCorePrinciple] = []
        self.predictions: List[str] = []
        self._init_defaults()

    def _init_defaults(self) -> None:
        self.principles = [
            EFCCorePrinciple(
                "Energy-Flow Primacy",
                "Energy flow (Ef) is the fundamental dynamic; mass and curvature are emergent.",
                ["Gravity is a manifestation of Ef gradients",
                 "Dark matter effects arise from non-local Ef patterns"]),
            EFCCorePrinciple(
                "Entropy-Gradient Structuring",
                "Cosmic structure forms along entropy gradients, not from initial density seeds alone.",
                ["Filaments trace maximal entropy flux channels",
                 "Voids are regions of minimal Ef"]),
            EFCCorePrinciple(
                "Observable Universality",
                "All observable phenomena can be described in terms of Ef and its derivatives.",
                ["Unification of forces as Ef coupling modes",
                 "Cosmological expansion as large-scale Ef divergence"]),
        ]
        self.predictions = [
            "Galaxy rotation curves follow Ef gradient profiles without dark matter",
            "Cosmic expansion rate correlates with total entropy production rate",
            "Gravitational lensing strength depends on Ef magnitude, not mass alone",
            "Structure formation timing predicted by entropy-gradient evolution",
        ]

    def evaluate_ef(self, ef_x: float, ef_y: float, ef_z: float,
                    temperature: float = 2.725) -> Dict[str, float]:
        """Evaluate key quantities from an Ef vector."""
        ef = EnergyFlowField(ef_x, ef_y, ef_z)
        return {
            "magnitude_W_m2": ef.magnitude,
            "entropy_gradient_proxy": ef.entropy_gradient_proxy(temperature),
            "direction": ef.direction,
        }

    def summary(self) -> str:
        lines = ["Energy Flow as the Fundamental Dynamic (EFC)",
                 f"  Core principles: {len(self.principles)}",
                 f"  Predictions: {len(self.predictions)}", ""]
        for p in self.principles:
            lines.append(p.summary())
            lines.append("")
        lines.append("Predictions:")
        for pred in self.predictions:
            lines.append(f"  * {pred}")
        return "\n".join(lines)
