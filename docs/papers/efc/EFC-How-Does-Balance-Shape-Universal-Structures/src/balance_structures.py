"""
Balance and Universal Structures Module

Models how balance between opposing gradients, entropic pressures,
and energy-flow resistance produces stable universal structures.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class GradientBalance:
    """
    Balance between opposing entropy and energy-flow gradients.

    Equilibrium when: grad_S * Ef = P_resist

    Attributes:
        grad_s: Entropy gradient magnitude
        ef: Energy flow density
        resistance: Grid resistance
    """
    grad_s: float
    ef: float
    resistance: float

    def driving_force(self) -> float:
        """Net driving force: grad_S * Ef."""
        return self.grad_s * self.ef

    def balance_ratio(self) -> float:
        """
        Ratio of driving force to resistance.

        Equilibrium at ratio = 1.

        Returns:
            Driving force / resistance
        """
        if self.resistance <= 0:
            return float("inf")
        return self.driving_force() / self.resistance

    def is_stable(self, tolerance: float = 0.1) -> bool:
        """Check if configuration is near equilibrium."""
        return abs(self.balance_ratio() - 1.0) < tolerance


@dataclass
class EquilibriumStructure:
    """
    A structure formed at an equilibrium point.

    Attributes:
        position: Spatial position of equilibrium
        scale: Characteristic size
        entropy: Local entropy value
        stability: Stability parameter (positive = stable)
    """
    position: float
    scale: float
    entropy: float
    stability: float

    def is_stable(self) -> bool:
        """Check stability."""
        return self.stability > 0

    def binding_energy(self) -> float:
        """
        Effective binding energy from entropy trapping.

        E_bind ~ stability * entropy * scale

        Returns:
            Binding energy estimate
        """
        return self.stability * self.entropy * self.scale


class UniversalStructureModel:
    """
    Model for structure formation across scales through
    gradient balance and entropic equilibrium.
    """

    def __init__(
        self,
        ef_0: float = 10.0,
        s_background: float = 1.0,
        resistance_base: float = 5.0,
        n_scales: int = 5,
    ):
        """
        Args:
            ef_0: Background energy flow density
            s_background: Background entropy
            resistance_base: Base grid resistance
            n_scales: Number of hierarchy levels
        """
        self.ef_0 = ef_0
        self.s_background = s_background
        self.resistance_base = resistance_base
        self.n_scales = n_scales

    def find_equilibria(self, x_values: List[float]) -> List[EquilibriumStructure]:
        """
        Find equilibrium structures along a spatial profile.

        Uses a simple model where entropy varies sinusoidally
        and equilibria form at gradient-balance points.

        Args:
            x_values: Spatial positions to evaluate

        Returns:
            List of equilibrium structures found
        """
        structures = []
        for i, x in enumerate(x_values):
            # Sinusoidal entropy variation
            s = self.s_background + 0.5 * math.sin(x)
            grad_s = 0.5 * math.cos(x)

            # Local resistance varies with position
            r = self.resistance_base * (1.0 + 0.2 * math.sin(2 * x))

            balance = GradientBalance(
                grad_s=abs(grad_s), ef=self.ef_0, resistance=r
            )

            if balance.is_stable(tolerance=0.3):
                # Stability from second derivative of potential
                stability = -0.5 * math.sin(x)
                scale = 1.0 / (1.0 + abs(grad_s))
                structures.append(EquilibriumStructure(
                    position=x,
                    scale=scale,
                    entropy=s,
                    stability=stability,
                ))
        return structures

    def hierarchy_spectrum(self) -> List[dict]:
        """
        Compute scale hierarchy from nested gradient balance.

        Each level has scale ~ base_scale * 3^n.

        Returns:
            List of dicts with level, scale, entropy, binding energy
        """
        base_scale = 1.0
        results = []
        for n in range(self.n_scales):
            scale = base_scale * 3.0 ** n
            s = self.s_background * (1.0 + 0.1 * n)
            stability = 1.0 / (1.0 + 0.2 * n)
            structure = EquilibriumStructure(
                position=0.0, scale=scale, entropy=s, stability=stability
            )
            results.append({
                "level": n,
                "scale": scale,
                "entropy": s,
                "stability": stability,
                "binding_energy": structure.binding_energy(),
                "stable": structure.is_stable(),
            })
        return results

    def summary(self) -> str:
        """Return human-readable summary."""
        return (
            "Universal Structure Model (EFC)\n"
            f"  Ef_0           = {self.ef_0}\n"
            f"  S_background   = {self.s_background}\n"
            f"  R_base         = {self.resistance_base}\n"
            f"  n_scales       = {self.n_scales}"
        )
