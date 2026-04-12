"""
Euclid DR1 Mock Likelihood for EFC Pipeline
============================================

Generates a Gaussian mock Cl likelihood for Euclid DR1-like survey specs.
Uses the EFC mu-Sigma parametrisation to compute modified Cl's.

Survey specifications (based on EC20 + Euclid Collaboration forecasts):
  - Sky area: ~2100 deg^2 (DR1 wide survey, first year)
  - 10 tomographic bins for weak lensing (z = 0.001 to 2.5)
  - 4 spectroscopic bins for galaxy clustering (z = 0.9 to 1.8)
  - ell range: 10 to 5000 (WL), 10 to 750 (GC spectroscopic)
  - n_eff ~ 30 arcmin^{-2} (WL source density)
  - sigma_eps = 0.26 (intrinsic ellipticity dispersion per component)

This mock creates a Fisher-level Gaussian likelihood that can be used
to test the pipeline BEFORE Euclid DR1 data arrives in October 2026.
When real data is available, swap the mock data vector and covariance.

Usage with cobaya:
  likelihood:
    euclid_dr1_mock:
      python_path: /path/to/src
      class: EuclidDR1MockLikelihood
"""

import numpy as np
from typing import Dict, Optional
import json


class EuclidDR1MockLikelihood:
    """Gaussian mock likelihood for Euclid DR1 WL + GC angular Cl's.

    For cobaya integration, this class provides:
      - get_requirements(): declares needed theory quantities
      - logp(**params): returns log-likelihood
    """

    # -- Survey specifications -------------------------------------------
    SKY_AREA_DEG2 = 2100.0          # DR1 wide survey
    F_SKY = SKY_AREA_DEG2 / 41253.0  # fraction of sky

    # Weak lensing tomographic bins (edges)
    WL_ZBIN_EDGES = np.array([0.001, 0.301, 0.501, 0.701, 0.901,
                               1.101, 1.301, 1.501, 1.801, 2.101, 2.501])
    N_WL_BINS = len(WL_ZBIN_EDGES) - 1

    # Galaxy clustering spectroscopic bins (edges)
    GC_ZBIN_EDGES = np.array([0.9, 1.1, 1.3, 1.5, 1.8])
    N_GC_BINS = len(GC_ZBIN_EDGES) - 1

    # Multipole range
    ELL_MIN = 10
    ELL_MAX_WL = 5000
    ELL_MAX_GC = 750
    N_ELL_WL = 30     # number of ell bins (log-spaced)
    N_ELL_GC = 15

    # Noise parameters
    N_EFF = 30.0       # arcmin^{-2}, effective galaxy number density
    SIGMA_EPS = 0.26   # intrinsic ellipticity per component

    def __init__(self, fiducial_model="LCDM",
                 efc_params: Optional[Dict] = None):
        """
        Parameters
        ----------
        fiducial_model : str
            'LCDM' or 'EFC' -- determines the mock data vector
        efc_params : dict, optional
            EFC parameters for generating fiducial {R0, kc, eps_tot}
        """
        self.fiducial = fiducial_model
        self.efc_params = efc_params or {}

        # Set up ell binning
        self.ell_wl = np.logspace(
            np.log10(self.ELL_MIN), np.log10(self.ELL_MAX_WL),
            self.N_ELL_WL)
        self.ell_gc = np.logspace(
            np.log10(self.ELL_MIN), np.log10(self.ELL_MAX_GC),
            self.N_ELL_GC)

        # Compute noise power spectra
        self._setup_noise()

        # Generate mock data vector and covariance
        self._generate_mock()

    def _setup_noise(self):
        """Compute shape noise for WL and shot noise for GC."""
        # Convert n_eff from arcmin^{-2} to sr^{-1}
        arcmin2_per_sr = (180 * 60 / np.pi)**2
        n_per_sr = self.N_EFF * arcmin2_per_sr
        n_per_bin = n_per_sr / self.N_WL_BINS

        # Shape noise power spectrum: N_ell = sigma_eps^2 / n_bar
        self.noise_wl = self.SIGMA_EPS**2 / n_per_bin

        # Shot noise for GC (approximate)
        # n_gc ~ 1700 deg^{-2} for H-alpha (Euclid spec)
        n_gc_per_sr = 1700 * (np.pi / 180)**(-2)
        n_gc_per_bin = n_gc_per_sr / self.N_GC_BINS
        self.noise_gc = 1.0 / n_gc_per_bin

    def _cl_wl_model(self, ell, z_mid, mu_func=None, sigma_func=None):
        """Simplified WL angular power spectrum model.

        C_ell^{ij} ~ (H_0/c)^4 * int W_i(chi) W_j(chi) P_delta(ell/chi, z) dchi/chi^2

        In the simplified version, we use:
        C_ell ~ A * Sigma^2(k_eff, z) * ell^{-1.2} * (1+z)^{-0.5}

        where k_eff = ell / chi(z) and A is normalized to realistic amplitude.
        """
        if mu_func is None:
            sigma2 = 1.0  # GR
        else:
            k_eff = ell / (3000.0 / (1 + z_mid))  # approximate chi -> k mapping
            sigma2 = sigma_func(k_eff, z_mid)**2

        # Approximate Cl shape (normalized to ~10^{-7} at ell=100, z=0.5)
        cl = 1e-7 * sigma2 * (ell / 100.0)**(-1.2) * (1 + z_mid)**(-0.5)
        return cl

    def _cl_gc_model(self, ell, z_mid, mu_func=None):
        """Simplified GC angular power spectrum."""
        if mu_func is None:
            mu2 = 1.0
        else:
            k_eff = ell / (3000.0 / (1 + z_mid))
            mu2 = mu_func(k_eff, z_mid)**2

        # Galaxy clustering Cl (bias^2 * mu^2 * P_m)
        b = 1.0 + 0.5 * z_mid  # simple linear bias model
        cl = 5e-7 * b**2 * mu2 * (ell / 100.0)**(-1.5) * (1 + z_mid)**(-1.0)
        return cl

    def _generate_mock(self):
        """Generate mock data vector and diagonal covariance."""
        from src.efc_mg_functions import mu_efc, sigma_efc

        if self.fiducial == "EFC":
            mu_func = lambda k, z: mu_efc(np.atleast_1d(k), np.atleast_1d(z))
            sig_func = lambda k, z: sigma_efc(np.atleast_1d(k), np.atleast_1d(z))
        else:
            mu_func = None
            sig_func = None

        # WL auto-spectra (10 bins -> 55 unique pairs)
        data_wl = []
        var_wl = []
        for i in range(self.N_WL_BINS):
            z_i = (self.WL_ZBIN_EDGES[i] + self.WL_ZBIN_EDGES[i+1]) / 2
            for ell in self.ell_wl:
                cl = self._cl_wl_model(ell, z_i, mu_func, sig_func)
                # Gaussian covariance: var = 2/(f_sky*(2ell+1)*Delta_ell) * (Cl + Nl)^2
                delta_ell = 0.3 * ell  # log-bin width
                n_modes = self.F_SKY * (2 * ell + 1) * delta_ell
                var = 2.0 / n_modes * (cl + self.noise_wl)**2
                data_wl.append(cl)
                var_wl.append(var)

        # GC auto-spectra (4 bins)
        data_gc = []
        var_gc = []
        for i in range(self.N_GC_BINS):
            z_i = (self.GC_ZBIN_EDGES[i] + self.GC_ZBIN_EDGES[i+1]) / 2
            for ell in self.ell_gc:
                cl = self._cl_gc_model(ell, z_i, mu_func)
                delta_ell = 0.3 * ell
                n_modes = self.F_SKY * (2 * ell + 1) * delta_ell
                var = 2.0 / n_modes * (cl + self.noise_gc)**2
                data_gc.append(cl)
                var_gc.append(var)

        self.data_vector = np.concatenate([data_wl, data_gc])
        self.covariance_diag = np.concatenate([var_wl, var_gc])
        self.inv_cov_diag = 1.0 / self.covariance_diag

    def logp(self, cl_theory):
        """Gaussian log-likelihood.

        Parameters
        ----------
        cl_theory : array
            Theory Cl vector (same ordering as data_vector)

        Returns
        -------
        logp : float
        """
        delta = self.data_vector - cl_theory
        chi2 = np.sum(delta**2 * self.inv_cov_diag)
        return -0.5 * chi2

    def compute_efc_theory(self, R0=None, kc=None, eps_tot=None):
        """Compute theory Cl vector for given EFC parameters."""
        from src.efc_mg_functions import mu_efc, sigma_efc, R_0, K_C, EPS_TOT

        R0 = R0 or R_0
        kc = kc or K_C
        eps = eps_tot or EPS_TOT

        mu_func = lambda k, z: mu_efc(np.atleast_1d(k), np.atleast_1d(z), R0, kc)
        sig_func = lambda k, z: sigma_efc(np.atleast_1d(k), np.atleast_1d(z), R0, kc, eps)

        theory_wl = []
        for i in range(self.N_WL_BINS):
            z_i = (self.WL_ZBIN_EDGES[i] + self.WL_ZBIN_EDGES[i+1]) / 2
            for ell in self.ell_wl:
                theory_wl.append(self._cl_wl_model(ell, z_i, mu_func, sig_func))

        theory_gc = []
        for i in range(self.N_GC_BINS):
            z_i = (self.GC_ZBIN_EDGES[i] + self.GC_ZBIN_EDGES[i+1]) / 2
            for ell in self.ell_gc:
                theory_gc.append(self._cl_gc_model(ell, z_i, mu_func))

        return np.concatenate([theory_wl, theory_gc])

    def forecast_delta_chi2(self):
        """Compute delta-chi2 between EFC and LCDM on mock data."""
        # LCDM theory (mu=Sigma=1)
        lcdm_mock = EuclidDR1MockLikelihood(fiducial_model="LCDM")
        cl_lcdm = lcdm_mock.data_vector

        # EFC theory
        cl_efc = self.compute_efc_theory()

        # Both evaluated on the same mock
        chi2_lcdm = -2 * self.logp(cl_lcdm)
        chi2_efc = -2 * self.logp(cl_efc)

        return chi2_efc - chi2_lcdm

    def save_mock(self, path):
        """Save mock data to JSON for reproducibility."""
        output = {
            "fiducial": self.fiducial,
            "f_sky": self.F_SKY,
            "n_data_wl": self.N_WL_BINS * self.N_ELL_WL,
            "n_data_gc": self.N_GC_BINS * self.N_ELL_GC,
            "n_total": len(self.data_vector),
            "data_vector": self.data_vector.tolist(),
            "covariance_diag": self.covariance_diag.tolist(),
        }
        with open(path, 'w') as f:
            json.dump(output, f, indent=2)


if __name__ == "__main__":
    print("=== Euclid DR1 Mock Likelihood Test ===")
    print()

    # Generate LCDM fiducial mock
    mock_lcdm = EuclidDR1MockLikelihood(fiducial_model="LCDM")
    print(f"Data vector length: {len(mock_lcdm.data_vector)}")
    print(f"  WL: {mock_lcdm.N_WL_BINS} bins x {mock_lcdm.N_ELL_WL} ell = {mock_lcdm.N_WL_BINS * mock_lcdm.N_ELL_WL}")
    print(f"  GC: {mock_lcdm.N_GC_BINS} bins x {mock_lcdm.N_ELL_GC} ell = {mock_lcdm.N_GC_BINS * mock_lcdm.N_ELL_GC}")
    print(f"  f_sky = {mock_lcdm.F_SKY:.4f}")
    print()

    # EFC on LCDM mock
    cl_efc = mock_lcdm.compute_efc_theory()
    logp_efc = mock_lcdm.logp(cl_efc)
    logp_lcdm = mock_lcdm.logp(mock_lcdm.data_vector)
    delta_chi2 = -2 * (logp_efc - logp_lcdm)

    print(f"EFC on LCDM mock:")
    print(f"  log L(LCDM) = {logp_lcdm:.1f}")
    print(f"  log L(EFC)  = {logp_efc:.1f}")
    print(f"  Delta chi2  = {delta_chi2:.1f}")
    print()

    # Generate EFC fiducial mock
    mock_efc = EuclidDR1MockLikelihood(fiducial_model="EFC")
    cl_lcdm_on_efc = mock_lcdm.data_vector  # LCDM theory
    logp_lcdm_on_efc = mock_efc.logp(cl_lcdm_on_efc)
    logp_efc_on_efc = mock_efc.logp(mock_efc.data_vector)
    delta_chi2_2 = -2 * (logp_lcdm_on_efc - logp_efc_on_efc)

    print(f"LCDM on EFC mock:")
    print(f"  Delta chi2 = {delta_chi2_2:.1f}")

    mock_lcdm.save_mock("data/euclid_dr1_mock_lcdm.json")
    print("\nMock saved to data/euclid_dr1_mock_lcdm.json")
