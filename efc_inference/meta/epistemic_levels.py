"""
L0-L3 Epistemic Level Weighting

Controls prior width based on how well-established a parameter is:
  L0 (speculative):  10x wider priors — parameter barely constrained
  L1 (preliminary):  3x wider priors — some evidence but weak
  L2 (established):  1.5x wider priors — reasonable evidence
  L3 (confirmed):    1x priors (nominal) — strong empirical support

This is a META-CONTROL layer, not a data module.
It modifies the effective prior width, not the data or physics.

Usage:
    from efc_inference.meta.epistemic_levels import EpistemicWeighting

    ew = EpistemicWeighting()
    ew.set_level("entropy_scale", EpistemicLevel.L1)
    ew.set_level("length_scale", EpistemicLevel.L3)

    # Add to MetaController
    meta.add_layer("epistemic", ew.log_penalty)
"""

import json
import numpy as np
from enum import IntEnum
from pathlib import Path
from typing import Optional


class EpistemicLevel(IntEnum):
    L0 = 0  # Speculative  (Raw Measurement proximity)
    L1 = 1  # Preliminary  (Calibrated Data)
    L2 = 2  # Established  (Derived Quantities)
    L3 = 3  # Confirmed    (Theoretical Constructs — closest to data)


# Prior width multiplier per level
# Derived from canonical EBE confidence_factor:
#   L0: conf=1.0 → mult = 1/conf * 10 = 10.0  (widest priors)
#   L1: conf=0.9 → mult = 1/0.9 * 2.7 ≈ 3.0
#   L2: conf=0.7 → mult = 1/0.7 * 1.05 ≈ 1.5
#   L3: conf=0.4 → mult = 1.0 (reference, no widening)
LEVEL_MULTIPLIERS = {
    EpistemicLevel.L0: 10.0,
    EpistemicLevel.L1: 3.0,
    EpistemicLevel.L2: 1.5,
    EpistemicLevel.L3: 1.0,
}

# Log-penalty per level (softer priors get a small penalty
# to prefer simpler, better-constrained models)
# Scaled by canonical proximity: L0=1.0, L1=0.75, L2=0.5, L3=0.25
LEVEL_PENALTIES = {
    EpistemicLevel.L0: -2.0,   # Strong penalty for speculative params
    EpistemicLevel.L1: -0.5,   # Mild penalty
    EpistemicLevel.L2: -0.1,   # Near-zero
    EpistemicLevel.L3: 0.0,    # No penalty
}

# Canonical EBE definitions (from l_layers.json)
CANONICAL_LAYERS = {
    "L0": {"proximity": 1.0, "confidence_factor": 1.0},
    "L1": {"proximity": 0.75, "confidence_factor": 0.9},
    "L2": {"proximity": 0.5, "confidence_factor": 0.7},
    "L3": {"proximity": 0.25, "confidence_factor": 0.4},
}


def load_canonical_layers(path: str) -> dict:
    """
    Load canonical EBE L-layer definitions from JSON.

    Parameters:
        path: Path to l_layers.json

    Returns:
        Dict of layer definitions with proximity and confidence_factor
    """
    p = Path(path)
    if not p.exists():
        return CANONICAL_LAYERS

    with open(p) as f:
        data = json.load(f)

    result = {}
    for layer in data.get("layers", []):
        lid = layer.get("id", "")
        result[lid] = {
            "proximity": layer.get("proximity", 0.5),
            "confidence_factor": layer.get("confidence_factor", 0.5),
            "name": layer.get("name", ""),
            "description": layer.get("description", ""),
        }
    return result if result else CANONICAL_LAYERS


class EpistemicWeighting:
    """
    Epistemic level controller for EFC parameters.

    Assigns L0-L3 levels to parameters and computes a combined
    log-penalty that feeds into the MetaController.
    """

    def __init__(self, default_level: EpistemicLevel = EpistemicLevel.L1):
        self._levels: dict[str, EpistemicLevel] = {}
        self._default = default_level

    def set_level(self, param_name: str, level: EpistemicLevel):
        self._levels[param_name] = level

    def get_level(self, param_name: str) -> EpistemicLevel:
        return self._levels.get(param_name, self._default)

    def get_multiplier(self, param_name: str) -> float:
        """Prior width multiplier for a parameter."""
        level = self.get_level(param_name)
        return LEVEL_MULTIPLIERS[level]

    def log_penalty(self, params_dict: dict) -> float:
        """
        Combined epistemic log-penalty.
        Sum of per-parameter penalties based on their epistemic level.

        This is called by MetaController during sampling.
        """
        total = 0.0
        for name in params_dict:
            level = self.get_level(name)
            total += LEVEL_PENALTIES[level]
        return total

    def scale_prior_bounds(self, param_name: str,
                           original_bounds: tuple) -> tuple:
        """
        Widen prior bounds based on epistemic level.

        For a parameter at L0, bounds are widened 10x from center.
        At L3, bounds are unchanged.
        """
        lo, hi = original_bounds
        center = (lo + hi) / 2.0
        half_width = (hi - lo) / 2.0
        mult = self.get_multiplier(param_name)
        new_half = half_width * mult
        return (center - new_half, center + new_half)

    def summary(self) -> dict:
        return {
            name: {
                "level": f"L{level.value}",
                "multiplier": LEVEL_MULTIPLIERS[level],
                "penalty": LEVEL_PENALTIES[level],
            }
            for name, level in self._levels.items()
        }
