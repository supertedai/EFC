"""
COSMOS-Web Galaxy Abundances Module
=====================================
Analysis of observed galaxy abundances at z > 6 exceeding
halo-limited predictions in COSMOS-Web JWST data.

Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
Affiliation: Symbiose Research, Sandnes, Norway
License: CC-BY-4.0
"""

from .cosmos_abundances import (
    GalaxySample,
    HaloMassFunction,
    AbundanceExcess,
    RedshiftBin,
)

__version__ = "1.0.0"
__author__ = "Morten Magnusson"
__all__ = [
    "GalaxySample",
    "HaloMassFunction",
    "AbundanceExcess",
    "RedshiftBin",
]
