"""
Structural Coherence Evaluation (SCE) Framework

Theory-agnostic evaluation of structural coherence and falsifiability.
"""

from .structural_coherence import (
    SCEFramework,
    TheoryProfile,
    ForbiddenPattern,
    PAPER_RESULTS,
)

__all__ = ['SCEFramework', 'TheoryProfile', 'ForbiddenPattern', 'PAPER_RESULTS']
__version__ = '1.0.0'
