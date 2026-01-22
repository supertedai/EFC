"""
Regime Classifier for Validity-Aware AI

Classifies queries into L0/L1/L2/L3 regimes based on entropy measurements.
Maps entropy values to regime classifications and confidence scores.

Part of: Validity-Aware AI
DOI: 10.6084/m9.figshare.31122970
"""

from enum import Enum
from typing import Tuple, Optional
from dataclasses import dataclass


class Regime(Enum):
    """
    The four regimes of Entropy-Bounded Empiricism.
    
    L0: Latent - system inactive, no inference
    L1: Stable Active - low entropy, confident inference valid
    L2: Complex Active - high entropy, uncertainty required
    L3: Residual - archival mode, no predictions
    """
    L0 = "latent"
    L1 = "stable_active"
    L2 = "complex_active"
    L3 = "residual"
    
    @property
    def allows_confident_output(self) -> bool:
        """Whether this regime allows confident/assertive outputs."""
        return self == Regime.L1
    
    @property
    def requires_uncertainty(self) -> bool:
        """Whether this regime requires explicit uncertainty."""
        return self == Regime.L2
    
    @property
    def is_archival(self) -> bool:
        """Whether this regime is archival (no predictions)."""
        return self == Regime.L3
    
    @property
    def is_active(self) -> bool:
        """Whether this regime supports active inference."""
        return self in (Regime.L1, Regime.L2)


@dataclass
class RegimeThresholds:
    """Configuration for regime classification thresholds."""
    theta_L1: float = 0.3  # Upper bound for L1
    theta_L2: float = 0.7  # Upper bound for L2 (above = L3 warning)
    
    def validate(self) -> bool:
        """Validate threshold configuration."""
        return 0 < self.theta_L1 < self.theta_L2 < 1


def classify_regime(
    entropy: float,
    theta_L1: float = 0.3,
    theta_L2: float = 0.7
) -> Tuple[Regime, float]:
    """
    Classify entropy value into regime with confidence.
    
    The classification follows the L0-L3 architecture:
    - H < theta_L1: L1 (stable, confident inference valid)
    - theta_L1 <= H < theta_L2: L2 (contested, uncertainty required)
    - H >= theta_L2: L3 warning (approaching collapse)
    
    Confidence is computed as distance from regime boundaries.
    
    Args:
        entropy: Total entropy value H(G) in [0, 1]
        theta_L1: Upper threshold for L1 regime
        theta_L2: Upper threshold for L2 regime
        
    Returns:
        Tuple of (Regime, confidence) where confidence is in [0, 1]
    """
    # Clamp entropy to valid range
    entropy = max(0.0, min(1.0, entropy))
    
    if entropy < theta_L1:
        # L1: Stable regime
        # Confidence = how far from L2 boundary (normalized)
        confidence = 1.0 - (entropy / theta_L1)
        return Regime.L1, confidence
    
    elif entropy < theta_L2:
        # L2: Complex regime
        # Confidence = how centered in L2 (highest at midpoint)
        midpoint = (theta_L1 + theta_L2) / 2
        distance_from_mid = abs(entropy - midpoint)
        range_half = (theta_L2 - theta_L1) / 2
        confidence = 1.0 - (distance_from_mid / range_half)
        return Regime.L2, confidence
    
    else:
        # L3 Warning: Approaching collapse
        # Confidence is always 0 (we're not confident in anything)
        return Regime.L3, 0.0


def classify_with_transition_zone(
    entropy: float,
    theta_L1: float = 0.3,
    theta_L2: float = 0.7,
    transition_width: float = 0.1
) -> Tuple[Regime, float, bool]:
    """
    Classify with explicit transition zone detection.
    
    The transition zone is a region around theta_L1 where the system
    is between stable (L1) and contested (L2) regimes.
    
    Args:
        entropy: Total entropy value
        theta_L1: L1 upper threshold
        theta_L2: L2 upper threshold
        transition_width: Width of transition zone around theta_L1
        
    Returns:
        Tuple of (Regime, confidence, in_transition_zone)
    """
    regime, confidence = classify_regime(entropy, theta_L1, theta_L2)
    
    # Check if in transition zone
    transition_lower = theta_L1 - (transition_width / 2)
    transition_upper = theta_L1 + (transition_width / 2)
    
    in_transition = transition_lower <= entropy <= transition_upper
    
    if in_transition:
        # Reduce confidence in transition zone
        confidence *= 0.7
    
    return regime, confidence, in_transition


def get_regime_for_system_state(
    system_active: bool,
    domain_active: bool,
    entropy: Optional[float] = None,
    theta_L1: float = 0.3,
    theta_L2: float = 0.7
) -> Regime:
    """
    Get regime considering system and domain state.
    
    This handles L0 (system inactive) and L3 (domain inactive) cases
    that aren't determined by entropy alone.
    
    Args:
        system_active: Whether the inference system is active
        domain_active: Whether the knowledge domain is actively maintained
        entropy: Computed entropy (optional if system/domain inactive)
        theta_L1: L1 threshold
        theta_L2: L2 threshold
        
    Returns:
        Appropriate Regime
    """
    # L0: System not active
    if not system_active:
        return Regime.L0
    
    # L3: Domain not active (regardless of entropy)
    if not domain_active:
        return Regime.L3
    
    # Active system with active domain: use entropy classification
    if entropy is not None:
        regime, _ = classify_regime(entropy, theta_L1, theta_L2)
        return regime
    
    # Default to L2 (conservative) if no entropy available
    return Regime.L2


class RegimeClassifier:
    """
    Stateful regime classifier with configuration.
    
    Usage:
        classifier = RegimeClassifier(theta_L1=0.25, theta_L2=0.6)
        regime, confidence = classifier.classify(entropy_value)
    """
    
    def __init__(
        self,
        theta_L1: float = 0.3,
        theta_L2: float = 0.7,
        enable_transition_detection: bool = True,
        transition_width: float = 0.1
    ):
        self.thresholds = RegimeThresholds(theta_L1, theta_L2)
        self.enable_transition_detection = enable_transition_detection
        self.transition_width = transition_width
        
        if not self.thresholds.validate():
            raise ValueError(f"Invalid thresholds: 0 < {theta_L1} < {theta_L2} < 1 required")
    
    def classify(self, entropy: float) -> Tuple[Regime, float]:
        """Classify entropy into regime."""
        return classify_regime(
            entropy,
            self.thresholds.theta_L1,
            self.thresholds.theta_L2
        )
    
    def classify_with_transition(self, entropy: float) -> Tuple[Regime, float, bool]:
        """Classify with transition zone information."""
        return classify_with_transition_zone(
            entropy,
            self.thresholds.theta_L1,
            self.thresholds.theta_L2,
            self.transition_width
        )
    
    def is_confident_inference_valid(self, entropy: float) -> bool:
        """Check if confident inference is valid for given entropy."""
        regime, _ = self.classify(entropy)
        return regime.allows_confident_output
    
    def get_confidence_ceiling(self, entropy: float) -> float:
        """Get maximum allowed confidence for given entropy."""
        regime, confidence = self.classify(entropy)
        
        if regime == Regime.L1:
            return 1.0
        elif regime == Regime.L2:
            # Scale ceiling based on position in L2
            return 0.3 + 0.4 * confidence  # Range: 0.3-0.7
        else:
            return 0.0
