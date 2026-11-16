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


def make_conductivity(a0, spacing=1.0, mu_func=None, floor=1e-6):
    """Create an AQUAL face conductivity from a full physical gradient norm.

    The returned callable accepts ``|grad Phi|`` in acceleration units and
    evaluates ``mu(|grad Phi| / a0)``. ``spacing`` remains an accepted argument
    for call-site compatibility and is validated, but is not multiplied into a
    gradient that has already been reconstructed with physical units.
    """
    if a0 <= 0 or spacing <= 0:
        raise ValueError("a0 and spacing must be positive")
    if mu_func is None:
        mu_func = mu_standard

    def conductivity(gradient_magnitude):
        gradient_magnitude = float(gradient_magnitude)
        x = gradient_magnitude / a0
        return max(float(mu_func(x)), floor)

    return conductivity
