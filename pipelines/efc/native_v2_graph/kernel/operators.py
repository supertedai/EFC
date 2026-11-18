"""
Discrete operators on graph: Laplacian, div, grad.

These are purely graph-theoretic — no continuum limit assumed.
"""
import numpy as np
from scipy.sparse import lil_matrix


def graph_laplacian(adjacency, degree, n_nodes):
    """
    Standard graph Laplacian: L = D - A.

    For a regular cubic grid with spacing h, ``L Phi`` approximates
    ``-h**2 * Laplacian(Phi)`` in the interior; the continuum-scaled
    Laplacian is ``-L / h**2``. The spacing is not embedded in this graph
    operator, so the field-equation source must carry matching ``h**2``.

    L[i,i] = degree[i]
    L[i,j] = -1 for j in adj[i]
    """
    L = lil_matrix((n_nodes, n_nodes))
    for i in range(n_nodes):
        L[i, i] = float(degree[i])
        for j in adjacency[i]:
            L[i, j] = -1.0
    return L


def weighted_laplacian(adjacency, weights_func, Phi, n_nodes, boundary,
                       gradient_vectors):
    """Conservative graph stencil with a full-vector face AQUAL coefficient.

    For edge ``i-j``, the normal field is represented by the potential
    difference, while the constitutive coefficient uses the norm of the
    symmetric face gradient ``0.5 * (grad_i + grad_j)``. The coefficient is
    therefore independent of edge orientation for a uniform linear field.

    ``weights_func`` receives the physical full-gradient magnitude at the face,
    not the magnitude of the single edge component.
    """
    Phi = np.asarray(Phi, dtype=float)
    gradient_vectors = np.asarray(gradient_vectors, dtype=float)
    boundary = np.asarray(boundary, dtype=bool)
    if Phi.shape != (n_nodes,):
        raise ValueError(f"Phi must have shape ({n_nodes},), got {Phi.shape}")
    if gradient_vectors.shape != (n_nodes, 3):
        raise ValueError(
            f"gradient_vectors must have shape ({n_nodes}, 3), "
            f"got {gradient_vectors.shape}"
        )
    if boundary.shape != (n_nodes,):
        raise ValueError(f"boundary must have shape ({n_nodes},), got {boundary.shape}")

    L = lil_matrix((n_nodes, n_nodes))
    for i in range(n_nodes):
        if boundary[i]:
            L[i, i] = 1.0
            continue
        diag = 0.0
        for j in adjacency[i]:
            grad_face = 0.5 * (gradient_vectors[i] + gradient_vectors[j])
            grad_norm = float(np.linalg.norm(grad_face))
            w = float(weights_func(grad_norm))
            L[i, j] = -w
            diag += w
        L[i, i] = diag
    return L


def gauss_flux_through_shell(positions, adjacency, Phi, gradient_vectors,
                             radius, spacing, weights_func):
    """Measure outward AQUAL flux across the graph cut at a spherical shell.

    Each undirected edge crossing ``|x| = radius`` is counted once from the
    inside node to the outside node. Its face flux is
    ``mu(|grad_face|/a0) * (Phi_out - Phi_in) / h * h**2``; with the standard
    potential convention this is positive for an attractive point source.
    """
    positions = np.asarray(positions, dtype=float)
    Phi = np.asarray(Phi, dtype=float)
    gradient_vectors = np.asarray(gradient_vectors, dtype=float)
    if Phi.shape != (len(positions),):
        raise ValueError("Phi length must match positions")
    if gradient_vectors.shape != positions.shape:
        raise ValueError("gradient_vectors shape must match positions")
    if radius <= 0 or spacing <= 0:
        raise ValueError("radius and spacing must be positive")

    inside = np.linalg.norm(positions, axis=1) < radius
    flux = 0.0
    for i, neighbours in enumerate(adjacency):
        if not inside[i]:
            continue
        for j in neighbours:
            if inside[j]:
                continue
            grad_face = 0.5 * (gradient_vectors[i] + gradient_vectors[j])
            weight = float(weights_func(float(np.linalg.norm(grad_face))))
            flux += weight * (Phi[j] - Phi[i]) * spacing
    return float(flux)


def discrete_gradient(positions, adjacency, Phi, spacing=None):
    """Return the signed physical gradient reconstructed from cubic neighbours.

    Opposing neighbours use the centered finite difference
    ``(Phi_plus - Phi_minus) / (2 h)``. At a mesh boundary, use the available
    one-sided difference. ``spacing`` may be supplied explicitly; otherwise
    infer the uniform edge length from the graph.

    Returns an ``(n, 3)`` gradient array and its ``(n,)`` Euclidean norm.
    This is grad(Phi), not gravitational acceleration; the solver applies the
    chosen sign convention separately.
    """
    positions = np.asarray(positions, dtype=float)
    Phi = np.asarray(Phi, dtype=float)
    n = len(positions)
    if Phi.shape != (n,):
        raise ValueError(f"Phi must have shape ({n},), got {Phi.shape}")

    if spacing is None:
        edge_lengths = [
            np.linalg.norm(positions[j] - positions[i])
            for i, neighbours in enumerate(adjacency)
            for j in neighbours
        ]
        if not edge_lengths:
            raise ValueError("cannot infer spacing from a graph without edges")
        spacing = float(np.median(edge_lengths))
    spacing = float(spacing)
    if not np.isfinite(spacing) or spacing <= 0.0:
        raise ValueError(f"spacing must be finite and positive, got {spacing}")

    gradient = np.zeros((n, 3), dtype=float)
    for i, neighbours in enumerate(adjacency):
        axis_values = {axis: {} for axis in range(3)}
        for j in neighbours:
            dr = positions[j] - positions[i]
            axes = np.flatnonzero(np.abs(dr) > 1e-12 * spacing)
            if len(axes) != 1:
                raise ValueError("discrete_gradient requires axis-aligned cubic edges")
            axis = int(axes[0])
            if not np.isclose(abs(dr[axis]), spacing, rtol=1e-10, atol=1e-12):
                raise ValueError("all cubic edges must match the declared spacing")
            side = 1 if dr[axis] > 0 else -1
            axis_values[axis][side] = Phi[j]

        for axis in range(3):
            neighbours_on_axis = axis_values[axis]
            if 1 in neighbours_on_axis and -1 in neighbours_on_axis:
                gradient[i, axis] = (
                    neighbours_on_axis[1] - neighbours_on_axis[-1]
                ) / (2.0 * spacing)
            elif 1 in neighbours_on_axis:
                gradient[i, axis] = (
                    neighbours_on_axis[1] - Phi[i]
                ) / spacing
            elif -1 in neighbours_on_axis:
                gradient[i, axis] = (
                    Phi[i] - neighbours_on_axis[-1]
                ) / spacing

    magnitude = np.linalg.norm(gradient, axis=1)
    return gradient, magnitude
