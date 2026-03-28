"""Grid Microphysics to RAR — Minimal gradient-coupled excitation model.

Bridges the EFC microphysical gap: gradient-coupled bosonic excitations
on a discrete substrate produce the Bose-Einstein RAR form
mu(g) = 1/(exp(sqrt(g/a0)) - 1) from three assumptions only.

DOI: 10.6084/m9.figshare.31878760
"""

from .grid_microphysics import (
    GridNode,
    GradientCoupling,
    BoseEinsteinRAR,
    LatticeDerivation,
    MicrophysicalBridge,
    FalsificationCondition,
    compute_excitation_energy,
    compute_mu,
    compute_spring_constant,
    compute_transition_radius,
)

__all__ = [
    "GridNode",
    "GradientCoupling",
    "BoseEinsteinRAR",
    "LatticeDerivation",
    "MicrophysicalBridge",
    "FalsificationCondition",
    "compute_excitation_energy",
    "compute_mu",
    "compute_spring_constant",
    "compute_transition_radius",
]
