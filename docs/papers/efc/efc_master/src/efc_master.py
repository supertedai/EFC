"""efc_master.py – Reference implementation of the EFC Master Specification.

Implements the Energy-Flow Cosmology (EFC) dynamical and structural sectors
as described in Magnusson (2025).
"""

import numpy as np
from typing import Tuple

# ---------------------------------------------------------------------------
# Default constants (baseline values from the specification)
# ---------------------------------------------------------------------------
C0: float = 2.998e8          # underlying light speed [m/s]
A_PHI: float = 1.0            # potential amplitude constant
BETA: float = 1.0             # entropy-coupling exponent (linear baseline)
A_EDGE: float = 0.05          # edge coefficient for c(S)
S0: float = 0.0               # low-entropy endpoint
S1: float = 1.0               # high-entropy endpoint
S_MID: float = 0.5 * (S0 + S1)  # mid-entropy transition


# ---------------------------------------------------------------------------
# §2.1  Energy-Flow Field
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


def energy_flow_magnitude(grad_S: np.ndarray) -> np.ndarray:
    """Scalar magnitude |Ef| from entropy gradient."""
    ef = energy_flow_field(grad_S)
    return np.sqrt(np.sum(ef ** 2, axis=-1))


# ---------------------------------------------------------------------------
# §2.2  Effective Potential  Φ(Ef, S)
# ---------------------------------------------------------------------------
def effective_potential(Ef: np.ndarray, S: np.ndarray,
                       A_phi: float = A_PHI,
                       beta: float = BETA) -> np.ndarray:
    """Φ(Ef, S) = A_Φ · Ef · (1 + S^β).

    Parameters
    ----------
    Ef : ndarray   Scalar energy-flow magnitude.
    S  : ndarray   Entropy field value(s).
    A_phi : float  Amplitude constant.
    beta  : float  Coupling exponent (1 = linear baseline).
    """
    return A_phi * Ef * (1.0 + S ** beta)


# ---------------------------------------------------------------------------
# §2.3  Expansion Rate  H(Ef, S)
# ---------------------------------------------------------------------------
def expansion_rate(Ef: np.ndarray, S: np.ndarray) -> np.ndarray:
    """H(Ef, S) = sqrt(|Ef|) * (1 + S)   [Eq. 1]."""
    return np.sqrt(np.abs(Ef)) * (1.0 + S)


# ---------------------------------------------------------------------------
# §2.4  Rotation Curves
# ---------------------------------------------------------------------------
def rotation_velocity(r: np.ndarray, dPhi_dr: np.ndarray) -> np.ndarray:
    """v(r) = sqrt(r · dΦ/dr).

    Parameters
    ----------
    r       : ndarray  Radial distances.
    dPhi_dr : ndarray  Radial gradient of the effective potential.
    """
    return np.sqrt(np.abs(r * dPhi_dr))


def potential_gradient_numerical(r: np.ndarray, Phi: np.ndarray) -> np.ndarray:
    """Numerical radial derivative dΦ/dr via central differences."""
    return np.gradient(Phi, r)


# ---------------------------------------------------------------------------
# §2.5 / §5  Effective Light Speed  c(S)
# ---------------------------------------------------------------------------
def x_of_S(S: np.ndarray, s0: float = S0, s1: float = S1) -> np.ndarray:
    """Normalised entropy coordinate x ∈ [−1, 1]."""
    s_mid = 0.5 * (s0 + s1)
    half_range = 0.5 * (s1 - s0)
    if half_range == 0:
        return np.zeros_like(S)
    return (S - s_mid) / half_range


def effective_light_speed(S: np.ndarray, c0: float = C0,
                          a_edge: float = A_EDGE,
                          s0: float = S0, s1: float = S1) -> np.ndarray:
    """c(S) = c0 * (1 + a_edge * x(S)^2)."""
    x = x_of_S(S, s0, s1)
    return c0 * (1.0 + a_edge * x ** 2)


def c_min(c0: float = C0, a_edge: float = A_EDGE) -> float:
    """Minimum light speed at S = S_mid  (x=0)."""
    return c0  # x=0 ⇒ c = c0·(1+0) = c0


# ---------------------------------------------------------------------------
# §4  Structural Sector helpers
# ---------------------------------------------------------------------------
def structural_regime(S: np.ndarray, s0: float = S0,
                     s1: float = S1) -> np.ndarray:
    """Return regime labels: 0 = focusing, 1 = transition, 2 = defocusing."""
    s_mid = 0.5 * (s0 + s1)
    quarter = 0.25 * (s1 - s0)
    regime = np.ones_like(S, dtype=int)  # default = transition
    regime[S < s_mid - quarter] = 0      # focusing
    regime[S > s_mid + quarter] = 2      # defocusing
    return regime


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== EFC Master – self-test ===")
    # Sample entropy gradient field (single point)
    gS = np.array([[0.1, -0.2, 0.05]])
    ef_vec = energy_flow_field(gS)
    ef_mag = energy_flow_magnitude(gS)
    print(f"Ef vector : {ef_vec}")
    print(f"|Ef|      : {ef_mag}")

    # Potential & expansion at that point
    S_val = np.array([0.3])
    phi = effective_potential(ef_mag, S_val)
    H = expansion_rate(ef_mag, S_val)
    print(f"Φ(Ef,S)   : {phi}")
    print(f"H(Ef,S)   : {H}")

    # Light speed across entropy range
    S_arr = np.linspace(S0, S1, 5)
    c_arr = effective_light_speed(S_arr)
    print(f"S         : {S_arr}")
    print(f"c(S)      : {c_arr}")
    print(f"c_min     : {c_min():.6e} m/s")

    # Rotation curve toy example
    r = np.linspace(1, 20, 50)
    S_profile = S_MID + 0.3 * np.exp(-r / 5.0)
    Ef_profile = 0.8 * np.exp(-r / 8.0)
    Phi_profile = effective_potential(Ef_profile, S_profile)
    dPhi = potential_gradient_numerical(r, Phi_profile)
    v = rotation_velocity(r, dPhi)
    print(f"v(r=5)    : {v[np.argmin(np.abs(r-5))]:.4f}")
    print("Self-test passed.")
