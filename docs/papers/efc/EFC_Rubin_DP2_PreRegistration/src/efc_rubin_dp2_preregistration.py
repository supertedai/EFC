"""efc_rubin_dp2_preregistration.py

Reference implementation of the Energy-Flow Cosmology (EFC) pre-registered
predictions for the Rubin Observatory LSST DP2 cosmic shear dataset.

Paper: Magnusson (2026)
DOI : 10.6084/m9.figshare.32013738
"""

import numpy as np
from typing import Tuple

# ---------------------------------------------------------------------------
# Frozen KC4 parameters  (Table 1)
# ---------------------------------------------------------------------------
ETA_Z0: float = 1.10          # gravitational slip eta(z=0)
ETA_Z0_ERR: float = 0.05
ALPHA_EFC: float = -0.695      # EFC coupling alpha
ALPHA_EFC_ERR: float = 0.02
A_T: float = 0.30              # regime-transition scale factor  (fixed)
DELTA_T: float = 0.30          # transition width               (fixed)
SIGMA8_EFC: float = 0.833
SIGMA8_EFC_ERR: float = 0.010
OMEGA_M: float = 0.310
OMEGA_M_ERR: float = 0.008
OMEGA_M_REF: float = 0.3       # reference value in S8 definition

# Derived lensing parameters at z_eff = 0.65
Z_EFF: float = 0.65
A_EFF: float = 1.0 / (1.0 + Z_EFF)   # ~0.606

# LCDM reference
S8_LCDM: float = 0.832
S8_LCDM_ERR: float = 0.013


# ---------------------------------------------------------------------------
# Eq.(1)-(3): regime gate and modified-gravity functions
# ---------------------------------------------------------------------------

def regime_gate(a: np.ndarray | float) -> np.ndarray:
    """EFC regime gate function G(a).

    Smooth activation at a >= a_t with width Delta.
    We model G as a logistic sigmoid centred on a_t:
        G(a) = 1 / (1 + exp(-(a - a_t) / (Delta / 6)))
    so that G ~ 0 for a << a_t and G ~ 1 for a >> a_t.
    """
    a = np.asarray(a, dtype=np.float64)
    steepness = DELTA_T / 6.0          # maps width to ~6-sigma range
    return 1.0 / (1.0 + np.exp(-(a - A_T) / steepness))


def _alpha_sigma_from_eta_alpha(eta0: float = ETA_Z0,
                                 alpha_mu: float = ALPHA_EFC) -> Tuple[float, float]:
    """Derive alpha_Sigma from eta(z=0)=Phi/Psi and alpha_mu.

    From Eq.(3) at a=1 where G(1)~1:
        eta = (1 + alpha_Sigma) / (1 + alpha_mu)
    => alpha_Sigma = eta * (1 + alpha_mu) - 1
    """
    G1 = float(regime_gate(1.0))
    alpha_sigma = eta0 * (1.0 + alpha_mu * G1) - 1.0
    return alpha_mu, alpha_sigma


ALPHA_MU, ALPHA_SIGMA = _alpha_sigma_from_eta_alpha()


def mu_func(a: np.ndarray | float) -> np.ndarray:
    """Eq.(1): mu(a) = 1 + alpha_mu * G(a)."""
    return 1.0 + ALPHA_MU * regime_gate(a)


def sigma_func(a: np.ndarray | float) -> np.ndarray:
    """Eq.(2): Sigma(a) = 1 + alpha_Sigma * G(a)."""
    return 1.0 + ALPHA_SIGMA * regime_gate(a)


def eta_func(a: np.ndarray | float) -> np.ndarray:
    """Eq.(3): eta(a) = (1 + alpha_Sigma G(a)) / (1 + alpha_mu G(a))."""
    return sigma_func(a) / mu_func(a)


# ---------------------------------------------------------------------------
# Eq.(4)-(5): S8 prediction
# ---------------------------------------------------------------------------

def s8_efc(sigma8: float = SIGMA8_EFC,
           omega_m: float = OMEGA_M) -> float:
    """Eq.(4): S8^efc = sigma8 * (Omega_m / 0.3)^0.5."""
    return sigma8 * (omega_m / OMEGA_M_REF) ** 0.5


def delta_s8(sigma8: float = SIGMA8_EFC,
             omega_m: float = OMEGA_M) -> float:
    """Eq.(5): Delta S8 = S8^efc - S8^LCDM."""
    return s8_efc(sigma8, omega_m) - S8_LCDM


# ---------------------------------------------------------------------------
# Eq.(6)-(7): lensing enhancement
# ---------------------------------------------------------------------------

def xi_plus_ratio(z_eff: float = Z_EFF) -> Tuple[float, float]:
    """Eq.(6): xi+^efc / xi+^LCDM ~ Sigma(z_eff)^2.

    Returns (central, uncertainty).
    """
    a_eff = 1.0 / (1.0 + z_eff)
    sig = float(sigma_func(a_eff))
    central = sig ** 2
    # propagate alpha_Sigma uncertainty (symmetric)
    G = float(regime_gate(a_eff))
    dsig_dalpha = G
    sig_err = ALPHA_EFC_ERR * dsig_dalpha   # rough
    ratio_err = 2.0 * sig * sig_err
    return central, ratio_err


def sigma_at_zeff(z_eff: float = Z_EFF) -> Tuple[float, float]:
    """Eq.(7): Sigma(z_eff) with uncertainty."""
    a_eff = 1.0 / (1.0 + z_eff)
    sig = float(sigma_func(a_eff))
    G = float(regime_gate(a_eff))
    sig_err = ALPHA_EFC_ERR * G
    return sig, sig_err


def delta_cl_over_cl(z_eff: float = Z_EFF) -> float:
    """Fractional convergence power spectrum enhancement ~ Sigma^2 - 1."""
    ratio, _ = xi_plus_ratio(z_eff)
    return ratio - 1.0


# ---------------------------------------------------------------------------
# Falsification threshold (Section 4)
# ---------------------------------------------------------------------------
S8_FALSIFICATION_THRESHOLD: float = 0.820


def is_kc4_falsified(s8_obs: float, s8_obs_err: float) -> bool:
    """Primary falsification: KC4 ruled out if S8_obs < 0.820 at >2sigma."""
    return (s8_obs + 2.0 * s8_obs_err) < S8_FALSIFICATION_THRESHOLD


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Verify key frozen numbers from the paper
    s8 = s8_efc()
    print(f"S8^efc           = {s8:.3f}  (paper: 0.847)")
    assert abs(s8 - 0.847) < 0.002, f"S8 mismatch: {s8}"

    ds8 = delta_s8()
    print(f"Delta S8         = {ds8:+.3f}  (paper: +0.015)")
    assert abs(ds8 - 0.015) < 0.002

    eta0 = float(eta_func(1.0))
    print(f"eta(z=0)         = {eta0:.3f}  (paper: 1.10)")
    assert abs(eta0 - 1.10) < 0.01

    sig_val, sig_err = sigma_at_zeff()
    print(f"Sigma(z_eff=0.65)= {sig_val:.3f} +/- {sig_err:.3f}  (paper: 1.04+/-0.02)")
    assert abs(sig_val - 1.04) < 0.02

    ratio, ratio_err = xi_plus_ratio()
    print(f"xi+ ratio        = {ratio:.3f} +/- {ratio_err:.3f}  (paper: 1.08+/-0.04)")
    assert abs(ratio - 1.08) < 0.02

    dcl = delta_cl_over_cl()
    print(f"Delta Cl / Cl    = {dcl*100:.1f}%  (paper: ~8%)")

    mu_val = float(mu_func(A_EFF))
    print(f"mu(z_eff=0.65)   = {mu_val:.3f}  (paper: 0.97+/-0.03)")
    assert abs(mu_val - 0.97) < 0.02

    print("\nAll self-tests passed.")
