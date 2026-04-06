"""
EFC Balance and Universal Structures

Implements the balance-driven structure formation model showing
how opposing gradients and entropic pressures produce stable
large-scale configurations.

Reference:
    Magnusson, M. EFC -- How Does Balance Shape Universal Structures?
"""

from .balance_structures import (
    GradientBalance,
    EquilibriumStructure,
    UniversalStructureModel,
)

__version__ = "1.0.0"
__all__ = [
    "GradientBalance",
    "EquilibriumStructure",
    "UniversalStructureModel",
]
