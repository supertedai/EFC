"""efc_compound_paper.py

Reference implementation for:
  'Parameter-Controlled Regime Transitions in Energy-Flow Cosmology:
   Cross-Sector Consistency Between Lensing and Background Observables'
  Magnusson 2026, DOI: 10.6084/m9.figshare.32080059

Implements the sealed EFC lensing engine (lensing.py) and P2 growth-sector
models, including:
  - V'-driven lambda dynamics vs Ricci-sourced backreaction
  - Effective gravitational couplings mu(z), eta(z), Sigma_eff(z)
  - P2 background gate function Theta(z) and growth modification mu_P2(a)
  - BBKS transfer function for cross-validation
"""
import numpy as np
from typing import Tuple, Dict

# ---------------------------------------------------------------------------
# Default parameter sets from the paper
# ---------------------------------------------------------------------------
# P1 Lensing-sector (action-level) parameters
P1_DEFAULTS: Dict[str, float] = {
    "K0": 1.37,          # kinetic stiffness scale (primary control)
    "V_prime": 0.05,     # V' potential gradient driving lambda-dynamics
    "alpha": 0.10,       # coupling constant
    "rho_crit": 1.0,     # critical density (normalised units)
    "gamma0": 0.02,      # backreaction amplitude
}

# P2 Growth-sector (phenomenological) parameters
P2_DEFAULTS: Dict[str, float] = {
    "z_t": 0.44,         # transition redshift
    "n": 4.0,            # steepness of gate function
    "mu0": 0.07,         # perturbation-level damping amplitude
}

# Pre-registered predictions
P1_CROSSOVER_Z = 0.44        # +/- 0.03
P2_FSIGMA8_Z07 = 0.430       # +/- 0.02


# ---------------------------------------------------------------------------
# P1 Lensing engine
# ---------------------------------------------------------------------------
def lambda_dynamics(z: np.ndarray, K0: float, V_prime: float,
                    alpha: float, rho_crit: float) -> np.ndarray:
    """V'-driven scalar field evolution: lambda(z).

    lambda(z) = (V_prime / K0) * (1+z)^2 - alpha * rho_crit * (1+z)^3 / K0^2

    The first term captures V'-driven dynamics; the second is Ricci-sourced
    backreaction scaling as matter density.
    """
    a = 1.0 / (1.0 + z)
    lam = (V_prime / K0) * (1.0 + z)**2 - alpha * rho_crit * (1.0 + z)**3 / K0**2
    return lam


def ricci_backreaction(z: np.ndarray, gamma0: float,
                       rho_crit: float) -> np.ndarray:
    """Ricci-sourced backreaction term B(z) = gamma0 * rho_crit * (1+z)^3."""
    return gamma0 * rho_crit * (1.0 + z)**3


def mu_lensing(z: np.ndarray, K0: float = P1_DEFAULTS["K0"],
              V_prime: float = P1_DEFAULTS["V_prime"],
              alpha: float = P1_DEFAULTS["alpha"],
              rho_crit: float = P1_DEFAULTS["rho_crit"],
              gamma0: float = P1_DEFAULTS["gamma0"]) -> np.ndarray:
    """Effective gravitational coupling mu(z) from lensing sector.

    mu = 1 + lambda(z) - B(z)
    EFC predicts mu < 1 (entropic damping of Newtonian potential).
    """
    lam = lambda_dynamics(z, K0, V_prime, alpha, rho_crit)
    B = ricci_backreaction(z, gamma0, rho_crit)
    return 1.0 + lam - B


def eta_lensing(z: np.ndarray, K0: float = P1_DEFAULTS["K0"],
               V_prime: float = P1_DEFAULTS["V_prime"],
               alpha: float = P1_DEFAULTS["alpha"],
               rho_crit: float = P1_DEFAULTS["rho_crit"],
               gamma0: float = P1_DEFAULTS["gamma0"]) -> np.ndarray:
    """Gravitational slip eta(z) = Phi/Psi deviation.

    eta = 1 + 2*lambda(z) + B(z)
    """
    lam = lambda_dynamics(z, K0, V_prime, alpha, rho_crit)
    B = ricci_backreaction(z, gamma0, rho_crit)
    return 1.0 + 2.0 * lam + B


def sigma_eff(z: np.ndarray, **kwargs) -> np.ndarray:
    """Effective weak-lensing coupling Sigma_eff(z) = mu * (1 + eta) / 2.

    P1 predicts a sign-changing crossover at z ~ 0.44.
    The sign change is the key structural prediction distinguishing EFC.
    """
    mu = mu_lensing(z, **kwargs)
    eta = eta_lensing(z, **kwargs)
    return mu * (1.0 + eta) / 2.0


def find_crossover_z(z_grid: np.ndarray, sigma_vals: np.ndarray) -> float:
    """Find redshift where Sigma_eff - 1 changes sign (crossover)."""
    delta = sigma_vals - 1.0
    sign_changes = np.where(np.diff(np.sign(delta)))[0]
    if len(sign_changes) == 0:
        return np.nan
    idx = sign_changes[0]
    # Linear interpolation
    z0, z1 = z_grid[idx], z_grid[idx + 1]
    d0, d1 = delta[idx], delta[idx + 1]
    return z0 - d0 * (z1 - z0) / (d1 - d0)


# ---------------------------------------------------------------------------
# P2 Growth sector
# ---------------------------------------------------------------------------
def gate_function(z: np.ndarray, z_t: float = P2_DEFAULTS["z_t"],
                  n: float = P2_DEFAULTS["n"]) -> np.ndarray:
    """Background gate function Theta(z) controlling regime transition.

    Theta(z) = 1 / (1 + (z/z_t)^n)
    """
    return 1.0 / (1.0 + (z / z_t)**n)


def mu_growth(z: np.ndarray, z_t: float = P2_DEFAULTS["z_t"],
             n: float = P2_DEFAULTS["n"],
             mu0: float = P2_DEFAULTS["mu0"]) -> np.ndarray:
    """Perturbation-level growth modification mu_P2(z).

    mu(z) = 1 - mu0 * Theta(z)
    EFC predicts mu < 1 (entropic damping) in both sectors.
    """
    return 1.0 - mu0 * gate_function(z, z_t, n)


def fsigma8_prediction(z: float = 0.7, sigma8_fid: float = 0.811,
                       omega_m: float = 0.315, **p2_kwargs) -> float:
    """Approximate f*sigma8 at redshift z under EFC P2 modification.

    f(z) ~ Omega_m(z)^0.55 * mu_P2(z)   (growth-rate with EFC damping)
    """
    z_arr = np.atleast_1d(z)
    Omega_m_z = omega_m * (1.0 + z_arr)**3 / (
        omega_m * (1.0 + z_arr)**3 + (1.0 - omega_m))
    f_z = Omega_m_z**0.55 * mu_growth(z_arr, **p2_kwargs)
    # Approximate sigma8(z) via linear growth normalisation
    D_z = 1.0 / (1.0 + z_arr)  # simplified linear growth
    return float(f_z[0] * sigma8_fid * D_z[0])


# ---------------------------------------------------------------------------
# BBKS transfer function (cross-validation)
# ---------------------------------------------------------------------------
def bbks_transfer(k: np.ndarray, omega_m: float = 0.315,
                  h: float = 0.674) -> np.ndarray:
    """BBKS transfer function T(k). Bardeen, Bond, Kaiser, Szalay 1986.

    q = k / (Omega_m * h^2)  [k in h/Mpc]
    T(q) = ln(1+2.34q)/(2.34q) * [1 + 3.89q + (16.1q)^2 + (5.46q)^3 + (6.71q)^4]^{-1/4}
    """
    q = k / (omega_m * h**2)
    t1 = np.log(1.0 + 2.34 * q) / (2.34 * q + 1e-30)
    t2 = (1.0 + 3.89 * q + (16.1 * q)**2 + (5.46 * q)**3 + (6.71 * q)**4)**(-0.25)
    return t1 * t2


# ---------------------------------------------------------------------------
# K0 scan utilities
# ---------------------------------------------------------------------------
def scan_K0(K0_range: np.ndarray,
            z_grid: np.ndarray = np.linspace(0.01, 2.0, 2000),
            **fixed_params) -> np.ndarray:
    """Scan crossover redshift as function of K0.

    Returns array of crossover redshifts.
    Paper reports Delta_z ~ 0.87 across K0 in [0.5, 4.0].
    """
    z_cross = np.empty_like(K0_range)
    for i, K0 in enumerate(K0_range):
        sig = sigma_eff(z_grid, K0=K0, **fixed_params)
        z_cross[i] = find_crossover_z(z_grid, sig)
    return z_cross


def scan_amplitude(scale_range: np.ndarray,
                   z_grid: np.ndarray = np.linspace(0.01, 2.0, 2000),
                   K0: float = P1_DEFAULTS["K0"]) -> np.ndarray:
    """Joint x-fold rescaling of amplitude parameters (alpha, V', gamma0).

    Paper reports Delta_z ~ 0.11 across x50 rescaling range.
    """
    z_cross = np.empty_like(scale_range)
    for i, s in enumerate(scale_range):
        sig = sigma_eff(z_grid, K0=K0,
                        V_prime=P1_DEFAULTS["V_prime"] * s,
                        alpha=P1_DEFAULTS["alpha"] * s,
                        gamma0=P1_DEFAULTS["gamma0"] * s,
                        rho_crit=P1_DEFAULTS["rho_crit"])
        z_cross[i] = find_crossover_z(z_grid, sig)
    return z_cross


# ---------------------------------------------------------------------------
# Cross-sector consistency check
# ---------------------------------------------------------------------------
def check_mu_consistency(z_check: float = 0.44) -> Dict[str, float]:
    """Compare mu from P1 (lensing) and P2 (growth) at a given redshift.

    Paper reports ~11% difference at z=0.44, but same sign (mu<1).
    """
    z_arr = np.array([z_check])
    mu_p1 = float(mu_lensing(z_arr))
    mu_p2 = float(mu_growth(z_arr))
    return {
        "z": z_check,
        "mu_P1_lensing": mu_p1,
        "mu_P2_growth": mu_p2,
        "relative_diff_pct": abs(mu_p1 - mu_p2) / abs(0.5 * (mu_p1 + mu_p2)) * 100,
        "both_less_than_1": mu_p1 < 1.0 and mu_p2 < 1.0,
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    z_test = np.linspace(0.01, 2.0, 2000)

    # Test Sigma_eff crossover at default parameters
    sig = sigma_eff(z_test)
    zc = find_crossover_z(z_test, sig)
    print(f"Sigma_eff crossover at z = {zc:.3f}  (target: {P1_CROSSOVER_Z})")

    # Test P2 fsigma8
    fs8 = fsigma8_prediction(z=0.7)
    print(f"f*sigma8(z=0.7) = {fs8:.3f}  (target: {P2_FSIGMA8_Z07})")

    # Cross-sector consistency
    cons = check_mu_consistency(0.44)
    print(f"mu_P1={cons['mu_P1_lensing']:.4f}, mu_P2={cons['mu_P2_growth']:.4f}, "
          f"diff={cons['relative_diff_pct']:.1f}%, both<1={cons['both_less_than_1']}")

    # K0 scan
    K0_vals = np.linspace(0.5, 4.0, 50)
    zc_vals = scan_K0(K0_vals)
    valid = ~np.isnan(zc_vals)
    if valid.any():
        dz = np.nanmax(zc_vals) - np.nanmin(zc_vals)
        print(f"K0 scan: Delta_z = {dz:.2f}  (paper: ~0.87)")

    print("Self-test complete.")
