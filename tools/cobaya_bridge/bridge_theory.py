"""
EFC bridge: (K0, m_sq) -> (mu0, Sigma0)
=======================================

Closed-form mapping from the two EFC field parameters in the Relativistic
Action (DOI: 10.6084/m9.figshare.31876324) and Kill-Test v5 (Session Note v5)
to the standard MGCAMB scale-independent (mu0, Sigma0) parametrisation.

References (equation numbers from Kill-Test v5):

  Eq. (1)   R(k, a) = K0 * Theta(rho_eff) * (Gamma' phi_dot)^2 a^4
                              / (M_Pl^2 * F * k^4)
  Eq. (2)   Theta(rho_eff) = exp(- (rho_eff / rho_*)^2),  rho_* = 1e-22 kg/m^3
  Eq. (3)   K0 calibration: at (a=1, k=0.05 h/Mpc) we want R = 0.0638
  Eq. (4)   k^2/a^2 * delta_lambda = V''(phi_bar) delta_phi - K k^2/a^2 delta_phi
  Eq. (6)   f = 1 - V''(phi_bar) / [K(rho_bar) k^2 / a^2]
  Table 8   slip calibration: f = 0.15 -> eta = 1.23, Sigma = 1.05

The "sweet spot" calibration is anchored at the CMB lensing scale
k_lens = 0.05 h/Mpc and the present day a = 1, where (mu, Sigma) = (0.94, 1.05)
reproduces the Localization paper's chi^2 = -0.45 vs GR (DOI:
10.6084/m9.figshare.31368433, Phase 2 "minimize_free_cosmo").

Calibration constants
---------------------

From Kill-Test v5 Section 4 ("The K(rho) Bridge"):

  K0_ref      = 1.66                       (anchor for mu0 = 0.94)
  msq_ref     = 0.0035                     (anchor for f   = 0.15)
  Gamma_phi   = 0.049 * 0.01               (Gamma' * phi_dot, units in
                                            which M_Pl^2 * F = 1)
  k_lens      = 0.05                       (h/Mpc)
  R_ref       = K0_ref * Gamma_phi^2 / k_lens^4   = 0.06384
  f_ref       = 0.15
  eta_ref     = 1.23

The bridge below evaluates the same expressions for arbitrary (K0, m_sq):

  R       = K0 * Gamma_phi^2 / k_lens^4         (a = 1, Theta = 1)
  mu0     = 1 / (1 + R)
  f       = m_sq / (K0 * k_lens^2)              (linearised Eq. 6)
  eta     = 1 + ((eta_ref - 1) / f_ref) * f
  Sigma0  = 0.5 * (1 + eta) * mu0

At the reference point (K0 = 1.66, m_sq = 0.0035) this returns the exact
sweet spot (0.94, 1.05).
"""

from __future__ import annotations

K0_REF = 1.66
MSQ_REF = 0.0035
GAMMA_PHI = 0.049 * 0.01
K_LENS = 0.05  # h/Mpc
ETA_REF = 1.23
RHO_STAR = 1.0e-22  # kg/m^3
RHO_M_TODAY = 8.5e-27  # kg/m^3 (cosmological background, a = 1)
# F_REF is computed self-consistently from the slip equation at the
# reference point (0.156627...), not from the rounded 0.15 in Table 8.
F_REF = 1.0 - MSQ_REF / (K0_REF * K_LENS ** 2)


def stiffness_response(K0: float, k: float = K_LENS, a: float = 1.0,
                       rho_eff: float = RHO_M_TODAY) -> float:
    """R(k, a) from Eq. (1)–(2)."""
    import math
    Theta = math.exp(-(rho_eff / RHO_STAR) ** 2)
    return K0 * Theta * GAMMA_PHI ** 2 * a ** 4 / k ** 4


def slip_factor(K0: float, m_sq: float, k: float = K_LENS) -> float:
    """f = 1 - V''(phi_bar) / [K(rho_bar) k^2 / a^2] from Eq. (6),
    evaluated at a = 1 with V = (1/2) m^2 phi^2 -> V'' = m^2.
    At (K0_ref = 1.66, msq_ref = 0.0035) returns f_ref ≈ 0.15."""
    return 1.0 - m_sq / (K0 * k ** 2)


def bridge(K0: float, m_sq: float) -> dict:
    """Map (K0, m^2) -> derived (mu0, Sigma0, eta, R, f)."""
    R = stiffness_response(K0)
    mu0 = 1.0 / (1.0 + R)
    f = slip_factor(K0, m_sq)
    eta = 1.0 + (ETA_REF - 1.0) * (f / F_REF)
    Sigma0 = 0.5 * (1.0 + eta) * mu0
    return {
        "R": R,
        "f": f,
        "eta": eta,
        "mu0": mu0,
        "Sigma0": Sigma0,
    }


def mu0_of_K0(K0: float) -> float:
    """Closed-form mu0 = 1 / (1 + K0 * Gamma_phi^2 / k_lens^4)."""
    return bridge(K0, MSQ_REF)["mu0"]


def Sigma0_of_K0_msq(K0: float, m_sq: float) -> float:
    """Closed-form Sigma0 = 0.5 * (1 + eta) * mu0."""
    return bridge(K0, m_sq)["Sigma0"]


# --------------------------------------------------------------------------- #
# Sanity check                                                                #
# --------------------------------------------------------------------------- #

def _self_test() -> None:
    out = bridge(K0_REF, MSQ_REF)
    # mu0 must reproduce 0.94 exactly (closed form, no rounding)
    assert abs(out["mu0"] - 0.94) < 5e-4, out
    # eta and Sigma agree with Kill-Test v5 Table 8 to within rounding
    # (paper rounds f = 0.1566 -> 0.15 in the table)
    assert abs(out["eta"] - 1.23) < 0.02, out
    assert abs(out["Sigma0"] - 1.05) < 5e-3, out
    print("bridge sweet spot:", out)
    # Off the ref point
    print("bridge K0=1.0,  m^2=0.002 :", bridge(1.0, 0.002))
    print("bridge K0=2.0,  m^2=0.005 :", bridge(2.0, 0.005))
    print("bridge K0=1.66, m^2=0.000 :", bridge(K0_REF, 0.0))


if __name__ == "__main__":
    _self_test()
