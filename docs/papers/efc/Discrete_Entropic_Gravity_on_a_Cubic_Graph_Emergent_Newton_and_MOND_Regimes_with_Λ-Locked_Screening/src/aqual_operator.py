"""
Discrete AQUAL operator on a cubic graph.

Implements the interpolating function μ(x), AQUAL edge weights,
and the discrete field equation:

    Σ_{j~i} w_ij (Φ_j − Φ_i) = 4πGρ_i

where w_ij = μ(|Φ_i − Φ_j| / (a₀ · a)).
"""

import math
import numpy as np
from typing import Optional


def mu_interpolation(x: float) -> float:
    """
    Standard AQUAL interpolating function.

        μ(x) = x / √(1 + x²)

    Limits:
        x >> 1: μ → 1  (Newtonian regime)
        x << 1: μ → x  (deep-MOND regime)

    Parameters
    ----------
    x : float
        Dimensionless gradient ratio |∇Φ| / a₀.

    Returns
    -------
    float
        Value of μ(x).
    """
    return x / math.sqrt(1.0 + x * x)


def aqual_weight(phi_i: float, phi_j: float, a0: float, a: float) -> float:
    """
    Compute AQUAL edge weight between nodes i and j.

        w_ij = μ(|Φ_i − Φ_j| / (a₀ · a))

    Parameters
    ----------
    phi_i : float
        Potential at node i.
    phi_j : float
        Potential at node j.
    a0 : float
        MOND acceleration scale (in lattice units).
    a : float
        Lattice spacing.

    Returns
    -------
    float
        Edge weight w_ij.
    """
    grad = abs(phi_i - phi_j) / (a0 * a)
    return mu_interpolation(grad)


def discrete_gradient(phi_i: float, phi_j: float, a: float) -> float:
    """
    Discrete gradient magnitude between two adjacent nodes.

        |∇Φ|_ij = |Φ_i − Φ_j| / a

    Parameters
    ----------
    phi_i, phi_j : float
        Potentials at adjacent nodes.
    a : float
        Lattice spacing.

    Returns
    -------
    float
        Gradient magnitude.
    """
    return abs(phi_i - phi_j) / a


def deep_mond_prediction(a0: float, g_newton: float, C: float = 2.32) -> float:
    """
    Graph deep-MOND acceleration prediction.

        g_graph = C √(a₀ g_N)

    Standard MOND has C = 1. The cubic graph produces C ≈ 2.32.

    Parameters
    ----------
    a0 : float
        MOND acceleration scale.
    g_newton : float
        Newtonian gravitational acceleration.
    C : float
        Discrete renormalization prefactor (default 2.32).

    Returns
    -------
    float
        Deep-MOND regime acceleration on the graph.
    """
    return C * math.sqrt(a0 * g_newton)


def effective_a0(a0: float, C: float = 2.32) -> float:
    """
    Effective acceleration scale accounting for discrete renormalization.

        a₀,eff = C² · a₀

    Parameters
    ----------
    a0 : float
        Standard MOND acceleration scale.
    C : float
        Prefactor (default 2.32).

    Returns
    -------
    float
        Effective acceleration scale.
    """
    return C * C * a0
