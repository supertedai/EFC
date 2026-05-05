"""EFC Master Specification -- canonical authoritative reference.

All fields, equations, parameters, regime architecture, consistency
rules, and cognitive/informational layers.
"""
from .efc_master_spec import (
    EFCCanonicalParameters, EFCMasterSpec, MasterRegime,
    ConsistencyRule, CognitiveLayer,
    entropy_sigmoid, mu, hubble_ratio_squared,
    master_regimes, consistency_rules,
)

__all__ = [
    "EFCCanonicalParameters", "EFCMasterSpec", "MasterRegime",
    "ConsistencyRule", "CognitiveLayer",
    "entropy_sigmoid", "mu", "hubble_ratio_squared",
    "master_regimes", "consistency_rules",
]
