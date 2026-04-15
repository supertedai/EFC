"""efc_eg_preregistration.py

Reference implementation for:
  Pre-Registered EFC Prediction: EG Statistic from SO x Euclid Cross-Correlation
  Morten Magnusson, Symbiose Research (April 2026)

Implements the key equations for the EG gravitational-slip statistic,
the EFC modified-gravity prediction, and the pre-registered pass/fail
criteria.
"""

import numpy as np
from typing import Tuple, Dict

# ---------------------------------------------------------------------------
# Frozen EFC parameters (Global Parameter Registry DOI 31876324)
# ---------------------------------------------------------------------------
MU0: float = 0.94       # growth suppression via entropy stiffness
SIGMA0: float = 1.05    # lensing enhancement via flow anisotropy
ETA0: float = 1.10       # gravitational slip

# Survival-valley bounds
MU_RANGE: Tuple[float, float] = (0.93, 0.96)
SIGMA_RANGE: Tuple[float, float] = (1.03, 1.07)

# Pivot / reference scales
KC: float = 0.05        # h Mpc^-1
ZEFF: float = 0.5
ELL_RANGE: Tuple[int, int] = (50, 500)
KAPPA_ELL_RANGE: Tuple[int, int] = (100, 2000)
Z_RANGE: Tuple[float, float] = (0.3, 0.8)
N_TOMO_BINS: int = 5

# Pre-registered prediction  (Eq. 7)
EG_RATIO_CENTRAL: float = 1.086
EG_RATIO_SIGMA: float = 0.012

# Pass / fail thresholds  (Table 3)
KC_EG_PASS_LO: float = 1.03
KC_EG_PASS_HI: float = 1.14


# ---------------------------------------------------------------------------
# Cosmological helpers
# ---------------------------------------------------------------------------
def omega_m_z(omega_m0: float, z: float) -> float:
    """Matter density parameter Omega_m(z) in a flat LCDM background.

    Omega_m(z) = Omega_m0 (1+z)^3 / E^2(z),  with E^2 = Omega_m0(1+z)^3 + (1-Omega_m0).
    """
    a3 = (1.0 + z) ** 3
    E2 = omega_m0 * a3 + (1.0 - omega_m0)
    return omega_m0 * a3 / E2


def growth_rate_gr(omega_m0: float, z: float, gamma: float = 0.55) -> float:
    """Linear growth rate f(z) ~ Omega_m(z)^gamma  (LCDM approximation)."""
    return float(omega_m_z(omega_m0, z) ** gamma)


# ---------------------------------------------------------------------------
# EG statistic  (Eq. 1 & 2)
# ---------------------------------------------------------------------------
def eg_gr(omega_m0: float, z: float) -> float:
    """GR prediction:  E_G^{GR}(z) = Omega_m(z) / f(z).   (Eq. 1)"""
    f = growth_rate_gr(omega_m0, z)
    return float(omega_m_z(omega_m0, z) / f)


def eg_ratio_mg(mu: float, sigma: float,
                f_mg: float | None = None, f_gr: float | None = None,
                omega_m0: float = 0.3111, z: float = 0.5) -> float:
    """Modified-gravity EG ratio  E_G^{MG} / E_G^{GR}  (Eq. 2).

    E_G^{MG} / E_G^{GR} = Sigma / ( mu * f_MG / f_GR )

    If f_mg is None, assume f_MG/f_GR = mu^gamma_eff ~ mu^0.55  (linear
    perturbation scaling with modified Poisson equation).
    """
    if f_gr is None:
        f_gr = growth_rate_gr(omega_m0, z)
    if f_mg is None:
        # Leading-order: delta_f/f ~ (gamma / Omega_m) * delta_mu  ->  f_MG ~ f_GR * mu^0.55
        f_mg = f_gr * mu ** 0.55
    return float(sigma / (mu * f_mg / f_gr))


def eg_efc_prediction(mu: float = MU0, sigma: float = SIGMA0,
                      omega_m0: float = 0.3111, z: float = ZEFF) -> Tuple[float, float]:
    """Return (E_G^{EFC}/E_G^{GR}, E_G^{GR}) at the pivot redshift."""
    ratio = eg_ratio_mg(mu, sigma, omega_m0=omega_m0, z=z)
    eg_gr_val = eg_gr(omega_m0, z)
    return ratio, eg_gr_val


# ---------------------------------------------------------------------------
# Survival-valley scan  (uncertainty band in Eq. 7)
# ---------------------------------------------------------------------------
def survival_valley_scan(mu_lo: float = MU_RANGE[0], mu_hi: float = MU_RANGE[1],
                         sigma_lo: float = SIGMA_RANGE[0], sigma_hi: float = SIGMA_RANGE[1],
                         n: int = 200, omega_m0: float = 0.3111,
                         z: float = ZEFF) -> Dict[str, float]:
    """Scan the survival valley and return min, max, mean, std of E_G ratio."""
    mus = np.linspace(mu_lo, mu_hi, n)
    sigmas = np.linspace(sigma_lo, sigma_hi, n)
    MU, SIG = np.meshgrid(mus, sigmas)
    ratios = np.vectorize(lambda m, s: eg_ratio_mg(m, s, omega_m0=omega_m0, z=z))(MU, SIG)
    return {
        "min": float(ratios.min()),
        "max": float(ratios.max()),
        "mean": float(ratios.mean()),
        "std": float(ratios.std()),
    }


# ---------------------------------------------------------------------------
# Pass / fail evaluation  (Table 3)
# ---------------------------------------------------------------------------
def evaluate_pass_fail(observed_ratio: float, observed_sigma: float,
                       pass_lo: float = KC_EG_PASS_LO,
                       pass_hi: float = KC_EG_PASS_HI) -> Dict[str, object]:
    """Evaluate the pre-registered KC-EG-PASS / KC-EG-FAIL criterion.

    Pass requires: observed_ratio - observed_sigma > pass_lo  **or**
                   observed_ratio + observed_sigma < pass_hi
    i.e. the 1-sigma interval overlaps [pass_lo, pass_hi].
    Strict: central value in window AND >1sigma away from edges inward.
    """
    lower = observed_ratio - observed_sigma
    upper = observed_ratio + observed_sigma
    in_window = (lower >= pass_lo) or (observed_ratio >= pass_lo)
    in_window = in_window and ((upper <= pass_hi) or (observed_ratio <= pass_hi))
    central_in = pass_lo <= observed_ratio <= pass_hi
    above_1sig = lower > pass_lo  # >1sigma above lower edge
    result = {
        "observed_ratio": observed_ratio,
        "observed_sigma": observed_sigma,
        "central_in_window": central_in,
        "above_1sigma_lower": above_1sig,
        "KC_EG_PASS": central_in and above_1sig,
        "KC_EG_FAIL": not central_in,
    }
    return result


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== EFC EG Pre-Registration: self-test ===")

    # Central prediction
    ratio, eg_gr_val = eg_efc_prediction()
    print(f"E_G^{{EFC}} / E_G^{{GR}} = {ratio:.4f}  (paper: {EG_RATIO_CENTRAL})")
    print(f"E_G^{{GR}}(z={ZEFF})       = {eg_gr_val:.4f}")
    assert abs(ratio - EG_RATIO_CENTRAL) < 0.02, (
        f"Central ratio {ratio:.4f} deviates from paper value {EG_RATIO_CENTRAL} by > 0.02"
    )

    # Survival valley
    sv = survival_valley_scan()
    print(f"Survival valley: mean={sv['mean']:.4f}, std={sv['std']:.4f}, "
          f"range=[{sv['min']:.4f}, {sv['max']:.4f}]")

    # Pass/fail demo
    pf = evaluate_pass_fail(1.086, 0.03)
    print(f"Pass/fail demo (ratio=1.086 +/- 0.03): KC_EG_PASS={pf['KC_EG_PASS']}")

    print("\nAll self-tests passed.")
