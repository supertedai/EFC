"""
EFC -- Hypothesis: Universe as an Energy-Driven System

Implements core concepts, equations, and parameters for the hypothesis
that the universe is an energy-driven system governed by entropy gradients,
energy flow, and grid-level resistance fields.

Author: Morten Magnusson, ORCID 0009-0002-4860-5095
License: CC-BY-4.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import math


# ---------------------------------------------------------------------------
# Physical constants and EFC parameters
# ---------------------------------------------------------------------------

BOLTZMANN_K: float = 1.380649e-23          # J/K
SPEED_OF_LIGHT: float = 2.998e8            # m/s
PLANCK_CONSTANT: float = 6.626e-34         # J s
GRAVITATIONAL_G: float = 6.674e-11         # m^3 kg^-1 s^-2

# EFC-specific default parameters
DEFAULT_GRID_RESISTANCE: float = 0.01      # dimensionless grid damping
DEFAULT_ENTROPY_GRADIENT: float = 1.0e-5   # K/m baseline gradient
DEFAULT_ENERGY_FLUX: float = 1.0e10        # J m^-2 s^-1


@dataclass
class GridField:
    """
    Represents the EFC grid field that mediates resistance to energy flow.

    The grid field provides a substrate through which energy propagates,
    with local resistance modulating structure formation and dynamics.
    """
    resistance: float = DEFAULT_GRID_RESISTANCE
    dimension: int = 3
    label: str = "default"

    def damping_factor(self, energy_density: float) -> float:
        """Compute damping factor: D = R / (1 + R * rho_E)."""
        return self.resistance / (1.0 + self.resistance * energy_density)

    def effective_propagation_speed(self, base_speed: float = SPEED_OF_LIGHT) -> float:
        """Effective propagation speed through the grid: v_eff = c / (1 + R)."""
        return base_speed / (1.0 + self.resistance)

    def grid_energy_density(self, temperature: float) -> float:
        """Thermal energy density of the grid: rho = k_B * T * (1 + R)."""
        return BOLTZMANN_K * temperature * (1.0 + self.resistance)


@dataclass
class EntropyGradient:
    """
    Models entropy gradients that drive structure and dynamics.

    In the EFC framework, entropy gradients are the primary organisational
    force: energy flows from low-entropy to high-entropy regions, producing
    structure along the way.
    """
    gradient_magnitude: float = DEFAULT_ENTROPY_GRADIENT   # K/m
    direction: List[float] = field(default_factory=lambda: [1.0, 0.0, 0.0])

    def driving_force(self, temperature: float) -> float:
        """Thermodynamic driving force: F = T * |nabla S|."""
        return temperature * self.gradient_magnitude

    def entropy_production_rate(self, energy_flux: float,
                                temperature: float) -> float:
        """Local entropy production: sigma = J_E * |nabla S| / T."""
        if temperature <= 0:
            return 0.0
        return energy_flux * self.gradient_magnitude / temperature

    def normalize_direction(self) -> List[float]:
        """Return unit direction vector."""
        mag = math.sqrt(sum(d ** 2 for d in self.direction))
        if mag == 0:
            return self.direction
        return [d / mag for d in self.direction]


@dataclass
class EnergyFlow:
    """
    Core energy-flow dynamics in the EFC universe model.

    Energy flow is the fundamental driver: the universe evolves because
    energy continuously moves along entropy gradients, modulated by the
    grid field resistance.
    """
    flux: float = DEFAULT_ENERGY_FLUX          # J m^-2 s^-1
    entropy_gradient: EntropyGradient = field(default_factory=EntropyGradient)
    grid: GridField = field(default_factory=GridField)

    def net_flow_rate(self, temperature: float) -> float:
        """
        Net energy-flow rate accounting for grid damping.

        J_net = J_E * (1 - D(rho_E))
        """
        rho = self.grid.grid_energy_density(temperature)
        damping = self.grid.damping_factor(rho)
        return self.flux * (1.0 - damping)

    def structure_formation_potential(self, temperature: float) -> float:
        """
        Structure-formation potential: Phi = F_drive * (1 - D).

        Regions with high driving force and low damping are candidates
        for structure emergence.
        """
        f_drive = self.entropy_gradient.driving_force(temperature)
        rho = self.grid.grid_energy_density(temperature)
        damping = self.grid.damping_factor(rho)
        return f_drive * (1.0 - damping)

    def energy_budget(self, temperature: float, volume: float) -> Dict[str, float]:
        """
        Partition the energy budget for a given volume element.

        Returns kinetic, thermal, and grid-stored fractions.
        """
        rho = self.grid.grid_energy_density(temperature)
        total = rho * volume
        damping = self.grid.damping_factor(rho)
        kinetic = total * (1.0 - damping)
        grid_stored = total * damping
        thermal = BOLTZMANN_K * temperature * volume
        return {
            "total_energy_density": rho,
            "kinetic_fraction": kinetic,
            "grid_stored_fraction": grid_stored,
            "thermal_energy": thermal,
        }


class EnergyDrivenUniverse:
    """
    Top-level model of the universe as an energy-driven system.

    Combines grid field, entropy gradients, and energy flow into a
    single framework that tracks cosmic evolution through thermodynamic
    state changes.
    """

    PARAMETERS = {
        "grid_resistance": DEFAULT_GRID_RESISTANCE,
        "entropy_gradient": DEFAULT_ENTROPY_GRADIENT,
        "energy_flux": DEFAULT_ENERGY_FLUX,
        "k_B": BOLTZMANN_K,
        "c": SPEED_OF_LIGHT,
        "G": GRAVITATIONAL_G,
    }

    def __init__(
        self,
        grid_resistance: float = DEFAULT_GRID_RESISTANCE,
        entropy_gradient_mag: float = DEFAULT_ENTROPY_GRADIENT,
        energy_flux: float = DEFAULT_ENERGY_FLUX,
    ):
        self.grid = GridField(resistance=grid_resistance)
        self.entropy_grad = EntropyGradient(gradient_magnitude=entropy_gradient_mag)
        self.flow = EnergyFlow(
            flux=energy_flux,
            entropy_gradient=self.entropy_grad,
            grid=self.grid,
        )

    def evolve_step(self, temperature: float, dt: float) -> Dict[str, float]:
        """
        Single evolution step: compute flow rate, entropy production,
        and structure potential over interval dt.
        """
        j_net = self.flow.net_flow_rate(temperature)
        sigma = self.entropy_grad.entropy_production_rate(j_net, temperature)
        phi = self.flow.structure_formation_potential(temperature)
        return {
            "net_flow_rate": j_net,
            "entropy_production": sigma * dt,
            "structure_potential": phi,
            "dt": dt,
        }

    def cosmic_timeline(self, t_start: float, t_end: float,
                        n_steps: int, t_initial: float) -> List[Dict[str, float]]:
        """
        Simulate a simplified cosmic timeline returning state at each step.

        Temperature cools as T ~ T_initial / (1 + t/t_scale) where
        t_scale = t_end - t_start.
        """
        dt = (t_end - t_start) / n_steps
        t_scale = t_end - t_start
        timeline: List[Dict[str, float]] = []
        for i in range(n_steps):
            t = t_start + i * dt
            temp = t_initial / (1.0 + t / t_scale)
            state = self.evolve_step(temp, dt)
            state["time"] = t
            state["temperature"] = temp
            timeline.append(state)
        return timeline

    def summary(self) -> str:
        """Human-readable summary of the model."""
        lines = [
            "EFC: Universe as an Energy-Driven System",
            "=" * 50,
            f"Grid resistance:    {self.grid.resistance}",
            f"Entropy gradient:   {self.entropy_grad.gradient_magnitude} K/m",
            f"Energy flux:        {self.flow.flux:.3e} J m^-2 s^-1",
            f"Effective v_prop:   {self.grid.effective_propagation_speed():.3e} m/s",
        ]
        return "\n".join(lines)
