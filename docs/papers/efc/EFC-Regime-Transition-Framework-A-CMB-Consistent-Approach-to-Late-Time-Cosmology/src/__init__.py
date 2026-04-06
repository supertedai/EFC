"""
EFC Regime Transition Framework: A CMB-Consistent Approach to Late-Time Cosmology

Landau-theory gating function, regime transitions, and CMB safety verification.
"""

from .regime_transition import (
    RegimeTransitionFramework,
    CosmologyParams,
    RegimeParams,
    NumericalParams,
    CMBSafetyResult,
    KEY_GATING_VALUES,
)

__all__ = [
    "RegimeTransitionFramework",
    "CosmologyParams",
    "RegimeParams",
    "NumericalParams",
    "CMBSafetyResult",
    "KEY_GATING_VALUES",
]

__version__ = "1.0.0"
