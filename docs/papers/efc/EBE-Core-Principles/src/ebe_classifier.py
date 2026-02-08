"""
EBE Classifier Implementation

Main classification engine for Entropy-Bounded Empiricism.
Combines S-axis and L-axis classification.
"""

from dataclasses import dataclass
from typing import Optional

from .s_axis import SAxis, SRegime, RegimeInfo
from .l_axis import LAxis, LLayer, LayerInfo


@dataclass
class ClassificationResult:
    """Result of an EBE classification."""
    observable: str
    s_regime: SRegime
    l_layer: LLayer
    s_info: RegimeInfo
    l_info: LayerInfo
    proxy_depth: int
    confidence: float
    regime_boundary: Optional[str] = None
    notes: Optional[str] = None

    def summary(self) -> str:
        """Generate human-readable summary."""
        return (
            f"Classification: {self.observable}\n"
            f"  S-Regime: {self.s_regime.value} ({self.s_info.name})\n"
            f"  L-Layer: {self.l_layer.value} ({self.l_info.name})\n"
            f"  Proxy Depth: {self.proxy_depth}\n"
            f"  Confidence: {self.confidence:.2%}"
        )


class EBEClassifier:
    """
    Main EBE classification engine.

    Classifies physical claims by their position in (S, L) space
    and computes associated epistemic confidence.

    Example:
        classifier = EBEClassifier()
        result = classifier.classify(
            observable="galaxy_rotation_velocity",
            s_parameter=0.8,
            proxy_depth=2
        )
        print(result.summary())
    """

    def __init__(self):
        """Initialize the classifier."""
        self.s_axis = SAxis()
        self.l_axis = LAxis()

    def classify(
        self,
        observable: str,
        s_parameter: Optional[float] = None,
        system_type: Optional[str] = None,
        proxy_depth: int = 0,
        regime_boundary: Optional[str] = None,
    ) -> ClassificationResult:
        """
        Classify an observable by (S, L) coordinates.

        Args:
            observable: Name of the physical quantity
            s_parameter: Normalized entropy parameter (0-1), or None
            system_type: Type of physical system, used if s_parameter is None
            proxy_depth: Number of proxy steps from direct measurement
            regime_boundary: Optional boundary condition string

        Returns:
            ClassificationResult with full classification
        """
        # Determine S-regime
        if s_parameter is not None:
            s_info = self.s_axis.classify(s_parameter)
        elif system_type is not None:
            s_info = self.s_axis.classify_by_system(system_type)
            if s_info is None:
                raise ValueError(f"Unknown system type: {system_type}")
        else:
            raise ValueError("Must provide either s_parameter or system_type")

        # Determine L-layer
        l_info = self.l_axis.classify(proxy_depth)

        # Compute confidence
        base_confidence = l_info.confidence_factor
        # Adjust for regime complexity
        regime_adjustment = 1.0 - (s_info.entropy_range[1] - 0.5) * 0.2
        confidence = base_confidence * regime_adjustment

        return ClassificationResult(
            observable=observable,
            s_regime=s_info.regime,
            l_layer=l_info.layer,
            s_info=s_info,
            l_info=l_info,
            proxy_depth=proxy_depth,
            confidence=confidence,
            regime_boundary=regime_boundary,
        )

    def classify_measurement(
        self,
        observable: str,
        measurement_type: str,
        regime: str,
    ) -> ClassificationResult:
        """
        Simplified classification interface.

        Args:
            observable: Name of quantity being measured
            measurement_type: Type of measurement (spectroscopic, photometric, etc.)
            regime: Physical regime name

        Returns:
            ClassificationResult
        """
        # Map measurement type to proxy depth
        measurement_depths = {
            "direct": 0,
            "spectroscopic": 1,
            "photometric": 1,
            "derived": 2,
            "model": 3,
            "theoretical": 3,
        }
        proxy_depth = measurement_depths.get(measurement_type.lower(), 2)

        # Map regime string to S-parameter
        regime_params = {
            "low_s": 0.15,
            "mid_s": 0.5,
            "high_s": 0.85,
            "particle": 0.1,
            "atomic": 0.2,
            "stellar": 0.5,
            "galactic": 0.8,
            "cosmological": 0.9,
        }
        s_param = regime_params.get(regime.lower(), 0.5)

        return self.classify(
            observable=observable,
            s_parameter=s_param,
            proxy_depth=proxy_depth,
        )

    def validate_claim_transfer(
        self,
        claim: str,
        source: ClassificationResult,
        target_s: SRegime,
        target_l: LLayer,
    ) -> tuple[bool, str]:
        """
        Validate if a claim can transfer between (S, L) positions.

        Args:
            claim: The claim being transferred
            source: Source classification
            target_s: Target S-regime
            target_l: Target L-layer

        Returns:
            Tuple of (is_valid, reason)
        """
        # Check S-axis transfer
        s_valid, s_reason = self.s_axis.can_transfer(source.s_regime, target_s)

        # Check L-axis degradation
        target_l_info = self.l_axis.get_layer(target_l)
        l_degradation = self.l_axis.compute_confidence_degradation(
            source.l_layer, target_l
        )

        if not s_valid:
            return False, f"S-axis: {s_reason}"

        if l_degradation < 0.5:
            return False, f"L-axis: Confidence degradation too severe ({l_degradation:.0%})"

        return True, f"Transfer valid with {l_degradation:.0%} confidence retention"
