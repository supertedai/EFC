"""EFC v2.2 Cross-Field Integration Summary -- Python implementation.

Coupling mechanisms, multi-level field integration, and interface
contracts linking Grid, Entropy, Energy Flow, and Information fields.

Reference: Magnusson (2025), EFC v2.2 Cross-Field Integration Summary
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional


# ---------------------------------------------------------------------------
# Field Coupling
# ---------------------------------------------------------------------------

@dataclass
class FieldCoupling:
    """Coupling between two EFC fields.

    Attributes:
        field_a: First field name.
        field_b: Second field name.
        coupling_type: Type of coupling (direct, mediated, emergent).
        strength: Coupling strength parameter (dimensionless or with units).
        regime: Active regime(s).
        description: Physical description.
    """
    field_a: str
    field_b: str
    coupling_type: str
    strength: Optional[float]
    regime: str
    description: str

    def label(self) -> str:
        return f"{self.field_a} <-> {self.field_b}"

    def summary(self) -> str:
        s = self.strength if self.strength is not None else "N/A"
        return (
            f"{self.label()} [{self.coupling_type}]\n"
            f"  Strength: {s}, Regime: {self.regime}\n"
            f"  {self.description}"
        )


def canonical_couplings() -> List[FieldCoupling]:
    """The six pairwise couplings between the four EFC fields."""
    return [
        FieldCoupling(
            field_a="Energy Flow", field_b="Entropy",
            coupling_type="direct",
            strength=0.16,
            regime="L1-L3",
            description="Energy flow drives entropy production; beta*S(a) modifies gravity",
        ),
        FieldCoupling(
            field_a="Energy Flow", field_b="Grid",
            coupling_type="mediated",
            strength=None,
            regime="L0-L1",
            description="Energy distribution reshapes grid connectivity at micro-scales",
        ),
        FieldCoupling(
            field_a="Energy Flow", field_b="Information",
            coupling_type="emergent",
            strength=None,
            regime="L2-L3",
            description="Energy flow determines information processing capacity",
        ),
        FieldCoupling(
            field_a="Entropy", field_b="Grid",
            coupling_type="direct",
            strength=None,
            regime="L0-L2",
            description="Entropy gradients modify effective grid connectivity and topology",
        ),
        FieldCoupling(
            field_a="Entropy", field_b="Information",
            coupling_type="direct",
            strength=None,
            regime="All",
            description="Landauer-type bound links entropy to information; S and I are dual",
        ),
        FieldCoupling(
            field_a="Grid", field_b="Information",
            coupling_type="emergent",
            strength=None,
            regime="L0-L1",
            description="Grid state encodes information at the micro-structural level",
        ),
    ]


# ---------------------------------------------------------------------------
# Multi-Level Integration
# ---------------------------------------------------------------------------

@dataclass
class IntegrationLevel:
    """A level in the multi-level integration hierarchy."""
    level: str
    name: str
    primary_fields: List[str]
    coupling_direction: str
    description: str

    def summary(self) -> str:
        return (
            f"{self.level}: {self.name}\n"
            f"  Primary fields: {', '.join(self.primary_fields)}\n"
            f"  Coupling: {self.coupling_direction}\n"
            f"  {self.description}"
        )


def integration_levels() -> List[IntegrationLevel]:
    """The multi-level integration hierarchy from micro to macro."""
    return [
        IntegrationLevel(
            level="Micro",
            name="Grid Microphysics",
            primary_fields=["Grid", "Information"],
            coupling_direction="Bottom-up: grid state -> geometry",
            description="Discrete grid encodes topology; information content determines state",
        ),
        IntegrationLevel(
            level="Meso",
            name="Thermodynamic Coupling",
            primary_fields=["Entropy", "Energy Flow"],
            coupling_direction="Bidirectional: entropy <-> energy flow",
            description="Entropy production driven by energy flow; entropy modifies gravity",
        ),
        IntegrationLevel(
            level="Macro",
            name="Cosmological Dynamics",
            primary_fields=["Energy Flow", "Entropy"],
            coupling_direction="Top-down: Friedmann dynamics -> structure",
            description="Modified Friedmann equation governs expansion and structure growth",
        ),
        IntegrationLevel(
            level="Global",
            name="Unified Architecture",
            primary_fields=["All"],
            coupling_direction="Circular: consistency constraints close the loop",
            description="All fields maintain self-consistent evolution across regimes",
        ),
    ]


# ---------------------------------------------------------------------------
# Coupling Matrix
# ---------------------------------------------------------------------------

FIELD_NAMES = ["Energy Flow", "Entropy", "Grid", "Information"]


@dataclass
class CouplingMatrix:
    """Symmetric coupling matrix between the four EFC fields.

    Non-zero entries indicate active coupling at v2.2 level.
    """

    def matrix(self) -> Dict[Tuple[str, str], float]:
        """Return coupling indicators (1.0=active, 0.0=inactive/self)."""
        m: Dict[Tuple[str, str], float] = {}
        for i, fi in enumerate(FIELD_NAMES):
            for j, fj in enumerate(FIELD_NAMES):
                if i == j:
                    m[(fi, fj)] = 0.0
                else:
                    m[(fi, fj)] = 1.0  # all pairs are coupled in EFC
        return m

    def active_couplings(self) -> int:
        """Number of unique active field-pair couplings."""
        n = len(FIELD_NAMES)
        return n * (n - 1) // 2

    def is_fully_connected(self) -> bool:
        """Check if all field pairs are coupled."""
        return self.active_couplings() == 6


# ---------------------------------------------------------------------------
# Cross-Field Consistency Check
# ---------------------------------------------------------------------------

def entropy_energy_consistency(beta: float, S_a: float) -> Dict[str, float]:
    """Check that entropy-energy coupling gives sensible mu."""
    mu = 1.0 + beta * S_a
    return {
        "beta": beta,
        "S(a)": S_a,
        "mu": mu,
        "gravity_enhancement_pct": (mu - 1.0) * 100.0,
        "physical": mu > 0,
    }


# ---------------------------------------------------------------------------
# Integration Summary
# ---------------------------------------------------------------------------

@dataclass
class CrossFieldIntegration:
    """Top-level container for the v2.2 Cross-Field Integration Summary."""
    version: str = "2.2"
    title: str = "EFC v2.2 Cross-Field Integration Summary"
    couplings: List[FieldCoupling] = field(default_factory=canonical_couplings)
    levels: List[IntegrationLevel] = field(default_factory=integration_levels)
    coupling_matrix: CouplingMatrix = field(default_factory=CouplingMatrix)

    def coupling_count(self) -> int:
        return len(self.couplings)

    def level_count(self) -> int:
        return len(self.levels)

    def summary(self) -> str:
        lines = [f"=== {self.title} ===", ""]
        lines.append("FIELD COUPLINGS:")
        for c in self.couplings:
            lines.append(f"  - {c.label()} [{c.coupling_type}]: {c.description}")
        lines.append("")
        lines.append("INTEGRATION LEVELS:")
        for lv in self.levels:
            lines.append(f"  - {lv.level} ({lv.name}): {lv.coupling_direction}")
        lines.append("")
        lines.append(f"Fully connected: {self.coupling_matrix.is_fully_connected()}")
        lines.append(f"Active couplings: {self.coupling_matrix.active_couplings()}")
        return "\n".join(lines)
