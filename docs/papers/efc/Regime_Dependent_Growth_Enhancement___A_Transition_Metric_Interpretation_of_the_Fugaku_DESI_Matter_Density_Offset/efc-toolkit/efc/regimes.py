"""
EFC Regime Architecture
=======================

Defines the L0-L3 regime hierarchy for Energy-Flow Cosmology.

Regimes:
- L0: Cosmological (CMB, BAO, early universe) - μ ≈ 1
- L1: Large-scale structure (clusters, voids) - transition zone
- L2: Galaxy scale (rotation curves, dynamics) - μ > 1
- L3: Sub-galactic (stellar, planetary) - Newtonian limit

Reference: DOI 10.6084/m9.figshare.31112536

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple, List
import numpy as np


class RegimeLevel(Enum):
    """Enumeration of EFC regime levels."""
    L0 = 0  # Cosmological
    L1 = 1  # Large-scale structure
    L2 = 2  # Galaxy scale
    L3 = 3  # Sub-galactic


@dataclass
class Regime:
    """
    Represents an EFC regime with its validity bounds and characteristics.
    
    Attributes:
        level: RegimeLevel enum (L0-L3)
        name: Human-readable name
        scale_min_mpc: Minimum characteristic scale (Mpc)
        scale_max_mpc: Maximum characteristic scale (Mpc)
        mu_typical: Typical μ(a) = G_eff/G in this regime
        mu_uncertainty: Uncertainty on μ
        description: Physical description
        doi: Reference DOI
    """
    level: RegimeLevel
    name: str
    scale_min_mpc: float
    scale_max_mpc: float
    mu_typical: float
    mu_uncertainty: float
    description: str
    doi: str = "10.6084/m9.figshare.31112536"
    
    def contains_scale(self, scale_mpc: float) -> bool:
        """Check if a given scale falls within this regime."""
        return self.scale_min_mpc <= scale_mpc <= self.scale_max_mpc
    
    def mu_range(self) -> Tuple[float, float]:
        """Return the (min, max) range of μ in this regime."""
        return (
            self.mu_typical - self.mu_uncertainty,
            self.mu_typical + self.mu_uncertainty
        )
    
    def is_gr_consistent(self, tolerance: float = 0.01) -> bool:
        """Check if this regime is consistent with GR (μ ≈ 1)."""
        return abs(self.mu_typical - 1.0) <= tolerance
    
    def __repr__(self) -> str:
        return f"Regime({self.level.name}: {self.name}, μ={self.mu_typical}±{self.mu_uncertainty})"


# =============================================================================
# Pre-defined Regime Instances
# =============================================================================

L0 = Regime(
    level=RegimeLevel.L0,
    name="Cosmological",
    scale_min_mpc=100.0,
    scale_max_mpc=float('inf'),
    mu_typical=1.0,
    mu_uncertainty=0.01,
    description="CMB-consistent regime. μ≈1 preserves Planck constraints. "
                "Applicable to BAO, CMB, and early universe physics."
)

L1 = Regime(
    level=RegimeLevel.L1,
    name="Large-Scale Structure",
    scale_min_mpc=1.0,
    scale_max_mpc=100.0,
    mu_typical=1.05,
    mu_uncertainty=0.05,
    description="Transition zone between cosmological and galaxy scales. "
                "DESI/Fugaku sensitivity window. Structure growth enhancement begins."
)

L2 = Regime(
    level=RegimeLevel.L2,
    name="Galaxy",
    scale_min_mpc=0.001,
    scale_max_mpc=1.0,
    mu_typical=1.15,
    mu_uncertainty=0.10,
    description="Galaxy-scale dynamics. Rotation curves, velocity dispersions. "
                "μ>1 provides effective enhancement without dark matter."
)

L3 = Regime(
    level=RegimeLevel.L3,
    name="Sub-galactic",
    scale_min_mpc=0.0,
    scale_max_mpc=0.001,
    mu_typical=1.0,
    mu_uncertainty=0.001,
    description="Sub-galactic scale. Solar system, stellar dynamics. "
                "Returns to Newtonian limit. Highly constrained by ephemeris data."
)

# Ordered list for lookup
_REGIMES: List[Regime] = [L0, L1, L2, L3]


def get_regime(scale_mpc: float) -> Regime:
    """
    Get the appropriate EFC regime for a given scale.
    
    Args:
        scale_mpc: Physical scale in Megaparsecs
        
    Returns:
        The Regime object containing this scale
        
    Examples:
        >>> get_regime(500.0)  # Cosmological
        Regime(L0: Cosmological, μ=1.0±0.01)
        
        >>> get_regime(15.0)   # Cluster scale
        Regime(L1: Large-Scale Structure, μ=1.05±0.05)
        
        >>> get_regime(0.015)  # Galaxy scale
        Regime(L2: Galaxy, μ=1.15±0.1)
    """
    for regime in _REGIMES:
        if regime.contains_scale(scale_mpc):
            return regime
    
    # Default to L3 for very small scales
    return L3


def get_regime_by_level(level: RegimeLevel) -> Regime:
    """Get regime by its level enum."""
    for regime in _REGIMES:
        if regime.level == level:
            return regime
    raise ValueError(f"Unknown regime level: {level}")


def all_regimes() -> List[Regime]:
    """Return all defined regimes."""
    return _REGIMES.copy()


# =============================================================================
# Entropy Sub-regimes (for L2 galaxy scale)
# =============================================================================

@dataclass
class EntropyRegime:
    """
    Sub-regime classification based on normalized entropy S.
    
    Used within L2 (galaxy scale) to determine model validity.
    
    Reference: DOI 10.6084/m9.figshare.31045126 (SPARC analysis)
    """
    name: str
    s_min: float
    s_max: float
    model_status: str
    description: str
    
    def contains(self, s: float) -> bool:
        """Check if entropy value falls in this sub-regime."""
        return self.s_min <= s <= self.s_max


LOW_S = EntropyRegime(
    name="Low-S",
    s_min=0.0,
    s_max=0.1,
    model_status="GR_LIMIT",
    description="Ordered, geometrical regime. EFC reduces to GR. μ→1."
)

MID_S = EntropyRegime(
    name="Mid-S", 
    s_min=0.1,
    s_max=0.9,
    model_status="CORE_DOMAIN",
    description="EFC core validity domain. Classical + entropy gradients. Good fits expected."
)

HIGH_S = EntropyRegime(
    name="High-S",
    s_min=0.9,
    s_max=1.0,
    model_status="BOUNDARY",
    description="Entropy-saturated, non-classical. Classical field theory expected to fail."
)

_ENTROPY_REGIMES = [LOW_S, MID_S, HIGH_S]


def get_entropy_regime(s: float) -> EntropyRegime:
    """
    Get entropy sub-regime for a normalized entropy value.
    
    Args:
        s: Normalized entropy (0 to 1)
        
    Returns:
        EntropyRegime object
    """
    s = max(0.0, min(1.0, s))  # Clamp to [0,1]
    
    for regime in _ENTROPY_REGIMES:
        if regime.contains(s):
            return regime
    
    return HIGH_S  # Default for edge cases
