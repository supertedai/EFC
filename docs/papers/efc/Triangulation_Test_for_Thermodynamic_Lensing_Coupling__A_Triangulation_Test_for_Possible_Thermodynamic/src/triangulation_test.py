"""
Triangulation Test for Thermodynamic-Lensing Coupling

Implementation of the methodology from:
"A Triangulation Test for Possible Thermodynamic Contributions
to Gravitational Lensing in Galaxy Clusters"
Magnusson (2026) - DOI: 10.6084/m9.figshare.31267297
"""

import numpy as np
from scipy import stats
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


# Physical constants
k_B = 1.381e-23      # Boltzmann constant [J/K]
m_p = 1.673e-27      # Proton mass [kg]
G = 6.674e-11        # Gravitational constant [m³/kg/s²]
c = 2.998e8          # Speed of light [m/s]
MU_ICM = 0.6         # Mean molecular weight for ICM


@dataclass
class ClusterData:
    """Container for cluster observational data."""
    name: str
    cluster_type: str  # 'merging' or 'relaxed'
    r_bins: np.ndarray  # Radial bins [kpc]
    M_lens: np.ndarray  # Lensing mass profile [M_sun]
    M_lens_err: np.ndarray  # Lensing mass errors
    T_profile: np.ndarray  # Temperature profile [keV]
    n_e_profile: np.ndarray  # Electron density profile [cm^-3]
    T_err: Optional[np.ndarray] = None
    n_e_err: Optional[np.ndarray] = None


class TriangulationAnalysis:
    """
    Triangulation test for thermodynamic-lensing coupling.

    Compares three independent observables:
    1. M_lens(r) - Lensing mass (geometric)
    2. M_HSE(r) - Hydrostatic mass (dynamic)
    3. |∇K(r)| - Entropy gradient (thermodynamic)

    Tests correlation between mass residual R = M_lens - M_HSE
    and entropy gradient magnitude |∇K|.
    """

    def __init__(self, data: ClusterData):
        """
        Initialize triangulation analysis.

        Parameters
        ----------
        data : ClusterData
            Cluster observational data container
        """
        self.data = data
        self.r = data.r_bins
        self.M_lens = data.M_lens
        self.T = data.T_profile
        self.n_e = data.n_e_profile

        # Computed quantities
        self._M_HSE = None
        self._K = None
        self._grad_K = None
        self._R = None

    def compute_entropy(self) -> np.ndarray:
        """
        Compute ICM entropy profile.

        K(r) = T(r) * n_e(r)^(-2/3)  [keV cm²]

        Returns
        -------
        K : ndarray
            Entropy profile
        """
        self._K = self.T * np.power(self.n_e, -2/3)
        return self._K

    def compute_entropy_gradient(self) -> np.ndarray:
        """
        Compute entropy gradient magnitude.

        |∇K(r)| ≈ |dK/dr|

        Returns
        -------
        grad_K : ndarray
            Entropy gradient profile
        """
        if self._K is None:
            self.compute_entropy()

        # Numerical gradient
        self._grad_K = np.abs(np.gradient(self._K, self.r))
        return self._grad_K

    def compute_hydrostatic_mass(self) -> np.ndarray:
        """
        Compute hydrostatic equilibrium mass.

        M_HSE(<r) = -(kT r)/(μ m_p G) × [d ln n_e/d ln r + d ln T/d ln r]

        Returns
        -------
        M_HSE : ndarray
            Hydrostatic mass profile [M_sun]
        """
        # Convert units: T in keV, r in kpc, n_e in cm^-3
        # Result in solar masses

        # Logarithmic derivatives
        d_ln_ne_d_ln_r = np.gradient(np.log(self.n_e), np.log(self.r))
        d_ln_T_d_ln_r = np.gradient(np.log(self.T), np.log(self.r))

        # Convert keV to Joules
        T_J = self.T * 1.602e-16  # keV to J

        # Convert kpc to meters
        r_m = self.r * 3.086e19  # kpc to m

        # HSE mass formula
        M_kg = -(k_B * T_J * r_m) / (MU_ICM * m_p * G) * (
            d_ln_ne_d_ln_r + d_ln_T_d_ln_r
        )

        # Convert to solar masses
        M_sun = 1.989e30  # kg
        self._M_HSE = np.abs(M_kg) / M_sun

        return self._M_HSE

    def compute_mass_residual(self) -> np.ndarray:
        """
        Compute mass residual.

        R(r) = M_lens(r) - M_HSE(r)

        Returns
        -------
        R : ndarray
            Mass residual profile
        """
        if self._M_HSE is None:
            self.compute_hydrostatic_mass()

        self._R = self.M_lens - self._M_HSE
        return self._R

    def compute_normalized_quantities(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute normalized residual and gradient for correlation analysis.

        R_norm(r) = R(r) / M_lens(r)
        G_norm(r) = |∇K(r)| / max|∇K|

        Returns
        -------
        R_norm, G_norm : tuple of ndarray
            Normalized residual and gradient
        """
        if self._R is None:
            self.compute_mass_residual()
        if self._grad_K is None:
            self.compute_entropy_gradient()

        R_norm = self._R / self.M_lens
        G_norm = self._grad_K / np.max(self._grad_K)

        return R_norm, G_norm

    def correlation_test(self) -> Dict:
        """
        Perform correlation test between mass residual and entropy gradient.

        Returns
        -------
        results : dict
            Contains Pearson/Spearman correlations, p-values, and interpretation
        """
        R_norm, G_norm = self.compute_normalized_quantities()

        # Remove NaN/inf values
        mask = np.isfinite(R_norm) & np.isfinite(G_norm)
        R_clean = R_norm[mask]
        G_clean = G_norm[mask]

        N = len(R_clean)

        # Pearson correlation
        pearson_rho, pearson_p = stats.pearsonr(R_clean, G_clean)

        # Spearman rank correlation (robust to outliers)
        spearman_rho, spearman_p = stats.spearmanr(R_clean, G_clean)

        # Significance test
        # t = ρ √[(N-2)/(1-ρ²)]
        if abs(pearson_rho) < 1:
            t_stat = pearson_rho * np.sqrt((N - 2) / (1 - pearson_rho**2))
        else:
            t_stat = np.inf

        # Required correlation for 2σ detection
        rho_2sigma = 2.0 / np.sqrt(N - 2) if N > 2 else 1.0

        results = {
            'n_bins': N,
            'pearson_rho': pearson_rho,
            'pearson_p': pearson_p,
            'spearman_rho': spearman_rho,
            'spearman_p': spearman_p,
            't_statistic': t_stat,
            'rho_required_2sigma': rho_2sigma,
            'significant_2sigma': abs(pearson_rho) > rho_2sigma,
            'interpretation': self._interpret_results(pearson_rho, pearson_p)
        }

        return results

    def _interpret_results(self, rho: float, p: float) -> str:
        """Generate interpretation of correlation results."""
        if p > 0.05:
            return "No statistically significant correlation detected (p > 0.05)"
        elif p > 0.01:
            if rho > 0:
                return "Weak positive correlation (consistent with thermodynamic coupling)"
            else:
                return "Weak negative correlation (opposite to expected sign)"
        else:
            if rho > 0:
                return "Significant positive correlation detected"
            else:
                return "Significant negative correlation (unexpected)"

    def summary(self) -> str:
        """Generate summary report of triangulation analysis."""
        results = self.correlation_test()

        report = f"""
Triangulation Test Results: {self.data.name}
{'='*50}
Cluster type: {self.data.cluster_type}
Number of radial bins: {results['n_bins']}

Correlation Analysis:
  Pearson ρ  = {results['pearson_rho']:.3f}  (p = {results['pearson_p']:.3f})
  Spearman ρ = {results['spearman_rho']:.3f} (p = {results['spearman_p']:.3f})

Detection threshold (2σ): |ρ| > {results['rho_required_2sigma']:.3f}
Significant at 2σ: {results['significant_2sigma']}

Interpretation: {results['interpretation']}
"""
        return report


def stacked_detection_threshold(n_clusters: int, bins_per_cluster: int = 57,
                                 sigma: float = 3.0) -> float:
    """
    Calculate detectable correlation for stacked cluster sample.

    Parameters
    ----------
    n_clusters : int
        Number of clusters in stack
    bins_per_cluster : int
        Average number of radial bins per cluster
    sigma : float
        Detection significance level

    Returns
    -------
    rho_min : float
        Minimum detectable correlation at given significance
    """
    N_eff = n_clusters * bins_per_cluster
    rho_min = sigma / np.sqrt(N_eff - 2)
    return rho_min


# Convenience function for quick analysis
def run_triangulation_test(r_kpc: np.ndarray, M_lens_Msun: np.ndarray,
                           T_keV: np.ndarray, n_e_cm3: np.ndarray,
                           name: str = "Cluster",
                           cluster_type: str = "unknown") -> Dict:
    """
    Run triangulation test on cluster data.

    Parameters
    ----------
    r_kpc : array
        Radial bins in kpc
    M_lens_Msun : array
        Lensing mass profile in solar masses
    T_keV : array
        Temperature profile in keV
    n_e_cm3 : array
        Electron density profile in cm^-3
    name : str
        Cluster name
    cluster_type : str
        'merging' or 'relaxed'

    Returns
    -------
    results : dict
        Correlation test results
    """
    data = ClusterData(
        name=name,
        cluster_type=cluster_type,
        r_bins=np.array(r_kpc),
        M_lens=np.array(M_lens_Msun),
        M_lens_err=np.zeros_like(M_lens_Msun),
        T_profile=np.array(T_keV),
        n_e_profile=np.array(n_e_cm3)
    )

    analysis = TriangulationAnalysis(data)
    return analysis.correlation_test()
