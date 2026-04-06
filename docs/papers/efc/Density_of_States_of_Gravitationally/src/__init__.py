"""
Density of States of Gravitationally Active Grid Modes — AI-Friendly Source Package
DOI: 10.6084/m9.figshare.31942800

Derives D_eff(ρ) ∝ √(ρ/ρ_crit) from boundary-mode mechanism.
Completes Γ(ρ) bridge: Γ = Γ₀ √(ρ/ρ_crit) / (1 + √(ρ/ρ_crit)).
"""

from .density_of_states import (
    GridActivation,
    DensityOfStates,
    PerModeEntropy,
    EntropyProductionFunction,
    ScenarioComparison,
    Predictions,
)

__all__ = [
    "GridActivation",
    "DensityOfStates",
    "PerModeEntropy",
    "EntropyProductionFunction",
    "ScenarioComparison",
    "Predictions",
]
