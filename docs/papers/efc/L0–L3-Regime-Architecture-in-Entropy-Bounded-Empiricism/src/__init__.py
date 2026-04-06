"""
L0-L3 Regime Architecture - Python Package
Provides tools for regime validation and leakage detection
in Entropy-Bounded Empiricism (EBE).
"""

from .regime_validator import Regime, InferenceType, RegimeValidator

__all__ = ["Regime", "InferenceType", "RegimeValidator"]
__version__ = "1.0.0"
