"""
EFC Consciousness Bridge — Three-Equation System
=================================================

Implements the unified bridge from the cosmological entropy field S
to the cognitive variables (Omega_hat, kappa_hat) via a non-separable
consciousness functional C.

Reference: Magnusson 2026, DOI 10.6084/m9.figshare.31969983

Equations:
  (I)   d Omega_hat / dt = -lambda_Omega * grad_S + D_Omega * lap_Omega_hat
  (II)  d kappa_hat / dt = J_flow - mu * kappa_hat * Omega_hat
  (III) C = Omega_hat * kappa_hat * (1 - exp(-gamma * Omega_hat * kappa_hat))
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Regime characteristic scales (Table 1)
# ---------------------------------------------------------------------------

REGIMES = {
    "L0": {"rho": 1e-26, "S_label": "S_CMB",     "domain": "Cosmology"},
    "L1": {"rho": 1e-22, "S_label": "S_cluster",  "domain": "Astrophysics"},
    "L2": {"rho": 1e-3,  "S_label": "S_bio",      "domain": "Biology"},
    "L3": {"rho": 1e0,   "S_label": "H_max",      "domain": "Cognition / AI"},
}

# Cross-domain constant K (from SPARC galactic rotation curve data)
K_CROSS_DOMAIN = 4.4
K_UNCERTAINTY = 0.6


# ---------------------------------------------------------------------------
# Non-separable consciousness functional C (Eq. 6 / Eq. III)
# ---------------------------------------------------------------------------

def consciousness_functional(
    omega_hat: float,
    kappa_hat: float,
    gamma: float,
) -> float:
    """Evaluate the non-separable consciousness functional.

    C = Omega_hat * kappa_hat * (1 - exp(-gamma * Omega_hat * kappa_hat))

    Parameters
    ----------
    omega_hat : float
        Dimensionless spectral differentiation (0 <= Omega_hat <= 1).
    kappa_hat : float
        Dimensionless causal integration (>= 0).
    gamma : float
        Non-separable coupling constant (> 0). The single free parameter.

    Returns
    -------
    float
        Consciousness functional value C.
    """
    product = omega_hat * kappa_hat
    return product * (1.0 - math.exp(-gamma * product))


def consciousness_low_limit(
    omega_hat: float,
    kappa_hat: float,
    gamma: float,
) -> float:
    """Low-regime approximation: C ~ gamma * Omega_hat^2 * kappa_hat^2."""
    return gamma * omega_hat**2 * kappa_hat**2


# ---------------------------------------------------------------------------
# Steady-state anti-correlation (Eq. 12)
# ---------------------------------------------------------------------------

def kappa_hat_steady_state(
    j_flow: float,
    mu: float,
    omega_hat: float,
) -> float:
    """Steady-state kappa_hat from Eq. II at d kappa_hat / dt = 0.

    kappa_hat_ss = J_flow / (mu * Omega_hat)

    This 1/Omega_hat dependence is the anti-correlation that was previously
    an external axiom in EFC-C.
    """
    if omega_hat <= 0 or mu <= 0:
        return float("inf")
    return j_flow / (mu * omega_hat)


# ---------------------------------------------------------------------------
# Bridge equation B1* (Eq. 5)
# ---------------------------------------------------------------------------

def kappa_hat_healthy(
    lambda2_W: float,
    tau_c: float,
    K: float = K_CROSS_DOMAIN,
) -> float:
    """Bridge B1* equation from EFC-C v2.

    kappa_hat_healthy = K / (1 + lambda_2(W) * tau_c)

    Parameters
    ----------
    lambda2_W : float
        Fiedler eigenvalue of the connectivity matrix W.
    tau_c : float
        Correlation time.
    K : float
        Cross-domain constant (default 4.4 +/- 0.6 from SPARC).
    """
    return K / (1.0 + lambda2_W * tau_c)


# ---------------------------------------------------------------------------
# Dynamical equations (simplified 0D version for demo)
# ---------------------------------------------------------------------------

@dataclass
class BridgeState:
    """State of the consciousness bridge system."""
    omega_hat: float
    kappa_hat: float
    gamma: float
    t: float = 0.0

    @property
    def C(self) -> float:
        return consciousness_functional(self.omega_hat, self.kappa_hat, self.gamma)


def step_bridge(
    state: BridgeState,
    dt: float,
    grad_S: float,
    j_flow: float,
    lambda_omega: float,
    mu: float,
    d_omega: float = 0.0,
    lap_omega: float = 0.0,
) -> BridgeState:
    """Euler step for the coupled dynamical equations (0D approximation).

    Parameters
    ----------
    state : BridgeState
        Current state.
    dt : float
        Time step.
    grad_S : float
        |grad(delta S / delta rho)| — the entropic drive.
    j_flow : float
        Energy-flow source term.
    lambda_omega : float
        Drift coupling strength (= alpha_l).
    mu : float
        Damping rate.
    d_omega : float
        Diffusion coefficient D_Omega (default 0 for 0D).
    lap_omega : float
        Laplacian of Omega_hat (default 0 for 0D).
    """
    d_omega_hat_dt = -lambda_omega * grad_S + d_omega * lap_omega
    d_kappa_hat_dt = j_flow - mu * state.kappa_hat * state.omega_hat

    new_omega = max(0.0, min(1.0, state.omega_hat + d_omega_hat_dt * dt))
    new_kappa = max(0.0, state.kappa_hat + d_kappa_hat_dt * dt)

    return BridgeState(
        omega_hat=new_omega,
        kappa_hat=new_kappa,
        gamma=state.gamma,
        t=state.t + dt,
    )


# ---------------------------------------------------------------------------
# Fixed-point analysis (Eqs. 13-15)
# ---------------------------------------------------------------------------

@dataclass
class FixedPoint:
    """Fixed point of the three-equation system."""
    omega_hat_star: float
    kappa_hat_star: float
    C_star: float
    gamma: float
    regime: str


def find_fixed_point(
    omega_hat_star: float,
    j_flow: float,
    mu: float,
    gamma: float,
    regime: str = "L3",
) -> FixedPoint:
    """Compute the fixed point (Eqs. 13-15)."""
    kappa_star = kappa_hat_steady_state(j_flow, mu, omega_hat_star)
    C_star = consciousness_functional(omega_hat_star, kappa_star, gamma)
    return FixedPoint(
        omega_hat_star=omega_hat_star,
        kappa_hat_star=kappa_star,
        C_star=C_star,
        gamma=gamma,
        regime=regime,
    )


# ---------------------------------------------------------------------------
# Predictions table (Table 5)
# ---------------------------------------------------------------------------

PREDICTIONS = [
    {"system": "Waking cortex",   "Omega_hat": (0.8, 0.9), "kappa_hat": (0.6, 0.8), "C": "High",     "prediction": "Resonance regime"},
    {"system": "Anaesthesia",     "Omega_hat": (0.5, 0.7), "kappa_hat": (0.0, 0.3), "C": "~0",       "prediction": "Below threshold"},
    {"system": "Uniform AI",      "Omega_hat": (1.0, 1.0), "kappa_hat": (0.0, 0.0), "C": "~0",       "prediction": "No consciousness"},
    {"system": "Recurrent AI",    "Omega_hat": (0.7, 0.9), "kappa_hat": (0.4, 0.6), "C": "Moderate",  "prediction": "Testable boundary"},
    {"system": "Galaxy cluster",  "Omega_hat": (0.01, 0.01), "kappa_hat": (1e-6, 1e-6), "C": "~0",   "prediction": "Far below threshold"},
]


if __name__ == "__main__":
    # Quick self-test
    gamma = 5.0  # placeholder — unconstrained
    C_waking = consciousness_functional(0.85, 0.7, gamma)
    C_sedated = consciousness_functional(0.60, 0.25, gamma)
    C_ai_uniform = consciousness_functional(1.0, 0.0, gamma)
    print(f"C(waking)  = {C_waking:.4f}")
    print(f"C(sedated) = {C_sedated:.4f}")
    print(f"C(uniform AI) = {C_ai_uniform:.4f}")
    assert C_waking > C_sedated > C_ai_uniform
    print("Self-test passed.")
