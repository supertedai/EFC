"""efc_rcmp_test_specification.py

Reference implementation of the EFC-ΛCDM Comparative Test Specification v1.1
(Magnusson 2026, DOI: 10.6084/m9.figshare.32080083).

Implements the (μ, Σ) phenomenological parametrization, gate function,
scale filter, priors, and pixel-level verification checks.
"""

import numpy as np
from typing import Tuple, Dict, Optional

# ---------------------------------------------------------------------------
# Locked gate / filter parameters  (Table in §1.2)
# ---------------------------------------------------------------------------
AT: float = 0.7          # scale-factor at transition
DELTA_A: float = 0.08    # regime-transition width
KC: float = 0.05         # h/Mpc  –  scale cut-off
ALPHA_SLIP: float = 1.0  # VariantH slip constraint coefficient

# ---------------------------------------------------------------------------
# ΛCDM baseline priors  (Table in §1.1)
# ---------------------------------------------------------------------------
LCDM_PRIORS: Dict[str, dict] = {
    "omega_b":      {"type": "uniform", "low": 0.020, "high": 0.025},
    "omega_c":      {"type": "uniform", "low": 0.09,  "high": 0.15},
    "100_theta_MC": {"type": "uniform", "low": 1.03,  "high": 1.05},
    "tau_reio":     {"type": "gaussian", "mean": 0.054, "sigma": 0.007},
    "ln10As":       {"type": "uniform", "low": 2.0,   "high": 4.0},
    "n_s":          {"type": "uniform", "low": 0.87,  "high": 1.07},
}

# EFC extra-parameter priors  (Table in §1.2)
EFC_PRIORS: Dict[str, dict] = {
    "A_mu":    {"type": "uniform", "low": -0.20, "high": 0.05},
    "A_Sigma": {"type": "uniform", "low": -0.05, "high": 0.20},
}


# ---------------------------------------------------------------------------
# Core equations  (Eqs 1–4)
# ---------------------------------------------------------------------------
def gate_function(a: np.ndarray, at: float = AT, delta_a: float = DELTA_A) -> np.ndarray:
    """Eq. 1 – temporal gate function g(a).

    Parameters
    ----------
    a : array_like   Scale factor(s).
    at : float       Transition scale factor (locked 0.7).
    delta_a : float  Transition width (locked 0.08).

    Returns
    -------
    g : ndarray  Values in (0, 1).
    """
    a = np.asarray(a, dtype=np.float64)
    return 0.5 * (1.0 + np.tanh((a - at) / delta_a))


def scale_filter(k: np.ndarray, kc: float = KC) -> np.ndarray:
    """Eq. 2 – Lorentzian scale filter f_k(k).

    Parameters
    ----------
    k : array_like   Wavenumber(s) in h/Mpc.
    kc : float       Cut-off wavenumber (locked 0.05 h/Mpc).

    Returns
    -------
    fk : ndarray  Values in (0, 1].
    """
    k = np.asarray(k, dtype=np.float64)
    return 1.0 / (1.0 + (k / kc) ** 2)


def mu_efc(k: np.ndarray, a: np.ndarray, A_mu: float,
           at: float = AT, delta_a: float = DELTA_A,
           kc: float = KC) -> np.ndarray:
    """Eq. 3 – modified gravity function μ(k, a).

    Returns 2-D array of shape (len(a), len(k)).
    """
    g = gate_function(a, at, delta_a)[:, None]   # (Na, 1)
    fk = scale_filter(k, kc)[None, :]            # (1, Nk)
    return 1.0 + A_mu * g * fk


def sigma_efc(k: np.ndarray, a: np.ndarray, A_Sigma: float,
              at: float = AT, delta_a: float = DELTA_A,
              kc: float = KC) -> np.ndarray:
    """Eq. 4 – lensing function Σ(k, a).

    Returns 2-D array of shape (len(a), len(k)).
    """
    g = gate_function(a, at, delta_a)[:, None]
    fk = scale_filter(k, kc)[None, :]
    return 1.0 + A_Sigma * g * fk


def sigma_variant_h(k: np.ndarray, a: np.ndarray, A_mu: float,
                    alpha: float = ALPHA_SLIP, **kw) -> np.ndarray:
    """EFC-VariantH slip constraint: Σ = 1 − α·(μ − 1)."""
    mu_val = mu_efc(k, a, A_mu, **kw)
    return 1.0 - alpha * (mu_val - 1.0)


def S8(sigma8: float, Omega_m: float) -> float:
    """Derived parameter S_8 ≡ σ_8 · (Ω_m / 0.3)^0.5."""
    return sigma8 * np.sqrt(Omega_m / 0.3)


# ---------------------------------------------------------------------------
# Pixel-level verification  (§1.3)
# ---------------------------------------------------------------------------
def pixel_level_check(rtol: float = 1e-4) -> bool:
    """Verify EFC → ΛCDM when A_mu = A_Sigma = 0 or g(a)→0.

    Returns True if all checks pass (deviations ≤ 0.01%).
    """
    k = np.linspace(0.001, 1.0, 500)
    a = np.linspace(0.3, 1.0, 200)

    # Check 1: amplitudes zero
    mu_zero = mu_efc(k, a, A_mu=0.0)
    sig_zero = sigma_efc(k, a, A_Sigma=0.0)
    ok1 = np.allclose(mu_zero, 1.0, atol=0, rtol=rtol)
    ok2 = np.allclose(sig_zero, 1.0, atol=0, rtol=rtol)

    # Check 2: at >> 1  ⟹  g(a) ≈ 0 for all observable a
    mu_far = mu_efc(k, a, A_mu=-0.15, at=10.0)
    sig_far = sigma_efc(k, a, A_Sigma=0.15, at=10.0)
    ok3 = np.allclose(mu_far, 1.0, atol=0, rtol=rtol)
    ok4 = np.allclose(sig_far, 1.0, atol=0, rtol=rtol)

    passed = ok1 and ok2 and ok3 and ok4
    return passed


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Running pixel-level verification (§1.3) ...")
    ok = pixel_level_check()
    status = "PASS" if ok else "FAIL – STOP: implementation error"
    print(f"  Pixel-level check: {status}")

    # Spot values
    a_test = np.array([0.5, 0.7, 0.9, 1.0])
    k_test = np.array([0.01, 0.05, 0.1, 0.5])
    print("\ng(a) at test points:", gate_function(a_test))
    print("f_k(k) at test points:", scale_filter(k_test))
    print("\nμ(k,a) with A_mu=-0.10:")
    print(mu_efc(k_test, a_test, A_mu=-0.10))
    print("\nΣ(k,a) with A_Sigma=0.10:")
    print(sigma_efc(k_test, a_test, A_Sigma=0.10))
    print("\nVariantH Σ (α=1, A_mu=-0.10):")
    print(sigma_variant_h(k_test, a_test, A_mu=-0.10))
    print("\nS8(0.81, 0.31) =", S8(0.81, 0.31))
