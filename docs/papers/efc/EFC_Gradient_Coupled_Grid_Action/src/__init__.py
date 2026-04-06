"""
EFC Gradient-Coupled Grid Action
=================================
Minimal Lagrangian derivation of E ∝ √g from the three-term grid action S_grid.

DOI: 10.6084/m9.figshare.31941465
Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)

Classes:
    GridAction              - Three-term Lagrangian (kinetic + bare elastic + gradient coupling)
    EffectiveStiffness      - κ_eff(x) = κ₀ + αg(x) from Euler-Lagrange
    DispersionRelation      - ω²(k,g) = κ_eff/m_eff · k²
    GradientCouplingTheorem - E ∝ √g in the gravitational regime (Theorem 1)
    OperatorElimination     - C1-C5 operator classification and elimination
    RegimeAnalysis          - Three physical regimes and crossover
    BosonicQuantisation     - Fock space and Bose-Einstein statistics
    FalsifiablePredictions  - P1 (stiffness bound) and P2 (dispersion signature)
"""

from .grid_action import (
    GridAction,
    EffectiveStiffness,
    DispersionRelation,
    GradientCouplingTheorem,
    OperatorElimination,
    RegimeAnalysis,
    BosonicQuantisation,
    FalsifiablePredictions,
)

__all__ = [
    "GridAction",
    "EffectiveStiffness",
    "DispersionRelation",
    "GradientCouplingTheorem",
    "OperatorElimination",
    "RegimeAnalysis",
    "BosonicQuantisation",
    "FalsifiablePredictions",
]

__version__ = "1.0.0"
__doi__ = "10.6084/m9.figshare.31941465"
