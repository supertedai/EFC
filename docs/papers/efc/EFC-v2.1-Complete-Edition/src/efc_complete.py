"""EFC v2.1 Complete Edition -- Python implementation.

Consolidated specification of Energy-Flow Cosmology: field equations,
entropy sigmoid, effective gravitational coupling, modified Friedmann
dynamics, and the complete regime architecture.

Reference: Magnusson (2025), EFC v2.1 Complete Edition
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

C_LIGHT = 2.998e8           # m/s
G_NEWTON = 6.674e-11        # m^3 kg^-1 s^-2
H0_PLANCK = 67.4            # km/s/Mpc (Planck 2018)
H0_SHOES = 73.0             # km/s/Mpc (SH0ES)


# ---------------------------------------------------------------------------
# Entropy Field
# ---------------------------------------------------------------------------

@dataclass
class EntropyField:
    """Entropy sigmoid S(a) = (S_inf/2)[1 + tanh((ln a - ln a_t)/sigma)].

    Attributes:
        S_inf: Asymptotic entropy (normalised).
        a_t: Transition scale factor.
        sigma: Transition width.
    """
    S_inf: float = 1.0
    a_t: float = 0.55
    sigma: float = 0.10

    def S(self, a: float) -> float:
        """Evaluate entropy field at scale factor a."""
        if a <= 0:
            return 0.0
        x = (math.log(a) - math.log(self.a_t)) / self.sigma
        return (self.S_inf / 2.0) * (1.0 + math.tanh(x))

    def dS_dlna(self, a: float) -> float:
        """Derivative dS/d(ln a) = (S_inf / 2sigma) * sech^2(...)."""
        if a <= 0:
            return 0.0
        x = (math.log(a) - math.log(self.a_t)) / self.sigma
        sech2 = 1.0 / (math.cosh(x) ** 2)
        return (self.S_inf / (2.0 * self.sigma)) * sech2

    def transition_redshift(self) -> float:
        """Redshift at the entropy transition: z_t = 1/a_t - 1."""
        return 1.0 / self.a_t - 1.0


# ---------------------------------------------------------------------------
# Effective Gravitational Coupling
# ---------------------------------------------------------------------------

@dataclass
class GravitationalCoupling:
    """mu(a) = G_eff/G = 1 + beta * S(a).

    Attributes:
        beta: EFC coupling constant.
        entropy: Entropy field instance.
    """
    beta: float = 0.16
    entropy: EntropyField = field(default_factory=EntropyField)

    def mu(self, a: float) -> float:
        """Effective gravitational coupling at scale factor a."""
        return 1.0 + self.beta * self.entropy.S(a)

    def G_eff(self, a: float) -> float:
        """Effective Newton constant G_eff = mu(a) * G."""
        return self.mu(a) * G_NEWTON

    def mu_today(self) -> float:
        """mu at a=1 (today)."""
        return self.mu(1.0)

    def mu_early(self) -> float:
        """mu at a << a_t (early universe, ~1)."""
        return self.mu(0.01)


# ---------------------------------------------------------------------------
# Modified Friedmann Equation
# ---------------------------------------------------------------------------

@dataclass
class ModifiedFriedmann:
    """EFC-modified Friedmann dynamics.

    H^2 = (8piG/3)(rho_m + rho_r + rho_Ef) + Lambda_eff/3
    where rho_Ef is the energy-flow contribution.
    """
    Omega_m: float = 0.315
    Omega_r: float = 9.0e-5
    Omega_Lambda: float = 0.685
    H0: float = 67.4  # km/s/Mpc
    coupling: GravitationalCoupling = field(default_factory=GravitationalCoupling)

    def H_squared_ratio(self, a: float) -> float:
        """(H(a)/H0)^2 including EFC modification.

        Standard: Omega_r/a^4 + Omega_m/a^3 + Omega_Lambda
        EFC adds: beta*S(a) correction to the matter term.
        """
        if a <= 0:
            return float('inf')
        mu = self.coupling.mu(a)
        matter = self.Omega_m * mu / (a ** 3)
        radiation = self.Omega_r / (a ** 4)
        dark_energy = self.Omega_Lambda
        return matter + radiation + dark_energy

    def H(self, a: float) -> float:
        """Hubble parameter H(a) in km/s/Mpc."""
        return self.H0 * math.sqrt(self.H_squared_ratio(a))

    def H_LCDM(self, a: float) -> float:
        """Standard LCDM Hubble parameter for comparison."""
        if a <= 0:
            return float('inf')
        return self.H0 * math.sqrt(
            self.Omega_r / a ** 4 + self.Omega_m / a ** 3 + self.Omega_Lambda
        )


# ---------------------------------------------------------------------------
# EFC Field Equation (symbolic description)
# ---------------------------------------------------------------------------

@dataclass
class EFCFieldEquation:
    """G_uv = 8piG (T_uv + T^(Ef)_uv) + Lambda_eff g_uv.

    Provides symbolic description and component access.
    """
    lhs: str = "G_{mu nu}"
    rhs_matter: str = "8 pi G T_{mu nu}"
    rhs_energy_flow: str = "8 pi G T^{(E_f)}_{mu nu}"
    rhs_cosmological: str = "Lambda_eff g_{mu nu}"

    def full_equation(self) -> str:
        return f"{self.lhs} = {self.rhs_matter} + {self.rhs_energy_flow} + {self.rhs_cosmological}"

    def components(self) -> Dict[str, str]:
        return {
            "Einstein_tensor": self.lhs,
            "matter_stress_energy": self.rhs_matter,
            "energy_flow_stress_energy": self.rhs_energy_flow,
            "effective_cosmological_constant": self.rhs_cosmological,
        }


# ---------------------------------------------------------------------------
# Complete Edition container
# ---------------------------------------------------------------------------

@dataclass
class EFCCompleteEdition:
    """Top-level container for EFC v2.1 Complete Edition."""
    version: str = "2.1"
    title: str = "EFC v2.1 Complete Edition"
    entropy: EntropyField = field(default_factory=EntropyField)
    coupling: GravitationalCoupling = field(default_factory=GravitationalCoupling)
    friedmann: ModifiedFriedmann = field(default_factory=ModifiedFriedmann)
    field_equation: EFCFieldEquation = field(default_factory=EFCFieldEquation)

    def summary(self) -> str:
        lines = [
            f"=== {self.title} ===",
            "",
            f"Field Equation: {self.field_equation.full_equation()}",
            "",
            f"Entropy field: S_inf={self.entropy.S_inf}, a_t={self.entropy.a_t}, "
            f"sigma={self.entropy.sigma}",
            f"  S(a=1) = {self.entropy.S(1.0):.4f}",
            f"  z_t = {self.entropy.transition_redshift():.2f}",
            "",
            f"Gravitational coupling: beta={self.coupling.beta}",
            f"  mu(a=1) = {self.coupling.mu_today():.4f}",
            f"  mu(a=0.01) = {self.coupling.mu_early():.6f}",
            "",
            f"Modified Friedmann: H0={self.friedmann.H0} km/s/Mpc",
            f"  H(a=1) EFC  = {self.friedmann.H(1.0):.2f} km/s/Mpc",
            f"  H(a=1) LCDM = {self.friedmann.H_LCDM(1.0):.2f} km/s/Mpc",
        ]
        return "\n".join(lines)

    def parameters(self) -> Dict[str, float]:
        return {
            "beta": self.coupling.beta,
            "a_t": self.entropy.a_t,
            "sigma": self.entropy.sigma,
            "S_inf": self.entropy.S_inf,
            "Omega_m": self.friedmann.Omega_m,
            "Omega_Lambda": self.friedmann.Omega_Lambda,
            "H0": self.friedmann.H0,
        }
