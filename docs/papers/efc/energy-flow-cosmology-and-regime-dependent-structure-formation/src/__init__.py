"""
EFC Regime-Dependent Structure Formation Module
=================================================
Core classes for energy decomposition, regime classification,
cross-scale correspondence, and structure formation analysis.

Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
Affiliation: Symbiose Research, Sandnes, Norway
License: CC-BY-4.0
"""

from .regime_structure import (
    EnergyDecomposition,
    RegimeStructure,
    CrossScaleCorrespondence,
    StructureFormationRate,
)

__version__ = "1.0.0"
__author__ = "Morten Magnusson"
__all__ = [
    "EnergyDecomposition",
    "RegimeStructure",
    "CrossScaleCorrespondence",
    "StructureFormationRate",
]
