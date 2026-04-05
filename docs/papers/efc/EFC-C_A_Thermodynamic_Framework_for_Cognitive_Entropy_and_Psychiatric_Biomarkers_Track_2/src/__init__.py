"""EFC-C: Cognitive Entropy and Psychiatric Biomarkers.

Thermodynamic framework extending EFC to neural systems. Models the
brain via entropy-gradient dynamics with three falsifiable predictions.

DOI: 10.6084/m9.figshare.31940505
"""
from .efc_cognition import (
    NeuralEntropyProduction, EntropyGradient, CentrifugalGradient,
    DisorderSignature, EntropyThreshold, FrameworkComparison,
    compute_s_dot_neural, compute_gradient_deviation,
)
__all__ = [
    "NeuralEntropyProduction", "EntropyGradient", "CentrifugalGradient",
    "DisorderSignature", "EntropyThreshold", "FrameworkComparison",
    "compute_s_dot_neural", "compute_gradient_deviation",
]
