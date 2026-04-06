"""
AUTH Layer -- Origin, Provenance, and Structural Signature of Energy-Flow Cosmology

Provenance chain verification and structural signature analysis for EFC.
"""

from .auth_layer import (
    AUTHLayer,
    ProvenanceChain,
    ProvenanceRecord,
    StructuralSignature,
    InsightTransition,
    LayerType,
    TransitionState,
)

__all__ = [
    "AUTHLayer",
    "ProvenanceChain",
    "ProvenanceRecord",
    "StructuralSignature",
    "InsightTransition",
    "LayerType",
    "TransitionState",
]

__version__ = "1.0.0"
