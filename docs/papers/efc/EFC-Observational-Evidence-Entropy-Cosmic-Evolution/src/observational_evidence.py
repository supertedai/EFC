"""
EFC -- Observational Evidence for Entropy in Cosmic Evolution

Models observational signatures that support entropy-driven cosmic
evolution: CMB anisotropies, structure formation metrics, galaxy
rotation curves, and temperature distributions.

Author: Morten Magnusson, ORCID 0009-0002-4860-5095
License: CC-BY-4.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import math


# ---------------------------------------------------------------------------
# Constants and observational reference values
# ---------------------------------------------------------------------------

BOLTZMANN_K: float = 1.380649e-23    # J/K
CMB_TEMPERATURE: float = 2.725       # K (present-day)
CMB_ANISOTROPY: float = 1e-5         # delta T / T
HUBBLE_H0: float = 67.4              # km/s/Mpc (Planck 2018)


@dataclass
class CMBObservable:
    """
    Cosmic microwave background observables relevant to entropy analysis.

    CMB anisotropies trace primordial entropy fluctuations.
    """
    temperature: float = CMB_TEMPERATURE      # K
    anisotropy_level: float = CMB_ANISOTROPY  # delta T / T
    multipole_l: int = 0
    power_spectrum_cl: float = 0.0            # muK^2

    def temperature_fluctuation(self) -> float:
        """Absolute temperature fluctuation: delta T = T * (dT/T)."""
        return self.temperature * self.anisotropy_level

    def entropy_fluctuation(self) -> float:
        """
        Entropy fluctuation from CMB: delta s ~ k_B * (delta T / T).

        In EFC, these trace the primordial entropy gradient seeds.
        """
        return BOLTZMANN_K * self.anisotropy_level

    def is_consistent_with_efc(self, predicted_anisotropy: float,
                               tolerance: float = 0.2) -> bool:
        """Check if observation is within tolerance of EFC prediction."""
        if self.anisotropy_level == 0:
            return predicted_anisotropy == 0
        ratio = predicted_anisotropy / self.anisotropy_level
        return abs(ratio - 1.0) < tolerance


@dataclass
class StructureFormationMetric:
    """
    Metrics for large-scale structure formation driven by entropy gradients.
    """
    scale_mpc: float = 0.0       # scale in Mpc
    density_contrast: float = 0.0  # delta rho / rho
    redshift: float = 0.0
    sigma_8: float = 0.811       # RMS density fluctuation at 8 Mpc/h

    def growth_factor(self, omega_m: float = 0.315) -> float:
        """
        Linear growth factor approximation (Carroll et al. 1992):
            D(z) ~ (1+z)^-1 in matter-dominated era.
        """
        return 1.0 / (1.0 + self.redshift)

    def evolved_sigma_8(self, z_ref: float = 0.0) -> float:
        """sigma_8 evolved to a different redshift."""
        d_now = 1.0 / (1.0 + z_ref)
        d_z = 1.0 / (1.0 + self.redshift)
        if d_now == 0:
            return 0.0
        return self.sigma_8 * (d_z / d_now)


@dataclass
class GalaxyRotationCurve:
    """
    Galaxy rotation curve data point for entropy-gradient analysis.

    In EFC, flat rotation curves emerge from entropy-gradient effects
    at the galaxy scale (the MOND-like regime).
    """
    radius_kpc: float = 0.0
    velocity_obs_km_s: float = 0.0
    velocity_newton_km_s: float = 0.0

    def velocity_excess(self) -> float:
        """Excess velocity over Newtonian prediction."""
        return self.velocity_obs_km_s - self.velocity_newton_km_s

    def excess_ratio(self) -> float:
        """Ratio v_obs / v_newton."""
        if self.velocity_newton_km_s <= 0:
            return 0.0
        return self.velocity_obs_km_s / self.velocity_newton_km_s

    def requires_entropy_correction(self, threshold: float = 1.1) -> bool:
        """True if observed velocity exceeds Newton by more than threshold."""
        return self.excess_ratio() > threshold


class ObservationalEvidenceModel:
    """
    Top-level model collecting observational evidence for
    entropy-driven cosmic evolution.
    """

    PARAMETERS = {
        "T_CMB": CMB_TEMPERATURE,
        "dT_over_T": CMB_ANISOTROPY,
        "H_0": HUBBLE_H0,
        "sigma_8": 0.811,
    }

    OBSERVABLES = [
        "CMB temperature anisotropies",
        "Large-scale structure (sigma_8, BAO)",
        "Galaxy rotation curves",
        "Cluster temperature profiles",
        "Cosmic expansion rate (H_0)",
    ]

    def __init__(self):
        self.cmb_data: List[CMBObservable] = []
        self.structure_data: List[StructureFormationMetric] = []
        self.rotation_curves: List[GalaxyRotationCurve] = []

    def add_cmb(self, multipole: int, cl: float,
                anisotropy: float = CMB_ANISOTROPY) -> CMBObservable:
        obs = CMBObservable(multipole_l=multipole, power_spectrum_cl=cl,
                            anisotropy_level=anisotropy)
        self.cmb_data.append(obs)
        return obs

    def add_rotation_point(self, r: float, v_obs: float,
                           v_newton: float) -> GalaxyRotationCurve:
        pt = GalaxyRotationCurve(radius_kpc=r, velocity_obs_km_s=v_obs,
                                 velocity_newton_km_s=v_newton)
        self.rotation_curves.append(pt)
        return pt

    def rotation_curve_analysis(self) -> Dict[str, object]:
        """Analyse all rotation curve points for entropy-correction need."""
        needs_correction = [p for p in self.rotation_curves
                            if p.requires_entropy_correction()]
        return {
            "total_points": len(self.rotation_curves),
            "needing_correction": len(needs_correction),
            "fraction": (len(needs_correction) / len(self.rotation_curves)
                         if self.rotation_curves else 0.0),
            "max_excess_ratio": (max(p.excess_ratio() for p in self.rotation_curves)
                                 if self.rotation_curves else 0.0),
        }

    def cmb_consistency(self, predicted_anisotropy: float) -> Dict[str, object]:
        """Check CMB data consistency with an EFC prediction."""
        results = []
        for obs in self.cmb_data:
            results.append({
                "multipole": obs.multipole_l,
                "consistent": obs.is_consistent_with_efc(predicted_anisotropy),
            })
        all_ok = all(r["consistent"] for r in results) if results else True
        return {"checks": results, "all_consistent": all_ok}

    def summary(self) -> str:
        lines = [
            "EFC: Observational Evidence for Entropy in Cosmic Evolution",
            "=" * 60,
            f"CMB data points:        {len(self.cmb_data)}",
            f"Structure metrics:      {len(self.structure_data)}",
            f"Rotation-curve points:  {len(self.rotation_curves)}",
        ]
        return "\n".join(lines)
