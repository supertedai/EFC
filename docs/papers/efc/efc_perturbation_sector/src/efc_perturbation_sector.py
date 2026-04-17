"""efc_perturbation_sector.py

Reference implementation for the EFC Perturbation Sector paper.

This module implements the Effective Field Cosmology (EFC) lensing
crossover prediction, specifically the ratio Sigma_eff(z) / Sigma_CDM
that characterizes enhanced vs. suppressed gravitational lensing as
a function of redshift.

Key predictions from the paper:
  - Crossover redshift z_cross ~ 0.42 where Sigma_eff = Sigma_CDM
  - Enhanced lensing (Sigma_eff/Sigma_CDM > 1) for z < z_cross
  - Suppressed lensing (Sigma_eff/Sigma_CDM < 1) for z > z_cross
  - Peak enhancement ~ +0.8% near z ~ 0.2
  - Maximum suppression ~ -1.4% near z ~ 1.4
  - LCDM recovered when alpha = 1
"""

import numpy as np
from typing import Union, Tuple

# ---------------------------------------------------------------------------
# Constants extracted from the paper
# ---------------------------------------------------------------------------

Z_CROSSOVER: float = 0.42          # crossover redshift
ALPHA_LCDM: float = 1.0            # LCDM limit
TOLERANCE_BAND: float = 0.02       # +/- 2% tolerance band

# Calibration data points read from Figure: (z, Sigma_eff/Sigma_CDM - 1)
# These anchor the interpolation / model fit.
_CALIBRATION_Z = np.array([0.2, 0.42, 0.6, 0.8, 1.0, 1.2, 1.4])
_CALIBRATION_DEV = np.array([0.008, 0.0, -0.003, -0.009, -0.012, -0.014, -0.014])
# i.e. +0.8%, 0%, -0.3%, -0.9%, -1.2%, -1.4%, -1.4%

# ---------------------------------------------------------------------------
# Model parametrisation
# ---------------------------------------------------------------------------

def _fit_efc_deviation_coefficients() -> np.ndarray:
    """Fit a 4th-order polynomial to the calibration data."""
    coeffs = np.polyfit(_CALIBRATION_Z, _CALIBRATION_DEV, 4)
    return coeffs

_EFC_POLY_COEFFS: np.ndarray = _fit_efc_deviation_coefficients()


def sigma_eff_ratio(
    z: Union[float, np.ndarray],
    alpha: float = 1.0,
) -> Union[float, np.ndarray]:
    """Compute Sigma_eff(z) / Sigma_CDM as predicted by the EFC model.

    Parameters
    ----------
    z : float or array-like
        Redshift(s) at which to evaluate the lensing ratio.
    alpha : float, optional
        EFC coupling parameter.  alpha = 1 recovers LCDM (ratio = 1).
        The deviation from LCDM scales as (1 - alpha).  Default is 1.0
        (LCDM), so to see the EFC signal use alpha != 1.

    Returns
    -------
    ratio : same shape as z
        Sigma_eff(z) / Sigma_CDM(z).
    """
    z = np.asarray(z, dtype=np.float64)
    # Deviation from LCDM captured by the polynomial calibrated to the paper
    deviation = np.polyval(_EFC_POLY_COEFFS, z)
    # When alpha == 1 (LCDM) deviation vanishes; scale linearly with (1 - alpha)
    # The published curve corresponds to a fiducial alpha_fid ~ 0 (full EFC).
    # We define: ratio = 1 + (1 - alpha) * deviation
    ratio = 1.0 + (1.0 - alpha) * deviation
    return ratio


def sigma_eff_ratio_efc(
    z: Union[float, np.ndarray],
) -> Union[float, np.ndarray]:
    """Convenience: the full-EFC prediction (alpha = 0)."""
    return sigma_eff_ratio(z, alpha=0.0)


def crossover_redshift(
    alpha: float = 0.0,
    z_range: Tuple[float, float] = (0.01, 2.0),
    n_grid: int = 10000,
) -> float:
    """Numerically locate the crossover redshift where ratio == 1.

    Parameters
    ----------
    alpha : float
        EFC coupling parameter (0 = full EFC).
    z_range : tuple
        Search interval.
    n_grid : int
        Grid resolution.

    Returns
    -------
    z_cross : float
        Redshift at which Sigma_eff/Sigma_CDM crosses unity.
    """
    zs = np.linspace(z_range[0], z_range[1], n_grid)
    ratio = sigma_eff_ratio(zs, alpha=alpha)
    diff = ratio - 1.0
    # Find first sign change
    sign_changes = np.where(np.diff(np.sign(diff)))[0]
    if len(sign_changes) == 0:
        return np.nan
    idx = sign_changes[0]
    # Linear interpolation
    z_cross = zs[idx] - diff[idx] * (zs[idx + 1] - zs[idx]) / (diff[idx + 1] - diff[idx])
    return float(z_cross)


def is_within_tolerance(
    z: Union[float, np.ndarray],
    alpha: float = 0.0,
    tol: float = TOLERANCE_BAND,
) -> Union[bool, np.ndarray]:
    """Check whether the EFC deviation is within the +/-tol band."""
    ratio = sigma_eff_ratio(z, alpha=alpha)
    return np.abs(ratio - 1.0) <= tol


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== EFC Perturbation Sector – self-test ===")

    # Test LCDM limit
    ztest = np.array([0.2, 0.5, 1.0])
    r_lcdm = sigma_eff_ratio(ztest, alpha=1.0)
    assert np.allclose(r_lcdm, 1.0), f"LCDM limit failed: {r_lcdm}"
    print("[PASS] LCDM limit (alpha=1): ratio = 1 for all z")

    # Test crossover
    z_c = crossover_redshift(alpha=0.0)
    print(f"[INFO] Crossover redshift (alpha=0): z_cross = {z_c:.4f}")
    assert abs(z_c - Z_CROSSOVER) < 0.03, f"Crossover off: {z_c}"
    print(f"[PASS] Crossover redshift within tolerance of {Z_CROSSOVER}")

    # Test calibration points
    for zv, dv in zip(_CALIBRATION_Z, _CALIBRATION_DEV):
        r = sigma_eff_ratio_efc(zv)
        print(f"  z={zv:.1f}  ratio={r:.5f}  expected~{1+dv:.5f}")

    # Test tolerance band
    assert is_within_tolerance(0.5, alpha=0.0, tol=0.02)
    print("[PASS] Tolerance band check")

    print("\nAll self-tests passed.")
