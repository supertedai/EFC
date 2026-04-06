"""
Lensing Response Model

Reference implementation for:
Magnusson (2026) "A Regime-Activated Lensing Response Improves the
Fit to KiDS-1000 Cosmic Shear and Reframes the S8 Tension"
DOI: 10.6084/m9.figshare.31271917
"""

from .lensing_response import (
    LensingResponseParams,
    LensingResponse,
    S8Reframing,
    TomographicFingerprint,
    LikelihoodAnalysis,
    demonstrate,
)

__all__ = [
    "LensingResponseParams",
    "LensingResponse",
    "S8Reframing",
    "TomographicFingerprint",
    "LikelihoodAnalysis",
    "demonstrate",
]

__version__ = "1.0.0"
__doi__ = "10.6084/m9.figshare.31271917"
