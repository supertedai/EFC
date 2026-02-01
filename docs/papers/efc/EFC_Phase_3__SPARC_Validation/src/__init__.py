"""
EFC Phase 3: SPARC Validation

Empirical test of EFC against the radial acceleration relation.

Key result: k = 0.415 ± 0.029, C = k/a_G = 4.4 ± 0.6
"""

from .screening_model import (
    EFCScreening,
    ScreeningResult,
    create_canonical_model,
)

__all__ = [
    "EFCScreening",
    "ScreeningResult",
    "create_canonical_model",
]

__version__ = "1.0.0"
