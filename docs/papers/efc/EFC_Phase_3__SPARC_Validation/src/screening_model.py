"""
EFC Screening Model

Implements the EFC screening form for the radial acceleration relation:
    μ = (1 + g†/g_bar)^k
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScreeningResult:
    """Result of screening calculation."""
    g_bar: float          # Baryonic acceleration
    g_obs: float          # Observed acceleration
    mu: float             # Enhancement factor
    ln_mu: float          # Log enhancement
    delta_phi: float      # Phase accumulation


class EFCScreening:
    """
    EFC screening model for gravitational enhancement.

    The screening ansatz suppresses phase accumulation when baryonic
    gravity dominates, yielding:
        ΔΦ = C × ln(1 + g†/g_bar)
        μ = exp(a_G × ΔΦ) = (1 + g†/g_bar)^k
    where k = a_G × C.

    Example:
        model = EFCScreening(k=0.415, g_dagger=2.51e-10)
        mu = model.enhancement(g_bar=1e-10)
        print(f"μ = {mu:.3f}")
    """

    def __init__(
        self,
        k: float = 0.415,
        g_dagger: float = 2.51e-10,
        aG: Optional[float] = 0.094
    ):
        """
        Initialize screening model.

        Args:
            k: Screening exponent (default: 0.415 from SPARC fit)
            g_dagger: Transition scale in m/s² (default: 2.51e-10)
            aG: Universal coupling (default: 0.094 from H₀)
        """
        self.k = k
        self.g_dagger = g_dagger
        self.aG = aG

        # Derive C if aG provided
        self.C = k / aG if aG else None

    def enhancement(self, g_bar: float) -> float:
        """
        Compute gravitational enhancement μ.

        μ = (1 + g†/g_bar)^k

        Args:
            g_bar: Baryonic acceleration in m/s²

        Returns:
            Enhancement factor μ = g_obs/g_bar
        """
        if g_bar <= 0:
            raise ValueError("g_bar must be positive")

        return (1 + self.g_dagger / g_bar) ** self.k

    def ln_enhancement(self, g_bar: float) -> float:
        """
        Compute log enhancement ln(μ).

        ln(μ) = k × ln(1 + g†/g_bar)

        Args:
            g_bar: Baryonic acceleration in m/s²

        Returns:
            Log enhancement
        """
        if g_bar <= 0:
            raise ValueError("g_bar must be positive")

        return self.k * math.log(1 + self.g_dagger / g_bar)

    def g_obs(self, g_bar: float) -> float:
        """
        Compute observed acceleration.

        g_obs = μ × g_bar

        Args:
            g_bar: Baryonic acceleration

        Returns:
            Observed acceleration
        """
        return self.enhancement(g_bar) * g_bar

    def phase_accumulation(self, g_bar: float) -> float:
        """
        Compute phase accumulation ΔΦ.

        ΔΦ = C × ln(1 + g†/g_bar) = ln(μ) / a_G

        Args:
            g_bar: Baryonic acceleration

        Returns:
            Phase accumulation
        """
        if self.C is None:
            return self.ln_enhancement(g_bar) / self.aG if self.aG else 0
        return self.C * math.log(1 + self.g_dagger / g_bar)

    def compute(self, g_bar: float) -> ScreeningResult:
        """
        Compute full screening result.

        Args:
            g_bar: Baryonic acceleration

        Returns:
            ScreeningResult with all quantities
        """
        mu = self.enhancement(g_bar)
        return ScreeningResult(
            g_bar=g_bar,
            g_obs=mu * g_bar,
            mu=mu,
            ln_mu=math.log(mu),
            delta_phi=self.phase_accumulation(g_bar),
        )

    def evaluate_array(self, g_bar_values: list[float]) -> list[ScreeningResult]:
        """Evaluate for array of g_bar values."""
        return [self.compute(g) for g in g_bar_values]

    def summary(self) -> str:
        """Get model summary."""
        lines = [
            "EFC Screening Model",
            "=" * 40,
            f"Parameters:",
            f"  k = {self.k:.3f} (screening exponent)",
            f"  g† = {self.g_dagger:.2e} m/s²",
        ]

        if self.aG:
            lines.append(f"  a_G = {self.aG} (universal coupling)")
        if self.C:
            lines.append(f"  C = k/a_G = {self.C:.1f} (phase-gain)")

        lines.extend([
            "",
            "Screening form:",
            "  μ = (1 + g†/g_bar)^k",
            "  ln μ = k × ln(1 + g†/g_bar)",
        ])

        return "\n".join(lines)


def create_canonical_model() -> EFCScreening:
    """Create model with canonical SPARC fit parameters."""
    return EFCScreening(k=0.415, g_dagger=2.51e-10, aG=0.094)
