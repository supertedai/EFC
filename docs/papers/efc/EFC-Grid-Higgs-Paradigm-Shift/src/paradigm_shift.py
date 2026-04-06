"""
Paradigm Shift Module

Reframes mass and inertia as emergent properties of energy flow,
entropy gradients, and grid-level resistance.
"""

import math
from dataclasses import dataclass
from typing import List


@dataclass
class ThermodynamicMass:
    """
    Mass as emergent from thermodynamic field interaction.

    m_thermo(S, Ef) = lambda_ * S * Ef / (1 + gamma * S)

    Attributes:
        lambda_: Thermodynamic mass coupling
        gamma: Saturation parameter
    """
    lambda_: float
    gamma: float

    def mass(self, s: float, ef: float) -> float:
        """
        Compute thermodynamic mass.

        Args:
            s: Entropy value
            ef: Energy flow density

        Returns:
            Emergent mass value
        """
        return self.lambda_ * s * ef / (1.0 + self.gamma * s)

    def mass_gradient(self, s: float, ef: float) -> float:
        """
        dm/dS at given entropy.

        dm/dS = lambda_ * Ef / (1 + gamma * S)^2

        Args:
            s: Entropy value
            ef: Energy flow density

        Returns:
            Mass gradient with respect to entropy
        """
        denom = (1.0 + self.gamma * s) ** 2
        return self.lambda_ * ef / denom

    def saturation_mass(self, ef: float) -> float:
        """
        Asymptotic mass as S -> infinity.

        m_sat = lambda_ * Ef / gamma

        Args:
            ef: Energy flow density

        Returns:
            Saturation mass
        """
        return self.lambda_ * ef / self.gamma


@dataclass
class InertiaField:
    """
    Inertia as energy-flow impedance through the grid.

    I(S) = I0 * (1 + eta * S^2)

    Attributes:
        i0: Base inertia
        eta: Entropy-inertia coupling
    """
    i0: float
    eta: float

    def inertia(self, s: float) -> float:
        """
        Compute inertia at entropy value s.

        Args:
            s: Entropy value

        Returns:
            Inertial coefficient
        """
        return self.i0 * (1.0 + self.eta * s ** 2)

    def response_time(self, s: float) -> float:
        """
        Response time proportional to inertia.

        tau ~ I(S)

        Args:
            s: Entropy value

        Returns:
            Response time scale
        """
        return self.inertia(s)


class ParadigmShiftModel:
    """
    Full paradigm-shift model: mass and inertia from
    thermodynamic field interactions.
    """

    def __init__(
        self,
        lambda_: float = 1.0,
        gamma: float = 0.3,
        i0: float = 1.0,
        eta: float = 0.1,
        ef_0: float = 10.0,
    ):
        self.thermo_mass = ThermodynamicMass(lambda_=lambda_, gamma=gamma)
        self.inertia_field = InertiaField(i0=i0, eta=eta)
        self.ef_0 = ef_0

    def compare_paradigms(self, s_values: List[float]) -> List[dict]:
        """
        Compare classical constant mass with emergent thermodynamic mass.

        Args:
            s_values: Entropy values to evaluate

        Returns:
            List of dicts with s, thermo_mass, inertia, classical_mass
        """
        m_classical = self.thermo_mass.mass(0.0, self.ef_0)
        results = []
        for s in s_values:
            m = self.thermo_mass.mass(s, self.ef_0)
            i = self.inertia_field.inertia(s)
            results.append({
                "s": s,
                "thermo_mass": m,
                "inertia": i,
                "classical_mass": m_classical,
                "mass_ratio": m / m_classical if m_classical > 0 else float("inf"),
            })
        return results

    def transition_entropy(self) -> float:
        """
        Entropy at which mass reaches half its saturation value.

        S_half = 1 / gamma

        Returns:
            Transition entropy
        """
        return 1.0 / self.thermo_mass.gamma

    def summary(self) -> str:
        """Return human-readable summary."""
        m_sat = self.thermo_mass.saturation_mass(self.ef_0)
        return (
            "Grid-Higgs Paradigm Shift Model\n"
            f"  lambda  = {self.thermo_mass.lambda_}\n"
            f"  gamma   = {self.thermo_mass.gamma}\n"
            f"  I0      = {self.inertia_field.i0}\n"
            f"  eta     = {self.inertia_field.eta}\n"
            f"  Ef_0    = {self.ef_0}\n"
            f"  m_sat   = {m_sat:.4f}\n"
            f"  S_half  = {self.transition_entropy():.4f}"
        )
