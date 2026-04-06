"""EFC v2.1 Complete Edition -- consolidated EFC specification.

Field equations, entropy sigmoid, gravitational coupling, modified
Friedmann dynamics, and complete regime architecture.
"""
from .efc_complete import (
    EntropyField, GravitationalCoupling, ModifiedFriedmann,
    EFCFieldEquation, EFCCompleteEdition,
    C_LIGHT, G_NEWTON, H0_PLANCK, H0_SHOES,
)

__all__ = [
    "EntropyField", "GravitationalCoupling", "ModifiedFriedmann",
    "EFCFieldEquation", "EFCCompleteEdition",
    "C_LIGHT", "G_NEWTON", "H0_PLANCK", "H0_SHOES",
]
