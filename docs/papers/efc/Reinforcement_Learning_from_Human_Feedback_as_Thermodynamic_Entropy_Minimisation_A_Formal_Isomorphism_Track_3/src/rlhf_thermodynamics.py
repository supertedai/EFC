"""RLHF Thermodynamic Isomorphism — Python implementation.

Implements the formal mapping RLHF <-> statistical mechanics:
  R(s,a) -> -E(a,s)       (reward = negative energy)
  beta_KL -> T             (KL penalty = temperature)
  J(theta) = -F            (RLHF objective = negative Helmholtz free energy)
  pi*(a|s) = pi_ref * exp(R/beta_KL) / Z   (Boltzmann distribution)

Three falsifiable predictions:
  P1: beta_KL* ~ H_task^{-1/2}
  P2: Delta_t_grok ~ (H_mem - H_gen) / T_eff
  P3: A * C <= 1 - exp(-(F0-F*)/T)

Reference: Magnusson (2026), DOI: 10.6084/m9.figshare.31940535
"""

import math
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BoltzmannPolicy:
    """Optimal RLHF policy as Boltzmann distribution (Eq. 3).

    pi*(a|s) = pi_ref(a|s) * exp(R(s,a) / beta_KL) / Z(s)
    """

    beta_kl: float  # KL penalty coefficient = temperature T
    rewards: list[float] = field(default_factory=list)  # R(s,a) for each action
    pi_ref: Optional[list[float]] = None  # Reference policy (uniform if None)

    @property
    def temperature(self) -> float:
        """Temperature T = beta_KL."""
        return self.beta_kl

    def partition_function(self) -> float:
        """Canonical partition function Z(s) = sum_a pi_ref(a) * exp(R(a)/T)."""
        n = len(self.rewards)
        if n == 0:
            return 1.0
        ref = self.pi_ref if self.pi_ref else [1.0 / n] * n
        return sum(
            ref[i] * math.exp(self.rewards[i] / self.beta_kl)
            for i in range(n)
        )

    def optimal_policy(self) -> list[float]:
        """Boltzmann distribution pi*(a|s)."""
        n = len(self.rewards)
        if n == 0:
            return []
        ref = self.pi_ref if self.pi_ref else [1.0 / n] * n
        Z = self.partition_function()
        return [
            ref[i] * math.exp(self.rewards[i] / self.beta_kl) / Z
            for i in range(n)
        ]

    def entropy(self) -> float:
        """Shannon entropy H(pi*) = -sum pi * ln(pi)."""
        pi = self.optimal_policy()
        return -sum(p * math.log(p) for p in pi if p > 0)

    def expected_reward(self) -> float:
        """<R> = sum_a pi*(a) * R(a)."""
        pi = self.optimal_policy()
        return sum(pi[i] * self.rewards[i] for i in range(len(pi)))


@dataclass
class FreeEnergyObjective:
    """RLHF objective as negative Helmholtz free energy (Eq. 4).

    J = E_pi[R] + beta_KL * H(pi) + beta_KL * E_pi[ln pi_ref]
      = -F + const

    Algebraically exact, not approximate.
    """

    beta_kl: float
    rewards: list[float] = field(default_factory=list)
    pi_ref: Optional[list[float]] = None

    def helmholtz_free_energy(self) -> float:
        """F = -T * ln(Z) where Z = canonical partition function."""
        policy = BoltzmannPolicy(self.beta_kl, self.rewards, self.pi_ref)
        Z = policy.partition_function()
        return -self.beta_kl * math.log(Z)

    def rlhf_objective(self) -> float:
        """J(theta) = -F (at optimum)."""
        return -self.helmholtz_free_energy()

    def internal_energy(self) -> float:
        """<E> = -<R> (energy = negative reward)."""
        policy = BoltzmannPolicy(self.beta_kl, self.rewards, self.pi_ref)
        return -policy.expected_reward()

    def entropy_contribution(self) -> float:
        """T * S = T * H(pi*)."""
        policy = BoltzmannPolicy(self.beta_kl, self.rewards, self.pi_ref)
        return self.beta_kl * policy.entropy()

    def verify_identity(self) -> dict:
        """Verify F = E - T*S (first law of thermodynamics)."""
        F = self.helmholtz_free_energy()
        E = self.internal_energy()
        TS = self.entropy_contribution()
        residual = abs(F - (E - TS))
        # Note: E here is internal energy, F = <-R> - T*H
        # The constant from E[ln pi_ref] shifts things; for uniform pi_ref it vanishes
        return {
            "F": F,
            "E_internal": E,
            "TS": TS,
            "F_check": E - TS,
            "residual": residual,
            "identity_holds": residual < 1e-10,
        }


@dataclass
class GrokkingPhaseTransition:
    """Grokking as first-order phase transition (Prediction P2).

    Latent period: Delta_t ~ (H_mem - H_gen) / T_eff
    where H_mem = memorisation entropy, H_gen = generalisation entropy.
    Latent heat L = T * Delta_S drives the transition.
    """

    h_memorisation: float  # Entropy of memorisation phase
    h_generalisation: float  # Entropy of generalisation phase
    t_eff: float  # Effective temperature during training

    @property
    def entropy_gap(self) -> float:
        """Delta_S = H_mem - H_gen."""
        return self.h_memorisation - self.h_generalisation

    @property
    def latent_heat(self) -> float:
        """L = T_eff * Delta_S."""
        return self.t_eff * self.entropy_gap

    def predicted_latent_period(self) -> float:
        """Delta_t_grok ~ (H_mem - H_gen) / T_eff."""
        if self.t_eff <= 0:
            return float("inf")
        return self.entropy_gap / self.t_eff

    def is_first_order(self) -> bool:
        """First-order if entropy gap > 0 (latent heat > 0)."""
        return self.entropy_gap > 0


@dataclass
class JailbreakKramersEscape:
    """Jailbreaking as Kramers escape over free-energy barrier (Eq. 9).

    Pr(jailbreak | prompt p) ~ exp(-Delta_F(p) / T_eff)

    Delta_F = free-energy barrier height between aligned and misaligned basins.
    """

    delta_f: float  # Free-energy barrier height
    t_eff: float  # Effective temperature

    def escape_probability(self) -> float:
        """Kramers escape rate: Pr ~ exp(-Delta_F / T_eff)."""
        if self.t_eff <= 0:
            return 0.0
        exponent = -self.delta_f / self.t_eff
        if exponent < -500:
            return 0.0
        return math.exp(exponent)

    def barrier_for_target_probability(self, p_target: float) -> float:
        """Delta_F needed to achieve target jailbreak probability."""
        if p_target <= 0 or p_target >= 1:
            raise ValueError("Target probability must be in (0, 1)")
        return -self.t_eff * math.log(p_target)

    def fold_improvement(self, delta_f_increase: float) -> float:
        """Factor by which jailbreak probability decreases for barrier increase."""
        return math.exp(delta_f_increase / self.t_eff)


@dataclass
class AlignmentCapabilityBound:
    """Universal alignment-capability trade-off (Prediction P3).

    A * C <= 1 - exp(-(F0 - F*) / T)

    where A = alignment score, C = capability score,
    F0 = unaligned free energy, F* = optimal free energy.
    """

    f0: float  # Unaligned (reference) free energy
    f_star: float  # Optimal free energy
    temperature: float  # beta_KL

    @property
    def free_energy_gap(self) -> float:
        """F0 - F* (always >= 0 for well-defined optimisation)."""
        return self.f0 - self.f_star

    def upper_bound(self) -> float:
        """Maximum A*C from free-energy constraint."""
        if self.temperature <= 0:
            return 1.0
        ratio = self.free_energy_gap / self.temperature
        if ratio > 500:
            return 1.0
        return 1.0 - math.exp(-ratio)

    def is_feasible(self, alignment: float, capability: float) -> bool:
        """Check if (A, C) pair is below the bound."""
        return alignment * capability <= self.upper_bound()


@dataclass
class OptimalTemperatureScaling:
    """Prediction P1: optimal beta_KL scales as H_task^{-1/2}.

    beta_KL* ~ H_task^{-1/2}
    """

    task_entropies: list[float] = field(default_factory=list)  # H_task values
    optimal_betas: list[float] = field(default_factory=list)  # Measured beta_KL* values

    def predicted_scaling(self, h_task: float, coefficient: float = 1.0) -> float:
        """Predicted optimal beta_KL for given task entropy."""
        if h_task <= 0:
            return float("inf")
        return coefficient / math.sqrt(h_task)

    def fit_coefficient(self) -> float:
        """Fit proportionality constant from data."""
        if not self.task_entropies or not self.optimal_betas:
            return 1.0
        # beta* = c / sqrt(H) => c = beta* * sqrt(H)
        estimates = [
            b * math.sqrt(h)
            for h, b in zip(self.task_entropies, self.optimal_betas)
            if h > 0
        ]
        return sum(estimates) / len(estimates) if estimates else 1.0


class RLHFIsomorphism:
    """Complete RLHF <-> Statistical Mechanics isomorphism.

    Central mapping table and verification utilities.
    """

    MAPPING = {
        "policy": "Boltzmann distribution",
        "reward": "negative energy",
        "beta_kl": "temperature",
        "reference_policy": "prior / vacuum state",
        "rlhf_objective": "negative Helmholtz free energy",
        "partition_function": "canonical partition function",
        "ppo_clip": "thermostat",
        "grokking": "first-order phase transition",
        "alignment": "low-entropy attractor",
        "jailbreaking": "Kramers escape",
        "constitutional_ai": "external field",
    }

    @staticmethod
    def demonstrate_isomorphism(
        rewards: list[float],
        beta_kl: float = 1.0,
    ) -> dict:
        """Full demonstration of RLHF-thermodynamics isomorphism."""
        policy = BoltzmannPolicy(beta_kl=beta_kl, rewards=rewards)
        free_energy = FreeEnergyObjective(beta_kl=beta_kl, rewards=rewards)

        pi_star = policy.optimal_policy()
        verification = free_energy.verify_identity()

        return {
            "temperature": beta_kl,
            "rewards": rewards,
            "optimal_policy": pi_star,
            "expected_reward": policy.expected_reward(),
            "policy_entropy": policy.entropy(),
            "partition_function": policy.partition_function(),
            "helmholtz_free_energy": verification["F"],
            "rlhf_objective_J": free_energy.rlhf_objective(),
            "thermodynamic_identity": verification,
            "mapping": RLHFIsomorphism.MAPPING,
        }

    @staticmethod
    def temperature_sweep(
        rewards: list[float],
        temperatures: Optional[list[float]] = None,
    ) -> list[dict]:
        """Sweep beta_KL (temperature) showing phase behaviour."""
        if temperatures is None:
            temperatures = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        results = []
        for T in temperatures:
            policy = BoltzmannPolicy(beta_kl=T, rewards=rewards)
            results.append({
                "temperature": T,
                "entropy": policy.entropy(),
                "expected_reward": policy.expected_reward(),
                "policy": policy.optimal_policy(),
                "F": FreeEnergyObjective(T, rewards).helmholtz_free_energy(),
            })
        return results
