"""EFC Formal Specification -- mathematical objects and constraints.

Canonical notation, field equations, entropy definition, thermodynamic
constraint set, and grid field formal structure.
"""
from .efc_formal import (
    FormalSymbol, FormalFieldEquation, FormalEntropySigmoid,
    ThermodynamicConstraint, GridFieldSpec, EFCFormalSpec,
    symbol_table, constraint_set,
)

__all__ = [
    "FormalSymbol", "FormalFieldEquation", "FormalEntropySigmoid",
    "ThermodynamicConstraint", "GridFieldSpec", "EFCFormalSpec",
    "symbol_table", "constraint_set",
]
