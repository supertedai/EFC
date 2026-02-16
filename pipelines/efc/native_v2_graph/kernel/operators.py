"""
Discrete operators on graph: Laplacian, div, grad.

These are purely graph-theoretic — no continuum limit assumed.
"""
import numpy as np
from scipy.sparse import lil_matrix


def graph_laplacian(adjacency, degree, n_nodes):
    """
    Standard graph Laplacian: L = D - A.

    L[i,i] = degree[i]
    L[i,j] = -1 for j in adj[i]
    """
    L = lil_matrix((n_nodes, n_nodes))
    for i in range(n_nodes):
        L[i, i] = float(degree[i])
        for j in adjacency[i]:
            L[i, j] = -1.0
    return L


def weighted_laplacian(adjacency, weights_func, Phi, n_nodes, boundary):
    """
    Nonlinear weighted Laplacian for AQUAL.

    L_w[i,j] = -w(|Phi_i - Phi_j|) for neighbours
    L_w[i,i] = sum of weights

    weights_func: callable(dPhi) -> weight (the conductivity/mu)
    """
    L = lil_matrix((n_nodes, n_nodes))
    for i in range(n_nodes):
        if boundary[i]:
            L[i, i] = 1.0
            continue
        diag = 0.0
        for j in adjacency[i]:
            dPhi = abs(Phi[i] - Phi[j])
            w = weights_func(dPhi)
            L[i, j] = -w
            diag += w
        L[i, i] = diag
    return L


def discrete_gradient(positions, adjacency, Phi):
    """
    Compute gradient vector at each node via neighbour differences.

    Returns (n, 3) gradient vectors and (n,) magnitudes.
    """
    n = len(positions)
    g_vec = np.zeros((n, 3))

    for i in range(n):
        gv = np.zeros(3)
        for j in adjacency[i]:
            dr = positions[j] - positions[i]
            dist = np.linalg.norm(dr)
            dPhi = Phi[i] - Phi[j]
            if dist > 0:
                gv += dPhi * dr / dist ** 2
        g_vec[i] = gv

    g_mag = np.linalg.norm(g_vec, axis=1)
    return g_vec, g_mag
