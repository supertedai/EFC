"""
EFC Flow, Entropy, and Spacetime Distortion in Cosmological Clusters

Implements cluster-scale spacetime distortion from energy flow
and entropy gradients within the EFC framework.

Reference:
    Magnusson, M. EFC -- Flow, Entropy, and Spacetime Distortion
    in Cosmological Clusters.
"""

from .cluster_distortion import (
    ClusterDistortion,
    EnergyFlowField,
    EntropyGradient,
    LensingProfile,
)

__version__ = "1.0.0"
__all__ = [
    "ClusterDistortion",
    "EnergyFlowField",
    "EntropyGradient",
    "LensingProfile",
]
