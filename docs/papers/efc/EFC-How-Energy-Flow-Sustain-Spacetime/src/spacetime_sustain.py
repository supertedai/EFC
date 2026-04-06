"""
Spacetime Sustain Module

Models how continuous energy flow maintains spacetime structure,
geometry, and dynamics via entropy gradients and resistance fields.
"""

import math
from dataclasses import dataclass
from typing import List


@dataclass
class EnergyFlowNetwork:
    """
    Distributed energy flow network sustaining spacetime.

    The flow density follows: Ef(r) = Ef_0 / (1 + (r/r_c)^2)

    Attributes:
        ef_0: Central flow density
        r_c: Core radius
        n_nodes: Number of flow nodes in the network
    """
    ef_0: float
    r_c: float
    n_nodes: int = 10

    def flow_density(self, r: float) -> float:
        """
        Energy flow density at distance r from a node.

        Args:
            r: Radial distance

        Returns:
            Flow density
        """
        return self.ef_0 / (1.0 + (r / self.r_c) ** 2)

    def total_flow(self, r_max: float, n_steps: int = 100) -> float:
        """
        Integrated flow within radius r_max (spherical).

        Integral of 4 pi r^2 Ef(r) dr from 0 to r_max.

        Args:
            r_max: Integration radius
            n_steps: Number of integration steps

        Returns:
            Total integrated flow
        """
        dr = r_max / n_steps
        total = 0.0
        for i in range(n_steps):
            r = (i + 0.5) * dr
            total += 4.0 * math.pi * r ** 2 * self.flow_density(r) * dr
        return total

    def network_coverage(self, volume: float) -> float:
        """
        Fraction of volume covered by flow network.

        Coverage ~ n_nodes * (4/3 pi r_c^3) / volume

        Args:
            volume: Total volume

        Returns:
            Coverage fraction (capped at 1.0)
        """
        node_vol = (4.0 / 3.0) * math.pi * self.r_c ** 3
        return min(1.0, self.n_nodes * node_vol / volume)


@dataclass
class SpacetimeStability:
    """
    Stability criterion for spacetime sustained by energy flow.

    Stability requires: Ef * grad_S >= R_threshold

    Attributes:
        r_threshold: Minimum flow-gradient product for stability
    """
    r_threshold: float

    def stability_parameter(self, ef: float, grad_s: float) -> float:
        """
        Compute stability parameter.

        Sigma = Ef * |grad_S| / R_threshold

        Stable when Sigma >= 1.

        Args:
            ef: Energy flow density
            grad_s: Entropy gradient magnitude

        Returns:
            Stability parameter
        """
        if self.r_threshold <= 0:
            return float("inf")
        return ef * abs(grad_s) / self.r_threshold

    def is_stable(self, ef: float, grad_s: float) -> bool:
        """Check if spacetime is locally stable."""
        return self.stability_parameter(ef, grad_s) >= 1.0

    def critical_flow(self, grad_s: float) -> float:
        """
        Minimum flow needed for stability at given gradient.

        Ef_min = R_threshold / |grad_S|

        Args:
            grad_s: Entropy gradient magnitude

        Returns:
            Critical energy flow density
        """
        if abs(grad_s) <= 0:
            return float("inf")
        return self.r_threshold / abs(grad_s)


class SpacetimeSustainModel:
    """
    Complete model for spacetime sustenance through energy flow.
    """

    def __init__(
        self,
        ef_0: float = 10.0,
        r_c: float = 1.0,
        n_nodes: int = 10,
        r_threshold: float = 1.0,
        grad_s_0: float = 0.5,
    ):
        self.network = EnergyFlowNetwork(ef_0=ef_0, r_c=r_c, n_nodes=n_nodes)
        self.stability = SpacetimeStability(r_threshold=r_threshold)
        self.grad_s_0 = grad_s_0

    def stability_profile(self, r_values: List[float]) -> List[dict]:
        """
        Compute stability profile at multiple radii.

        Args:
            r_values: Radial distances

        Returns:
            List of dicts with r, flow, stability_param, is_stable
        """
        results = []
        for r in r_values:
            ef = self.network.flow_density(r)
            # Gradient decreases with distance
            grad_s = self.grad_s_0 / (1.0 + r)
            sigma = self.stability.stability_parameter(ef, grad_s)
            results.append({
                "r": r,
                "flow": ef,
                "grad_s": grad_s,
                "stability_param": sigma,
                "is_stable": sigma >= 1.0,
            })
        return results

    def find_stability_horizon(
        self, r_max: float = 100.0, n_steps: int = 1000
    ) -> float:
        """
        Find the radius beyond which spacetime becomes unstable.

        Returns:
            Stability horizon radius, or r_max if always stable
        """
        dr = r_max / n_steps
        for i in range(n_steps):
            r = (i + 0.5) * dr
            ef = self.network.flow_density(r)
            grad_s = self.grad_s_0 / (1.0 + r)
            if not self.stability.is_stable(ef, grad_s):
                return r
        return r_max

    def summary(self) -> str:
        """Return human-readable summary."""
        horizon = self.find_stability_horizon()
        return (
            "Spacetime Sustain Model (EFC)\n"
            f"  Ef_0         = {self.network.ef_0}\n"
            f"  r_c          = {self.network.r_c}\n"
            f"  n_nodes      = {self.network.n_nodes}\n"
            f"  R_threshold  = {self.stability.r_threshold}\n"
            f"  grad_S_0     = {self.grad_s_0}\n"
            f"  Stability horizon ~ {horizon:.2f}"
        )
