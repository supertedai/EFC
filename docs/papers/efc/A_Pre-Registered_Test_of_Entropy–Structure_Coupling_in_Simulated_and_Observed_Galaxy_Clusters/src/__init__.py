"""
Entropy-Structure Coupling Analysis

Reference implementation for:
Magnusson (2026) "A Pre-Registered Test of Entropy-Structure Coupling
in Simulated and Observed Galaxy Clusters"
DOI: 10.6084/m9.figshare.31286368
"""

from .entropy_structure_coupling import (
    CoolCoreClass,
    EntropyProfileParams,
    CorrelationResult,
    EntropyProfileModel,
    AlphaProxy,
    CoolCoreClassifier,
    CorrelationAnalysis,
    PreRegisteredTest,
    InterpretationFramework,
    compute_entropy,
    classify_cool_core,
    compute_alpha_proxy,
)

__all__ = [
    "CoolCoreClass",
    "EntropyProfileParams",
    "CorrelationResult",
    "EntropyProfileModel",
    "AlphaProxy",
    "CoolCoreClassifier",
    "CorrelationAnalysis",
    "PreRegisteredTest",
    "InterpretationFramework",
    "compute_entropy",
    "classify_cool_core",
    "compute_alpha_proxy",
]

__version__ = "1.0.0"
__doi__ = "10.6084/m9.figshare.31286368"
