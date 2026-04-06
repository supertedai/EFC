"""
Regime Consistency of EFC Coupling T(z) across Lya, BAO, and RSD

Three-regime consistency test evaluated using the SCE framework.
"""

from .regime_consistency import RegimeConsistencyTest, TransitionFunction, SCEEvaluation, PAPER_RESULTS

__all__ = ['RegimeConsistencyTest', 'TransitionFunction', 'SCEEvaluation', 'PAPER_RESULTS']
__version__ = '1.0.0'
