"""Centrifugal Entropy Score (kappa) — Connectome functional variability gradients.

Quantifies the hub-to-periphery functional variability gradient using
kappa = <S_hub> / <S_periph> and identifies local degree heterogeneity
as its primary structural driver (r = -0.97, 94% variance explained).

DOI: 10.6084/m9.figshare.31940370
"""

from .connectome_kappa import (
    CentrifugalEntropyScore,
    ConnectomeAnalysis,
    NetworkFeatures,
    ThresholdSensitivity,
    BiomarkerPredictions,
    compute_kappa,
    compute_fc_cv,
    compute_structural_log_degree,
    compute_degree_ratio,
)

__all__ = [
    "CentrifugalEntropyScore",
    "ConnectomeAnalysis",
    "NetworkFeatures",
    "ThresholdSensitivity",
    "BiomarkerPredictions",
    "compute_kappa",
    "compute_fc_cv",
    "compute_structural_log_degree",
    "compute_degree_ratio",
]
