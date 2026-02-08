"""
Entropy Mapping S(z)

The entropy parameter is defined as a sigmoid function of redshift,
motivated by structure formation dynamics (Cosmic Noon at z~3).
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class EntropyMappingParams:
    """Parameters for the entropy mapping."""
    z_trans: float = 3.0  # Transition redshift (Cosmic Noon)
    delta: float = 0.5    # Sigmoid width


def S_of_z(
    z: float,
    z_trans: float = 3.0,
    delta: float = 0.5
) -> float:
    """
    Compute entropy parameter S as function of redshift.

    S(z) = ½[1 - tanh((ln(1+z) - ln(1+z_trans))/Δ)]

    Args:
        z: Redshift
        z_trans: Transition redshift (default: 3, Cosmic Noon)
        delta: Sigmoid width (default: 0.5)

    Returns:
        Entropy parameter S in [0, 1]

    Examples:
        >>> S_of_z(0)      # Today
        0.996...
        >>> S_of_z(1100)   # CMB
        0.000...
    """
    if z < 0:
        raise ValueError(f"Redshift must be non-negative, got {z}")

    ln_ratio = (math.log(1 + z) - math.log(1 + z_trans)) / delta
    return 0.5 * (1 - math.tanh(ln_ratio))


class EntropyMapping:
    """
    Entropy mapping from redshift to entropy parameter.

    The sigmoid form is motivated by structure formation:
    - High S (near 1) at low redshift (today)
    - Low S (near 0) at high redshift (CMB)
    - Transition at z_trans ~ 3 (Cosmic Noon)

    Example:
        mapping = EntropyMapping(z_trans=3.0, delta=0.5)
        S_today = mapping.S(z=0)        # ~0.996
        S_cmb = mapping.S(z=1100)       # ~0
        delta_S = mapping.delta_S(0, 1100)  # ~0.996
    """

    def __init__(
        self,
        z_trans: float = 3.0,
        delta: float = 0.5
    ):
        """
        Initialize the entropy mapping.

        Args:
            z_trans: Transition redshift (Cosmic Noon)
            delta: Sigmoid width parameter
        """
        self.z_trans = z_trans
        self.delta = delta
        self.params = EntropyMappingParams(z_trans=z_trans, delta=delta)

    def S(self, z: float) -> float:
        """Compute S at redshift z."""
        return S_of_z(z, self.z_trans, self.delta)

    def delta_S(self, z1: float, z2: float) -> float:
        """Compute S(z1) - S(z2)."""
        return self.S(z1) - self.S(z2)

    def S_today(self) -> float:
        """S at z=0."""
        return self.S(0)

    def S_cmb(self, z_cmb: float = 1100) -> float:
        """S at CMB redshift."""
        return self.S(z_cmb)

    def evaluate_array(self, z_values: list[float]) -> list[float]:
        """Evaluate S for array of redshifts."""
        return [self.S(z) for z in z_values]

    def summary(self) -> str:
        """Get summary of mapping parameters and key values."""
        return (
            f"Entropy Mapping S(z)\n"
            f"{'=' * 30}\n"
            f"Parameters:\n"
            f"  z_trans = {self.z_trans}\n"
            f"  Δ = {self.delta}\n"
            f"\n"
            f"Key values:\n"
            f"  S(z=0) = {self.S_today():.4f}\n"
            f"  S(z=1) = {self.S(1):.4f}\n"
            f"  S(z=3) = {self.S(3):.4f}\n"
            f"  S(z=1100) = {self.S_cmb():.6f}\n"
            f"  ΔS(0→1100) = {self.delta_S(0, 1100):.4f}\n"
        )


def create_standard_mapping() -> EntropyMapping:
    """Create mapping with standard parameters (z_trans=3, Δ=0.5)."""
    return EntropyMapping(z_trans=3.0, delta=0.5)
