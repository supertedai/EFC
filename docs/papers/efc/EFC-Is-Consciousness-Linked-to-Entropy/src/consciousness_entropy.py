"""
EFC -- Is Consciousness Linked to Entropy?

Models the hypothesis that consciousness emerges from entropy gradients
and information flow, exploring the relationship between entropy,
structure, informational asymmetry, and cognitive processes.

Author: Morten Magnusson, ORCID 0009-0002-4860-5095
License: CC-BY-4.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import math


# ---------------------------------------------------------------------------
# Constants and parameters
# ---------------------------------------------------------------------------

BOLTZMANN_K: float = 1.380649e-23   # J/K

# Consciousness-entropy coupling defaults
DEFAULT_PHI_THRESHOLD: float = 0.5    # integrated information threshold
DEFAULT_ENTROPY_RATE: float = 1.0     # J K^-1 s^-1
DEFAULT_INFO_CAPACITY: float = 100.0  # bits


@dataclass
class InformationState:
    """
    Information-theoretic state of a cognitive subsystem.

    Consciousness in EFC is linked to the rate at which a system
    processes entropy gradients into structured information.
    """
    entropy_rate: float = DEFAULT_ENTROPY_RATE      # J K^-1 s^-1
    information_capacity: float = DEFAULT_INFO_CAPACITY  # bits
    integration_level: float = 0.0    # Phi (integrated information)

    def entropy_to_info_ratio(self) -> float:
        """Ratio of entropy production to information capacity."""
        if self.information_capacity <= 0:
            return 0.0
        return self.entropy_rate / self.information_capacity

    def is_above_threshold(self, threshold: float = DEFAULT_PHI_THRESHOLD) -> bool:
        """Check if integration level exceeds consciousness threshold."""
        return self.integration_level >= threshold

    def cognitive_temperature(self) -> float:
        """
        Effective cognitive temperature: T_cog = S_rate / I_cap.

        Analogous to thermodynamic temperature but for information processing.
        """
        return self.entropy_to_info_ratio()


@dataclass
class EntropyConsciousnessLink:
    """
    Models the link between entropy gradients and consciousness emergence.

    The hypothesis: consciousness arises when a system maintains a
    sufficiently steep internal entropy gradient while sustaining
    high informational integration.
    """
    internal_entropy_gradient: float = 0.0   # internal dS/dx
    external_entropy_gradient: float = 0.0   # environmental dS/dx
    phi: float = 0.0                         # integrated information

    def gradient_asymmetry(self) -> float:
        """
        Asymmetry between internal and external entropy gradients.

        Consciousness requires the internal gradient to exceed the external.
        """
        total = abs(self.internal_entropy_gradient) + abs(self.external_entropy_gradient)
        if total == 0:
            return 0.0
        return (self.internal_entropy_gradient - self.external_entropy_gradient) / total

    def emergence_score(self) -> float:
        """
        Consciousness emergence score: E = Phi * asymmetry.

        Higher score indicates more favourable conditions for consciousness.
        """
        asym = self.gradient_asymmetry()
        return self.phi * max(asym, 0.0)

    def is_conscious_candidate(self, phi_min: float = DEFAULT_PHI_THRESHOLD) -> bool:
        """
        Determine if the system meets minimum conditions for consciousness.

        Requires: Phi >= threshold AND positive gradient asymmetry.
        """
        return self.phi >= phi_min and self.gradient_asymmetry() > 0


class ConsciousnessEntropyModel:
    """
    Top-level model linking consciousness to entropy within EFC.

    Combines entropy gradients, information integration, and
    cognitive temperature to explore conscious emergence conditions.
    """

    PARAMETERS = {
        "k_B": BOLTZMANN_K,
        "phi_threshold": DEFAULT_PHI_THRESHOLD,
        "default_entropy_rate": DEFAULT_ENTROPY_RATE,
        "default_info_capacity": DEFAULT_INFO_CAPACITY,
    }

    EQUATIONS = {
        "cognitive_temperature": "T_cog = S_rate / I_cap",
        "gradient_asymmetry": "A = (grad_int - grad_ext) / (|grad_int| + |grad_ext|)",
        "emergence_score": "E = Phi * max(A, 0)",
        "consciousness_condition": "Phi >= Phi_min AND A > 0",
    }

    def __init__(self, phi_threshold: float = DEFAULT_PHI_THRESHOLD):
        self.phi_threshold = phi_threshold
        self.systems: List[EntropyConsciousnessLink] = []

    def add_system(self, internal_grad: float, external_grad: float,
                   phi: float) -> EntropyConsciousnessLink:
        link = EntropyConsciousnessLink(
            internal_entropy_gradient=internal_grad,
            external_entropy_gradient=external_grad,
            phi=phi,
        )
        self.systems.append(link)
        return link

    def evaluate_all(self) -> List[Dict[str, object]]:
        """Evaluate all registered systems for consciousness candidacy."""
        results = []
        for i, s in enumerate(self.systems):
            results.append({
                "index": i,
                "phi": s.phi,
                "asymmetry": round(s.gradient_asymmetry(), 4),
                "emergence_score": round(s.emergence_score(), 4),
                "conscious_candidate": s.is_conscious_candidate(self.phi_threshold),
            })
        return results

    def scan_threshold(self, phi_values: List[float],
                       internal_grad: float,
                       external_grad: float) -> List[Dict[str, object]]:
        """
        Scan across Phi values to find the consciousness transition.
        """
        results = []
        for phi in phi_values:
            link = EntropyConsciousnessLink(
                internal_entropy_gradient=internal_grad,
                external_entropy_gradient=external_grad,
                phi=phi,
            )
            results.append({
                "phi": phi,
                "emergence_score": round(link.emergence_score(), 4),
                "candidate": link.is_conscious_candidate(self.phi_threshold),
            })
        return results

    def summary(self) -> str:
        lines = [
            "EFC: Is Consciousness Linked to Entropy?",
            "=" * 50,
            f"Phi threshold:     {self.phi_threshold}",
            f"Systems tracked:   {len(self.systems)}",
        ]
        return "\n".join(lines)
