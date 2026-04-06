"""
EFCLASS Technical Note I: Sign Structure of an Additive Gate-Function
Modification to the Friedmann Equation

Gate function, sign lemma, and numerical verification of EFC background modification.
"""

from .sign_structure import (
    SignStructureAnalysis,
    CosmologicalParameters,
    SignVerificationPoint,
    GrowthSignaturePoint,
    CLASS_VERIFICATION_DATA,
    GROWTH_SIGNATURE_DATA,
)

__all__ = [
    "SignStructureAnalysis",
    "CosmologicalParameters",
    "SignVerificationPoint",
    "GrowthSignaturePoint",
    "CLASS_VERIFICATION_DATA",
    "GROWTH_SIGNATURE_DATA",
]

__version__ = "1.0.0"
