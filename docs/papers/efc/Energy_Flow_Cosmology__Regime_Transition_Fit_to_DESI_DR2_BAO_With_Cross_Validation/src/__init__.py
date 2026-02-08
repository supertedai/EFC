"""
EFC Regime-Transition Model for DESI DR2 BAO

Implements the EFC modification to the Friedmann equation:
    E²(z) → E²(z) × [1 + α_L2 × f(z) × Θ(z)]
"""

from .efc_model import (
    EFCTransition,
    ModelResult,
    create_best_fit_model,
    create_LCDM_model,
)

__all__ = [
    "EFCTransition",
    "ModelResult",
    "create_best_fit_model",
    "create_LCDM_model",
]

__version__ = "1.0.0"
