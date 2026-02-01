"""
EFC Closure Conjectures

Proposed relations: g† = cH₀/e and C = 2e - 1
"""

from .closure_relations import (
    compute_g_dagger,
    compute_C,
    predict_h0,
    compute_k,
    ClosureConjectures,
    ClosureResult,
)

__all__ = [
    "compute_g_dagger",
    "compute_C",
    "predict_h0",
    "compute_k",
    "ClosureConjectures",
    "ClosureResult",
]

__version__ = "1.0.0"
