"""
EFC Relativistic Action: Field Equations, Perturbation Theory, and Extraction of mu, Sigma, eta.
Reference implementation for the paper by Morten Magnusson (2026).
"""

from .efc_relativistic import (
    EFCAction,
    KineticStiffness,
    EntropyProduction,
    EFCPerturbations,
    TensorSector,
    FalsificationCondition,
    compute_mu,
    compute_eta,
    compute_sigma,
    compute_stiffness_response,
    run_perturbation_demo,
)

__all__ = [
    "EFCAction",
    "KineticStiffness",
    "EntropyProduction",
    "EFCPerturbations",
    "TensorSector",
    "FalsificationCondition",
    "compute_mu",
    "compute_eta",
    "compute_sigma",
    "compute_stiffness_response",
    "run_perturbation_demo",
]
