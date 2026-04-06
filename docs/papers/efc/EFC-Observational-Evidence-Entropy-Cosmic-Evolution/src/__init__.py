"""EFC Observational Evidence for Entropy in Cosmic Evolution -- parameter and concept access module."""

from .observational_evidence import (
    CMBObservable,
    StructureFormationMetric,
    GalaxyRotationCurve,
    ObservationalEvidenceModel,
    BOLTZMANN_K,
    CMB_TEMPERATURE,
    CMB_ANISOTROPY,
    HUBBLE_H0,
)

__all__ = [
    "CMBObservable",
    "StructureFormationMetric",
    "GalaxyRotationCurve",
    "ObservationalEvidenceModel",
    "BOLTZMANN_K",
    "CMB_TEMPERATURE",
    "CMB_ANISOTROPY",
    "HUBBLE_H0",
]

__version__ = "1.0.0"
