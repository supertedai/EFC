"""
EFC Regime Transition Test
==========================
Numerical consistency test of the EFC regime transition: μ < 1 (linear)
and μ > 1 (non-linear) from the same relativistic action.

DOI: 10.6084/m9.figshare.31941543
Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)

Classes:
    EFCRegimeTransition   - Core μ(k), η(k), Σ(k) computation
    StiffnessResponse     - R(k) ∝ k⁻⁴ mechanism
    SurvivalValley        - Constraint checking μ ∈ [0.90,0.97], η>1.05, Σ>1
    SpatiotemporalGrid    - μ(k,z), η(k,z), Σ(k,z) with gate function
    ParameterScan         - (K_bar, λ_dot) robustness scan
    GrowthODE             - Linear growth δ(a) with modified μ
    Predictions           - P1 (cluster-scale) and P2 (no μ>1 in linear)
"""

from .regime_transition import (
    EFCRegimeTransition,
    StiffnessResponse,
    SurvivalValley,
    SpatiotemporalGrid,
    ParameterScan,
    GrowthODE,
    Predictions,
)

__all__ = [
    "EFCRegimeTransition",
    "StiffnessResponse",
    "SurvivalValley",
    "SpatiotemporalGrid",
    "ParameterScan",
    "GrowthODE",
    "Predictions",
]

__version__ = "1.0.0"
__doi__ = "10.6084/m9.figshare.31941543"
