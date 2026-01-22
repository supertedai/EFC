"""
Validity-Aware AI

An Entropy-Bounded Architecture for Regime-Sensitive Inference.

This package provides tools for implementing regime-aware inference in RAG systems,
enabling AI systems to recognize and report their own epistemic limits.

DOI: 10.6084/m9.figshare.31122970
Author: Morten Magnusson
License: CC BY 4.0
"""

from .regime_classifier import Regime, RegimeClassifier, classify_regime
from .entropy_measures import (
    compute_edge_entropy,
    compute_node_entropy,
    compute_structural_entropy,
    compute_retrieval_entropy,
    compute_total_entropy
)
from .response_protocols import (
    ResponseProtocol,
    ProtocolEngine,
    get_protocol,
    PROTOCOL_L1,
    PROTOCOL_L2,
    PROTOCOL_L3
)
from .ebe_filter import EBEFilter, create_ebe_filter, EntropyResult, RegimeResult

__version__ = "1.0.0"
__author__ = "Morten Magnusson"
__doi__ = "10.6084/m9.figshare.31122970"

__all__ = [
    # Regime classification
    "Regime",
    "RegimeClassifier",
    "classify_regime",
    
    # Entropy measures
    "compute_edge_entropy",
    "compute_node_entropy",
    "compute_structural_entropy",
    "compute_retrieval_entropy",
    "compute_total_entropy",
    
    # Protocols
    "ResponseProtocol",
    "ProtocolEngine",
    "get_protocol",
    "PROTOCOL_L1",
    "PROTOCOL_L2",
    "PROTOCOL_L3",
    
    # Main filter
    "EBEFilter",
    "create_ebe_filter",
    "EntropyResult",
    "RegimeResult",
]
