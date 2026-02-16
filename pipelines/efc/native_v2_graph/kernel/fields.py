"""
Fields on the graph: Phi, S, rho, bulk reservoir.

All fields are defined on nodes. No continuum interpolation.
"""
import numpy as np


def point_source_density(positions, r_arr, M, G_eff, r_source=2.0,
                         source_center=None):
    """
    Create RHS for Poisson equation from a spherical source.

    4*pi*G*rho distributed uniformly within r < r_source.
    """
    n = len(positions)
    rhs = np.zeros(n)

    if source_center is None:
        dist = r_arr
    else:
        dist = np.linalg.norm(positions - np.array(source_center), axis=1)

    vol = (4.0 / 3.0) * np.pi * r_source ** 3
    mask = dist < r_source
    rhs[mask] = 4.0 * np.pi * G_eff * M / vol

    return rhs


def multi_source_density(positions, sources, G_eff, r_source=2.0):
    """
    Create RHS from multiple sources.

    sources: list of (position_3d, mass) tuples.
    """
    n = len(positions)
    rhs = np.zeros(n)
    vol = (4.0 / 3.0) * np.pi * r_source ** 3

    for src_pos, src_M in sources:
        src_pos = np.array(src_pos, dtype=float)
        dist = np.linalg.norm(positions - src_pos, axis=1)
        mask = dist < r_source
        rhs[mask] += 4.0 * np.pi * G_eff * src_M / vol

    return rhs


def boundary_potential(positions, boundary, phi_func=None):
    """
    Compute boundary Dirichlet values.

    phi_func: callable(pos_3d) -> scalar, or None for phi=0.
    """
    n = len(positions)
    phi_bc = np.zeros(n)

    if phi_func is not None:
        for i in np.where(boundary)[0]:
            phi_bc[i] = phi_func(positions[i])

    return phi_bc
