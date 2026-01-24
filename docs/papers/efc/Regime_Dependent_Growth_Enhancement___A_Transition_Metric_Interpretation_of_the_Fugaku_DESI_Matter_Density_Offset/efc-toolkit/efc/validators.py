"""
EFC Validity Checkers
=====================

Tools for checking whether EFC applies to a given physical situation.
Critical for AI systems to avoid making claims outside validity domain.

Key principle: EFC admits where it stops working.
A model that fits everything is typically over-tuned.
A model that admits where it fails builds credibility.

Reference: DOI 10.6084/m9.figshare.31045126 (Domain of Validity Theorem)

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
"""

from dataclasses import dataclass
from typing import Tuple, Optional, List
from enum import Enum

from .regimes import Regime, L0, L1, L2, L3, get_regime, get_entropy_regime
from .constants import EFC_CONSTANTS


class ValidityStatus(Enum):
    """Validity status for EFC claims."""
    VALID = "valid"                    # Within EFC core domain
    BOUNDARY = "boundary"              # At regime boundary, use caution
    OUTSIDE = "outside"                # Outside EFC validity
    GR_LIMIT = "gr_limit"             # Reduces to GR, no EFC needed
    UNKNOWN = "unknown"                # Cannot determine


@dataclass
class ValidityResult:
    """Result of a validity check."""
    status: ValidityStatus
    regime: Optional[Regime]
    reason: str
    confidence: float  # 0-1
    recommendation: str
    doi_reference: str = ""
    
    def is_valid(self) -> bool:
        """Check if claim is valid for EFC."""
        return self.status in [ValidityStatus.VALID, ValidityStatus.GR_LIMIT]
    
    def requires_caution(self) -> bool:
        """Check if claim requires epistemic caution."""
        return self.status in [ValidityStatus.BOUNDARY, ValidityStatus.UNKNOWN]


class RegimeBoundary:
    """
    Defines and checks regime boundaries.
    
    EFC does not fail randomly - it stops precisely where 
    classical potential physics is expected to stop.
    """
    
    def __init__(self):
        self.scale_boundaries = {
            "L0_L1": EFC_CONSTANTS.scale_L0_min,  # 100 Mpc
            "L1_L2": EFC_CONSTANTS.scale_L1_min,  # 1 Mpc
            "L2_L3": EFC_CONSTANTS.scale_L2_min,  # 0.001 Mpc
        }
        
        self.entropy_boundaries = {
            "low_mid": EFC_CONSTANTS.S_low_max,   # 0.1
            "mid_high": EFC_CONSTANTS.S_mid_max,  # 0.9
        }
    
    def near_boundary(
        self, 
        scale_mpc: float, 
        margin_fraction: float = 0.1
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if scale is near a regime boundary.
        
        Args:
            scale_mpc: Physical scale in Mpc
            margin_fraction: Fraction of boundary defining "near"
            
        Returns:
            (is_near, boundary_name)
        """
        for name, boundary in self.scale_boundaries.items():
            margin = boundary * margin_fraction
            if abs(scale_mpc - boundary) < margin:
                return True, name
        return False, None
    
    def crossing_regime(
        self, 
        scale_start: float, 
        scale_end: float
    ) -> List[str]:
        """Check which regime boundaries are crossed between two scales."""
        crossings = []
        for name, boundary in self.scale_boundaries.items():
            if (scale_start < boundary < scale_end) or (scale_end < boundary < scale_start):
                crossings.append(name)
        return crossings


class ValidityChecker:
    """
    Main validity checker for EFC claims.
    
    Use before making any EFC-based claim to ensure you're 
    within the framework's validity domain.
    
    Example:
        >>> checker = ValidityChecker()
        >>> result = checker.check_scale(scale_mpc=15.0)
        >>> if result.is_valid():
        ...     # Safe to apply EFC
        ... else:
        ...     print(f"Warning: {result.reason}")
    """
    
    def __init__(self):
        self.boundary_checker = RegimeBoundary()
    
    def check_scale(self, scale_mpc: float) -> ValidityResult:
        """
        Check validity for a given physical scale.
        
        Args:
            scale_mpc: Physical scale in Megaparsecs
            
        Returns:
            ValidityResult with status and recommendation
        """
        regime = get_regime(scale_mpc)
        near_boundary, boundary_name = self.boundary_checker.near_boundary(scale_mpc)
        
        if regime.level.name == "L0":
            return ValidityResult(
                status=ValidityStatus.GR_LIMIT,
                regime=regime,
                reason="Cosmological scale: μ≈1, GR applies",
                confidence=0.95,
                recommendation="Use standard ΛCDM; EFC reduces to GR here",
                doi_reference="10.6084/m9.figshare.31095466"
            )
        
        elif regime.level.name == "L1":
            return ValidityResult(
                status=ValidityStatus.VALID if not near_boundary else ValidityStatus.BOUNDARY,
                regime=regime,
                reason="Transition zone: structure growth enhancement active",
                confidence=0.85 if not near_boundary else 0.70,
                recommendation="EFC transition metric applies; check Δ_F consistency",
                doi_reference="10.6084/m9.figshare.31127380"
            )
        
        elif regime.level.name == "L2":
            return ValidityResult(
                status=ValidityStatus.VALID,
                regime=regime,
                reason="Galaxy scale: EFC core domain",
                confidence=0.90,
                recommendation="Apply EFC rotation curve analysis; check entropy regime",
                doi_reference="10.6084/m9.figshare.31045126"
            )
        
        elif regime.level.name == "L3":
            return ValidityResult(
                status=ValidityStatus.GR_LIMIT,
                regime=regime,
                reason="Sub-galactic scale: Newtonian limit",
                confidence=0.99,
                recommendation="Use Newtonian gravity; EFC reduces to GR",
                doi_reference="10.6084/m9.figshare.31112536"
            )
        
        return ValidityResult(
            status=ValidityStatus.UNKNOWN,
            regime=regime,
            reason="Could not determine validity",
            confidence=0.0,
            recommendation="Manual review required"
        )
    
    def check_entropy(self, s: float, scale_mpc: Optional[float] = None) -> ValidityResult:
        """
        Check validity for a given entropy value (galaxy-scale).
        
        Args:
            s: Normalized entropy (0-1)
            scale_mpc: Optional scale for context
            
        Returns:
            ValidityResult
        """
        entropy_regime = get_entropy_regime(s)
        
        if entropy_regime.name == "Low-S":
            return ValidityResult(
                status=ValidityStatus.GR_LIMIT,
                regime=L2 if scale_mpc is None else get_regime(scale_mpc),
                reason=f"Low entropy (S={s:.2f}): ordered, GR limit",
                confidence=0.95,
                recommendation="EFC corrections vanish; classical GR applies",
                doi_reference="10.6084/m9.figshare.31045126"
            )
        
        elif entropy_regime.name == "Mid-S":
            return ValidityResult(
                status=ValidityStatus.VALID,
                regime=L2 if scale_mpc is None else get_regime(scale_mpc),
                reason=f"Mid entropy (S={s:.2f}): EFC core domain",
                confidence=0.90,
                recommendation="EFC rotation curve analysis valid; expect χ²/dof < 5",
                doi_reference="10.6084/m9.figshare.31045126"
            )
        
        elif entropy_regime.name == "High-S":
            return ValidityResult(
                status=ValidityStatus.BOUNDARY,
                regime=L2 if scale_mpc is None else get_regime(scale_mpc),
                reason=f"High entropy (S={s:.2f}): classical field theory limit",
                confidence=0.60,
                recommendation="EFC may underpredict; non-local physics may dominate",
                doi_reference="10.6084/m9.figshare.31045126"
            )
        
        return ValidityResult(
            status=ValidityStatus.UNKNOWN,
            regime=None,
            reason="Could not determine entropy regime",
            confidence=0.0,
            recommendation="Check entropy calculation"
        )
    
    def check_claim(
        self,
        regime: Regime,
        claim_type: str,
        entropy_normalized: Optional[float] = None
    ) -> Tuple[bool, str]:
        """
        Simple interface: check if a claim is valid.
        
        Args:
            regime: EFC regime
            claim_type: Type of claim ("rotation_curve", "cmb", "lss", etc.)
            entropy_normalized: Normalized entropy if applicable
            
        Returns:
            (is_valid, reason)
        """
        # Scale-based check
        if regime.level.name in ["L0", "L3"]:
            return True, f"GR limit in {regime.name}; claim valid but EFC not needed"
        
        # Entropy check for galaxy scale
        if regime.level.name == "L2" and entropy_normalized is not None:
            if entropy_normalized > 0.9:
                return False, f"High-S regime (S={entropy_normalized}): outside EFC core domain"
            elif entropy_normalized < 0.1:
                return True, "Low-S regime: GR limit applies"
            else:
                return True, "Mid-S regime: EFC core domain"
        
        # Default for L1/L2 without entropy info
        if regime.level.name in ["L1", "L2"]:
            return True, f"Within {regime.name} regime"
        
        return False, "Unknown regime"
    
    def in_domain(self, regime: Regime, entropy: Optional[float] = None) -> bool:
        """Quick check if in EFC validity domain."""
        is_valid, _ = self.check_claim(regime, "", entropy)
        return is_valid


# =============================================================================
# Convenience functions
# =============================================================================

def validate_before_claim(
    scale_mpc: float,
    entropy: Optional[float] = None
) -> ValidityResult:
    """
    One-call validation before making an EFC claim.
    
    Args:
        scale_mpc: Physical scale in Mpc
        entropy: Normalized entropy (0-1) if known
        
    Returns:
        ValidityResult with full context
    """
    checker = ValidityChecker()
    
    # First check scale
    result = checker.check_scale(scale_mpc)
    
    # If at galaxy scale and entropy provided, refine
    if result.regime and result.regime.level.name == "L2" and entropy is not None:
        entropy_result = checker.check_entropy(entropy, scale_mpc)
        # Use stricter of the two
        if entropy_result.confidence < result.confidence:
            return entropy_result
    
    return result
