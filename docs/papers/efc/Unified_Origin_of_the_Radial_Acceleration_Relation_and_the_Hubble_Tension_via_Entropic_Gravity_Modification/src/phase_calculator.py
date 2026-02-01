"""
Phase Calculator Φ(S)

The accumulated entropy phase determines how observables project
from the fundamental grid state function.
"""

import math
from dataclasses import dataclass
from typing import Optional

from .entropy_mapping import EntropyMapping, S_of_z


@dataclass
class PhaseResult:
    """Result of a phase calculation."""
    S: float
    phi: float
    f0: float
    delta_s: float


def phi_of_S(
    S: float,
    f0: float = 1.0,
    delta_s: float = 1.0
) -> float:
    """
    Compute accumulated phase Φ(S).

    Φ(S) = (ΔS/f₀)[exp(S/ΔS) - 1]

    With normalization f₀ = ΔS = 1:
    Φ(S) = e^S - 1

    Args:
        S: Entropy parameter
        f0: Initial grid state value
        delta_s: Characteristic entropy scale

    Returns:
        Accumulated phase Φ
    """
    return (delta_s / f0) * (math.exp(S / delta_s) - 1)


def compute_delta_phi(
    z1: float = 0,
    z2: float = 1100,
    z_trans: float = 3.0,
    delta: float = 0.5,
    f0: float = 1.0,
    delta_s: float = 1.0
) -> float:
    """
    Compute phase difference between two redshifts.

    ΔΦ = Φ(S(z1)) - Φ(S(z2))

    Args:
        z1: First redshift (default: 0, today)
        z2: Second redshift (default: 1100, CMB)
        z_trans: Transition redshift
        delta: Sigmoid width
        f0: Initial grid state
        delta_s: Entropy scale

    Returns:
        Phase difference ΔΦ
    """
    S1 = S_of_z(z1, z_trans, delta)
    S2 = S_of_z(z2, z_trans, delta)

    phi1 = phi_of_S(S1, f0, delta_s)
    phi2 = phi_of_S(S2, f0, delta_s)

    return phi1 - phi2


class PhaseCalculator:
    """
    Calculator for entropy phase Φ(S).

    The accumulated phase determines observable projections:
    ln(X/X₀) = a_X · Φ(S)

    Example:
        calc = PhaseCalculator()
        phi_today = calc.phi(S=0.996)
        delta_phi = calc.delta_phi_cmb_today()  # ~1.71
    """

    def __init__(
        self,
        f0: float = 1.0,
        delta_s: float = 1.0,
        z_trans: float = 3.0,
        delta: float = 0.5
    ):
        """
        Initialize the phase calculator.

        Args:
            f0: Initial grid state value
            delta_s: Characteristic entropy scale
            z_trans: Transition redshift for S(z)
            delta: Sigmoid width for S(z)
        """
        self.f0 = f0
        self.delta_s = delta_s
        self.entropy_mapping = EntropyMapping(z_trans=z_trans, delta=delta)

    def phi(self, S: float) -> float:
        """Compute phase at entropy S."""
        return phi_of_S(S, self.f0, self.delta_s)

    def phi_at_z(self, z: float) -> float:
        """Compute phase at redshift z."""
        S = self.entropy_mapping.S(z)
        return self.phi(S)

    def delta_phi(self, z1: float, z2: float) -> float:
        """Compute phase difference Φ(z1) - Φ(z2)."""
        return self.phi_at_z(z1) - self.phi_at_z(z2)

    def delta_phi_cmb_today(self, z_cmb: float = 1100) -> float:
        """
        Compute standard phase difference from CMB to today.

        This is the key quantity: ΔΦ ≈ 1.71
        """
        return self.delta_phi(0, z_cmb)

    def result(self, S: float) -> PhaseResult:
        """Get full result for entropy S."""
        return PhaseResult(
            S=S,
            phi=self.phi(S),
            f0=self.f0,
            delta_s=self.delta_s,
        )

    def summary(self) -> str:
        """Get summary of calculator parameters."""
        delta_phi = self.delta_phi_cmb_today()
        return (
            f"Phase Calculator Φ(S)\n"
            f"{'=' * 30}\n"
            f"Parameters:\n"
            f"  f₀ = {self.f0}\n"
            f"  ΔS = {self.delta_s}\n"
            f"\n"
            f"Key values:\n"
            f"  Φ(S=0) = {self.phi(0):.4f}\n"
            f"  Φ(S=0.5) = {self.phi(0.5):.4f}\n"
            f"  Φ(S=1) = {self.phi(1):.4f}\n"
            f"  Φ(z=0) = {self.phi_at_z(0):.4f}\n"
            f"  Φ(z=1100) = {self.phi_at_z(1100):.6f}\n"
            f"  ΔΦ(CMB→today) = {delta_phi:.4f}\n"
        )


def create_standard_calculator() -> PhaseCalculator:
    """Create calculator with standard parameters."""
    return PhaseCalculator(f0=1.0, delta_s=1.0, z_trans=3.0, delta=0.5)
