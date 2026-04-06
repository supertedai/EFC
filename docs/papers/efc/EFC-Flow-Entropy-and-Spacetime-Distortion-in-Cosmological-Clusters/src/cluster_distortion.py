"""
Cluster Distortion Module

Models how energy flow (Ef), entropy gradients, and grid-level
resistance produce spacetime distortions in cosmological clusters.
"""

import math
from dataclasses import dataclass
from typing import List


@dataclass
class EntropyGradient:
    """
    Entropy gradient field in a cluster environment.

    Attributes:
        s_center: Central entropy value
        grad_s: Entropy gradient magnitude (per Mpc)
        scale_radius: Characteristic scale radius (Mpc)
    """
    s_center: float
    grad_s: float
    scale_radius: float

    def profile(self, r: float) -> float:
        """
        Compute entropy at radial distance r.

        S(r) = S_center + grad_s * scale_radius * (1 - exp(-r / scale_radius))

        Args:
            r: Radial distance from cluster centre (Mpc)

        Returns:
            Entropy value at radius r
        """
        return self.s_center + self.grad_s * self.scale_radius * (
            1.0 - math.exp(-r / self.scale_radius)
        )

    def gradient_at(self, r: float) -> float:
        """
        Compute dS/dr at radial distance r.

        Args:
            r: Radial distance (Mpc)

        Returns:
            Local entropy gradient
        """
        return self.grad_s * math.exp(-r / self.scale_radius)


@dataclass
class EnergyFlowField:
    """
    Energy flow field Ef in a cluster.

    Attributes:
        ef_0: Central energy flow density
        decay_length: Characteristic decay length (Mpc)
    """
    ef_0: float
    decay_length: float

    def density(self, r: float) -> float:
        """
        Energy flow density at radius r.

        Ef(r) = Ef_0 * exp(-r / decay_length)

        Args:
            r: Radial distance (Mpc)

        Returns:
            Energy flow density
        """
        return self.ef_0 * math.exp(-r / self.decay_length)


class LensingProfile:
    """
    Gravitational lensing profile from entropy-driven distortion.

    Computes the deflection angle from the entropy gradient
    and energy flow field without requiring dark matter.
    """

    def __init__(
        self,
        entropy: EntropyGradient,
        flow: EnergyFlowField,
        coupling: float = 1.0,
    ):
        """
        Args:
            entropy: Entropy gradient field
            flow: Energy flow field
            coupling: Coupling constant between entropy gradient and distortion
        """
        self.entropy = entropy
        self.flow = flow
        self.coupling = coupling

    def deflection_angle(self, r: float) -> float:
        """
        Compute deflection angle at impact parameter r.

        alpha(r) = coupling * grad_S(r) * Ef(r) / r

        Args:
            r: Impact parameter (Mpc), must be > 0

        Returns:
            Deflection angle (radians)
        """
        if r <= 0:
            raise ValueError("Impact parameter must be positive")
        grad_s = self.entropy.gradient_at(r)
        ef = self.flow.density(r)
        return self.coupling * grad_s * ef / r

    def convergence(self, r: float, dr: float = 0.001) -> float:
        """
        Compute convergence kappa from the deflection profile.

        kappa ~ (1/2) * d(r * alpha) / (r * dr)

        Args:
            r: Radial distance (Mpc)
            dr: Numerical step size

        Returns:
            Convergence value
        """
        alpha_plus = self.deflection_angle(r + dr)
        alpha_minus = self.deflection_angle(max(r - dr, dr))
        d_r_alpha = ((r + dr) * alpha_plus - max(r - dr, dr) * alpha_minus) / (2 * dr)
        return 0.5 * d_r_alpha / r


class ClusterDistortion:
    """
    Full cluster distortion model combining entropy gradients,
    energy flow, and spacetime curvature effects.
    """

    def __init__(
        self,
        entropy: EntropyGradient,
        flow: EnergyFlowField,
        coupling: float = 1.0,
    ):
        self.entropy = entropy
        self.flow = flow
        self.coupling = coupling
        self.lensing = LensingProfile(entropy, flow, coupling)

    def temperature_asymmetry(self, r: float) -> float:
        """
        Compute temperature asymmetry factor at radius r.

        Delta_T / T ~ grad_S(r) * Ef(r)

        Args:
            r: Radial distance (Mpc)

        Returns:
            Relative temperature asymmetry
        """
        return self.entropy.gradient_at(r) * self.flow.density(r)

    def distortion_profile(
        self, r_values: List[float]
    ) -> List[dict]:
        """
        Compute full distortion profile at multiple radii.

        Args:
            r_values: List of radial distances (Mpc)

        Returns:
            List of dicts with r, entropy, flow, deflection, temp_asymmetry
        """
        results = []
        for r in r_values:
            if r <= 0:
                continue
            results.append({
                "r": r,
                "entropy": self.entropy.profile(r),
                "flow": self.flow.density(r),
                "deflection": self.lensing.deflection_angle(r),
                "temp_asymmetry": self.temperature_asymmetry(r),
            })
        return results

    def summary(self) -> str:
        """Return human-readable summary of the model."""
        return (
            "Cluster Distortion Model (EFC)\n"
            f"  S_center = {self.entropy.s_center}\n"
            f"  grad_S   = {self.entropy.grad_s}\n"
            f"  scale_r  = {self.entropy.scale_radius} Mpc\n"
            f"  Ef_0     = {self.flow.ef_0}\n"
            f"  decay_l  = {self.flow.decay_length} Mpc\n"
            f"  coupling = {self.coupling}"
        )
