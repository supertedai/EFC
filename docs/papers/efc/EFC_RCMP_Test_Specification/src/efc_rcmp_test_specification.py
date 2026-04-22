"""efc_rcmp_test_specification.py

Reference implementation of the EFC-ΛCDM Comparative Test Specification v1.1
(Magnusson 2026, DOI: 10.6084/m9.figshare.32080083).

Implements the (μ, Σ) phenomenological parametrization, gate function,
scale filter, pixel-level checks, and S8 derived parameter.
"""
import numpy as np
from typing import Tuple, Optional

# ---------------------------------------------------------------------------
# Locked gate / filter constants (Table in §1.2)
# ---------------------------------------------------------------------------
A_T: float = 0.7          # scale-factor at transition
DELTA_A: float = 0.08     # regime-transition width
K_C: float = 0.05         # h/Mpc  – pivot wavenumber

# EFC-VariantH slip constraint
ALPHA_SLIP: float = 1.0   # locked

# Pixel-level tolerance (§1.3)
PIXEL_TOL: float = 1.0e-4  # 0.01 %


def gate_function(a: np.ndarray, a_t: float = A_T, delta_a: float = DELTA_A) -> np.ndarray:
    """Temporal gate  g(a) = 0.5 * [1 + tanh((a - a_t) / delta_a)]   (Eq. 1)"""
    return 0.5 * (1.0 + np.tanh((a - a_t) / delta_a))


def scale_filter(k: np.ndarray, k_c: float = K_C) -> np.ndarray:
    """Scale filter   f_k(k) = [1 + (k/k_c)^2]^{-1}               (Eq. 2)"""
    return 1.0 / (1.0 + (k / k_c) ** 2)


def mu(k: np.ndarray, a: np.ndarray,
       A_mu: float = 0.0,
       a_t: float = A_T, delta_a: float = DELTA_A,
       k_c: float = K_C) -> np.ndarray:
    """Modified gravity function μ(k,a)  (Eq. 3).

    Parameters
    ----------
    k : array  – wavenumber(s) in h/Mpc
    a : array  – scale factor(s), broadcastable with *k*
    A_mu : float – free EFC amplitude (default 0 → ΛCDM)
    """
    return 1.0 + A_mu * gate_function(a, a_t, delta_a) * scale_filter(k, k_c)


def sigma(k: np.ndarray, a: np.ndarray,
         A_sigma: float = 0.0,
         a_t: float = A_T, delta_a: float = DELTA_A,
         k_c: float = K_C) -> np.ndarray:
    """Modified gravity function Σ(k,a)  (Eq. 4)."""
    return 1.0 + A_sigma * gate_function(a, a_t, delta_a) * scale_filter(k, k_c)


def sigma_variant_h(k: np.ndarray, a: np.ndarray,
                    A_mu: float = 0.0,
                    alpha: float = ALPHA_SLIP,
                    **kw) -> np.ndarray:
    """EFC-VariantH slip constraint: Σ = 1 − α·(μ − 1)."""
    return 1.0 - alpha * (mu(k, a, A_mu, **kw) - 1.0)


def S8(sigma8: float, Omega_m: float) -> float:
    """Derived parameter  S8 ≡ σ8 · (Ωm / 0.3)^0.5 ."""
    return sigma8 * np.sqrt(Omega_m / 0.3)


# ---------------------------------------------------------------------------
# Pixel-level verification (§1.3)
# ---------------------------------------------------------------------------
def pixel_level_check_null(k: np.ndarray, a: np.ndarray,
                           tol: float = PIXEL_TOL) -> bool:
    """Verify EFC(Aμ=0, AΣ=0) == ΛCDM within *tol* fractional error."""
    mu_vals = mu(k, a, A_mu=0.0)
    sig_vals = sigma(k, a, A_sigma=0.0)
    ok_mu = np.all(np.abs(mu_vals - 1.0) <= tol)
    ok_sig = np.all(np.abs(sig_vals - 1.0) <= tol)
    return bool(ok_mu and ok_sig)


def pixel_level_check_gate_off(k: np.ndarray, a: np.ndarray,
                                A_mu: float = -0.10, A_sigma: float = 0.10,
                                a_t_far: float = 5.0,
                                tol: float = PIXEL_TOL) -> bool:
    """Verify that when a_t >> 1 the gate suppresses EFC → ΛCDM."""
    mu_vals = mu(k, a, A_mu=A_mu, a_t=a_t_far)
    sig_vals = sigma(k, a, A_sigma=A_sigma, a_t=a_t_far)
    ok_mu = np.all(np.abs(mu_vals - 1.0) <= tol)
    ok_sig = np.all(np.abs(sig_vals - 1.0) <= tol)
    return bool(ok_mu and ok_sig)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    k_test = np.logspace(-3, 0, 200)   # h/Mpc
    a_test = np.linspace(0.2, 1.0, 100)
    K, A = np.meshgrid(k_test, a_test)

    # 1) Null check
    assert pixel_level_check_null(K, A), 'Pixel-level null check FAILED'
    print('[PASS] Pixel-level null check (Aμ=AΣ=0 → ΛCDM)')

    # 2) Gate-off check
    assert pixel_level_check_gate_off(K, A), 'Pixel-level gate-off check FAILED'
    print('[PASS] Pixel-level gate-off check (a_t >> 1 → ΛCDM)')

    # 3) Spot values
    a0 = np.array([0.7])
    k0 = np.array([0.05])
    g_val = gate_function(a0)[0]
    f_val = scale_filter(k0)[0]
    print(f'g(a=0.7) = {g_val:.6f}  (expect 0.5)')
    print(f'f_k(k=k_c) = {f_val:.6f}  (expect 0.5)')
    print(f'μ(k_c, 0.7, Aμ=-0.10) = {mu(k0, a0, A_mu=-0.10)[0]:.6f}')
    print(f'Σ(k_c, 0.7, AΣ=+0.10) = {sigma(k0, a0, A_sigma=0.10)[0]:.6f}')
    print(f'S8(σ8=0.81, Ωm=0.30) = {S8(0.81, 0.30):.4f}')
    print('\nAll self-tests passed.')
