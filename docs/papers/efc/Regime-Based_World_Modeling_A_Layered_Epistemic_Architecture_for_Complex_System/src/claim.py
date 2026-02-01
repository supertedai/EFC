"""
Claim Implementation

Claims are statements with (R, L) coordinates and associated metadata.
"""

from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4

from .r_axis import RRegime
from .l_axis import LLayer


@dataclass
class Claim:
    """
    A physical claim with (R, L) coordinates.

    Attributes:
        statement: The claim being made
        r_regime: Physical regime (R0, R1, R2)
        l_layer: Epistemic layer (L0, L1, L2, L3)
        driver: Primary physical driver
        validity_domain: Conditions where claim holds
        confidence: Epistemic confidence (0-1)
        id: Unique identifier
    """
    statement: str
    r_regime: RRegime
    l_layer: LLayer
    driver: Optional[str] = None
    validity_domain: Optional[str] = None
    confidence: float = 1.0
    id: str = field(default_factory=lambda: str(uuid4())[:8])

    @property
    def coordinate(self) -> tuple[RRegime, LLayer]:
        """Get (R, L) coordinate tuple."""
        return (self.r_regime, self.l_layer)

    @property
    def coordinate_str(self) -> str:
        """Get coordinate as string, e.g., '(R1, L2)'."""
        return f"({self.r_regime.value}, {self.l_layer.value})"

    def summary(self) -> str:
        """Get human-readable summary."""
        return (
            f"Claim [{self.id}]: {self.statement}\n"
            f"  Coordinate: {self.coordinate_str}\n"
            f"  Driver: {self.driver or 'Not specified'}\n"
            f"  Domain: {self.validity_domain or 'Not specified'}\n"
            f"  Confidence: {self.confidence:.0%}"
        )


class ClaimSet:
    """
    Collection of claims with validation and query operations.

    Example:
        claims = ClaimSet()
        claims.add(Claim(
            statement="Galaxy rotation curves are flat",
            r_regime=RRegime.R2,
            l_layer=LLayer.L2
        ))
        r2_claims = claims.filter_by_regime(RRegime.R2)
    """

    def __init__(self):
        """Initialize empty claim set."""
        self.claims: dict[str, Claim] = {}

    def add(self, claim: Claim) -> None:
        """Add a claim to the set."""
        self.claims[claim.id] = claim

    def remove(self, claim_id: str) -> Optional[Claim]:
        """Remove and return a claim by ID."""
        return self.claims.pop(claim_id, None)

    def get(self, claim_id: str) -> Optional[Claim]:
        """Get a claim by ID."""
        return self.claims.get(claim_id)

    def all(self) -> list[Claim]:
        """Get all claims."""
        return list(self.claims.values())

    def filter_by_regime(self, regime: RRegime) -> list[Claim]:
        """Get all claims in a specific regime."""
        return [c for c in self.claims.values() if c.r_regime == regime]

    def filter_by_layer(self, layer: LLayer) -> list[Claim]:
        """Get all claims at a specific layer."""
        return [c for c in self.claims.values() if c.l_layer == layer]

    def filter_by_coordinate(self, r: RRegime, l: LLayer) -> list[Claim]:
        """Get all claims at specific (R, L) coordinate."""
        return [c for c in self.claims.values()
                if c.r_regime == r and c.l_layer == l]

    def filter_by_driver(self, driver: str) -> list[Claim]:
        """Get all claims with a specific driver."""
        return [c for c in self.claims.values()
                if c.driver and driver.lower() in c.driver.lower()]

    def count(self) -> int:
        """Get total number of claims."""
        return len(self.claims)

    def summary(self) -> str:
        """Get summary of claim distribution."""
        regime_counts = {}
        layer_counts = {}

        for claim in self.claims.values():
            regime_counts[claim.r_regime] = regime_counts.get(claim.r_regime, 0) + 1
            layer_counts[claim.l_layer] = layer_counts.get(claim.l_layer, 0) + 1

        lines = [f"ClaimSet: {self.count()} claims"]
        lines.append("  By Regime:")
        for r in RRegime:
            lines.append(f"    {r.value}: {regime_counts.get(r, 0)}")
        lines.append("  By Layer:")
        for l in LLayer:
            lines.append(f"    {l.value}: {layer_counts.get(l, 0)}")

        return "\n".join(lines)
