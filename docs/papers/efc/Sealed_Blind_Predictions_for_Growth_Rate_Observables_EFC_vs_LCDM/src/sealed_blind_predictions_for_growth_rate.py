"""sealed_blind_predictions_for_growth_rate.py

Reference implementation for:
  Sealed Blind Predictions for Growth-Rate Observables:
  Energy-Flow Cosmology vs LCDM
  DOI: 10.6084/m9.figshare.32013156

Key physics: EFC modifies the linear growth equation by an entropy-driven
coupling alpha that alters the Hubble friction term.  A negative alpha
suppresses structure growth at late times (z < ~1).

Standard linear growth ODE (LCDM):
  f''(a) + [3/a + E'(a)/E(a)] f'(a) - 3 Omega_m0 / (2 a^5 E(a)^2) f(a) = 0

EFC replaces the friction prefactor:
  friction_coeff -> (3 + alpha) / a + E'(a)/E(a)

where alpha is the EFC entropy-coupling parameter (alpha=0 recovers LCDM).
"""
import numpy as np
from typing import Tuple

# --------------- Cosmological constants (Planck 2018 + LCDM baseline) -------
OMEGA_M0: float = 0.3111
OMEGA_L0: float = 1.0 - OMEGA_M0
H0: float = 67.66          # km/s/Mpc
SIGMA8_0: float = 0.8102   # z=0 normalisation

# --------------- EFC parameters from sealed freezes -------------------------
ALPHA_PRIMARY: float = -0.689    # freeze 2026-02-18
ALPHA_SECONDARY: float = -0.702  # freeze 2026-02-21
CROSSOVER_Z: float = 2.042       # f*sigma8 crossover redshift

# --------------- Sealed predictions (Table 2) -------------------------------
PREDICTIONS = {
    "fsigma8_z0.7":  {"efc": 0.430, "lcdm": 0.449, "separation_sigma": 2.0},
    "DH_rd_z0.7":    {"efc": 19.797, "lcdm": 20.719, "separation_sigma": 2.3},
    "DH_rd_z1.0":    {"efc": 16.527, "lcdm": 17.466, "separation_sigma": 3.1},
}


def E_squared(a: float, omega_m: float = OMEGA_M0) -> float:
    """Dimensionless Hubble parameter squared: E^2(a) = Omega_m/a^3 + Omega_L."""
    return omega_m / a**3 + (1.0 - omega_m)


def E(a: float, omega_m: float = OMEGA_M0) -> float:
    return np.sqrt(E_squared(a, omega_m))


def dE_da(a: float, omega_m: float = OMEGA_M0) -> float:
    """dE/da via analytic derivative of E = sqrt(Om/a^3 + OL)."""
    Esq = E_squared(a, omega_m)
    return -1.5 * omega_m / a**4 / np.sqrt(Esq)


def growth_ode(y: np.ndarray, a: float, omega_m: float,
               alpha: float) -> np.ndarray:
    """RHS of the linear growth ODE in scale-factor variable.

    y = [D, dD/da]
    EFC modification: friction coefficient (3+alpha)/a  instead of 3/a.
    """
    D, dDda = y
    Ea = E(a, omega_m)
    dEa = dE_da(a, omega_m)
    friction = (3.0 + alpha) / a + dEa / Ea
    source = 1.5 * omega_m / (a**5 * Ea**2)
    d2Dda2 = -friction * dDda + source * D
    return np.array([dDda, d2Dda2])


def solve_growth(alpha: float = 0.0, omega_m: float = OMEGA_M0,
                 a_init: float = 1e-3, a_final: float = 1.0,
                 n_steps: int = 5000) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Integrate the growth ODE from a_init to a_final (simple RK4).

    Returns (a_array, D_array, f_array) where f = d ln D / d ln a.
    """
    a_arr = np.linspace(a_init, a_final, n_steps)
    da = a_arr[1] - a_arr[0]
    # Initial conditions: matter-dominated D ~ a, dD/da ~ 1
    y = np.array([a_init, 1.0])
    D_arr = np.zeros(n_steps)
    dDda_arr = np.zeros(n_steps)
    D_arr[0] = y[0]
    dDda_arr[0] = y[1]
    for i in range(1, n_steps):
        a = a_arr[i - 1]
        k1 = growth_ode(y, a, omega_m, alpha)
        k2 = growth_ode(y + 0.5 * da * k1, a + 0.5 * da, omega_m, alpha)
        k3 = growth_ode(y + 0.5 * da * k2, a + 0.5 * da, omega_m, alpha)
        k4 = growth_ode(y + da * k3, a + da, omega_m, alpha)
        y = y + da / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        D_arr[i] = y[0]
        dDda_arr[i] = y[1]
    f_arr = a_arr * dDda_arr / D_arr  # f = a/D * dD/da
    return a_arr, D_arr, f_arr


def fsigma8(z: float, alpha: float = 0.0,
           sigma8_0: float = SIGMA8_0,
           omega_m: float = OMEGA_M0) -> float:
    """Compute f*sigma8 at redshift z for given EFC alpha."""
    a_arr, D_arr, f_arr = solve_growth(alpha=alpha, omega_m=omega_m)
    a_target = 1.0 / (1.0 + z)
    D_interp = np.interp(a_target, a_arr, D_arr)
    f_interp = np.interp(a_target, a_arr, f_arr)
    D0 = D_arr[-1]  # D(a=1)
    sigma8_z = sigma8_0 * D_interp / D0
    return float(f_interp * sigma8_z)


def DH_over_rd(z: float, omega_m: float = OMEGA_M0,
              rd: float = 147.09) -> float:
    """Hubble distance ratio DH/rd = c/(H(z)*rd) in Mpc units.

    rd ~ 147.09 Mpc (Planck 2018 sound horizon).
    """
    a = 1.0 / (1.0 + z)
    Hz = H0 * E(a, omega_m)  # km/s/Mpc
    c_km_s = 299792.458
    DH = c_km_s / Hz  # Mpc
    return DH / rd


# ======================== Self-test ==========================================
if __name__ == "__main__":
    print("=== Self-test: sealed blind predictions ===")
    # LCDM baseline
    fs8_lcdm_07 = fsigma8(0.7, alpha=0.0)
    print(f"LCDM  f*sigma8(z=0.7) = {fs8_lcdm_07:.4f}  (paper: 0.449)")
    # EFC primary
    fs8_efc_07 = fsigma8(0.7, alpha=ALPHA_PRIMARY)
    print(f"EFC   f*sigma8(z=0.7) = {fs8_efc_07:.4f}  (paper: 0.430)")
    # DH/rd checks
    dh07 = DH_over_rd(0.7)
    dh10 = DH_over_rd(1.0)
    print(f"LCDM  DH/rd(z=0.7) = {dh07:.3f}  (paper: 20.719)")
    print(f"LCDM  DH/rd(z=1.0) = {dh10:.3f}  (paper: 17.466)")
    print("Self-test complete.")
