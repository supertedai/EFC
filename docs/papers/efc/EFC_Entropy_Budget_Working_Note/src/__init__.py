"""
EFC Entropy Budget Working Note — AI-Friendly Source Package
DOI: 10.6084/m9.figshare.31942734

Cosmic entropy budget as constraint on the EFC S-field.
SMBH-dominated entropy (~10^104 k_B) maps to S=S_max (grid collapse).
"""

from .entropy_budget import (
    CosmicEntropyInventory,
    BekensteinHawkingEntropy,
    GRCTriadMapping,
    SFieldNormalization,
    ThermostatConjecture,
    Predictions,
)

__all__ = [
    "CosmicEntropyInventory",
    "BekensteinHawkingEntropy",
    "GRCTriadMapping",
    "SFieldNormalization",
    "ThermostatConjecture",
    "Predictions",
]
