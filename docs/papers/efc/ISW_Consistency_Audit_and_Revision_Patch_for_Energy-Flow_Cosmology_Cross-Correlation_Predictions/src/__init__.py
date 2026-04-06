"""
ISW Revision Patch

Reference implementation for revised ISW cross-correlation predictions
following the ISW Consistency Audit v1.1.

Paper: "ISW Paper Revision Patch: Proposed Corrections to ISW Cross-Correlation
       Predictions for EFC with DESI DR1 Tracers"
DOI: 10.6084/m9.figshare.31329082
"""

from .isw_revision import (
    ISWChannel,
    MuParameters,
    TracerPrediction,
    RevisedISWPredictions,
    ChannelComparison,
    FalsificationCriteria,
    ValidationLedgerUpdate,
    get_revised_prediction,
    get_all_predictions,
    check_falsification,
)

__all__ = [
    "ISWChannel",
    "MuParameters",
    "TracerPrediction",
    "RevisedISWPredictions",
    "ChannelComparison",
    "FalsificationCriteria",
    "ValidationLedgerUpdate",
    "get_revised_prediction",
    "get_all_predictions",
    "check_falsification",
]

__version__ = "1.0.0"
__doi__ = "10.6084/m9.figshare.31329082"
