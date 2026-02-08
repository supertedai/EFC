"""
EFC Regime-Transition Model

Implements the EFC modification to the Friedmann equation:
    E²(z) → E²(z) × [1 + α_L2 × f(z) × Θ(z)]
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelResult:
    """Result of model evaluation."""
    z: float
    E2_LCDM: float
    E2_EFC: float
    modification: float
    theta: float


class EFCTransition:
    """
    EFC regime-transition model for cosmological expansion.

    Modifies the Friedmann equation:
        E²(z) → E²(z) × [1 + α_L2 × f(z) × Θ(z)]

    where:
        f(z) = (1+z)⁻¹
        Θ(z) = ½[1 + tanh((z_L1L2 - z)/Δz)]

    For α_L2 = 0, reduces exactly to ΛCDM.

    Example:
        model = EFCTransition(z_L1L2=1.01, alpha_L2=0.045)
        E2_ratio = model.E2_ratio(z=0.5)
    """

    def __init__(
        self,
        z_L1L2: float = 1.01,
        alpha_L2: float = 0.045,
        delta_z: float = 0.3,
        Omega_m: float = 0.3134,
        H0: float = 67.4
    ):
        """
        Initialize the model.

        Args:
            z_L1L2: Transition redshift
            alpha_L2: Energy flow coupling strength
            delta_z: Transition width
            Omega_m: Matter density parameter
            H0: Hubble constant in km/s/Mpc
        """
        self.z_L1L2 = z_L1L2
        self.alpha_L2 = alpha_L2
        self.delta_z = delta_z
        self.Omega_m = Omega_m
        self.Omega_L = 1 - Omega_m
        self.H0 = H0

    def f(self, z: float) -> float:
        """Coupling function f(z) = (1+z)⁻¹."""
        return 1 / (1 + z)

    def theta(self, z: float) -> float:
        """
        Smooth transition function.

        Θ(z) = ½[1 + tanh((z_L1L2 - z)/Δz)]

        Returns ~1 for z < z_L1L2, ~0 for z > z_L1L2.
        """
        arg = (self.z_L1L2 - z) / self.delta_z
        return 0.5 * (1 + math.tanh(arg))

    def E2_LCDM(self, z: float) -> float:
        """
        Standard ΛCDM normalized Hubble parameter squared.

        E²(z) = Ω_m(1+z)³ + Ω_Λ
        """
        return self.Omega_m * (1 + z)**3 + self.Omega_L

    def modification(self, z: float) -> float:
        """
        EFC modification factor.

        [1 + α_L2 × f(z) × Θ(z)]
        """
        return 1 + self.alpha_L2 * self.f(z) * self.theta(z)

    def E2_EFC(self, z: float) -> float:
        """
        EFC-modified E²(z).

        E²_EFC(z) = E²_ΛCDM(z) × [1 + α_L2 × f(z) × Θ(z)]
        """
        return self.E2_LCDM(z) * self.modification(z)

    def E2_ratio(self, z: float) -> float:
        """Ratio E²_EFC / E²_ΛCDM."""
        return self.modification(z)

    def H(self, z: float) -> float:
        """Hubble parameter H(z) in km/s/Mpc."""
        return self.H0 * math.sqrt(self.E2_EFC(z))

    def evaluate(self, z: float) -> ModelResult:
        """Full evaluation at redshift z."""
        return ModelResult(
            z=z,
            E2_LCDM=self.E2_LCDM(z),
            E2_EFC=self.E2_EFC(z),
            modification=self.modification(z),
            theta=self.theta(z),
        )

    def is_LCDM(self) -> bool:
        """Check if model reduces to ΛCDM."""
        return self.alpha_L2 == 0

    def summary(self) -> str:
        """Get model summary."""
        return (
            f"EFC Regime-Transition Model\n"
            f"{'=' * 40}\n"
            f"Parameters:\n"
            f"  z_L1L2 = {self.z_L1L2} (transition redshift)\n"
            f"  α_L2 = {self.alpha_L2} (coupling strength)\n"
            f"  Δz = {self.delta_z} (transition width)\n"
            f"\n"
            f"Cosmology:\n"
            f"  H₀ = {self.H0} km/s/Mpc\n"
            f"  Ω_m = {self.Omega_m}\n"
            f"\n"
            f"Model: E²(z) → E²(z) × [1 + α_L2 × f(z) × Θ(z)]\n"
            f"  where f(z) = (1+z)⁻¹\n"
            f"        Θ(z) = ½[1 + tanh((z_L1L2 - z)/Δz)]\n"
        )


def create_best_fit_model() -> EFCTransition:
    """Create model with DESI DR2 best-fit parameters."""
    return EFCTransition(z_L1L2=1.01, alpha_L2=0.045)


def create_LCDM_model() -> EFCTransition:
    """Create ΛCDM model (α_L2 = 0)."""
    return EFCTransition(z_L1L2=1.0, alpha_L2=0.0)
