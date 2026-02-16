"""
Three-sector discrete entropic functional and Euler-Lagrange equation.

    F[Φ] = Σ_{⟨i,j⟩} κ_ij F(|Φ_i − Φ_j|/a₀)       [gradient sector]
          + Σ_i ½ μ_Λ (Φ_i − Φ_V)²                  [bulk sector]
          + Σ_i λ_i ρ_i Φ_i                           [source sector]

Stationary configurations satisfy the Euler-Lagrange equation:
    Σ_{j~i} κ_ij μ(|Φ_i−Φ_j|/(a₀ a)) (Φ_j−Φ_i) − μ_Λ(Φ_i−Φ_V) = 4πGρ_i
"""

import math
from dataclasses import dataclass
from typing import List, Tuple

from .interpolating_function import mu, aqual_integrand


# Physical constants
G = 6.674e-11       # m³ kg⁻¹ s⁻²
FOUR_PI_G = 4.0 * math.pi * G


@dataclass
class SectorContribution:
    """Contribution of a single sector to the functional."""
    name: str
    value: float
    fraction: float


def gradient_sector(phi_i: float, phi_j: float, a0: float,
                    kappa: float = 1.0) -> float:
    """
    Gradient sector contribution for a single edge ⟨i,j⟩.

        F_grad = κ_ij * F(|Φ_i − Φ_j| / a₀)

    Parameters
    ----------
    phi_i : float
        Potential at node i.
    phi_j : float
        Potential at node j.
    a0 : float
        MOND acceleration scale (m/s²).
    kappa : float
        Edge weight (default 1.0).

    Returns
    -------
    float
        Gradient sector contribution for this edge.
    """
    x = abs(phi_i - phi_j) / a0
    return kappa * aqual_integrand(x)


def bulk_sector(phi_i: float, phi_v: float, mu_lambda: float) -> float:
    """
    Bulk sector contribution for a single node.

        F_bulk = ½ μ_Λ (Φ_i − Φ_V)²

    Parameters
    ----------
    phi_i : float
        Potential at node i.
    phi_v : float
        Volume-averaged background potential.
    mu_lambda : float
        Bulk coupling strength (proportional to Λ).

    Returns
    -------
    float
        Bulk sector contribution for this node.
    """
    return 0.5 * mu_lambda * (phi_i - phi_v) ** 2


def source_sector(phi_i: float, rho_i: float, lambda_i: float = 1.0) -> float:
    """
    Source sector contribution for a single node.

        F_source = λ_i ρ_i Φ_i

    Parameters
    ----------
    phi_i : float
        Potential at node i.
    rho_i : float
        Matter density at node i.
    lambda_i : float
        Coupling constant (default 1.0).

    Returns
    -------
    float
        Source sector contribution for this node.
    """
    return lambda_i * rho_i * phi_i


def sector_decomposition(phi_i: float, phi_j: float, phi_v: float,
                         rho_i: float, a0: float, mu_lambda: float,
                         kappa: float = 1.0) -> List[SectorContribution]:
    """
    Decompose the functional into sector contributions for a node-edge pair.

    Returns the gradient, bulk, and source contributions with their
    fractional shares of the total.

    Parameters
    ----------
    phi_i : float
        Potential at node i.
    phi_j : float
        Potential at representative neighbour j.
    phi_v : float
        Volume-averaged background potential.
    rho_i : float
        Matter density at node i.
    a0 : float
        MOND acceleration scale.
    mu_lambda : float
        Bulk coupling strength.
    kappa : float
        Edge weight.

    Returns
    -------
    list of SectorContribution
        Three contributions with name, value, and fraction.
    """
    f_grad = abs(gradient_sector(phi_i, phi_j, a0, kappa))
    f_bulk = abs(bulk_sector(phi_i, phi_v, mu_lambda))
    f_source = abs(source_sector(phi_i, rho_i))

    total = f_grad + f_bulk + f_source
    if total == 0:
        total = 1.0  # avoid division by zero

    return [
        SectorContribution("gradient", f_grad, f_grad / total),
        SectorContribution("bulk", f_bulk, f_bulk / total),
        SectorContribution("source", f_source, f_source / total),
    ]


def euler_lagrange_residual(phi_i: float, neighbours: List[Tuple[float, float]],
                            phi_v: float, rho_i: float, a0: float,
                            spacing: float, mu_lambda: float) -> float:
    """
    Compute the Euler-Lagrange residual at node i.

        R_i = Σ_{j~i} κ_ij μ(|Φ_i−Φ_j|/(a₀ a)) (Φ_j−Φ_i)
              − μ_Λ (Φ_i − Φ_V) − 4πGρ_i

    R_i = 0 at equilibrium.

    Parameters
    ----------
    phi_i : float
        Potential at node i.
    neighbours : list of (phi_j, kappa_ij) tuples
        Potentials and edge weights for neighbours of i.
    phi_v : float
        Volume-averaged background potential.
    rho_i : float
        Matter density at node i.
    a0 : float
        MOND acceleration scale.
    spacing : float
        Lattice spacing.
    mu_lambda : float
        Bulk coupling strength.

    Returns
    -------
    float
        Euler-Lagrange residual at node i.
    """
    gradient_sum = 0.0
    for phi_j, kappa_ij in neighbours:
        x = abs(phi_i - phi_j) / (a0 * spacing)
        mu_val = mu(x)
        gradient_sum += kappa_ij * mu_val * (phi_j - phi_i)

    bulk_term = mu_lambda * (phi_i - phi_v)
    source_term = FOUR_PI_G * rho_i

    return gradient_sum - bulk_term - source_term
