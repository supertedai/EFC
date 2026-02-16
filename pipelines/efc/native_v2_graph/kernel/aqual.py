"""
AQUAL flux: nonlinear Poisson on graph.

The field equation is:
    div( mu(|grad Phi| / a0) * grad Phi ) = 4*pi*G*rho

Discretized on graph via weighted Laplacian with Picard iteration.

KEY DESIGN CHOICE: Nonlinearity is on the potential Phi, NOT on S.
This is the AQUAL mechanism — flux conservation in the potential field.
"""
import numpy as np


def mu_standard(x):
    """
    Standard MOND interpolation function.

    mu(x) = x / sqrt(1 + x^2)

    Limits:
        x >> 1: mu -> 1 (Newton)
        x << 1: mu -> x (deep MOND)
    """
    return x / np.sqrt(1.0 + x ** 2)


def mu_simple(x):
    """
    Simple MOND interpolation function.

    mu(x) = x / (1 + x)

    Limits:
        x >> 1: mu -> 1 (Newton)
        x << 1: mu -> x (deep MOND)
    """
    return x / (1.0 + x)


def make_conductivity(a0, spacing, mu_func=None, floor=1e-6):
    """
    Create conductivity function for the weighted Laplacian.

    Returns callable: dPhi -> w = mu(|dPhi| / (a0 * h))
    """
    if mu_func is None:
        mu_func = mu_standard

    def conductivity(dPhi):
        x = dPhi / (a0 * spacing) if a0 > 0 else 1e10
        return max(mu_func(x), floor)

    return conductivity
