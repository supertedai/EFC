"""
EFC -- Light Speed as a Regulator of Energy Flow in the Universe

Models how the speed of light emerges as a regulating boundary for energy
propagation, stability, and dynamic structure in the EFC framework.

Author: Morten Magnusson, ORCID 0009-0002-4860-5095
License: CC-BY-4.0
"""

from dataclasses import dataclass, field
from typing import List, Dict
import math


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SPEED_OF_LIGHT: float = 2.998e8          # m/s
BOLTZMANN_K: float = 1.380649e-23        # J/K
PLANCK_LENGTH: float = 1.616e-35         # m
PLANCK_TIME: float = 5.391e-44           # s
DEFAULT_GRID_RESISTANCE: float = 0.01


@dataclass
class PropagationRegime:
    """
    A propagation regime defined by grid resistance and entropy conditions.

    The speed of light is not an arbitrary constant but the maximum
    propagation speed allowed by the grid's entropy-energy balance.
    """
    grid_resistance: float = DEFAULT_GRID_RESISTANCE
    entropy_density: float = 1.0   # J K^-1 m^-3
    energy_density: float = 1.0    # J m^-3

    def effective_speed(self) -> float:
        """Effective propagation speed: v = c / (1 + R)."""
        return SPEED_OF_LIGHT / (1.0 + self.grid_resistance)

    def speed_ratio(self) -> float:
        """Ratio of effective speed to c."""
        return 1.0 / (1.0 + self.grid_resistance)

    def regulation_strength(self) -> float:
        """
        Regulation strength: how much the grid slows propagation.

        Gamma_reg = R / (1 + R), ranges from 0 (no regulation) to 1 (full stop).
        """
        return self.grid_resistance / (1.0 + self.grid_resistance)

    def entropy_energy_ratio(self) -> float:
        """Ratio s/rho -- determines the local thermodynamic regime."""
        if self.energy_density <= 0:
            return 0.0
        return self.entropy_density / self.energy_density


@dataclass
class CausalHorizon:
    """
    Causal horizon set by the speed of light in a given regime.

    The horizon defines the maximum distance from which information
    can arrive within a given time.
    """
    regime: PropagationRegime = field(default_factory=PropagationRegime)

    def horizon_radius(self, time: float) -> float:
        """Causal horizon radius: r = v_eff * t."""
        return self.regime.effective_speed() * time

    def horizon_volume(self, time: float) -> float:
        """Volume of the causal sphere: V = (4/3) pi r^3."""
        r = self.horizon_radius(time)
        return (4.0 / 3.0) * math.pi * r ** 3

    def light_crossing_time(self, distance: float) -> float:
        """Time for light to cross a given distance in this regime."""
        v = self.regime.effective_speed()
        if v <= 0:
            return float('inf')
        return distance / v


class StabilityAnalysis:
    """
    Analyses how light speed regulates stability of energy-flow structures.

    Structures are stable when their internal communication time
    (set by light speed) is shorter than their dynamical time.
    """

    def __init__(self, grid_resistance: float = DEFAULT_GRID_RESISTANCE):
        self.regime = PropagationRegime(grid_resistance=grid_resistance)
        self.horizon = CausalHorizon(regime=self.regime)

    def communication_time(self, size: float) -> float:
        """Internal communication time: t_comm = L / v_eff."""
        return self.horizon.light_crossing_time(size)

    def stability_ratio(self, size: float, dynamical_time: float) -> float:
        """
        Stability ratio: t_comm / t_dyn.

        Stable if ratio < 1 (can communicate faster than it evolves).
        """
        t_comm = self.communication_time(size)
        if dynamical_time <= 0:
            return float('inf')
        return t_comm / dynamical_time

    def is_stable(self, size: float, dynamical_time: float) -> bool:
        """Check if the structure is causally stable."""
        return self.stability_ratio(size, dynamical_time) < 1.0

    def critical_size(self, dynamical_time: float) -> float:
        """Maximum stable size: L_crit = v_eff * t_dyn."""
        return self.regime.effective_speed() * dynamical_time


class LightSpeedRegulatorModel:
    """
    Top-level model: light speed as regulator of energy flow.
    """

    PARAMETERS = {
        "c": SPEED_OF_LIGHT,
        "k_B": BOLTZMANN_K,
        "l_P": PLANCK_LENGTH,
        "t_P": PLANCK_TIME,
        "R_default": DEFAULT_GRID_RESISTANCE,
    }

    EQUATIONS = {
        "effective_speed": "v_eff = c / (1 + R)",
        "regulation_strength": "Gamma_reg = R / (1 + R)",
        "causal_horizon": "r_H = v_eff * t",
        "stability_condition": "L / v_eff < t_dyn",
        "critical_size": "L_crit = v_eff * t_dyn",
    }

    def __init__(self, grid_resistance: float = DEFAULT_GRID_RESISTANCE):
        self.grid_resistance = grid_resistance
        self.stability = StabilityAnalysis(grid_resistance)

    def speed_vs_resistance(self, r_values: List[float]) -> List[Dict[str, float]]:
        """Tabulate effective speed and regulation across resistance values."""
        results = []
        for R in r_values:
            pr = PropagationRegime(grid_resistance=R)
            results.append({
                "R": R,
                "v_eff": pr.effective_speed(),
                "speed_ratio": pr.speed_ratio(),
                "regulation": pr.regulation_strength(),
            })
        return results

    def summary(self) -> str:
        lines = [
            "EFC: Light Speed as a Regulator of Energy Flow",
            "=" * 50,
            f"Grid resistance:     {self.grid_resistance}",
            f"v_eff:               {self.stability.regime.effective_speed():.6e} m/s",
            f"Regulation strength: {self.stability.regime.regulation_strength():.6f}",
        ]
        return "\n".join(lines)
