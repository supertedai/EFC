"""
EFC ISW Cross-Correlation Predictions with DESI DR1 Tracers

Computes ISW-galaxy angular power spectra and cancellation metric.
"""

from .isw_cross_correlation import ISWCrossCorrelation, ISWKernel, PAPER_RESULTS

__all__ = ['ISWCrossCorrelation', 'ISWKernel', 'PAPER_RESULTS']
__version__ = '1.0.0'
