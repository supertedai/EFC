"""
EFC CMB Localization Study — Reference Implementation
DOI: 10.6084/m9.figshare.31368433
"""
from .cmb_localization import (
    BackgroundGate,
    MuSigmaValley,
    ALDegeneracy,
    GrowthSignTest,
    SurvivingSignalSpec,
)

__all__ = [
    "BackgroundGate",
    "MuSigmaValley",
    "ALDegeneracy",
    "GrowthSignTest",
    "SurvivingSignalSpec",
]
