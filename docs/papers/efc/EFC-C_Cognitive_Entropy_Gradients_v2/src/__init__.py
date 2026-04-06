"""
EFC-C v2.0: Cognitive Entropy Gradients
=========================================
Quantitative entropy-gradient predictions for cognitive states
using connectome-constrained Bridge B1* equation.

Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)

Classes:
    CentrifugalEntropyScore  - kappa = <S_hub> / <S_periph>
    BridgeB1Star             - kappa = C / (1 + lambda_2 * tau_c)
    ConnectomeParameters     - Fiedler eigenvalue and hub classification
    DisorderPrediction       - Disorder-specific kappa and alpha_AP shifts
    CognitiveCoherenceThreshold - kappa_crit = 0.73
    EFCC_Framework           - Complete EFC-C v2 prediction framework
"""

from .cognitive_entropy import (
    CentrifugalEntropyScore,
    BridgeB1Star,
    ConnectomeParameters,
    DisorderPrediction,
    CognitiveCoherenceThreshold,
    EFCC_Framework,
)

__all__ = [
    "CentrifugalEntropyScore",
    "BridgeB1Star",
    "ConnectomeParameters",
    "DisorderPrediction",
    "CognitiveCoherenceThreshold",
    "EFCC_Framework",
]

__version__ = "2.0.0"
