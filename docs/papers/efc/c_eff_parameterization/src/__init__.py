"""
EFC c_eff Parameterization
============================
Effective speed of sound parameterization c_eff(a) = c_0[1 + epsilon*beta*T(a)]
within Energy-Flow Cosmology.

DOI: 10.6084/m9.figshare.31305421
Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)

Classes:
    TransitionFunction     - T(a) EFC transition function
    CEffParameterization   - c_eff(a) = c_0[1 + epsilon*beta*T(a)]
    DistanceModification   - Modified comoving and luminosity distances
    CDDRTest               - Cosmic Distance Duality Relation analysis
    DegeneracyBreaker      - Four degeneracy-breaking tests
    FalsificationCriteria  - Six falsification criteria
"""

from .c_eff import (
    TransitionFunction,
    CEffParameterization,
    DistanceModification,
    CDDRTest,
    DegeneracyBreaker,
    FalsificationCriteria,
)

__all__ = [
    "TransitionFunction",
    "CEffParameterization",
    "DistanceModification",
    "CDDRTest",
    "DegeneracyBreaker",
    "FalsificationCriteria",
]

__version__ = "3.0.0"
__doi__ = "10.6084/m9.figshare.31305421"
