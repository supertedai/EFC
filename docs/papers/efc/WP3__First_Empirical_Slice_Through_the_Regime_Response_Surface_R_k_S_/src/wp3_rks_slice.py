"""WP3 R(k,S) Empirical Slice -- core classes.

First entry in the EFC Response Atlas. Maps one trajectory through R(k,S)
space using fsigma8 measurements from BOSS, eBOSS, and DESI.

Key result: R(k~0.13, S~0.30) ~ +0.30, but LCDM preferred by ΔAIC = -3.8.

Author: Morten Magnusson (ORCID 0009-0002-4860-5095)
License: CC-BY-4.0
"""

import math


class RSDMeasurement:
    """A single redshift-space distortion (RSD) measurement of fsigma8.

    Parameters
    ----------
    survey : str
        Survey name (e.g., 'BOSS DR12', 'eBOSS DR16', 'DESI Y1').
    z : float
        Effective redshift.
    fsigma8 : float
        Measured f * sigma_8 value.
    error : float
        1-sigma measurement uncertainty.
    """

    def __init__(self, survey: str, z: float, fsigma8: float, error: float):
        self.survey = survey
        self.z = z
        self.fsigma8 = fsigma8
        self.error = error

    def structural_maturity(self, z_mid: float = 0.8) -> float:
        """Compute structural maturity S at this redshift.

        S(z) = 1 / (1 + (z/z_mid)^2)
        """
        return 1.0 / (1.0 + (self.z / z_mid) ** 2)

    def effective_k(self) -> float:
        """Effective wavenumber for RSD measurements (~0.1-0.13 h/Mpc)."""
        return 0.10 + 0.03 * (1.0 - self.z / 2.0)

    def __repr__(self) -> str:
        return (f"RSDMeasurement({self.survey!r}, z={self.z}, "
                f"fsigma8={self.fsigma8}+/-{self.error})")


class WP3Trajectory:
    """The WP3 trajectory through R(k,S) space.

    Collects RSD measurements and computes the empirical R(k,S) slice.

    Parameters
    ----------
    measurements : list of RSDMeasurement
        The input data points.
    z_mid : float
        Midpoint for structural maturity. Default 0.8.
    """

    def __init__(self, measurements: list = None, z_mid: float = 0.8):
        self.measurements = measurements or []
        self.z_mid = z_mid

    def add(self, m: RSDMeasurement):
        """Add a measurement to the trajectory."""
        self.measurements.append(m)

    def n_points(self) -> int:
        """Number of data points."""
        return len(self.measurements)

    def k_range(self) -> tuple:
        """Return the (min, max) wavenumber range."""
        if not self.measurements:
            return (0, 0)
        ks = [m.effective_k() for m in self.measurements]
        return (min(ks), max(ks))

    def S_range(self) -> tuple:
        """Return the (min, max) structural maturity range."""
        if not self.measurements:
            return (0, 0)
        Ss = [m.structural_maturity(self.z_mid) for m in self.measurements]
        return (min(Ss), max(Ss))

    def z_range(self) -> tuple:
        """Return the (min, max) redshift range."""
        if not self.measurements:
            return (0, 0)
        zs = [m.z for m in self.measurements]
        return (min(zs), max(zs))

    def chi2_lcdm(self, fsigma8_model: float = 0.472) -> float:
        """Chi-squared for flat LCDM (constant fsigma8 model).

        This is a simplified version using a constant prediction.

        Parameters
        ----------
        fsigma8_model : float
            LCDM prediction for fsigma8 (approximate). Default 0.472.
        """
        chi2 = 0.0
        for m in self.measurements:
            # Scale LCDM prediction with redshift (simplified growth)
            growth = (1.0 / (1.0 + m.z)) ** 0.55 * 0.8
            pred = fsigma8_model * growth / 0.472
            chi2 += ((m.fsigma8 - pred) / m.error) ** 2
        return chi2

    def __repr__(self) -> str:
        return f"WP3Trajectory(N={self.n_points()})"


class ModelComparison:
    """Compare LCDM and R(k,S) slice models using AIC.

    Parameters
    ----------
    chi2_lcdm : float
        Chi-squared for LCDM.
    chi2_rks : float
        Chi-squared for R(k,S) slice.
    n_params_lcdm : int
        Number of free parameters in LCDM. Default 3.
    n_params_rks : int
        Number of free parameters in R(k,S). Default 5.
    """

    def __init__(self, chi2_lcdm: float = 9.36, chi2_rks: float = 9.12,
                 n_params_lcdm: int = 3, n_params_rks: int = 5):
        self.chi2_lcdm = chi2_lcdm
        self.chi2_rks = chi2_rks
        self.n_params_lcdm = n_params_lcdm
        self.n_params_rks = n_params_rks

    def aic_lcdm(self) -> float:
        """AIC for LCDM: chi2 + 2k."""
        return self.chi2_lcdm + 2 * self.n_params_lcdm

    def aic_rks(self) -> float:
        """AIC for R(k,S) slice: chi2 + 2k."""
        return self.chi2_rks + 2 * self.n_params_rks

    def delta_aic(self) -> float:
        """ΔAIC = AIC_LCDM - AIC_RkS. Negative means LCDM preferred."""
        return self.aic_lcdm() - self.aic_rks()

    def preferred_model(self) -> str:
        """Which model is preferred by AIC."""
        if self.delta_aic() < 0:
            return "LCDM"
        elif self.delta_aic() > 0:
            return "R(k,S)"
        return "indistinguishable"

    def verdict(self) -> str:
        """Human-readable verdict."""
        model = self.preferred_model()
        daic = abs(self.delta_aic())
        if daic < 2:
            strength = "weakly"
        elif daic < 6:
            strength = "moderately"
        else:
            strength = "strongly"
        return f"{model} {strength} preferred (ΔAIC = {self.delta_aic():.1f})"

    def summary(self) -> dict:
        """Return a comparison summary."""
        return {
            "chi2_lcdm": self.chi2_lcdm,
            "chi2_rks": self.chi2_rks,
            "AIC_lcdm": self.aic_lcdm(),
            "AIC_rks": self.aic_rks(),
            "delta_AIC": self.delta_aic(),
            "preferred": self.preferred_model(),
            "verdict": self.verdict(),
        }

    def __repr__(self) -> str:
        return f"ModelComparison(ΔAIC={self.delta_aic():.1f})"
