"""
EFC Phenomenology vs DESI DR2 BAO: A Comparative Fit Analysis

EFC-inspired w(z) parameterization and chi-squared comparison against DESI DR2 BAO.
"""

from .efc_desi_bao import (
    DESIComparison,
    EFCParameters,
    LCDMParameters,
    CPLParameters,
    BAODataPoint,
    FitResult,
    DESI_DR2_BAO,
)

__all__ = [
    "DESIComparison",
    "EFCParameters",
    "LCDMParameters",
    "CPLParameters",
    "BAODataPoint",
    "FitResult",
    "DESI_DR2_BAO",
]

__version__ = "1.0.0"
