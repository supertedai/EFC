"""
EFC Weak Lensing Phenomenology

A testable μ(k,z) framework for Energy-Flow Cosmology weak lensing predictions.

DOI: 10.6084/m9.figshare.31188193
Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
License: CC BY 4.0
"""

from .efc_weak_lensing import (
    EFCParams,
    mu_efc,
    sigma_lens_efc,
    eta_efc,
    growth_modification,
)

__version__ = "1.0.0"
__author__ = "Morten Magnusson"
__doi__ = "10.6084/m9.figshare.31188193"

__all__ = [
    "EFCParams",
    "mu_efc",
    "sigma_lens_efc", 
    "eta_efc",
    "growth_modification",
]
