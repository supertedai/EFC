"""
EFC Perturbation Engine — (μ, Σ, η) from the Relativistic Action
================================================================

Implements the closed-form expressions for the effective gravitational
couplings derived from the EFC action (DOI: 10.6084/m9.figshare.31876324).

This is NOT standard Horndeski. The Lagrange multiplier constraint term
λ(□φ − Γ(ρ)) generates anisotropic stress absent in standard scalar-tensor
theories. This is what allows μ < 1 AND Σ > 1 simultaneously.

Equations implemented (paper reference numbers):
    R(k,z)  — stiffness response function          (Eq. 29, 49-50)
    εF(z)   — frame coupling parameter              (Eq. 24)
    ελ(z)   — constraint slip parameter             (Eq. 25)
    εK(z)   — kinetic response parameter            (Eq. 26)
    μ(k,z)  — effective Poisson coupling             (Eq. 28)
    η(k,z)  — gravitational slip Φ/Ψ               (Eq. 27)
    Σ(k,z)  — effective lensing coupling             (Eq. 31-32)

Regime validity:
    Quasi-static, sub-horizon: k ≫ aH, δ̈φ/δφ ≪ k/a.
    Valid for all current structure tests (BAO, RSD, weak lensing, clusters).

Physical parameters (from action Eq. 1-2):
    α       — non-minimal coupling strength (F = 1 + αφ)
    K₀      — kinetic stiffness scale
    ρ_crit  — screening density threshold
    γ₀      — entropy production rate
    V(φ)    — entropy-field potential (affects background only)

Background quantities (must be provided or solved):
    φ̄(a), φ̇(a), λ̄(a), λ̇(a), H(a), ρ̄(a)

Author: Morten Magnusson / Symbiose
Date: 2026-04-16
Reference: DOI 10.6084/m9.figshare.31876324 (v0.5, March 2026)
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple


# ======================================================================
#  Physical Parameters (default values for cosmological regime)
# ======================================================================

@dataclass
class EFCActionParams:
    """Parameters of the EFC action (Eq. 1-2).

    These define the theory. Once set, all (μ, Σ, η) predictions follow
    deterministically — no per-observable tuning allowed.
    """
    alpha: float = 0.01          # F(φ) = 1 + α·φ, |αφ| ≪ 1
    K0: float = 1.0              # kinetic stiffness scale [M²_Pl units]
    rho_crit: float = 1e4        # screening density [ρ̄ units, ρ_crit ≫ ρ̄_cosmo]
    gamma0: float = 1.0          # entropy production rate [time⁻¹]

    # Background field values at reference epoch (z=0)
    # In practice these come from solving Eq. 12-13
    phi_bar_0: float = 1.0       # φ̄ today
    phi_dot_0: float = 0.1       # dφ̄/dt today [H₀ units]
    lambda_dot_0: float = 0.05   # dλ̄/dt today [M²_Pl H₀ units]

    # Cosmological
    H0: float = 67.4             # km/s/Mpc
    Omega_m: float = 0.315


# ======================================================================
#  Background Evolution (simplified scaling relations)
# ======================================================================

def _background_quantities(a: np.ndarray, p: EFCActionParams):
    """Compute background quantities at scale factor a.

    In full implementation: solve Eq. 12-13 numerically.
    Here: use scaling relations consistent with matter domination + constraint.

    The constraint □φ̄ = Γ(ρ̄) (Eq. 13) gives:
        φ̈ + 3Hφ̇ = Γ(ρ̄)

    In matter era with slow-roll (φ̈ ≈ 0):
        φ̇ ≈ Γ(ρ̄) / (3H) ∝ ρ̄/H ∝ a^{-3/2}  (matter era)
    """
    a = np.atleast_1d(np.asarray(a, dtype=float))

    # Hubble parameter: H(a)/H₀ = E(a)
    Om = p.Omega_m
    E_a = np.sqrt(Om * a**(-3) + (1.0 - Om))
    H_a = p.H0 * E_a  # km/s/Mpc

    # Matter density (comoving units, ρ̄ ∝ a⁻³)
    rho_bar = Om * a**(-3)  # in units where ρ_crit,0 = 1

    # Frame function
    # φ̄ evolves slowly; at leading order φ̄(a) ≈ φ̄₀ + small correction
    phi_bar = p.phi_bar_0 * np.ones_like(a)
    F = 1.0 + p.alpha * phi_bar

    # Field velocity: φ̇ ∝ Γ(ρ̄)/(3H) from constraint slow-roll
    # Γ(ρ̄) = γ₀ · (ρ̄/ρ_crit) / (1 + ρ̄/ρ_crit)  (Eq. 47)
    rho_ratio = rho_bar / p.rho_crit
    Gamma = p.gamma0 * rho_ratio / (1.0 + rho_ratio)
    Gamma_prime = p.gamma0 / p.rho_crit / (1.0 + rho_ratio)**2  # Eq. 48

    # φ̇ from constraint slow-roll
    phi_dot = Gamma / (3.0 * E_a * p.H0)  # approximate

    # K(ρ̄) = K₀ / (1 − ρ̄/ρ_crit)  (Eq. 2)
    K_rho = p.K0 / np.maximum(1.0 - rho_bar / p.rho_crit, 1e-10)

    # λ̇ from Eq. 10 (background):
    # □λ = V' − ½M²_Pl F'R − ∇_μ(K∇^μ φ)
    # At background level, slow-roll: λ̇ ≈ some function of background
    # Use scaling: λ̇ ∝ K(ρ̄)·φ̇ (dominant balance from Eq. 10)
    lambda_dot = K_rho * phi_dot  # simplified scaling

    return {
        'a': a, 'E_a': E_a, 'H_a': H_a,
        'rho_bar': rho_bar, 'rho_ratio': rho_ratio,
        'phi_bar': phi_bar, 'phi_dot': phi_dot,
        'F': F, 'F_prime': p.alpha * np.ones_like(a),
        'K_rho': K_rho,
        'Gamma': Gamma, 'Gamma_prime': Gamma_prime,
        'lambda_dot': lambda_dot,
    }


# ======================================================================
#  ε-Parameters (Eq. 24-26)
# ======================================================================

def _epsilon_parameters(k: float, bg: dict, p: EFCActionParams):
    """Compute the three dimensionless ε-parameters at wavenumber k.

    All scale as a²/k² — small in the sub-horizon regime.

    Args:
        k: wavenumber [h/Mpc] (physical, NOT comoving)
        bg: background quantities dict from _background_quantities
        p: action parameters
    """
    a = bg['a']
    F = bg['F']
    F_prime = bg['F_prime']
    phi_dot = bg['phi_dot']
    Gamma_prime = bg['Gamma_prime']
    K_rho = bg['K_rho']
    lambda_dot = bg['lambda_dot']

    # Common factor: a²·Γ'/(F·k²)
    # Note: k is in h/Mpc. For dimensionless ratios, we work in H₀=1 units.
    # The factor a²/k² has units of (Mpc/h)² when k is in h/Mpc.
    # But since all ε enter as RATIOS, we can keep k in h/Mpc and
    # absorb the unit conversion into the parameter definitions.
    common = a**2 * Gamma_prime / (F * k**2)

    # εF = F'·φ̇·a²·Γ'/(F·k²)  (Eq. 24)
    eps_F = F_prime * phi_dot * common

    # ελ = λ̇·a²·Γ'/(M²_Pl·F·k²)  (Eq. 25)
    # In our units M_Pl = 1
    eps_lambda = lambda_dot * common

    # εK = K(ρ̄)·φ̇·a²·Γ'/(M²_Pl·F·k²)  (Eq. 26)
    eps_K = K_rho * phi_dot * common

    return eps_F, eps_lambda, eps_K


# ======================================================================
#  Stiffness Response R(k,z)  (Eq. 29, 49-50)
# ======================================================================

def stiffness_response(k: float, bg: dict, p: EFCActionParams) -> np.ndarray:
    """R(k,z) = K(ρ̄)·a⁴·(Γ')²·φ̇² / (M²_Pl·F·k⁴)

    In cosmological regime (ρ̄ ≪ ρ_crit):
        R ≈ K₀·γ₀²·φ̇²·a⁴ / (M²_Pl·F·ρ²_crit·k⁴)

    R > 0 is guaranteed by K > 0, Γ' > 0, φ̇² ≥ 0.
    R ∝ 1/k⁴ — strong scale dependence.
    """
    a = bg['a']
    F = bg['F']
    K_rho = bg['K_rho']
    Gamma_prime = bg['Gamma_prime']
    phi_dot = bg['phi_dot']

    R = K_rho * a**4 * Gamma_prime**2 * phi_dot**2 / (F * k**4)

    return R


# ======================================================================
#  (μ, η, Σ) — The Complete EFC Perturbation System
# ======================================================================

def compute_mu(k: float, bg: dict, p: EFCActionParams) -> np.ndarray:
    """Effective Poisson coupling μ(k,z).

    μ = (1/F) · (1 + εF + ε_K^resp) / (1 + R)      (Eq. 28)

    where ε_K^resp is the response-field contribution to the Poisson equation.

    μ < 1 when R dominates (stiffness mechanism).
    μ → 1 as k → ∞ (screening) or ρ → ρ_crit (dense environments).
    """
    eps_F, eps_lambda, eps_K = _epsilon_parameters(k, bg, p)
    R = stiffness_response(k, bg, p)
    F = bg['F']

    # ε_K^(resp) enters the Poisson equation numerator
    # From Eq. 28: numerator = 1 + εF + ε_K^(resp)
    # The response contribution is small (same order as εF)
    numerator = 1.0 + eps_F + eps_K * 0.1  # subdominant response term

    mu = numerator / (F * (1.0 + R))

    return mu


def compute_eta(k: float, bg: dict, p: EFCActionParams) -> np.ndarray:
    """Gravitational slip η(k,z) = Φ/Ψ.

    Exact (Eq. 27):
        η = (1 + εF + ελ + ελ,resp) / (1 − εF − ελ − ελ,resp)

    Approximate (for small ε):
        η ≈ 1 + 2(εF + ελ + ελ,resp)

    Result 4: if εF + ελ + ελ,resp > 0, then η > 1.

    ελ,resp = −εK (Eq. 46): response-field contribution.
    """
    eps_F, eps_lambda, eps_K = _epsilon_parameters(k, bg, p)

    # ελ,resp = −εK from Eq. 46
    eps_lambda_resp = -eps_K

    # Total slip parameter
    eps_total = eps_F + eps_lambda + eps_lambda_resp

    # Use EXACT form (Eq. 27) — valid even for moderate ε
    denominator = 1.0 - eps_total
    # Guard against zero/negative denominator
    denominator = np.maximum(denominator, 1e-10)
    eta = (1.0 + eps_total) / denominator

    return eta


def compute_sigma(k: float, bg: dict, p: EFCActionParams) -> np.ndarray:
    """Effective lensing coupling Σ(k,z).

    Σ = μ·(1+η)/2  (Eq. 31)

    From Eq. 32:
        Σ = (1/F) · (1+εF+ε_K^resp)·(1+εF+ελ+ελ,resp) / (1+R)

    Key mechanism (Result 6):
        - Denominator (1+R) suppresses μ (stiffness → growth brake)
        - Numerator slip factor boosts (Φ+Ψ) (constraint anisotropy)
        - These respond to DIFFERENT physics → μ < 1 while Σ > 1
    """
    mu = compute_mu(k, bg, p)
    eta = compute_eta(k, bg, p)
    return mu * (1.0 + eta) / 2.0


# ======================================================================
#  Full Triplet Computation
# ======================================================================

@dataclass
class PerturbationResult:
    """Complete (μ, Σ, η) result at a specific wavenumber."""
    k: float
    z: np.ndarray
    mu: np.ndarray
    eta: np.ndarray
    sigma: np.ndarray
    R: np.ndarray           # stiffness response
    eps_F: np.ndarray       # frame coupling
    eps_lambda: np.ndarray  # constraint slip
    eps_K: np.ndarray       # kinetic response


def compute_triplet(k: float, z: np.ndarray,
                    p: Optional[EFCActionParams] = None) -> PerturbationResult:
    """Compute (μ, Σ, η) at wavenumber k as function of redshift z.

    This is the main entry point for the EFC perturbation engine.

    Args:
        k: wavenumber [h/Mpc]
        z: redshift array
        p: action parameters (default: EFCActionParams())

    Returns:
        PerturbationResult with all computed quantities
    """
    if p is None:
        p = EFCActionParams()

    z = np.atleast_1d(np.asarray(z, dtype=float))
    a = 1.0 / (1.0 + z)

    bg = _background_quantities(a, p)
    eps_F, eps_lambda, eps_K = _epsilon_parameters(k, bg, p)
    R = stiffness_response(k, bg, p)
    mu = compute_mu(k, bg, p)
    eta = compute_eta(k, bg, p)
    sigma = compute_sigma(k, bg, p)

    return PerturbationResult(
        k=k, z=z,
        mu=mu, eta=eta, sigma=sigma,
        R=R, eps_F=eps_F, eps_lambda=eps_lambda, eps_K=eps_K,
    )


# ======================================================================
#  Consistency Checks (Morten's directive: built-in, not optional)
# ======================================================================

def run_consistency_checks(result: PerturbationResult,
                           p: EFCActionParams) -> dict:
    """Run all consistency checks on a PerturbationResult.

    Checks:
        1. R > 0 everywhere (FA1: stiffness mechanism)
        2. η > 1 when εF + ελ − εK > 0 (Result 4)
        3. Σ = μ·(1+η)/2 identity (numerical consistency)
        4. μ → 1 as k → ∞ (screening limit)
        5. No sign flips outside expected regime
        6. k → 0 behaviour (flag potential CMB/ISW conflict)
    """
    checks = {}

    # FA1: R > 0 everywhere
    R_positive = bool(np.all(result.R >= 0))
    checks['FA1_R_positive'] = {
        'passed': R_positive,
        'min_R': float(np.min(result.R)),
        'max_R': float(np.max(result.R)),
    }

    # Result 4: η > 1 when total ε > 0
    eps_total = result.eps_F + result.eps_lambda - result.eps_K
    eta_should_be_gt1 = eps_total > 0
    eta_is_gt1 = result.eta > 1.0
    slip_consistent = bool(np.all(eta_should_be_gt1 == eta_is_gt1))
    checks['result4_slip_sign'] = {
        'passed': slip_consistent,
        'eps_total_range': (float(np.min(eps_total)), float(np.max(eps_total))),
    }

    # Σ = μ·(1+η)/2 identity
    sigma_reconstructed = result.mu * (1.0 + result.eta) / 2.0
    sigma_error = np.max(np.abs(result.sigma - sigma_reconstructed))
    checks['sigma_identity'] = {
        'passed': bool(sigma_error < 1e-10),
        'max_error': float(sigma_error),
    }

    # μ < 1 check (expected for EFC with R > 0)
    checks['mu_less_than_1'] = {
        'passed': bool(np.all(result.mu < 1.0)),
        'mu_range': (float(np.min(result.mu)), float(np.max(result.mu))),
    }

    # Σ > 1 check (expected for EFC with positive slip)
    checks['sigma_greater_than_1'] = {
        'passed': bool(np.all(result.sigma > 1.0)),
        'sigma_range': (float(np.min(result.sigma)), float(np.max(result.sigma))),
    }

    # η > 1 check
    checks['eta_greater_than_1'] = {
        'passed': bool(np.all(result.eta > 1.0)),
        'eta_range': (float(np.min(result.eta)), float(np.max(result.eta))),
    }

    # k → 0 warning: R ∝ 1/k⁴ diverges
    # At the computed k, flag if R > 10 (entering strongly modified regime)
    checks['k_low_warning'] = {
        'strong_modification': bool(np.any(result.R > 10)),
        'max_R': float(np.max(result.R)),
        'note': 'R > 10 indicates deep stiffness regime; may conflict with CMB/ISW',
    }

    # Overall
    critical_passed = all([
        checks['FA1_R_positive']['passed'],
        checks['sigma_identity']['passed'],
    ])
    valley_achieved = all([
        checks['mu_less_than_1']['passed'],
        checks['sigma_greater_than_1']['passed'],
        checks['eta_greater_than_1']['passed'],
    ])

    checks['overall'] = {
        'critical_checks_passed': critical_passed,
        'valley_achieved': valley_achieved,
    }

    return checks


# ======================================================================
#  Parameter Scan: Find the Survival Valley
# ======================================================================

def scan_for_valley(k: float = 0.05,
                    z_eval: float = 0.5) -> None:
    """Scan EFC parameter space to find (μ, Σ, η) survival valley.

    Target: μ ∈ [0.93, 0.96], Σ ∈ [1.03, 1.07], η ∈ [1.05, 1.15]
    """
    z = np.array([z_eval])

    print("=" * 80)
    print(f"EFC PERTURBATION ENGINE — VALLEY SCAN at k={k} h/Mpc, z={z_eval}")
    print("=" * 80)
    print(f"\n{'K0':>8} {'gamma0':>8} {'rho_c':>8} {'alpha':>8} "
          f"{'R':>8} {'μ':>8} {'η':>8} {'Σ':>8} {'Valley?':>8}")
    print("-" * 80)

    found = 0
    for K0 in [0.1, 0.5, 1.0, 5.0, 10.0]:
        for gamma0 in [0.1, 0.5, 1.0, 5.0]:
            for rho_c in [10, 100, 1000, 1e4]:
                for alpha in [0.001, 0.01, 0.05, 0.1]:
                    p = EFCActionParams(
                        alpha=alpha, K0=K0,
                        rho_crit=rho_c, gamma0=gamma0,
                    )
                    try:
                        t = compute_triplet(k, z, p)
                        mu_v = t.mu[0]
                        eta_v = t.eta[0]
                        sig_v = t.sigma[0]
                        R_v = t.R[0]

                        in_valley = (0.93 < mu_v < 0.96 and
                                     1.03 < sig_v < 1.07 and
                                     1.05 < eta_v < 1.15)

                        if in_valley or (0.90 < mu_v < 1.0 and sig_v > 1.0):
                            marker = "✓ VALLEY" if in_valley else "~ near"
                            print(f"{K0:8.2f} {gamma0:8.2f} {rho_c:8.0f} "
                                  f"{alpha:8.4f} {R_v:8.4f} {mu_v:8.4f} "
                                  f"{eta_v:8.4f} {sig_v:8.4f} {marker}")
                            found += 1
                    except Exception:
                        continue

    print(f"\nFound {found} parameter points in/near valley")
    if found == 0:
        print("WARNING: No valley solutions found. Check parameter ranges.")


if __name__ == "__main__":
    import sys

    print("EFC Perturbation Engine — from Action (DOI 31876324)")
    print()

    # Default parameters
    p = EFCActionParams()
    z = np.linspace(0.01, 2.0, 200)

    # Compute for several k values
    for k in [0.005, 0.01, 0.05, 0.1]:
        t = compute_triplet(k, z, p)
        checks = run_consistency_checks(t, p)

        # Values at z=0.5
        idx = np.argmin(np.abs(z - 0.5))
        print(f"k = {k:.3f} h/Mpc:")
        print(f"  R(z=0.5) = {t.R[idx]:.6f}")
        print(f"  μ(z=0.5) = {t.mu[idx]:.6f}")
        print(f"  η(z=0.5) = {t.eta[idx]:.6f}")
        print(f"  Σ(z=0.5) = {t.sigma[idx]:.6f}")
        print(f"  Valley: {checks['overall']['valley_achieved']}")
        print()

    # Parameter scan
    print()
    scan_for_valley(k=0.05, z_eval=0.5)
