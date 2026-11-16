"""
Fields on the graph: Phi, S, rho, bulk reservoir.

All fields are defined on nodes. No continuum interpolation.
"""
import numpy as np


def point_source_density(positions, r_arr, M, r_source=2.0,
                         source_center=None, spacing=1.0):
    """Return a node-sampled uniform sphere with discrete mass exactly ``M``.

    The mass measure is equal cubic node-cell volume: ``sum(rho_i * h**3)``.
    Support uses the strict ``distance < r_source`` mask.
    """
    positions = np.asarray(positions, dtype=float)
    n = len(positions)
    if M <= 0 or spacing <= 0 or r_source <= 0:
        raise ValueError("M, spacing, and r_source must be positive")

    if source_center is None:
        dist = np.asarray(r_arr, dtype=float)
    else:
        dist = np.linalg.norm(positions - np.asarray(source_center, dtype=float), axis=1)

    mask = dist < r_source
    n_source = int(np.count_nonzero(mask))
    if n_source == 0:
        raise ValueError("source support contains no lattice nodes")

    rho = np.zeros(n, dtype=float)
    rho[mask] = M / (n_source * spacing ** 3)
    return rho


def multi_source_density(positions, sources, r_source=2.0, spacing=1.0):
    """Return the sum of individually mass-normalized node-sampled sources.

    Each source uses strict ``distance < r_source`` support and integrates to
    its declared mass under equal ``spacing**3`` node cells. Overlapping source
    supports add linearly.
    """
    positions = np.asarray(positions, dtype=float)
    n = len(positions)
    if spacing <= 0 or r_source <= 0:
        raise ValueError("spacing and r_source must be positive")

    rho = np.zeros(n, dtype=float)
    for src_pos, src_M in sources:
        if src_M <= 0:
            raise ValueError("source masses must be positive")
        src_pos = np.asarray(src_pos, dtype=float)
        dist = np.linalg.norm(positions - src_pos, axis=1)
        mask = dist < r_source
        n_source = int(np.count_nonzero(mask))
        if n_source == 0:
            raise ValueError("source support contains no lattice nodes")
        rho[mask] += src_M / (n_source * spacing ** 3)

    return rho


def active_source_mass(rho, boundary, spacing=1.0):
    """Return the source mass on non-boundary (active) rows.

    The solvers pin boundary rows to the Dirichlet value, so source support
    that lies on the boundary mask never enters the solved equation. Under the
    equal node-cell measure this is ``sum(rho[~boundary] * spacing**3)``.
    """
    rho = np.asarray(rho, dtype=float)
    boundary = np.asarray(boundary, dtype=bool)
    if rho.shape != boundary.shape:
        raise ValueError("rho and boundary must have the same shape")
    if spacing <= 0:
        raise ValueError("spacing must be positive")
    return float(np.sum(rho[~boundary]) * spacing ** 3)


def reject_source_on_boundary(rho, boundary):
    """Raise if any source node lies on the Dirichlet boundary mask.

    A source node on the boundary mask is pinned to the boundary value, so its
    mass is dropped from the solved equation and the declared ``sum rho h**3``
    would silently overstate the solved mass. Rejecting the configuration keeps
    the discrete mass measure honest; move the source centre inward or shrink
    its support.
    """
    rho = np.asarray(rho, dtype=float)
    boundary = np.asarray(boundary, dtype=bool)
    if rho.shape != boundary.shape:
        raise ValueError("rho and boundary must have the same shape")
    overlap = int(np.count_nonzero((rho > 0) & boundary))
    if overlap:
        raise ValueError(
            f"{overlap} source node(s) overlap the Dirichlet boundary mask; "
            "the solver pins those rows to the boundary value and would drop "
            "their mass from the solved equation. Move the source centre "
            "inward or shrink r_source."
        )


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
