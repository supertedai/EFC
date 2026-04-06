"""
EFC -- The Thermodynamic Bridge Between GR and QFT
====================================================
Models the thermodynamic layer that connects General Relativity
(curvature) with Quantum Field Theory (quantised excitations)
through entropy gradients and energy flow.

Key relations:
  GR side  : G_mu_nu ~ 8 pi G / c^4  T_mu_nu   (Einstein)
  QFT side : excitation energy E_n = n * hbar * omega
  Bridge   : S_bridge = S_GR + S_QFT, mediated by energy flow J

Author : Morten Magnusson
ORCID  : 0009-0002-4860-5095
License: CC-BY-4.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List

# Constants
HBAR = 1.0546e-34   # J s
K_B = 1.3806e-23    # J/K
G_NEWTON = 6.674e-11  # m^3 kg^-1 s^-2
C_LIGHT = 299792458.0  # m/s


@dataclass
class GRSector:
    """General Relativity sector properties.

    Parameters
    ----------
    curvature_R : float
        Ricci scalar curvature (m^-2).
    energy_density : float
        Local energy density (J m^-3).
    entropy_density_GR : float
        GR-sector entropy density (J K^-1 m^-3).
    """

    curvature_R: float
    energy_density: float
    entropy_density_GR: float = 0.0

    @property
    def einstein_source(self) -> float:
        """8 pi G / c^4 * energy_density  (m^-2)."""
        return 8.0 * math.pi * G_NEWTON / C_LIGHT ** 4 * self.energy_density

    @property
    def beckenstein_bound_proxy(self) -> float:
        """Proxy for Bekenstein-type entropy bound: S ~ E / T.
        Uses T ~ hbar c / k_B as Unruh-scale temperature for unit acceleration."""
        T_unruh = HBAR * C_LIGHT / K_B  # ~2.4e-11 K (for a~1 m/s^2)
        if T_unruh == 0:
            return 0.0
        return self.energy_density / T_unruh


@dataclass
class QFTSector:
    """Quantum Field Theory sector properties.

    Parameters
    ----------
    omega : float
        Angular frequency of the dominant mode (rad/s).
    occupation_n : float
        Mean occupation number.
    entropy_density_QFT : float
        QFT-sector entropy density (J K^-1 m^-3).
    """

    omega: float
    occupation_n: float = 1.0
    entropy_density_QFT: float = 0.0

    @property
    def excitation_energy(self) -> float:
        """E_n = n * hbar * omega  (J)."""
        return self.occupation_n * HBAR * self.omega

    @property
    def thermal_wavelength(self) -> float:
        """lambda = 2 pi c / omega (m)."""
        if self.omega <= 0:
            return float("inf")
        return 2.0 * math.pi * C_LIGHT / self.omega


@dataclass
class ThermodynamicBridge:
    """The bridge connecting GR and QFT sectors via entropy flow.

    Parameters
    ----------
    gr : GRSector
    qft : QFTSector
    J_bridge : float
        Energy-flow magnitude across the bridge (W m^-2).
    R_grid : float
        Grid resistance at the bridge.
    """

    gr: GRSector
    qft: QFTSector
    J_bridge: float = 1.0
    R_grid: float = 1.0

    @property
    def total_entropy_density(self) -> float:
        """S_bridge = S_GR + S_QFT."""
        return self.gr.entropy_density_GR + self.qft.entropy_density_QFT

    @property
    def bridge_flux(self) -> float:
        """Phi_bridge = S_total * J / R_grid."""
        return self.total_entropy_density * self.J_bridge / max(self.R_grid, 1e-30)

    @property
    def coupling_ratio(self) -> float:
        """Ratio of GR to QFT entropy density."""
        if self.qft.entropy_density_QFT == 0:
            return float("inf")
        return self.gr.entropy_density_GR / self.qft.entropy_density_QFT

    def energy_balance(self) -> dict:
        return {
            "GR_einstein_source": self.gr.einstein_source,
            "QFT_excitation_energy": self.qft.excitation_energy,
            "bridge_flux": self.bridge_flux,
            "coupling_ratio": self.coupling_ratio,
        }


@dataclass
class BridgeAnalyzer:
    """Analyze multiple bridge configurations."""

    bridges: List[ThermodynamicBridge] = field(default_factory=list)

    def mean_coupling_ratio(self) -> float:
        ratios = [b.coupling_ratio for b in self.bridges if math.isfinite(b.coupling_ratio)]
        if not ratios:
            return 0.0
        return sum(ratios) / len(ratios)

    def total_bridge_flux(self) -> float:
        return sum(b.bridge_flux for b in self.bridges)

    def summary(self) -> dict:
        return {
            "n_bridges": len(self.bridges),
            "mean_coupling_ratio": self.mean_coupling_ratio(),
            "total_bridge_flux": self.total_bridge_flux(),
        }
