"""jwst_hmf_prereg_v4.py

Reference implementation of the EFC prediction chain for the high-redshift
halo mass function (HMF) as described in:

  Pre-Registration: EFC dN/dM (z>7) — Halo Mass Function via mu(a)
  Perturbation Channel, Magnusson 2026, DOI 10.6084/m9.figshare.32149654

Chain: g(a) -> mu(a) -> D(a) -> sigma(M,z) -> n(M,z)
"""
import numpy as np
from scipy.integrate import solve_ivp, quad
from scipy.interpolate import interp1d
from typing import Tuple, Callable, Optional

# --------------- physical constants / fiducial cosmology -----------------
H0 = 67.4          # km/s/Mpc  (Planck 2018)
OMEGA_M0 = 0.315
OMEGA_L0 = 1.0 - OMEGA_M0
N_S = 0.965
SIGMA8 = 0.811
RHO_CRIT0 = 2.775e11  # h^2 Msun / Mpc^3
RHO_M0 = OMEGA_M0 * RHO_CRIT0  # h^2 Msun / Mpc^3
DELTA_C = 1.686      # spherical-collapse threshold

# --------------- EFC gate parameters (placeholders until joint S(z)-fit) --
B_DEFAULT = 0.04     # perturbation amplitude (illustrative)
ZT_DEFAULT = 3.0     # transition redshift
N_EXP_DEFAULT = 4.0  # steepness exponent


# ========================== Step 1: gate function =========================
def gate_function(a: float, zt: float = ZT_DEFAULT,
                  n: float = N_EXP_DEFAULT) -> float:
    """EFC gate function g(a) — Eq. (2)."""
    z = 1.0 / a - 1.0
    if z <= 0:
        return 1.0
    return 1.0 / (1.0 + (zt / z) ** n)


# ========================== Step 2: mu(a) =================================
def mu_eff(a: float, B: float = B_DEFAULT, zt: float = ZT_DEFAULT,
           n: float = N_EXP_DEFAULT) -> float:
    """Effective gravitational coupling mu(a) = 1 - B g(a) — Eq. (3)."""
    return 1.0 - B * gate_function(a, zt, n)


# ========================== Step 3: growth factor D(a) ====================
def _E2_lcdm(a: float) -> float:
    """(H/H0)^2 for flat LCDM."""
    return OMEGA_M0 * a**-3 + OMEGA_L0


def _delta_E2(a: float, A: float, zt: float, n: float) -> float:
    """Background EFC correction Delta E^2 — Eq. (1)."""
    return A * (gate_function(a, zt, n) - gate_function(1e-6, zt, n))


def solve_growth(B: float = B_DEFAULT, zt: float = ZT_DEFAULT,
                 n: float = N_EXP_DEFAULT,
                 A: float = 0.0,
                 a_start: float = 1e-4, a_end: float = 1.0,
                 n_pts: int = 2000) -> Tuple[np.ndarray, np.ndarray]:
    """Solve the modified linear growth ODE and return (a_arr, D_arr).

    The ODE for f = d ln D / d ln a is:
        a df/da + f^2 + f [1/2 - 3/2 w_eff(a)] - 3/2 mu(a) Omega_m(a) = 0
    For dust (w_eff ~ 0 in matter era) this simplifies; we keep the full
    expression using Omega_m(a) = Omega_m0 a^{-3} / E^2(a).

    We integrate the second-order form for delta:
        delta'' + (3/a + E'/E) delta' - 3/(2a^2) mu(a) Omega_m(a) delta = 0
    rewritten as a system in ln(a).
    """
    lna = np.linspace(np.log(a_start), np.log(a_end), n_pts)

    def rhs(lna_val, y):
        a_val = np.exp(lna_val)
        E2 = _E2_lcdm(a_val) + _delta_E2(a_val, A, zt, n)
        E2 = max(E2, 1e-30)
        Om_a = OMEGA_M0 * a_val**-3 / E2
        # d(E2)/d(lna) via finite diff
        da = a_val * 1e-5
        E2p = _E2_lcdm(a_val + da) + _delta_E2(a_val + da, A, zt, n)
        E2m = _E2_lcdm(a_val - da) + _delta_E2(a_val - da, A, zt, n)
        dE2_dlna = (E2p - E2m) / (2.0 * 1e-5)  # dE2/dlna = a dE2/da
        eps = dE2_dlna / (2.0 * E2)  # d ln E / d ln a

        mu = mu_eff(a_val, B, zt, n)
        # y = [delta, d(delta)/d(lna)]
        ddelta = y[1]
        dd_delta = -(2.0 + eps) * y[1] + 1.5 * mu * Om_a * y[0]
        return [ddelta, dd_delta]

    y0 = [a_start, a_start]  # growing mode D ~ a in matter dom.
    sol = solve_ivp(rhs, [lna[0], lna[-1]], y0, t_eval=lna,
                    rtol=1e-10, atol=1e-14, method='DOP853')
    a_arr = np.exp(sol.t)
    D_arr = sol.y[0]
    D_arr = D_arr / D_arr[-1]  # normalise D(a=1)=1
    return a_arr, D_arr


# ========================== Step 4: sigma(M, z) ===========================
def _top_hat_W(kR: np.ndarray) -> np.ndarray:
    """Fourier-space top-hat window."""
    return 3.0 * (np.sin(kR) - kR * np.cos(kR)) / kR**3


def mass_to_radius(M: float) -> float:
    """Lagrangian radius R [Mpc/h] for mass M [Msun/h]."""
    return (3.0 * M / (4.0 * np.pi * RHO_M0)) ** (1.0 / 3.0)


def _Pk_EH(k: np.ndarray) -> np.ndarray:
    """Eisenstein-Hu no-wiggle power spectrum (shape only), normalised later."""
    h = H0 / 100.0
    Omh2 = OMEGA_M0 * h**2
    Omb = 0.0493
    Obh2 = Omb * h**2
    theta = 2.7255 / 2.7  # CMB temp ratio
    s = 44.5 * np.log(9.83 / Omh2) / np.sqrt(1 + 10 * Obh2**0.75)
    alpha_g = 1 - 0.328 * np.log(431 * Omh2) * (Obh2 / Omh2) + \
              0.38 * np.log(22.3 * Omh2) * (Obh2 / Omh2)**2
    Gamma_eff = OMEGA_M0 * h * (alpha_g + (1 - alpha_g) /
                                 (1 + (0.43 * k * s)**4))
    q = k * theta**2 / Gamma_eff
    L0 = np.log(2 * np.e + 1.8 * q)
    C0 = 14.2 + 731.0 / (1 + 62.5 * q)
    T = L0 / (L0 + C0 * q**2)
    Pk = k**N_S * T**2
    return Pk


def sigma_M(M: float, D_of_z: float, k: Optional[np.ndarray] = None,
            Pk: Optional[np.ndarray] = None) -> float:
    """RMS variance sigma(M) at the scale R(M), scaled by D(z)."""
    R = mass_to_radius(M)
    if k is None:
        k = np.logspace(-4, 2, 4000)
    if Pk is None:
        Pk = _Pk_EH(k)
    W = _top_hat_W(k * R)
    integrand = k**2 * Pk * W**2 / (2.0 * np.pi**2)
    sig2_raw = np.trapz(integrand, k)
    # normalise so that sigma8 = SIGMA8 at z=0 (D=1)
    R8 = 8.0  # Mpc/h
    W8 = _top_hat_W(k * R8)
    integrand8 = k**2 * Pk * W8**2 / (2.0 * np.pi**2)
    sig2_8 = np.trapz(integrand8, k)
    norm = SIGMA8**2 / sig2_8
    sigma = np.sqrt(norm * sig2_raw) * D_of_z
    return sigma


# ========================== Step 5: n(M, z) — HMF ========================
def _dln_sigma_inv_dM(M: float, D_of_z: float, dM_frac: float = 0.01
                      ) -> float:
    """Numerical |d ln sigma^{-1} / dM|."""
    s1 = sigma_M(M * (1 + dM_frac), D_of_z)
    s0 = sigma_M(M * (1 - dM_frac), D_of_z)
    dlns_inv = -(np.log(1.0/s1) - np.log(1.0/s0))
    dM = M * 2 * dM_frac
    return abs(dlns_inv / dM)


def f_PS(sigma: float) -> float:
    """Press-Schechter multiplicity function."""
    nu = DELTA_C / sigma
    return np.sqrt(2.0 / np.pi) * nu * np.exp(-0.5 * nu**2)


def f_ST(sigma: float, A_st: float = 0.3222, a_st: float = 0.707,
         p: float = 0.3) -> float:
    """Sheth-Tormen multiplicity function."""
    nu = DELTA_C / sigma
    nu2 = a_st * nu**2
    return A_st * np.sqrt(2.0 * nu2 / np.pi) * (1 + nu2**(-p)) * \
        np.exp(-0.5 * nu2)


def f_Tinker(sigma: float, z: float = 0.0, Delta: float = 200.0) -> float:
    """Tinker 2008 multiplicity (Delta=200 calibration)."""
    # Tinker 2008 Table 2 params for Delta=200, interpolated to z
    A0, a0, b0, c0 = 0.186, 1.47, 2.57, 1.19
    # redshift evolution (Tinker 2010 approx)
    A = A0 * (1 + z)**(-0.14)
    a = a0 * (1 + z)**(-0.06)
    b = b0 * (1 + z)**(-0.0 * np.exp(-(Delta / 500)**2))  # ~constant for 200
    c = c0
    return A * ((sigma / b)**(-a) + 1) * np.exp(-c / sigma**2)


def dn_dM(M: float, z: float, D_interp: Callable, prescription: str = 'ST',
          ) -> float:
    """Comoving halo mass function dn/dM [h^4 Msun^{-1} Mpc^{-3}]."""
    a = 1.0 / (1.0 + z)
    D_val = float(D_interp(a))
    sig = sigma_M(M, D_val)
    if prescription == 'PS':
        fval = f_PS(sig)
    elif prescription == 'ST':
        fval = f_ST(sig)
    elif prescription == 'Tinker':
        fval = f_Tinker(sig, z)
    else:
        raise ValueError(f'Unknown prescription {prescription}')
    return (RHO_M0 / M) * fval * _dln_sigma_inv_dM(M, D_val)


# ========================== convenience ==================================
def build_D_interpolator(B: float = B_DEFAULT, zt: float = ZT_DEFAULT,
                         n: float = N_EXP_DEFAULT, A: float = 0.0
                         ) -> Callable:
    """Return an interpolator D(a) for given EFC parameters."""
    a_arr, D_arr = solve_growth(B, zt, n, A)
    return interp1d(a_arr, D_arr, kind='cubic', fill_value='extrapolate')


# ========================== self-test ====================================
if __name__ == '__main__':
    print('Running self-test...')
    # gate function checks
    assert abs(gate_function(1.0, 3.0, 4.0) - 1.0) < 0.01  # z=0 => g~1
    assert gate_function(0.01, 3.0, 4.0) > 0.9  # z=99 >> zt => g->1
    assert gate_function(0.5, 3.0, 4.0) < 0.1   # z=1 < zt => g small

    # mu check
    assert mu_eff(0.01) < 1.0  # suppressed at high z
    assert abs(mu_eff(0.5) - 1.0) < 0.01  # near unity at low z

    # growth
    D_interp = build_D_interpolator(B=0.0)  # LCDM limit
    a_test = 1.0 / (1.0 + 8.0)
    print(f'  D(z=8) LCDM  = {D_interp(a_test):.6f}')

    D_interp_efc = build_D_interpolator()
    print(f'  D(z=8) EFC   = {D_interp_efc(a_test):.6f}')

    # sigma
    M_test = 1e11  # Msun/h
    sig = sigma_M(M_test, D_interp_efc(a_test))
    print(f'  sigma(1e11, z=8) EFC = {sig:.6f}')

    # HMF
    dndm = dn_dM(M_test, 8.0, D_interp_efc, 'ST')
    print(f'  dn/dM(1e11, z=8) ST  = {dndm:.4e}')
    print('Self-test passed.')
