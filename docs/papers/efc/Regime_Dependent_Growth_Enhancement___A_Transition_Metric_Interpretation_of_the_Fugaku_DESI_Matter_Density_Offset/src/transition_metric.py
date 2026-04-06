"""
Transition Metric for Fugaku-DESI Matter Density Offset

Implements the transition estimator Delta_F = integral W(a)[mu(a)-1] d(ln a)
which reinterprets the ~10% density offset as integrated transition strength.
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class TransitionKernel:
    """Smooth bounded transition kernel for mu(a)."""
    delta_mu: float = 0.1
    a_t: float = 0.55
    sigma: float = 0.3

    def mu(self, a: np.ndarray) -> np.ndarray:
        """
        Effective gravitational coupling mu(a) = 1 + delta_mu * R(x).

        R(x) = 0.5 * [1 + tanh(x)] where x = (ln a - ln a_t) / sigma.
        """
        a = np.asarray(a, dtype=float)
        x = (np.log(a) - np.log(self.a_t)) / self.sigma
        R = 0.5 * (1.0 + np.tanh(x))
        return 1.0 + self.delta_mu * R

    def mu_minus_1(self, a: np.ndarray) -> np.ndarray:
        """Return mu(a) - 1, the deviation from GR."""
        return self.mu(a) - 1.0


class TransitionMetric:
    """
    Transition metric Delta_F for Fugaku-DESI interpretation.

    Delta_F = integral W(a) [mu(a) - 1] d(ln a)

    where W(a) is a window function centred on the transition band.

    Parameters
    ----------
    delta_mu : float
        Amplitude of effective coupling deviation.
    a_t : float
        Transition scale factor.
    sigma : float
        Transition width in ln(a).
    Omega_m : float
        Present-day matter density.
    """

    def __init__(
        self,
        delta_mu: float = 0.1,
        a_t: float = 0.55,
        sigma: float = 0.3,
        Omega_m: float = 0.315,
    ):
        self.kernel = TransitionKernel(delta_mu=delta_mu, a_t=a_t, sigma=sigma)
        self.Omega_m = Omega_m
        self.Omega_L = 1.0 - Omega_m

    def compute_delta_F(
        self,
        a_min: float = 0.01,
        a_max: float = 1.0,
        n_points: int = 5000,
    ) -> float:
        """
        Compute transition estimator Delta_F.

        Delta_F = integral_{ln a_min}^{ln a_max} W(a) [mu(a) - 1] d(ln a)

        Uses uniform window W(a) = 1 over the integration range.
        """
        lna = np.linspace(np.log(a_min), np.log(a_max), n_points)
        a_grid = np.exp(lna)

        mu_dev = self.kernel.mu_minus_1(a_grid)
        delta_F = float(np.trapezoid(mu_dev, lna))

        return delta_F

    def consistency_check(self) -> Dict[str, Dict]:
        """
        Check regime consistency conditions.

        Returns status for CMB, DESI/Fugaku, and galaxy regimes.
        """
        a_cmb = 1.0 / 1101.0
        a_desi = 1.0 / (1.0 + 0.5)  # z ~ 0.5
        a_galaxy = 1.0  # z = 0

        results = {}

        # CMB: mu ~ 1 at recombination
        mu_cmb = float(self.kernel.mu(np.array([a_cmb]))[0])
        results['CMB'] = {
            'z': 1100,
            'a': a_cmb,
            'mu': mu_cmb,
            'mu_minus_1': mu_cmb - 1.0,
            'requirement': 'mu ~ 1 at recombination',
            'status': 'satisfied' if abs(mu_cmb - 1.0) < 1e-3 else 'violated',
        }

        # DESI/Fugaku transition band
        delta_F = self.compute_delta_F()
        results['DESI_Fugaku'] = {
            'z': 0.5,
            'a': a_desi,
            'Delta_F': delta_F,
            'requirement': 'Delta_F ~ 0.1 in transition band',
            'status': 'satisfied' if 0.05 < delta_F < 0.2 else 'violated',
        }

        # Galaxy regime: mu > 1 asymptotically
        mu_gal = float(self.kernel.mu(np.array([a_galaxy]))[0])
        results['Galaxy'] = {
            'z': 0,
            'a': a_galaxy,
            'mu': mu_gal,
            'requirement': 'mu > 1 asymptotically',
            'status': 'satisfied' if mu_gal > 1.0 else 'violated',
        }

        return results

    def mu_profile(self, n_points: int = 500) -> Dict[str, np.ndarray]:
        """Return mu(a) profile for plotting."""
        a_grid = np.linspace(0.01, 1.0, n_points)
        z_grid = 1.0 / a_grid - 1.0
        mu_vals = self.kernel.mu(a_grid)

        return {
            'a': a_grid,
            'z': z_grid,
            'mu': mu_vals,
            'mu_minus_1': mu_vals - 1.0,
        }


# Paper results for reference
PAPER_RESULTS = {
    'delta_F': 0.1,
    'interpretation': '10% matter density offset = integrated transition strength',
    'consistency_conditions': [
        {'regime': 'CMB', 'requirement': 'mu ~ 1 at recombination', 'status': 'satisfied'},
        {'regime': 'DESI/Fugaku', 'requirement': 'Delta_F ~ 0.1', 'status': 'satisfied'},
        {'regime': 'Galaxy', 'requirement': 'mu > 1 asymptotically', 'status': 'satisfied'},
    ],
    'data_sources': [
        {'name': 'DESI DR2 BAO', 'reference': 'arXiv:2404.03002'},
        {'name': 'Planck 2018', 'reference': 'A&A 641, A6'},
        {'name': 'Fugaku/Uchuu simulations', 'reference': 'MNRAS 506, 4210'},
    ],
}


if __name__ == '__main__':
    tm = TransitionMetric(delta_mu=0.1)
    delta_F = tm.compute_delta_F()
    print(f"Delta_F = {delta_F:.4f}")
    check = tm.consistency_check()
    for regime, info in check.items():
        print(f"{regime}: {info['status']}")
