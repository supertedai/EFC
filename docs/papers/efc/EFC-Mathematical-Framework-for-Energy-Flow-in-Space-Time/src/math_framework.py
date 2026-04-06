"""
EFC -- Mathematical Framework for Energy Flow in Space-Time

Core equations, field definitions, and relationships that formalise
how energy propagation and structure emerge in a thermodynamic spacetime.

Author: Morten Magnusson, ORCID 0009-0002-4860-5095
License: CC-BY-4.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Callable
import math


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BOLTZMANN_K: float = 1.380649e-23    # J/K
SPEED_OF_LIGHT: float = 2.998e8      # m/s
GRAVITATIONAL_G: float = 6.674e-11   # m^3 kg^-1 s^-2
DEFAULT_GRID_RESISTANCE: float = 0.01


@dataclass
class ScalarField:
    """
    Scalar field on a 1-D lattice (extendable to higher dimensions).

    Used for entropy density s(x), energy density rho(x), etc.
    """
    values: List[float] = field(default_factory=list)
    dx: float = 1.0
    label: str = "phi"

    def gradient(self) -> List[float]:
        """Central-difference gradient at interior points."""
        n = len(self.values)
        if n < 3:
            return []
        return [
            (self.values[i + 1] - self.values[i - 1]) / (2.0 * self.dx)
            for i in range(1, n - 1)
        ]

    def laplacian(self) -> List[float]:
        """Second derivative (1-D Laplacian) at interior points."""
        n = len(self.values)
        if n < 3:
            return []
        return [
            (self.values[i + 1] - 2.0 * self.values[i] + self.values[i - 1]) / (self.dx ** 2)
            for i in range(1, n - 1)
        ]

    def integral(self) -> float:
        """Trapezoidal integral over the field."""
        if len(self.values) < 2:
            return 0.0
        total = 0.0
        for i in range(len(self.values) - 1):
            total += 0.5 * (self.values[i] + self.values[i + 1]) * self.dx
        return total

    def norm_l2(self) -> float:
        """L2 norm of the field."""
        return math.sqrt(sum(v ** 2 for v in self.values) * self.dx)


@dataclass
class EnergyFlowEquation:
    """
    The core energy-flow equation:

        partial rho / partial t + div J = -R * rho + Q

    where rho is energy density, J is flux, R is grid resistance,
    and Q is a source term.
    """
    grid_resistance: float = DEFAULT_GRID_RESISTANCE
    source_strength: float = 0.0

    def rhs(self, rho: float, div_j: float) -> float:
        """Right-hand side: d(rho)/dt = -div J - R*rho + Q."""
        return -div_j - self.grid_resistance * rho + self.source_strength

    def steady_state_density(self, div_j: float = 0.0) -> float:
        """Steady-state density: rho_ss = Q / R  (when div J = 0)."""
        if self.grid_resistance <= 0:
            return float('inf') if self.source_strength > 0 else 0.0
        return (self.source_strength - div_j) / self.grid_resistance

    def characteristic_time(self) -> float:
        """Damping time: tau = 1 / R."""
        if self.grid_resistance <= 0:
            return float('inf')
        return 1.0 / self.grid_resistance


@dataclass
class EntropyFieldEquation:
    """
    Entropy field equation:

        ds/dt = sigma - div J_s

    where sigma >= 0 is the local entropy production rate (second law).
    """

    def production_rate(self, energy_flux: float, grad_T: float,
                        temperature: float) -> float:
        """
        Entropy production from Fourier-like heat flow:
            sigma = J * |nabla T| / T^2
        """
        if temperature <= 0:
            return 0.0
        return energy_flux * abs(grad_T) / (temperature ** 2)

    def is_second_law_satisfied(self, sigma: float) -> bool:
        """Check sigma >= 0 (local second law)."""
        return sigma >= 0.0


class GateFunction:
    """
    Gate function g(mu) that modulates gravitational response
    based on the local entropy-energy ratio mu.

    g(mu) = 1 + alpha * (1 - exp(-mu / mu_0))

    where alpha is the modification amplitude and mu_0 is the
    transition scale.
    """

    def __init__(self, alpha: float = 0.1, mu_0: float = 1.0):
        self.alpha = alpha
        self.mu_0 = mu_0

    def evaluate(self, mu: float) -> float:
        """Evaluate g(mu)."""
        return 1.0 + self.alpha * (1.0 - math.exp(-mu / self.mu_0))

    def derivative(self, mu: float) -> float:
        """dg/dmu = alpha / mu_0 * exp(-mu / mu_0)."""
        return (self.alpha / self.mu_0) * math.exp(-mu / self.mu_0)

    def limit_low_mu(self) -> float:
        """g(mu -> 0) = 1 (GR recovered)."""
        return 1.0

    def limit_high_mu(self) -> float:
        """g(mu -> inf) = 1 + alpha."""
        return 1.0 + self.alpha


class MathFrameworkModel:
    """
    Top-level mathematical framework for EFC.

    Combines scalar fields, energy-flow equation, entropy production,
    and the gate function into a unified computation tool.
    """

    PARAMETERS = {
        "k_B": BOLTZMANN_K,
        "c": SPEED_OF_LIGHT,
        "G": GRAVITATIONAL_G,
        "R_default": DEFAULT_GRID_RESISTANCE,
    }

    EQUATIONS = {
        "energy_flow": "d(rho)/dt + div J = -R*rho + Q",
        "entropy_production": "sigma = J * |nabla T| / T^2",
        "gate_function": "g(mu) = 1 + alpha * (1 - exp(-mu/mu_0))",
        "second_law": "sigma >= 0",
        "steady_state": "rho_ss = Q / R",
    }

    def __init__(self, grid_resistance: float = DEFAULT_GRID_RESISTANCE,
                 gate_alpha: float = 0.1, gate_mu0: float = 1.0):
        self.flow_eq = EnergyFlowEquation(grid_resistance=grid_resistance)
        self.entropy_eq = EntropyFieldEquation()
        self.gate = GateFunction(alpha=gate_alpha, mu_0=gate_mu0)

    def evolve_density(self, rho_initial: float, div_j: float,
                       n_steps: int, dt: float) -> List[Dict[str, float]]:
        """Euler integration of the energy-flow equation."""
        results = []
        rho = rho_initial
        for i in range(n_steps):
            drho = self.flow_eq.rhs(rho, div_j) * dt
            rho += drho
            results.append({
                "step": i,
                "rho": rho,
                "drho_dt": drho / dt,
            })
        return results

    def gate_profile(self, mu_values: List[float]) -> List[Dict[str, float]]:
        """Evaluate gate function over a range of mu values."""
        return [
            {"mu": mu, "g": self.gate.evaluate(mu), "dg": self.gate.derivative(mu)}
            for mu in mu_values
        ]

    def summary(self) -> str:
        lines = [
            "EFC: Mathematical Framework for Energy Flow in Space-Time",
            "=" * 60,
            f"Grid resistance (R):  {self.flow_eq.grid_resistance}",
            f"Gate alpha:           {self.gate.alpha}",
            f"Gate mu_0:            {self.gate.mu_0}",
            f"Damping time:         {self.flow_eq.characteristic_time():.2f}",
            f"g(0) = {self.gate.limit_low_mu():.3f}  "
            f"g(inf) = {self.gate.limit_high_mu():.3f}",
        ]
        return "\n".join(lines)
