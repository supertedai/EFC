"""Sealed EFC pre-registered predictions.

The values below mirror ``data/parameters.json`` exactly. They are frozen
prior to the Euclid DR1, Rubin DP2, and Simons Observatory x Euclid data
releases. Any post-release re-tuning invalidates the pre-registration.
"""
from __future__ import annotations

from typing import Dict


FROZEN_PARAMETERS: Dict[str, float] = {
    "B0": 0.02,
    "M0": 0.06,
    "a_t": 0.30,
    "Delta": 0.20,
}

PREDICTED_SHIFTS_VS_LCDM_PERCENT: Dict[str, float] = {
    "sigma8": 1.2,
    "lensing": -6.0,
    "EG": -4.0,
}

# Acceptance windows (kill criteria are the complement).
VERDICT_WINDOWS: Dict[str, tuple[float, float]] = {
    "lensing_to_CMB_ratio": (0.90, 1.00),
    "eta": (1.06, 1.14),
}


def frozen_parameters() -> Dict[str, float]:
    """Return the sealed EFC benchmark parameters."""
    return dict(FROZEN_PARAMETERS)


def predicted_shifts() -> Dict[str, float]:
    """Return the predicted fractional shifts relative to LCDM (percent)."""
    return dict(PREDICTED_SHIFTS_VS_LCDM_PERCENT)


def verdict_window(name: str) -> tuple[float, float]:
    """Return the acceptance window for the named observable."""
    return VERDICT_WINDOWS[name]
