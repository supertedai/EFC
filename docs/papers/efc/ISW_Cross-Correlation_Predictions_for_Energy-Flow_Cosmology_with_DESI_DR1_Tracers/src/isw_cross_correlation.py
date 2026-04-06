"""
ISW Cross-Correlation Predictions for Energy-Flow Cosmology

Computes ISW-galaxy cross-correlation C_l^Tg for EFC, including
kernel decomposition and the cancellation metric C.
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, Optional


@dataclass
class ISWKernel:
    """
    ISW kernel decomposition for EFC.

    K(a) = d/d(ln a) [mu * D / a] = K_mu + K_mu'

    K_mu:  Standard ISW term (potential decay in accelerating universe)
    K_mu': EFC transition term (temporal variation of mu)
    """
    z: np.ndarray
    K_mu: np.ndarray
    K_mu_prime: np.ndarray

    @property
    def K_total(self) -> np.ndarray:
        """Total ISW kernel."""
        return self.K_mu + self.K_mu_prime


class ISWCrossCorrelation:
    """
    ISW-galaxy cross-correlation predictions for EFC.

    Uses modified Poisson equation mu(a) = 1 + beta * S(a) with
    smooth transition function S(a).

    Parameters
    ----------
    beta : float
        EFC coupling amplitude (default 0.16).
    a_t : float
        Transition scale factor (default 0.55, z_t = 0.82).
    sigma_cos : float
        Transition width parameter (default 0.25).
    Omega_m : float
        Present-day matter density parameter.
    H0 : float
        Hubble constant in km/s/Mpc.
    """

    c = 299792.458  # km/s

    def __init__(
        self,
        beta: float = 0.16,
        a_t: float = 0.55,
        sigma_cos: float = 0.25,
        Omega_m: float = 0.315,
        H0: float = 67.4,
    ):
        self.beta = beta
        self.a_t = a_t
        self.z_t = 1.0 / a_t - 1.0
        self.sigma_cos = sigma_cos
        self.Omega_m = Omega_m
        self.Omega_L = 1.0 - Omega_m
        self.H0 = H0

    def S(self, a: np.ndarray) -> np.ndarray:
        """
        Smooth transition function.

        S(a) = 0.5 * [1 + tanh((ln a - ln a_t) / sigma_cos)]
        """
        a = np.asarray(a, dtype=float)
        return 0.5 * (1.0 + np.tanh((np.log(a) - np.log(self.a_t)) / self.sigma_cos))

    def dS_dlna(self, a: np.ndarray) -> np.ndarray:
        """Derivative dS/d(ln a)."""
        a = np.asarray(a, dtype=float)
        x = (np.log(a) - np.log(self.a_t)) / self.sigma_cos
        return 0.5 / self.sigma_cos / np.cosh(x)**2

    def mu(self, a: np.ndarray) -> np.ndarray:
        """Effective gravitational coupling mu(a) = 1 + beta * S(a)."""
        return 1.0 + self.beta * self.S(a)

    def dmu_dlna(self, a: np.ndarray) -> np.ndarray:
        """Derivative d(mu)/d(ln a)."""
        return self.beta * self.dS_dlna(a)

    def E(self, z: np.ndarray) -> np.ndarray:
        """Dimensionless Hubble parameter E(z) = H(z)/H0."""
        z = np.asarray(z, dtype=float)
        return np.sqrt(self.Omega_m * (1 + z)**3 + self.Omega_L)

    def H(self, z: np.ndarray) -> np.ndarray:
        """Hubble parameter H(z) in km/s/Mpc."""
        return self.H0 * self.E(z)

    def Omega_m_z(self, z: np.ndarray) -> np.ndarray:
        """Matter density at redshift z."""
        z = np.asarray(z, dtype=float)
        E2 = self.Omega_m * (1 + z)**3 + self.Omega_L
        return self.Omega_m * (1 + z)**3 / E2

    def comoving_distance(self, z: float, n_int: int = 1000) -> float:
        """Comoving distance chi(z) in Mpc/h."""
        z_arr = np.linspace(0, z, n_int)
        return float(self.c * np.trapezoid(1.0 / self.H(z_arr), z_arr))

    def growth_factor_approx(self, z: np.ndarray) -> np.ndarray:
        """
        Approximate growth factor D(z) using Carroll et al. (1992).

        Includes EFC mu modification via enhanced growth.
        """
        z = np.asarray(z, dtype=float)
        a = 1.0 / (1.0 + z)
        om_z = self.Omega_m_z(z)
        ol_z = 1.0 - om_z
        mu_val = self.mu(a)

        # Carroll approximation modified by mu
        D = mu_val * (5.0 / 2.0) * om_z / (
            om_z**(4.0/7.0) - ol_z + (1.0 + om_z / 2.0) * (1.0 + ol_z / 70.0)
        )
        # Normalise to D(0) = 1
        D0 = self.growth_factor_approx_lcdm(0.0)
        return D / D[0] if len(D) > 0 else D

    def growth_factor_approx_lcdm(self, z: float) -> float:
        """LCDM growth factor at single redshift."""
        om_z = float(self.Omega_m_z(np.array([z]))[0])
        ol_z = 1.0 - om_z
        return (5.0 / 2.0) * om_z / (
            om_z**(4.0/7.0) - ol_z + (1.0 + om_z / 2.0) * (1.0 + ol_z / 70.0)
        )

    def isw_kernel(self, z_grid: np.ndarray) -> ISWKernel:
        """
        Compute ISW kernel decomposition K(a) = K_mu + K_mu'.

        K_mu:  standard ISW from potential decay
        K_mu': EFC transition contribution from d(mu)/dt
        """
        a = 1.0 / (1.0 + z_grid)
        mu_vals = self.mu(a)
        dmu_vals = self.dmu_dlna(a)

        # Approximate D(z) variation
        D_approx = np.ones_like(z_grid)
        for i, z in enumerate(z_grid):
            D_approx[i] = self.growth_factor_approx_lcdm(z)
        D_approx = D_approx / D_approx[0]

        # K_mu: standard term ~ mu * dD/dlna / a - mu*D/a
        dD_dlna = np.gradient(D_approx, np.log(a))
        K_mu = mu_vals * (dD_dlna / a - D_approx / a)

        # K_mu': transition term ~ dmu/dlna * D/a
        K_mu_prime = dmu_vals * D_approx / a

        return ISWKernel(z=z_grid, K_mu=K_mu, K_mu_prime=K_mu_prime)

    def cancellation_metric(self, z_eff: float, ell_min: int = 2, ell_max: int = 60) -> float:
        """
        Compute cancellation metric C for a tracer at z_eff.

        C = 1 - |sum C_l,tot| / (|sum C_l,mu| + |sum C_l,mu'|)

        C = 0: no cancellation (LCDM-like)
        C = 1: perfect cancellation
        """
        z_grid = np.linspace(0.01, 4.0, 500)
        kernel = self.isw_kernel(z_grid)

        # Simplified: integrate kernel contributions weighted by
        # proximity to z_eff (Gaussian window approximation)
        sigma_z = 0.15
        W = np.exp(-0.5 * ((z_grid - z_eff) / sigma_z)**2)
        W /= np.sum(W)

        sum_mu = np.sum(W * kernel.K_mu)
        sum_mu_prime = np.sum(W * kernel.K_mu_prime)
        sum_total = sum_mu + sum_mu_prime

        denom = abs(sum_mu) + abs(sum_mu_prime)
        if denom < 1e-30:
            return 0.0

        return 1.0 - abs(sum_total) / denom

    def A_ISW(self, z_eff: float) -> float:
        """
        ISW amplitude relative to LCDM.

        A_ISW = |C_l,EFC| / |C_l,LCDM| ~ 1 - C
        """
        C = self.cancellation_metric(z_eff)
        return max(0.0, 1.0 - C)

    def predict_tracers(self) -> Dict[str, Dict]:
        """
        Predict C and A_ISW for DESI DR1 tracer samples.
        """
        tracers = {
            'LRGz0': {'z_eff': 0.51, 'description': 'Low-z LRG'},
            'LRG_ELG': {'z_eff': 0.93, 'description': 'LRG+ELG overlap'},
            'ELG': {'z_eff': 1.32, 'description': 'Emission line galaxies'},
        }

        results = {}
        for name, info in tracers.items():
            C = self.cancellation_metric(info['z_eff'])
            A = self.A_ISW(info['z_eff'])
            results[name] = {
                'z_eff': info['z_eff'],
                'description': info['description'],
                'C': C,
                'A_ISW': A,
            }

        return results


# Paper results for reference
PAPER_RESULTS = {
    'parameters': {
        'beta': 0.16,
        'a_t': 0.55,
        'z_t': 0.82,
        'sigma_cos': [0.20, 0.30],
        'multipole_range': [2, 60],
    },
    'tracer_predictions': {
        'LRGz0': {'z_eff': 0.51, 'C': 0.59, 'A_ISW': 0.56},
        'LRG_ELG': {'z_eff': 0.93, 'C': 0.79, 'A_ISW': 0.29},
        'ELG': {'z_eff': 1.32, 'C': 0.96},
    },
    'lcdm_expectation': {'A_ISW': 1.0, 'C': 0.0},
    'observational_benchmark': {
        'desi_legacy_planck': {'A_ISW': 0.984, 'error': 0.349, 'source': 'Hang et al. 2021'},
    },
    'falsification': {
        'EFC_falsified_if': 'Tomographic bins overlapping z_t yield A_ISW = 1.0 and C = 0',
        'LCDM_challenged_if': 'A_ISW << 1 with high C at z_t',
    },
}


if __name__ == '__main__':
    isw = ISWCrossCorrelation(beta=0.16, a_t=0.55)
    tracers = isw.predict_tracers()
    for name, result in tracers.items():
        print(f"{name}: z_eff={result['z_eff']}, C={result['C']:.2f}, A_ISW={result['A_ISW']:.2f}")
