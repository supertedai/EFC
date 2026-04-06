"""
EFC Void ISW Sign-Flip
======================
Density-dependent gravitational coupling predicts ISW sign-flip in deep voids.

DOI: 10.6084/m9.figshare.31942677
Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)

Classes:
    ISWDecomposition   - dΦ/dt = μ·(dδ/dt) + δ·(dμ/dt)
    ReesSciamaTerm     - Non-linear RS contribution δ·dμ/dt
    AmplitudeRatio     - A_total = ΔT_EFC/ΔT_ΛCDM (Table 1)
    VoidProfile        - Void density and evolution models
    SignFlipAnalysis   - Find sign-flip threshold and turnover
    Predictions        - P1 (depth turnover), P2 (scale), P3 (redshift)
"""

from .void_isw import (
    ISWDecomposition,
    ReesSciamaTerm,
    AmplitudeRatio,
    VoidProfile,
    SignFlipAnalysis,
    Predictions,
)

__all__ = [
    "ISWDecomposition",
    "ReesSciamaTerm",
    "AmplitudeRatio",
    "VoidProfile",
    "SignFlipAnalysis",
    "Predictions",
]

__version__ = "2.1.0"
__doi__ = "10.6084/m9.figshare.31942677"
