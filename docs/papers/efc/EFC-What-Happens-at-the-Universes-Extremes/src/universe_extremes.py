"""
EFC -- What Happens at the Universe's Extremes?
=================================================
Models the behaviour near entropic boundaries S->0 (maximal order)
and S->1 (maximal disorder), including structure stability, energy
propagation limits, and information collapse.

Key concepts:
  S -> 0 : crystalline order, frozen flow, maximal structure
  S -> 1 : heat death, maximal disorder, information loss
  Critical thresholds: S_crit_low, S_crit_high

Author : Morten Magnusson
ORCID  : 0009-0002-4860-5095
License: CC-BY-4.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List


@dataclass
class EntropicBoundary:
    """Properties near an entropic boundary.

    Parameters
    ----------
    S : float
        Entropy value (0-1).
    energy_flow : float
        Energy-flow magnitude at this entropy (W m^-2).
    structure_stability : float
        Normalised structure stability (0 = unstable, 1 = fully stable).
    propagation_speed_ratio : float
        v / c ratio at this entropy.
    """

    S: float
    energy_flow: float
    structure_stability: float
    propagation_speed_ratio: float = 1.0

    @property
    def regime(self) -> str:
        if self.S < 0.05:
            return "near-zero (maximal order)"
        elif self.S > 0.95:
            return "near-one (maximal disorder)"
        elif self.S < 0.3:
            return "low-entropy"
        elif self.S > 0.7:
            return "high-entropy"
        else:
            return "mid-range"

    @property
    def information_capacity(self) -> float:
        """Shannon-like information capacity: -S*log(S) - (1-S)*log(1-S).
        Peaks at S=0.5, vanishes at boundaries."""
        if self.S <= 0 or self.S >= 1:
            return 0.0
        return -(self.S * math.log2(self.S) + (1 - self.S) * math.log2(1 - self.S))


@dataclass
class ExtremeRegime:
    """A regime characterisation near S=0 or S=1.

    Parameters
    ----------
    name : str
        Regime identifier.
    S_min : float
        Lower entropy bound of the regime.
    S_max : float
        Upper entropy bound of the regime.
    flow_suppression : float
        Factor by which energy flow is suppressed (0-1).
    description : str
        Physical description of the regime.
    """

    name: str
    S_min: float
    S_max: float
    flow_suppression: float = 0.0
    description: str = ""

    @property
    def width(self) -> float:
        return self.S_max - self.S_min

    @property
    def midpoint(self) -> float:
        return 0.5 * (self.S_min + self.S_max)

    def contains(self, S: float) -> bool:
        return self.S_min <= S <= self.S_max


@dataclass
class InformationCollapse:
    """Model of information collapse as S -> boundary.

    Parameters
    ----------
    S_current : float
        Current entropy.
    S_target : float
        Target boundary (0 or 1).
    collapse_rate : float
        Rate of information loss (Gyr^-1).
    """

    S_current: float
    S_target: float = 1.0
    collapse_rate: float = 0.1

    @property
    def distance_to_boundary(self) -> float:
        return abs(self.S_target - self.S_current)

    @property
    def time_to_collapse(self) -> float:
        """Estimated time to reach boundary (Gyr), exponential approach."""
        d = self.distance_to_boundary
        if d <= 0 or self.collapse_rate <= 0:
            return 0.0
        return -math.log(0.01) / self.collapse_rate  # time to 99% approach

    @property
    def information_remaining(self) -> float:
        """Fraction of information remaining relative to S=0.5 peak."""
        if self.S_current <= 0 or self.S_current >= 1:
            return 0.0
        h = -(self.S_current * math.log2(self.S_current)
              + (1 - self.S_current) * math.log2(1 - self.S_current))
        return h  # max = 1.0 at S=0.5


@dataclass
class ExtremesAnalyzer:
    """Analyze a set of entropic boundary points and regimes."""

    boundaries: List[EntropicBoundary] = field(default_factory=list)
    regimes: List[ExtremeRegime] = field(default_factory=list)

    def mean_information_capacity(self) -> float:
        if not self.boundaries:
            return 0.0
        return sum(b.information_capacity for b in self.boundaries) / len(self.boundaries)

    def near_zero_count(self) -> int:
        return sum(1 for b in self.boundaries if b.S < 0.05)

    def near_one_count(self) -> int:
        return sum(1 for b in self.boundaries if b.S > 0.95)

    def summary(self) -> dict:
        return {
            "n_boundaries": len(self.boundaries),
            "mean_info_capacity": round(self.mean_information_capacity(), 4),
            "near_zero_count": self.near_zero_count(),
            "near_one_count": self.near_one_count(),
            "n_regimes": len(self.regimes),
        }
