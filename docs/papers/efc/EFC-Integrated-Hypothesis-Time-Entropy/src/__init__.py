"""EFC Integrated Hypothesis: Time and Entropy -- parameter and concept access module."""

from .time_entropy import (
    EntropyState,
    TemporalGradient,
    CausalChain,
    TimeEntropyModel,
    BOLTZMANN_K,
)

__all__ = [
    "EntropyState",
    "TemporalGradient",
    "CausalChain",
    "TimeEntropyModel",
    "BOLTZMANN_K",
]

__version__ = "1.0.0"
