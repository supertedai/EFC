"""EFC v1.2 Foundational Framework -- Python implementation.

Defines core EFC concepts: four fundamental fields (Energy Flow, Entropy,
Grid, Information), regime architecture (L0-L3), thermodynamic foundations,
and structural relationships.

Reference: Magnusson (2025), DOI: 10.6084/m9.figshare.30563738
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BOLTZMANN_K = 1.380649e-23  # J/K
PLANCK_H = 6.62607015e-34   # J*s
C_LIGHT = 2.998e8           # m/s
G_NEWTON = 6.674e-11        # m^3 kg^-1 s^-2


# ---------------------------------------------------------------------------
# EFC Fields
# ---------------------------------------------------------------------------

@dataclass
class EFCField:
    """A fundamental field in the EFC framework."""
    name: str
    symbol: str
    description: str
    role: str
    regime_coupling: str

    def summary(self) -> str:
        return (
            f"Field: {self.name} ({self.symbol})\n"
            f"  Role: {self.role}\n"
            f"  Description: {self.description}\n"
            f"  Regime coupling: {self.regime_coupling}"
        )


def canonical_fields() -> Dict[str, EFCField]:
    """Return the four canonical EFC fields as defined in v1.2."""
    return {
        "energy_flow": EFCField(
            name="Energy Flow",
            symbol="E_f",
            description="Net directional energy transfer driving cosmic evolution",
            role="Primary dynamical driver; sources the modified Einstein equation",
            regime_coupling="Active across all regimes; amplitude varies with epoch",
        ),
        "entropy": EFCField(
            name="Entropy Field",
            symbol="S",
            description="Thermodynamic entropy production governing irreversibility and structure",
            role="Determines arrow of time and structure formation rate",
            regime_coupling="Monotonically non-decreasing; sigmoid transition at L1-L2 boundary",
        ),
        "grid": EFCField(
            name="Grid Field",
            symbol="G_grid",
            description="Discrete substrate encoding spatial connectivity and topology",
            role="Provides the micro-structural scaffold for spacetime geometry",
            regime_coupling="Dominant at small scales (L0); emergent smoothness at L2-L3",
        ),
        "information": EFCField(
            name="Information Field",
            symbol="I",
            description="Information content linked to entropy via Landauer-like bound",
            role="Bridges thermodynamic and informational descriptions of structure",
            regime_coupling="Relevant at all scales; strongest coupling at L2-L3",
        ),
    }


# ---------------------------------------------------------------------------
# Regime Architecture
# ---------------------------------------------------------------------------

@dataclass
class Regime:
    """An EFC regime (L0 through L3)."""
    label: str
    name: str
    scale: str
    dominant_physics: str
    entropy_behaviour: str
    description: str

    def summary(self) -> str:
        return (
            f"Regime {self.label}: {self.name}\n"
            f"  Scale: {self.scale}\n"
            f"  Dominant physics: {self.dominant_physics}\n"
            f"  Entropy behaviour: {self.entropy_behaviour}"
        )


def regime_architecture() -> Dict[str, Regime]:
    """Return the four-level regime architecture."""
    return {
        "L0": Regime(
            label="L0",
            name="Planck / Sub-Planck",
            scale="< l_P ~ 1.6e-35 m",
            dominant_physics="Quantum gravity / grid microphysics",
            entropy_behaviour="Near-zero; pre-thermodynamic",
            description="Sub-Planckian domain where the discrete grid dominates",
        ),
        "L1": Regime(
            label="L1",
            name="Quantum / Early Universe",
            scale="l_P to ~Mpc",
            dominant_physics="Quantum fields, radiation, nucleosynthesis",
            entropy_behaviour="Low and slowly rising",
            description="Early universe through recombination; entropy production begins",
        ),
        "L2": Regime(
            label="L2",
            name="Classical / Structure Formation",
            scale="Mpc to ~Gpc",
            dominant_physics="Gravity, structure formation, galaxy evolution",
            entropy_behaviour="Rapidly rising; sigmoid transition from L1",
            description="Late-time regime where entropy-driven modification becomes significant",
        ),
        "L3": Regime(
            label="L3",
            name="Cosmological / Horizon",
            scale="> Gpc (Hubble scale)",
            dominant_physics="Dark energy, horizon thermodynamics",
            entropy_behaviour="Approaching asymptotic maximum S_inf",
            description="Largest observable scales; entropy saturation and de Sitter approach",
        ),
    }


# ---------------------------------------------------------------------------
# Thermodynamic Foundations
# ---------------------------------------------------------------------------

@dataclass
class ThermodynamicFoundation:
    """Core thermodynamic principles underlying EFC."""
    principle: str
    statement: str
    efc_role: str

    def summary(self) -> str:
        return f"{self.principle}: {self.statement} [EFC role: {self.efc_role}]"


def thermodynamic_principles() -> List[ThermodynamicFoundation]:
    """The thermodynamic first principles used in EFC v1.2."""
    return [
        ThermodynamicFoundation(
            principle="Second Law (generalised)",
            statement="Total entropy of the universe is non-decreasing: dS/dt >= 0",
            efc_role="Drives the arrow of time and constrains all EFC field evolution",
        ),
        ThermodynamicFoundation(
            principle="Energy Conservation (first law)",
            statement="Total energy is conserved; energy flow is redistributed, not created",
            efc_role="Ensures self-consistency of the modified Friedmann dynamics",
        ),
        ThermodynamicFoundation(
            principle="Entropy-Structure Coupling",
            statement="Structure formation is an entropy-producing process",
            efc_role="Links thermodynamic evolution to gravitational clustering",
        ),
        ThermodynamicFoundation(
            principle="Landauer Bound",
            statement="Erasure of one bit costs >= kT ln 2 energy",
            efc_role="Connects the information field to the entropy field",
        ),
    ]


# ---------------------------------------------------------------------------
# Structural Relationships
# ---------------------------------------------------------------------------

@dataclass
class StructuralRelation:
    """A structural relationship between EFC fields."""
    name: str
    fields: List[str]
    equation_description: str
    regime: str

    def summary(self) -> str:
        return (
            f"{self.name}: {' <-> '.join(self.fields)}\n"
            f"  {self.equation_description}\n"
            f"  Active in regime(s): {self.regime}"
        )


def structural_relationships() -> List[StructuralRelation]:
    """Key structural relationships defined in v1.2."""
    return [
        StructuralRelation(
            name="Energy-Entropy coupling",
            fields=["E_f", "S"],
            equation_description="Energy flow drives entropy production; dS/dt ~ |E_f|",
            regime="All regimes",
        ),
        StructuralRelation(
            name="Entropy-Grid feedback",
            fields=["S", "G_grid"],
            equation_description="Entropy gradients modify effective grid connectivity",
            regime="L0-L1 (strong), L2 (emergent)",
        ),
        StructuralRelation(
            name="Grid-Geometry emergence",
            fields=["G_grid", "g_mu_nu"],
            equation_description="Smooth spacetime metric emerges from grid averaging",
            regime="L1-L3",
        ),
        StructuralRelation(
            name="Information-Entropy duality",
            fields=["I", "S"],
            equation_description="I and S are dual descriptions bounded by Landauer relation",
            regime="All regimes",
        ),
    ]


# ---------------------------------------------------------------------------
# Entropy sigmoid (used across EFC)
# ---------------------------------------------------------------------------

def entropy_sigmoid(a: float, S_inf: float = 1.0, a_t: float = 0.55,
                    sigma: float = 0.10) -> float:
    """Entropy field S(a) = (S_inf/2) * [1 + tanh((ln a - ln a_t) / sigma)].

    Parameters
    ----------
    a : float
        Scale factor (0 < a <= 1 for past, a=1 today).
    S_inf : float
        Asymptotic entropy (normalised to 1 by default).
    a_t : float
        Transition scale factor.
    sigma : float
        Transition width.
    """
    if a <= 0:
        return 0.0
    x = (math.log(a) - math.log(a_t)) / sigma
    return (S_inf / 2.0) * (1.0 + math.tanh(x))


# ---------------------------------------------------------------------------
# Framework summary
# ---------------------------------------------------------------------------

@dataclass
class FoundationalFramework:
    """Top-level container for the EFC v1.2 Foundational Framework."""
    version: str = "1.2"
    title: str = "EFC v1.2 Foundational Framework"
    fields: Dict[str, EFCField] = field(default_factory=canonical_fields)
    regimes: Dict[str, Regime] = field(default_factory=regime_architecture)
    principles: List[ThermodynamicFoundation] = field(
        default_factory=thermodynamic_principles
    )
    relationships: List[StructuralRelation] = field(
        default_factory=structural_relationships
    )

    def summary(self) -> str:
        lines = [
            f"=== {self.title} ===",
            "",
            "FIELDS:",
        ]
        for f in self.fields.values():
            lines.append(f"  - {f.name} ({f.symbol}): {f.role}")
        lines.append("")
        lines.append("REGIMES:")
        for r in self.regimes.values():
            lines.append(f"  - {r.label} ({r.name}): {r.dominant_physics}")
        lines.append("")
        lines.append("THERMODYNAMIC PRINCIPLES:")
        for p in self.principles:
            lines.append(f"  - {p.principle}: {p.statement}")
        lines.append("")
        lines.append("STRUCTURAL RELATIONSHIPS:")
        for s in self.relationships:
            lines.append(f"  - {s.name}: {' <-> '.join(s.fields)}")
        return "\n".join(lines)

    def field_count(self) -> int:
        return len(self.fields)

    def regime_count(self) -> int:
        return len(self.regimes)

    def entropy_at(self, a: float) -> float:
        """Evaluate the canonical entropy sigmoid at scale factor *a*."""
        return entropy_sigmoid(a)
