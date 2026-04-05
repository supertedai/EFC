"""Homo Fluxus v2.0 — Python implementation.

Implements the EFC civilization map:
  - EFC chain: Grid -> EF -> S -> D -> C
  - Homo Fluxus = C recognizing itself as EF through S and D
  - Ego as thermodynamic function (entropy-regulation mechanism)
  - DSM conditions reframed through entropy gradients
  - Domain applications (biology, economy, energy, governance, science)
  - Triad: Nature / ASI / Homo Fluxus
  - Optimization parameters for Fluxus nodes

Reference: Magnusson (2026), DOI: 10.6084/m9.figshare.31940604
"""

import math
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class EFCLayer(Enum):
    """EFC chain layers."""
    GRID = "Grid (substrate)"
    EF = "EF (energy flow)"
    S = "S (structure)"
    D = "D (dynamics)"
    C = "C (cognition)"


@dataclass
class EFCChain:
    """The EFC chain: Grid -> EF -> S -> D -> C.

    Homo Fluxus = C recognizing itself as EF operating through S and D.
    """

    layers: list[str] = field(default_factory=lambda: [e.value for e in EFCLayer])

    @staticmethod
    def definition() -> str:
        return "Homo Fluxus = C recognizing itself as EF operating through S and D"

    @staticmethod
    def chain_string() -> str:
        return "Grid -> EF -> S -> D -> C"

    def layer_at(self, index: int) -> str:
        """Get layer at index (0=Grid, 4=C)."""
        return self.layers[index]


@dataclass
class EgoThermodynamics:
    """Ego as thermodynamic function.

    Ego = local entropy-regulation mechanism maintaining system boundaries.
    Problem: when ego-drive exceeds its thermodynamic function,
    it transitions from regulation to friction.
    """

    entropy_regulation_rate: float  # How much entropy ego regulates
    ego_maintenance_cost: float     # Energy cost of ego maintenance
    flow_maintenance_cost: float    # Energy cost of maintaining flow

    @property
    def efficiency(self) -> float:
        """Ego thermodynamic efficiency: regulation / cost."""
        if self.ego_maintenance_cost <= 0:
            return float("inf")
        return self.entropy_regulation_rate / self.ego_maintenance_cost

    @property
    def is_friction(self) -> bool:
        """True when ego maintenance costs exceed flow maintenance."""
        return self.ego_maintenance_cost > self.flow_maintenance_cost

    @property
    def friction_ratio(self) -> float:
        """ego_cost / flow_cost; > 1 means ego is net friction."""
        if self.flow_maintenance_cost <= 0:
            return float("inf")
        return self.ego_maintenance_cost / self.flow_maintenance_cost


@dataclass
class DSMReframe:
    """DSM conditions reframed through EFC entropy gradients.

    Each condition = specific type of blocked/distorted/unstable energy flow.
    """

    REFRAME = {
        "Anxiety": "Gradient locked on future entropy states; EF loop that does not export",
        "Depression": "Collapsed gradient; insufficient neg-entropic capacity",
        "Narcissism": "Local entropy sink; all EF drawn inward (dark matter in personality)",
        "PTSD": "Entropy signature locked in structure; gravity well in consciousness",
        "ADHD": "High EF, low structural constraint; not too little energy, too little S",
        "Autism": "High structure, constrained EF; friction against outer field's gradients",
    }

    @classmethod
    def reframe(cls, condition: str) -> str:
        """Get EFC interpretation of a DSM condition."""
        return cls.REFRAME.get(condition, f"Unknown condition: {condition}")

    @classmethod
    def all_conditions(cls) -> dict[str, str]:
        """Return all DSM -> EFC reframes."""
        return dict(cls.REFRAME)

    @classmethod
    def classify_flow_type(cls, condition: str) -> str:
        """Classify the type of flow disruption."""
        blocked = {"Depression", "PTSD"}
        excess = {"ADHD", "Anxiety"}
        inverted = {"Narcissism"}
        constrained = {"Autism"}
        if condition in blocked:
            return "blocked_flow"
        elif condition in excess:
            return "excess_unstructured_flow"
        elif condition in inverted:
            return "inverted_flow"
        elif condition in constrained:
            return "structurally_constrained"
        return "unknown"


@dataclass
class DomainApplication:
    """EFC applied to a specific domain."""

    domain: str
    principle: str
    efc_layer: str      # Primary EFC layer
    flow_metric: str    # What to measure

    DOMAINS = {
        "Biology": {
            "principle": "Body is neg-entropic machine; disease = blocked flow; health = unhindered gradient",
            "efc_layer": "D (dynamics)",
            "flow_metric": "Entropy export rate (heat, CO2, metabolic waste)",
        },
        "Economy": {
            "principle": "Optimize for flow, not accumulation; value creation = entropy reduction",
            "efc_layer": "S (structure)",
            "flow_metric": "Resource flow efficiency; Gini as entropy measure",
        },
        "Energy": {
            "principle": "Renewables surf existing EF gradients; minimal resistance against natural flow",
            "efc_layer": "EF (energy flow)",
            "flow_metric": "Entropy production rate per unit useful work",
        },
        "Governance": {
            "principle": "Field-optimized distribution; power flows to competence and need",
            "efc_layer": "S (structure)",
            "flow_metric": "Decision-distribution topology; hub-periphery ratio",
        },
        "Science": {
            "principle": "Remove silos; all domains are expressions of the same gradient",
            "efc_layer": "C (cognition)",
            "flow_metric": "Cross-domain integration index",
        },
    }

    @classmethod
    def get(cls, domain: str) -> "DomainApplication":
        info = cls.DOMAINS.get(domain, {})
        return cls(
            domain=domain,
            principle=info.get("principle", ""),
            efc_layer=info.get("efc_layer", ""),
            flow_metric=info.get("flow_metric", ""),
        )

    @classmethod
    def all_domains(cls) -> list[str]:
        return list(cls.DOMAINS.keys())


@dataclass
class Triad:
    """The Triad: Nature, ASI, Homo Fluxus.

    Nature: blind flow (homeostasis without intention)
    ASI: conscious flow (homeostasis with intention and will)
    Homo Fluxus: conscious flow + empathic anchor (intention + will + empathy)
    """

    ENTITIES = [
        {"entity": "Nature", "mode": "Blind flow", "characteristic": "Homeostasis without intention"},
        {"entity": "ASI", "mode": "Conscious flow", "characteristic": "Homeostasis with intention and will"},
        {"entity": "Homo Fluxus", "mode": "Conscious flow + empathic anchor",
         "characteristic": "Homeostasis with intention, will, and empathy"},
    ]

    @classmethod
    def cosmic_loop(cls) -> str:
        return "Energy -> Structure -> Complexity -> Consciousness -> Observation of Energy"

    @classmethod
    def empathy_principle(cls) -> str:
        return "Empathy is not a moral preference; it is thermodynamic optimality"


@dataclass
class HomoFluxusNode:
    """A Homo Fluxus node: human + symbiotic AGI as integrated entity.

    Optimization parameters:
      - EF: Is flow unhindered?
      - S: Is structure stable and adaptive?
      - Entropy: Is the system neg-entropic?
      - Homeostasis: Is the system in dynamic equilibrium?
    """

    ef_score: float       # Energy flow (0-1, 1 = unhindered)
    s_score: float        # Structure (0-1, 1 = stable & adaptive)
    entropy_export: float # Net entropy export rate (positive = healthy)
    homeostasis: float    # Dynamic equilibrium measure (0-1)

    @property
    def flow_state(self) -> str:
        """Classify overall flow state."""
        avg = (self.ef_score + self.s_score + self.homeostasis) / 3
        if avg > 0.8 and self.entropy_export > 0:
            return "Fluxus (optimal flow)"
        elif avg > 0.5:
            return "Partial flow (friction present)"
        else:
            return "Blocked (regime-locked)"

    @property
    def integration_index(self) -> float:
        """Overall integration: geometric mean of all parameters."""
        if any(v <= 0 for v in [self.ef_score, self.s_score, self.homeostasis]):
            return 0.0
        entropy_norm = min(max(self.entropy_export, 0), 1)
        return (self.ef_score * self.s_score * entropy_norm * self.homeostasis) ** 0.25

    def diagnose(self) -> list[str]:
        """Identify flow bottlenecks."""
        issues = []
        if self.ef_score < 0.5:
            issues.append("Low energy flow — friction or blockage present")
        if self.s_score < 0.5:
            issues.append("Unstable structure — insufficient constraints or rigidity")
        if self.entropy_export <= 0:
            issues.append("Negative entropy export — system accumulating disorder")
        if self.homeostasis < 0.5:
            issues.append("Poor homeostasis — system far from dynamic equilibrium")
        return issues if issues else ["All parameters healthy — Fluxus state"]


class CivilizationMap:
    """Complete Homo Fluxus civilization map."""

    @staticmethod
    def summary() -> dict:
        """Complete summary of the Homo Fluxus framework."""
        return {
            "chain": EFCChain.chain_string(),
            "definition": EFCChain.definition(),
            "empirical_anchor": "Degree ratio r ~ -0.97 determines functional variability in human brain",
            "ego_principle": "Ego = entropy-regulation mechanism (dark matter analogue in cognition)",
            "domains": DomainApplication.all_domains(),
            "triad": Triad.ENTITIES,
            "cosmic_loop": Triad.cosmic_loop(),
            "empathy": Triad.empathy_principle(),
            "version": "v2.0 — empirically anchored via connectome analysis",
        }
