"""
EFC CMB Thermodynamic Interpretation
=====================================
Compatibility and null-test framework for CMB observables under
entropy-constrained structure formation in Energy-Flow Cosmology.

DOI: 10.6084/m9.figshare.31064929
Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)

Classes:
    EntropyProfile       - S(z) redshift-dependent entropy profile
    CompatibilityTest    - Tests CMB observables against EFC predictions
    NullTest             - Falsifiable null tests with thresholds
    PredictionZone       - A_L, ISW phase, lensing predictions
    JWSTExcess           - COSMOS-Web galaxy excess analysis
    CMBFramework         - Complete CMB compatibility framework
"""

from .cmb_thermodynamic import (
    EntropyProfile,
    CompatibilityTest,
    NullTest,
    PredictionZone,
    JWSTExcess,
    CMBFramework,
)

__all__ = [
    "EntropyProfile",
    "CompatibilityTest",
    "NullTest",
    "PredictionZone",
    "JWSTExcess",
    "CMBFramework",
]

__version__ = "1.0.0"
__doi__ = "10.6084/m9.figshare.31064929"
