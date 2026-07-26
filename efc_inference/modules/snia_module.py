"""
SN Ia (Type Ia Supernovae) Module

Loads SN Ia distance modulus measurements and computes likelihood
against EFC Hubble predictions via luminosity distance.

Data sources:
    - Pantheon (Scolnic et al. 2018): 40 binned distance moduli
    - Pantheon+ (Scolnic et al. 2022): future upgrade path

Observable:
    Distance modulus: mu = m_B - M_B
    where m_B is the apparent B-band magnitude (standardized)
    and M_B is the absolute magnitude (nuisance parameter).

    Theoretical prediction:
        mu_th(z) = 5 * log10(d_L(z) / 10 pc)
                 = 5 * log10(d_L(z) [Mpc]) + 25

    Luminosity distance:
        d_L(z) = (1 + z) * D_M(z)
        D_M(z) = integral_0^z c/H(z') dz'    (comoving distance)

Likelihood:
    Uses full covariance matrix (systematic + statistical):
        ln L = -0.5 * (Delta mu)^T C^{-1} (Delta mu) - 0.5 * ln|C| - N/2 * ln(2*pi)
    where Delta mu_i = m_B,i - M_B - mu_th(z_i)

    M_B is analytically marginalized (Conley et al. 2011 method):
        ln L_marg = -0.5 * [chi2 - B^2/D + ln(D/(2*pi))]
    where:
        B = sum_ij C^{-1}_{ij} * (m_B,j - mu_th,j)
        D = sum_ij C^{-1}_{ij}
        chi2 = sum_ij (m_B,i - mu_th,i) C^{-1}_{ij} (m_B,j - mu_th,j)

    This eliminates M_B from the parameter space entirely.

Usage:
    engine = EFCHubble()
    module = SNIaModule(engine)
    module.load_data(data_path="efc_inference/data/snia/pantheon_binned.csv",
                     cov_path="efc_inference/data/snia/pantheon_binned_covtotal.npy")
    ll = module.log_likelihood(params_dict)
"""

import numpy as np
import logging
from pathlib import Path
from typing import Optional

from .base_module import BaseModule
from ..engine.hubble import EFCHubble

logger = logging.getLogger(__name__)

# Speed of light in km/s
C_KM_S = 299792.458


class SNIaModule(BaseModule):
    """
    Type Ia Supernova distance modulus module.

    Computes luminosity distances from H(z) via comoving distance integration,
    then compares against observed apparent magnitudes with M_B analytically
    marginalized out.

    Supports:
        - Diagonal errors (chi2 likelihood)
        - Full covariance matrix (recommended for Pantheon)
    """

    def __init__(self, engine: Optional[EFCHubble] = None):
        if engine is None:
            engine = EFCHubble()
        super().__init__(engine)
        self._covariance = None
        self._cov_inv = None  # cached inverse
        self._cov_logdet = None  # cached log-determinant

    @property
    def name(self) -> str:
        return "snia"

    def load_data(self, data_path: str = None, cov_path: str = None, **kwargs):
        """
        Load SN Ia data from CSV + optional covariance matrix.

        CSV format: z, mb, dmb
            z:   CMB-frame redshift
            mb:  apparent B-band magnitude (standardized)
            dmb: statistical error on mb

        Covariance: numpy .npy file, shape (N, N)
            Total covariance = systematic + statistical.

        Parameters:
            data_path:  Path to CSV data file
            cov_path:   Path to .npy covariance matrix (optional)
            min_z:      Minimum redshift to include (default 0.0)
        """
        if data_path is None:
            raise ValueError("data_path is required")

        path = Path(data_path)
        if not path.exists():
            raise FileNotFoundError(f"SN Ia data not found: {path}")

        # Load CSV: z, mb, dmb
        raw = np.loadtxt(str(path), delimiter=",", skiprows=1)

        if raw.ndim == 1:
            raw = raw.reshape(1, -1)

        if raw.shape[1] < 3:
            raise ValueError(
                f"Expected 3 columns (z, mb, dmb), got {raw.shape[1]}"
            )

        z_all = raw[:, 0]
        mb_all = raw[:, 1]
        dmb_all = raw[:, 2]

        # Optional redshift cut
        min_z = kwargs.get("min_z", 0.0)
        mask = z_all >= min_z
        if min_z > 0:
            logger.info("Applying min_z=%.4f cut: %d → %d",
                        min_z, len(z_all), np.sum(mask))

        self.coordinates = z_all[mask]  # redshifts
        self.observed = mb_all[mask]     # apparent magnitudes m_B
        self.errors = dmb_all[mask]      # statistical errors

        # Validate
        if np.any(self.coordinates <= 0):
            raise ValueError("Redshifts must be positive")
        if np.any(self.errors <= 0):
            raise ValueError("Errors must be positive")

        # Load covariance if provided
        if cov_path is not None:
            cov_file = Path(cov_path)
            if not cov_file.exists():
                raise FileNotFoundError(f"Covariance not found: {cov_file}")

            cov_full = np.load(str(cov_file))

            # Apply same redshift mask if needed
            if min_z > 0 and cov_full.shape[0] == len(z_all):
                idx = np.where(mask)[0]
                cov_full = cov_full[np.ix_(idx, idx)]

            if cov_full.shape != (self.n_data, self.n_data):
                raise ValueError(
                    f"Covariance shape {cov_full.shape} doesn't match "
                    f"data length {self.n_data}"
                )

            self._covariance = cov_full

            # Pre-compute inverse and log-determinant for speed
            try:
                L = np.linalg.cholesky(self._covariance)
                self._cov_inv = np.linalg.solve(
                    self._covariance, np.eye(self.n_data)
                )
                self._cov_logdet = 2.0 * np.sum(np.log(np.diag(L)))
            except np.linalg.LinAlgError:
                logger.warning("Covariance not positive definite, "
                               "falling back to diagonal")
                self._covariance = None
                self._cov_inv = None
                self._cov_logdet = None

        self._loaded = True
        logger.info(
            "Loaded SN Ia data: %d points, z=[%.3f, %.3f], cov=%s",
            self.n_data, self.coordinates.min(), self.coordinates.max(),
            "full" if self._covariance is not None else "diagonal"
        )

    def predict(self, params_dict: dict) -> np.ndarray:
        """
        Compute theoretical distance modulus mu_th(z).

        mu_th = 5 * log10(d_L [Mpc]) + 25

        where d_L = (1+z) * D_M(z) and D_M = integral c/H(z') dz'.

        Note: This returns mu_th WITHOUT M_B subtracted.
        The log_likelihood handles M_B marginalization.
        """
        if not self._loaded:
            raise RuntimeError("Call load_data() first")

        mu_th = np.zeros(self.n_data)

        for i, z in enumerate(self.coordinates):
            DM = self._comoving_distance(params_dict, z)
            dL = (1.0 + z) * DM  # luminosity distance in Mpc

            if dL <= 0:
                mu_th[i] = np.nan
            else:
                mu_th[i] = 5.0 * np.log10(dL) + 25.0

        return mu_th

    def _comoving_distance(self, params_dict: dict, z: float) -> float:
        """
        Compute comoving distance D_M(z) = integral_0^z c/H(z') dz'.

        Uses trapezoidal integration with adaptive grid density:
            - 201 points for z < 1
            - 301 points for z >= 1

        Returns:
            D_M in Mpc
        """
        n_grid = 201 if z < 1.0 else 301
        z_grid = np.linspace(0.0, z, n_grid)
        Hz_grid = self.engine.compute(params_dict, z_grid)

        # c / H(z') integrand
        integrand = C_KM_S / Hz_grid

        _trapz = getattr(np, 'trapezoid', None) or np.trapz
        return _trapz(integrand, z_grid)

    def log_likelihood(self, params_dict: dict) -> float:
        """
        Log-likelihood with M_B analytically marginalized.

        Conley et al. (2011) method:
            ln L = -0.5 * [chi2 - B^2/D + ln(D/(2*pi))]

        where:
            Delta_i = m_B,i - mu_th(z_i)
            chi2 = Delta^T C^{-1} Delta
            B = 1^T C^{-1} Delta
            D = 1^T C^{-1} 1

        This is exact marginalization over a flat M_B prior.
        """
        if not self._loaded:
            raise RuntimeError("Call load_data() first")

        mu_th = self.predict(params_dict)

        if np.any(~np.isfinite(mu_th)):
            return -np.inf

        # Delta = m_B - mu_th  (residuals before M_B subtraction)
        delta = self.observed - mu_th

        if self._cov_inv is not None:
            # Full covariance path
            Cinv_delta = self._cov_inv @ delta
            chi2 = delta @ Cinv_delta

            ones = np.ones(self.n_data)
            B = ones @ Cinv_delta
            D = ones @ (self._cov_inv @ ones)

            # Marginalized log-likelihood
            log_like = -0.5 * (chi2 - B**2 / D + np.log(D / (2 * np.pi)))

            # Add normalization from covariance determinant
            log_like -= 0.5 * self._cov_logdet

        else:
            # Diagonal path (fallback)
            var = self.errors**2
            w = 1.0 / var  # weights

            chi2 = np.sum(delta**2 * w)
            B = np.sum(delta * w)
            D = np.sum(w)

            log_like = -0.5 * (chi2 - B**2 / D + np.log(D / (2 * np.pi)))
            log_like -= 0.5 * np.sum(np.log(2 * np.pi * var))

        return log_like

    def log_likelihood_fixed_MB(self, params_dict: dict,
                                 M_B: float = -19.253) -> float:
        """
        Log-likelihood with fixed M_B (for diagnostic purposes).

        Uses the standard formulation without marginalization.
        Default M_B = -19.253 (Pantheon best-fit).
        """
        if not self._loaded:
            raise RuntimeError("Call load_data() first")

        mu_th = self.predict(params_dict)

        if np.any(~np.isfinite(mu_th)):
            return -np.inf

        # Distance modulus residuals
        delta = self.observed - M_B - mu_th

        if self._covariance is not None:
            from ..core.likelihoods import log_likelihood_covariance
            return log_likelihood_covariance(
                np.zeros(self.n_data), delta, self._covariance
            )
        else:
            from ..core.likelihoods import log_likelihood_chi2
            return log_likelihood_chi2(
                np.zeros(self.n_data), delta, self.errors
            )

    def best_fit_MB(self, params_dict: dict) -> float:
        """
        Compute best-fit M_B from analytic marginalization.

        Given the current cosmological parameters, this returns the M_B
        that maximizes the likelihood (= the weighted mean of m_B - mu_th).

        M_B_best = (1^T C^{-1} Delta) / (1^T C^{-1} 1)
        where Delta_i = m_B,i - mu_th(z_i).
        """
        mu_th = self.predict(params_dict)
        delta = self.observed - mu_th
        ones = np.ones(self.n_data)

        if self._cov_inv is not None:
            B = ones @ (self._cov_inv @ delta)
            D = ones @ (self._cov_inv @ ones)
        else:
            w = 1.0 / self.errors**2
            B = np.sum(delta * w)
            D = np.sum(w)

        return float(B / D)

    def ppc_predict(self, params_dict: dict) -> np.ndarray:
        """
        PPC-compatible prediction: m_b_pred = mu_th + M_B_best.

        Unlike predict() which returns raw mu_th, this adds the best-fit
        M_B so residuals are on the same scale as the observed m_B data.
        This is the correct observable for posterior predictive checks.
        """
        mu_th = self.predict(params_dict)
        M_B = self.best_fit_MB(params_dict)
        return mu_th + M_B

    def summary(self) -> dict:
        base = super().summary()
        base["covariance"] = "full" if self._covariance is not None else "diagonal"
        return base
