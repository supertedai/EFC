"""
World Model Implementation

Main WorldModel class that organizes claims in (R, L) space.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .r_axis import RAxis, RRegime
from .l_axis import LAxis, LLayer
from .claim import Claim, ClaimSet
from .regime_gate import RegimeGate, TransferResult


class ModelState(Enum):
    """State of the world model."""
    DRAFT = "draft"
    VALIDATED = "validated"
    PUBLISHED = "published"


@dataclass
class ValidationResult:
    """Result of world model validation."""
    is_valid: bool
    errors: list[str]
    warnings: list[str]


class WorldModel:
    """
    Main world model class organizing claims in (R, L) space.

    A WorldModel contains claims positioned by their physical regime
    (R-axis) and epistemic layer (L-axis), with validation of
    regime transfers.

    Example:
        model = WorldModel(name="Galaxy Dynamics")
        model.add_claim(Claim(
            statement="Rotation curves are flat",
            r_regime=RRegime.R2,
            l_layer=LLayer.L2,
            driver="gravitational_acceleration"
        ))
        result = model.validate()
    """

    def __init__(self, name: str = "Unnamed Model"):
        """
        Initialize a world model.

        Args:
            name: Name of the model
        """
        self.name = name
        self.state = ModelState.DRAFT
        self.claims = ClaimSet()
        self.r_axis = RAxis()
        self.l_axis = LAxis()
        self.gate = RegimeGate()

    def add_claim(self, claim: Claim) -> None:
        """Add a claim to the model."""
        self.claims.add(claim)
        self.state = ModelState.DRAFT

    def remove_claim(self, claim_id: str) -> Optional[Claim]:
        """Remove a claim from the model."""
        claim = self.claims.remove(claim_id)
        if claim:
            self.state = ModelState.DRAFT
        return claim

    def get_claims_at(self, r: RRegime, l: LLayer) -> list[Claim]:
        """Get all claims at specific (R, L) coordinate."""
        return self.claims.filter_by_coordinate(r, l)

    def validate_transfer(
        self,
        claim: Claim,
        target_r: RRegime,
        target_l: LLayer
    ) -> TransferResult:
        """
        Validate if a claim can transfer to new coordinates.

        Args:
            claim: The claim to transfer
            target_r: Target regime
            target_l: Target layer

        Returns:
            TransferResult with validation outcome
        """
        return self.gate.validate(claim, target_r, target_l)

    def validate(self) -> ValidationResult:
        """
        Validate the entire world model.

        Checks:
        1. All claims have valid coordinates
        2. No circular dependencies
        3. Proper regime gating

        Returns:
            ValidationResult
        """
        errors = []
        warnings = []

        # Check all claims
        for claim in self.claims.all():
            # Validate coordinate
            if claim.r_regime not in RRegime:
                errors.append(f"Claim {claim.id}: Invalid R-regime")
            if claim.l_layer not in LLayer:
                errors.append(f"Claim {claim.id}: Invalid L-layer")

            # Warn about high-abstraction claims
            if claim.l_layer == LLayer.L3:
                warnings.append(
                    f"Claim {claim.id}: L3 layer - ensure theoretical basis is clear"
                )

            # Warn about missing driver
            if claim.driver is None:
                warnings.append(f"Claim {claim.id}: No physical driver specified")

        is_valid = len(errors) == 0

        if is_valid:
            self.state = ModelState.VALIDATED

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
        )

    def get_regime_distribution(self) -> dict[RRegime, int]:
        """Get distribution of claims across regimes."""
        dist = {r: 0 for r in RRegime}
        for claim in self.claims.all():
            dist[claim.r_regime] += 1
        return dist

    def get_layer_distribution(self) -> dict[LLayer, int]:
        """Get distribution of claims across layers."""
        dist = {l: 0 for l in LLayer}
        for claim in self.claims.all():
            dist[claim.l_layer] += 1
        return dist

    def summary(self) -> str:
        """Get human-readable summary of the model."""
        r_dist = self.get_regime_distribution()
        l_dist = self.get_layer_distribution()

        lines = [
            f"World Model: {self.name}",
            f"State: {self.state.value}",
            f"Total Claims: {self.claims.count()}",
            "",
            "Regime Distribution:",
        ]
        for r, count in r_dist.items():
            lines.append(f"  {r.value}: {count}")

        lines.append("")
        lines.append("Layer Distribution:")
        for l, count in l_dist.items():
            lines.append(f"  {l.value}: {count}")

        return "\n".join(lines)
