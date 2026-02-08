"""
EFC Closure Relations

Implements the conjectured closure relations:
    g† = c × H₀ / e
    C = 2e - 1
"""

import math
from dataclasses import dataclass
from typing import Optional

# Physical constants
c = 299792458  # Speed of light in m/s
e = math.e     # Euler's number

# Unit conversions
KM_S_MPC_TO_SI = 1e3 / 3.086e22  # km/s/Mpc to 1/s


@dataclass
class ClosureResult:
    """Result of closure relation computation."""
    g_dagger: float          # Transition acceleration (m/s²)
    C: float                 # Phase factor
    H0: float               # Hubble constant (km/s/Mpc)
    k: Optional[float]      # Screening exponent (if aG provided)
    delta_phi_cosmo: float  # Cosmological phase


def compute_g_dagger(H0: float) -> float:
    """
    Compute transition acceleration from H₀.

    g† = c × H₀ / e

    Args:
        H0: Hubble constant in km/s/Mpc

    Returns:
        Transition acceleration in m/s²

    Example:
        >>> compute_g_dagger(70.0)
        2.50e-10
    """
    H0_si = H0 * KM_S_MPC_TO_SI
    return c * H0_si / e


def compute_C() -> float:
    """
    Compute the phase factor.

    C = 2e - 1 ≈ 4.437

    Returns:
        Phase factor C
    """
    return 2 * e - 1


def predict_h0(g_dagger: float, g_dagger_error: Optional[float] = None) -> tuple[float, Optional[float]]:
    """
    Predict H₀ from measured g†.

    H₀ = e × g† / c

    Args:
        g_dagger: Transition acceleration in m/s²
        g_dagger_error: Uncertainty on g† (optional)

    Returns:
        Tuple of (H₀, H₀_error) in km/s/Mpc

    Example:
        >>> predict_h0(2.51e-10, 0.60e-10)
        (70.2, 16.8)
    """
    H0_si = e * g_dagger / c
    H0 = H0_si / KM_S_MPC_TO_SI

    if g_dagger_error is not None:
        # Error propagation (linear)
        H0_error = H0 * (g_dagger_error / g_dagger)
        return H0, H0_error

    return H0, None


def compute_k(aG: float) -> float:
    """
    Compute screening exponent from a_G.

    k = a_G × C = a_G × (2e - 1)

    Args:
        aG: Universal coupling coefficient

    Returns:
        Screening exponent k
    """
    return aG * compute_C()


def compute_delta_phi_cosmo(S_today: float = 1.0) -> float:
    """
    Compute cosmological phase difference.

    ΔΦ_cosmo ≈ e^S_today - 1

    Args:
        S_today: Entropy parameter today (default: 1.0)

    Returns:
        Cosmological phase difference
    """
    return math.exp(S_today) - 1


def full_closure(H0: float, aG: float = 0.094, S_today: float = 1.0) -> ClosureResult:
    """
    Compute all closure parameters.

    Args:
        H0: Hubble constant in km/s/Mpc
        aG: Universal coupling coefficient
        S_today: Entropy parameter today

    Returns:
        ClosureResult with all parameters
    """
    return ClosureResult(
        g_dagger=compute_g_dagger(H0),
        C=compute_C(),
        H0=H0,
        k=compute_k(aG),
        delta_phi_cosmo=compute_delta_phi_cosmo(S_today),
    )


class ClosureConjectures:
    """
    EFC closure conjectures calculator.

    Conjectures:
        1. g† = c × H₀ / e
        2. C = 2e - 1 ≈ 4.437

    Example:
        conj = ClosureConjectures()

        # From H₀
        g_dagger = conj.g_dagger_from_h0(70.0)

        # From SPARC g†
        H0, H0_err = conj.h0_from_sparc(2.51e-10, 0.60e-10)
    """

    def __init__(self, aG: float = 0.094):
        """Initialize with universal coupling."""
        self.aG = aG
        self.C = compute_C()
        self.k = compute_k(aG)

    def g_dagger_from_h0(self, H0: float) -> float:
        """Compute g† from H₀."""
        return compute_g_dagger(H0)

    def h0_from_sparc(
        self,
        g_dagger: float,
        g_dagger_error: Optional[float] = None
    ) -> tuple[float, Optional[float]]:
        """Predict H₀ from SPARC g†."""
        return predict_h0(g_dagger, g_dagger_error)

    def summary(self) -> str:
        """Get summary of conjectures."""
        return (
            f"EFC Closure Conjectures\n"
            f"{'=' * 40}\n"
            f"\n"
            f"Conjecture 1: g† = c × H₀ / e\n"
            f"  For H₀ = 67.4: g† = {compute_g_dagger(67.4):.2e} m/s²\n"
            f"  For H₀ = 70.2: g† = {compute_g_dagger(70.2):.2e} m/s²\n"
            f"  For H₀ = 73.0: g† = {compute_g_dagger(73.0):.2e} m/s²\n"
            f"\n"
            f"Conjecture 2: C = 2e - 1\n"
            f"  C = {self.C:.3f}\n"
            f"  k = a_G × C = {self.aG} × {self.C:.3f} = {self.k:.3f}\n"
            f"\n"
            f"Key prediction:\n"
            f"  H₀ = e × g† / c\n"
            f"  Using SPARC g† = 2.51e-10 m/s²:\n"
            f"  H₀ = {predict_h0(2.51e-10)[0]:.1f} km/s/Mpc\n"
        )
