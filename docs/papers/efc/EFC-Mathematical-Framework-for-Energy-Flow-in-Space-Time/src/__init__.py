"""EFC Mathematical Framework for Energy Flow in Space-Time -- parameter and concept access module."""

from .math_framework import (
    ScalarField,
    EnergyFlowEquation,
    EntropyFieldEquation,
    GateFunction,
    MathFrameworkModel,
    BOLTZMANN_K,
    SPEED_OF_LIGHT,
    GRAVITATIONAL_G,
    DEFAULT_GRID_RESISTANCE,
)

__all__ = [
    "ScalarField",
    "EnergyFlowEquation",
    "EntropyFieldEquation",
    "GateFunction",
    "MathFrameworkModel",
    "BOLTZMANN_K",
    "SPEED_OF_LIGHT",
    "GRAVITATIONAL_G",
    "DEFAULT_GRID_RESISTANCE",
]

__version__ = "1.0.0"
