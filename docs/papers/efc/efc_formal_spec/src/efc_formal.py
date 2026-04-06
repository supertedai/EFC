"""EFC Formal Specification -- Python implementation.

Mathematical objects, field equations, notation, thermodynamic constraints,
and structural relations as defined in the formal spec.

Reference: Magnusson (2025), EFC Formal Specification
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Formal Symbol Table
# ---------------------------------------------------------------------------

@dataclass
class FormalSymbol:
    """A formally defined symbol in the EFC notation system."""
    symbol: str
    latex: str
    name: str
    domain: str
    description: str

    def summary(self) -> str:
        return f"{self.symbol} ({self.latex}): {self.name} -- {self.description}"


def symbol_table() -> Dict[str, FormalSymbol]:
    """Canonical symbol table for the EFC formal specification."""
    return {
        "G_uv": FormalSymbol(
            symbol="G_uv", latex="G_{\\mu\\nu}",
            name="Einstein tensor", domain="Symmetric (0,2)-tensor",
            description="Encodes spacetime curvature",
        ),
        "T_uv": FormalSymbol(
            symbol="T_uv", latex="T_{\\mu\\nu}",
            name="Stress-energy tensor", domain="Symmetric (0,2)-tensor",
            description="Standard matter-energy content",
        ),
        "T_Ef_uv": FormalSymbol(
            symbol="T^(Ef)_uv", latex="T^{(E_f)}_{\\mu\\nu}",
            name="Energy-flow stress-energy", domain="Symmetric (0,2)-tensor",
            description="EFC-specific energy-flow contribution to field equations",
        ),
        "Lambda_eff": FormalSymbol(
            symbol="Lambda_eff", latex="\\Lambda_{\\text{eff}}",
            name="Effective cosmological constant", domain="Scalar",
            description="Effective dark energy term in EFC",
        ),
        "S_a": FormalSymbol(
            symbol="S(a)", latex="S(a)",
            name="Entropy field", domain="[0, S_inf]",
            description="Entropy sigmoid as function of scale factor",
        ),
        "mu_a": FormalSymbol(
            symbol="mu(a)", latex="\\mu(a)",
            name="Effective gravitational coupling", domain="[1, 1+beta*S_inf]",
            description="Ratio G_eff/G = 1 + beta*S(a)",
        ),
        "beta": FormalSymbol(
            symbol="beta", latex="\\beta",
            name="EFC coupling constant", domain="R >= 0",
            description="Amplitude of entropy-gravity coupling",
        ),
        "a_t": FormalSymbol(
            symbol="a_t", latex="a_t",
            name="Transition scale factor", domain="(0, 1]",
            description="Scale factor at entropy sigmoid midpoint",
        ),
        "sigma": FormalSymbol(
            symbol="sigma", latex="\\sigma",
            name="Transition width", domain="R > 0",
            description="Width of entropy sigmoid transition",
        ),
        "g_uv": FormalSymbol(
            symbol="g_uv", latex="g_{\\mu\\nu}",
            name="Metric tensor", domain="Symmetric (0,2)-tensor, signature (-,+,+,+)",
            description="Spacetime metric",
        ),
    }


# ---------------------------------------------------------------------------
# Formal Field Equation
# ---------------------------------------------------------------------------

@dataclass
class FormalFieldEquation:
    """The EFC field equation in formal notation.

    G_{mu nu} = 8 pi G (T_{mu nu} + T^{(E_f)}_{mu nu}) + Lambda_eff g_{mu nu}
    """
    lhs: str = "G_{mu nu}"
    rhs_terms: List[str] = field(default_factory=lambda: [
        "8 pi G T_{mu nu}",
        "8 pi G T^{(E_f)}_{mu nu}",
        "Lambda_eff g_{mu nu}",
    ])

    def equation_string(self) -> str:
        return f"{self.lhs} = {' + '.join(self.rhs_terms)}"

    def term_count(self) -> int:
        return len(self.rhs_terms)

    def reduces_to_GR(self) -> str:
        """Condition for GR recovery."""
        return "T^{(E_f)}_{mu nu} -> 0 and Lambda_eff -> Lambda"


# ---------------------------------------------------------------------------
# Entropy Sigmoid (formal definition)
# ---------------------------------------------------------------------------

@dataclass
class FormalEntropySigmoid:
    """Formal definition of the entropy field S(a).

    S(a) = (S_inf / 2) [1 + tanh((ln a - ln a_t) / sigma)]

    Boundary conditions:
      lim_{a->0} S(a) = 0
      lim_{a->inf} S(a) = S_inf
      S(a_t) = S_inf / 2
    """
    S_inf: float = 1.0
    a_t: float = 0.55
    sigma: float = 0.10

    def evaluate(self, a: float) -> float:
        if a <= 0:
            return 0.0
        x = (math.log(a) - math.log(self.a_t)) / self.sigma
        return (self.S_inf / 2.0) * (1.0 + math.tanh(x))

    def derivative(self, a: float) -> float:
        """dS/d(ln a)."""
        if a <= 0:
            return 0.0
        x = (math.log(a) - math.log(self.a_t)) / self.sigma
        return (self.S_inf / (2.0 * self.sigma)) / (math.cosh(x) ** 2)

    def boundary_conditions(self) -> Dict[str, str]:
        return {
            "a -> 0": "S -> 0",
            "a = a_t": f"S = S_inf/2 = {self.S_inf / 2}",
            "a -> inf": f"S -> S_inf = {self.S_inf}",
        }

    def verify_boundary(self, a_test: float = 0.001) -> bool:
        """Verify that boundary conditions hold approximately."""
        return (
            self.evaluate(a_test) < 0.01 * self.S_inf and
            abs(self.evaluate(self.a_t) - self.S_inf / 2.0) < 0.01 and
            self.evaluate(100.0) > 0.99 * self.S_inf
        )


# ---------------------------------------------------------------------------
# Thermodynamic Constraint Set
# ---------------------------------------------------------------------------

@dataclass
class ThermodynamicConstraint:
    """A formal thermodynamic constraint in EFC."""
    name: str
    formal_statement: str
    implication: str


def constraint_set() -> List[ThermodynamicConstraint]:
    """The formal thermodynamic constraint set."""
    return [
        ThermodynamicConstraint(
            name="C1: Entropy monotonicity",
            formal_statement="dS/dt >= 0 for all t",
            implication="Arrow of time; forbids entropy decrease",
        ),
        ThermodynamicConstraint(
            name="C2: Energy conservation",
            formal_statement="nabla_mu T^{mu nu}_{total} = 0",
            implication="Covariant conservation of total stress-energy",
        ),
        ThermodynamicConstraint(
            name="C3: Entropy boundedness",
            formal_statement="0 <= S(a) <= S_inf for all a",
            implication="Entropy is bounded above; prevents divergence",
        ),
        ThermodynamicConstraint(
            name="C4: GR limit",
            formal_statement="lim_{beta->0} EFC = GR + Lambda",
            implication="EFC reduces to standard GR when coupling vanishes",
        ),
        ThermodynamicConstraint(
            name="C5: Positive definiteness",
            formal_statement="mu(a) >= 1 for beta >= 0",
            implication="Effective gravity is enhanced, never reduced",
        ),
    ]


# ---------------------------------------------------------------------------
# Grid Field Formal Structure
# ---------------------------------------------------------------------------

@dataclass
class GridFieldSpec:
    """Formal specification of the Grid field."""
    name: str = "Grid Field"
    symbol: str = "G_grid"
    dimensionality: int = 4
    topology: str = "Locally finite graph -> smooth manifold (emergent)"
    signature: Tuple[int, ...] = (-1, 1, 1, 1)

    def emergent_metric_condition(self) -> str:
        return "Averaging over grid cells on scales >> l_grid yields smooth g_{mu nu}"

    def degrees_of_freedom(self) -> int:
        """Independent metric components."""
        d = self.dimensionality
        return d * (d + 1) // 2


# ---------------------------------------------------------------------------
# Formal Specification Container
# ---------------------------------------------------------------------------

@dataclass
class EFCFormalSpec:
    """Top-level container for the EFC Formal Specification."""
    version: str = "1.0"
    title: str = "EFC Formal Specification"
    symbols: Dict[str, FormalSymbol] = field(default_factory=symbol_table)
    field_equation: FormalFieldEquation = field(default_factory=FormalFieldEquation)
    entropy: FormalEntropySigmoid = field(default_factory=FormalEntropySigmoid)
    constraints: List[ThermodynamicConstraint] = field(default_factory=constraint_set)
    grid: GridFieldSpec = field(default_factory=GridFieldSpec)

    def symbol_count(self) -> int:
        return len(self.symbols)

    def constraint_count(self) -> int:
        return len(self.constraints)

    def summary(self) -> str:
        lines = [f"=== {self.title} ===", ""]
        lines.append(f"Field Equation: {self.field_equation.equation_string()}")
        lines.append(f"GR recovery: {self.field_equation.reduces_to_GR()}")
        lines.append("")
        lines.append(f"Symbols defined: {self.symbol_count()}")
        lines.append(f"Constraints: {self.constraint_count()}")
        lines.append("")
        lines.append("Entropy boundary conditions:")
        for k, v in self.entropy.boundary_conditions().items():
            lines.append(f"  {k}: {v}")
        lines.append("")
        lines.append(f"Grid: {self.grid.topology}")
        lines.append(f"  Emergent metric: {self.grid.emergent_metric_condition()}")
        return "\n".join(lines)
