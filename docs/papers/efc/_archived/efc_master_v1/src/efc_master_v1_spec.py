"""EFC Master Specification v1 (Archive) -- Python implementation.

Earliest complete EFC formulation: initial field definitions, entropy
sigmoid, regime architecture, and thermodynamic foundations.

Reference: Magnusson (2025), EFC Master Specification v1
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List


# ---------------------------------------------------------------------------
# v1 Parameters (original formulation)
# ---------------------------------------------------------------------------

@dataclass
class V1Parameters:
    """EFC v1 canonical parameters (original formulation).

    These are the original values from the v1 master specification.
    Later versions may have refined some of these.
    """
    S_inf: float = 1.0
    a_t: float = 0.55
    sigma: float = 0.10
    beta: float = 0.16
    H0: float = 67.4
    Omega_m: float = 0.315
    Omega_Lambda: float = 0.685
    G: float = 6.674e-11
    c: float = 2.998e8

    def as_dict(self) -> Dict[str, float]:
        return {k: v for k, v in self.__dict__.items()}


# ---------------------------------------------------------------------------
# v1 Entropy Field
# ---------------------------------------------------------------------------

def v1_entropy(a: float, S_inf: float = 1.0, a_t: float = 0.55,
               sigma: float = 0.10) -> float:
    """Original v1 entropy sigmoid S(a)."""
    if a <= 0:
        return 0.0
    x = (math.log(a) - math.log(a_t)) / sigma
    return (S_inf / 2.0) * (1.0 + math.tanh(x))


def v1_mu(a: float, beta: float = 0.16, **kwargs) -> float:
    """Original v1 effective gravitational coupling."""
    return 1.0 + beta * v1_entropy(a, **kwargs)


# ---------------------------------------------------------------------------
# v1 Regime Architecture
# ---------------------------------------------------------------------------

@dataclass
class V1Regime:
    """Regime as defined in the v1 master spec."""
    label: str
    name: str
    description: str
    dominant_field: str


def v1_regimes() -> List[V1Regime]:
    return [
        V1Regime("L0", "Planck Scale",
                 "Sub-Planckian grid microphysics domain", "Grid"),
        V1Regime("L1", "Early Universe",
                 "Radiation-dominated era through recombination", "Energy Flow"),
        V1Regime("L2", "Structure Formation",
                 "Matter-dominated era with entropy-driven modification", "Entropy"),
        V1Regime("L3", "Horizon Scale",
                 "Cosmological horizon and de Sitter approach", "Information"),
    ]


# ---------------------------------------------------------------------------
# v1 Field Definitions
# ---------------------------------------------------------------------------

@dataclass
class V1FieldDefinition:
    """A field as defined in the v1 master specification."""
    name: str
    symbol: str
    description: str
    introduced_in: str


def v1_fields() -> List[V1FieldDefinition]:
    return [
        V1FieldDefinition("Energy Flow", "E_f",
                          "Net directional energy transfer",
                          "v1 master spec, Section 2"),
        V1FieldDefinition("Entropy", "S",
                          "Thermodynamic entropy production",
                          "v1 master spec, Section 3"),
        V1FieldDefinition("Grid", "G_grid",
                          "Discrete spatial connectivity substrate",
                          "v1 master spec, Section 4"),
        V1FieldDefinition("Information", "I",
                          "Information content via Landauer bound",
                          "v1 master spec, Section 5"),
    ]


# ---------------------------------------------------------------------------
# Version Comparison Utility
# ---------------------------------------------------------------------------

@dataclass
class VersionComparison:
    """Utility for comparing v1 with later versions."""
    v1_params: V1Parameters = field(default_factory=V1Parameters)

    def compare_entropy(self, a: float, v2_S_inf: float = 1.0,
                        v2_a_t: float = 0.55, v2_sigma: float = 0.10) -> Dict[str, float]:
        """Compare v1 and v2 entropy at a given scale factor."""
        S_v1 = v1_entropy(a, self.v1_params.S_inf, self.v1_params.a_t,
                          self.v1_params.sigma)
        S_v2 = v1_entropy(a, v2_S_inf, v2_a_t, v2_sigma)  # same functional form
        return {
            "a": a,
            "S_v1": S_v1,
            "S_v2": S_v2,
            "delta_S": S_v2 - S_v1,
            "identical_form": True,
        }

    def parameters_unchanged(self) -> bool:
        """Check if v1 core parameters match v2 defaults."""
        return (
            self.v1_params.beta == 0.16 and
            self.v1_params.a_t == 0.55 and
            self.v1_params.sigma == 0.10
        )


# ---------------------------------------------------------------------------
# v1 Master Spec Container
# ---------------------------------------------------------------------------

@dataclass
class EFCMasterV1:
    """The archived v1 Master Specification."""
    version: str = "1.0"
    status: str = "archived"
    title: str = "EFC Master Specification (v1 Archive)"
    params: V1Parameters = field(default_factory=V1Parameters)
    regimes: List[V1Regime] = field(default_factory=v1_regimes)
    fields: List[V1FieldDefinition] = field(default_factory=v1_fields)

    def entropy_at(self, a: float) -> float:
        return v1_entropy(a, self.params.S_inf, self.params.a_t, self.params.sigma)

    def mu_at(self, a: float) -> float:
        return v1_mu(a, self.params.beta, S_inf=self.params.S_inf,
                     a_t=self.params.a_t, sigma=self.params.sigma)

    def field_count(self) -> int:
        return len(self.fields)

    def regime_count(self) -> int:
        return len(self.regimes)

    def summary(self) -> str:
        lines = [
            f"=== {self.title} (status: {self.status}) ===",
            "",
            f"Parameters: beta={self.params.beta}, a_t={self.params.a_t}, "
            f"sigma={self.params.sigma}",
            "",
            f"Fields ({self.field_count()}):",
        ]
        for f in self.fields:
            lines.append(f"  {f.symbol}: {f.name} -- {f.description}")
        lines.append("")
        lines.append(f"Regimes ({self.regime_count()}):")
        for r in self.regimes:
            lines.append(f"  {r.label}: {r.name} (dominant: {r.dominant_field})")
        lines.append("")
        lines.append("Note: This version is archived. See v2.x for current spec.")
        return "\n".join(lines)
