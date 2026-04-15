"""EFC Effective Horndeski Reduction reference implementation.

Exposes the closed-form expressions for the effective Bellini-Sawicki
alpha-functions derived in the paper. The full Boltzmann integration lives
in the companion ``hi_class`` pipeline referenced by DOI 31876324.
"""
from .alpha_functions import (
    alpha_M,
    alpha_B,
    alpha_K,
    alpha_T,
    stiffness_response,
)

__all__ = [
    "alpha_M",
    "alpha_B",
    "alpha_K",
    "alpha_T",
    "stiffness_response",
]
