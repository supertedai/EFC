"""
EFC -- Integrated Hypothesis: Time and Entropy

Implements the hypothesis that time emerges from entropy gradients and
energy-flow directionality within the EFC framework.  Covers temporal
ordering, causality, and the arrow of time.

Author: Morten Magnusson, ORCID 0009-0002-4860-5095
License: CC-BY-4.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import math


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BOLTZMANN_K: float = 1.380649e-23   # J/K


@dataclass
class EntropyState:
    """Snapshot of local entropy at a given moment."""
    entropy: float          # J/K
    temperature: float      # K
    time_label: float = 0.0 # coordinate time

    def entropy_density(self, volume: float) -> float:
        """Entropy per unit volume."""
        if volume <= 0:
            return 0.0
        return self.entropy / volume


@dataclass
class TemporalGradient:
    """
    Entropy gradient that defines the local arrow of time.

    In EFC, the direction of increasing entropy IS the direction
    of time.  The magnitude of the gradient sets the local 'tick rate'.
    """
    dS_dt: float = 1.0          # entropy change rate (J K^-1 s^-1)
    grid_resistance: float = 0.01

    def arrow_of_time(self) -> int:
        """Return +1 for forward, -1 for reverse, 0 for equilibrium."""
        if self.dS_dt > 0:
            return 1
        elif self.dS_dt < 0:
            return -1
        return 0

    def effective_tick_rate(self) -> float:
        """
        Local tick rate: tau_dot = |dS/dt| / (1 + R).

        Higher entropy production -> faster local time.
        Grid resistance slows it.
        """
        return abs(self.dS_dt) / (1.0 + self.grid_resistance)

    def time_dilation_factor(self, reference_rate: float) -> float:
        """
        Ratio of local tick rate to a reference rate.

        Values < 1 indicate local time runs slower (high-resistance region).
        """
        if reference_rate <= 0:
            return 0.0
        return self.effective_tick_rate() / reference_rate


class CausalChain:
    """
    A chain of entropy states that defines a causal sequence.

    Causality in EFC is the requirement that entropy never decreases
    along a connected flow path.
    """

    def __init__(self):
        self.states: List[EntropyState] = []

    def add_state(self, state: EntropyState) -> None:
        """Append a state to the causal chain."""
        self.states.append(state)

    def is_causal(self) -> bool:
        """Check that entropy is monotonically non-decreasing."""
        for i in range(1, len(self.states)):
            if self.states[i].entropy < self.states[i - 1].entropy:
                return False
        return True

    def total_entropy_change(self) -> float:
        """Net entropy change from first to last state."""
        if len(self.states) < 2:
            return 0.0
        return self.states[-1].entropy - self.states[0].entropy

    def average_rate(self) -> float:
        """Average dS/dt across the chain."""
        if len(self.states) < 2:
            return 0.0
        dt = self.states[-1].time_label - self.states[0].time_label
        if dt <= 0:
            return 0.0
        return self.total_entropy_change() / dt

    def causality_violations(self) -> List[int]:
        """Return indices where entropy decreases (violations)."""
        violations = []
        for i in range(1, len(self.states)):
            if self.states[i].entropy < self.states[i - 1].entropy:
                violations.append(i)
        return violations


class TimeEntropyModel:
    """
    Top-level model linking time emergence to entropy dynamics.

    Encapsulates the integrated hypothesis: time is not a background
    parameter but an emergent quantity driven by entropy gradients and
    modulated by grid resistance.
    """

    PARAMETERS = {
        "k_B": BOLTZMANN_K,
        "default_grid_resistance": 0.01,
        "arrow_condition": "dS/dt > 0",
        "tick_rate_eq": "tau_dot = |dS/dt| / (1 + R)",
    }

    def __init__(self, grid_resistance: float = 0.01):
        self.grid_resistance = grid_resistance
        self.chains: List[CausalChain] = []

    def create_chain(self) -> CausalChain:
        """Create and register a new causal chain."""
        chain = CausalChain()
        self.chains.append(chain)
        return chain

    def temporal_gradient(self, dS_dt: float) -> TemporalGradient:
        """Build a temporal gradient with the model's grid resistance."""
        return TemporalGradient(dS_dt=dS_dt, grid_resistance=self.grid_resistance)

    def simulate_time_emergence(
        self, s_initial: float, ds_dt: float, t_initial: float,
        n_steps: int, dt: float,
    ) -> List[Dict[str, float]]:
        """
        Simulate time emergence from entropy production.

        Returns a list of state dicts with emergent tick rate and
        accumulated proper time.
        """
        results: List[Dict[str, float]] = []
        s = s_initial
        tau = 0.0   # proper time
        tg = self.temporal_gradient(ds_dt)

        for i in range(n_steps):
            t = t_initial + i * dt
            tick = tg.effective_tick_rate()
            tau += tick * dt
            s += ds_dt * dt
            results.append({
                "step": i,
                "coordinate_time": t,
                "entropy": s,
                "tick_rate": tick,
                "proper_time": tau,
                "arrow": tg.arrow_of_time(),
            })
        return results

    def verify_all_chains(self) -> Dict[str, object]:
        """Verify causality in all registered chains."""
        return {
            f"chain_{i}": {
                "causal": c.is_causal(),
                "length": len(c.states),
                "delta_S": c.total_entropy_change(),
                "violations": c.causality_violations(),
            }
            for i, c in enumerate(self.chains)
        }

    def summary(self) -> str:
        """Human-readable summary."""
        lines = [
            "EFC: Integrated Hypothesis -- Time and Entropy",
            "=" * 50,
            f"Grid resistance:  {self.grid_resistance}",
            f"Tick-rate eq:     tau_dot = |dS/dt| / (1 + R)",
            f"Arrow condition:  dS/dt > 0",
            f"Causal chains:    {len(self.chains)}",
        ]
        return "\n".join(lines)
