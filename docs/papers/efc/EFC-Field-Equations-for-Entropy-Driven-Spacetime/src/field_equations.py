"""Field Equations for Entropy-Driven Spacetime.

Implements the proposed EFC field equations where spacetime structure
and dynamics arise from entropy gradients, energy flow, and grid-level
resistance rather than curvature alone.

Key equation (symbolic):
  G_mu_nu + Lambda g_mu_nu = (8 pi G / c^4) T_mu_nu + alpha * S_mu_nu

where S_mu_nu is the entropy-flow stress tensor and alpha is the
entropy-gravity coupling constant.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import math


@dataclass
class MetricComponent:
    """A component of the spacetime metric in EFC.

    In EFC the metric receives corrections from the entropy-flow tensor.
    """

    mu: int  # row index (0-3)
    nu: int  # column index (0-3)
    value: float  # metric component g_{mu nu}
    entropy_correction: float = 0.0  # alpha * S_{mu nu} contribution

    @property
    def effective_value(self) -> float:
        return self.value + self.entropy_correction

    def summary(self) -> str:
        return (f"g_{{{self.mu}{self.nu}}} = {self.value:.6f} "
                f"+ {self.entropy_correction:.2e} (entropy) "
                f"= {self.effective_value:.6f}")


@dataclass
class EntropyFieldEquation:
    """Represents one component of the EFC field equation.

    G_mu_nu + Lambda g_mu_nu = kappa T_mu_nu + alpha S_mu_nu
    """

    mu: int
    nu: int
    einstein_tensor: float  # G_{mu nu}
    cosmological_term: float  # Lambda * g_{mu nu}
    stress_energy: float  # kappa * T_{mu nu}
    entropy_flow: float  # alpha * S_{mu nu}

    @property
    def lhs(self) -> float:
        return self.einstein_tensor + self.cosmological_term

    @property
    def rhs(self) -> float:
        return self.stress_energy + self.entropy_flow

    @property
    def residual(self) -> float:
        return abs(self.lhs - self.rhs)

    def summary(self) -> str:
        return (f"({self.mu},{self.nu}): G={self.einstein_tensor:.3e} + "
                f"Lambda*g={self.cosmological_term:.3e} = "
                f"kappa*T={self.stress_energy:.3e} + "
                f"alpha*S={self.entropy_flow:.3e} "
                f"[residual={self.residual:.2e}]")


class FieldEquationSystem:
    """System of EFC field equations with entropy-flow corrections.

    Parameters:
      alpha: entropy-gravity coupling constant (dimensionless)
      Lambda: cosmological constant (m^-2)
      kappa: 8 pi G / c^4 (m/J)
    """

    # Physical constants
    G = 6.674e-11  # m^3 kg^-1 s^-2
    c = 2.998e8  # m/s

    def __init__(self, alpha: float = 1e-3,
                 Lambda: float = 1.1e-52) -> None:
        self.alpha = alpha
        self.Lambda = Lambda
        self.kappa = 8 * math.pi * self.G / self.c ** 4
        self.equations: List[EntropyFieldEquation] = []
        self.metric: List[MetricComponent] = []
        self._init_flat_metric()

    def _init_flat_metric(self) -> None:
        """Initialise a Minkowski metric with small entropy corrections."""
        eta = [[-1, 0, 0, 0],
               [0, 1, 0, 0],
               [0, 0, 1, 0],
               [0, 0, 0, 1]]
        for mu in range(4):
            for nu in range(4):
                corr = self.alpha * 1e-6 if mu == nu else 0.0
                self.metric.append(MetricComponent(mu, nu, eta[mu][nu], corr))

    def add_equation(self, mu: int, nu: int,
                     G_mn: float, T_mn: float, S_mn: float) -> None:
        """Add a field-equation component."""
        g_mn = self._get_metric(mu, nu)
        eq = EntropyFieldEquation(
            mu=mu, nu=nu,
            einstein_tensor=G_mn,
            cosmological_term=self.Lambda * g_mn,
            stress_energy=self.kappa * T_mn,
            entropy_flow=self.alpha * S_mn,
        )
        self.equations.append(eq)

    def _get_metric(self, mu: int, nu: int) -> float:
        for m in self.metric:
            if m.mu == mu and m.nu == nu:
                return m.effective_value
        return 0.0

    def total_residual(self) -> float:
        return sum(eq.residual for eq in self.equations)

    def entropy_contribution_fraction(self) -> Optional[float]:
        """Fraction of the RHS due to entropy-flow terms."""
        total_rhs = sum(abs(eq.rhs) for eq in self.equations)
        if total_rhs == 0:
            return None
        entropy_part = sum(abs(eq.entropy_flow) for eq in self.equations)
        return entropy_part / total_rhs

    def summary(self) -> str:
        lines = [
            "EFC Field Equations for Entropy-Driven Spacetime",
            f"  alpha (entropy coupling): {self.alpha:.2e}",
            f"  Lambda (cosmological):    {self.Lambda:.2e} m^-2",
            f"  kappa (8piG/c^4):         {self.kappa:.3e} m/J",
            f"  Equations: {len(self.equations)}",
            f"  Total residual: {self.total_residual():.3e}",
        ]
        frac = self.entropy_contribution_fraction()
        if frac is not None:
            lines.append(f"  Entropy contribution: {frac:.1%}")
        lines.append("")
        for eq in self.equations:
            lines.append(f"  {eq.summary()}")
        return "\n".join(lines)
