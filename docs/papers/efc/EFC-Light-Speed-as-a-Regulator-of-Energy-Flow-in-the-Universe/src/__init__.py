"""EFC Light Speed as a Regulator of Energy Flow -- parameter and concept access module."""

from .light_speed_regulator import (
    PropagationRegime,
    CausalHorizon,
    StabilityAnalysis,
    LightSpeedRegulatorModel,
    SPEED_OF_LIGHT,
    BOLTZMANN_K,
    PLANCK_LENGTH,
    PLANCK_TIME,
    DEFAULT_GRID_RESISTANCE,
)

__all__ = [
    "PropagationRegime",
    "CausalHorizon",
    "StabilityAnalysis",
    "LightSpeedRegulatorModel",
    "SPEED_OF_LIGHT",
    "BOLTZMANN_K",
    "PLANCK_LENGTH",
    "PLANCK_TIME",
    "DEFAULT_GRID_RESISTANCE",
]

__version__ = "1.0.0"
