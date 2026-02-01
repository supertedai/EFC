"""
H0-RAR Unification Package

Demonstrates that the Hubble tension and radial acceleration relation
arise from the same mechanism: entropy-driven gravity modification.

Key components:
- entropy_mapping: S(z) sigmoid function
- phase_calculator: Φ(S) computation
- h0_predictor: H₀ prediction from a_G
- mond_interpolation: MOND μ(x) functions
- unification: Complete analysis
"""

from .entropy_mapping import EntropyMapping, S_of_z
from .phase_calculator import PhaseCalculator, compute_delta_phi
from .h0_predictor import H0Predictor, predict_h0
from .mond_interpolation import mond_mu, compute_aG_from_mond
from .unification import UnificationAnalysis, run_full_analysis

__version__ = "1.0.0"
__author__ = "Morten Magnusson"
__doi__ = "10.6084/m9.figshare.31223908"

__all__ = [
    "EntropyMapping",
    "S_of_z",
    "PhaseCalculator",
    "compute_delta_phi",
    "H0Predictor",
    "predict_h0",
    "mond_mu",
    "compute_aG_from_mond",
    "UnificationAnalysis",
    "run_full_analysis",
]
