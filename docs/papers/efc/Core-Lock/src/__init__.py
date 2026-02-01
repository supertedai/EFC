"""
EBE Core Lock - Python Implementation

Mathematical engine for Entropy-Bounded Empiricism.
Implements the grid state function, beta constraint, and projection laws.

Reference:
    Magnusson, M. (2026). EBE Core Lock v1.0: The S-Dynamic Foundation.
    DOI: 10.6084/m9.figshare.31223503
"""

from .grid_state_function import GridStateFunction
from .beta_constraint import BetaConstraint, verify_constraint
from .information_length import InformationLength, compute_length
from .projection_laws import ProjectionLaw, project_observable
from .simulation import CoreLockSimulation, run_verification

__version__ = "1.0.0"
__all__ = [
    "GridStateFunction",
    "BetaConstraint",
    "verify_constraint",
    "InformationLength",
    "compute_length",
    "ProjectionLaw",
    "project_observable",
    "CoreLockSimulation",
    "run_verification",
]
