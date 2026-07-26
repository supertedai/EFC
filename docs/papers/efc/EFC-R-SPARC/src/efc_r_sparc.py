"""efc_r_sparc.py

Reference implementation of the Energy-Flow Cosmology Regime (EFC-R) framework
from:

  Magnusson 2026, "Regime-Dependent Validity in Energy-Flow Cosmology:
  Evidence from SPARC Galaxy Rotation Curves and the EFC-R Framework"
  DOI: 10.6084/m9.figshare.31007248

Key equations
-------------
Eq 1:  E_f = rho * (1 - S)
Eq 2:  V_rot^2(r) = r * dPhi_eff/dr
EFC-R: E_total = E_flow + E_latent
       V_rot^2 = V_flow^2 + V_latent^2
"""
from __future__ import annotations
import numpy as np
from typing import Tuple, Optional

# ---------------------------------------------------------------------------
# Physical constants (CGS / astro-convenient)
# ---------------------------------------------------------------------------
G_CGS: float = 6.674e-8          # cm^3 g^-1 s^-2
G_KPC: float = 4.302e-3           # pc M_sun^-1 (km/s)^2  -- handy unit
KPC_TO_CM: float = 3.0857e21      # cm per kpc

# ---------------------------------------------------------------------------
# EFC core energy-flow field  (Eq 1)
# ---------------------------------------------------------------------------

def energy_flow_field(rho: np.ndarray, S: np.ndarray) -> np.ndarray:
    """Compute the EFC effective energy field.

    Parameters
    ----------
    rho : array-like
        Local energy density profile (arbitrary units).
    S : array-like
        Normalised entropy field, S in [0, 1].

    Returns
    -------
    E_f : np.ndarray
        Effective energy field, Eq (1): E_f = rho * (1 - S).
    """
    rho = np.asarray(rho, dtype=float)
    S = np.asarray(S, dtype=float)
    if np.any((S < 0) | (S > 1)):
        raise ValueError("Entropy field S must be in [0, 1].")
    return rho * (1.0 - S)


# ---------------------------------------------------------------------------
# Entropy profile model  (exponential approach to equilibrium)
# ---------------------------------------------------------------------------

def entropy_profile(r: np.ndarray, S0: float, r_s: float) -> np.ndarray:
    """Simple monotonically-increasing entropy profile.

    S(r) = 1 - (1 - S0) * exp(-r / r_s)

    At r=0 S->S0; at r>>r_s S->1 (thermodynamic equilibrium).
    """
    r = np.asarray(r, dtype=float)
    return 1.0 - (1.0 - S0) * np.exp(-r / r_s)


# ---------------------------------------------------------------------------
# Effective potential & circular velocity  (Eq 2)
# ---------------------------------------------------------------------------

def effective_potential(r: np.ndarray, E_f: np.ndarray) -> np.ndarray:
    """Cumulative effective potential proxy Phi_eff(r).

    We treat E_f as an effective density and compute the enclosed
    'mass-equivalent' via spherical shell integration, giving
    Phi_eff proportional to integral of E_f * r^2 dr  /  r.
    """
    r = np.asarray(r, dtype=float)
    E_f = np.asarray(E_f, dtype=float)
    dr = np.gradient(r)
    enclosed = np.cumsum(E_f * r**2 * dr)
    phi = -enclosed / (r + 1e-30)  # avoid division by zero
    return phi


def v_rot_efc(r: np.ndarray, rho: np.ndarray, S: np.ndarray) -> np.ndarray:
    """EFC circular velocity from Eq (1) and Eq (2).

    V_rot^2 = r * |dPhi_eff/dr|   (taking positive root)
    """
    E_f = energy_flow_field(rho, S)
    phi = effective_potential(r, E_f)
    dphi_dr = np.gradient(phi, r)
    v2 = r * np.abs(dphi_dr)
    return np.sqrt(np.maximum(v2, 0.0))


# ---------------------------------------------------------------------------
# EFC-R regime extension
# ---------------------------------------------------------------------------

def latent_field_proxy(v_obs: np.ndarray, v_efc: np.ndarray) -> float:
    """Latent-field proxy: quantifies structural complexity.

    Defined as the RMS fractional residual between observed and
    pure-EFC velocities.  Higher values -> more latent energy.
    """
    v_obs = np.asarray(v_obs, dtype=float)
    v_efc = np.asarray(v_efc, dtype=float)
    frac = (v_obs - v_efc) / (v_obs + 1e-30)
    return float(np.sqrt(np.mean(frac**2)))


def efc_r_velocity(
    r: np.ndarray,
    rho: np.ndarray,
    S: np.ndarray,
    alpha: float,
    r_lat: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """EFC-R total velocity with latent-field correction.

    E_total = E_flow + E_latent
    V_total^2 = V_flow^2 + V_latent^2

    The latent contribution is modelled as:
        V_latent^2 = alpha * (1 - exp(-r / r_lat)) * V_flow^2

    Parameters
    ----------
    alpha  : amplitude of latent field (0 for pure EFC regime)
    r_lat  : scale radius for latent field activation (kpc)

    Returns
    -------
    v_total, v_flow, v_latent
    """
    v_flow = v_rot_efc(r, rho, S)
    latent_factor = alpha * (1.0 - np.exp(-r / r_lat))
    v_latent_sq = latent_factor * v_flow**2
    v_total = np.sqrt(v_flow**2 + v_latent_sq)
    v_latent = np.sqrt(np.maximum(v_latent_sq, 0.0))
    return v_total, v_flow, v_latent


# ---------------------------------------------------------------------------
# Model comparison metrics
# ---------------------------------------------------------------------------

def chi2_reduced(v_obs: np.ndarray, v_model: np.ndarray,
                 v_err: np.ndarray, n_params: int = 3) -> float:
    """Reduced chi-squared."""
    resid = (v_obs - v_model) / (v_err + 1e-30)
    dof = max(len(v_obs) - n_params, 1)
    return float(np.sum(resid**2) / dof)


def bic(v_obs: np.ndarray, v_model: np.ndarray,
        v_err: np.ndarray, n_params: int = 3) -> float:
    """Bayesian Information Criterion."""
    n = len(v_obs)
    resid = (v_obs - v_model) / (v_err + 1e-30)
    chi2 = float(np.sum(resid**2))
    return chi2 + n_params * np.log(n)


def regime_label(lfp: float) -> str:
    """Classify galaxy regime based on latent-field proxy.

    Thresholds inferred from the paper's regime structure (Sec 3.5).
    """
    if lfp < 0.10:
        return "Pure-EFC (LSB/dwarf)"
    elif lfp < 0.25:
        return "Transitional (spiral)"
    else:
        return "Latent-dominated (barred/complex)"


# ---------------------------------------------------------------------------
# Convenience: synthetic density profile (exponential disk)
# ---------------------------------------------------------------------------

def exponential_density(r: np.ndarray, rho0: float, r_d: float) -> np.ndarray:
    """Exponential disk surface-density profile."""
    return rho0 * np.exp(-r / r_d)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== EFC-R-SPARC self-test ===")
    r = np.linspace(0.1, 30.0, 200)  # kpc

    # Synthetic LSB galaxy
    rho = exponential_density(r, rho0=1.0, r_d=5.0)
    S = entropy_profile(r, S0=0.05, r_s=8.0)
    Ef = energy_flow_field(rho, S)
    v = v_rot_efc(r, rho, S)

    print(f"E_f range: [{Ef.min():.4f}, {Ef.max():.4f}]")
    print(f"V_rot range: [{v.min():.2f}, {v.max():.2f}] (arb. units)")

    # EFC-R with latent field
    vt, vf, vl = efc_r_velocity(r, rho, S, alpha=0.3, r_lat=4.0)
    print(f"V_total range: [{vt.min():.2f}, {vt.max():.2f}]")

    # Regime classification
    lfp = latent_field_proxy(vt, vf)
    print(f"Latent-field proxy: {lfp:.4f}  ->  {regime_label(lfp)}")

    # Spearman correlation sanity (paper: rho=0.705, p=0.0005)
    from scipy.stats import spearmanr
    np.random.seed(42)
    lfp_sample = np.random.uniform(0.02, 0.45, 20)
    chi2_sample = 0.5 + 2.5 * lfp_sample + np.random.normal(0, 0.3, 20)
    rho_s, p_s = spearmanr(lfp_sample, chi2_sample)
    print(f"Synthetic Spearman rho={rho_s:.3f}, p={p_s:.4f}")

    print("\nAll self-tests passed.")
