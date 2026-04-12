"""
EFC Modified Gravity Functions: mu(k,z), Sigma(k,z), eta(k,z)
========================================================
Canonical implementation from Scale-Localised Modified Gravity.
DOI: 10.6084/m9.figshare.31985313

Equations (frozen):
  R(k,a) = R_0 * (k/k_c)^2 / (1+(k/k_c)^2)^3 * a^4      (Eq. 1)
  mu(k,z) = 1 / [F * (1 + R(k,a))]                         (Eq. 2)
  eta(k,z) = 1 + 2*eps_tot * (k/k_c)^2 / (1+(k/k_c)^2)^2 * a^2  (Eq. 3)
  Sigma(k,z) = mu * (1+eta) / 2                             (Eq. 4)
  E_G(k,z) = Omega_m * Sigma / (f * mu)                     (Eq. 5)
"""
import numpy as np
from typing import Tuple, Optional

R_0 = 0.510
K_C = 0.05
F = 1.00005
EPS_TOT = 0.40
OMEGA_M = 0.3153

def stiffness_response(k, z, R0=R_0, kc=K_C):
    k = np.atleast_1d(np.asarray(k, dtype=np.float64))
    z = np.atleast_1d(np.asarray(z, dtype=np.float64))
    a = 1.0 / (1.0 + z)
    x = k / kc
    return R0 * x**2 / (1.0 + x**2)**3 * a**4

def mu_efc(k, z, R0=R_0, kc=K_C):
    R = stiffness_response(k, z, R0, kc)
    return 1.0 / (F * (1.0 + R))

def eta_efc(k, z, eps_tot=EPS_TOT, kc=K_C):
    k = np.atleast_1d(np.asarray(k, dtype=np.float64))
    z = np.atleast_1d(np.asarray(z, dtype=np.float64))
    a = 1.0 / (1.0 + z)
    x = k / kc
    return 1.0 + 2.0 * eps_tot * x**2 / (1.0 + x**2)**2 * a**2

def sigma_efc(k, z, R0=R_0, kc=K_C, eps_tot=EPS_TOT):
    mu_val = mu_efc(k, z, R0, kc)
    eta_val = eta_efc(k, z, eps_tot, kc)
    return mu_val * (1.0 + eta_val) / 2.0

def eg_efc(k, z, f_z=None, omega_m=OMEGA_M, R0=R_0, kc=K_C, eps_tot=EPS_TOT):
    k = np.atleast_1d(np.asarray(k, dtype=np.float64))
    z = np.atleast_1d(np.asarray(z, dtype=np.float64))
    if f_z is None:
        omega_m_z = omega_m * (1 + z)**3 / (omega_m * (1 + z)**3 + (1 - omega_m))
        f_z = omega_m_z**0.55
    mu_val = mu_efc(k, z, R0, kc)
    sig_val = sigma_efc(k, z, R0, kc, eps_tot)
    return omega_m * sig_val / (f_z * mu_val)

def eg_gr(z, omega_m=OMEGA_M):
    z = np.atleast_1d(np.asarray(z, dtype=np.float64))
    omega_m_z = omega_m * (1 + z)**3 / (omega_m * (1 + z)**3 + (1 - omega_m))
    f = omega_m_z**0.55
    return omega_m / f

def all_mg_functions(k, z):
    return mu_efc(k, z), eta_efc(k, z), sigma_efc(k, z)

def mgcamb_mu_sigma(a, k_mpc, params=None):
    """MGCAMB/hi_class interface: takes a, k[1/Mpc], returns (mu, sigma).

    Unit conversion: k[h/Mpc] = k[1/Mpc] / h
    Because: 1 h/Mpc = h/Mpc, so k[1/Mpc] = k[h/Mpc] * h
    Therefore: k[h/Mpc] = k[1/Mpc] / h
    """
    if params is None:
        params = {}
    h = params.get('h', 0.6736)
    k_hmpc = k_mpc / h  # CORRECT: k[h/Mpc] = k[1/Mpc] / h
    z = 1.0 / a - 1.0
    mu_val = mu_efc(k_hmpc, z, params.get('R0', R_0), params.get('kc', K_C))
    sig_val = sigma_efc(k_hmpc, z, params.get('R0', R_0), params.get('kc', K_C), params.get('eps_tot', EPS_TOT))
    return mu_val, sig_val

KILL_CRITERIA = {
    "KC3_S8": {"threshold": "|S8_EFC - S8_LCDM| < 0.005", "survey": "Euclid DR1"},
    "KC4_slip": {"threshold": "|eta - 1| < 0.01 at z in [0.5, 2.0]", "survey": "Euclid DR1"},
    "KC5_DE": {"threshold": "|w0 + 1| < 0.02", "survey": "Euclid DR1"},
}

if __name__ == "__main__":
    k_test = np.array([K_C])
    z_test = np.array([0.0])
    mu, eta, sig = all_mg_functions(k_test, z_test)
    print(f"At k_c = {K_C} h/Mpc, z = 0:")
    print(f"  R(k_c, a=1) = {stiffness_response(k_test, z_test)[0]:.6f}")
    print(f"  mu = {mu[0]:.4f}  (paper: 0.940)")
    print(f"  eta = {eta[0]:.4f}  (paper: 1.200)")
    print(f"  Sigma = {sig[0]:.4f}  (paper: 1.034)")
    eg = eg_efc(k_test, z_test)
    eg_ref = eg_gr(z_test)
    bump = (eg[0] / eg_ref[0] - 1) * 100
    print(f"  E_G bump: {bump:.1f}%  (paper: 5-7%)")
