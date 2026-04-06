"""
Grid-Higgs Framework Module

Models how grid-level resistance and entropy gradients produce
Higgs-like mass effects in the EFC framework.
"""

import math
from dataclasses import dataclass
from typing import List


@dataclass
class GridResistance:
    """
    Grid-level resistance field that impedes energy flow.

    Attributes:
        r0: Base resistance at zero entropy
        alpha: Coupling between entropy and resistance
    """
    r0: float
    alpha: float

    def resistance(self, s: float) -> float:
        """
        Compute grid resistance at entropy value s.

        R(S) = R0 * (1 + alpha * S)

        Args:
            s: Local entropy value

        Returns:
            Grid resistance
        """
        return self.r0 * (1.0 + self.alpha * s)

    def derivative(self, s: float) -> float:
        """dR/dS = R0 * alpha."""
        return self.r0 * self.alpha


@dataclass
class EffectiveMass:
    """
    Effective mass emerging from grid resistance and energy flow.

    m_eff = kappa * R(S) * Ef

    Attributes:
        kappa: Mass-generation coupling constant
        resistance: Grid resistance field
    """
    kappa: float
    resistance: GridResistance

    def mass(self, s: float, ef: float) -> float:
        """
        Compute effective mass.

        m_eff = kappa * R(S) * Ef

        Args:
            s: Local entropy
            ef: Local energy flow density

        Returns:
            Effective mass
        """
        return self.kappa * self.resistance.resistance(s) * ef

    def inertia(self, s: float, ef: float) -> float:
        """
        Compute inertial response (resistance to acceleration).

        Inertia ~ d(m_eff)/d(Ef) = kappa * R(S)

        Args:
            s: Local entropy
            ef: Energy flow density (unused, kept for interface consistency)

        Returns:
            Inertial coefficient
        """
        return self.kappa * self.resistance.resistance(s)


class GridHiggsModel:
    """
    Complete Grid-Higgs model combining resistance, entropy, and
    energy flow to produce emergent mass.
    """

    def __init__(
        self,
        r0: float = 1.0,
        alpha: float = 0.5,
        kappa: float = 1.0,
        ef_0: float = 10.0,
    ):
        """
        Args:
            r0: Base grid resistance
            alpha: Entropy-resistance coupling
            kappa: Mass-generation coupling constant
            ef_0: Reference energy flow density
        """
        self.resistance = GridResistance(r0=r0, alpha=alpha)
        self.effective_mass = EffectiveMass(kappa=kappa, resistance=self.resistance)
        self.ef_0 = ef_0
        self.kappa = kappa

    def mass_spectrum(self, s_values: List[float]) -> List[dict]:
        """
        Compute mass spectrum over entropy range.

        Args:
            s_values: List of entropy values

        Returns:
            List of dicts with s, resistance, mass, inertia
        """
        results = []
        for s in s_values:
            r = self.resistance.resistance(s)
            m = self.effective_mass.mass(s, self.ef_0)
            i = self.effective_mass.inertia(s, self.ef_0)
            results.append({
                "s": s,
                "resistance": r,
                "mass": m,
                "inertia": i,
            })
        return results

    def critical_entropy(self) -> float:
        """
        Entropy value where mass doubles relative to S=0.

        R(S_c) = 2 * R0  =>  S_c = 1 / alpha

        Returns:
            Critical entropy value
        """
        return 1.0 / self.resistance.alpha

    def summary(self) -> str:
        """Return human-readable summary."""
        return (
            "Grid-Higgs Framework Model\n"
            f"  R0    = {self.resistance.r0}\n"
            f"  alpha = {self.resistance.alpha}\n"
            f"  kappa = {self.kappa}\n"
            f"  Ef_0  = {self.ef_0}\n"
            f"  m_eff(S=0) = {self.effective_mass.mass(0, self.ef_0):.4f}\n"
            f"  S_critical = {self.critical_entropy():.4f}"
        )
