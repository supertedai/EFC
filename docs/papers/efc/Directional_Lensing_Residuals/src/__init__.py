"""
Directional Lensing Residuals Analysis Pipeline

Reference implementation for:
Magnusson (2026) "Directional Lensing Residuals at Cluster Merger Shock Fronts"
DOI: 10.6084/m9.figshare.31288063
"""

from .directional_lensing import (
    ShockGeometry,
    MassModel,
    AsigEstimator,
    RotationNull,
    DecisionCriteria,
    MockValidationResults,
    ExpectedSignal,
    GcDegeneracyBreaking,
    analyze_cluster,
)

__all__ = [
    "ShockGeometry",
    "MassModel",
    "AsigEstimator",
    "RotationNull",
    "DecisionCriteria",
    "MockValidationResults",
    "ExpectedSignal",
    "GcDegeneracyBreaking",
    "analyze_cluster",
]

__version__ = "1.0.0"
__doi__ = "10.6084/m9.figshare.31288063"
