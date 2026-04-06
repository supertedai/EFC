"""
EFC -- The Energy-Flow Interface
=================================
Models the boundary layer where entropy, grid, and energy-flow fields
interact.  The interface regulates transitions, stabilises patterns,
and bridges local processes with large-scale behaviour.

Key equations:
  Phi_interface = S * J / R_grid        (interface flux)
  Stability: d(Phi)/dt -> 0 at equilibrium

Author : Morten Magnusson
ORCID  : 0009-0002-4860-5095
License: CC-BY-4.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List


@dataclass
class InterfaceLayer:
    """A single interface layer between two regions.

    Parameters
    ----------
    name : str
        Layer identifier.
    S_left : float
        Entropy on the left side (0-1).
    S_right : float
        Entropy on the right side (0-1).
    J_through : float
        Energy-flow magnitude across the interface (W m^-2).
    R_grid : float
        Grid resistance at the interface (>=1).
    width : float
        Interface width (kpc).
    """

    name: str
    S_left: float
    S_right: float
    J_through: float
    R_grid: float = 1.0
    width: float = 0.1

    @property
    def entropy_jump(self) -> float:
        """Entropy discontinuity across the interface."""
        return self.S_right - self.S_left

    @property
    def interface_flux(self) -> float:
        """Phi = mean(S) * J / R_grid."""
        S_mean = 0.5 * (self.S_left + self.S_right)
        return S_mean * self.J_through / max(self.R_grid, 1e-30)

    @property
    def gradient_across(self) -> float:
        """Entropy gradient across the layer (kpc^-1)."""
        if self.width <= 0:
            return 0.0
        return self.entropy_jump / self.width


@dataclass
class FieldInteraction:
    """Interaction strength between pairs of EFC fields.

    Parameters
    ----------
    S_value : float
        Local entropy field value.
    J_value : float
        Local energy-flow magnitude.
    R_grid : float
        Local grid resistance.
    """

    S_value: float
    J_value: float
    R_grid: float = 1.0

    @property
    def SJ_coupling(self) -> float:
        """Entropy-flow coupling: S * J."""
        return self.S_value * self.J_value

    @property
    def SR_coupling(self) -> float:
        """Entropy-grid coupling: S / R_grid."""
        return self.S_value / max(self.R_grid, 1e-30)

    @property
    def total_interaction(self) -> float:
        """Combined interaction strength: S * J / R_grid."""
        return self.S_value * self.J_value / max(self.R_grid, 1e-30)


@dataclass
class BoundaryDynamics:
    """Time evolution of an interface layer.

    Parameters
    ----------
    layer : InterfaceLayer
        The interface layer.
    relaxation_rate : float
        Rate at which the interface relaxes toward equilibrium (Gyr^-1).
    """

    layer: InterfaceLayer
    relaxation_rate: float = 1.0

    def evolve(self, dt: float) -> InterfaceLayer:
        """Evolve the interface by dt (Gyr) toward equilibrium.

        The entropy jump relaxes exponentially.
        """
        factor = math.exp(-self.relaxation_rate * dt)
        S_mid = 0.5 * (self.layer.S_left + self.layer.S_right)
        new_left = S_mid + (self.layer.S_left - S_mid) * factor
        new_right = S_mid + (self.layer.S_right - S_mid) * factor
        return InterfaceLayer(
            name=self.layer.name,
            S_left=new_left,
            S_right=new_right,
            J_through=self.layer.J_through,
            R_grid=self.layer.R_grid,
            width=self.layer.width,
        )


@dataclass
class EnergyFlowInterfaceAnalyzer:
    """Analyze a collection of interface layers."""

    layers: List[InterfaceLayer] = field(default_factory=list)

    def total_interface_flux(self) -> float:
        return sum(l.interface_flux for l in self.layers)

    def mean_entropy_jump(self) -> float:
        if not self.layers:
            return 0.0
        return sum(abs(l.entropy_jump) for l in self.layers) / len(self.layers)

    def max_gradient(self) -> float:
        if not self.layers:
            return 0.0
        return max(abs(l.gradient_across) for l in self.layers)

    def summary(self) -> dict:
        return {
            "n_layers": len(self.layers),
            "total_interface_flux": self.total_interface_flux(),
            "mean_entropy_jump": self.mean_entropy_jump(),
            "max_gradient_kpc": self.max_gradient(),
        }
