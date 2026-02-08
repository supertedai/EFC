"""
L-Axis Implementation

The L-axis represents the epistemic layer hierarchy based on measurement proximity.

Layers:
- L0: Raw measurement (direct sensor output)
- L1: Calibrated data (processed, corrected)
- L2: Derived quantities (computed from L1)
- L3: Theoretical constructs (model-dependent)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class LLayer(Enum):
    """Epistemic layer classification on L-axis."""
    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


@dataclass
class LayerInfo:
    """Information about an epistemic layer."""
    layer: LLayer
    name: str
    description: str
    proximity_to_observable: float  # 1.0 = direct, 0.0 = fully theoretical
    typical_examples: list[str]
    confidence_factor: float  # Epistemic confidence multiplier


class LAxis:
    """
    L-Axis classifier for epistemic layers.

    The L-axis organizes measurements by their proximity to
    raw observational data.
    """

    LAYER_DEFINITIONS = {
        LLayer.L0: LayerInfo(
            layer=LLayer.L0,
            name="Raw Measurement",
            description="Direct sensor output with minimal processing",
            proximity_to_observable=1.0,
            typical_examples=["photon counts", "voltage readings", "pixel values"],
            confidence_factor=1.0
        ),
        LLayer.L1: LayerInfo(
            layer=LLayer.L1,
            name="Calibrated Data",
            description="Processed data with instrument corrections applied",
            proximity_to_observable=0.75,
            typical_examples=["flux values", "calibrated spectra", "corrected images"],
            confidence_factor=0.9
        ),
        LLayer.L2: LayerInfo(
            layer=LLayer.L2,
            name="Derived Quantities",
            description="Computed values requiring assumptions or models",
            proximity_to_observable=0.5,
            typical_examples=["distances", "masses", "velocities", "accelerations"],
            confidence_factor=0.7
        ),
        LLayer.L3: LayerInfo(
            layer=LLayer.L3,
            name="Theoretical Constructs",
            description="Model-dependent quantities not directly observable",
            proximity_to_observable=0.25,
            typical_examples=["dark matter density", "inflation parameters", "string tensions"],
            confidence_factor=0.4
        ),
    }

    def __init__(self):
        """Initialize the L-axis classifier."""
        pass

    def classify(self, proxy_depth: int) -> LayerInfo:
        """
        Classify by proxy chain depth.

        Args:
            proxy_depth: Number of transformations from raw measurement

        Returns:
            LayerInfo for the classified layer
        """
        if proxy_depth < 0:
            raise ValueError("Proxy depth must be non-negative")

        if proxy_depth == 0:
            return self.LAYER_DEFINITIONS[LLayer.L0]
        elif proxy_depth == 1:
            return self.LAYER_DEFINITIONS[LLayer.L1]
        elif proxy_depth == 2:
            return self.LAYER_DEFINITIONS[LLayer.L2]
        else:
            return self.LAYER_DEFINITIONS[LLayer.L3]

    def get_layer(self, layer: LLayer) -> LayerInfo:
        """Get information about a specific layer."""
        return self.LAYER_DEFINITIONS[layer]

    def compute_confidence_degradation(self, start_layer: LLayer, end_layer: LLayer) -> float:
        """
        Compute confidence degradation between layers.

        Args:
            start_layer: Starting epistemic layer
            end_layer: Ending epistemic layer

        Returns:
            Confidence ratio (end/start)
        """
        start_info = self.LAYER_DEFINITIONS[start_layer]
        end_info = self.LAYER_DEFINITIONS[end_layer]

        return end_info.confidence_factor / start_info.confidence_factor

    def get_proxy_requirements(self, layer: LLayer) -> list[str]:
        """
        Get documentation requirements for a layer.

        Args:
            layer: Epistemic layer

        Returns:
            List of required documentation items
        """
        requirements = {
            LLayer.L0: ["instrument specification", "raw data format"],
            LLayer.L1: ["calibration procedure", "systematic corrections", "uncertainty estimates"],
            LLayer.L2: ["derivation method", "assumptions made", "input parameters", "error propagation"],
            LLayer.L3: ["theoretical model", "model parameters", "validity domain", "alternative models"],
        }
        return requirements.get(layer, [])
