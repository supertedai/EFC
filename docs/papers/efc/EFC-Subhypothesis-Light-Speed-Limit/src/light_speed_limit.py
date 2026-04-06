"""
EFC -- Subhypothesis: Light Speed Limit
========================================
Models the speed of light as a thermodynamic limit arising from grid
resistance, entropy-field coupling, and energy-flow dynamics.

Key concept: c emerges from the balance between the entropy field gradient
and the grid resistance R_grid, such that the maximum propagation speed
v_max = E_flow / R_grid converges to c in equilibrium.

Author : Morten Magnusson
ORCID  : 0009-0002-4860-5095
License: CC-BY-4.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List

# Physical constants
C_LIGHT = 299792458.0  # m/s


@dataclass
class GridResistance:
    """Grid resistance properties of a spacetime region.

    Parameters
    ----------
    R_grid : float
        Normalised grid resistance (dimensionless, >=1).
        R_grid = 1 corresponds to vacuum.
    entropy_density : float
        Local entropy density (normalised 0-1).
    energy_flow_density : float
        Local energy-flow density (W m^-2).
    """

    R_grid: float = 1.0
    entropy_density: float = 0.5
    energy_flow_density: float = 1.0

    @property
    def effective_speed(self) -> float:
        """Maximum propagation speed in this region (m/s).

        v_max = c / R_grid
        """
        if self.R_grid <= 0:
            return C_LIGHT
        return C_LIGHT / self.R_grid

    @property
    def speed_ratio(self) -> float:
        """v_max / c  --  always <= 1 for R_grid >= 1."""
        return self.effective_speed / C_LIGHT


@dataclass
class LightSpeedLimit:
    """Thermodynamic derivation of the light-speed limit.

    Parameters
    ----------
    entropy_gradient : float
        Magnitude of the entropy gradient (m^-1).
    flow_coupling : float
        Coupling constant between energy flow and entropy (dimensionless).
    R_grid : float
        Background grid resistance.
    """

    entropy_gradient: float = 0.0
    flow_coupling: float = 1.0
    R_grid: float = 1.0

    @property
    def v_limit(self) -> float:
        """Limiting propagation speed (m/s).

        v_limit = c * flow_coupling / R_grid
        Clamped to c.
        """
        v = C_LIGHT * self.flow_coupling / max(self.R_grid, 1e-30)
        return min(v, C_LIGHT)

    @property
    def deviation_from_c(self) -> float:
        """Fractional deviation (c - v_limit) / c."""
        return (C_LIGHT - self.v_limit) / C_LIGHT

    def with_entropy_perturbation(self, delta_S: float) -> "LightSpeedLimit":
        """Return a new limit with perturbed entropy gradient."""
        return LightSpeedLimit(
            entropy_gradient=self.entropy_gradient + delta_S,
            flow_coupling=self.flow_coupling,
            R_grid=self.R_grid * (1.0 + abs(delta_S)),
        )


@dataclass
class ThermodynamicSpeedAnalyzer:
    """Analyse speed-limit behaviour across multiple regions."""

    regions: List[GridResistance] = field(default_factory=list)

    def mean_effective_speed(self) -> float:
        if not self.regions:
            return C_LIGHT
        return sum(r.effective_speed for r in self.regions) / len(self.regions)

    def min_effective_speed(self) -> float:
        if not self.regions:
            return C_LIGHT
        return min(r.effective_speed for r in self.regions)

    def max_resistance(self) -> float:
        if not self.regions:
            return 1.0
        return max(r.R_grid for r in self.regions)

    def summary(self) -> dict:
        return {
            "n_regions": len(self.regions),
            "c_vacuum": C_LIGHT,
            "mean_effective_speed_m_s": self.mean_effective_speed(),
            "min_effective_speed_m_s": self.min_effective_speed(),
            "max_R_grid": self.max_resistance(),
            "mean_speed_ratio": self.mean_effective_speed() / C_LIGHT,
        }
