"""Grid Microphysics to RAR — Python implementation.

Implements the minimal gradient-coupled excitation model that bridges
EFC macro-framework to micro-interpretation. Three assumptions produce
the Bose-Einstein RAR form: mu(g) = 1/(exp(sqrt(g/a0)) - 1).

Reference: Magnusson (2026), DOI: 10.6084/m9.figshare.31878760
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional


# Constants
A0_SPARC = 1.2e-10          # m/s^2, measured SPARC value
G_N = 6.674e-11             # m^3 kg^-1 s^-2, Newton's constant
HBAR = 1.0546e-34           # J*s, reduced Planck constant
K_B = 1.3806e-23            # J/K, Boltzmann constant


@dataclass
class GridNode:
    """A single node on the discrete substrate (grid).

    Each node supports bosonic excitation modes whose energy
    depends on the local gravitational environment via gradient coupling.

    Attributes:
        g_local: Local gravitational acceleration |nabla Phi| at this node (m/s^2).
        a0: Acceleration scale (m/s^2). Default: SPARC value.
    """
    g_local: float
    a0: float = A0_SPARC

    @property
    def excitation_energy_ratio(self) -> float:
        """E / (k_B T_grid) = sqrt(g / a0). Eq. (6)."""
        return math.sqrt(self.g_local / self.a0)

    @property
    def occupation_number(self) -> float:
        """Mean occupation number <n> = 1/(exp(sqrt(g/a0)) - 1). Eq. (7)."""
        x = self.excitation_energy_ratio
        if x > 500:
            return math.exp(-x)
        return 1.0 / (math.expm1(x))

    @property
    def mu(self) -> float:
        """Gravitational enhancement mu(g) = <n>."""
        return self.occupation_number


@dataclass
class GradientCoupling:
    """Why sqrt(g) and not g or Phi.

    Gradient coupling is physically natural: in an elastic medium,
    energy is proportional to strain. For a discrete substrate in a
    gravitational field, the relevant strain is |nabla Phi| * l_g.

    Only gradient coupling produces universal RAR consistent with SPARC.
    """

    @staticmethod
    def density_coupling(rho: float, G: float = G_N) -> float:
        """Coupling to density: m_eff ~ sqrt(G*rho). WRONG form."""
        return math.sqrt(G * rho)

    @staticmethod
    def potential_coupling(Phi: float) -> float:
        """Coupling to potential: m_eff ~ sqrt(|Phi|). NOT universal."""
        return math.sqrt(abs(Phi))

    @staticmethod
    def gradient_coupling(g: float, a0: float = A0_SPARC) -> float:
        """Coupling to acceleration: E ~ sqrt(g). CORRECT — gives BE form."""
        return math.sqrt(g / a0)

    @staticmethod
    def test_alternatives(g: float, rho: float, Phi: float) -> dict:
        """Compare all three coupling options."""
        gc = GradientCoupling()
        return {
            "density_coupling": gc.density_coupling(rho),
            "potential_coupling": gc.potential_coupling(Phi),
            "gradient_coupling": gc.gradient_coupling(g),
            "correct": "gradient_coupling",
            "reason": "Only gradient coupling gives universal RAR independent of enclosed mass"
        }


@dataclass
class BoseEinsteinRAR:
    """Bose-Einstein form of the Radial Acceleration Relation.

    mu(g) = 1 / (exp(sqrt(g/a0)) - 1)

    Derived from three assumptions:
    A1: Bosonic statistics
    A2: Gradient-coupled excitation energy E = hbar*omega0*sqrt(g/g*)
    A3: Single scale a0 = g*(k_B T_grid / hbar omega0)^2

    Attributes:
        a0: Acceleration scale (m/s^2).
    """
    a0: float = A0_SPARC

    def mu(self, g: float) -> float:
        """Gravitational enhancement factor. Eq. (7)."""
        x = math.sqrt(g / self.a0)
        if x > 500:
            return math.exp(-x)
        return 1.0 / (math.expm1(x))

    def g_eff(self, g_bar: float) -> float:
        """Effective gravitational acceleration: g_eff = g_bar * (1 + mu(g_bar))."""
        return g_bar * (1.0 + self.mu(g_bar))

    def rar_curve(self, g_bar_values: List[float]) -> List[dict]:
        """Compute RAR for array of baryonic accelerations."""
        return [
            {
                "g_bar": g,
                "mu": self.mu(g),
                "g_obs": self.g_eff(g),
                "g_obs_over_g_bar": 1.0 + self.mu(g)
            }
            for g in g_bar_values
        ]

    def asymptotic_limits(self, g: float) -> dict:
        """Show asymptotic behaviour in different regimes."""
        x = math.sqrt(g / self.a0)
        return {
            "g": g,
            "x": x,
            "regime": "deep MOND" if x < 0.1 else ("Newtonian" if x > 3 else "transition"),
            "mu_exact": self.mu(g),
            "mu_deep_mond_approx": 1.0 / x if x > 0 else float('inf'),
            "mu_newtonian_approx": math.exp(-x),
            "note_deep_mond": "mu ~ 1/x ~ sqrt(a0/g): standard MOND limit",
            "note_newtonian": "mu ~ exp(-sqrt(g/a0)): exponentially suppressed"
        }


@dataclass
class LatticeDerivation:
    """Lattice derivation of E proportional to sqrt(g).

    Two adjacent grid nodes separated by l_g. A bosonic mode
    displaced by xi from equilibrium experiences restoring force
    from gravitational gradient:

    Delta F = -(g/l_g) * xi   (Hooke's law with k_eff = g/l_g)
    omega = sqrt(k_eff / m_eff) = sqrt(g / (m_eff * l_g))
    E = hbar * omega proportional to sqrt(g)

    Attributes:
        l_g: Lattice spacing (m).
        m_eff: Effective mode mass (kg).
    """
    l_g: float = 1.0      # lattice spacing (normalised)
    m_eff: float = 1.0     # effective mass (normalised)

    def spring_constant(self, g: float) -> float:
        """Effective spring constant k_eff = g/l_g. Eq. (10)."""
        return g / self.l_g

    def mode_frequency(self, g: float) -> float:
        """Mode frequency omega = sqrt(k_eff / m_eff). Eq. (11)."""
        k = self.spring_constant(g)
        return math.sqrt(k / self.m_eff)

    def excitation_energy(self, g: float) -> float:
        """Excitation energy E = hbar * omega (in normalised units)."""
        return self.mode_frequency(g)  # hbar=1 in normalised units

    def verify_sqrt_scaling(self, g_values: List[float]) -> List[dict]:
        """Verify that E scales as sqrt(g)."""
        results = []
        for g in g_values:
            E = self.excitation_energy(g)
            sqrt_g = math.sqrt(g)
            ratio = E / sqrt_g if sqrt_g > 0 else float('inf')
            results.append({
                "g": g,
                "E": E,
                "sqrt_g": sqrt_g,
                "E_over_sqrt_g": ratio,
                "constant_ratio": True  # by construction
            })
        return results


@dataclass
class MicrophysicalBridge:
    """The complete bridge from grid DOF to RAR.

    Chain (Eq. 14):
    Grid DOF -> gradient coupling -> E ~ sqrt(g) -> BE stats -> mu(g) -> G_eff -> RAR

    Also provides the KT3 resolution pathway:
    Statistical occupation (not classical operator) should restore beta=0.5.
    """
    a0: float = A0_SPARC
    rar: BoseEinsteinRAR = field(default=None)
    lattice: LatticeDerivation = field(default=None)

    def __post_init__(self):
        if self.rar is None:
            self.rar = BoseEinsteinRAR(a0=self.a0)
        if self.lattice is None:
            self.lattice = LatticeDerivation()

    def full_chain(self, g: float) -> dict:
        """Execute the complete derivation chain for a given g."""
        node = GridNode(g_local=g, a0=self.a0)
        return {
            "input_g": g,
            "step1_gradient_coupling": f"E proportional to sqrt(g) = sqrt({g:.2e})",
            "step2_energy_ratio": node.excitation_energy_ratio,
            "step3_be_occupation": node.occupation_number,
            "step4_mu": node.mu,
            "step5_g_eff": g * (1.0 + node.mu),
            "step6_enhancement": 1.0 + node.mu,
            "chain": "Grid DOF -> E~sqrt(g) -> BE -> mu -> G_eff -> RAR"
        }

    def kt3_resolution(self, M_solar_masses: float) -> dict:
        """Predict transition radius via statistical occupation.

        The condition <n> ~ 1 gives g_trans ~ a0, therefore
        r_trans ~ sqrt(G*M/a0) — the MOND scaling that KT3 misses.
        """
        M_kg = M_solar_masses * 1.989e30
        g_trans = self.a0
        r_trans = math.sqrt(G_N * M_kg / self.a0)
        r_kpc = r_trans / 3.086e19
        return {
            "M_solar": M_solar_masses,
            "g_trans_m_s2": g_trans,
            "r_trans_m": r_trans,
            "r_trans_kpc": r_kpc,
            "beta_predicted": 0.5,
            "beta_classical_KT3": 0.29,
            "mechanism": "Statistical occupation imposes local gradient scale, not bulk Lambda-scale",
            "scaling": "r_trans ~ sqrt(G*M/a0) follows from <n>~1 condition"
        }

    def macro_micro_comparison(self) -> dict:
        """Compare macro (EFT) and micro (grid) descriptions."""
        return {
            "macro_framework": {
                "source": "Covariant EFT (DOI: 10.6084/m9.figshare.31878334)",
                "results": [
                    "c_gw = c exactly (theorem)",
                    "eta approx 1 with O(Phi*mu) suppression",
                    "Solar system screening (exponential amplitude suppression)",
                    "Ghost-free, tachyon-free, hyperbolic",
                    "RAR = Bose-Einstein occupation number (form identified)"
                ],
                "gap": "Classical field equation gives correction INCREASING with acceleration"
            },
            "micro_model": {
                "source": "This paper (DOI: 10.6084/m9.figshare.31878760)",
                "results": [
                    "Gradient-coupled excitation energy: E ~ sqrt(g)",
                    "BE statistics produce mu(g) = 1/(exp(sqrt(g/a0))-1)",
                    "Correction DECREASING with acceleration (as required)",
                    "Single observable scale a0 from grid parameters",
                    "Lattice derivation: k_eff = g/l_g -> omega ~ sqrt(g)"
                ],
                "gap_status": "CLOSED (kinematic bridge established)"
            },
            "bridge": "Grid DOF -> E~sqrt(g) -> BE stats -> mu(g) -> G_eff -> RAR"
        }


@dataclass
class FalsificationCondition:
    """Falsification conditions for the microphysical model."""

    id: str
    condition: str
    test: str

    @staticmethod
    def all_conditions() -> list:
        return [
            FalsificationCondition(
                id="FC1",
                condition="mu must have exact BE form — not FD, not Boltzmann, not power law",
                test="Deviation from BE at ≤5% galaxy-survey precision"
            ),
            FalsificationCondition(
                id="FC2",
                condition="Coupling variable must be g = |nabla Phi|, not rho, Phi, or other",
                test="Evidence for density- or potential-dependent mu would falsify"
            ),
            FalsificationCondition(
                id="FC3",
                condition="E must scale as sqrt(g), i.e. alpha = 1/2 exactly",
                test="Grid Hamiltonian yielding alpha != 1/2 would falsify"
            ),
            FalsificationCondition(
                id="FC4",
                condition="KT3 should recover beta=0.5 with statistical occupation",
                test="Numerical test within existing GRAV pipeline"
            ),
        ]


# ─── Convenience functions ─────────────────────────────────────────

def compute_excitation_energy(g: float, a0: float = A0_SPARC) -> float:
    """Compute dimensionless excitation energy ratio E/(k_B T) = sqrt(g/a0)."""
    return math.sqrt(g / a0)


def compute_mu(g: float, a0: float = A0_SPARC) -> float:
    """Compute gravitational enhancement mu(g) = 1/(exp(sqrt(g/a0))-1)."""
    x = math.sqrt(g / a0)
    if x > 500:
        return math.exp(-x)
    return 1.0 / (math.expm1(x))


def compute_spring_constant(g: float, l_g: float = 1.0) -> float:
    """Compute effective spring constant k_eff = g/l_g from lattice derivation."""
    return g / l_g


def compute_transition_radius(M_kg: float, a0: float = A0_SPARC) -> float:
    """Compute MOND transition radius r_trans = sqrt(G*M/a0) in metres."""
    return math.sqrt(G_N * M_kg / a0)
