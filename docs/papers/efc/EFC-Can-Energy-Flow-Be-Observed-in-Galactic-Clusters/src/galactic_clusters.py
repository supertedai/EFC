"""Galactic Clusters energy-flow observation module.

Classes modelling observable signatures of the energy-flow field (Ef)
in galaxy cluster dynamics, temperature gradients, entropy distributions,
and gravitational lensing profiles.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class EfSignature:
    """An observable signature of the energy-flow field in a cluster."""

    observable: str  # e.g. "X-ray temperature gradient"
    method: str  # e.g. "Chandra X-ray spectroscopy"
    predicted_signal: str  # qualitative or quantitative prediction
    units: str = ""
    magnitude: Optional[float] = None  # predicted magnitude if quantitative

    def summary(self) -> str:
        mag = f" ({self.magnitude} {self.units})" if self.magnitude else ""
        return f"{self.observable} [{self.method}]: {self.predicted_signal}{mag}"


@dataclass
class GalaxyCluster:
    """A galaxy cluster modelled with EFC energy-flow properties."""

    name: str
    mass_solar: float  # total mass in solar masses
    temperature_keV: float  # X-ray temperature in keV
    redshift: float
    entropy_profile_keV_cm2: List[float] = field(default_factory=list)
    ef_magnitude_W_m2: float = 0.0  # characteristic Ef at virial radius

    @property
    def temperature_K(self) -> float:
        """Convert keV to Kelvin (1 keV ~ 1.16e7 K)."""
        return self.temperature_keV * 1.16e7

    def lensing_deflection_arcsec(self, impact_param_kpc: float) -> float:
        """Estimate gravitational lensing deflection (simplified).

        In EFC, lensing is produced by the Ef gradient rather than
        spacetime curvature from mass alone.
        theta ~ 4 G M / (c^2 b)  with Ef correction
        """
        G = 6.674e-11
        c = 3e8
        M_kg = self.mass_solar * 1.989e30
        b_m = impact_param_kpc * 3.086e19  # kpc to metres
        if b_m == 0:
            return float("inf")
        theta_rad = 4 * G * M_kg / (c ** 2 * b_m)
        # Ef correction factor (1 + ef / ef_ref)
        ef_ref = 1e-10  # reference Ef scale
        correction = 1.0 + self.ef_magnitude_W_m2 / ef_ref
        return theta_rad * correction * 206265  # radians to arcsec

    def summary(self) -> str:
        lines = [
            f"Cluster: {self.name}",
            f"  Mass: {self.mass_solar:.2e} M_sun",
            f"  T_X: {self.temperature_keV} keV ({self.temperature_K:.2e} K)",
            f"  Redshift: {self.redshift}",
            f"  Ef magnitude: {self.ef_magnitude_W_m2:.2e} W/m^2",
            f"  Entropy profile points: {len(self.entropy_profile_keV_cm2)}",
        ]
        return "\n".join(lines)


class ClusterObservatory:
    """Manages clusters and their predicted Ef signatures."""

    def __init__(self) -> None:
        self.clusters: Dict[str, GalaxyCluster] = {}
        self.signatures: List[EfSignature] = []
        self._init_defaults()

    def _init_defaults(self) -> None:
        self.signatures = [
            EfSignature("X-ray temperature gradient", "Chandra spectroscopy",
                        "Steeper gradient in cluster outskirts than LCDM predicts"),
            EfSignature("Entropy floor", "Suzaku / eROSITA",
                        "Entropy excess at r > r500 from Ef injection"),
            EfSignature("Lensing-mass discrepancy", "Weak lensing surveys",
                        "Ef-corrected lensing mass lower than dynamical mass"),
            EfSignature("ICM bulk flow", "SZ kinetic effect",
                        "Residual bulk flow aligned with large-scale Ef gradient"),
        ]

    def add_cluster(self, cluster: GalaxyCluster) -> None:
        self.clusters[cluster.name] = cluster

    def summary(self) -> str:
        lines = ["Cluster Observatory (EFC)", f"  Clusters: {len(self.clusters)}",
                 f"  Predicted signatures: {len(self.signatures)}"]
        for s in self.signatures:
            lines.append(f"  - {s.summary()}")
        for c in self.clusters.values():
            lines.append(f"\n{c.summary()}")
        return "\n".join(lines)
