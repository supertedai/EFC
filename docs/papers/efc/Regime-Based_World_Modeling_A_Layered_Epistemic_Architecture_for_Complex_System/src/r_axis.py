"""
R-Axis Implementation

The R-axis represents the physical regime hierarchy based on complexity.

Regimes:
- R0: Field (fundamental physics, spacetime)
- R1: Structure (organized matter, molecules, crystals)
- R2: Complex (emergent systems, life, economies)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RRegime(Enum):
    """Physical regime classification on R-axis."""
    R0 = "R0"  # Field
    R1 = "R1"  # Structure
    R2 = "R2"  # Complex


@dataclass
class RegimeInfo:
    """Information about a classified regime."""
    regime: RRegime
    name: str
    description: str
    scale_range: str
    typical_systems: list[str]
    emergent_properties: list[str]


class RAxis:
    """
    R-Axis classifier for physical regimes.

    The R-axis organizes physical phenomena by their characteristic
    complexity level, from fundamental fields to complex systems.
    """

    REGIME_DEFINITIONS = {
        RRegime.R0: RegimeInfo(
            regime=RRegime.R0,
            name="Field Regime",
            description="Fundamental physics, quantum fields, spacetime",
            scale_range="Planck to nuclear",
            typical_systems=["QFT", "General Relativity", "particle physics"],
            emergent_properties=[]
        ),
        RRegime.R1: RegimeInfo(
            regime=RRegime.R1,
            name="Structure Regime",
            description="Organized matter with stable configurations",
            scale_range="Atomic to planetary",
            typical_systems=["atoms", "molecules", "crystals", "stars"],
            emergent_properties=["phase transitions", "collective modes"]
        ),
        RRegime.R2: RegimeInfo(
            regime=RRegime.R2,
            name="Complex Regime",
            description="Emergent systems with irreducible properties",
            scale_range="Cellular to cosmic",
            typical_systems=["life", "economies", "ecosystems", "societies"],
            emergent_properties=["self-organization", "adaptation", "consciousness"]
        ),
    }

    def __init__(self):
        """Initialize the R-axis classifier."""
        pass

    def classify_by_name(self, regime_name: str) -> Optional[RegimeInfo]:
        """
        Classify by regime name.

        Args:
            regime_name: Name like "R0", "R1", "R2", "field", "structure", "complex"

        Returns:
            RegimeInfo if recognized, None otherwise
        """
        name_upper = regime_name.upper()

        # Direct match
        for regime in RRegime:
            if regime.value == name_upper:
                return self.REGIME_DEFINITIONS[regime]

        # Name match
        name_lower = regime_name.lower()
        name_map = {
            "field": RRegime.R0,
            "fundamental": RRegime.R0,
            "structure": RRegime.R1,
            "organized": RRegime.R1,
            "complex": RRegime.R2,
            "emergent": RRegime.R2,
        }

        if name_lower in name_map:
            return self.REGIME_DEFINITIONS[name_map[name_lower]]

        return None

    def get_regime(self, regime: RRegime) -> RegimeInfo:
        """Get information about a specific regime."""
        return self.REGIME_DEFINITIONS[regime]

    def get_regime_order(self) -> list[RRegime]:
        """Get regimes in complexity order."""
        return [RRegime.R0, RRegime.R1, RRegime.R2]

    def distance(self, r1: RRegime, r2: RRegime) -> int:
        """
        Compute distance between two regimes.

        Args:
            r1: First regime
            r2: Second regime

        Returns:
            Number of regime steps between them
        """
        order = self.get_regime_order()
        return abs(order.index(r1) - order.index(r2))

    def can_transfer(self, source: RRegime, target: RRegime) -> tuple[bool, str]:
        """
        Check if a claim can transfer between regimes.

        Args:
            source: Source regime
            target: Target regime

        Returns:
            Tuple of (allowed, reason)
        """
        if source == target:
            return True, "Same regime - no transfer needed"

        dist = self.distance(source, target)

        if dist == 1:
            return True, "Adjacent regimes - transfer requires justification"
        else:
            return False, "Non-adjacent regimes - transfer blocked without bridging"
