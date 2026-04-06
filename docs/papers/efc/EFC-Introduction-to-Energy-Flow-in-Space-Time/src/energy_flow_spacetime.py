"""
EFC -- Introduction to Energy Flow in Space-Time

Core concepts for how energy flow drives structure, motion, and
information propagation in spacetime.

Author: Morten Magnusson, ORCID 0009-0002-4860-5095
License: CC-BY-4.0
"""

from dataclasses import dataclass, field
from typing import List, Dict
import math


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BOLTZMANN_K: float = 1.380649e-23   # J/K
SPEED_OF_LIGHT: float = 2.998e8     # m/s
DEFAULT_GRID_RESISTANCE: float = 0.01


@dataclass
class SpacetimePoint:
    """A point in EFC spacetime defined by coordinates and local entropy."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    t: float = 0.0
    entropy_density: float = 0.0  # J K^-1 m^-3
    energy_density: float = 0.0   # J m^-3


@dataclass
class EnergyFlowField:
    """
    Energy flow field in spacetime.

    The field J(x,t) describes the local energy flux vector.
    Structure emerges where the flow converges or is modulated
    by grid resistance.
    """
    flux_magnitude: float = 1e10      # J m^-2 s^-1
    direction: List[float] = field(default_factory=lambda: [1.0, 0.0, 0.0])
    grid_resistance: float = DEFAULT_GRID_RESISTANCE

    def effective_flux(self) -> float:
        """Net flux after grid damping: J_eff = J / (1 + R)."""
        return self.flux_magnitude / (1.0 + self.grid_resistance)

    def momentum_density(self) -> float:
        """Energy-flow momentum density: p = J / c^2."""
        return self.flux_magnitude / (SPEED_OF_LIGHT ** 2)

    def information_speed(self) -> float:
        """Maximum information propagation speed: v_info = c / (1 + R)."""
        return SPEED_OF_LIGHT / (1.0 + self.grid_resistance)


@dataclass
class EntropyField:
    """
    Entropy field on a spacetime region.

    The gradient of this field drives energy flow.
    """
    values: List[float] = field(default_factory=list)   # entropy at grid points
    spacing: float = 1.0  # spatial spacing between points

    def gradient_at(self, index: int) -> float:
        """Central difference gradient at interior point."""
        if index <= 0 or index >= len(self.values) - 1:
            return 0.0
        return (self.values[index + 1] - self.values[index - 1]) / (2.0 * self.spacing)

    def max_gradient(self) -> float:
        """Maximum absolute gradient across all interior points."""
        if len(self.values) < 3:
            return 0.0
        return max(abs(self.gradient_at(i)) for i in range(1, len(self.values) - 1))

    def total_entropy(self) -> float:
        """Total entropy (sum over all points * spacing)."""
        return sum(self.values) * self.spacing


class SpacetimeEnergyFlow:
    """
    Top-level model: energy flow in spacetime.

    Combines energy flow fields and entropy fields to show how
    structure, motion, and information arise from thermodynamic
    gradients in a grid-mediated spacetime.
    """

    PARAMETERS = {
        "k_B": BOLTZMANN_K,
        "c": SPEED_OF_LIGHT,
        "R_default": DEFAULT_GRID_RESISTANCE,
    }

    EQUATIONS = {
        "effective_flux": "J_eff = J / (1 + R)",
        "momentum_density": "p = J / c^2",
        "info_speed": "v_info = c / (1 + R)",
        "entropy_gradient": "nabla S = (S[i+1] - S[i-1]) / (2 dx)",
        "flow_divergence": "div J = -dE/dt  (continuity)",
    }

    def __init__(self, grid_resistance: float = DEFAULT_GRID_RESISTANCE):
        self.grid_resistance = grid_resistance

    def propagation_delay(self, distance: float) -> float:
        """Time for information to cross a distance through the grid."""
        v = SPEED_OF_LIGHT / (1.0 + self.grid_resistance)
        return distance / v

    def flow_convergence(self, entropy_field: EntropyField,
                         flux_magnitude: float) -> List[Dict[str, float]]:
        """
        Compute flow convergence at each interior point.

        Regions of high convergence are candidates for structure formation.
        """
        results = []
        for i in range(1, len(entropy_field.values) - 1):
            grad = entropy_field.gradient_at(i)
            local_flux = flux_magnitude * grad
            eff = local_flux / (1.0 + self.grid_resistance)
            results.append({
                "index": i,
                "gradient": grad,
                "local_flux": local_flux,
                "effective_flux": eff,
            })
        return results

    def energy_conservation_check(self, inflow: float,
                                  outflow: float, stored: float) -> Dict[str, float]:
        """Verify energy conservation: inflow = outflow + d(stored)/dt."""
        residual = inflow - outflow - stored
        return {
            "inflow": inflow,
            "outflow": outflow,
            "stored_change": stored,
            "residual": residual,
            "conserved": abs(residual) < 1e-10,
        }

    def summary(self) -> str:
        lines = [
            "EFC: Introduction to Energy Flow in Space-Time",
            "=" * 50,
            f"Grid resistance:   {self.grid_resistance}",
            f"Info speed:        {SPEED_OF_LIGHT / (1 + self.grid_resistance):.3e} m/s",
        ]
        return "\n".join(lines)
