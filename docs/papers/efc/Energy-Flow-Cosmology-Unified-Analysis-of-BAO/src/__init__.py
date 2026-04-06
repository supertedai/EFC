"""EFC Unified Analysis of BAO, SN Ia, and RSD.

Effective gravitational coupling mu(a), entropy field S(a),
chi-squared analysis, and regime-consistency results.

DOI: 10.6084/m9.figshare.31215613
"""
from .efc_unified_bao import (
    UnifiedAnalysisParameters, DataSource, ChiSquaredResult,
    UnifiedAnalysis, entropy_field, mu_eff, a_from_z,
    data_sources, lcdm_result, efc_result, delta_chi2,
    key_findings, total_data_points,
)

__all__ = [
    "UnifiedAnalysisParameters", "DataSource", "ChiSquaredResult",
    "UnifiedAnalysis", "entropy_field", "mu_eff", "a_from_z",
    "data_sources", "lcdm_result", "efc_result", "delta_chi2",
    "key_findings", "total_data_points",
]
