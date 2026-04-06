"""Bridging Scales: EFC and Free Energy Principle.

Classes for the key concepts linking variational free energy to
measurable energy-flow dynamics across entropy gradients.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import math


@dataclass
class MarkovBlanket:
    """Markov blanket reinterpreted as a physical energy-flow interface.

    In this framework, the blanket boundary is characterised by zero net
    flux or an extremal gradient condition on the energy-flow field Ef.
    """

    name: str
    internal_energy: float  # Joules
    boundary_flux: float = 0.0  # W/m^2, net flux across boundary
    gradient_magnitude: float = 0.0  # W/m^3

    @property
    def is_steady_state(self) -> bool:
        """True when the blanket is in a non-equilibrium steady state."""
        return abs(self.boundary_flux) < 1e-10

    def summary(self) -> str:
        lines = [
            f"Markov Blanket: {self.name}",
            f"  Internal energy: {self.internal_energy:.3e} J",
            f"  Boundary flux: {self.boundary_flux:.3e} W/m^2",
            f"  Gradient magnitude: {self.gradient_magnitude:.3e} W/m^3",
            f"  Steady state: {self.is_steady_state}",
        ]
        return "\n".join(lines)


@dataclass
class ResonanceParameter:
    """Empirically motivated resonance parameter (xi).

    Proposed as a stability threshold for self-organising structures.
    Explicitly non-universal by assumption -- varies across systems.
    """

    xi: float  # dimensionless
    system_label: str = "generic"
    description: str = "Stability threshold for self-organising structure"

    @property
    def is_stable(self) -> bool:
        """Structure is stable when xi > 1."""
        return self.xi > 1.0

    def summary(self) -> str:
        return (f"Resonance xi={self.xi:.4f} ({self.system_label}): "
                f"{'stable' if self.is_stable else 'unstable'}")


class BridgingFramework:
    """Main access class linking FEP variational free energy to EFC energy flow.

    Key equations from the paper:
      - Variational free energy F = E_q[ln q(s) - ln p(s, o)]
      - Blanket-integrated scalar Phi_B = integral of Ef . dA over blanket
      - Bridge condition: dF/dt ~ -alpha * Phi_B under NESS
    """

    def __init__(self, alpha: float = 1.0) -> None:
        self.alpha = alpha  # coupling constant
        self.blankets: List[MarkovBlanket] = []
        self.resonance_params: List[ResonanceParameter] = []

    def add_blanket(self, blanket: MarkovBlanket) -> None:
        self.blankets.append(blanket)

    def add_resonance(self, rp: ResonanceParameter) -> None:
        self.resonance_params.append(rp)

    def blanket_integrated_scalar(self, blanket: MarkovBlanket,
                                   area: float = 1.0) -> float:
        """Compute Phi_B = Ef_boundary * A (simplified scalar integral)."""
        return blanket.boundary_flux * area

    def variational_free_energy_rate(self, phi_b: float) -> float:
        """Estimate dF/dt ~ -alpha * Phi_B under NESS conditions."""
        return -self.alpha * phi_b

    def effective_temperature(self, energy: float,
                               entropy: float) -> Optional[float]:
        """T_eff via fluctuation-dissipation: T = dE/dS."""
        if entropy == 0:
            return None
        return energy / entropy

    def summary(self) -> str:
        lines = [
            "Bridging Framework: EFC <-> FEP",
            f"  Coupling alpha = {self.alpha}",
            f"  Blankets registered: {len(self.blankets)}",
            f"  Resonance parameters: {len(self.resonance_params)}",
        ]
        for b in self.blankets:
            lines.append(f"  {b.summary()}")
        for r in self.resonance_params:
            lines.append(f"  {r.summary()}")
        return "\n".join(lines)
