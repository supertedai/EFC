"""
EFC Background No-Go Theorem
=============================

Analytical proof, numerical verification, and observational confirmation that
the EFC background coupling channel (β·T(a) modification to Friedmann equation)
cannot suppress σ₈ and is observationally empty.

Exports
-------
BackgroundNoGo : class
    Sign lemma verification and growth enhancement computation.

Version: 1.0
DOI: 10.6084/m9.figshare.31985163
License: CC-BY-4.0
"""

from .background_nogo import BackgroundNoGo

__version__ = "1.0"
__author__ = "Morten Magnusson"
__all__ = ["BackgroundNoGo"]
