"""
Energy-Entropy Interrelation Module

Models the hypothesis that energy flow and entropy gradients are
interdependent components of a unified thermodynamic field.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class UnifiedField:
    """
    Unified thermodynamic field combining energy flow and entropy.

    The field state is described by the pair (Ef, S) with
    interdependence constraint: dEf/dS = -kappa * grad_S

    Attributes:
        ef_0: Initial energy flow density
        s_0: Initial entropy value
        kappa: Coupling constant between Ef and grad_S
    """
    ef_0: float
    s_0: float
    kappa: float

    def energy_flow(self, s: float) -> float:
        """
        Energy flow as function of entropy.

        Ef(S) = Ef_0 - kappa * (S - S_0)^2 / 2

        Args:
            s: Entropy value

        Returns:
            Energy flow density
        """
        return self.ef_0 - self.kappa * (s - self.s_0) ** 2 / 2.0

    def entropy_production_rate(self, s: float, grad_s: float) -> float:
        """
        Entropy production rate from the unified field.

        sigma_s = kappa * Ef(S) * grad_S^2

        Args:
            s: Entropy value
            grad_s: Entropy gradient

        Returns:
            Entropy production rate
        """
        ef = self.energy_flow(s)
        return self.kappa * ef * grad_s ** 2

    def information_bound(self, s: float, grad_s: float) -> float:
        """
        Information propagation bound from entropy production.

        v_info <= sqrt(sigma_s / kappa)

        Args:
            s: Entropy value
            grad_s: Entropy gradient

        Returns:
            Maximum information propagation speed
        """
        sigma_s = self.entropy_production_rate(s, grad_s)
        if sigma_s <= 0 or self.kappa <= 0:
            return 0.0
        return math.sqrt(sigma_s / self.kappa)


@dataclass
class InterrelationCoupling:
    """
    Coupling dynamics between energy and entropy fields.

    Attributes:
        kappa: Primary coupling constant
        mu: Secondary (nonlinear) coupling
    """
    kappa: float
    mu: float

    def coupling_strength(self, s: float) -> float:
        """
        Effective coupling strength at entropy S.

        K_eff(S) = kappa * (1 + mu * S)

        Args:
            s: Entropy value

        Returns:
            Effective coupling strength
        """
        return self.kappa * (1.0 + self.mu * s)

    def feedback_rate(self, ef: float, grad_s: float) -> float:
        """
        Rate at which energy flow feeds back into entropy.

        dS/dt ~ kappa * Ef * |grad_S|

        Args:
            ef: Energy flow density
            grad_s: Entropy gradient

        Returns:
            Feedback rate
        """
        return self.kappa * ef * abs(grad_s)

    def equilibrium_entropy(self, ef: float) -> float:
        """
        Entropy at which feedback balances dissipation.

        S_eq = ef / (kappa * (1 + mu))

        Args:
            ef: Energy flow density

        Returns:
            Equilibrium entropy
        """
        denom = self.kappa * (1.0 + self.mu)
        if denom <= 0:
            return float("inf")
        return ef / denom


class EnergyEntropyModel:
    """
    Complete model for energy-entropy interrelation.
    """

    def __init__(
        self,
        ef_0: float = 10.0,
        s_0: float = 1.0,
        kappa: float = 0.5,
        mu: float = 0.1,
    ):
        self.field = UnifiedField(ef_0=ef_0, s_0=s_0, kappa=kappa)
        self.coupling = InterrelationCoupling(kappa=kappa, mu=mu)
        self.ef_0 = ef_0
        self.s_0 = s_0

    def field_profile(self, s_values: List[float]) -> List[dict]:
        """
        Compute unified field profile over entropy range.

        Args:
            s_values: List of entropy values

        Returns:
            List of dicts with s, ef, coupling, eq_entropy
        """
        results = []
        for s in s_values:
            ef = self.field.energy_flow(s)
            k_eff = self.coupling.coupling_strength(s)
            s_eq = self.coupling.equilibrium_entropy(ef)
            results.append({
                "s": s,
                "ef": ef,
                "coupling": k_eff,
                "eq_entropy": s_eq,
            })
        return results

    def evolution_step(
        self, s: float, grad_s: float, dt: float = 0.01
    ) -> Tuple[float, float]:
        """
        Single time step of coupled evolution.

        dS/dt = feedback_rate
        dEf/dt = -kappa * grad_S * (dS/dt)

        Args:
            s: Current entropy
            grad_s: Current entropy gradient
            dt: Time step

        Returns:
            (new_s, new_ef) after one step
        """
        ef = self.field.energy_flow(s)
        ds_dt = self.coupling.feedback_rate(ef, grad_s)
        s_new = s + ds_dt * dt
        ef_new = self.field.energy_flow(s_new)
        return (s_new, ef_new)

    def evolve(
        self, s_init: float, grad_s: float, n_steps: int = 100, dt: float = 0.01
    ) -> List[dict]:
        """
        Evolve the coupled system over time.

        Args:
            s_init: Initial entropy
            grad_s: Entropy gradient (constant)
            n_steps: Number of time steps
            dt: Time step size

        Returns:
            Time series of (t, s, ef)
        """
        history = []
        s = s_init
        for i in range(n_steps):
            ef = self.field.energy_flow(s)
            history.append({"t": i * dt, "s": s, "ef": ef})
            s_new, _ = self.evolution_step(s, grad_s, dt)
            s = s_new
        return history

    def summary(self) -> str:
        """Return human-readable summary."""
        return (
            "Energy-Entropy Interrelation Model (EFC)\n"
            f"  Ef_0     = {self.ef_0}\n"
            f"  S_0      = {self.s_0}\n"
            f"  kappa    = {self.coupling.kappa}\n"
            f"  mu       = {self.coupling.mu}\n"
            f"  S_eq     = {self.coupling.equilibrium_entropy(self.ef_0):.4f}"
        )
