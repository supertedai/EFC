"""
EBE Core Principles - Python Implementation

Entropy-Bounded Empiricism framework for organizing physical claims
by entropy regime (S-axis) and epistemic layer (L-axis).

Reference:
    Magnusson, M. (2026). Entropy-Bounded Empiricism: Core Principles.
    DOI: 10.6084/m9.figshare.31222903
"""

from .ebe_classifier import EBEClassifier, ClassificationResult
from .s_axis import SAxis, SRegime
from .l_axis import LAxis, LLayer
from .regime_gating import RegimeGate, TransferValidator

__version__ = "1.0.0"
__all__ = [
    "EBEClassifier",
    "ClassificationResult",
    "SAxis",
    "SRegime",
    "LAxis",
    "LLayer",
    "RegimeGate",
    "TransferValidator",
]
