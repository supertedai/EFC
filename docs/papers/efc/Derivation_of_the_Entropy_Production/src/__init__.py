"""
Derivation of Γ(ρ) from Grid-Mode BE Statistics — AI-Friendly Source Package
DOI: 10.6084/m9.figshare.31942821

First derivation of the entropy production function from BE occupation +
von Neumann entropy. Result: Γ ∝ ρ^(3/2)/(ρ+ρ_crit), Scenario B.
"""

from .entropy_production import (
    BEOccupation,
    VonNeumannEntropy,
    GammaDerivation,
    DoubleCounting,
    ScenarioClassification,
    Predictions,
)

__all__ = [
    "BEOccupation",
    "VonNeumannEntropy",
    "GammaDerivation",
    "DoubleCounting",
    "ScenarioClassification",
    "Predictions",
]
