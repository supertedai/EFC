"""
EFC -- Observational Evidence for Energy Flow
==============================================
Classes for modelling observational signatures of energy flow in galaxies,
clusters, CMB radiation, and anisotropic large-scale structure.

Author : Morten Magnusson
ORCID  : 0009-0002-4860-5095
License: CC-BY-4.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------------------------
# Core data classes
# ---------------------------------------------------------------------------

@dataclass
class EnergyFlowSignature:
    """A single observational signature of energy flow.

    Parameters
    ----------
    name : str
        Identifier for the signature (e.g. galaxy name, survey ID).
    energy_flux : float
        Observed energy flux in W m^-2.
    entropy_gradient : float
        Estimated entropy gradient in kpc^-1.
    redshift : float
        Cosmological redshift of the source.
    """

    name: str
    energy_flux: float
    entropy_gradient: float
    redshift: float = 0.0

    @property
    def luminosity_distance(self) -> float:
        """Simplified luminosity distance (Mpc) using Hubble law d = cz/H0."""
        c_km_s = 299792.458
        H0 = 70.0  # km/s/Mpc
        if self.redshift <= 0:
            return 0.0
        return c_km_s * self.redshift / H0

    @property
    def luminosity(self) -> float:
        """Estimated luminosity (W) from flux and luminosity distance."""
        d_mpc = self.luminosity_distance
        if d_mpc <= 0:
            return 0.0
        d_m = d_mpc * 3.0857e22  # Mpc -> metres
        return 4.0 * math.pi * d_m ** 2 * self.energy_flux


@dataclass
class CMBAnisotropy:
    """CMB temperature anisotropy linked to energy-flow dynamics.

    Parameters
    ----------
    multipole_l : int
        Spherical-harmonic multipole number.
    delta_T : float
        Temperature fluctuation amplitude (micro-K).
    energy_flow_contribution : float
        Fraction of the signal attributed to energy flow (0-1).
    """

    multipole_l: int
    delta_T: float
    energy_flow_contribution: float = 0.0

    @property
    def angular_scale_deg(self) -> float:
        """Approximate angular scale in degrees for multipole *l*."""
        if self.multipole_l <= 0:
            return 180.0
        return 180.0 / self.multipole_l


@dataclass
class GalaxyClusterFlow:
    """Energy-flow properties of a galaxy cluster.

    Parameters
    ----------
    cluster_name : str
        Catalogue name of the cluster.
    mass_solar : float
        Total cluster mass in solar masses.
    temperature_keV : float
        Intra-cluster medium temperature in keV.
    entropy_index : float
        Normalised entropy index (0-1).
    bulk_velocity_km_s : float
        Bulk peculiar velocity in km/s.
    """

    cluster_name: str
    mass_solar: float
    temperature_keV: float
    entropy_index: float = 0.5
    bulk_velocity_km_s: float = 0.0

    @property
    def thermal_energy_erg(self) -> float:
        """Rough thermal energy of the ICM (erg)."""
        # E ~ (3/2) N k_B T; approximate N from mass
        n_particles = self.mass_solar * 1.989e33 / 1.673e-24  # protons
        kT_erg = self.temperature_keV * 1.602e-9  # keV -> erg
        return 1.5 * n_particles * kT_erg

    @property
    def flow_parameter(self) -> float:
        """Dimensionless flow parameter beta = v_bulk / c."""
        return self.bulk_velocity_km_s / 299792.458


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------

@dataclass
class ObservationalEvidenceAnalyzer:
    """Aggregate analyser for a collection of observational signatures."""

    signatures: List[EnergyFlowSignature] = field(default_factory=list)
    cmb_modes: List[CMBAnisotropy] = field(default_factory=list)
    clusters: List[GalaxyClusterFlow] = field(default_factory=list)

    # -- signatures ----------------------------------------------------------

    def mean_entropy_gradient(self) -> float:
        """Mean entropy gradient across all signatures."""
        if not self.signatures:
            return 0.0
        return sum(s.entropy_gradient for s in self.signatures) / len(self.signatures)

    def total_flux(self) -> float:
        """Total energy flux (W m^-2) from all signatures."""
        return sum(s.energy_flux for s in self.signatures)

    # -- CMB -----------------------------------------------------------------

    def mean_energy_flow_fraction(self) -> float:
        """Mean energy-flow contribution across CMB modes."""
        if not self.cmb_modes:
            return 0.0
        return sum(m.energy_flow_contribution for m in self.cmb_modes) / len(self.cmb_modes)

    # -- clusters ------------------------------------------------------------

    def mean_cluster_entropy(self) -> float:
        """Mean entropy index across clusters."""
        if not self.clusters:
            return 0.0
        return sum(c.entropy_index for c in self.clusters) / len(self.clusters)

    def summary(self) -> dict:
        """Return a summary dictionary of key statistics."""
        return {
            "n_signatures": len(self.signatures),
            "mean_entropy_gradient": self.mean_entropy_gradient(),
            "total_flux": self.total_flux(),
            "n_cmb_modes": len(self.cmb_modes),
            "mean_cmb_ef_fraction": self.mean_energy_flow_fraction(),
            "n_clusters": len(self.clusters),
            "mean_cluster_entropy": self.mean_cluster_entropy(),
        }
