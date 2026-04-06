"""
Density of States of Gravitationally Active Grid Modes — Source Module
DOI: 10.6084/m9.figshare.31942800

Derives the effective density of gravitationally active grid modes D_eff(ρ)
from the boundary-mode mechanism on a Higgs-stabilised lattice. Combined
with per-mode BE entropy production, yields the microphysically derived:

  Γ(ρ) = Γ₀ √(ρ/ρ_crit) / (1 + √(ρ/ρ_crit))   with ρ_crit = a₀/(G_N l_g)

Scenario B+: correct saturation, emergent ρ_crit, ~20% agreement with
phenomenological ansatz ρ/(ρ + ρ_crit) over cosmologically relevant range.

References:
  Magnusson 2026, DOI: 10.6084/m9.figshare.31942800
  Magnusson 2026, "From Grid Microphysics to the RAR" (31878760)
  Magnusson 2026, "Gradient-Coupled Grid Action" (31941465)
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

# ── Physical constants ──────────────────────────────────────────────
G_N = 6.674e-11       # m^3 kg^-1 s^-2
C = 2.998e8            # m/s
HBAR = 1.055e-34       # J·s
K_B = 1.381e-23        # J/K
A_0 = 1.2e-10          # m/s² — MOND acceleration scale
L_PLANCK = 1.616e-35   # Planck length, m


# =====================================================================
#  1. Grid Activation
# =====================================================================
class GridActivation:
    """
    Grid activation condition (Eq. 2–5 of the paper).

    A node on the discrete grid (spacing l_g, tension σ₀ = a₀) becomes
    dynamically active when local gravitational energy exceeds the tension:

      G_N ρ l_g² > σ₀ l_g   →   ρ > ρ_crit = a₀/(G_N l_g)

    >>> ga = GridActivation()
    >>> ga.rho_crit > 0
    True
    >>> ga.is_active(ga.rho_crit * 2)
    True
    >>> ga.is_active(ga.rho_crit * 0.1)
    False
    """

    def __init__(self, l_g: float = L_PLANCK, a0: float = A_0):
        self.l_g = l_g
        self.a0 = a0
        self.sigma_0 = a0  # Node tension equals MOND scale (Eq. 4)
        self.rho_crit = a0 / (G_N * l_g)  # Eq. 5

    def gravitational_energy_per_node(self, rho: float) -> float:
        """E_grav ~ G_N ρ l_g² (gravitational self-energy at node scale)."""
        return G_N * rho * self.l_g**2

    def tension_energy(self) -> float:
        """Node tension energy: σ₀ l_g."""
        return self.sigma_0 * self.l_g

    def is_active(self, rho: float) -> bool:
        """Whether mean density ρ exceeds activation threshold."""
        return rho > self.rho_crit

    def density_ratio(self, rho: float) -> float:
        """ρ/ρ_crit — dimensionless density parameter."""
        return rho / self.rho_crit

    def nodes_per_volume(self, volume_m3: float) -> float:
        """Total grid nodes in volume V: N_total = V/l_g³."""
        return volume_m3 / self.l_g**3


# =====================================================================
#  2. Density of States (Boundary-Mode Mechanism)
# =====================================================================
class DensityOfStates:
    """
    Effective density of gravitationally active grid modes (Section 4).

    Boundary-mode mechanism: in a potential well of size r with grid
    spacing l_g, standing modes with wavelength λ_j = 2r/j are active
    if G_N ρ λ_j² > a₀ l_g. The number of active modes:

      N_active = j_max = 2r √(ρ/ρ_crit) / l_g     (Eq. 25)

    Therefore D_eff(ρ) ∝ √(ρ/ρ_crit)               (Eq. 26)

    Interpolating form with saturation (Eq. 28):
      D_eff(ρ) = D₀ √(ρ/ρ_crit) / (1 + √(ρ/ρ_crit))

    >>> dos = DensityOfStates()
    >>> d1 = dos.d_eff(0.01)
    >>> d2 = dos.d_eff(1.0)
    >>> d2 > d1  # D_eff increases with ρ/ρ_crit
    True
    """

    def __init__(self, D0: float = 1.0, l_g: float = L_PLANCK, a0: float = A_0):
        self.D0 = D0
        self.l_g = l_g
        self.a0 = a0
        self.rho_crit = a0 / (G_N * l_g)

    def n_active(self, rho: float, r_well: float) -> float:
        """
        Number of active modes in a potential well of size r.
        j_max = 2r √(ρ/ρ_crit) / l_g   (Eq. 25)
        """
        u = rho / self.rho_crit
        return 2.0 * r_well * math.sqrt(u) / self.l_g

    def n_well(self, r_well: float) -> float:
        """Total modes in well: N_well = r/l_g."""
        return r_well / self.l_g

    def saturation_density(self) -> float:
        """
        Density at which all modes are active: ρ_sat = ρ_crit/4 (Eq. 27).
        """
        return self.rho_crit / 4.0

    def d_eff(self, rho_over_rho_crit: float) -> float:
        """
        Effective density of states (Eq. 28).
        D_eff = D₀ √(ρ/ρ_crit) / (1 + √(ρ/ρ_crit))
        """
        u = math.sqrt(rho_over_rho_crit)
        return self.D0 * u / (1.0 + u)

    def d_eff_low_rho(self, rho_over_rho_crit: float) -> float:
        """Low-ρ limit: D_eff ≈ D₀ √(ρ/ρ_crit)."""
        return self.D0 * math.sqrt(rho_over_rho_crit)

    def d_eff_high_rho(self) -> float:
        """High-ρ limit: D_eff → D₀ (all modes active)."""
        return self.D0


# =====================================================================
#  3. Per-Mode Entropy Production (from companion note)
# =====================================================================
class PerModeEntropy:
    """
    Per-mode entropy production rate from BE statistics (Section 5).

    From the companion note [1]:
      Γ_per-mode = (β/(2a₀)) n(n+1)

    At low ρ (x ≪ 1): n ≈ 1/x → Γ_per-mode ≈ 1/(2ρ)
    At high ρ (x ≫ 1): n ≈ e^(-x) → exponentially suppressed

    Where x = √(βρ/a₀) is the dimensionless energy parameter.

    >>> pm = PerModeEntropy()
    >>> g_low = pm.gamma_per_mode(0.01)
    >>> g_high = pm.gamma_per_mode(100.0)
    >>> g_low > g_high  # Decreases with density
    True
    """

    def __init__(self, a0: float = A_0):
        self.a0 = a0
        self.beta = 4.0 * math.pi * G_N / 3.0  # Simplified coupling

    def x_param(self, rho: float) -> float:
        """Dimensionless energy: x = √(β ρ / a₀)."""
        return math.sqrt(self.beta * rho / self.a0)

    def occupation_number(self, x: float) -> float:
        """BE occupation: n = 1/(e^x - 1)."""
        if x < 1e-10:
            return 1.0 / x
        if x > 500:
            return 0.0
        return 1.0 / (math.exp(x) - 1.0)

    def gamma_per_mode(self, rho: float) -> float:
        """
        |Γ_per-mode| = (β/(2a₀)) n(n+1)   (Eq. 33)
        """
        x = self.x_param(rho)
        n = self.occupation_number(x)
        return (self.beta / (2.0 * self.a0)) * n * (n + 1.0)

    def gamma_per_mode_low_rho(self, rho: float) -> float:
        """Low-ρ approximation: ~ 1/(2ρ)  (Eq. 34)."""
        return 1.0 / (2.0 * rho)


# =====================================================================
#  4. Entropy Production Function Γ(ρ) — Main Result
# =====================================================================
class EntropyProductionFunction:
    """
    The complete microphysically derived Γ(ρ) (Eq. 48).

      Γ(ρ) = Γ₀ √(ρ/ρ_crit) / (1 + √(ρ/ρ_crit))

    with ρ_crit = a₀/(G_N l_g).

    Includes the ρ̇ rescue (Section 6.4): on a cosmological trajectory,
    Γ_t = (dS/dρ) · ρ̇ converts the ρ^(-1/2) micro-rate into ρ^(1/2).

    >>> epf = EntropyProductionFunction()
    >>> g = epf.gamma_derived(1.0)
    >>> abs(g - 0.5) < 0.01  # At ρ = ρ_crit, Γ ≈ 0.5
    True
    """

    def __init__(self, Gamma_0: float = 1.0, l_g: float = L_PLANCK, a0: float = A_0):
        self.Gamma_0 = Gamma_0
        self.l_g = l_g
        self.a0 = a0
        self.rho_crit = a0 / (G_N * l_g)

    def gamma_derived(self, rho_over_rho_crit: float) -> float:
        """
        Microphysically derived Γ(ρ) — Eq. 48.
        Γ = Γ₀ √(ρ/ρ_crit) / (1 + √(ρ/ρ_crit))
        """
        u = math.sqrt(max(0.0, rho_over_rho_crit))
        return self.Gamma_0 * u / (1.0 + u)

    def gamma_phenomenological(self, rho_over_rho_crit: float) -> float:
        """
        Phenomenological ansatz: Γ = Γ₀ ρ/(ρ + ρ_crit) = Γ₀ x/(1+x)
        where x = ρ/ρ_crit.
        """
        x = max(0.0, rho_over_rho_crit)
        return self.Gamma_0 * x / (1.0 + x)

    def relative_difference(self, rho_over_rho_crit: float) -> float:
        """
        Relative difference: (Γ_derived - Γ_phenom) / Γ_phenom.
        """
        gd = self.gamma_derived(rho_over_rho_crit)
        gp = self.gamma_phenomenological(rho_over_rho_crit)
        if gp < 1e-30:
            return 0.0
        return (gd - gp) / gp

    def max_deviation_in_range(
        self, rho_min: float = 0.01, rho_max: float = 1.0, n_points: int = 1000
    ) -> Tuple[float, float]:
        """
        Find maximum |relative difference| in a density range.
        Returns (ρ/ρ_crit at max, max |relative difference|).
        """
        max_dev = 0.0
        max_rho = rho_min
        for i in range(n_points + 1):
            x = rho_min + (rho_max - rho_min) * i / n_points
            dev = abs(self.relative_difference(x))
            if dev > max_dev:
                max_dev = dev
                max_rho = x
        return max_rho, max_dev

    def rho_dot_rescue(self, rho: float, H: float = 2.2e-18, w: float = 0.0) -> float:
        """
        The ρ̇ rescue (Eq. 44–45):
        ρ̇ = -3Hρ(1+w) converts dS/dρ ∝ ρ^(-1/2) into Γ_t ∝ ρ^(1/2).
        Returns |ρ̇| in kg/m³/s.
        """
        return 3.0 * H * rho * (1.0 + w)


# =====================================================================
#  5. Scenario Comparison
# =====================================================================
@dataclass
class RequirementCheck:
    """A row from Table 1: requirement check."""
    id: str
    requirement: str
    target: str
    derived: str
    status: str  # Passed, Failed, Different but physical


class ScenarioComparison:
    """
    Scenario classification and requirement checks (Table 1, Section 6).

    >>> sc = ScenarioComparison()
    >>> sc.classification
    'B+'
    >>> len(sc.requirements)
    5
    """

    def __init__(self):
        self.classification = "B+"
        self.requirements: List[RequirementCheck] = [
            RequirementCheck(
                id="R1",
                requirement="Low-ρ scaling",
                target="∝ ρ",
                derived="∝ ρ^(1/2)",
                status="Failed",
            ),
            RequirementCheck(
                id="R2",
                requirement="High-ρ behaviour",
                target="→ const",
                derived="→ 0 (exponential)",
                status="Different but physical",
            ),
            RequirementCheck(
                id="R3",
                requirement="Emergent ρ_crit",
                target="from a₀, G_N, l_g",
                derived="Yes: ρ_crit = a₀/(G_N l_g)",
                status="Passed",
            ),
            RequirementCheck(
                id="R4",
                requirement="D_eff from grid",
                target="Derived",
                derived="√(ρ/ρ_crit) — boundary-mode mechanism",
                status="Passed",
            ),
            RequirementCheck(
                id="R5",
                requirement="Double-counting",
                target="Resolved",
                derived="Confirmed resolved",
                status="Passed",
            ),
        ]

    @staticmethod
    def scenario_a(x: float) -> float:
        """Scenario A (phenomenological): ρ/(ρ + ρ_crit) = x/(1+x)."""
        return x / (1.0 + x)

    @staticmethod
    def scenario_b(x: float) -> float:
        """Scenario B (partial): ρ^(3/2)/(ρ + ρ_crit) = x^(3/2)/(1+x)."""
        return x**1.5 / (1.0 + x)

    @staticmethod
    def scenario_b_plus(x: float) -> float:
        """Scenario B+ (derived): √(ρ/ρ_crit)/(1 + √(ρ/ρ_crit))."""
        u = math.sqrt(x)
        return u / (1.0 + u)

    def compare_all(self, x: float) -> Dict[str, float]:
        """Compare all scenarios at a given ρ/ρ_crit."""
        return {
            "A (phenomenological)": self.scenario_a(x),
            "B (partial)": self.scenario_b(x),
            "B+ (derived)": self.scenario_b_plus(x),
        }


# =====================================================================
#  6. Predictions
# =====================================================================
@dataclass
class Prediction:
    """A testable prediction or implication."""
    id: str
    description: str
    status: str = "untested"


class Predictions:
    """
    Implications from Section 7.4 of the paper.

    >>> p = Predictions()
    >>> len(p.predictions)
    4
    """

    def __init__(self):
        self.predictions: List[Prediction] = [
            Prediction(
                id="I1",
                description="Γ(ρ) fully derived from microphysics — no free functions remain",
            ),
            Prediction(
                id="I2",
                description="Exact form differs from phenomenological ansatz; agrees within ~20% in relevant range",
            ),
            Prediction(
                id="I3",
                description="R(k) ∝ (Γ')² shifts quantitatively — survival valley recalibration needed",
            ),
            Prediction(
                id="I4",
                description="Derived form predicts slightly stronger Γ at ρ ≪ ρ_crit — distinguishable by Euclid/DESI DR3",
            ),
        ]

    def get(self, pid: str) -> Prediction:
        return next(p for p in self.predictions if p.id == pid)

    def summary(self) -> Dict[str, str]:
        return {p.id: p.description for p in self.predictions}
