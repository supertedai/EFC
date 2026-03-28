"""
Covariant EFT for Entropy-Driven Gravitational Modification.
Reference implementation for the paper by Morten Magnusson (2026).
"""

from .covariant_eft import (
    CovEFTAction,
    BoseEinsteinRAR,
    GravitationalSlip,
    SolarSystemTest,
    StabilityAnalysis,
    SelfConsistentSolution,
    ConstructionIteration,
    run_eft_demo,
)

__all__ = [
    "CovEFTAction",
    "BoseEinsteinRAR",
    "GravitationalSlip",
    "SolarSystemTest",
    "StabilityAnalysis",
    "SelfConsistentSolution",
    "ConstructionIteration",
    "run_eft_demo",
]
