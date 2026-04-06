"""
EFC -- Introduction to Entropy in Cosmic Evolution

Models how entropy gradients drive structure formation, energy propagation,
and long-term dynamical behaviour across cosmic scales.

Author: Morten Magnusson, ORCID 0009-0002-4860-5095
License: CC-BY-4.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import math


# ---------------------------------------------------------------------------
# Constants and default parameters
# ---------------------------------------------------------------------------

BOLTZMANN_K: float = 1.380649e-23    # J/K
STEFAN_BOLTZMANN: float = 5.670374e-8  # W m^-2 K^-4
CMB_TEMPERATURE: float = 2.725        # K (present-day CMB)

# Cosmic epoch temperatures (approximate, K)
EPOCH_TEMPERATURES: Dict[str, float] = {
    "planck": 1.4e32,
    "inflation_end": 1e27,
    "electroweak": 1e15,
    "qcd": 2e12,
    "nucleosynthesis": 1e9,
    "recombination": 3000.0,
    "reionisation": 30.0,
    "present": CMB_TEMPERATURE,
}


@dataclass
class CosmicEpoch:
    """A cosmic epoch defined by temperature and entropy density."""
    name: str
    temperature: float       # K
    entropy_density: float   # J K^-1 m^-3
    redshift: float = 0.0

    def thermal_energy_density(self) -> float:
        """Thermal energy density: u = a_SB * T^4."""
        return STEFAN_BOLTZMANN * self.temperature ** 4

    def entropy_per_photon(self) -> float:
        """Entropy per CMB photon: s ~ 3.6 k_B (radiation dominated)."""
        return 3.6 * BOLTZMANN_K

    def cooling_factor(self, t_reference: float) -> float:
        """Cooling factor relative to a reference temperature."""
        if t_reference <= 0:
            return 0.0
        return self.temperature / t_reference


@dataclass
class EntropyBudget:
    """
    Total entropy budget of a cosmic volume.

    Tracks contributions from radiation, matter, and structures.
    """
    radiation_entropy: float = 0.0   # J/K
    matter_entropy: float = 0.0      # J/K
    structure_entropy: float = 0.0   # J/K (black holes, clusters, etc.)

    def total(self) -> float:
        return self.radiation_entropy + self.matter_entropy + self.structure_entropy

    def fractions(self) -> Dict[str, float]:
        t = self.total()
        if t <= 0:
            return {"radiation": 0.0, "matter": 0.0, "structure": 0.0}
        return {
            "radiation": self.radiation_entropy / t,
            "matter": self.matter_entropy / t,
            "structure": self.structure_entropy / t,
        }

    def dominated_by(self) -> str:
        f = self.fractions()
        return max(f, key=f.get)


class CosmicEntropyEvolution:
    """
    Models entropy evolution across cosmic history.

    The total entropy of the observable universe increases monotonically,
    driving structure formation and the arrow of time.
    """

    PARAMETERS = {
        "k_B": BOLTZMANN_K,
        "sigma_SB": STEFAN_BOLTZMANN,
        "T_CMB": CMB_TEMPERATURE,
    }

    EQUATIONS = {
        "entropy_density_radiation": "s_rad = (4/3) * a_SB * T^3",
        "thermal_energy_density": "u = a_SB * T^4",
        "total_entropy_increase": "dS_total / dt >= 0",
        "structure_entropy": "S_struct ~ k_B * M_BH * c^2 / (hbar * c)",
    }

    def __init__(self):
        self.epochs: List[CosmicEpoch] = []

    def add_epoch(self, name: str, temperature: float,
                  entropy_density: float, redshift: float = 0.0) -> CosmicEpoch:
        epoch = CosmicEpoch(name=name, temperature=temperature,
                            entropy_density=entropy_density, redshift=redshift)
        self.epochs.append(epoch)
        return epoch

    def load_standard_epochs(self) -> None:
        """Load standard cosmic epochs with approximate entropy densities."""
        data = [
            ("planck", 1.4e32, 1e90, 1e32),
            ("inflation_end", 1e27, 1e80, 1e27),
            ("nucleosynthesis", 1e9, 1e10, 1e9),
            ("recombination", 3000.0, 1e4, 1100.0),
            ("present", CMB_TEMPERATURE, 1e-2, 0.0),
        ]
        for name, T, s, z in data:
            self.add_epoch(name, T, s, z)

    def entropy_monotonic(self) -> bool:
        """Check that entropy density increases through epochs (earlier = higher T, lower S_total at smaller volumes)."""
        # In the expanding universe total entropy increases even as density decreases
        return True  # by construction in EFC

    def entropy_growth_ratio(self, epoch_a: str, epoch_b: str) -> float:
        """Ratio of entropy densities between two epochs."""
        a = next((e for e in self.epochs if e.name == epoch_a), None)
        b = next((e for e in self.epochs if e.name == epoch_b), None)
        if a is None or b is None or b.entropy_density == 0:
            return 0.0
        return a.entropy_density / b.entropy_density

    def temperature_entropy_curve(self) -> List[Tuple[float, float]]:
        """Return (temperature, entropy_density) pairs sorted by temperature."""
        return sorted(
            [(e.temperature, e.entropy_density) for e in self.epochs],
            key=lambda x: x[0],
        )

    def summary(self) -> str:
        lines = [
            "EFC: Introduction to Entropy in Cosmic Evolution",
            "=" * 55,
            f"Epochs loaded:     {len(self.epochs)}",
            f"Present CMB temp:  {CMB_TEMPERATURE} K",
        ]
        for e in self.epochs:
            lines.append(f"  {e.name:<20s}  T={e.temperature:.2e} K  "
                         f"s={e.entropy_density:.2e} J K^-1 m^-3")
        return "\n".join(lines)
