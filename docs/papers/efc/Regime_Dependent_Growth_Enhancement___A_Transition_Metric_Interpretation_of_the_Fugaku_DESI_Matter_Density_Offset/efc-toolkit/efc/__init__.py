"""
EFC Toolkit - Energy-Flow Cosmology Framework
=============================================

A Python package for regime-dependent cosmological calculations,
transition metrics, and validity-aware inference.

Author: Morten Magnusson
Address: Hasselvegen 5, 4051 Sola, Norway
ORCID: 0009-0002-4860-5095
License: MIT

Core Publications (DOIs):
- Foundations: 10.6084/m9.figshare.31135597
- DESI BAO Fit: 10.6084/m9.figshare.31127380
- Regime Transition: 10.6084/m9.figshare.31096951
- L0-L3 Architecture: 10.6084/m9.figshare.31112536
- SPARC Analysis: 10.6084/m9.figshare.31045126
"""

__version__ = "0.1.0"
__author__ = "Morten Magnusson"
__author_address__ = "Hasselvegen 5, 4051 Sola, Norway"
__orcid__ = "0009-0002-4860-5095"

from .regimes import Regime, L0, L1, L2, L3, get_regime
from .transition import TransitionFunction, TransitionEstimator
from .constants import EFC_CONSTANTS, DOIS
from .validators import ValidityChecker, RegimeBoundary

__all__ = [
    # Regimes
    "Regime", "L0", "L1", "L2", "L3", "get_regime",
    # Transition
    "TransitionFunction", "TransitionEstimator", 
    # Constants
    "EFC_CONSTANTS", "DOIS",
    # Validators
    "ValidityChecker", "RegimeBoundary",
]
