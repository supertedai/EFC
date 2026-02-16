"""
Graph primitives: nodes, edges, geometry, neighbours.

The graph is the fundamental object. Space is emergent from connectivity.
No continuum assumptions — everything is discrete from the start.
"""
import numpy as np


def build_cubic_lattice(N, spacing=1.0):
    """
    Build a 3D cubic lattice centered at origin.

    Returns:
        positions: (N^3, 3) array of node coordinates
        adjacency: list of lists, adjacency[i] = [j, k, ...] neighbours of node i
        degree: (N^3,) array of node degrees
    """
    n_nodes = N ** 3
    positions = np.zeros((n_nodes, 3))
    adjacency = [[] for _ in range(n_nodes)]

    def idx(x, y, z):
        return x * N * N + y * N + z

    for x in range(N):
        for y in range(N):
            for z in range(N):
                i = idx(x, y, z)
                positions[i] = [x * spacing, y * spacing, z * spacing]
                for dx, dy, dz in [(1, 0, 0), (-1, 0, 0),
                                   (0, 1, 0), (0, -1, 0),
                                   (0, 0, 1), (0, 0, -1)]:
                    nx_, ny_, nz_ = x + dx, y + dy, z + dz
                    if 0 <= nx_ < N and 0 <= ny_ < N and 0 <= nz_ < N:
                        j = idx(nx_, ny_, nz_)
                        adjacency[i].append(j)

    degree = np.array([len(adj) for adj in adjacency])
    center = (N - 1) * spacing / 2.0
    positions -= center

    return positions, adjacency, degree


def radial_distances(positions):
    """Compute radial distance from origin for each node."""
    return np.linalg.norm(positions, axis=1)


def boundary_mask(positions, r_arr=None, margin_factor=1.5, spacing=1.0):
    """
    Identify boundary nodes (outermost shell).

    These get Dirichlet conditions in the solver.
    """
    if r_arr is None:
        r_arr = radial_distances(positions)
    r_max = np.max(r_arr)
    return r_arr > (r_max - margin_factor * spacing)
