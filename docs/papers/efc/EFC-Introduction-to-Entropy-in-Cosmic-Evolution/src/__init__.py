"""EFC Introduction to Entropy in Cosmic Evolution -- parameter and concept access module."""

from .entropy_cosmic_evolution import (
    CosmicEpoch,
    EntropyBudget,
    CosmicEntropyEvolution,
    BOLTZMANN_K,
    STEFAN_BOLTZMANN,
    CMB_TEMPERATURE,
    EPOCH_TEMPERATURES,
)

__all__ = [
    "CosmicEpoch",
    "EntropyBudget",
    "CosmicEntropyEvolution",
    "BOLTZMANN_K",
    "STEFAN_BOLTZMANN",
    "CMB_TEMPERATURE",
    "EPOCH_TEMPERATURES",
]

__version__ = "1.0.0"
