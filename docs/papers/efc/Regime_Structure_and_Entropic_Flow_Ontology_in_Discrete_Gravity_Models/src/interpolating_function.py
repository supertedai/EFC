"""
Standard interpolating function μ(x) and AQUAL kinetic integrand F(x).

    μ(x) = x / √(1 + x²)

Properties:
    x >> 1:  μ(x) → 1    (Newtonian regime)
    x << 1:  μ(x) ~ x    (MOND regime)
    x = 1:   μ(1) = 1/√2  (transition)

The AQUAL kinetic integrand:
    F(x) = ∫₀ˣ y μ(y) dy

References:
    Bekenstein & Milgrom (1984), ApJ 286, 7-14
"""

import math


def mu(x: float) -> float:
    """
    Standard interpolating function.

        μ(x) = x / √(1 + x²)

    Parameters
    ----------
    x : float
        Dimensionless argument |∇Φ|/a₀.

    Returns
    -------
    float
        Value of μ(x), between 0 and 1.
    """
    return x / math.sqrt(1.0 + x * x)


def mu_derivative(x: float) -> float:
    """
    Derivative of the interpolating function.

        dμ/dx = 1 / (1 + x²)^{3/2}

    Parameters
    ----------
    x : float
        Dimensionless argument.

    Returns
    -------
    float
        Value of dμ/dx.
    """
    return 1.0 / (1.0 + x * x) ** 1.5


def aqual_integrand(x: float) -> float:
    """
    AQUAL kinetic integrand F(x) = ∫₀ˣ y μ(y) dy.

    Closed-form: F(x) = √(1 + x²) − 1

    Parameters
    ----------
    x : float
        Upper integration limit (dimensionless).

    Returns
    -------
    float
        Value of F(x).
    """
    return math.sqrt(1.0 + x * x) - 1.0


def mu_table(x_values: list) -> list:
    """
    Compute μ(x) for a list of x values.

    Parameters
    ----------
    x_values : list of float
        Dimensionless arguments.

    Returns
    -------
    list of dict
        Each dict has keys 'x', 'mu', 'regime'.
    """
    results = []
    for x in x_values:
        if x > 10.0:
            regime = "Newtonian (μ → 1)"
        elif x < 0.1:
            regime = "MOND (μ ~ x)"
        else:
            regime = "Transition"
        results.append({
            "x": x,
            "mu": mu(x),
            "regime": regime
        })
    return results
