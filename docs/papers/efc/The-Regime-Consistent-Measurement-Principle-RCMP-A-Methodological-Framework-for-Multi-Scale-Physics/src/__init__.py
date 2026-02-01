"""
RCMP - Regime-Consistent Measurement Principle

A methodological framework for preventing interpretive errors when
measurements span multiple physical regimes.

Reference:
    Magnusson, M. (2026). The Regime-Consistent Measurement Principle (RCMP):
    A Methodological Framework for Multi-Scale Physics.
    DOI: 10.6084/m9.figshare.31222900

Usage:
    from src.rcmp_validator import RCMPValidator
    from src.regime_tagger import RegimeTagger
    from src.proxy_chain import ProxyChain
    from src.uncertainty_propagator import UncertaintyPropagator

License: CC BY 4.0
"""

__version__ = "1.0.0"
__author__ = "Morten Magnusson"
__doi__ = "10.6084/m9.figshare.31222900"

from .rcmp_validator import RCMPValidator, ValidationResult, ChecklistItem
from .regime_tagger import RegimeTagger, RegimeInfo, EpistemicLayer
from .proxy_chain import ProxyChain, ProxyStep
from .uncertainty_propagator import UncertaintyPropagator

__all__ = [
    "RCMPValidator",
    "ValidationResult",
    "ChecklistItem",
    "RegimeTagger",
    "RegimeInfo",
    "EpistemicLayer",
    "ProxyChain",
    "ProxyStep",
    "UncertaintyPropagator",
]
