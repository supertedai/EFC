"""EFC v2.1 Modular Synthesis -- Python implementation.

Modular decomposition of EFC into Structural, Dynamical, Entropic,
and Informational modules with defined interfaces and consistency checks.

Reference: Magnusson (2025), EFC v2.1 Modular Synthesis
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Module Interface
# ---------------------------------------------------------------------------

@dataclass
class ModuleInterface:
    """Specification of a module's inputs and outputs."""
    inputs: List[str]
    outputs: List[str]
    constraints: List[str]

    def is_compatible(self, other: "ModuleInterface") -> bool:
        """Check if this module's outputs satisfy another module's inputs."""
        return all(inp in self.outputs for inp in other.inputs
                   if inp in self.outputs)

    def summary(self) -> str:
        return (
            f"  Inputs:  {', '.join(self.inputs)}\n"
            f"  Outputs: {', '.join(self.outputs)}\n"
            f"  Constraints: {', '.join(self.constraints)}"
        )


# ---------------------------------------------------------------------------
# Structural Module
# ---------------------------------------------------------------------------

@dataclass
class StructuralModule:
    """Module M1: Structural -- spacetime geometry and topology."""
    name: str = "Structural"
    label: str = "M1"
    description: str = (
        "Defines the spacetime metric, grid topology, and geometric "
        "relationships. Provides the geometric substrate on which other "
        "modules operate."
    )
    interface: ModuleInterface = field(default_factory=lambda: ModuleInterface(
        inputs=["grid_state", "energy_distribution"],
        outputs=["metric_tensor", "curvature", "topology"],
        constraints=["Bianchi identity", "metric signature (-,+,+,+)"],
    ))

    def metric_signature(self) -> Tuple[int, ...]:
        return (-1, 1, 1, 1)

    def degrees_of_freedom(self) -> int:
        """Independent components of the metric in 4D."""
        return 10  # symmetric 4x4 tensor


# ---------------------------------------------------------------------------
# Dynamical Module
# ---------------------------------------------------------------------------

@dataclass
class DynamicalModule:
    """Module M2: Dynamical -- evolution equations and energy flow."""
    name: str = "Dynamical"
    label: str = "M2"
    description: str = (
        "Contains the modified Einstein field equation and Friedmann "
        "dynamics including the energy-flow stress-energy tensor."
    )
    interface: ModuleInterface = field(default_factory=lambda: ModuleInterface(
        inputs=["metric_tensor", "matter_content", "entropy_state"],
        outputs=["field_equations", "Hubble_rate", "growth_rate"],
        constraints=["Energy conservation", "Covariant divergence = 0"],
    ))

    beta: float = 0.16
    H0: float = 67.4
    Omega_m: float = 0.315

    def field_equation_symbolic(self) -> str:
        return "G_{mu nu} = 8 pi G (T_{mu nu} + T^{(E_f)}_{mu nu}) + Lambda_eff g_{mu nu}"

    def H_squared_ratio(self, a: float, S_a: float) -> float:
        """(H/H0)^2 given scale factor and entropy S(a)."""
        mu = 1.0 + self.beta * S_a
        return self.Omega_m * mu / (a ** 3) + (1.0 - self.Omega_m)


# ---------------------------------------------------------------------------
# Entropic Module
# ---------------------------------------------------------------------------

@dataclass
class EntropicModule:
    """Module M3: Entropic -- entropy field and thermodynamic behaviour."""
    name: str = "Entropic"
    label: str = "M3"
    description: str = (
        "Governs the entropy sigmoid S(a), thermodynamic arrow of time, "
        "and entropy-structure coupling."
    )
    interface: ModuleInterface = field(default_factory=lambda: ModuleInterface(
        inputs=["scale_factor"],
        outputs=["entropy_state", "entropy_gradient", "entropy_production_rate"],
        constraints=["Second Law: dS/dt >= 0", "S bounded by S_inf"],
    ))

    S_inf: float = 1.0
    a_t: float = 0.55
    sigma: float = 0.10

    def S(self, a: float) -> float:
        if a <= 0:
            return 0.0
        x = (math.log(a) - math.log(self.a_t)) / self.sigma
        return (self.S_inf / 2.0) * (1.0 + math.tanh(x))

    def dS_dlna(self, a: float) -> float:
        if a <= 0:
            return 0.0
        x = (math.log(a) - math.log(self.a_t)) / self.sigma
        return (self.S_inf / (2.0 * self.sigma)) / (math.cosh(x) ** 2)

    def satisfies_second_law(self, a_values: List[float]) -> bool:
        """Check that S is non-decreasing for a sorted list of scale factors."""
        S_vals = [self.S(a) for a in sorted(a_values)]
        return all(S_vals[i] <= S_vals[i + 1] + 1e-15 for i in range(len(S_vals) - 1))


# ---------------------------------------------------------------------------
# Informational Module
# ---------------------------------------------------------------------------

@dataclass
class InformationalModule:
    """Module M4: Informational -- information field and Landauer coupling."""
    name: str = "Informational"
    label: str = "M4"
    description: str = (
        "Links information content to entropy via Landauer-type bounds. "
        "Bridges thermodynamic and informational descriptions."
    )
    interface: ModuleInterface = field(default_factory=lambda: ModuleInterface(
        inputs=["entropy_state", "temperature"],
        outputs=["information_content", "erasure_cost", "complexity_measure"],
        constraints=["Landauer bound: E >= kT ln 2 per bit"],
    ))

    k_B: float = 1.380649e-23  # J/K

    def landauer_cost(self, T: float, n_bits: int = 1) -> float:
        """Minimum energy to erase n_bits at temperature T."""
        return n_bits * self.k_B * T * math.log(2)

    def max_bits_from_energy(self, E: float, T: float) -> float:
        """Maximum bits erasable with energy E at temperature T."""
        if T <= 0:
            return float('inf')
        return E / (self.k_B * T * math.log(2))


# ---------------------------------------------------------------------------
# Global Consistency
# ---------------------------------------------------------------------------

@dataclass
class ModularArchitecture:
    """The complete modular architecture with inter-module consistency."""
    structural: StructuralModule = field(default_factory=StructuralModule)
    dynamical: DynamicalModule = field(default_factory=DynamicalModule)
    entropic: EntropicModule = field(default_factory=EntropicModule)
    informational: InformationalModule = field(default_factory=InformationalModule)

    def modules(self) -> Dict[str, object]:
        return {
            "M1_Structural": self.structural,
            "M2_Dynamical": self.dynamical,
            "M3_Entropic": self.entropic,
            "M4_Informational": self.informational,
        }

    def module_count(self) -> int:
        return 4

    def check_entropy_dynamics_consistency(self, a: float) -> Dict[str, float]:
        """Cross-module check: entropy feeds into dynamics."""
        S_a = self.entropic.S(a)
        H2_ratio = self.dynamical.H_squared_ratio(a, S_a)
        return {"a": a, "S(a)": S_a, "(H/H0)^2": H2_ratio}

    def interface_map(self) -> Dict[str, ModuleInterface]:
        return {
            "M1": self.structural.interface,
            "M2": self.dynamical.interface,
            "M3": self.entropic.interface,
            "M4": self.informational.interface,
        }

    def summary(self) -> str:
        lines = ["=== EFC v2.1 Modular Synthesis ===", ""]
        for label, mod in self.modules().items():
            lines.append(f"{label}: {mod.name}")
            lines.append(f"  {mod.description}")
            lines.append(mod.interface.summary())
            lines.append("")
        return "\n".join(lines)
