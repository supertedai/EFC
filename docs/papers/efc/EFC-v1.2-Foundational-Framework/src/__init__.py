"""EFC v1.2 Foundational Framework -- core definitions and fields.

Implements the four fundamental EFC fields, regime architecture (L0-L3),
thermodynamic foundations, and structural relationships.

DOI: 10.6084/m9.figshare.30563738
"""
from .efc_foundational import (
    EFCField, Regime, ThermodynamicFoundation, StructuralRelation,
    FoundationalFramework, canonical_fields, regime_architecture,
    thermodynamic_principles, structural_relationships, entropy_sigmoid,
    BOLTZMANN_K, PLANCK_H, C_LIGHT, G_NEWTON,
)

__all__ = [
    "EFCField", "Regime", "ThermodynamicFoundation", "StructuralRelation",
    "FoundationalFramework", "canonical_fields", "regime_architecture",
    "thermodynamic_principles", "structural_relationships", "entropy_sigmoid",
    "BOLTZMANN_K", "PLANCK_H", "C_LIGHT", "G_NEWTON",
]
