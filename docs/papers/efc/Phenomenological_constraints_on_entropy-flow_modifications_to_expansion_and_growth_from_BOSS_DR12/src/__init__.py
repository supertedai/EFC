"""
EFC Phenomenological Constraints Module

Single-parameter extension of ΛCDM where entropy-gradient couplings
modify both background expansion and linear growth rate.

Key result: α_L2 = 0.34 ± 0.16 (1σ) from BOSS DR12
"""

from .efc_phenomenology import EFCPhenomenology

__all__ = ['EFCPhenomenology']
__version__ = '1.0.0'
