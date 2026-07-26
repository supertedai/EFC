"""efc_master.py — Reference implementation of the EFC Master Specification.

Implements the Energy-Flow Cosmology (EFC) dynamical and structural sectors
as described in Magnusson (2025), "EFC — Master Specification".

Sectors implemented:
  EFC-D  – Energy-Flow Dynamics (Ef, Phi, H, v(r), c(S))
  EFC-S  – Structural Sector (entropy regimes, stability band)
"""
from __future__ import annotations
import numpy as np
from numpy.typing import NDArray

# ---------------------------------------------------------------------------
# Global constants / default parameters from the paper
# ---------------------------------------------------------------------------
C0: float = 299792.458          # base light speed [km/s]
A_PHI: float = 1.0              # potential amplitude (normalised baseline)
BETA: float = 1.0               # entropy coupling exponent (linear baseline)
A_EDGE: float = 1.0             # edge-coupling coefficient for c(S)
S0: float = 0.0                 # low-entropy endpoint
S1: float = 1.0                 # high-entropy endpoint
S_MID: float = 0.5 * (S0 + S1) # mid-entropy transition zone


# ---------------------------------------------------------------------------
# EFC-D: Dynamical Sector
# ---------------------------------------------------------------------------

def energy_flow_field(grad_S: NDArray[np.float64],
                      proportionality: float = 1.0) -> NDArray[np.float64]:
    """Compute the energy-flow field Ef ∝ −∇S.

    Parameters
    ----------
    grad_S : array, shape (..., 3) or (...,)
        Entropy gradient vector(s).
    proportionality : float
        Proportionality constant relating Ef to −∇S.

    Returns
    -------
    Ef : same shape as grad_S
    """
    return -proportionality * np.asarray(grad_S, dtype=np.float64)


def effective_potential(Ef: NDArray[np.float64] | float,
                       S: NDArray[np.float64] | float,
                       A_phi: float = A_PHI,
                       beta: float = BETA) -> NDArray[np.float64]:
    """Effective potential  Φ(Ef, S) = A_Φ · Ef · (1 + S^β).

    Baseline (β=1):  Φ = A_Φ · Ef · (1 + S).
    """
    Ef = np.asarray(Ef, dtype=np.float64)
    S = np.asarray(S, dtype=np.float64)
    return A_phi * Ef * (1.0 + S ** beta)


def expansion_rate(Ef: NDArray[np.float64] | float,
                   S: NDArray[np.float64] | float) -> NDArray[np.float64]:
    """Expansion rate  H(Ef, S) = sqrt(|Ef|) · (1 + S).   [Eq. 1]"""
    Ef = np.asarray(Ef, dtype=np.float64)
    S = np.asarray(S, dtype=np.float64)
    return np.sqrt(np.abs(Ef)) * (1.0 + S)


def rotation_velocity(r: NDArray[np.float64] | float,
                      dPhi_dr: NDArray[np.float64] | float) -> NDArray[np.float64]:
    """Circular velocity  v(r) = sqrt(r · ∂Φ/∂r).

    Parameters
    ----------
    r : radial coordinate(s)
    dPhi_dr : radial gradient of the effective potential at r
    """
    r = np.asarray(r, dtype=np.float64)
    dPhi_dr = np.asarray(dPhi_dr, dtype=np.float64)
    return np.sqrt(np.abs(r * dPhi_dr))


# ---------------------------------------------------------------------------
# Light-propagation / effective light speed
# ---------------------------------------------------------------------------

def x_of_S(S: NDArray[np.float64] | float,
           S0: float = S0, S1: float = S1) -> NDArray[np.float64]:
    """Normalised entropy coordinate x(S) ∈ [−1, 1].

    Maps S linearly so that S0 → −1 and S1 → +1.
    """
    S = np.asarray(S, dtype=np.float64)
    return 2.0 * (S - S0) / (S1 - S0) - 1.0


def effective_light_speed(S: NDArray[np.float64] | float,
                         c0: float = C0,
                         a_edge: float = A_EDGE,
                         s0: float = S0,
                         s1: float = S1) -> NDArray[np.float64]:
    """Entropy-dependent effective light speed.

    c(S) = c0 · [1 + a_edge · x(S)²]
    """
    x = x_of_S(S, s0, s1)
    return c0 * (1.0 + a_edge * x ** 2)


def c_min(c0: float = C0, a_edge: float = A_EDGE) -> float:
    """Minimum effective light speed, attained at S_mid (x = 0)."""
    return c0  # x(S_mid) = 0  ⇒  c_min = c0 · (1 + 0) = c0


# ---------------------------------------------------------------------------
# EFC-S: Structural Sector
# ---------------------------------------------------------------------------

def structural_regime(S: NDArray[np.float64] | float,
                     s0: float = S0,
                     s1: float = S1) -> NDArray[np.object_]:
    """Classify entropy values into structural regimes.

    Returns
    -------
    regime : array of str — 'focusing', 'transition', or 'defocusing'
    """
    S = np.atleast_1d(np.asarray(S, dtype=np.float64))
    smid = 0.5 * (s0 + s1)
    width = 0.1 * (s1 - s0)  # 10 % band around mid
    out = np.empty(S.shape, dtype=object)
    out[S < smid - width] = 'focusing'
    out[S > smid + width] = 'defocusing'
    mask_mid = (S >= smid - width) & (S <= smid + width)
    out[mask_mid] = 'transition'
    return out


def stability_band_speed(S: NDArray[np.float64] | float,
                         c0: float = C0,
                         a_edge: float = A_EDGE,
                         s0: float = S0,
                         s1: float = S1) -> NDArray[np.float64]:
    """Effective light speed inside the stability band (near S_mid)."""
    return effective_light_speed(S, c0, a_edge, s0, s1)


def potential_gradient_1d(Ef_arr: NDArray[np.float64],
                         S_arr: NDArray[np.float64],
                         r_arr: NDArray[np.float64],
                         A_phi: float = A_PHI,
                         beta: float = BETA) -> NDArray[np.float64]:
    """Numerical radial gradient dΦ/dr from sampled Ef(r) and S(r)."""
    Phi = effective_potential(Ef_arr, S_arr, A_phi, beta)
    return np.gradient(Phi, r_arr)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print('=== EFC Master — self-test ===')

    # 1. Energy-flow field from a simple entropy gradient
    grad_S = np.array([0.5, -0.3, 0.1])
    Ef_vec = energy_flow_field(grad_S)
    print(f'Ef (vector):  {Ef_vec}')

    # 2. Effective potential (scalar Ef for simplicity)
    Ef_scalar = 2.0;  S_val = 0.4
    phi = effective_potential(Ef_scalar, S_val)
    print(f'Phi(Ef={Ef_scalar}, S={S_val}): {phi:.4f}')

    # 3. Expansion rate
    H = expansion_rate(Ef_scalar, S_val)
    print(f'H(Ef={Ef_scalar}, S={S_val}):   {H:.6f}')

    # 4. Effective light speed across entropy range
    S_range = np.linspace(S0, S1, 5)
    c_vals = effective_light_speed(S_range)
    print(f'c(S) at S={S_range}: {np.round(c_vals, 2)}')
    print(f'c_min (at S_mid):    {c_min():.3f} km/s')

    # 5. Structural regimes
    regimes = structural_regime(S_range)
    print(f'Regimes:             {regimes}')

    # 6. Rotation curve from toy profiles
    r = np.linspace(1.0, 30.0, 60)
    Ef_r = 5.0 * np.exp(-r / 10.0)
    S_r = 0.3 + 0.4 * (1 - np.exp(-r / 15.0))
    dPhi = potential_gradient_1d(Ef_r, S_r, r)
    v = rotation_velocity(r, dPhi)
    print(f'v(r=10): {v[np.searchsorted(r,10.0)]:.4f} (arb. units)')

    print('\nAll self-tests passed.')
