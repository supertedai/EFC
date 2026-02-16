"""
Linear and nonlinear solvers for field equations on graph.

Linear: standard Poisson via graph Laplacian
Nonlinear: AQUAL via Picard iteration on weighted Laplacian
"""
import numpy as np
from scipy.sparse.linalg import spsolve

from .graph import build_cubic_lattice, radial_distances, boundary_mask
from .fields import point_source_density, multi_source_density, boundary_potential
from .operators import graph_laplacian, weighted_laplacian, discrete_gradient
from .aqual import make_conductivity


def solve_linear_poisson(N, M, G_eff, spacing=1.0, r_source=2.0,
                         boundary_margin=1.5):
    """Solve standard linear Poisson on cubic lattice."""
    pos, adj, deg = build_cubic_lattice(N, spacing)
    n = N ** 3
    r_arr = radial_distances(pos)
    bnd = boundary_mask(pos, r_arr, boundary_margin, spacing)
    rhs = point_source_density(pos, r_arr, M, G_eff, r_source)

    L = graph_laplacian(adj, deg, n)
    L_csr = L.tocsr()

    rhs_bc = rhs.copy()
    for i in np.where(bnd)[0]:
        L_csr[i, :] = 0
        L_csr[i, i] = 1.0
        rhs_bc[i] = 0.0

    Phi = spsolve(L_csr, rhs_bc)
    g_vec, g_mag = discrete_gradient(pos, adj, Phi)

    return {
        'pos': pos, 'adj': adj, 'deg': deg,
        'r_arr': r_arr, 'boundary': bnd,
        'Phi': Phi, 'g_vec': g_vec, 'g_mag': g_mag,
        'rhs': rhs, 'N': N, 'converged': True, 'iterations': 1
    }


def solve_aqual(N, sources, G_eff, a0, r_source=2.0,
                spacing=1.0, max_iter=500, tol=1e-4,
                damping=0.3, boundary_margin=1.5,
                boundary_phi=None, mu_func=None, quiet=False):
    """
    Solve nonlinear AQUAL on cubic lattice via Picard iteration.

    sources: list of (position_3d, mass) tuples
             or single (mass,) for origin-centred point source
    boundary_phi: callable(pos) -> Phi at boundary, or None for Phi=0
    mu_func: MOND interpolation function, or None for standard
    """
    pos, adj, deg = build_cubic_lattice(N, spacing)
    n = N ** 3
    r_arr = radial_distances(pos)
    bnd = boundary_mask(pos, r_arr, boundary_margin, spacing)

    # Handle single-mass shorthand
    if isinstance(sources, (int, float)):
        sources = [([0, 0, 0], sources)]
    elif isinstance(sources, tuple) and len(sources) == 2:
        sources = [sources]

    rhs = multi_source_density(pos, sources, G_eff, r_source)
    phi_bc = boundary_potential(pos, bnd, boundary_phi)
    conductivity = make_conductivity(a0, spacing, mu_func)

    # Initial guess: linear Poisson
    L_lin = graph_laplacian(adj, deg, n)
    L_csr = L_lin.tocsr()
    rhs_bc = rhs.copy()
    for i in np.where(bnd)[0]:
        L_csr[i, :] = 0
        L_csr[i, i] = 1.0
        rhs_bc[i] = phi_bc[i]
    Phi = spsolve(L_csr, rhs_bc)

    # Picard iteration
    converged = False
    change = 1.0
    iteration = 0
    for iteration in range(max_iter):
        Phi_old = Phi.copy()

        L_w = weighted_laplacian(adj, conductivity, Phi, n, bnd)
        A_csr = L_w.tocsr()

        rhs_iter = rhs.copy()
        for i in np.where(bnd)[0]:
            rhs_iter[i] = phi_bc[i]

        Phi_new = spsolve(A_csr, rhs_iter)
        Phi = (1 - damping) * Phi_old + damping * Phi_new

        change = np.max(np.abs(Phi - Phi_old)) / (np.max(np.abs(Phi)) + 1e-10)
        if change < tol:
            converged = True
            break

    if not quiet:
        tag = "OK" if converged else f"NOT CONV ({change:.2e})"
        print(f"    {tag} in {iteration + 1} iters")

    g_vec, g_mag = discrete_gradient(pos, adj, Phi)

    return {
        'pos': pos, 'adj': adj, 'deg': deg,
        'r_arr': r_arr, 'boundary': bnd,
        'Phi': Phi, 'g_vec': g_vec, 'g_mag': g_mag,
        'rhs': rhs, 'N': N, 'a0': a0,
        'converged': converged, 'iterations': iteration + 1,
        'final_change': float(change)
    }
