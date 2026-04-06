"""EFC v2.2 Cross-Field Integration Summary -- coupling and integration.

Field coupling mechanisms, multi-level integration hierarchy, and
cross-field consistency checks.
"""
from .efc_cross_field import (
    FieldCoupling, IntegrationLevel, CouplingMatrix,
    CrossFieldIntegration, canonical_couplings, integration_levels,
    entropy_energy_consistency, FIELD_NAMES,
)

__all__ = [
    "FieldCoupling", "IntegrationLevel", "CouplingMatrix",
    "CrossFieldIntegration", "canonical_couplings", "integration_levels",
    "entropy_energy_consistency", "FIELD_NAMES",
]
