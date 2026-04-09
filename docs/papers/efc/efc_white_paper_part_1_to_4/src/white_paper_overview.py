"""
EFC White Paper Series — Overview utilities.

Provides quick access to the key equations and parameters
from all four parts of the White Paper series.
"""

import numpy as np


# --- Part 1: Recovery conditions ---

def theta_z(z, sigma_z=0.5):
    """Redshift window function (Eq. from Part 1)."""
    return np.exp(-z**2 / (2 * sigma_z**2))


def mu_recovery(k, z, beta=0.16, S=0.04, sigma_z=0.5):
    """Modified gravitational coupling with recovery limit."""
    return 1.0 + beta * S * theta_z(z, sigma_z)


# --- Part 2: Field equations ---

def entropy_field(a, S0=0.04, alpha=1.5, lam=0.01):
    """Entropy field S(a) (Eq. 1 of Part 2)."""
    return S0 * a**alpha * np.exp(-lam / a)


def mu_coupling(a, beta=0.16, S0=0.04, alpha=1.5, lam=0.01):
    """Gravitational coupling mu(a) = 1 + beta * S(a)."""
    S = entropy_field(a, S0, alpha, lam)
    return 1.0 + beta * S


# --- Part 3: Validation summary ---

VALIDATION_SUMMARY = {
    "total_tests": 102,
    "pass": 66,
    "partial": 5,
    "collapsed": 3,
    "failed": 17,
    "falsified_with_successor": 5,
    "kill_criteria": 5,
    "sealed_predictions": 2,
}


# --- Part 4: Regime susceptibility ---

def rho_eff(S):
    """Effective energy density rho_eff = S(1 - S)."""
    return S * (1.0 - S)


def susceptibility_T(S, S0=0.04):
    """Susceptibility function T(S) = S0(1-S0) / [S(1-S)]."""
    return S0 * (1.0 - S0) / (S * (1.0 - S))


def equation_of_state(a, beta_func=None, S0=0.04, alpha=1.5, lam=0.01):
    """Dynamical dark energy w(a) = -beta(S) * a."""
    S = entropy_field(a, S0, alpha, lam)
    beta_val = beta_func(S) if beta_func else 0.16
    return -beta_val * a
