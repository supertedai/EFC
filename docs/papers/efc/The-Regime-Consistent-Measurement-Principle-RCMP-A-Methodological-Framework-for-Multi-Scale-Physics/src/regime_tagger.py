"""
Regime Tagger

Classifies measurements into epistemic layers (L0-L3) and physical regimes.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class EpistemicLayer(Enum):
    """
    Epistemic layer classification.

    L0: Direct measurement - raw sensor output
    L1: Calibrated observable - instrument corrections applied
    L2: Derived quantity - computed from L1 via physical models
    L3: Theoretical construct - inferred via theoretical framework
    """
    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"

    @property
    def description(self) -> str:
        descriptions = {
            "L0": "Direct measurement",
            "L1": "Calibrated observable",
            "L2": "Derived quantity",
            "L3": "Theoretical construct",
        }
        return descriptions[self.value]

    @property
    def epistemic_distance(self) -> int:
        """Distance from direct measurement (0-3)."""
        return int(self.value[1])


@dataclass
class RegimeInfo:
    """Information about a measurement's regime classification."""
    layer: EpistemicLayer
    regime_name: str
    boundary_condition: Optional[str] = None
    confidence: float = 1.0
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer": self.layer.value,
            "regime": self.regime_name,
            "boundary": self.boundary_condition,
            "confidence": self.confidence,
            "notes": self.notes,
        }


class RegimeTagger:
    """
    Tags measurements with epistemic layer and regime information.

    Example:
        tagger = RegimeTagger()

        # Classify by acceleration threshold
        regime = tagger.classify_acceleration(g_bar=5e-12)
        # Returns: RegimeInfo(layer=L2, regime_name="low_acceleration", ...)

        # Classify by custom measurement
        regime = tagger.classify(
            measurement={"type": "velocity", "value": 125.3},
            layer=EpistemicLayer.L1
        )
    """

    # Default thresholds for galaxy dynamics
    DEFAULT_THRESHOLDS = {
        "acceleration": {
            "low": 1e-11,  # m/s² - below this is low-acceleration regime
            "high": 1e-9,  # m/s² - above this is high-acceleration regime
        },
        "velocity": {
            "low": 50,     # km/s - slow rotators
            "high": 200,   # km/s - fast rotators
        },
    }

    def __init__(self, thresholds: Optional[Dict] = None):
        """
        Initialize with optional custom thresholds.

        Args:
            thresholds: Custom threshold dictionary
        """
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS

    def classify(
        self,
        measurement: Dict[str, Any],
        layer: Optional[EpistemicLayer] = None,
    ) -> RegimeInfo:
        """
        Classify a measurement into regime.

        Args:
            measurement: Dictionary with measurement data
            layer: Explicit epistemic layer (if known)

        Returns:
            RegimeInfo with classification
        """
        # Determine layer from measurement type if not provided
        if layer is None:
            layer = self._infer_layer(measurement)

        # Determine regime from value and type
        regime_name = self._determine_regime(measurement)
        boundary = self._get_boundary_condition(measurement)

        return RegimeInfo(
            layer=layer,
            regime_name=regime_name,
            boundary_condition=boundary,
        )

    def classify_acceleration(
        self,
        g_bar: float,
        g_obs: Optional[float] = None,
    ) -> RegimeInfo:
        """
        Classify by baryonic acceleration.

        Args:
            g_bar: Baryonic acceleration in m/s²
            g_obs: Observed acceleration in m/s² (optional)

        Returns:
            RegimeInfo for acceleration regime
        """
        low_threshold = self.thresholds["acceleration"]["low"]
        high_threshold = self.thresholds["acceleration"]["high"]

        if g_bar < low_threshold:
            regime_name = "low_acceleration"
            boundary = f"g_bar < {low_threshold:.0e} m/s²"
        elif g_bar > high_threshold:
            regime_name = "high_acceleration"
            boundary = f"g_bar > {high_threshold:.0e} m/s²"
        else:
            regime_name = "intermediate_acceleration"
            boundary = f"{low_threshold:.0e} < g_bar < {high_threshold:.0e} m/s²"

        return RegimeInfo(
            layer=EpistemicLayer.L2,  # Acceleration is derived (L2)
            regime_name=regime_name,
            boundary_condition=boundary,
        )

    def classify_velocity(self, v_rot: float) -> RegimeInfo:
        """
        Classify by rotation velocity.

        Args:
            v_rot: Rotation velocity in km/s

        Returns:
            RegimeInfo for velocity regime
        """
        low_threshold = self.thresholds["velocity"]["low"]
        high_threshold = self.thresholds["velocity"]["high"]

        if v_rot < low_threshold:
            regime_name = "slow_rotator"
            boundary = f"V_rot < {low_threshold} km/s"
        elif v_rot > high_threshold:
            regime_name = "fast_rotator"
            boundary = f"V_rot > {high_threshold} km/s"
        else:
            regime_name = "moderate_rotator"
            boundary = f"{low_threshold} < V_rot < {high_threshold} km/s"

        return RegimeInfo(
            layer=EpistemicLayer.L1,  # Velocity is calibrated observable (L1)
            regime_name=regime_name,
            boundary_condition=boundary,
        )

    def tag_dataset(
        self,
        measurements: List[Dict[str, Any]],
        regime_key: str = "g_bar",
    ) -> List[Dict[str, Any]]:
        """
        Tag all measurements in a dataset.

        Args:
            measurements: List of measurement dictionaries
            regime_key: Key to use for regime classification

        Returns:
            Measurements with added regime tags
        """
        tagged = []
        for m in measurements:
            m_copy = m.copy()

            if regime_key == "g_bar" and "g_bar" in m:
                regime = self.classify_acceleration(m["g_bar"])
            elif regime_key == "velocity" and "v_rot" in m:
                regime = self.classify_velocity(m["v_rot"])
            else:
                regime = self.classify(m)

            m_copy["regime_info"] = regime.to_dict()
            tagged.append(m_copy)

        return tagged

    def _infer_layer(self, measurement: Dict[str, Any]) -> EpistemicLayer:
        """Infer epistemic layer from measurement type."""
        mtype = measurement.get("type", "").lower()

        layer_mapping = {
            # L0 - Direct measurements
            "spectral_line": EpistemicLayer.L0,
            "photon_count": EpistemicLayer.L0,
            "raw_velocity": EpistemicLayer.L0,

            # L1 - Calibrated observables
            "velocity": EpistemicLayer.L1,
            "magnitude": EpistemicLayer.L1,
            "flux": EpistemicLayer.L1,

            # L2 - Derived quantities
            "acceleration": EpistemicLayer.L2,
            "mass": EpistemicLayer.L2,
            "distance": EpistemicLayer.L2,

            # L3 - Theoretical constructs
            "dark_matter_density": EpistemicLayer.L3,
            "halo_mass": EpistemicLayer.L3,
        }

        return layer_mapping.get(mtype, EpistemicLayer.L1)

    def _determine_regime(self, measurement: Dict[str, Any]) -> str:
        """Determine regime name from measurement."""
        # Check for explicit regime
        if "regime" in measurement:
            return measurement["regime"]

        # Check for acceleration-based classification
        if "g_bar" in measurement:
            return self.classify_acceleration(measurement["g_bar"]).regime_name

        return "unclassified"

    def _get_boundary_condition(self, measurement: Dict[str, Any]) -> Optional[str]:
        """Get boundary condition for regime."""
        if "g_bar" in measurement:
            return self.classify_acceleration(measurement["g_bar"]).boundary_condition
        return None
