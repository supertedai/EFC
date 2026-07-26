"""
Regime Boundary Controller (RBC) — STUB

Controls which physics regime is active based on the alpha parameter:
    S1 (alpha -> 1): Free resonance, energy flow dominates
    S0 (alpha -> 0): Frozen structure, phase-locked

The RBC ensures smooth transitions between regimes and penalizes
parameter combinations that are inconsistent with the active regime.

Physics (to be implemented by Morten):
    alpha(L) = E_flow / E_total
    - At galactic scales: alpha ~ 0.3-0.7 (mixed regime)
    - At cosmological scales: alpha ~ 0.8-1.0 (flow-dominated)
    - At planetary scales: alpha ~ 0.01-0.1 (structure-dominated)

    The RBC penalty ensures that parameters are consistent with
    the scale being modeled.

This is a META-CONTROL layer — it doesn't compute physics,
it controls which physics regime is valid for the current parameters.

Usage:
    rbc = RBCRegime(scale="galactic")
    meta.add_layer("rbc", rbc.log_penalty)
"""

import json
import numpy as np
from pathlib import Path


# Canonical EBE S-regime definitions (from s_regimes.json)
CANONICAL_REGIMES = {
    "low_s": {"entropy_range": [0.0, 0.3], "predictability": "high"},
    "mid_s": {"entropy_range": [0.3, 0.7], "predictability": "medium"},
    "high_s": {"entropy_range": [0.7, 1.0], "predictability": "low"},
}


def load_canonical_regimes(path: str) -> dict:
    """
    Load canonical EBE S-regime definitions from JSON.

    Parameters:
        path: Path to s_regimes.json

    Returns:
        Dict of regime definitions with entropy_range and characteristics
    """
    p = Path(path)
    if not p.exists():
        return CANONICAL_REGIMES

    with open(p) as f:
        data = json.load(f)

    result = {}
    for regime in data.get("regimes", []):
        rid = regime.get("id", "")
        result[rid] = {
            "entropy_range": regime.get("entropy_range", [0.0, 1.0]),
            "predictability": regime.get("characteristics", {}).get(
                "predictability", "unknown"
            ),
            "name": regime.get("name", ""),
            "typical_systems": regime.get("typical_systems", []),
        }
    return result if result else CANONICAL_REGIMES


class RBCRegime:
    """
    Regime Boundary Controller.

    STATUS: STUB — returns 0.0 (no regime constraint).
    Morten: implement compute_alpha() and regime penalty.
    """

    # Known scale regimes with expected alpha ranges
    REGIMES = {
        "planetary": (0.001, 0.15),
        "stellar": (0.05, 0.3),
        "galactic": (0.2, 0.8),
        "cluster": (0.5, 0.95),
        "cosmological": (0.7, 1.0),
    }

    def __init__(self, scale: str = "galactic"):
        if scale not in self.REGIMES:
            raise ValueError(f"Unknown scale '{scale}'. "
                             f"Known: {list(self.REGIMES.keys())}")
        self.scale = scale
        self.alpha_range = self.REGIMES[scale]
        self.enabled = True

    def log_penalty(self, params_dict: dict) -> float:
        """
        Penalize parameters inconsistent with the active regime.

        Returns:
            0.0 if alpha is within expected range (or stub mode)
            Negative penalty if alpha is outside expected range

        Morten: implement compute_alpha() to calculate alpha
        from the current parameter values.
        """
        if not self.enabled:
            return 0.0

        # STUB: No alpha computation implemented yet
        # Morten: replace this with actual EFC alpha calculation
        #
        # Example implementation:
        # alpha = self.compute_alpha(params_dict)
        # lo, hi = self.alpha_range
        # if alpha < lo:
        #     return -50.0 * (lo - alpha)**2  # Soft penalty
        # if alpha > hi:
        #     return -50.0 * (alpha - hi)**2
        # return 0.0

        return 0.0

    def compute_alpha(self, params_dict: dict) -> float:
        """
        Compute alpha = E_flow / E_total from current parameters.

        Morten: implement this.
        Must return a value in [0, 1].
        """
        raise NotImplementedError(
            "RBCRegime.compute_alpha() is a stub.\n"
            "Morten: implement alpha(L) = E_flow / E_total here.\n"
            "Input: params_dict with relevant EFC parameters\n"
            "Output: alpha value in [0, 1]"
        )

    def regime_report(self, params_dict: dict) -> dict:
        """Diagnostic report (not used during sampling)."""
        return {
            "scale": self.scale,
            "expected_alpha_range": self.alpha_range,
            "status": "stub — alpha not computed",
        }
