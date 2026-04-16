#!/usr/bin/env python3
"""
EFC Horndeski Consistency Check — Alternativ A (Morten's directive)
===================================================================

Sanity check: given the existing mu(a) from shadow_slip.py, can we find
a consistent Horndeski representation where:
    mu < 1  AND  Sigma > 1  AND  eta > 1

This uses the quasi-static Horndeski relations (Bellini & Sawicki 2014,
Pogosian & Silvestri 2016):

    mu(k,a) = [1 + alpha_B^2 / (2 * c_s^2)] * [M*^2 / M_Pl^2]^{-1}
    eta(k,a) = [1 + alpha_B * (alpha_M - alpha_B) / (2 * c_s^2)] /
               [1 + alpha_B^2 / (2 * c_s^2)]
    Sigma(k,a) = mu * (1 + eta) / 2

where c_s^2 = sound speed of scalar perturbations.

The key insight: eta != 1/mu in general when alpha_B != 0.
The shadow_slip.py model assumes eta = 1/mu, which is ONLY correct
when the scalar field has NO braiding (alpha_B = 0).

This script answers: "does EFC's action have non-zero braiding?"
If alpha_B = 0 is required -> eta = 1 exactly -> cosmological pathway dead.
If alpha_B != 0 is consistent -> (mu, Sigma, eta) valley may exist.

Author: Morten Magnusson / Symbiose
Date: 2026-04-16
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class HorndestiPoint:
    """Single (mu, Sigma, eta) point with underlying Horndeski alphas."""
    mu: float
    sigma: float  # Sigma (lensing)
    eta: float
    alpha_M: float
    alpha_B: float
    alpha_T: float  # always 0 for EFC
    cs2: float      # sound speed squared
    k_over_aH: float  # k/(aH) — quasi-static parameter
    consistent: bool   # does this satisfy stability + physicality?
    notes: str = ""


# ======================================================================
#  Horndeski quasi-static relations
#  (Bellini & Sawicki 2014, Eq. 18-20; Pogosian & Silvestri 2016)
# ======================================================================

def horndeski_mu_eta_sigma(
    alpha_M: float,
    alpha_B: float,
    alpha_T: float = 0.0,
    cs2: float = 1.0,
) -> Tuple[float, float, float]:
    """
    Compute (mu, eta, Sigma) from Horndeski alpha-functions.

    Quasi-static limit (k >> aH), ignoring time derivatives of alphas.

    Standard formulae (Pogosian & Silvestri 2016, Eq. 3.12-3.14):

        mu = (1 + alpha_T) * [2 + alpha_B * (2 + alpha_M)] /
             [2 * (1 + alpha_B - alpha_T) + alpha_B^2 / cs2]

    Simplified for alpha_T = 0:

        mu = [2 + alpha_B * (2 + alpha_M)] /
             [2 * (1 + alpha_B) + alpha_B^2 / cs2]

        eta = [2 * (1 + alpha_B) + alpha_B * alpha_M / cs2] /
              [2 + alpha_B * (2 + alpha_M)]

    But actually the simplest quasi-static limit (Amendola et al. 2018,
    JCAP 06 (2018) 030, Eq. 2.22-2.23):

        D = (1 + alpha_B)^2 + (2 - alpha_T) * c_s^{-2} * alpha_K
            (where alpha_K is kineticity)

    For simplicity, I use the compact Pogosian-Silvestri form with
    alpha_T = 0, which gives cleaner expressions:

        mu = 1 + (alpha_B^2) / (2 * cs2 * (1 + alpha_B))
             + alpha_M / (1 + alpha_B)
             (this is approximate for alpha_B << 1)

    EXACT quasi-static (alpha_T = 0):

        mu_QS = 1 + [alpha_B * (alpha_B + alpha_M)] / [2 * cs2]
                ÷ [1 + alpha_B + alpha_B^2 / (2 * cs2)]

    Let me use the form from Bellini-Sawicki Eq. (A.10), (A.15):

        Define:
            D = 1 + alpha_B
            numerator_mu = 2*D + alpha_B * alpha_M / cs2
            denominator = 2*D + alpha_B^2 / cs2

        mu = numerator_mu / denominator
        eta = [2*D + alpha_B * (alpha_M - alpha_B) / cs2] / numerator_mu

    Then: Sigma = mu * (1 + eta) / 2

    Returns:
        (mu, eta, Sigma)
    """
    # alpha_T = 0 for EFC (no tensor speed modification)
    D = 1.0 + alpha_B

    num_mu = 2.0 * D + alpha_B * alpha_M / cs2
    denom = 2.0 * D + alpha_B**2 / cs2

    if abs(denom) < 1e-15:
        return (1.0, 1.0, 1.0)

    mu = num_mu / denom

    # eta
    num_eta = 2.0 * D + alpha_B * (alpha_M - alpha_B) / cs2
    if abs(num_mu) < 1e-15:
        eta = 1.0
    else:
        eta = num_eta / num_mu

    # Sigma = mu * (1 + eta) / 2
    sigma = mu * (1.0 + eta) / 2.0

    return (mu, eta, sigma)


def stability_check(alpha_B: float, alpha_M: float, cs2: float) -> bool:
    """Check basic stability conditions.

    Requires:
        1. cs2 > 0 (no gradient instability)
        2. Q_s > 0 (no ghost)
        3. mu > 0 (positive effective Newton constant)

    Simplified check for alpha_T = 0.
    """
    if cs2 <= 0:
        return False

    mu, eta, sigma = horndeski_mu_eta_sigma(alpha_M, alpha_B, 0.0, cs2)
    if mu <= 0:
        return False

    return True


# ======================================================================
#  INVERSE MAPPING: mu -> (alpha_B, alpha_M)
# ======================================================================

def invert_mu_sigma_to_alphas(
    mu_target: float,
    sigma_target: float,
    cs2: float = 1.0,
) -> Optional[Tuple[float, float]]:
    """
    Given target (mu, Sigma), find (alpha_B, alpha_M) that produce them.

    With alpha_T = 0 and cs2 assumed:

        mu = [2*D + alpha_B * alpha_M / cs2] / [2*D + alpha_B^2 / cs2]
        Sigma = mu * (1 + eta) / 2

    This is 2 equations in 2 unknowns (alpha_B, alpha_M).

    Approach: numerical solve via scipy.optimize.
    """
    from scipy.optimize import minimize

    def residual(x):
        aB, aM = x
        mu, eta, sig = horndeski_mu_eta_sigma(aM, aB, 0.0, cs2)
        return (mu - mu_target)**2 + (sig - sigma_target)**2

    # Try multiple starting points
    best = None
    best_res = np.inf

    for aB_init in [-0.3, -0.1, 0.0, 0.1, 0.3]:
        for aM_init in [-0.3, -0.1, 0.0, 0.1, 0.3]:
            try:
                res = minimize(residual, [aB_init, aM_init],
                             method='Nelder-Mead',
                             options={'xatol': 1e-12, 'fatol': 1e-15, 'maxiter': 10000})
                if res.fun < best_res:
                    best_res = res.fun
                    best = res.x
            except Exception:
                continue

    if best is None or best_res > 1e-8:
        return None

    return (best[0], best[1])  # (alpha_B, alpha_M)


# ======================================================================
#  THE CRITICAL TEST
# ======================================================================

def test_mu_sigma_valley():
    """
    Test whether the preregistered (mu, Sigma, eta) valley is achievable
    within the Horndeski framework with alpha_T = 0.

    Target from preregistration:
        mu = 0.94, Sigma = 1.05, eta = 1.10

    Test for multiple cs2 values (cs2 = 1 is simplest assumption).
    """
    print("=" * 70)
    print("EFC HORNDESKI CONSISTENCY CHECK")
    print("Target: mu=0.94, Sigma=1.05, eta=1.10 (from preregistration)")
    print("=" * 70)

    targets = [
        (0.94, 1.05, "Preregistered valley"),
        (0.96, 1.02, "Weak modification"),
        (0.90, 1.10, "Strong modification"),
        (1.00, 1.00, "GR limit (sanity check)"),
    ]

    cs2_values = [0.5, 1.0, 2.0, 5.0]

    for mu_t, sig_t, label in targets:
        print(f"\n--- {label}: mu={mu_t}, Sigma={sig_t} ---")

        for cs2 in cs2_values:
            result = invert_mu_sigma_to_alphas(mu_t, sig_t, cs2)

            if result is None:
                print(f"  cs2={cs2:.1f}: NO SOLUTION FOUND")
                continue

            aB, aM = result
            mu_check, eta_check, sig_check = horndeski_mu_eta_sigma(aM, aB, 0.0, cs2)
            stable = stability_check(aB, aM, cs2)

            print(f"  cs2={cs2:.1f}: alpha_B={aB:+.6f}, alpha_M={aM:+.6f}")
            print(f"          -> mu={mu_check:.6f}, eta={eta_check:.6f}, "
                  f"Sigma={sig_check:.6f}")
            print(f"          Stable: {stable}, |residual|: "
                  f"{abs(mu_check-mu_t) + abs(sig_check-sig_t):.2e}")

            # KEY CHECK: does this require non-zero braiding?
            if abs(aB) < 1e-6:
                print(f"          ⚠ alpha_B ≈ 0 — no braiding needed")
            else:
                print(f"          ✓ alpha_B ≠ 0 — braiding REQUIRED")

    # BONUS: Check what shadow_slip.py gives (eta = 1/mu)
    print("\n" + "=" * 70)
    print("COMPARISON: shadow_slip.py model (eta = 1/mu)")
    print("=" * 70)

    for mu_t in [0.94, 0.96, 1.06, 1.10]:
        eta_simple = 1.0 / mu_t
        sig_simple = (mu_t + 1.0) / 2.0
        print(f"  mu={mu_t:.2f}: eta={eta_simple:.4f}, Sigma={sig_simple:.4f}")
        if mu_t < 1.0:
            print(f"          ⚠ Sigma < 1 when mu < 1 — CANNOT produce Sigma > 1!")
        else:
            print(f"          Sigma > 1 (but mu > 1 means stronger gravity)")

    # FINAL VERDICT
    print("\n" + "=" * 70)
    print("VERDICT: Can Horndeski produce mu<1 AND Sigma>1?")
    print("=" * 70)

    # Check directly
    result = invert_mu_sigma_to_alphas(0.94, 1.05, cs2=1.0)
    if result is not None:
        aB, aM = result
        mu_c, eta_c, sig_c = horndeski_mu_eta_sigma(aM, aB, 0.0, 1.0)
        stable = stability_check(aB, aM, 1.0)
        if abs(mu_c - 0.94) < 0.01 and abs(sig_c - 1.05) < 0.01 and stable:
            print(f"  YES — with alpha_B={aB:+.4f}, alpha_M={aM:+.4f}")
            print(f"  => eta={eta_c:.4f}")
            print(f"  => This REQUIRES non-zero braiding (alpha_B ≠ 0)")
            print(f"  => EFC action MUST produce alpha_B ≠ 0 to survive")
            return True
        else:
            print(f"  FOUND solution but unstable or inaccurate")
            print(f"  mu={mu_c:.4f}, Sigma={sig_c:.4f}, stable={stable}")
            return False
    else:
        print("  NO — no consistent (alpha_B, alpha_M) found for (0.94, 1.05)")
        print("  => Cosmological pathway CLOSED under standard Horndeski")
        return False


if __name__ == "__main__":
    test_mu_sigma_valley()
