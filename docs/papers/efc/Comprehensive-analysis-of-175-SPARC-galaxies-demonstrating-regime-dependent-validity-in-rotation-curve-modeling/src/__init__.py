"""
SPARC175 Regime Analysis Module
================================
Comprehensive analysis of 175 SPARC galaxies demonstrating
regime-dependent validity in rotation curve modeling.

Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
Affiliation: Symbiose Research, Sandnes, Norway
License: CC-BY-4.0
"""

from .sparc175 import (
    EFCRotationCurve,
    NFWRotationCurve,
    LatentProxy,
    RegimeClassifier,
    REGIME_FLOW,
    REGIME_TRANSITION,
    REGIME_LATENT,
)

__version__ = "1.0.0"
__author__ = "Morten Magnusson"
__all__ = [
    "EFCRotationCurve",
    "NFWRotationCurve",
    "LatentProxy",
    "RegimeClassifier",
    "REGIME_FLOW",
    "REGIME_TRANSITION",
    "REGIME_LATENT",
]
