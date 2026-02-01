"""
Regime Gating Implementation

The Regime-Gating Principle states that claims valid in one regime
may not automatically transfer to another regime without explicit
justification.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .s_axis import SRegime
from .l_axis import LLayer


class TransferStatus(Enum):
    """Status of a regime transfer validation."""
    ALLOWED = "allowed"
    CONDITIONAL = "conditional"
    BLOCKED = "blocked"


@dataclass
class TransferResult:
    """Result of a transfer validation."""
    status: TransferStatus
    source_regime: SRegime
    target_regime: SRegime
    source_layer: LLayer
    target_layer: LLayer
    reason: str
    conditions: list[str]
    confidence_degradation: float

    @property
    def is_valid(self) -> bool:
        return self.status in (TransferStatus.ALLOWED, TransferStatus.CONDITIONAL)


@dataclass
class Claim:
    """A physical claim with (S, L) coordinates."""
    statement: str
    s_regime: SRegime
    l_layer: LLayer
    domain: Optional[str] = None
    confidence: float = 1.0


class RegimeGate:
    """
    Regime gating validator.

    Enforces the principle that claims cannot freely transfer
    between physical regimes without explicit justification.
    """

    # Define transfer rules
    TRANSFER_RULES = {
        # (source_S, target_S): (status, conditions)
        (SRegime.LOW_S, SRegime.LOW_S): (TransferStatus.ALLOWED, []),
        (SRegime.LOW_S, SRegime.MID_S): (TransferStatus.CONDITIONAL,
            ["Verify scale invariance", "Check emergent effects"]),
        (SRegime.LOW_S, SRegime.HIGH_S): (TransferStatus.BLOCKED,
            ["Requires intermediate bridging"]),

        (SRegime.MID_S, SRegime.LOW_S): (TransferStatus.CONDITIONAL,
            ["Verify reductionist assumption"]),
        (SRegime.MID_S, SRegime.MID_S): (TransferStatus.ALLOWED, []),
        (SRegime.MID_S, SRegime.HIGH_S): (TransferStatus.CONDITIONAL,
            ["Check for phase transitions", "Verify collective behavior"]),

        (SRegime.HIGH_S, SRegime.LOW_S): (TransferStatus.BLOCKED,
            ["Emergent properties may not reduce"]),
        (SRegime.HIGH_S, SRegime.MID_S): (TransferStatus.CONDITIONAL,
            ["Verify decomposition validity"]),
        (SRegime.HIGH_S, SRegime.HIGH_S): (TransferStatus.ALLOWED, []),
    }

    # Confidence degradation by layer distance
    LAYER_DEGRADATION = {
        0: 1.0,   # Same layer
        1: 0.85,  # Adjacent layers
        2: 0.60,  # Two layers apart
        3: 0.35,  # Maximum distance
    }

    def __init__(self):
        """Initialize the regime gate."""
        pass

    def validate_transfer(
        self,
        claim: Claim,
        target_s: SRegime,
        target_l: LLayer,
    ) -> TransferResult:
        """
        Validate if a claim can transfer to new coordinates.

        Args:
            claim: The claim to transfer
            target_s: Target S-regime
            target_l: Target L-layer

        Returns:
            TransferResult with validation outcome
        """
        # Get S-axis transfer rule
        rule_key = (claim.s_regime, target_s)
        status, conditions = self.TRANSFER_RULES.get(
            rule_key,
            (TransferStatus.BLOCKED, ["Unknown transfer path"])
        )

        # Compute layer distance
        layer_order = [LLayer.L0, LLayer.L1, LLayer.L2, LLayer.L3]
        source_idx = layer_order.index(claim.l_layer)
        target_idx = layer_order.index(target_l)
        layer_distance = abs(target_idx - source_idx)

        # Get confidence degradation
        degradation = self.LAYER_DEGRADATION.get(layer_distance, 0.2)

        # Build reason
        if status == TransferStatus.ALLOWED:
            reason = "Transfer allowed within same regime"
        elif status == TransferStatus.CONDITIONAL:
            reason = f"Transfer requires verification: {', '.join(conditions)}"
        else:
            reason = f"Transfer blocked: {', '.join(conditions)}"

        return TransferResult(
            status=status,
            source_regime=claim.s_regime,
            target_regime=target_s,
            source_layer=claim.l_layer,
            target_layer=target_l,
            reason=reason,
            conditions=conditions,
            confidence_degradation=degradation,
        )


class TransferValidator:
    """
    High-level transfer validation interface.

    Validates transfers between any two (S, L) positions
    and tracks validation history.
    """

    def __init__(self):
        """Initialize the validator."""
        self.gate = RegimeGate()
        self.history: list[TransferResult] = []

    def validate(
        self,
        claim: Claim,
        target_s: SRegime,
        target_l: LLayer,
    ) -> TransferResult:
        """
        Validate and record a transfer attempt.

        Args:
            claim: The claim to transfer
            target_s: Target S-regime
            target_l: Target L-layer

        Returns:
            TransferResult with validation outcome
        """
        result = self.gate.validate_transfer(claim, target_s, target_l)
        self.history.append(result)
        return result

    def summary(self) -> str:
        """Get summary of all validations."""
        if not self.history:
            return "No validations performed"

        allowed = sum(1 for r in self.history if r.status == TransferStatus.ALLOWED)
        conditional = sum(1 for r in self.history if r.status == TransferStatus.CONDITIONAL)
        blocked = sum(1 for r in self.history if r.status == TransferStatus.BLOCKED)

        return (
            f"Transfer Validation Summary:\n"
            f"  Allowed: {allowed}\n"
            f"  Conditional: {conditional}\n"
            f"  Blocked: {blocked}\n"
            f"  Total: {len(self.history)}"
        )
