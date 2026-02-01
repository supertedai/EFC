"""
Regime-Based World Modeling - Python Implementation

(R, L) coordinate system for organizing knowledge claims across
physical regimes and epistemic layers.

Reference:
    Magnusson, M. (2026). Regime-Based World Modeling: A Layered
    Epistemic Architecture for Complex Systems.
    DOI: 10.6084/m9.figshare.31223650
"""

from .world_model import WorldModel, ModelState
from .r_axis import RAxis, RRegime
from .l_axis import LAxis, LLayer
from .claim import Claim, ClaimSet
from .regime_gate import RegimeGate, TransferResult
from .driver_proximity import ProximityScore, compute_proximity

__version__ = "1.0.0"
__all__ = [
    "WorldModel",
    "ModelState",
    "RAxis",
    "RRegime",
    "LAxis",
    "LLayer",
    "Claim",
    "ClaimSet",
    "RegimeGate",
    "TransferResult",
    "ProximityScore",
    "compute_proximity",
]
