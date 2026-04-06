"""
Entropy-Bounded Empiricism (EBE) - SPARC175 Analysis Module.

Provides classes for regime classification, entropy computation,
and statistical validation of galaxy rotation curves.

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
License: CC-BY-4.0
"""

from .ebe_sparc175 import (
    EntropyBoundedEmpiricism,
    RegimeClassifier,
    Galaxy,
)

__all__ = [
    "EntropyBoundedEmpiricism",
    "RegimeClassifier",
    "Galaxy",
]
