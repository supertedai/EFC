"""
EFC Ontological Foundations - Python Implementation

Tools for analyzing the co-primary structure and testing
for circularity in ontological hypotheses.

Reference:
    Magnusson, M. (2026). EFC Ontological Foundations v1.0:
    The Co-Primary Structure.
"""

from .circularity_tester import CircularityTester, test_definition
from .hypothesis_analyzer import HypothesisAnalyzer, AnalysisResult
from .ontology_model import CoPrimaryModel, Differentiation
from .phase_classifier import PhaseClassifier, Phase

__version__ = "1.0.0"
__all__ = [
    "CircularityTester",
    "test_definition",
    "HypothesisAnalyzer",
    "AnalysisResult",
    "CoPrimaryModel",
    "Differentiation",
    "PhaseClassifier",
    "Phase",
]
