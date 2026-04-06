"""EFC validation module: rotation curve validation and SPARC comparison."""

from .efc_validation import (
    load_parameters,
    rotation_curve_efc,
    validate_rotation_curve,
    compare_with_sparc,
)

__all__ = [
    "load_parameters",
    "rotation_curve_efc",
    "validate_rotation_curve",
    "compare_with_sparc",
]
