'''homo_fluxus_a_thermodynamic_framework.py

Reference implementation for the paper:
Homo Fluxus: A Thermodynamic Framework for Consciousness, Systemic Empathy, and Aligned Intelligence
DOI: 10.6084/m9.figshare.32099389 (April 25, 2026)

Implements the paper's Eq. (1) at the cognitive/field scale:

  ∂S_local/∂t < 0  =>  E_f · ∇Φ_coh > 0

This module provides utilities to:
- compute local entropy rate ∂S/∂t from a time-indexed field S(t, ...)
- compute spatial gradient ∇Φ_coh of a scalar coherence potential field Φ_coh(x, ...)
- compute alignment E_f · ∇Φ_coh and evaluate the Eq. (1) implication as a mask
- summarize the fraction of a domain satisfying the inequality

Notes
- The paper treats Φ_coh as an operational quantity whose proxies must be observable; here we assume Φ_coh is given as a scalar field defined on a grid.
- No additional model assumptions beyond Eq. (1) are introduced; helper functions simply operationalize the inequality on discretized fields.

Author: Symbiose Research (per paper)
'''
from __future__ import annotations
from typing import Sequence, List, Tuple, Optional
import numpy as np

# Constants explicitly present in the paper text
PAPER_DOI: str = "10.6084/m9.figshare.32099389"
PAPER_DATE: str = "2026-04-25"
EQUATION_1: str = "dS_local/dt < 0 => E_f · ∇Φ_coh > 0"

__all__ = [
    "entropy_rate",
    "gradient_field",
    "dot_product_fields",
    "entropy_reduction_mask",
    "coherence_alignment_fraction",
    "evaluate_equation_1",
    "PAPER_DOI",
    "PAPER_DATE",
    "EQUATION_1",
]


def entropy_rate(S: np.ndarray, t: np.ndarray, axis: int = 0) -> np.ndarray:
    """Compute local entropy rate ∂S/∂t along a time axis using numpy.gradient.

    Parameters
    - S: ndarray of entropy values indexed along time 'axis'. Shape (T, ...)
    - t: 1D array of monotonically increasing time coordinates of length T
    - axis: index of the time dimension in S (default 0)

    Returns
    - ndarray of the same shape as S with the derivative along the time axis

    Requirements
    - Implements the left-hand side of Eq. (1): ∂S_local/∂t.
    """
    t = np.asarray(t)
    if t.ndim != 1:
        raise ValueError("t must be 1D array of time coordinates")
    if S.shape[axis] != t.size:
        raise ValueError("Length of t must match S.shape[axis]")
    # Use numpy.gradient with irregular spacing along the specified axis
    dS_dt = np.gradient(S, t, axis=axis, edge_order=2)
    return dS_dt


def gradient_field(phi: np.ndarray, coords: Sequence[np.ndarray]) -> List[np.ndarray]:
    """Compute spatial gradient ∇Φ_coh on a rectilinear grid.

    Parameters
    - phi: scalar field Φ_coh defined on an N-D grid, ndarray with shape (n0, n1, ...)
    - coords: sequence of 1D coordinate arrays for each axis (len == phi.ndim)

    Returns
    - list of ndarrays [∂phi/∂x0, ∂phi/∂x1, ...], each with shape phi.shape

    Notes
    - Implements the ∇Φ_coh term in Eq. (1).
    """
    if len(coords) != phi.ndim:
        raise ValueError("coords length must equal phi.ndim")
    # numpy.gradient expects spacing per axis; supply coords (can be 1D arrays)
    grads = np.gradient(phi, *coords, edge_order=2)
    # numpy.gradient returns list with component order matching axes of phi
    return [np.asarray(g) for g in grads]


def dot_product_fields(Ef_components: Sequence[np.ndarray],
                       grad_phi_components: Sequence[np.ndarray]) -> np.ndarray:
    """Compute E_f · ∇Φ_coh as a pointwise dot product of vector fields.

    Parameters
    - Ef_components: sequence [E0, E1, ...] of ndarray components of E_f
    - grad_phi_components: sequence [G0, G1, ...] corresponding components of ∇Φ_coh

    Returns
    - ndarray of the broadcasted sum over i of Ei * Gi, shape is broadcast of inputs

    Requirements
    - Implements the right-hand side inner product in Eq. (1): E_f · ∇Φ_coh.
    """
    if len(Ef_components) != len(grad_phi_components):
        raise ValueError("E_f and grad_phi must have same number of components")
    acc = None
    for Ei, Gi in zip(Ef_components, grad_phi_components):
        term = np.asarray(Ei) * np.asarray(Gi)
        acc = term if acc is None else acc + term
    return acc


def entropy_reduction_mask(dS_dt_local: np.ndarray,
                           Ef_dot_grad_phi: np.ndarray,
                           tol: float = 0.0) -> np.ndarray:
    """Evaluate Eq. (1) as a boolean mask over a domain.

    Returns True where both conditions hold:
    - dS_dt_local < -tol
    - Ef_dot_grad_phi > tol

    Parameters
    - dS_dt_local: ndarray of local entropy rates ∂S/∂t
    - Ef_dot_grad_phi: ndarray of E_f · ∇Φ_coh broadcastable to dS_dt_local
    - tol: non-negative tolerance for numerical robustness (default 0.0)

    Returns
    - boolean ndarray of the broadcasted shape
    """
    if tol < 0:
        raise ValueError("tol must be non-negative")
    dS_dt_b = np.asarray(dS_dt_local)
    E_dot_b = np.asarray(Ef_dot_grad_phi)
    return (dS_dt_b < -tol) & (E_dot_b > tol)


def coherence_alignment_fraction(mask: np.ndarray) -> float:
    """Compute the fraction of the domain satisfying Eq. (1).

    Parameters
    - mask: boolean ndarray from entropy_reduction_mask

    Returns
    - fraction in [0, 1]
    """
    mask = np.asarray(mask, dtype=bool)
    total = mask.size
    if total == 0:
        return float("nan")
    return float(mask.sum() / total)


def evaluate_equation_1(
    S: np.ndarray,
    t: np.ndarray,
    phi: np.ndarray,
    coords: Sequence[np.ndarray],
    Ef_components: Sequence[np.ndarray],
    time_axis: int = 0,
    tol: float = 0.0,
) -> Tuple[np.ndarray, float, np.ndarray]:
    """High-level helper to evaluate Eq. (1) on discretized fields.

    Parameters
    - S: entropy field over time and space, shape (T, ...)
    - t: 1D time coordinates of length T
    - phi: scalar coherence potential field over the spatial grid (time-invariant here)
    - coords: sequence of 1D coordinates for each spatial axis of phi
    - Ef_components: sequence of ndarray components of energy-flow vector field E_f
    - time_axis: which axis of S is time (default 0)
    - tol: numerical tolerance for inequality checks

    Returns
    - mask: boolean ndarray on the spatial grid for a representative time slice
    - frac: fraction of spatial points satisfying Eq. (1)
    - Ef_dot_grad_phi: ndarray of E_f · ∇Φ_coh on the grid

    Notes
    - For S, this computes ∂S/∂t and uses the central time slice when available.
    - If S has only one time slice, the time derivative is zero everywhere.
    """
    dS_dt = entropy_rate(S, t, axis=time_axis)
    # Select central time index to represent the local rate
    T = S.shape[time_axis]
    idx = T // 2
    slicer = [slice(None)] * S.ndim
    slicer[time_axis] = idx
    dS_dt_local = dS_dt[tuple(slicer)]

    grad = gradient_field(phi, coords)
    Ef_dot = dot_product_fields(Ef_components, grad)
    mask = entropy_reduction_mask(dS_dt_local, Ef_dot, tol=tol)
    frac = coherence_alignment_fraction(mask)
    return mask, frac, Ef_dot


if __name__ == "__main__":
    # Self-test: construct a scenario where Eq. (1) holds everywhere.
    nx, ny, T = 40, 40, 5
    x = np.linspace(0.0, 1.0, nx)
    y = np.linspace(0.0, 1.0, ny)
    X, Y = np.meshgrid(x, y, indexing='xy')

    # Define Φ_coh = X + Y (constant gradient [1, 1])
    phi = X + Y

    # Energy flow aligned with gradient: E = (1, 1)
    Ef_x = np.ones_like(phi)
    Ef_y = np.ones_like(phi)

    # Entropy decreases uniformly over time: S(t, x, y) = -a * t + const
    t = np.linspace(0.0, 1.0, T)
    a = 1.0
    S = np.empty((T, ny, nx))
    for i, ti in enumerate(t):
        S[i] = -a * ti + 0.5

    mask, frac, Ef_dot = evaluate_equation_1(
        S=S,
        t=t,
        phi=phi,
        coords=(x, y),
        Ef_components=(Ef_x, Ef_y),
        time_axis=0,
        tol=1e-8,
    )

    print("Paper DOI:", PAPER_DOI)
    print("Eq. (1):", EQUATION_1)
    print("Self-test: fraction of domain satisfying Eq. (1) =", frac)
    # Expect fraction ~ 1.0 and mask all True
    assert np.isclose(frac, 1.0), "Eq. (1) should hold everywhere in the self-test"
    assert mask.all(), "All points should satisfy Eq. (1) in the self-test"
    print("Self-test passed.")
