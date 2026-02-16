"""
Energy functional: F = F_grad + F_source + F_bulk + F_AQUAL(Phi).

The functional whose variation gives the field equation.
This module computes the energy contributions for diagnostics.
"""
import numpy as np


def F_grad(Phi, adjacency, n_nodes):
    """
    Gradient energy: F_grad = (1/2) sum_{<ij>} (Phi_i - Phi_j)^2

    This is the standard elastic/Poisson term.
    """
    E = 0.0
    for i in range(n_nodes):
        for j in adjacency[i]:
            if j > i:  # count each edge once
                E += 0.5 * (Phi[i] - Phi[j]) ** 2
    return E


def F_source(Phi, rhs, n_nodes):
    """
    Source coupling: F_source = -sum_i rho_i * Phi_i
    """
    return -np.dot(rhs[:n_nodes], Phi[:n_nodes])


def F_aqual(Phi, adjacency, a0, spacing, mu_integral, n_nodes):
    """
    AQUAL energy: F_AQUAL = a0^2 * sum_{<ij>} f(|dPhi|/(a0*h))

    where f(x) = integral of mu(t)*t dt from 0 to x
    and mu_integral is a callable: mu_integral(x) -> f(x)
    """
    E = 0.0
    for i in range(n_nodes):
        for j in adjacency[i]:
            if j > i:
                dPhi = abs(Phi[i] - Phi[j])
                x = dPhi / (a0 * spacing)
                E += a0 ** 2 * spacing ** 2 * mu_integral(x)
    return E


def mu_standard_integral(x):
    """
    Integral of mu(t)*t dt for standard MOND: mu(t) = t/sqrt(1+t^2).

    integral = (1/2) * [sqrt(1+x^2) - 1]
    (since d/dx[sqrt(1+x^2)] = x/sqrt(1+x^2) = mu(x))
    """
    return 0.5 * (np.sqrt(1.0 + x ** 2) - 1.0)


def total_energy(Phi, adjacency, rhs, a0, spacing, n_nodes):
    """Compute total energy functional."""
    Eg = F_grad(Phi, adjacency, n_nodes)
    Es = F_source(Phi, rhs, n_nodes)
    Ea = F_aqual(Phi, adjacency, a0, spacing, mu_standard_integral, n_nodes)
    return {'F_grad': Eg, 'F_source': Es, 'F_aqual': Ea,
            'F_total': Eg + Es + Ea}
