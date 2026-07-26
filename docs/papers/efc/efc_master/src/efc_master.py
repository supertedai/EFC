"""efc_master.py — Reference implementation of EFC Master Specification.

Implements the Energy-Flow Cosmology (EFC) dynamical and structural sectors
as described in Magnusson (2025), "EFC — Master Specification".

Sectors implemented:
  EFC-D  (Dynamical): Ef, Φ, H, v(r), c(S)
  EFC-S  (Structural): entropy regimes, stability band
"""

import numpy as np
from typing import Union, Tuple

# ---------------------------------------------------------------------------
# Global constants / default parameters
# ---------------------------------------------------------------------------
c0: float = 2.998e8           # vacuum speed of light [m/s]
A_PHI: float = 1.0            # potential amplitude (normalised)
BETA: float = 1.0             # baseline coupling exponent
A_EDGE: float = 1.0           # edge-coupling coefficient for c(S)
S0: float = 0.0               # low-entropy endpoint
S1: float = 1.0               # high-entropy endpoint
S_MID: float = 0.5 * (S0 + S1)  # mid-entropy transition

Arr = Union[float, np.ndarray]

# ---------------------------------------------------------------------------
# EFC-D: Dynamical Sector
# ---------------------------------------------------------------------------

def energy_flow_field(grad_S: np.ndarray) -> np.ndarray:
    """Compute the energy-flow field Ef ∝ −∇S.

    Parameters
    ----------
    grad_S : ndarray, shape (..., 3)
        Entropy gradient vector(s).

    Returns
    -------
    Ef : ndarray, same shape as grad_S
    """
    return -grad_S


def effective_potential(Ef: Arr, S: Arr, A_phi: float = A_PHI,
                        beta: float = BETA) -> Arr:
    """Effective potential  Φ(Ef, S) = A_Φ · Ef · (1 + S^β).

    Parameters
    ----------
    Ef : float or ndarray   Energy-flow magnitude (scalar component).
    S  : float or ndarray   Entropy level.
    A_phi : float           Amplitude constant.
    beta  : float           Coupling exponent (1 = linear baseline).

    Returns
    -------
    Phi : same type as inputs
    """
    return A_phi * Ef * (1.0 + np.power(S, beta))


def expansion_rate(Ef: Arr, S: Arr) -> Arr:
    """Expansion rate  H(Ef, S) = sqrt(|Ef|) · (1 + S).   [Eq. 1]"""
    return np.sqrt(np.abs(Ef)) * (1.0 + S)


def rotation_velocity(r: Arr, dPhi_dr: Arr) -> Arr:
    """Circular velocity from potential gradient: v(r) = sqrt(r · dΦ/dr)."""
    return np.sqrt(np.abs(r * dPhi_dr))


def effective_light_speed(S: Arr, c_0: float = c0,
                          a_edge: float = A_EDGE) -> Arr:
    """Entropy-dependent effective light speed.

    c(S) = c0 · [1 + a_edge · x(S)^2]
    where x(S) = (S − S_mid) / (S1 − S0)  is a normalised entropy coordinate.
    """
    x = (S - S_MID) / (S1 - S0) if (S1 - S0) != 0 else 0.0
    return c_0 * (1.0 + a_edge * x ** 2)


# ---------------------------------------------------------------------------
# EFC-S: Structural Sector
# ---------------------------------------------------------------------------

def entropy_regime(S: Arr) -> np.ndarray:
    """Classify entropy into regimes: 'low', 'mid', 'high'."""
    S_arr = np.atleast_1d(np.asarray(S, dtype=float))
    labels = np.empty(S_arr.shape, dtype='<U4')
    third = (S1 - S0) / 3.0
    labels[S_arr < S0 + third] = 'low'
    labels[(S_arr >= S0 + third) & (S_arr <= S1 - third)] = 'mid'
    labels[S_arr > S1 - third] = 'high'
    return labels


def stability_band_cmin(c_0: float = c0, a_edge: float = A_EDGE) -> float:
    """Minimum effective light speed at S_mid (stability band centre)."""
    return effective_light_speed(S_MID, c_0, a_edge)


def dPhi_dr_numerical(r: np.ndarray, Ef_r: np.ndarray, S_r: np.ndarray,
                      A_phi: float = A_PHI, beta: float = BETA) -> np.ndarray:
    """Numerical radial derivative of Φ given Ef(r) and S(r) profiles."""
    Phi = effective_potential(Ef_r, S_r, A_phi, beta)
    return np.gradient(Phi, r)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print('=== EFC Master — self-test ===')
    # 1. Energy-flow from a simple gradient
    grad = np.array([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0]])
    Ef_vec = energy_flow_field(grad)
    assert np.allclose(Ef_vec, -grad), 'Ef test failed'
    print(f'Ef vectors: {Ef_vec}')

    # 2. Potential
    phi_val = effective_potential(1.0, 0.5)
    print(f'Phi(Ef=1, S=0.5, beta=1) = {phi_val:.4f}  (expect 1.5)')
    assert np.isclose(phi_val, 1.5)

    # 3. Expansion rate
    H_val = expansion_rate(4.0, 0.5)
    print(f'H(Ef=4, S=0.5) = {H_val:.4f}  (expect 3.0)')
    assert np.isclose(H_val, 3.0)

    # 4. Light speed at S_mid
    c_mid = effective_light_speed(S_MID)
    print(f'c(S_mid) = {c_mid:.6e} m/s  (should equal c0 = {c0:.6e})')
    assert np.isclose(c_mid, c0)

    # 5. Stability band
    cmin = stability_band_cmin()
    print(f'c_min (stability band) = {cmin:.6e} m/s')

    # 6. Regimes
    S_test = np.array([0.1, 0.5, 0.9])
    print(f'Regimes for S={S_test}: {entropy_regime(S_test)}')

    # 7. Rotation curve (toy profile)
    r = np.linspace(1, 50, 200)
    Ef_r = 10.0 / (1.0 + r)          # decaying Ef
    S_r = 0.3 + 0.01 * r             # gently rising S
    dphi = dPhi_dr_numerical(r, Ef_r, S_r)
    v = rotation_velocity(r, dphi)
    print(f'v(r=25) ≈ {np.interp(25, r, v):.3f}  (model units)')

    print('All self-tests passed.')
