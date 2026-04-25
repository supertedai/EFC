from __future__ import annotations

"""
Homo Fluxus: A Thermodynamic Framework (Python reference implementation)

Implements the core operational condition stated in the paper excerpt:

  (1) dS_local/dt < 0  =>  E_f · ∇Phi_coh > 0

Where:
- S_local is local entropy
- E_f is the local energy-flow vector field
- Phi_coh is the coherence potential field

This module provides utilities to:
- Compute ∇Phi_coh on an N-D grid
- Compute the pointwise dot product E_f · ∇Phi_coh
- Estimate dS_local/dt from a time-series
- Evaluate the implication in (1) pointwise and in aggregate

Notes:
- Only equation (1) is explicitly present in the provided excerpt; no other
  quantitative definitions (e.g., closed-form Phi_coh, cosmological constants)
  are specified therein. This implementation therefore focuses strictly on
  the operational condition.

Paper metadata (from excerpt):
- Title: Homo Fluxus: A Thermodynamic Framework for Consciousness, Systemic Empathy, and Aligned Intelligence
- Author: Morten Magnusson (Symbiose Research)
- ORCID: 0009-0002-4860-5095
- DOI: 10.6084/m9.figshare.32099389
- Date: April 25, 2026
"""

from typing import Iterable, Tuple, Union, Dict
import numpy as np

Array = np.ndarray
Number = Union[int, float]

# --- Paper metadata and small-count numeric facts present in the excerpt ---
PAPER_TITLE: str = (
    "Homo Fluxus: A Thermodynamic Framework for Consciousness, Systemic Empathy, and Aligned Intelligence"
)
PAPER_DOI: str = "10.6084/m9.figshare.32099389"
PAPER_ORCID: str = "0009-0002-4860-5095"
PAPER_DATE_ISO: str = "2026-04-25"
LEVELS_WITH_PREDICTIONS: int = 6  # cosmological, neural, affective, social, ethical, computational
FRAGMENTATION_DOMAINS: int = 5    # five domains listed in the introduction
CONSTRUCTS_INTRODUCED: int = 2    # Homo Fluxus and systemic empathy

# Defaults for numeric operations (not from paper constants; operational choices)
DEFAULT_DT: float = 1.0
DEFAULT_GRID_SPACING: float = 1.0


def _normalize_spacing(
    spacing: Union[Number, Iterable[Number]], ndim: int
) -> Tuple[Number, ...]:
    """Normalize grid spacing to a tuple matching the number of spatial dimensions.

    Parameters
    - spacing: float or iterable of floats
    - ndim: number of spatial dimensions

    Returns
    - tuple of length ndim
    """
    if isinstance(spacing, (int, float)):
        return tuple([float(spacing)] * ndim)
    sp = tuple(float(s) for s in spacing)  # type: ignore[arg-type]
    if len(sp) != ndim:
        raise ValueError(f"Expected spacing length {ndim}, got {len(sp)}")
    return sp


def coherence_gradient(phi: Array, spacing: Union[Number, Iterable[Number]] = DEFAULT_GRID_SPACING) -> Array:
    """Compute the spatial gradient ∇Phi_coh of the coherence potential field.

    Implements the gradient over an N-D scalar field using numpy.gradient and returns
    an array with an extra trailing axis for vector components.

    Parameters
    - phi: ndarray of shape (n1, n2, ..., nk); scalar field Phi_coh on a regular grid
    - spacing: scalar or iterable specifying grid spacing along each axis

    Returns
    - grad_phi: ndarray of shape (n1, n2, ..., nk, k) where the last axis indexes components
    """
    if phi.ndim < 1:
        raise ValueError("phi must have at least one spatial dimension")
    sp = _normalize_spacing(spacing, phi.ndim)
    grads = np.gradient(phi, *sp, edge_order=2)
    grad_phi = np.stack(grads, axis=-1)
    return grad_phi


def energy_flow_dot_coherence_gradient(
    Ef: Array,
    phi: Array,
    spacing: Union[Number, Iterable[Number]] = DEFAULT_GRID_SPACING,
) -> Array:
    """Compute the pointwise dot product E_f · ∇Phi_coh on a grid.

    Parameters
    - Ef: ndarray of shape (n1, ..., nk, k) energy-flow vector field per grid point
    - phi: ndarray of shape (n1, ..., nk) coherence potential field
    - spacing: grid spacing for gradient

    Returns
    - dot: ndarray of shape (n1, ..., nk) with the dot product at each grid point

    Notes
    - This directly operationalizes the consequent term in equation (1).
    """
    grad_phi = coherence_gradient(phi, spacing=spacing)
    if Ef.shape != grad_phi.shape:
        raise ValueError(
            f"Shape mismatch: Ef {Ef.shape} vs grad_phi {grad_phi.shape}. Ef must match grad_phi."
        )
    dot = np.sum(Ef * grad_phi, axis=-1)
    return dot


def estimate_entropy_rate(S_series: Array, dt: float = DEFAULT_DT, axis: int = 0) -> Array:
    """Estimate the time derivative dS_local/dt from an entropy time-series.

    Parameters
    - S_series: ndarray with a time axis; local entropy samples over time
    - dt: time step between samples
    - axis: which axis is time

    Returns
    - dS_dt: ndarray with the same shape as S_series but with finite-difference derivative
      along the time axis (shape preserved using central differences internally)
    """
    S_series = np.asarray(S_series, dtype=float)
    dS_dt = np.gradient(S_series, dt, axis=axis, edge_order=2)
    return dS_dt


def implication_mask(dS_dt: Array, dot_Ef_gradPhi: Array, tol: float = 0.0) -> Array:
    """Evaluate the implication (1) pointwise: (dS_dt < 0) => (E_f · ∇Phi_coh > tol).

    Parameters
    - dS_dt: ndarray of dS_local/dt aligned to the same spatial indices as dot_Ef_gradPhi.
             If dS_dt has a time axis, it should be broadcastable to dot_Ef_gradPhi.
    - dot_Ef_gradPhi: ndarray of E_f · ∇Phi_coh
    - tol: small threshold to treat as strictly positive condition (default 0)

    Returns
    - mask: boolean ndarray where the implication holds. It is False only where dS_dt < 0
            and dot_Ef_gradPhi <= tol.
    """
    premise = dS_dt < 0
    consequent = dot_Ef_gradPhi > tol
    # Implication A=>B is logically equivalent to (~A) or B
    mask = (~premise) | consequent
    return mask


def implication_score(mask: Array) -> Dict[str, float]:
    """Summarize implication satisfaction.

    Returns
    - dict with keys:
      - satisfied_fraction: fraction of points where implication holds
      - violation_fraction: fraction where premise true and consequent false
      - n_true_premise: count where dS_dt < 0
      - n_violations: count of violations among true premises
    """
    mask_bool = mask.astype(bool)
    total = mask_bool.size
    satisfied = mask_bool.sum()
    violation = total - satisfied
    # For reporting, we need counts of true premise and violations among them.
    # Recoverable only if user supplied those masks; here we approximate by
    # counting positions where mask is False as violations of premise=>consequent.
    # Since mask is False iff premise True and consequent False.
    n_violations = int(violation)
    # n_true_premise is at least n_violations; we cannot know other true-premise
    # locations that also had consequent True without the raw masks, so we report
    # lower bound equals violations and set satisfied_fraction reliably.
    return {
        "satisfied_fraction": float(satisfied / total) if total > 0 else 1.0,
        "violation_fraction": float(violation / total) if total > 0 else 0.0,
        "n_true_premise_lower_bound": float(n_violations),
        "n_violations": float(n_violations),
    }


def evaluate_condition(
    Ef: Array,
    phi: Array,
    S_series: Array,
    dt: float = DEFAULT_DT,
    spacing: Union[Number, Iterable[Number]] = DEFAULT_GRID_SPACING,
    time_axis: int = 0,
    tol: float = 0.0,
) -> Dict[str, Array]:
    """High-level evaluation of equation (1) across a grid and over time.

    Parameters
    - Ef: ndarray (n1,...,nk,k): energy-flow field (assumed time-independent here)
    - phi: ndarray (n1,...,nk): coherence potential field (assumed time-independent here)
    - S_series: ndarray with leading time axis matching spatial shape of phi (time, n1,...,nk)
    - dt: time step for entropy derivative
    - spacing: spatial spacing for gradient
    - time_axis: axis of time in S_series (default 0)
    - tol: threshold for positive dot product condition

    Returns
    - dict with fields:
      - dS_dt: estimated entropy rate (same shape as S_series)
      - dot_field: E_f · ∇Phi_coh field (same spatial shape as phi)
      - implication_mask_t: boolean with shape S_series where implication holds at each time
    """
    dS_dt = estimate_entropy_rate(S_series, dt=dt, axis=time_axis)
    dot_field = energy_flow_dot_coherence_gradient(Ef, phi, spacing=spacing)

    # Broadcast dot_field to S_series shape for timewise implication
    # Move time axis to front for broadcasting convenience
    if time_axis != 0:
        dS_dt = np.moveaxis(dS_dt, time_axis, 0)
    # Now dS_dt has shape (T, *spatial)
    # Expand dot_field to (T, *spatial) via broadcasting
    implication = implication_mask(dS_dt, dot_field, tol=tol)

    # Restore original time axis position if needed
    if time_axis != 0:
        implication = np.moveaxis(implication, 0, time_axis)
        dS_dt = np.moveaxis(dS_dt, 0, time_axis)

    return {
        "dS_dt": dS_dt,
        "dot_field": dot_field,
        "implication_mask_t": implication,
    }


def _self_test() -> None:
    """Run a minimal self-test consistent with the paper's equation (1).

    Constructs a simple 2D grid where Phi has a constant gradient and Ef is aligned
    so that E_f · ∇Phi_coh > 0 everywhere, while S decreases linearly in time.
    Then introduces a region with anti-aligned Ef to produce violations and reports
    satisfaction fractions.
    """
    rng = np.random.default_rng(0)

    # Build a simple 2D grid
    nx, ny = 64, 48
    x = np.linspace(0.0, 1.0, nx)
    y = np.linspace(0.0, 1.0, ny)
    X, Y = np.meshgrid(x, y, indexing="ij")

    # Define Phi with constant gradient g = (1, 0.5)
    phi = 1.0 * X + 0.5 * Y

    # Define Ef aligned with grad phi: proportional to (1, 0.5)
    g = np.stack(np.gradient(phi, x[1]-x[0], y[1]-y[0], edge_order=2), axis=-1)
    g_norm = np.linalg.norm(g, axis=-1, keepdims=True) + 1e-12
    Ef = 2.0 * g / g_norm  # aligned unit field scaled

    # Time series of entropy decreasing: S(t) = S0 - alpha * t
    T = 20
    alpha = 0.1
    S0 = 10.0
    t = np.arange(T)
    S_series = (S0 - alpha * t)[:, None, None] * np.ones_like(phi)[None, :, :]

    results = evaluate_condition(Ef, phi, S_series, dt=1.0, spacing=(x[1]-x[0], y[1]-y[0]))
    mask = results["implication_mask_t"]
    sat_frac_all = mask.mean()

    # Now introduce a violating half-plane by flipping Ef sign on right half
    Ef_violate = Ef.copy()
    Ef_violate[nx//2:, :, :] *= -1.0
    results2 = evaluate_condition(Ef_violate, phi, S_series, dt=1.0, spacing=(x[1]-x[0], y[1]-y[0]))
    mask2 = results2["implication_mask_t"]
    sat_frac_violate = mask2.mean()

    print("Paper:", PAPER_TITLE)
    print("DOI:", PAPER_DOI)
    print("ORCID:", PAPER_ORCID)
    print("Eq. (1) satisfied fraction (aligned field):", round(float(sat_frac_all), 4))
    print("Eq. (1) satisfied fraction (half anti-aligned):", round(float(sat_frac_violate), 4))


if __name__ == "__main__":
    _self_test()
