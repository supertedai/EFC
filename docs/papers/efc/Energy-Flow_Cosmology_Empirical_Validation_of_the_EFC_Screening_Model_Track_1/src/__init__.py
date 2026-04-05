"""EFC Screening Model — Multi-scale empirical validation.

Implements the EFC screening form ln(mu) = k*ln(1 + g†/g_bar) and
cross-scale consistency tests (SPARC RAR, KiDS-1000, H0 tension).

DOI: 10.6084/m9.figshare.31940469
"""
from .efc_screening import (
    EFCScreening, CrossScaleConsistency, KiDS1000Analysis,
    BulletClusterInterpretation, HubbleTension, ClosureConjecture,
    compute_mu, compute_phase_gain, compute_a_G,
)
__all__ = [
    "EFCScreening", "CrossScaleConsistency", "KiDS1000Analysis",
    "BulletClusterInterpretation", "HubbleTension", "ClosureConjecture",
    "compute_mu", "compute_phase_gain", "compute_a_G",
]
