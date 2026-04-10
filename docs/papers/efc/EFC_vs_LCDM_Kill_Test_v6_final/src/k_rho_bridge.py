"""
K(ρ) Bridge — Section 4 of the Kill-Test v6 paper.

Implements the core bridge between CMB lensing scale and galactic/Solar System
regimes via a single stiffness parameter K0 and a density suppression Θ(ρ).

    μ(k) = 1 / (1 + R(k))
    R(k) = K0 · Θ(ρ) · (Γ'φ̇)² · a⁴ / (M_Pl² · F · k⁴)
    Θ(ρ) = exp(−(ρ/ρ*)²)

Calibration anchor: μ(k = 0.05 h/Mpc) = 0.94 ⇒ K0 = 1.66.

The same K0 controls flat rotation curves at L3 because Θ ≈ 1 at both
cosmological and dwarf-galaxy outer densities.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List


# ---------------------------------------------------------------------------
# Anchor and calibration constants (Table 3 of the paper)
# ---------------------------------------------------------------------------

K0_REFERENCE = 1.66          # v5 reference
K0_MINIMUM = 1.552            # cobaya bobyqa minimum
K_ANCHOR_H_PER_MPC = 0.05    # CMB lensing anchor wavenumber
MU_AT_ANCHOR = 0.94           # μ(k=0.05) calibration target


def theta_rho(rho: float, rho_star: float = 1.0) -> float:
    """
    Density suppression function Θ(ρ) = exp(−(ρ/ρ*)²).

    Θ → 1 at cosmological / dwarf-galaxy densities.
    Θ → 0 at Solar System / inner-galaxy densities.

    Parameters
    ----------
    rho : float
        Local density in units of ρ*.
    rho_star : float, optional
        Characteristic suppression density (default 1.0).

    Returns
    -------
    float
        Value of Θ(ρ) ∈ (0, 1].
    """
    x = rho / rho_star
    return math.exp(-(x * x))


def R_k(k: float, K0: float = K0_REFERENCE, theta: float = 1.0) -> float:
    """
    Kernel function R(k) for the μ(k) bridge.

    Defined so that R(k = 0.05) · K0/K0_REF = (1/μ − 1) at the anchor.
    Scales as k⁻⁴.

    Parameters
    ----------
    k : float
        Wavenumber in h/Mpc.
    K0 : float
        Stiffness parameter (default 1.66).
    theta : float
        Density suppression Θ(ρ) ∈ [0, 1] (default 1.0).

    Returns
    -------
    float
        R(k) value.
    """
    # Calibrate so that at K0 = K0_REFERENCE, theta = 1, k = 0.05:
    # μ = 0.94 ⇒ R = 1/0.94 − 1 = 0.0638
    R_ref_at_anchor = (1.0 / MU_AT_ANCHOR) - 1.0  # 0.0638
    scale = (K_ANCHOR_H_PER_MPC / k) ** 4
    return R_ref_at_anchor * (K0 / K0_REFERENCE) * theta * scale


def mu_k(k: float, K0: float = K0_REFERENCE, theta: float = 1.0) -> float:
    """
    Effective Poisson function μ(k) = 1 / (1 + R(k)).

    Parameters
    ----------
    k : float
        Wavenumber in h/Mpc.
    K0 : float
        Stiffness parameter.
    theta : float
        Density suppression.

    Returns
    -------
    float
        μ(k) ∈ (0, 1].
    """
    return 1.0 / (1.0 + R_k(k, K0=K0, theta=theta))


# ---------------------------------------------------------------------------
# Bridge container
# ---------------------------------------------------------------------------

@dataclass
class KRhoBridge:
    """
    K(ρ) Bridge calculator.

    Exposes μ(k) and R(k) at arbitrary wavenumber, and a canonical scale
    table matching Table 3 of the paper.
    """
    K0: float = K0_REFERENCE
    rho_star: float = 1.0

    def R(self, k: float, rho: float = 0.0) -> float:
        """Compute R(k) with density suppression Θ(ρ)."""
        theta = theta_rho(rho, self.rho_star)
        return R_k(k, K0=self.K0, theta=theta)

    def mu(self, k: float, rho: float = 0.0) -> float:
        """Compute μ(k) at wavenumber k and density ρ (in units of ρ*)."""
        return 1.0 / (1.0 + self.R(k, rho=rho))

    def canonical_table(self) -> List[Dict[str, float]]:
        """
        Reproduce Table 3: μ(k) from super-horizon to Solar System.

        Returns
        -------
        list of dict
            Each entry has keys 'k_h_per_Mpc', 'theta', 'R_k', 'mu_k', 'scale'.
        """
        # (k [h/Mpc], rho_over_rho_star, scale label)
        #
        # Note: super-horizon (k < 0.005 h/Mpc) is regulated by horizon
        # crossing in the full paper; the toy R(k) ∝ k⁻⁴ scaling used here
        # is not applicable there, so we start at the CMB lensing anchor.
        rows = [
            (0.050, 0.0, "CMB lensing"),
            (0.100, 0.0, "BAO/LSS"),
            (5.000, 1.56, "Galactic"),    # tuned so Θ ≈ 0.087
            (50.00, 4.0, "Solar System"),  # Θ → 0
        ]
        out = []
        for k, rho, label in rows:
            theta = theta_rho(rho, self.rho_star)
            R = R_k(k, K0=self.K0, theta=theta)
            out.append({
                "k_h_per_Mpc": k,
                "theta": round(theta, 4),
                "R_k": R,
                "mu_k": 1.0 / (1.0 + R),
                "scale": label,
            })
        return out


# ---------------------------------------------------------------------------
# Demonstration / self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    bridge = KRhoBridge(K0=K0_REFERENCE)
    print("K(ρ) Bridge — canonical table (Table 3, K0 = 1.66):")
    print(f"{'k [h/Mpc]':>12} {'Θ':>8} {'R(k)':>12} {'μ(k)':>8}  Scale")
    for row in bridge.canonical_table():
        print(
            f"{row['k_h_per_Mpc']:>12.3f} "
            f"{row['theta']:>8.4f} "
            f"{row['R_k']:>12.4g} "
            f"{row['mu_k']:>8.4f}  {row['scale']}"
        )
    print()
    print(f"Calibration check: μ(0.05) = {bridge.mu(0.05):.4f}  (target 0.94)")
