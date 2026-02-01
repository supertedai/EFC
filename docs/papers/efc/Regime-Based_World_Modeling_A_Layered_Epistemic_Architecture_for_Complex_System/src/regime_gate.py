"""
Regime Gate Implementation

Regime gating validates transfers between (R, L) coordinates.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .r_axis import RAxis, RRegime
from .l_axis import LAxis, LLayer
from .claim import Claim


class TransferStatus(Enum):
    """Status of a regime transfer."""
    ALLOWED = "allowed"
    CONDITIONAL = "conditional"
    BLOCKED = "blocked"


@dataclass
class TransferResult:
    """Result of a transfer validation."""
    status: TransferStatus
    source_r: RRegime
    source_l: LLayer
    target_r: RRegime
    target_l: LLayer
    reason: str
    conditions: list[str]
    confidence_factor: float

    @property
    def is_valid(self) -> bool:
        return self.status in (TransferStatus.ALLOWED, TransferStatus.CONDITIONAL)


class RegimeGate:
    """
    Regime gating validator for (R, L) transfers.

    Enforces the Regime-Gating Principle: claims cannot freely
    transfer between regimes without explicit justification.
    """

    def __init__(self):
        """Initialize the regime gate."""
        self.r_axis = RAxis()
        self.l_axis = LAxis()

    def validate(
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
        source_r = claim.r_regime
        source_l = claim.l_layer

        # Same coordinate - always allowed
        if source_r == target_r and source_l == target_l:
            return TransferResult(
                status=TransferStatus.ALLOWED,
                source_r=source_r,
                source_l=source_l,
                target_r=target_r,
                target_l=target_l,
                reason="Same coordinate - no transfer needed",
                conditions=[],
                confidence_factor=1.0,
            )

        # Check R-axis transfer
        r_distance = self.r_axis.distance(source_r, target_r)
        r_status, r_conditions = self._check_r_transfer(source_r, target_r, r_distance)

        # Check L-axis transfer
        l_distance = self.l_axis.distance(source_l, target_l)
        l_degradation = self.l_axis.confidence_degradation(source_l, target_l)

        # Combine results
        conditions = r_conditions.copy()

        if r_status == TransferStatus.BLOCKED:
            return TransferResult(
                status=TransferStatus.BLOCKED,
                source_r=source_r,
                source_l=source_l,
                target_r=target_r,
                target_l=target_l,
                reason=f"R-axis transfer blocked: distance = {r_distance}",
                conditions=conditions,
                confidence_factor=l_degradation,
            )

        if l_degradation < 0.5:
            conditions.append("Severe confidence degradation - verify necessity")

        if r_status == TransferStatus.CONDITIONAL or l_distance > 1:
            status = TransferStatus.CONDITIONAL
            reason = f"Conditional: R-distance={r_distance}, L-distance={l_distance}"
        else:
            status = TransferStatus.ALLOWED
            reason = "Transfer allowed"

        return TransferResult(
            status=status,
            source_r=source_r,
            source_l=source_l,
            target_r=target_r,
            target_l=target_l,
            reason=reason,
            conditions=conditions,
            confidence_factor=l_degradation,
        )

    def _check_r_transfer(
        self,
        source: RRegime,
        target: RRegime,
        distance: int
    ) -> tuple[TransferStatus, list[str]]:
        """Check R-axis transfer rules."""
        if distance == 0:
            return TransferStatus.ALLOWED, []

        if distance == 1:
            # Adjacent regime transfer
            if source == RRegime.R0 and target == RRegime.R1:
                return TransferStatus.CONDITIONAL, [
                    "Verify emergence conditions",
                    "Check scale separation"
                ]
            elif source == RRegime.R1 and target == RRegime.R0:
                return TransferStatus.CONDITIONAL, [
                    "Verify reductionist assumption",
                    "Check coarse-graining validity"
                ]
            elif source == RRegime.R1 and target == RRegime.R2:
                return TransferStatus.CONDITIONAL, [
                    "Verify emergent properties",
                    "Check system boundaries"
                ]
            elif source == RRegime.R2 and target == RRegime.R1:
                return TransferStatus.CONDITIONAL, [
                    "Verify decomposition validity",
                    "Check for irreducible properties"
                ]
            else:
                return TransferStatus.CONDITIONAL, ["Justify regime transfer"]

        # Non-adjacent regime transfer
        return TransferStatus.BLOCKED, ["Non-adjacent regimes require bridging"]
