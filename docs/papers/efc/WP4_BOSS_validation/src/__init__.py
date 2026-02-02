"""
EFC BOSS DR12 Transfer Test Implementation

Cross-survey validation of Energy-Flow Cosmology using BOSS DR12 BAO data.
"""

from .efc_boss_transfer import EFCTransferTest, BOSSData, CovarianceDiagnostics

__all__ = ['EFCTransferTest', 'BOSSData', 'CovarianceDiagnostics']
__version__ = '1.0.0'
