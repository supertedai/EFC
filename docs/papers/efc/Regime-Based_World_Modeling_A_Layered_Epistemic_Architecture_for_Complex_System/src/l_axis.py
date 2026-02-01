"""
L-Axis Implementation

The L-axis represents the epistemic layer hierarchy based on measurement proximity.

Layers:
- L0: Raw (direct sensor output)
- L1: Calibrated (processed, corrected)
- L2: Derived (computed from L1)
- L3: Theoretical (model-dependent)
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
    proximity: float  # 1.0 = direct, 0.0 = fully theoretical
    confidence_factor: float


class LAxis:
    """
    L-Axis classifier for epistemic layers.

    The L-axis organizes measurements by their proximity to
    raw observational data.
    """

    LAYER_DEFINITIONS = {
        LLayer.L0: LayerInfo(
            layer=LLayer.L0,
            name="Raw",
            description="Direct measurement output",
            proximity=1.0,
            confidence_factor=1.0
        ),
        LLayer.L1: LayerInfo(
            layer=LLayer.L1,
            name="Calibrated",
            description="Processed and corrected data",
            proximity=0.75,
            confidence_factor=0.9
        ),
        LLayer.L2: LayerInfo(
            layer=LLayer.L2,
            name="Derived",
            description="Computed quantities",
            proximity=0.5,
            confidence_factor=0.7
        ),
        LLayer.L3: LayerInfo(
            layer=LLayer.L3,
            name="Theoretical",
            description="Model-dependent constructs",
            proximity=0.25,
            confidence_factor=0.4
        ),
    }

    def __init__(self):
        """Initialize the L-axis classifier."""
        pass

    def classify_by_depth(self, proxy_depth: int) -> LayerInfo:
        """
        Classify by proxy chain depth.

        Args:
            proxy_depth: Number of steps from direct measurement

        Returns:
            LayerInfo for the classified layer
        """
        if proxy_depth <= 0:
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

    def get_layer_order(self) -> list[LLayer]:
        """Get layers in order of abstraction."""
        return [LLayer.L0, LLayer.L1, LLayer.L2, LLayer.L3]

    def distance(self, l1: LLayer, l2: LLayer) -> int:
        """
        Compute distance between two layers.

        Args:
            l1: First layer
            l2: Second layer

        Returns:
            Number of layer steps between them
        """
        order = self.get_layer_order()
        return abs(order.index(l1) - order.index(l2))

    def confidence_degradation(self, source: LLayer, target: LLayer) -> float:
        """
        Compute confidence degradation between layers.

        Args:
            source: Starting layer
            target: Ending layer

        Returns:
            Confidence ratio (end/start)
        """
        source_info = self.LAYER_DEFINITIONS[source]
        target_info = self.LAYER_DEFINITIONS[target]
        return target_info.confidence_factor / source_info.confidence_factor
