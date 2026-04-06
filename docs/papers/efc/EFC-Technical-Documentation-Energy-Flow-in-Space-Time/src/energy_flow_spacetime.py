"""
EFC -- Technical Documentation: Energy Flow in Space-Time
==========================================================
Field specifications, variable sets, operators, and integration rules
for simulating energy flow in spacetime.

Core fields:
  - S(x,t)     : entropy field (normalised 0-1)
  - J(x,t)     : energy-flow vector field (W m^-2)
  - R_grid(x,t): grid resistance scalar field

Continuity: dS/dt + div(J) = sigma   (entropy production rate)

Author : Morten Magnusson
ORCID  : 0009-0002-4860-5095
License: CC-BY-4.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class FieldVariable:
    """A scalar or vector field variable at a point.

    Parameters
    ----------
    name : str
        Variable name (e.g. 'S', 'J_x', 'R_grid').
    value : float
        Current value.
    unit : str
        Physical unit string.
    """

    name: str
    value: float
    unit: str = ""

    def scale(self, factor: float) -> "FieldVariable":
        return FieldVariable(self.name, self.value * factor, self.unit)


@dataclass
class SpacetimePoint:
    """A point in spacetime carrying field values.

    Parameters
    ----------
    x, y, z : float
        Spatial coordinates (kpc).
    t : float
        Time coordinate (Gyr).
    S : float
        Entropy field value (normalised 0-1).
    Jx, Jy, Jz : float
        Energy-flow vector components (W m^-2).
    R_grid : float
        Grid resistance (>=1).
    """

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    t: float = 0.0
    S: float = 0.5
    Jx: float = 0.0
    Jy: float = 0.0
    Jz: float = 0.0
    R_grid: float = 1.0

    @property
    def J_magnitude(self) -> float:
        return math.sqrt(self.Jx ** 2 + self.Jy ** 2 + self.Jz ** 2)

    @property
    def effective_speed(self) -> float:
        """Effective propagation speed at this point (m/s)."""
        c = 299792458.0
        return c / max(self.R_grid, 1e-30)

    def fields_dict(self) -> dict:
        return {
            "S": self.S,
            "Jx": self.Jx,
            "Jy": self.Jy,
            "Jz": self.Jz,
            "R_grid": self.R_grid,
        }


@dataclass
class EnergyFlowField:
    """A discretised energy-flow field on a 1-D grid.

    Parameters
    ----------
    points : list of SpacetimePoint
        Ordered spatial points along x-axis.
    """

    points: List[SpacetimePoint] = field(default_factory=list)

    def entropy_gradient(self) -> List[float]:
        """Central-difference estimate of dS/dx."""
        grads = []
        for i in range(len(self.points)):
            if i == 0 or i == len(self.points) - 1:
                grads.append(0.0)
            else:
                dx = self.points[i + 1].x - self.points[i - 1].x
                if dx == 0:
                    grads.append(0.0)
                else:
                    dS = self.points[i + 1].S - self.points[i - 1].S
                    grads.append(dS / dx)
        return grads

    def divergence_J(self) -> List[float]:
        """Central-difference estimate of div(J) = dJx/dx (1-D)."""
        divs = []
        for i in range(len(self.points)):
            if i == 0 or i == len(self.points) - 1:
                divs.append(0.0)
            else:
                dx = self.points[i + 1].x - self.points[i - 1].x
                if dx == 0:
                    divs.append(0.0)
                else:
                    dJx = self.points[i + 1].Jx - self.points[i - 1].Jx
                    divs.append(dJx / dx)
        return divs

    def total_entropy(self) -> float:
        return sum(p.S for p in self.points)


@dataclass
class EFCIntegrator:
    """Simple forward-Euler integrator for the entropy continuity equation.

    dS/dt = sigma - div(J)

    Parameters
    ----------
    field : EnergyFlowField
        The field to integrate.
    sigma : float
        Uniform entropy production rate.
    dt : float
        Time step (Gyr).
    """

    field: EnergyFlowField
    sigma: float = 0.01
    dt: float = 0.001

    def step(self) -> None:
        """Advance the field by one time step."""
        div_J = self.field.divergence_J()
        for i, p in enumerate(self.field.points):
            dS = (self.sigma - div_J[i]) * self.dt
            p.S = max(0.0, min(1.0, p.S + dS))
            p.t += self.dt

    def run(self, n_steps: int) -> List[float]:
        """Run n_steps and return entropy history (total S per step)."""
        history = []
        for _ in range(n_steps):
            self.step()
            history.append(self.field.total_entropy())
        return history
