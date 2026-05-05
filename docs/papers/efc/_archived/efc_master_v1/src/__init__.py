"""EFC Master Specification v1 (Archive) -- earliest complete formulation.

Initial field definitions, entropy sigmoid, regime architecture,
and thermodynamic foundations. Archived for reproducibility.
"""
from .efc_master_v1_spec import (
    V1Parameters, V1Regime, V1FieldDefinition, VersionComparison,
    EFCMasterV1, v1_entropy, v1_mu, v1_regimes, v1_fields,
)

__all__ = [
    "V1Parameters", "V1Regime", "V1FieldDefinition", "VersionComparison",
    "EFCMasterV1", "v1_entropy", "v1_mu", "v1_regimes", "v1_fields",
]
