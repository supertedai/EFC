"""EFC Screening Model — Python implementation.

Multi-scale empirical validation: SPARC RAR (k=0.415, g†=2.51e-10),
KiDS-1000 lensing, Bullet Cluster, Hubble tension via a_G=0.094.

Reference: Magnusson (2026), DOI: 10.6084/m9.figshare.31940469
"""

import math
from dataclasses import dataclass, field
from typing import List

E = math.e
C_LIGHT = 2.998e5  # km/s


@dataclass
class EFCScreening:
    """EFC screening model: ln mu = k * ln(1 + g†/g_bar). Eq. (1).

    Attributes:
        k: Screening exponent (0.415 +/- 0.029).
        g_dagger: Transition acceleration (m/s^2).
        sigma_int: Intrinsic scatter in ln mu.
    """
    k: float = 0.415
    g_dagger: float = 2.51e-10
    sigma_int: float = 0.33  # in ln mu (~0.14 dex)

    def ln_mu(self, g_bar: float) -> float:
        """Compute ln(mu) = k * ln(1 + g†/g_bar). Eq. (1)."""
        if g_bar <= 0:
            return float('inf')
        return self.k * math.log(1.0 + self.g_dagger / g_bar)

    def mu(self, g_bar: float) -> float:
        """Gravitational enhancement factor mu = (1 + g†/g_bar)^k."""
        if g_bar <= 0:
            return float('inf')
        return (1.0 + self.g_dagger / g_bar) ** self.k

    def g_obs(self, g_bar: float) -> float:
        """Observed acceleration: g_obs = g_bar * mu(g_bar)."""
        return g_bar * self.mu(g_bar)

    def rar_curve(self, g_bar_values: List[float]) -> List[dict]:
        """Compute RAR for array of baryonic accelerations."""
        return [
            {"g_bar": g, "mu": self.mu(g), "g_obs": self.g_obs(g), "ln_mu": self.ln_mu(g)}
            for g in g_bar_values
        ]

    def log_likelihood_point(self, y_obs: float, g_bar: float, sigma_y: float) -> float:
        """Single-point log-likelihood. Eq. (3)."""
        y_model = self.ln_mu(g_bar)
        sigma_tot2 = sigma_y**2 + self.sigma_int**2
        return -0.5 * ((y_obs - y_model)**2 / sigma_tot2 + math.log(sigma_tot2))

    def fit_summary(self) -> dict:
        """Summary of canonical fit results (Table 1)."""
        return {
            "k": {"value": self.k, "error": 0.029, "range": [0.38, 0.45]},
            "g_dagger": {"value": self.g_dagger, "error": 0.60e-10, "unit": "m/s^2"},
            "sigma_int": {"value": self.sigma_int, "unit": "ln mu", "dex": self.sigma_int / math.log(10)},
            "n_galaxies": 174,
            "n_data_points": 3264,
            "bootstrap_iterations": 500,
        }


@dataclass
class CrossScaleConsistency:
    """Phase-gain C = k/a_G connects galactic and cosmological scales.

    Attributes:
        k: Screening exponent from SPARC.
        a_G: Universal coupling from H0 analysis.
    """
    k: float = 0.415
    a_G: float = 0.094

    @property
    def C(self) -> float:
        """Phase-gain parameter C = k/a_G."""
        return self.k / self.a_G

    @property
    def C_error(self) -> float:
        """Propagated error on C."""
        dk = 0.029
        da = 0.01
        return self.C * math.sqrt((dk / self.k)**2 + (da / self.a_G)**2)

    def closure_test(self) -> dict:
        """Test closure conjecture C = 2e - 1 ~ 4.44."""
        C_conj = 2 * E - 1
        return {
            "C_observed": self.C,
            "C_error": self.C_error,
            "C_conjectured": C_conj,
            "deviation_sigma": abs(self.C - C_conj) / self.C_error,
            "consistent": abs(self.C - C_conj) < 2 * self.C_error,
        }


@dataclass
class KiDS1000Analysis:
    """KiDS-1000 weak lensing analysis (Case A). Section 4."""
    alpha_L2: float = 0.10
    delta_log_L: float = -50.9
    S8_efc: float = 0.685
    S8_lcdm: float = 0.739

    def summary(self) -> dict:
        return {
            "case": "A (phenomenological lensing boost)",
            "alpha_L2": self.alpha_L2,
            "delta_neg2lnL": self.delta_log_L,
            "S8_efc_case_a": self.S8_efc,
            "S8_lcdm": self.S8_lcdm,
            "note": "Case A worsens S8 tension (3.6 sigma vs 2.3 sigma). Case B (mu in growth) needed.",
            "low_z_localisation": "3.2x stronger in low-z bins (consistent with late-time activation)",
        }

    def s8_landscape(self) -> dict:
        """Updated Stage-III S8 landscape (Table 4)."""
        return {
            "kids_legacy": {"S8": 0.815, "source": "Wright et al. (2025)"},
            "hsc_y3": {"S8": 0.805, "source": "Choppin de Janvry et al. (2025)"},
            "combined_wl": {"S8": 0.813, "source": "Combined KiDS+DES+HSC"},
            "cmb_lensing": {"S8": 0.828, "source": "Combined CMB lensing"},
            "efc_beta_008": {"sigma8": 0.805, "note": "Matches without tuning"},
        }


@dataclass
class BulletClusterInterpretation:
    """EFC entropy-gradient interpretation of Bullet Cluster. Section 5."""

    @staticmethod
    def effective_potential_description() -> dict:
        return {
            "equation": "Phi_eff = Phi_N + alpha * nabla_S",
            "mechanism": {
                "shocked_gas": "High entropy, steep negative gradients → reduced enhancement",
                "galaxies": "Moderate entropy, gentle gradients → maintained enhancement",
            },
            "prediction": "Lensing peak at galaxy concentrations, not gas peak",
            "offset": "~150 kpc (set by shock-front geometry)",
            "status": "Qualitative; hydrodynamic simulations with EFC coupling needed",
        }


@dataclass
class HubbleTension:
    """H0 tension resolution via entropy-modified Friedmann. Section 6."""
    H0_SH0ES: float = 73.0
    H0_Planck: float = 67.4

    @property
    def a_H0(self) -> float:
        """a_H0 derived from H0 ratio. Eq. (8-9)."""
        return math.log(self.H0_SH0ES / self.H0_Planck) / 1.71

    @property
    def a_G(self) -> float:
        """a_G = 2 * a_H0. Eq. (10)."""
        return 2 * self.a_H0

    def derivation_chain(self) -> dict:
        return {
            "ln_ratio": math.log(self.H0_SH0ES / self.H0_Planck),
            "a_H0": self.a_H0,
            "a_G": self.a_G,
            "note": "Factor 1/2 emerges from Friedmann equation structure (H^2 ~ G*rho), not fitted",
        }


@dataclass
class ClosureConjecture:
    """Closure conjectures: g† = cH0/e and C = 2e-1. Section 6.3."""

    @staticmethod
    def g_dagger_from_H0(H0_km_s_Mpc: float) -> dict:
        """Compute g† = c*H0/e. Eq. (11)."""
        H0_per_s = H0_km_s_Mpc / 3.086e19  # Convert to 1/s
        g_pred = C_LIGHT * 1e3 * H0_per_s / E  # m/s^2
        return {
            "H0": H0_km_s_Mpc,
            "g_dagger_predicted": g_pred,
            "g_dagger_observed": 2.51e-10,
            "formula": "g† = c*H0/e",
        }

    @staticmethod
    def H0_from_g_dagger(g_dagger: float) -> dict:
        """Invert: H0 = g†*e/c. From Eq. (11)."""
        H0_per_s = g_dagger * E / (C_LIGHT * 1e3)
        H0 = H0_per_s * 3.086e19
        return {
            "g_dagger": g_dagger,
            "H0_predicted": H0,
            "H0_error": 16.8,
            "unit": "km/s/Mpc",
        }

    @staticmethod
    def C_conjecture() -> dict:
        return {"C_conjectured": 2 * E - 1, "C_observed": 4.4, "C_error": 0.6}


# Convenience functions
def compute_mu(g_bar: float, k: float = 0.415, g_dagger: float = 2.51e-10) -> float:
    """Compute mu = (1 + g†/g_bar)^k."""
    return (1.0 + g_dagger / g_bar) ** k if g_bar > 0 else float('inf')

def compute_phase_gain(k: float = 0.415, a_G: float = 0.094) -> float:
    """Compute phase-gain C = k/a_G."""
    return k / a_G

def compute_a_G(H0_high: float = 73.0, H0_low: float = 67.4) -> float:
    """Derive a_G from H0 values. a_G = 2*a_H0."""
    return 2.0 * math.log(H0_high / H0_low) / 1.71
