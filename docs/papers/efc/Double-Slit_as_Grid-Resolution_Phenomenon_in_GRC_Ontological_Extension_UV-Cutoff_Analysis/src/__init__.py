"""
GRC Double-Slit — Reference Implementation
Working Note v0.2, March 8, 2026
"""
from .grc_double_slit import (
    GRCAxioms, EntropyClarity, UVCutoffModel,
    PredictionStatus, OpenGaps,
    PREDICTIONS, FALSIFICATION_POINTS, OPEN_GAPS, G2_CANDIDATES,
)

__all__ = [
    "GRCAxioms", "EntropyClarity", "UVCutoffModel",
    "PredictionStatus", "OpenGaps",
    "PREDICTIONS", "FALSIFICATION_POINTS", "OPEN_GAPS", "G2_CANDIDATES",
]
