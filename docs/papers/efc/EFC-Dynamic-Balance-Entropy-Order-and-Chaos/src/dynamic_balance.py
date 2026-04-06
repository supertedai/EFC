"""Dynamic Balance: Entropy, Order, and Chaos module.

Models the co-evolution of entropy flow, structure (order), and
disorder (chaos) in dynamically balanced systems.  Describes
transition mechanisms between ordered states, chaotic zones, and
entropic equilibria within EFC.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import math


@dataclass
class SystemState:
    """A thermodynamic state characterised by its order/chaos balance.

    order_param: 0 = fully chaotic, 1 = fully ordered
    entropy_rate: rate of entropy production (J K^-1 s^-1)
    """

    label: str
    order_param: float  # [0, 1]
    entropy_rate: float  # J K^-1 s^-1
    energy_flow: float  # W

    @property
    def regime(self) -> str:
        if self.order_param > 0.7:
            return "ordered"
        elif self.order_param < 0.3:
            return "chaotic"
        return "transitional"

    @property
    def balance_index(self) -> float:
        """Dynamic balance index: B = order * (1 - order) * Ef / dS.

        Peaks when the system is in the transitional regime with
        high energy flow relative to entropy production.
        """
        if self.entropy_rate == 0:
            return float("inf")
        return (self.order_param * (1 - self.order_param)
                * self.energy_flow / self.entropy_rate)

    def summary(self) -> str:
        return (f"{self.label}: order={self.order_param:.2f} [{self.regime}], "
                f"dS/dt={self.entropy_rate:.2e} J/(K s), "
                f"Ef={self.energy_flow:.2e} W, "
                f"B={self.balance_index:.3f}")


@dataclass
class PhaseTransition:
    """A transition between two system states."""

    from_state: str
    to_state: str
    trigger: str
    critical_order_param: float
    description: str = ""

    def summary(self) -> str:
        return (f"Transition {self.from_state} -> {self.to_state} "
                f"at order={self.critical_order_param:.2f}: {self.trigger}")


class DynamicBalance:
    """Access class for the dynamic balance between entropy, order, and chaos.

    Provides methods for computing balance indices and modelling transitions.
    """

    def __init__(self) -> None:
        self.states: List[SystemState] = []
        self.transitions: List[PhaseTransition] = []
        self._init_defaults()

    def _init_defaults(self) -> None:
        self.states = [
            SystemState("Crystal lattice", 0.95, 1e-5, 1e2),
            SystemState("Living cell", 0.55, 1e-2, 1e0),
            SystemState("Turbulent plasma", 0.15, 1e4, 1e8),
            SystemState("Equilibrium gas", 0.02, 1e-8, 1e-4),
        ]
        self.transitions = [
            PhaseTransition("ordered", "transitional", "Entropy injection",
                            0.7, "Energy flow exceeds structural binding"),
            PhaseTransition("transitional", "chaotic", "Cascade instability",
                            0.3, "Positive feedback in entropy production"),
            PhaseTransition("chaotic", "ordered", "Dissipative condensation",
                            0.3, "Entropy export enables re-ordering"),
        ]

    def most_balanced(self) -> Optional[SystemState]:
        """Return the state closest to peak dynamic balance."""
        if not self.states:
            return None
        return max(self.states, key=lambda s: s.balance_index
                   if math.isfinite(s.balance_index) else -1)

    def summary(self) -> str:
        lines = ["Dynamic Balance: Entropy, Order, and Chaos (EFC)",
                 f"  States: {len(self.states)}",
                 f"  Transitions: {len(self.transitions)}", ""]
        for s in self.states:
            lines.append(f"  {s.summary()}")
        lines.append("")
        for t in self.transitions:
            lines.append(f"  {t.summary()}")
        mb = self.most_balanced()
        if mb:
            lines.append(f"\n  Most balanced state: {mb.label} (B={mb.balance_index:.3f})")
        return "\n".join(lines)
