"""
EFC-C v2.1: Cognitive Entropy Gradients
========================================

Bridge B1** (degree-heterogeneity): kappa = C_eff * D_ratio**gamma

DOI: 10.6084/m9.figshare.32091700 (v2)
Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)

Classes:
    CentrifugalEntropyScore  - kappa = <S_hub>/<S_periph>
    DegreeRatio              - D_ratio = <k_hub>/<k_periph>
    BridgeB1DoubleStar       - kappa = C_eff * D_ratio^gamma
    LayerAPredictions        - A1 (slope), A2 (SCZ asymmetry), A3 (MDD asymmetry)
    LayerBPredictions        - B1 (kappa interval), B2 (critical threshold)
    EFCC_v21_Framework       - Complete v2.1 framework
"""

from .cognitive_entropy import (
    CentrifugalEntropyScore,
    DegreeRatio,
    BridgeB1DoubleStar,
    LayerAPredictions,
    LayerBPredictions,
    EFCC_v21_Framework,
)

__all__ = [
    "CentrifugalEntropyScore",
    "DegreeRatio",
    "BridgeB1DoubleStar",
    "LayerAPredictions",
    "LayerBPredictions",
    "EFCC_v21_Framework",
]

__version__ = "2.1.0"
