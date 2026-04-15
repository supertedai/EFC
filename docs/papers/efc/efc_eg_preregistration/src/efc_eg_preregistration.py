"""efc_eg_preregistration.py

Reference implementation for the EFC EG Pre-Registration paper.

Implements the EG gravitational-slip statistic prediction from
Energy-Flow Cosmology (EFC), including the modified-gravity EG ratio,
pass/fail criteria, and supporting cosmological functions.

Author: Reference implementation based on Magnusson (2026)
"""

import numpy as np
from typing import Tuple, Dict

# ---------------------------------------------------------------------------
# Frozen EFC parameters (Global Parameter Registry DOI 31876324)
# ---------------------------------------------------------------------------
MU0: float = 0.94       # growth suppression via entropy stiffness
SIGMA0: float = 1.05    # lensing enhancement via flow anisotropy
ETA0: float = 1.10       # gravitational slip

# Survival valley bounds
MU_RANGE: Tuple[float, float] = (0.93, 0.96)
SIGMA_RANGE: Tuple[float, float] = (1.03, 1.07)

# Pivot point
KC: float = 0.05        # h Mpc^-1
ZEFF: float = 0.5

# Pre-registered prediction  (Eq. 7)
EG_RATIO_CENTRAL: float = 1.086
EG_RATIO_SIGMA: float = 0.012

# Pass / fail window  (Table 3)
KC_EG_PASS_LO: float = 1.03
KC_EG_PASS_HI: float = 1.14

# ell ranges
ELL_KAPPA_MIN: int = 100
ELL_KAPPA_MAX: int = 2000
ELL_ANALYSIS_MIN: int = 50
ELL_ANALYSIS_MAX: int = 500

# Redshift range for Euclid DR2 photometric sample
Z_MIN: float = 0.3
Z_MAX: float = 0.8
N_TOMO_BINS: int = 5


# ---------------------------------------------------------------------------
# Cosmological helper functions (flat LCDM background)
# ---------------------------------------------------------------------------
def omega_m_z(omega_m0: float, z: float) -> float:
    """Matter density parameter Omega_m(z) in flat LCDM.

    Parameters
    ----------
    omega_m0 : float
        Present-day matter density parameter.
    z : float
        Redshift.

    Returns
    -------
    float
    """
    a = 1.0 / (1.0 + z)
    return omega_m0 / (omega_m0 + (1.0 - omega_m0) * a**3)


def growth_rate_gr(omega_m0: float, z: float, gamma: float = 0.55) -> float:
    """Linear growth rate f(z) ~ Omega_m(z)^gamma  (GR approximation).

    Parameters
    ----------
    omega_m0 : float
        Present-day matter density parameter.
    z : float
        Redshift.
    gamma : float, optional
        Growth index (default 0.55 for GR/LCDM).

    Returns
    -------
    float
    """
    return omega_m_z(omega_m0, z) ** gamma


def eg_gr(omega_m0: float, z: float) -> float:
    """GR prediction for EG: EG^GR = Omega_m(z) / f(z).

    Parameters
    ----------
    omega_m0 : float
    z : float

    Returns
    -------
    float
    """
    om = omega_m_z(omega_m0, z)
    f = growth_rate_gr(omega_m0, z)
    return om / f


# ---------------------------------------------------------------------------
# Core EFC prediction  (Eq. 2 & 7)
# ---------------------------------------------------------------------------
def eg_ratio_mg(mu: float, sigma: float, f_ratio: float = 1.0) -> float:
    """EG^MG / EG^GR  =  Sigma / (mu * f/f_GR)   (Eq. 2).

    Parameters
    ----------
    mu : float
        Modified-gravity parameter mu (Poisson equation).
    sigma : float
        Modified-gravity parameter Sigma (lensing equation).
    f_ratio : float, optional
        f_EFC / f_GR.  For mu ~ 0.94 the growth-rate shift is
        already absorbed into the mu parameterisation at the
        pivot scale, so the default is 1.0.

    Returns
    -------
    float
    """
    return sigma / (mu * f_ratio)


def eg_ratio_efc(mu: float = MU0, sigma: float = SIGMA0) -> float:
    """Central EFC prediction for EG^EFC / EG^GR  (Eq. 7)."""
    return eg_ratio_mg(mu, sigma)


def eg_ratio_uncertainty(mu_range: Tuple[float, float] = MU_RANGE,
                         sigma_range: Tuple[float, float] = SIGMA_RANGE,
                         n_samples: int = 10000) -> Tuple[float, float]:
    """Monte-Carlo estimate of the EG ratio uncertainty from the
    survival-valley parameter ranges.

    Returns
    -------
    (mean, std) of the EG ratio distribution.
    """
    rng = np.random.default_rng(42)
    mus = rng.uniform(mu_range[0], mu_range[1], n_samples)
    sigmas = rng.uniform(sigma_range[0], sigma_range[1], n_samples)
    ratios = sigmas / mus
    return float(np.mean(ratios)), float(np.std(ratios))


# ---------------------------------------------------------------------------
# Pass / fail evaluation  (Table 3)
# ---------------------------------------------------------------------------
def evaluate_pass_fail(observed_ratio: float,
                       observed_sigma: float) -> Dict[str, object]:
    """Apply the frozen KC-EG-PASS criterion.

    Parameters
    ----------
    observed_ratio : float
        Measured EG^obs / EG^GR.
    observed_sigma : float
        1-sigma uncertainty on the measured ratio.

    Returns
    -------
    dict with keys 'ratio', 'sigma', 'in_window', 'above_1sigma',
    'pass', 'status'.
    """
    in_window = KC_EG_PASS_LO <= observed_ratio <= KC_EG_PASS_HI
    # "> 1 sigma" above GR (ratio > 1) check
    above_1sig = (observed_ratio - 1.0) > observed_sigma
    passed = in_window  # primary criterion
    status = "KC-EG-PASS" if passed else "KC-EG-FAIL"
    return {
        "ratio": observed_ratio,
        "sigma": observed_sigma,
        "in_window": in_window,
        "above_1sigma_from_gr": above_1sig,
        "pass": passed,
        "status": status,
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Verify central prediction reproduces Eq. 7
    ratio = eg_ratio_efc()
    print(f"EG^EFC / EG^GR (central) = {ratio:.4f}")
    assert abs(ratio - EG_RATIO_CENTRAL) < 0.002, (
        f"Central ratio {ratio} deviates from paper value {EG_RATIO_CENTRAL}")

    # MC uncertainty
    mc_mean, mc_std = eg_ratio_uncertainty()
    print(f"MC survival valley: mean = {mc_mean:.4f}, std = {mc_std:.4f}")

    # GR baseline at z_eff = 0.5 with Planck Omega_m0 = 0.315
    eg_gr_val = eg_gr(0.315, ZEFF)
    print(f"EG^GR(z=0.5) = {eg_gr_val:.4f}")

    # Pass/fail demo
    result = evaluate_pass_fail(1.086, 0.04)
    print(f"Pass/fail test: {result}")
    assert result["pass"] is True

    result_fail = evaluate_pass_fail(0.98, 0.03)
    assert result_fail["pass"] is False

    print("All self-tests passed.")
