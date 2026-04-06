"""
EFC Grid-Higgs Framework

Implements the Grid-Higgs model for mass emergence from
grid-level resistance, energy flow, and entropy gradients.

Reference:
    Magnusson, M. EFC -- Grid-Higgs Framework.
"""

from .grid_higgs import (
    GridResistance,
    EffectiveMass,
    GridHiggsModel,
)

__version__ = "1.0.0"
__all__ = [
    "GridResistance",
    "EffectiveMass",
    "GridHiggsModel",
]
