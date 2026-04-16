"""
EFC Lensing Engine — From the Relativistic Action
==================================================

Computes the effective lensing coupling Sigma(k,z) from the EFC action
(DOI: 10.6084/m9.figshare.31876324).

This replaces the previous stub. The engine computes three quantities:
    mu(k,z)    — Poisson coupling (governs growth/RSD)
    eta(k,z)   — gravitational slip Phi/Psi
    Sigma(k,z) — lensing coupling (governs weak lensing/CMB lensing)

The EFC mechanism that produces mu < 1 AND Sigma > 1 simultaneously:
    - Stiffness (K(rho) in denominator) brakes growth via R(k,z) -> mu < 1
    - Flow-constraint anisotropy (lambda term) boosts lensing -> eta > 1
    - V'(phi) drives lambda_dot above background balance -> breaks cancellation
    - Sigma = mu*(1+eta)/2 > 1 because eta-boost > mu-suppression

This is NOT standard Horndeski. The Lagrange multiplier generates
anisotropic stress absent in standard scalar-tensor theories.

Regime validity: quasi-static, sub-horizon (k >> aH).
RCMP: Each output is tagged with its regime classification.

Reference: DOI 10.6084/m9.figshare.31876324 (Eq. 24-32, 46-50)
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple
from .base_engine import EFCEngine


# ======================================================================
#  Action Parameters
# ======================================================================

@dataclass
class EFCLensingParams:
    """Physical parameters from the EFC action.

    Once frozen, these determine ALL (mu, Sigma, eta) predictions.
    No per-observable tuning is permitted.
    """
    # Coupling
    alpha: float = 0.012         # F(phi) = 1 + alpha*phi, |alpha*phi| << 1

    # Kinetic stiffness
    K0: float = 1.37             # stiffness scale
    rho_crit: float = 94.5       # screening density (100 * rho_bar_0)

    # Entropy production
    gamma0: float = 5.13         # production rate

    # Potential gradient (V'(phi) — drives lambda above background balance)
    V_prime: float = 0.61        # in H0=1 units; V'/H^2 ~ 0.35

    # Cosmology
    Omega_m: float = 0.315
    H0: float = 67.4             # km/s/Mpc (used for unit context only)


# ======================================================================
#  Regime Classification (RCMP)
# ======================================================================

def classify_regime(R: float, slip: float) -> str:
    """Classify the physical regime at a given (k,z) point.

    Returns one of:
        "GR"        — R < 0.01, slip < 0.01: indistinguishable from GR
        "VALLEY"    — 0.01 < R < 0.2, 0.02 < slip < 0.15: observable EFC
        "STIFFNESS" — R > 0.2: stiffness-dominated, slip may diverge
        "EXTREME"   — R > 10: deep modification, QS may break down
    """
    if R > 10.0:
        return "EXTREME"
    if R > 0.2:
        return "STIFFNESS"
    if R > 0.01 and 0.02 < slip < 0.15:
        return "VALLEY"
    return "GR"


# ======================================================================
#  Core Computation
# ======================================================================

def _compute_background(a: float, p: EFCLensingParams) -> dict:
    """Background quantities at scale factor a. Units: H0=1, M_Pl=1."""
    Om = p.Omega_m
    E2 = Om * a**(-3) + (1.0 - Om)
    E = np.sqrt(E2)
    H = E

    rho = 3.0 * Om * a**(-3)
    rr = rho / p.rho_crit
    F = 1.0 + p.alpha

    # K(rho)
    denom_K = max(1.0 - rho / p.rho_crit, 1e-10)
    K_rho = p.K0 / denom_K

    # Gamma, Gamma'
    Gamma = p.gamma0 * rr / (1.0 + rr)
    Gamma_prime = p.gamma0 / p.rho_crit / (1.0 + rr)**2

    # phi_dot from constraint slow-roll
    phi_dot = Gamma / (3.0 * H)

    # K_dot = dK/dt = (dK/drho)*rho_dot, rho_dot = -3*H*rho
    K_dot = p.K0 / denom_K**2 / p.rho_crit * (-3.0 * H * rho)

    # Ricci scalar
    Om_a = Om * a**(-3) / E2
    R_ricci = 6.0 * H**2 * (2.0 - 1.5 * Om_a)

    # lambda_dot from full Eq. 10
    Ricci_term = 0.5 * p.alpha * R_ricci
    K_bracket = K_dot * phi_dot + K_rho * Gamma
    lambda_dot = (p.V_prime - Ricci_term - K_bracket) / (3.0 * H)

    return {
        'a': a, 'E': E, 'H': H, 'F': F,
        'rho': rho, 'rr': rr,
        'K_rho': K_rho, 'K_dot': K_dot,
        'Gamma': Gamma, 'Gamma_prime': Gamma_prime,
        'phi_dot': phi_dot, 'lambda_dot': lambda_dot,
        'R_ricci': R_ricci,
    }


def compute_mu_eta_sigma(k: float, z: float,
                         p: Optional[EFCLensingParams] = None) -> dict:
    """Compute (mu, eta, Sigma) at a single (k, z) point.

    Returns dict with all quantities plus diagnostics.
    """
    if p is None:
        p = EFCLensingParams()

    a = 1.0 / (1.0 + z)
    bg = _compute_background(a, p)

    F = bg['F']
    K_rho = bg['K_rho']
    phi_dot = bg['phi_dot']
    lambda_dot = bg['lambda_dot']
    Gamma_prime = bg['Gamma_prime']

    # Common factor for epsilon parameters
    common = a**2 * Gamma_prime / (F * k**2)

    # Epsilon parameters (Eq. 24-26)
    eps_F = p.alpha * phi_dot * common
    eps_lambda = lambda_dot * common
    eps_K = K_rho * phi_dot * common

    # Stiffness response R (Eq. 29, 50)
    R = K_rho * a**4 * Gamma_prime**2 * phi_dot**2 / (F * k**4)

    # Slip (Eq. 27)
    slip = eps_F + eps_lambda - eps_K

    # mu (Eq. 28)
    mu = (1.0 + eps_F) / (F * (1.0 + R))

    # eta — exact form (Eq. 27)
    if abs(slip) < 0.99:
        eta = (1.0 + slip) / (1.0 - slip)
    else:
        eta = np.inf if slip > 0 else 0.0

    # Sigma (Eq. 31)
    sigma = mu * (1.0 + eta) / 2.0 if np.isfinite(eta) else np.inf

    regime = classify_regime(R, slip)

    return {
        'k': k, 'z': z, 'a': a,
        'mu': mu, 'eta': eta, 'sigma': sigma,
        'R': R, 'slip': slip,
        'eps_F': eps_F, 'eps_lambda': eps_lambda, 'eps_K': eps_K,
        'regime': regime,
        'lambda_dot': lambda_dot,
        'Kphi_dot': K_rho * phi_dot,
        'delta_lambda': lambda_dot - K_rho * phi_dot,
    }


# ======================================================================
#  EFCLensing Engine (replaces stub)
# ======================================================================

class EFCLensing(EFCEngine):
    """
    Compute Sigma(k,z) from EFC action parameters.

    This is the physics-based lensing engine derived from
    DOI 10.6084/m9.figshare.31876324.

    Usage:
        engine = EFCLensing()
        # coordinates: (N,2) array of (k, z) pairs
        sigma_values = engine.compute(params_dict, coordinates)

    Where params_dict contains EFCLensingParams fields:
        alpha, K0, rho_crit, gamma0, V_prime, Omega_m
    """

    REQUIRED_PARAMS = ["alpha", "K0", "rho_crit", "gamma0", "V_prime", "Omega_m"]

    def __init__(self, params: Optional[EFCLensingParams] = None):
        self._params = params or EFCLensingParams()

    @property
    def name(self) -> str:
        return "lensing-efc-action"

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """
        Compute Sigma(k,z) at (k,z) coordinate pairs.

        Parameters:
            params_dict: EFC action parameters (overrides defaults)
            coordinates: (N,2) array where col0=k [h/Mpc], col1=z

        Returns:
            (N,) array of Sigma(k,z) values
        """
        p = EFCLensingParams(
            alpha=params_dict.get("alpha", self._params.alpha),
            K0=params_dict.get("K0", self._params.K0),
            rho_crit=params_dict.get("rho_crit", self._params.rho_crit),
            gamma0=params_dict.get("gamma0", self._params.gamma0),
            V_prime=params_dict.get("V_prime", self._params.V_prime),
            Omega_m=params_dict.get("Omega_m", self._params.Omega_m),
        )

        coords = np.atleast_2d(coordinates)
        if coords.shape[1] != 2:
            raise ValueError(f"coordinates must be (N,2), got shape {coords.shape}")

        result = np.zeros(len(coords))
        for i, (k, z) in enumerate(coords):
            r = compute_mu_eta_sigma(float(k), float(z), p)
            result[i] = r['sigma']

        return result

    def compute_full(self, params_dict: dict,
                     coordinates: np.ndarray) -> List[dict]:
        """Compute full diagnostics at each (k,z) point.

        Returns list of dicts with mu, eta, sigma, regime, etc.
        """
        p = EFCLensingParams(
            alpha=params_dict.get("alpha", self._params.alpha),
            K0=params_dict.get("K0", self._params.K0),
            rho_crit=params_dict.get("rho_crit", self._params.rho_crit),
            gamma0=params_dict.get("gamma0", self._params.gamma0),
            V_prime=params_dict.get("V_prime", self._params.V_prime),
            Omega_m=params_dict.get("Omega_m", self._params.Omega_m),
        )

        coords = np.atleast_2d(coordinates)
        return [compute_mu_eta_sigma(float(k), float(z), p)
                for k, z in coords]


# ======================================================================
#  Built-in Kill Tests (run BEFORE trusting any result)
# ======================================================================

def run_kill_tests(p: Optional[EFCLensingParams] = None) -> dict:
    """Run the 4 critical robustness tests.

    Tests:
        KT-A: k-integration stability (valley survives weighted average?)
        KT-B: Parameter sensitivity (10% perturbation stability)
        KT-C: GR recovery (k -> infinity gives mu=eta=Sigma=1?)
        KT-D: No divergence (R stays bounded in observable k-range?)

    Returns dict with pass/fail for each test.
    """
    if p is None:
        p = EFCLensingParams()

    results = {}
    z_test = 0.5

    # ── KT-A: k-integration stability ──────────────────────────
    # Compute weighted average over k with simple top-hat weight
    k_arr = np.logspace(-2, 0, 100)  # 0.01 to 1.0 h/Mpc
    mu_arr = []
    sigma_arr = []
    valid_count = 0

    for k in k_arr:
        r = compute_mu_eta_sigma(float(k), z_test, p)
        if r['regime'] not in ('EXTREME',) and np.isfinite(r['mu']):
            mu_arr.append(r['mu'])
            sigma_arr.append(r['sigma'])
            valid_count += 1

    if valid_count > 10:
        mu_avg = np.mean(mu_arr)
        sigma_avg = np.mean(sigma_arr)
        # Valley signal must survive averaging
        kt_a = {
            'passed': mu_avg < 1.0 and sigma_avg > 1.0,
            'mu_avg': float(mu_avg),
            'sigma_avg': float(sigma_avg),
            'n_valid': valid_count,
            'note': 'Valley survives k-average' if mu_avg < 1.0 and sigma_avg > 1.0
                    else 'Valley washed out by k-integration',
        }
    else:
        kt_a = {'passed': False, 'note': 'Too few valid k-points'}
    results['KT_A_k_integration'] = kt_a

    # ── KT-B: Parameter sensitivity (10% perturbation) ─────────
    ref = compute_mu_eta_sigma(0.08, z_test, p)
    perturbations = {
        'K0': p.K0 * 1.1,
        'gamma0': p.gamma0 * 1.1,
        'alpha': p.alpha * 1.1,
        'V_prime': p.V_prime * 1.1,
    }
    max_delta_mu = 0
    max_delta_sigma = 0
    for param_name, new_val in perturbations.items():
        p_pert = EFCLensingParams(
            alpha=new_val if param_name == 'alpha' else p.alpha,
            K0=new_val if param_name == 'K0' else p.K0,
            rho_crit=p.rho_crit,
            gamma0=new_val if param_name == 'gamma0' else p.gamma0,
            V_prime=new_val if param_name == 'V_prime' else p.V_prime,
            Omega_m=p.Omega_m,
        )
        r_pert = compute_mu_eta_sigma(0.08, z_test, p_pert)
        d_mu = abs(r_pert['mu'] - ref['mu'])
        d_sig = abs(r_pert['sigma'] - ref['sigma'])
        max_delta_mu = max(max_delta_mu, d_mu)
        max_delta_sigma = max(max_delta_sigma, d_sig)

    # 10% parameter change should not cause >50% change in output
    kt_b = {
        'passed': max_delta_mu < 0.5 * abs(1.0 - ref['mu'])
                  and max_delta_sigma < 0.5 * abs(ref['sigma'] - 1.0),
        'max_delta_mu': float(max_delta_mu),
        'max_delta_sigma': float(max_delta_sigma),
        'ref_mu': float(ref['mu']),
        'ref_sigma': float(ref['sigma']),
    }
    results['KT_B_sensitivity'] = kt_b

    # ── KT-C: GR recovery at high k ───────────────────────────
    r_highk = compute_mu_eta_sigma(10.0, z_test, p)
    kt_c = {
        'passed': (abs(r_highk['mu'] - 1.0) < 0.001
                   and abs(r_highk['eta'] - 1.0) < 0.001
                   and abs(r_highk['sigma'] - 1.0) < 0.001),
        'mu_at_k10': float(r_highk['mu']),
        'eta_at_k10': float(r_highk['eta']),
        'sigma_at_k10': float(r_highk['sigma']),
    }
    results['KT_C_GR_recovery'] = kt_c

    # ── KT-D: No divergence in observable range ────────────────
    max_R = 0
    divergent = False
    for k in np.logspace(-2, 0, 50):
        r = compute_mu_eta_sigma(float(k), z_test, p)
        if r['R'] > max_R:
            max_R = r['R']
        if not np.isfinite(r['mu']) or abs(r['mu']) > 100:
            divergent = True

    kt_d = {
        'passed': not divergent and max_R < 100,
        'max_R_in_range': float(max_R),
        'divergent': divergent,
    }
    results['KT_D_no_divergence'] = kt_d

    # Overall
    all_passed = all(r['passed'] for r in results.values())
    results['overall_passed'] = all_passed

    return results


# ======================================================================
#  CLI
# ======================================================================

if __name__ == "__main__":
    print("EFC Lensing Engine — Kill Test Suite")
    print("=" * 60)

    p = EFCLensingParams()  # best-fit from sweep
    results = run_kill_tests(p)

    for name, r in results.items():
        if name == 'overall_passed':
            continue
        status = "PASS" if r['passed'] else "FAIL"
        print(f"\n  [{status}] {name}")
        for key, val in r.items():
            if key != 'passed':
                print(f"    {key}: {val}")

    print(f"\n{'='*60}")
    print(f"  OVERALL: {'ALL PASSED' if results['overall_passed'] else 'FAILED'}")
    print(f"{'='*60}")

    # Show valley profile
    print(f"\nValley profile at z=0.5:")
    print(f"  {'k':>8} {'regime':>10} {'mu':>8} {'eta':>8} {'Sigma':>8} {'R':>8}")
    for k in [0.01, 0.02, 0.05, 0.08, 0.1, 0.2, 0.5, 1.0]:
        r = compute_mu_eta_sigma(k, 0.5, p)
        print(f"  {k:8.3f} {r['regime']:>10} {r['mu']:8.4f} "
              f"{r['eta']:8.4f} {r['sigma']:8.4f} {r['R']:8.4f}")
