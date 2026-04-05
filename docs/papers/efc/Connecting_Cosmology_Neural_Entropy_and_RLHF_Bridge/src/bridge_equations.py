"""EFC Cross-Domain Bridge Equations — Python implementation.

Implements:
  - Unified gradient-flow dynamics (Eq. 2): dF/dt = -integral |nabla s_dot|^2 dV + B
  - Bridge B1: Cosmology -> Neural (Eq. 5, 7)
  - Bridge B1** (revised): eta = C_eff / D_ratio^gamma (degree heterogeneity)
  - Bridge B2: Neural -> RLHF (Eq. 10-11, 13-14)
  - Three cross-domain predictions (P4**, P5, P6)

Reference: Magnusson (2026), DOI: 10.6084/m9.figshare.31940547
"""

import math
from dataclasses import dataclass, field
from typing import Optional


# ── EFC Spor 1 parameters ──────────────────────────────────────────
K_EFC = 0.415       # Screening exponent (Spor 1)
A_G = 0.094         # Gravitational coupling (Spor 1)
C_CROSS = K_EFC / A_G  # Cross-scale consistency: ~4.4


@dataclass
class UnifiedGradientFlow:
    """Unified dynamical postulate (Eq. 2).

    dF/dt = -integral_Omega |nabla s_dot|^2 dV + B[s_dot]
    Stability: dF/dt <= 0 when dissipation dominates boundary fluxes.
    """

    grad_s_dot_squared: list[float] = field(default_factory=list)
    boundary_flux: float = 0.0

    def volume_dissipation(self) -> float:
        """integral |nabla s_dot|^2 dV (discretised sum)."""
        return sum(self.grad_s_dot_squared)

    def dF_dt(self) -> float:
        """dF/dt = -dissipation + boundary flux."""
        return -self.volume_dissipation() + self.boundary_flux

    def is_stable(self) -> bool:
        """Lyapunov stability: dF/dt <= 0."""
        return self.dF_dt() <= 0

    def stability_margin(self) -> float:
        """How much dissipation exceeds boundary flux."""
        return self.volume_dissipation() - self.boundary_flux


@dataclass
class BridgeB1Cosmology2Neural:
    """Bridge B1: Cosmology -> Neural (Eq. 5).

    s_dot_i = alpha_N * g_eff_i * sigma_syn_i * Gamma_i

    where:
      g_eff_i = |nabla Phi_eff_i| / c_m^2  (dimensionless effective gradient)
      alpha_N = k / (a_G * L_cortex^3)      (neural coupling constant)
    """

    l_cortex: float = 0.1  # Cortical scale (m)
    k: float = K_EFC
    a_g: float = A_G

    @property
    def alpha_n(self) -> float:
        """Neural coupling constant alpha_N = k / (a_G * L^3)."""
        return self.k / (self.a_g * self.l_cortex ** 3)

    def effective_gradient(
        self,
        grad_phi_eff: float,
        c_m: float = 50.0,
    ) -> float:
        """g_eff_i = |nabla Phi_eff| / c_m^2 (Eq. 4)."""
        return grad_phi_eff / (c_m ** 2)

    def entropy_production_rate(
        self,
        g_eff: float,
        sigma_syn: float = 1.0,
        gamma_info: float = 1.0,
    ) -> float:
        """s_dot_i = alpha_N * g_eff * sigma_syn * Gamma (Eq. 5)."""
        return self.alpha_n * g_eff * sigma_syn * gamma_info


@dataclass
class BridgeB1StarStar:
    """Revised Bridge B1** (Eq. 7): degree-heterogeneity formulation.

    eta = C_eff / D_ratio^gamma

    where:
      D_ratio = <k_hub> / <k_periph>  (hub-to-periphery degree ratio)
      C_eff = kappa * k / a_G          (~1.9-2.2)
      gamma ~ 0.5-0.6                  (empirical)
    """

    k_hub_mean: float       # Mean degree of hub nodes (top 10%)
    k_periph_mean: float    # Mean degree of peripheral nodes (bottom 30%)
    kappa: float = 0.5      # Regime-transform factor
    gamma: float = 0.55     # Empirical exponent (0.5-0.6)
    k: float = K_EFC
    a_g: float = A_G

    @property
    def d_ratio(self) -> float:
        """Hub-to-periphery degree ratio (Eq. 8)."""
        if self.k_periph_mean <= 0:
            return float("inf")
        return self.k_hub_mean / self.k_periph_mean

    @property
    def c_eff(self) -> float:
        """Regime-transformed cross-scale constant C_eff = kappa * k / a_G."""
        return self.kappa * self.k / self.a_g

    def eta_predicted(self) -> float:
        """Predicted entropy-production ratio eta = C_eff / D_ratio^gamma (Eq. 7)."""
        dr = self.d_ratio
        if dr <= 0:
            return float("inf")
        return self.c_eff / (dr ** self.gamma)

    def limit_homogeneous(self) -> float:
        """Limit D_ratio -> 1: eta -> C_eff."""
        return self.c_eff

    def is_falsified(self, eta_obs: float, sigma: float, n_subjects: int = 20) -> dict:
        """Check falsification criterion: |eta_obs - eta_pred| / sigma > 3."""
        eta_pred = self.eta_predicted()
        z_score = abs(eta_obs - eta_pred) / sigma if sigma > 0 else float("inf")
        return {
            "eta_predicted": eta_pred,
            "eta_observed": eta_obs,
            "z_score": z_score,
            "n_subjects": n_subjects,
            "falsified": z_score > 3 and n_subjects >= 20,
        }


@dataclass
class BridgeB2Neural2RLHF:
    """Bridge B2: Neural -> RLHF (Eq. 10-14).

    Tensor:  nabla S_neural <-> nabla^2 R(s,a)   (Eq. 10)
    Scalar:  S_neural / (k_B * T_cog) <-> H(pi|s) (Eq. 11)
    Temperature: beta_KL <-> 1/T_cog               (Eq. 13)
    T_cog = S_neural_star / (k_B * I_net)          (Eq. 14)
    """

    s_neural_star: float   # Threshold entropy-production rate (from Spor 2)
    i_net: float           # Total integrated information (bits)
    k_b: float = 1.0      # Boltzmann constant (normalised)

    @property
    def t_cog(self) -> float:
        """Cognitive temperature T_cog = S*_neural / (k_B * I_net) (Eq. 14)."""
        if self.i_net <= 0:
            return float("inf")
        return self.s_neural_star / (self.k_b * self.i_net)

    @property
    def beta_kl_predicted(self) -> float:
        """Predicted optimal beta_KL = 1/T_cog (Eq. 13)."""
        t = self.t_cog
        if t <= 0:
            return float("inf")
        return 1.0 / t

    def neural_to_policy_entropy(self, s_neural: float) -> float:
        """Map S_neural -> H(pi|s) via scalar identification (Eq. 11)."""
        return s_neural / (self.k_b * self.t_cog)

    def validate_p5(self, beta_kl_observed: float, tolerance: float = 0.5) -> dict:
        """Test P5: does T_cog from fMRI predict optimal beta_KL?"""
        predicted = self.beta_kl_predicted
        deviation = abs(beta_kl_observed - predicted)
        return {
            "beta_kl_predicted": predicted,
            "beta_kl_observed": beta_kl_observed,
            "t_cog": self.t_cog,
            "deviation": deviation,
            "consistent": deviation <= tolerance * predicted,
        }


@dataclass
class CrossDomainPredictions:
    """Three cross-domain predictions from bridge equations (Table 2)."""

    @staticmethod
    def p4_star_star(
        k_hub_mean: float,
        k_periph_mean: float,
        kappa: float = 0.5,
        gamma: float = 0.55,
    ) -> dict:
        """P4**: eta from degree ratio, no free parameters."""
        b1 = BridgeB1StarStar(k_hub_mean, k_periph_mean, kappa, gamma)
        return {
            "prediction": "P4**",
            "d_ratio": b1.d_ratio,
            "c_eff": b1.c_eff,
            "eta_predicted": b1.eta_predicted(),
            "limit_homogeneous": b1.limit_homogeneous(),
            "test": "HCP SC + MSE; |r| > 0.40, p < 0.05",
            "falsification": "|r| < 0.30 on n >= 20, or |z| > 3",
        }

    @staticmethod
    def p5(s_neural_star: float, i_net: float) -> dict:
        """P5: T_cog calibrates beta_KL."""
        b2 = BridgeB2Neural2RLHF(s_neural_star, i_net)
        return {
            "prediction": "P5",
            "t_cog": b2.t_cog,
            "beta_kl_predicted": b2.beta_kl_predicted,
            "test": "Calibrate RLHF beta_KL from resting-state fMRI",
            "falsification": "Optimal beta_KL inconsistent with fMRI prediction",
        }

    @staticmethod
    def p6() -> dict:
        """P6: DMN topology <-> reward curvature."""
        return {
            "prediction": "P6",
            "mapping": "nabla S_neural <-> nabla^2 R(s,a)",
            "test": "fMRI nabla S_neural vs reward curvature in trained LLMs",
            "falsification": "Gradient topology uncorrelated with reward curvature",
        }


class ObservableDictionary:
    """Observable dictionary across three regimes (Table 1)."""

    TABLE = [
        {
            "quantity": "Entropy field",
            "cosmology": "s_dot(x,t)",
            "neural": "s_dot_i(V_i)",
            "rlhf": "-H(pi_theta|s)",
        },
        {
            "quantity": "Free energy F",
            "cosmology": "-ln(mu) * g_bar",
            "neural": "-T_cog * H(pi_net)",
            "rlhf": "<E> - beta_KL * H(pi_theta)",
        },
        {
            "quantity": "Temperature T",
            "cosmology": "g_dagger (transition)",
            "neural": "T_cog",
            "rlhf": "beta_KL",
        },
        {
            "quantity": "Gradient",
            "cosmology": "nabla s_dot (large-scale)",
            "neural": "nabla S_n (connectome)",
            "rlhf": "nabla^2 R (reward curvature)",
        },
        {
            "quantity": "Attractor",
            "cosmology": "Low-mu screening",
            "neural": "DMN-centrifugal",
            "rlhf": "Low-entropy policy",
        },
    ]

    @classmethod
    def print_table(cls) -> None:
        """Display the observable dictionary."""
        header = f"{'Quantity':>16s}  {'Cosmology':>25s}  {'Neural':>25s}  {'RLHF':>25s}"
        print(header)
        print("-" * len(header))
        for row in cls.TABLE:
            print(
                f"{row['quantity']:>16s}  {row['cosmology']:>25s}  "
                f"{row['neural']:>25s}  {row['rlhf']:>25s}"
            )
