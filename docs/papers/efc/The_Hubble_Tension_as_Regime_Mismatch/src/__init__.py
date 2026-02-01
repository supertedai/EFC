"""
The Hubble Tension as Regime Mismatch

This package provides tools for analyzing the Hubble tension
as a regime mismatch between background and structure gravity.

Key insight: Different probes see different G, not different H₀.

Modules:
    regime_classifier: Classify probes by gravitational regime
    g_effective: Calculate regime-dependent G_eff
    h0_predictor: Predict H₀ by regime
    falsification: Test falsification criteria
"""

from .regime_classifier import (
    Regime,
    RegimeClassifier,
    classify_probe,
    get_probe_info,
)
from .g_effective import (
    GravityRegime,
    GEffectiveCalculator,
    compute_g_effective,
    compute_enhancement,
)

__all__ = [
    "Regime",
    "RegimeClassifier",
    "classify_probe",
    "get_probe_info",
    "GravityRegime",
    "GEffectiveCalculator",
    "compute_g_effective",
    "compute_enhancement",
]

__version__ = "1.0.0"
