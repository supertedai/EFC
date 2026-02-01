"""
S-Axis Implementation

The S-axis represents the physical regime hierarchy based on entropy/complexity.

Regimes:
- Low-S: Simple, low-entropy systems (particle physics, atoms)
- Mid-S: Moderate complexity (stellar dynamics, molecules)
- High-S: Complex, high-entropy systems (galaxies, life)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SRegime(Enum):
    """Physical regime classification on S-axis."""
    LOW_S = "low_s"
    MID_S = "mid_s"
    HIGH_S = "high_s"


@dataclass
class RegimeInfo:
    """Information about a classified regime."""
    regime: SRegime
    name: str
    description: str
    entropy_range: tuple[float, float]
    typical_systems: list[str]


class SAxis:
    """
    S-Axis classifier for physical regimes.

    The S-axis organizes physical phenomena by their characteristic
    entropy or complexity level.
    """

    REGIME_DEFINITIONS = {
        SRegime.LOW_S: RegimeInfo(
            regime=SRegime.LOW_S,
            name="Low-S Regime",
            description="Simple, low-entropy systems with few degrees of freedom",
            entropy_range=(0.0, 0.3),
            typical_systems=["particle physics", "atomic systems", "crystals"]
        ),
        SRegime.MID_S: RegimeInfo(
            regime=SRegime.MID_S,
            name="Mid-S Regime",
            description="Moderate complexity with emergent collective behavior",
            entropy_range=(0.3, 0.7),
            typical_systems=["stellar interiors", "molecular systems", "plasmas"]
        ),
        SRegime.HIGH_S: RegimeInfo(
            regime=SRegime.HIGH_S,
            name="High-S Regime",
            description="Complex, high-entropy systems with many degrees of freedom",
            entropy_range=(0.7, 1.0),
            typical_systems=["galaxies", "biological systems", "economies"]
        ),
    }

    def __init__(self):
        """Initialize the S-axis classifier."""
        pass

    def classify(self, entropy_parameter: float) -> RegimeInfo:
        """
        Classify a system by its entropy parameter.

        Args:
            entropy_parameter: Normalized entropy value (0 to 1)

        Returns:
            RegimeInfo for the classified regime
        """
        if entropy_parameter < 0 or entropy_parameter > 1:
            raise ValueError("Entropy parameter must be between 0 and 1")

        if entropy_parameter < 0.3:
            return self.REGIME_DEFINITIONS[SRegime.LOW_S]
        elif entropy_parameter < 0.7:
            return self.REGIME_DEFINITIONS[SRegime.MID_S]
        else:
            return self.REGIME_DEFINITIONS[SRegime.HIGH_S]

    def classify_by_system(self, system_type: str) -> Optional[RegimeInfo]:
        """
        Classify by known system type.

        Args:
            system_type: Name of physical system

        Returns:
            RegimeInfo if system is recognized, None otherwise
        """
        system_lower = system_type.lower()

        for regime_info in self.REGIME_DEFINITIONS.values():
            for typical in regime_info.typical_systems:
                if typical in system_lower or system_lower in typical:
                    return regime_info

        return None

    def get_regime(self, regime: SRegime) -> RegimeInfo:
        """Get information about a specific regime."""
        return self.REGIME_DEFINITIONS[regime]

    def can_transfer(self, source: SRegime, target: SRegime) -> tuple[bool, str]:
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

        # Adjacent regimes may transfer with caution
        regime_order = [SRegime.LOW_S, SRegime.MID_S, SRegime.HIGH_S]
        source_idx = regime_order.index(source)
        target_idx = regime_order.index(target)

        if abs(source_idx - target_idx) == 1:
            return True, "Adjacent regimes - transfer requires justification"
        else:
            return False, "Non-adjacent regimes - transfer not allowed without explicit bridging"
