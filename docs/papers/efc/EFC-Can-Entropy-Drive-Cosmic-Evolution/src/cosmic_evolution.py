"""Entropy-driven cosmic evolution module.

Models whether entropy gradients, entropy flow, and thermodynamic
imbalances alone can generate and sustain cosmic structure and evolution.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import math


@dataclass
class EntropyGradient:
    """An entropy gradient that drives structure formation."""

    label: str
    magnitude: float  # J/(K m^3) -- entropy density gradient
    scale_m: float  # characteristic spatial scale (metres)
    drives_structure: bool = True

    @property
    def entropy_flux(self) -> float:
        """Estimate entropy flux ~ magnitude * scale (J K^-1 m^-2 s^-1)."""
        return self.magnitude * self.scale_m

    def summary(self) -> str:
        status = "structure-forming" if self.drives_structure else "dissipative"
        return (f"{self.label}: |nabla S|={self.magnitude:.2e} J/(K m^3), "
                f"scale={self.scale_m:.2e} m [{status}]")


@dataclass
class CosmicEpoch:
    """A cosmic epoch characterised by its dominant entropy processes."""

    name: str
    time_after_bb_s: float  # seconds after Big Bang
    entropy_density: float  # J/(K m^3)
    dominant_process: str
    structure_formed: List[str] = field(default_factory=list)

    @property
    def time_gyr(self) -> float:
        """Time in gigayears."""
        return self.time_after_bb_s / (3.156e16)

    def summary(self) -> str:
        lines = [
            f"Epoch: {self.name} (t={self.time_gyr:.3f} Gyr)",
            f"  Entropy density: {self.entropy_density:.2e} J/(K m^3)",
            f"  Dominant process: {self.dominant_process}",
        ]
        if self.structure_formed:
            lines.append(f"  Structures: {', '.join(self.structure_formed)}")
        return "\n".join(lines)


class EntropicEvolution:
    """Access class for entropy-driven cosmic evolution concepts.

    Tracks how entropy gradients drive structure across cosmic epochs.
    """

    def __init__(self) -> None:
        self.epochs: List[CosmicEpoch] = []
        self.gradients: List[EntropyGradient] = []
        self._init_defaults()

    def _init_defaults(self) -> None:
        self.epochs = [
            CosmicEpoch("Radiation era", 1.0, 1e12, "Photon entropy dominance",
                        []),
            CosmicEpoch("Recombination", 1.2e13, 1e8,
                        "Entropy gradient freeze-out",
                        ["Density perturbations"]),
            CosmicEpoch("Structure formation", 1e16, 1e4,
                        "Gravitational entropy channelling",
                        ["Galaxy clusters", "Filaments"]),
            CosmicEpoch("Present", 4.35e17, 1e2,
                        "Stellar and black-hole entropy production",
                        ["Stars", "Galaxies", "Black holes"]),
        ]
        self.gradients = [
            EntropyGradient("Primordial", 1e10, 1e22, True),
            EntropyGradient("Cluster-scale", 1e4, 1e23, True),
            EntropyGradient("Void-filament boundary", 1e2, 1e24, True),
        ]

    def total_entropy_growth(self) -> float:
        """Ratio of present to initial entropy density."""
        if len(self.epochs) < 2:
            return 1.0
        return self.epochs[0].entropy_density / self.epochs[-1].entropy_density

    def summary(self) -> str:
        lines = ["Entropy-Driven Cosmic Evolution (EFC)",
                 f"  Epochs: {len(self.epochs)}",
                 f"  Entropy gradients: {len(self.gradients)}",
                 f"  Entropy growth factor: {self.total_entropy_growth():.2e}",
                 ""]
        for e in self.epochs:
            lines.append(e.summary())
            lines.append("")
        for g in self.gradients:
            lines.append(f"  {g.summary()}")
        return "\n".join(lines)
