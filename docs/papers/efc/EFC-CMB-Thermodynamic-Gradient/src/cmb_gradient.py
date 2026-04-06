"""CMB Thermodynamic Gradient module.

Classes modelling the thermodynamic-gradient interpretation of the CMB
within Energy-Flow Cosmology.  The observed CMB pattern is explained
via entropy flow, energy gradients, and grid-level structure rather
than dark matter or dark energy.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import math


@dataclass
class CMBAnisotropy:
    """A single CMB anisotropy mode described by EFC entropy gradients."""

    multipole_l: int
    amplitude_uK: float  # micro-Kelvin
    entropy_gradient: float  # W/m^3/K — local entropy gradient contribution

    def summary(self) -> str:
        return (f"l={self.multipole_l}: amplitude={self.amplitude_uK:.2f} uK, "
                f"dS/dx={self.entropy_gradient:.3e} W/m^3/K")


@dataclass
class ThermodynamicGrid:
    """Grid-level structure that shapes the CMB pattern.

    In EFC the background grid carries resistance to energy flow,
    producing anisotropy without requiring dark matter.
    """

    grid_scale_m: float  # characteristic scale of grid cells (metres)
    resistance: float  # dimensionless resistance coefficient
    temperature_K: float = 2.725  # CMB mean temperature

    @property
    def energy_density(self) -> float:
        """Stefan-Boltzmann energy density u = a T^4 (J/m^3)."""
        a = 7.5657e-16  # radiation constant J m^-3 K^-4
        return a * self.temperature_K ** 4

    def summary(self) -> str:
        return (f"Grid: scale={self.grid_scale_m:.2e} m, "
                f"resistance={self.resistance:.4f}, "
                f"T={self.temperature_K:.3f} K, "
                f"u={self.energy_density:.3e} J/m^3")


class CMBGradient:
    """Main class for the CMB thermodynamic-gradient analysis.

    Provides access to anisotropy modes, grid properties, and key
    parameters from the paper.
    """

    def __init__(self, mean_temperature: float = 2.725) -> None:
        self.mean_temperature = mean_temperature  # Kelvin
        self.anisotropies: List[CMBAnisotropy] = []
        self.grid: Optional[ThermodynamicGrid] = None
        self._init_defaults()

    def _init_defaults(self) -> None:
        """Populate representative modes and grid from paper values."""
        self.grid = ThermodynamicGrid(
            grid_scale_m=1e24,
            resistance=0.01,
            temperature_K=self.mean_temperature,
        )
        # Representative low-l modes
        for l_val, amp, grad in [
            (2, 25.0, 1e-30), (10, 40.0, 3e-30),
            (100, 70.0, 8e-30), (200, 72.0, 9e-30),
        ]:
            self.anisotropies.append(
                CMBAnisotropy(multipole_l=l_val, amplitude_uK=amp,
                              entropy_gradient=grad)
            )

    def temperature_fluctuation(self, delta_S: float,
                                 grid_resistance: Optional[float] = None) -> float:
        """Estimate delta-T/T from an entropy gradient perturbation.

        delta_T/T ~ R * delta_S / S_background
        """
        R = grid_resistance if grid_resistance is not None else (
            self.grid.resistance if self.grid else 0.01)
        s_bg = 1e-28  # representative background entropy density
        return R * delta_S / s_bg

    def total_rms_anisotropy(self) -> float:
        """RMS of all registered anisotropy amplitudes (uK)."""
        if not self.anisotropies:
            return 0.0
        return math.sqrt(sum(a.amplitude_uK ** 2 for a in self.anisotropies)
                         / len(self.anisotropies))

    def summary(self) -> str:
        lines = [
            "CMB Thermodynamic Gradient (EFC)",
            f"  Mean temperature: {self.mean_temperature} K",
            f"  Anisotropy modes: {len(self.anisotropies)}",
            f"  RMS anisotropy:   {self.total_rms_anisotropy():.2f} uK",
        ]
        if self.grid:
            lines.append(f"  {self.grid.summary()}")
        for a in self.anisotropies:
            lines.append(f"  {a.summary()}")
        return "\n".join(lines)
