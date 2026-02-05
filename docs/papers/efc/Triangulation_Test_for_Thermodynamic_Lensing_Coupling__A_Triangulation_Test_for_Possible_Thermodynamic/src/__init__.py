"""
Triangulation Test for Thermodynamic-Lensing Coupling

A methodology to test whether gravitational lensing in galaxy clusters
exhibits residual structure correlated with ICM thermodynamics.
"""

from .triangulation_test import (
    TriangulationAnalysis,
    ClusterData,
    run_triangulation_test,
    stacked_detection_threshold
)

__all__ = [
    'TriangulationAnalysis',
    'ClusterData',
    'run_triangulation_test',
    'stacked_detection_threshold'
]
