"""
EFC Perturbation Package
========================

Implements the perturbation-level physics from EFCLASS Technical Notes I & II
and the MVP-G1 Hubble-Friction robustness analysis.

Modules
-------
gate        : Sigmoid gate function g(a) and calibration protocol
background  : Background-level ΔE² sign structure (Technical Note I)
mu          : Perturbation-level μ(a) < 1 modification (Technical Note II)
growth      : Linear growth equation solver with modified μ(a)
robustness  : Leave-one-out and fit utilities (Growth-Sector Robustness)
data        : Observational data compilations (BAO, fσ₈)

References
----------
- DOI: 10.6084/m9.figshare.31333414 (Technical Note I: Sign structure)
- DOI: 10.6084/m9.figshare.31333600 (Technical Note II: σ₈ suppression)
- DOI: 10.6084/m9.figshare.31332730 (Growth-Sector Robustness)
"""

from .gate import gate_function, gate_function_z, calibrate_B
from .background import delta_E2, E2_efc, hubble_efc
from .mu import mu_of_a, mu_of_z, sigma8_suppression_integral
from .growth import growth_ode, solve_growth, compute_fsigma8

__all__ = [
    "gate_function",
    "gate_function_z",
    "calibrate_B",
    "delta_E2",
    "E2_efc",
    "hubble_efc",
    "mu_of_a",
    "mu_of_z",
    "sigma8_suppression_integral",
    "growth_ode",
    "solve_growth",
    "compute_fsigma8",
]
