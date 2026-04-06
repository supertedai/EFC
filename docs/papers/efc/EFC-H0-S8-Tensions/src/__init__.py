"""
EFC H0 and S8 Tensions Resolution

Implements the entropy-dependent gravitational coupling model
that resolves the Hubble and S8 tensions simultaneously.

Reference:
    Magnusson, M. (2026). Resolving the H0 and S8 Tensions Through
    Local-Global Inference Separation. DOI: 10.6084/m9.figshare.31026151
"""

from .h0_s8_tensions import (
    EffectiveGravity,
    HubbleTension,
    S8Tension,
    TensionResolver,
)

__version__ = "1.0.0"
__all__ = [
    "EffectiveGravity",
    "HubbleTension",
    "S8Tension",
    "TensionResolver",
]
