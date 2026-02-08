"""
EFC Transfer Test: DESI DR2 to BOSS DR12

Implementation of the cross-survey validation methodology for Energy-Flow Cosmology.
Tests whether DESI-derived parameters successfully predict BOSS observations.
"""

import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class BOSSData:
    """BOSS DR12 consensus BAO measurements."""

    # Effective redshifts
    z_eff: np.ndarray = None

    # Observed D_M/r_s values
    DM_over_rs: np.ndarray = None

    # Observed D_H/r_s values
    DH_over_rs: np.ndarray = None

    # Full covariance matrix (6x6)
    covariance: np.ndarray = None

    def __post_init__(self):
        """Initialize with BOSS DR12 consensus values."""
        if self.z_eff is None:
            self.z_eff = np.array([0.38, 0.51, 0.61])

        # BOSS DR12 consensus measurements (Alam et al. 2017)
        if self.DM_over_rs is None:
            self.DM_over_rs = np.array([10.27, 13.38, 15.87])

        if self.DH_over_rs is None:
            self.DH_over_rs = np.array([24.89, 22.43, 20.75])

    @property
    def data_vector(self) -> np.ndarray:
        """Combined data vector [DM/rs, DH/rs]."""
        return np.concatenate([self.DM_over_rs, self.DH_over_rs])

    @property
    def n_points(self) -> int:
        """Total number of data points."""
        return len(self.data_vector)


class EFCTransferTest:
    """
    EFC transfer test implementation.

    Tests whether DESI-derived EFC parameters successfully predict
    BOSS DR12 BAO observations without refitting.
    """

    # Planck 2018 baseline cosmology
    H0 = 67.4  # km/s/Mpc
    Omega_m = 0.315
    Omega_L = 1 - 0.315
    r_s = 147.09  # Mpc
    c = 299792.458  # km/s

    def __init__(
        self,
        z_L1L2: float = 1.01,
        alpha_L2: float = 0.045,
        delta_z: float = 0.05
    ):
        """
        Initialize EFC transfer test.

        Parameters
        ----------
        z_L1L2 : float
            Transition redshift (DESI best-fit: 1.01)
        alpha_L2 : float
            L2 amplitude (DESI best-fit: 0.045)
        delta_z : float
            Transition width (default: 0.05)
        """
        self.z_L1L2 = z_L1L2
        self.alpha_L2 = alpha_L2
        self.delta_z = delta_z
        self.boss_data = BOSSData()

    def theta(self, z: np.ndarray) -> np.ndarray:
        """
        Regime gating function.

        Θ(z) = ½[1 + tanh((z_L1L2 - z) / Δz)]

        Returns ~1 for z < z_L1L2 (L2 active)
        Returns ~0 for z > z_L1L2 (ΛCDM)
        """
        return 0.5 * (1 + np.tanh((self.z_L1L2 - z) / self.delta_z))

    def E_LCDM(self, z: np.ndarray) -> np.ndarray:
        """ΛCDM normalized Hubble parameter E(z) = H(z)/H0."""
        return np.sqrt(self.Omega_m * (1 + z)**3 + self.Omega_L)

    def E_EFC(self, z: np.ndarray) -> np.ndarray:
        """
        EFC modified Hubble parameter.

        E_EFC(z) = E_ΛCDM(z) × [1 + α_L2 · Θ(z)]
        """
        return self.E_LCDM(z) * (1 + self.alpha_L2 * self.theta(z))

    def H_LCDM(self, z: np.ndarray) -> np.ndarray:
        """ΛCDM Hubble parameter H(z) in km/s/Mpc."""
        return self.H0 * self.E_LCDM(z)

    def H_EFC(self, z: np.ndarray) -> np.ndarray:
        """EFC modified Hubble parameter H(z) in km/s/Mpc."""
        return self.H0 * self.E_EFC(z)

    def DH_LCDM(self, z: np.ndarray) -> np.ndarray:
        """ΛCDM Hubble distance D_H(z) = c/H(z) in Mpc."""
        return self.c / self.H_LCDM(z)

    def DH_EFC(self, z: np.ndarray) -> np.ndarray:
        """EFC Hubble distance D_H(z) = c/H(z) in Mpc."""
        return self.c / self.H_EFC(z)

    def DM_LCDM(self, z: np.ndarray, n_int: int = 1000) -> np.ndarray:
        """
        ΛCDM comoving angular diameter distance D_M(z).

        D_M(z) = c ∫₀ᶻ dz'/H(z')
        """
        DM = np.zeros_like(z)
        for i, zi in enumerate(z):
            z_int = np.linspace(0, zi, n_int)
            integrand = 1 / self.H_LCDM(z_int)
            DM[i] = self.c * np.trapz(integrand, z_int)
        return DM

    def DM_EFC(self, z: np.ndarray, n_int: int = 1000) -> np.ndarray:
        """
        EFC comoving angular diameter distance D_M(z).

        D_M(z) = c ∫₀ᶻ dz'/H_EFC(z')
        """
        DM = np.zeros_like(z)
        for i, zi in enumerate(z):
            z_int = np.linspace(0, zi, n_int)
            integrand = 1 / self.H_EFC(z_int)
            DM[i] = self.c * np.trapz(integrand, z_int)
        return DM

    def model_vector_LCDM(self) -> np.ndarray:
        """ΛCDM prediction for BOSS data vector."""
        z = self.boss_data.z_eff
        DM = self.DM_LCDM(z) / self.r_s
        DH = self.DH_LCDM(z) / self.r_s
        return np.concatenate([DM, DH])

    def model_vector_EFC(self) -> np.ndarray:
        """EFC prediction for BOSS data vector."""
        z = self.boss_data.z_eff
        DM = self.DM_EFC(z) / self.r_s
        DH = self.DH_EFC(z) / self.r_s
        return np.concatenate([DM, DH])

    def chi2(
        self,
        model: np.ndarray,
        covariance: Optional[np.ndarray] = None
    ) -> float:
        """
        Compute χ² for a model prediction.

        χ² = (d - m)ᵀ C⁻¹ (d - m)
        """
        data = self.boss_data.data_vector
        residual = data - model

        if covariance is None:
            # Use diagonal approximation
            # Typical ~2% fractional errors
            sigma = 0.02 * data
            return np.sum((residual / sigma)**2)
        else:
            C_inv = np.linalg.inv(covariance)
            return residual @ C_inv @ residual

    def transfer_test(
        self,
        covariance: Optional[np.ndarray] = None
    ) -> Dict:
        """
        Perform transfer test.

        Returns
        -------
        dict with chi2_LCDM, chi2_EFC, delta_chi2
        """
        model_LCDM = self.model_vector_LCDM()
        model_EFC = self.model_vector_EFC()

        chi2_LCDM = self.chi2(model_LCDM, covariance)
        chi2_EFC = self.chi2(model_EFC, covariance)

        return {
            'chi2_LCDM': chi2_LCDM,
            'chi2_EFC': chi2_EFC,
            'delta_chi2': chi2_EFC - chi2_LCDM,
            'z_L1L2': self.z_L1L2,
            'alpha_L2': self.alpha_L2,
            'transfer_supported': (chi2_EFC - chi2_LCDM) < 0
        }

    def robustness_sweep(
        self,
        full_covariance: np.ndarray,
        n_rho: int = 11
    ) -> Dict:
        """
        Sweep covariance interpolation parameter.

        C(ρ) = (1-ρ) diag(C) + ρ C

        Tests robustness from diagonal (ρ=0) to full (ρ=1).
        """
        rho_values = np.linspace(0, 1, n_rho)
        delta_chi2 = []

        diag_C = np.diag(np.diag(full_covariance))

        for rho in rho_values:
            C_interp = (1 - rho) * diag_C + rho * full_covariance
            result = self.transfer_test(C_interp)
            delta_chi2.append(result['delta_chi2'])

        return {
            'rho': rho_values,
            'delta_chi2': np.array(delta_chi2),
            'diagonal_delta_chi2': delta_chi2[0],
            'full_delta_chi2': delta_chi2[-1],
            'all_negative': all(d < 0 for d in delta_chi2)
        }


class CovarianceDiagnostics:
    """Covariance diagnostic tests."""

    @staticmethod
    def whitening_analysis(
        residual_LCDM: np.ndarray,
        residual_EFC: np.ndarray,
        covariance: np.ndarray
    ) -> Dict:
        """
        Whitening analysis via Cholesky decomposition.

        w = L⁻¹ r where C = L Lᵀ
        """
        L = np.linalg.cholesky(covariance)
        L_inv = np.linalg.inv(L)

        w_LCDM = L_inv @ residual_LCDM
        w_EFC = L_inv @ residual_EFC

        chi2_components_LCDM = w_LCDM**2
        chi2_components_EFC = w_EFC**2

        return {
            'w_LCDM': w_LCDM,
            'w_EFC': w_EFC,
            'chi2_LCDM': chi2_components_LCDM,
            'chi2_EFC': chi2_components_EFC,
            'delta_chi2': chi2_components_EFC - chi2_components_LCDM,
            'total_LCDM': np.sum(chi2_components_LCDM),
            'total_EFC': np.sum(chi2_components_EFC)
        }

    @staticmethod
    def eigenmode_analysis(
        residual_LCDM: np.ndarray,
        residual_EFC: np.ndarray,
        covariance: np.ndarray
    ) -> Dict:
        """
        Eigenmode decomposition analysis.

        C = U diag(λ) Uᵀ
        χ² = Σᵢ aᵢ²/λᵢ where a = Uᵀ r
        """
        eigenvalues, eigenvectors = np.linalg.eigh(covariance)

        a_LCDM = eigenvectors.T @ residual_LCDM
        a_EFC = eigenvectors.T @ residual_EFC

        chi2_modes_LCDM = a_LCDM**2 / eigenvalues
        chi2_modes_EFC = a_EFC**2 / eigenvalues

        # Split by eigenvalue magnitude
        median_lambda = np.median(eigenvalues)
        low_lambda = eigenvalues < median_lambda
        high_lambda = ~low_lambda

        return {
            'eigenvalues': eigenvalues,
            'chi2_LCDM': chi2_modes_LCDM,
            'chi2_EFC': chi2_modes_EFC,
            'delta_chi2': chi2_modes_EFC - chi2_modes_LCDM,
            'low_lambda_gain': np.sum((chi2_modes_EFC - chi2_modes_LCDM)[low_lambda]),
            'high_lambda_gain': np.sum((chi2_modes_EFC - chi2_modes_LCDM)[high_lambda])
        }


# Paper results for reference
PAPER_RESULTS = {
    'transfer_test': {
        'chi2_LCDM': 20.83,
        'chi2_EFC': 13.06,
        'delta_chi2': -7.77
    },
    'diagonal_covariance': {
        'delta_chi2': -4.24
    },
    'eigenmode': {
        'low_lambda_gain': -5.50,
        'high_lambda_gain': -2.27
    },
    'whitened_components': {
        'w1': {'LCDM': 1.27, 'EFC': 2.29, 'delta': 1.01},
        'w2': {'LCDM': 1.09, 'EFC': 2.14, 'delta': 1.05},
        'w3': {'LCDM': 0.01, 'EFC': 2.82, 'delta': 2.81},
        'w4': {'LCDM': 1.50, 'EFC': 0.48, 'delta': -1.02},
        'w5': {'LCDM': 15.30, 'EFC': 3.91, 'delta': -11.39},
        'w6': {'LCDM': 1.65, 'EFC': 1.43, 'delta': -0.23}
    },
    'best_fit': {
        'BOSS': {'z_L1L2': '> 0.6', 'alpha_L2': 0.036},
        'BOSS_eBOSS': {'z_L1L2': 1.60, 'alpha_L2': 0.036},
        'DESI': {'z_L1L2': 1.01, 'alpha_L2': 0.045}
    }
}


if __name__ == '__main__':
    # Quick demonstration
    test = EFCTransferTest(z_L1L2=1.01, alpha_L2=0.045)
    result = test.transfer_test()

    print("EFC Transfer Test: DESI → BOSS")
    print("=" * 40)
    print(f"DESI parameters: z_L1L2 = {test.z_L1L2}, α_L2 = {test.alpha_L2}")
    print(f"Transfer supported: {result['transfer_supported']}")
    print(f"Δχ² = {result['delta_chi2']:.2f}")
