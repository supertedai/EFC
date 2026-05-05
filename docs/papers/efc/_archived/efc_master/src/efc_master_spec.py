"""EFC Master Specification -- Python implementation.

Canonical, authoritative reference for the EFC theory: all fields,
equations, parameters, regime architecture, consistency rules, and
cognitive/informational layers.

Reference: Magnusson (2025), EFC Master Specification
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Canonical Parameters
# ---------------------------------------------------------------------------

@dataclass
class EFCCanonicalParameters:
    """All canonical EFC parameters in one place."""
    # Entropy sigmoid
    S_inf: float = 1.0
    a_t: float = 0.55
    sigma: float = 0.10
    z_t: float = 0.82  # = 1/a_t - 1

    # Coupling
    beta: float = 0.16

    # Cosmological
    H0: float = 67.4  # km/s/Mpc
    Omega_m: float = 0.315
    Omega_r: float = 9.0e-5
    Omega_Lambda: float = 0.685

    # Physical constants
    G: float = 6.674e-11      # m^3 kg^-1 s^-2
    c: float = 2.998e8        # m/s
    k_B: float = 1.380649e-23 # J/K

    def as_dict(self) -> Dict[str, float]:
        return {
            "S_inf": self.S_inf, "a_t": self.a_t, "sigma": self.sigma,
            "beta": self.beta, "H0": self.H0, "Omega_m": self.Omega_m,
            "Omega_Lambda": self.Omega_Lambda, "G": self.G, "c": self.c,
        }


# ---------------------------------------------------------------------------
# Core Equations
# ---------------------------------------------------------------------------

def entropy_sigmoid(a: float, p: Optional[EFCCanonicalParameters] = None) -> float:
    """S(a) = (S_inf/2)[1 + tanh((ln a - ln a_t)/sigma)]."""
    if p is None:
        p = EFCCanonicalParameters()
    if a <= 0:
        return 0.0
    x = (math.log(a) - math.log(p.a_t)) / p.sigma
    return (p.S_inf / 2.0) * (1.0 + math.tanh(x))


def mu(a: float, p: Optional[EFCCanonicalParameters] = None) -> float:
    """mu(a) = 1 + beta * S(a)."""
    if p is None:
        p = EFCCanonicalParameters()
    return 1.0 + p.beta * entropy_sigmoid(a, p)


def hubble_ratio_squared(a: float, p: Optional[EFCCanonicalParameters] = None) -> float:
    """(H(a)/H0)^2 with EFC modification."""
    if p is None:
        p = EFCCanonicalParameters()
    if a <= 0:
        return float('inf')
    return (p.Omega_r / a**4 + p.Omega_m * mu(a, p) / a**3 + p.Omega_Lambda)


# ---------------------------------------------------------------------------
# Regime Definitions
# ---------------------------------------------------------------------------

@dataclass
class MasterRegime:
    """Regime as defined in the master specification."""
    label: str
    name: str
    scale_range: str
    dominant_fields: List[str]
    key_physics: str
    transition_condition: str


def master_regimes() -> List[MasterRegime]:
    return [
        MasterRegime("L0", "Planck/Sub-Planck", "< l_P",
                      ["Grid"], "Quantum gravity, grid microphysics",
                      "Grid averaging yields emergent geometry"),
        MasterRegime("L1", "Quantum/Early Universe", "l_P to Mpc",
                      ["Energy Flow", "Grid"], "QFT, nucleosynthesis, CMB",
                      "Entropy begins rising; S << S_inf/2"),
        MasterRegime("L2", "Classical/Structure Formation", "Mpc to Gpc",
                      ["Energy Flow", "Entropy"], "Gravity, clustering, galaxy evolution",
                      "Sigmoid transition; S crosses S_inf/2 at a_t"),
        MasterRegime("L3", "Cosmological/Horizon", "> Gpc",
                      ["Entropy", "Information"], "Dark energy, horizon thermodynamics",
                      "S -> S_inf; de Sitter approach"),
    ]


# ---------------------------------------------------------------------------
# Consistency Rules
# ---------------------------------------------------------------------------

@dataclass
class ConsistencyRule:
    """A cross-field consistency rule from the master specification."""
    id: str
    name: str
    statement: str
    fields_involved: List[str]


def consistency_rules() -> List[ConsistencyRule]:
    return [
        ConsistencyRule("CR1", "Entropy monotonicity",
                        "dS/dt >= 0 globally",
                        ["Entropy"]),
        ConsistencyRule("CR2", "Energy conservation",
                        "nabla_mu T^{mu nu}_{total} = 0",
                        ["Energy Flow", "Entropy"]),
        ConsistencyRule("CR3", "GR recovery",
                        "beta -> 0 recovers GR + Lambda",
                        ["Energy Flow"]),
        ConsistencyRule("CR4", "Metric emergence",
                        "Grid averaging on scales >> l_grid yields smooth g_{mu nu}",
                        ["Grid"]),
        ConsistencyRule("CR5", "Information-entropy duality",
                        "I and S are bounded by Landauer relation",
                        ["Information", "Entropy"]),
        ConsistencyRule("CR6", "Regime continuity",
                        "All fields are continuous across regime boundaries",
                        ["All"]),
    ]


# ---------------------------------------------------------------------------
# Cognitive/Informational Layer
# ---------------------------------------------------------------------------

@dataclass
class CognitiveLayer:
    """The cognitive and informational layer of EFC."""
    name: str = "Cognitive/Informational Layer"
    fields: List[str] = field(default_factory=lambda: ["Information", "Entropy"])
    landauer_bound: str = "E >= k_B T ln 2 per bit erased"
    role: str = "Bridges thermodynamic entropy and information-theoretic descriptions"
    regime: str = "Most relevant at L2-L3"

    def summary(self) -> str:
        return (
            f"{self.name}\n"
            f"  Fields: {', '.join(self.fields)}\n"
            f"  Landauer bound: {self.landauer_bound}\n"
            f"  Role: {self.role}\n"
            f"  Regime: {self.regime}"
        )


# ---------------------------------------------------------------------------
# Master Specification Container
# ---------------------------------------------------------------------------

@dataclass
class EFCMasterSpec:
    """The complete EFC Master Specification."""
    version: str = "1.0"
    title: str = "EFC Master Specification"
    params: EFCCanonicalParameters = field(default_factory=EFCCanonicalParameters)
    regimes: List[MasterRegime] = field(default_factory=master_regimes)
    rules: List[ConsistencyRule] = field(default_factory=consistency_rules)
    cognitive: CognitiveLayer = field(default_factory=CognitiveLayer)

    def entropy_at(self, a: float) -> float:
        return entropy_sigmoid(a, self.params)

    def mu_at(self, a: float) -> float:
        return mu(a, self.params)

    def H_ratio_sq(self, a: float) -> float:
        return hubble_ratio_squared(a, self.params)

    def regime_count(self) -> int:
        return len(self.regimes)

    def rule_count(self) -> int:
        return len(self.rules)

    def summary(self) -> str:
        lines = [
            f"=== {self.title} (v{self.version}) ===",
            "",
            "CANONICAL PARAMETERS:",
            f"  beta={self.params.beta}, a_t={self.params.a_t}, "
            f"sigma={self.params.sigma}",
            f"  H0={self.params.H0}, Omega_m={self.params.Omega_m}",
            "",
            "FIELD EQUATION:",
            "  G_uv = 8piG(T_uv + T^(Ef)_uv) + Lambda_eff g_uv",
            "",
            f"REGIMES ({self.regime_count()}):",
        ]
        for r in self.regimes:
            lines.append(f"  {r.label}: {r.name} -- {r.key_physics}")
        lines.append("")
        lines.append(f"CONSISTENCY RULES ({self.rule_count()}):")
        for rule in self.rules:
            lines.append(f"  {rule.id}: {rule.statement}")
        lines.append("")
        lines.append(self.cognitive.summary())
        return "\n".join(lines)
