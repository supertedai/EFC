"""
EFC Cosmic Dipole Working Note
===============================
Regime-dependent anisotropy: entropy gradient ∇S produces intrinsic dipole.

DOI: 10.6084/m9.figshare.31942731
Author: Morten Magnusson

Classes:
    KinematicDipole     - Standard kinematic dipole D_kin ≈ 2v/c
    EntropyGradient     - Large-scale ∇S mechanism
    DipoleAmplitude     - D_EFC from entropy gradient (Eq. 4)
    DipoleExcess        - Comparison with observations
    RegimeDependentIsotropy - Isotropy as regime condition
    Predictions         - P1-P4 and open gaps G1-G4
"""

from .cosmic_dipole import (
    KinematicDipole,
    EntropyGradient,
    DipoleAmplitude,
    DipoleExcess,
    RegimeDependentIsotropy,
    Predictions,
)

__all__ = [
    "KinematicDipole",
    "EntropyGradient",
    "DipoleAmplitude",
    "DipoleExcess",
    "RegimeDependentIsotropy",
    "Predictions",
]

__version__ = "0.1.0"
__doi__ = "10.6084/m9.figshare.31942731"
