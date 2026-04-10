"""
EFC White Paper Part 4 — Regime Susceptibility and Cross-Scale Mapping.

Implements the susceptibility function T(S), effective energy density
rho_eff(S), equation of state w(a), and cross-scale amplification.

Reference: Magnusson (2026), doi:10.6084/m9.figshare.31970907
"""

import numpy as np


# --- Reference calibration ---
S_0 = 0.1       # SPARC galactic regime
BETA_0 = 0.16   # SPARC rotation curve coupling amplitude


def rho_eff(S: float) -> float:
    """Effective energy density (Eq. 3).

    rho_eff(S) = S(1 - S)
    Bernoulli variance form. Vanishes at both boundaries,
    maximum of 0.25 at S = 0.5.
    """
    return S * (1.0 - S)


def susceptibility_T(S: float, S_ref: float = S_0) -> float:
    """Regime susceptibility function (Eq. 6).

    T(S) = S_0(1 - S_0) / [S(1 - S)]
    Inverse of dynamical capacity.
    """
    if S <= 0 or S >= 1:
        return float("inf")
    return (S_ref * (1.0 - S_ref)) / (S * (1.0 - S))


def beta_scaled(S: float, beta_0: float = BETA_0) -> float:
    """Regime-scaled coupling amplitude (Eq. 7).

    beta(S) = beta_0 * T(S) = beta_0 * S_0(1-S_0) / [S(1-S)]
    """
    return beta_0 * susceptibility_T(S)


def self_regulation_product(S: float, beta_0: float = BETA_0) -> float:
    """Self-regulation product (Proposition 1, Eq. 8).

    beta(S) * rho_eff(S) = beta_0 * S_0(1-S_0) = const
    """
    return beta_scaled(S, beta_0) * rho_eff(S)


def equation_of_state(a: float, S: float) -> float:
    """Effective equation of state (Eq. 5).

    w(a) = p_eff / rho_eff = -beta(S) * a

    At a=1 (today): w_0 = -beta_cosm.
    """
    return -beta_scaled(S) * a


def amplification_ratio(S_gal: float = S_0, S_cosm: float = 0.9) -> float:
    """Cross-scale amplification ratio.

    beta_cosm / beta_gal = T(S_cosm) / T(S_gal)
    """
    return susceptibility_T(S_cosm) / susceptibility_T(S_gal)


def energy_flow_divergence(phase: str) -> dict:
    """Energy-flow current divergence interpretation (Eq. 1).

    Maps div(J^mu) sign to physical regime.
    """
    phases = {
        "DM": {"div_J": "< 0", "flow": "convergent", "effect": "excess gravity"},
        "equilibrium": {"div_J": "= 0", "flow": "equilibrium", "effect": "matter-dominated"},
        "DE": {"div_J": "> 0", "flow": "divergent", "effect": "accelerated expansion"},
    }
    return phases.get(phase, {})


def effective_pressure(div_J: float) -> float:
    """Effective pressure (Eq. 4).

    p_eff proportional to -div(J^mu)
    Convergent flow => positive pressure (structure resists)
    Divergent flow => negative pressure (system releases)
    """
    return -div_J
