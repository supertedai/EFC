"""
Entropic Dynamics Module

Models how entropic dynamics emerge from the Grid field, entropy
field S, and energy-flow field Ef interactions.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class GridField:
    """
    The Grid field providing resistance to energy flow.

    G(x) = G0 * exp(-x^2 / (2 * sigma^2))

    Attributes:
        g0: Grid field amplitude
        sigma: Characteristic width
    """
    g0: float
    sigma: float

    def value(self, x: float) -> float:
        """Grid field value at position x."""
        return self.g0 * math.exp(-x ** 2 / (2.0 * self.sigma ** 2))

    def gradient(self, x: float) -> float:
        """dG/dx at position x."""
        return -x / (self.sigma ** 2) * self.value(x)


@dataclass
class EntropicFlow:
    """
    Entropy-driven energy flow field.

    The flow J is driven by entropy gradient and resisted by the grid:
    J(x) = -D * dS/dx / G(x)

    Attributes:
        diffusion: Diffusion coefficient D
        grid: Grid field providing resistance
    """
    diffusion: float
    grid: GridField

    def entropy_profile(self, x: float, s0: float, grad_s: float) -> float:
        """
        Linear entropy profile: S(x) = s0 + grad_s * x.

        Args:
            x: Position
            s0: Entropy at origin
            grad_s: Entropy gradient

        Returns:
            Entropy at position x
        """
        return s0 + grad_s * x

    def flow(self, x: float, grad_s: float) -> float:
        """
        Compute entropy-driven flow at position x.

        J(x) = -D * grad_S / G(x)

        Args:
            x: Position
            grad_s: Entropy gradient at x

        Returns:
            Flow magnitude
        """
        g = self.grid.value(x)
        if g <= 0:
            return 0.0
        return -self.diffusion * grad_s / g

    def entropy_production(self, x: float, grad_s: float) -> float:
        """
        Local entropy production rate.

        sigma_s = D * (grad_S)^2 / G(x)

        Args:
            x: Position
            grad_s: Entropy gradient

        Returns:
            Entropy production rate
        """
        g = self.grid.value(x)
        if g <= 0:
            return 0.0
        return self.diffusion * grad_s ** 2 / g


class EntropicDynamicsModel:
    """
    Full entropic dynamics model: structure formation from
    Grid-S-Ef field interactions.
    """

    def __init__(
        self,
        g0: float = 1.0,
        sigma: float = 2.0,
        diffusion: float = 1.0,
        s0: float = 1.0,
        grad_s: float = 0.5,
    ):
        self.grid = GridField(g0=g0, sigma=sigma)
        self.entropic_flow = EntropicFlow(diffusion=diffusion, grid=self.grid)
        self.s0 = s0
        self.grad_s = grad_s

    def dynamics_profile(
        self, x_values: List[float]
    ) -> List[dict]:
        """
        Compute dynamics at multiple positions.

        Args:
            x_values: List of positions

        Returns:
            List of dicts with x, grid, entropy, flow, production
        """
        results = []
        for x in x_values:
            s = self.entropic_flow.entropy_profile(x, self.s0, self.grad_s)
            g = self.grid.value(x)
            j = self.entropic_flow.flow(x, self.grad_s)
            sigma_s = self.entropic_flow.entropy_production(x, self.grad_s)
            results.append({
                "x": x,
                "grid": g,
                "entropy": s,
                "flow": j,
                "production": sigma_s,
            })
        return results

    def equilibrium_condition(self, x: float) -> Tuple[float, float]:
        """
        Check equilibrium: net flow should balance entropy production.

        Returns (flow, production) for comparison.
        """
        j = self.entropic_flow.flow(x, self.grad_s)
        sigma_s = self.entropic_flow.entropy_production(x, self.grad_s)
        return (j, sigma_s)

    def summary(self) -> str:
        """Return human-readable summary."""
        return (
            "Grid Model for Entropic Dynamics\n"
            f"  G0        = {self.grid.g0}\n"
            f"  sigma     = {self.grid.sigma}\n"
            f"  D         = {self.entropic_flow.diffusion}\n"
            f"  S0        = {self.s0}\n"
            f"  grad_S    = {self.grad_s}"
        )
