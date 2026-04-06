"""
Derivation of Γ(ρ) from Grid-Mode Bose-Einstein Statistics — Source Module
DOI: 10.6084/m9.figshare.31942821

Derives the entropy production function Γ(ρ) from first principles:
  BE occupation n(g) → von Neumann entropy S[n] → chain rule dS/dρ

Result: Γ(ρ) ∝ ρ^(3/2) / (ρ + ρ_crit)  with ρ_crit = a₀/(G_N l_g)

Scenario B: correct qualitative structure, exponent 3/2 vs phenomenological 1.
Double-counting (μ_BE vs Γ) resolved: μ is static occupation, Γ is dynamical rate.

References:
  Magnusson 2026, DOI: 10.6084/m9.figshare.31942821
  Companion: Density of States (31942800) — upgrades to Scenario B+
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
#  1. BE Occupation Number
# =====================================================================
class BEOccupation:
    """
    Bose-Einstein occupation of grid modes (Eq. 1).

      n(g) = 1 / (exp(√(g/a₀)) - 1)

    Parametrised by dimensionless energy x = √(βρ/a₀) where β = 4πG_N r*/3.

    >>> be = BEOccupation()
    >>> n = be.occupation(x=0.1)
    >>> abs(n - 1/0.1) / (1/0.1) < 0.06  # n ≈ 1/x at small x
    True
    """

    def __init__(self, a0: float = A_0):
        self.a0 = a0

    def occupation(self, x: float) -> float:
        """n(x) = 1/(e^x - 1), the BE occupation number."""
        if x < 1e-10:
            return 1.0 / x
        if x > 500:
            return 0.0
        return 1.0 / (math.exp(x) - 1.0)

    def x_from_rho(self, rho: float, beta: float) -> float:
        """Dimensionless energy: x = √(βρ/a₀) (Eq. 4)."""
        return math.sqrt(beta * rho / self.a0)

    def dn_dx(self, x: float) -> float:
        """dn/dx = -e^x/(e^x - 1)² = -n(n+1) (Eq. 13)."""
        n = self.occupation(x)
        return -n * (n + 1.0)

    def dn_drho(self, x: float, rho: float) -> float:
        """dn/dρ = -n(n+1) · x/(2ρ) (Eq. 16)."""
        n = self.occupation(x)
        if rho < 1e-30:
            return 0.0
        return -n * (n + 1.0) * x / (2.0 * rho)

    def low_x_approx(self, x: float) -> float:
        """Low-x: n ≈ 1/x (quantum-degenerate regime)."""
        return 1.0 / x

    def high_x_approx(self, x: float) -> float:
        """High-x: n ≈ e^(-x) (classical regime)."""
        if x > 500:
            return 0.0
        return math.exp(-x)


# =====================================================================
#  2. Von Neumann Entropy
# =====================================================================
class VonNeumannEntropy:
    """
    Von Neumann entropy for a bosonic mode (Eq. 5-7).

      s(n) = (1+n)ln(1+n) - n ln(n)

    Key result (Eq. 11): ds/dn = ln(1+1/n) = x for BE distribution.
    The marginal entropy per mode equals the dimensionless energy.

    >>> vn = VonNeumannEntropy()
    >>> s = vn.entropy_per_mode(n=10.0)
    >>> s > 0
    True
    """

    @staticmethod
    def entropy_per_mode(n: float) -> float:
        """s(n) = (1+n)ln(1+n) - n ln(n) (Eq. 7)."""
        if n < 1e-30:
            return 0.0
        return (1.0 + n) * math.log(1.0 + n) - n * math.log(n)

    @staticmethod
    def entropy_from_x(x: float) -> float:
        """s(x) = x/(e^x - 1) - ln(1 - e^(-x)) (Planck entropy, Eq. 26)."""
        if x < 1e-10:
            return 1.0 - math.log(x) if x > 0 else 0.0
        if x > 500:
            return x * math.exp(-x)
        return x / (math.exp(x) - 1.0) - math.log(1.0 - math.exp(-x))

    @staticmethod
    def ds_dn(n: float) -> float:
        """ds/dn = ln(1 + 1/n) (Eq. 9)."""
        if n < 1e-30:
            return 0.0
        return math.log(1.0 + 1.0 / n)

    @staticmethod
    def ds_dn_for_BE(x: float) -> float:
        """
        For BE distribution: ds/dn = x exactly (Eq. 11).
        Key result: marginal entropy = dimensionless energy.
        """
        return x

    @staticmethod
    def verify_marginal_identity(x: float) -> float:
        """
        Verify ds/dn = x for BE distribution.
        Returns |ds/dn - x| / x (should be ~0).
        """
        if x < 1e-10 or x > 500:
            return 0.0
        n = 1.0 / (math.exp(x) - 1.0)
        ds = math.log(1.0 + 1.0 / n)
        return abs(ds - x) / x


# =====================================================================
#  3. Gamma Derivation (Main Result)
# =====================================================================
class GammaDerivation:
    """
    The complete Γ(ρ) derivation chain (Sections 3-4).

    Per-mode (Eq. 20):
      |Γ_per-mode| = (β/(2a₀)) n(n+1)

    With density-dependent mode activation D_eff = D₀ ρ/(ρ+ρ_crit):
      Γ_total(ρ) ∝ ρ^(3/2) / (ρ + ρ_crit)     (Eq. 37)

    >>> gd = GammaDerivation()
    >>> g = gd.gamma_total(1.0)
    >>> g > 0
    True
    """

    def __init__(self, Gamma_0: float = 1.0, a0: float = A_0):
        self.Gamma_0 = Gamma_0
        self.a0 = a0
        self.beta = 4.0 * math.pi * G_N / 3.0
        self._be = BEOccupation(a0)
        self._vn = VonNeumannEntropy()

    @property
    def rho_crit_over_beta(self) -> float:
        """ρ_crit = a₀/(G_N l_g). For dimensionless work, use ρ/ρ_crit."""
        return self.a0 / (G_N * L_PLANCK)

    def gamma_per_mode(self, x: float) -> float:
        """
        Per-mode entropy production |Γ| = (β/(2a₀)) n(n+1) (Eq. 20).
        """
        n = self._be.occupation(x)
        return (self.beta / (2.0 * self.a0)) * n * (n + 1.0)

    def d_eff(self, rho_ratio: float) -> float:
        """
        Density-dependent mode activation (Eq. 32):
        D_eff = D₀ ρ/(ρ + ρ_crit) = x/(1+x) where x = ρ/ρ_crit.
        """
        return rho_ratio / (1.0 + rho_ratio)

    def x_sx_product(self, x: float) -> float:
        """x · s(x) — appears in the total Γ expression (Eq. 28)."""
        s = self._vn.entropy_from_x(x)
        return x * s

    def gamma_total(self, rho_ratio: float) -> float:
        """
        Total Γ(ρ) ∝ ρ^(3/2)/(ρ + ρ_crit) (Eq. 37).
        Normalised: Γ₀ at ρ = ρ_crit.

        Uses ρ/ρ_crit as input (dimensionless).
        """
        if rho_ratio <= 0:
            return 0.0
        return self.Gamma_0 * rho_ratio**1.5 / (1.0 + rho_ratio)

    def gamma_phenomenological(self, rho_ratio: float) -> float:
        """
        Phenomenological ansatz: Γ = Γ₀ ρ/(ρ + ρ_crit) = x/(1+x).
        """
        return self.Gamma_0 * rho_ratio / (1.0 + rho_ratio)

    def relative_difference(self, rho_ratio: float) -> float:
        """(Γ_derived - Γ_phenom) / Γ_phenom."""
        gd = self.gamma_total(rho_ratio)
        gp = self.gamma_phenomenological(rho_ratio)
        if gp < 1e-30:
            return 0.0
        return (gd - gp) / gp

    def derivation_chain(self, x: float) -> Dict[str, float]:
        """
        Show all intermediate quantities in the derivation chain for a given x.
        """
        n = self._be.occupation(x)
        s = self._vn.entropy_per_mode(n)
        ds_dn = self._vn.ds_dn(n)
        ds_dn_be = x  # The key identity
        dn_dx = -n * (n + 1)
        return {
            "x": x,
            "n(x)": n,
            "s(n)": s,
            "ds/dn": ds_dn,
            "ds/dn (BE identity)": ds_dn_be,
            "dn/dx": dn_dx,
            "n(n+1)": n * (n + 1),
        }


# =====================================================================
#  4. Double-Counting Resolution
# =====================================================================
class DoubleCounting:
    """
    Resolution of the μ_BE vs Γ double-counting concern (Section 1.2).

    μ_BE(g): static, local, instantaneous occupation number
    Γ(ρ): dynamical, rate of entropy change as distribution evolves

    Analogy: in a Bose gas, n̄(ε) → equation of state, dS/dt → relaxation dynamics.
    Both from same statistics; neither redundant.

    >>> dc = DoubleCounting()
    >>> dc.mu_be(x=1.0) == dc.occupation(x=1.0)
    True
    """

    def __init__(self, a0: float = A_0):
        self.a0 = a0

    @staticmethod
    def occupation(x: float) -> float:
        """n(x) = 1/(e^x - 1) — the BE occupation number."""
        if x < 1e-10:
            return 1.0 / x
        if x > 500:
            return 0.0
        return 1.0 / (math.exp(x) - 1.0)

    def mu_be(self, x: float) -> float:
        """
        μ_BE(g) = n(x): gravitational response (static, local).
        Determines equation of state / gravitational coupling.
        """
        return self.occupation(x)

    def gamma_rate(self, x: float) -> float:
        """
        Γ contribution ∝ n(n+1): entropy production rate (dynamical).
        Determines relaxation dynamics.
        """
        n = self.occupation(x)
        return n * (n + 1.0)

    def are_distinct(self, x: float) -> bool:
        """μ and Γ differ unless n(n+1) = n, i.e. n = 0 (trivial)."""
        n = self.occupation(x)
        return abs(n * (n + 1) - n) > 1e-10


# =====================================================================
#  5. Scenario Classification
# =====================================================================
@dataclass
class RequirementCheck:
    """A row from Table 1."""
    id: str
    target: str
    result: str
    status: str  # Yes, Partial, No, Resolved


class ScenarioClassification:
    """
    Scenario B classification and requirement checks (Table 1).

    >>> sc = ScenarioClassification()
    >>> sc.scenario
    'B'
    >>> len(sc.requirements)
    4
    """

    def __init__(self):
        self.scenario = "B"
        self.requirements: List[RequirementCheck] = [
            RequirementCheck(
                id="R1",
                target="Γ ∝ ρ at low density",
                result="Γ ∝ ρ^(3/2) — exponent 3/2, not 1",
                status="Partial",
            ),
            RequirementCheck(
                id="R2",
                target="Γ → const at high density",
                result="Γ ∝ ρ^(1/2) — slow growth, not saturation",
                status="Partial",
            ),
            RequirementCheck(
                id="R3",
                target="ρ_crit from microphysics",
                result="ρ_crit = a₀/(G_N l_g) — emergent",
                status="Yes",
            ),
            RequirementCheck(
                id="DC",
                target="μ ≠ Γ (no double-counting)",
                result="μ is static occupation; Γ is dynamical rate",
                status="Resolved",
            ),
        ]

    def path_to_scenario_a(self) -> List[str]:
        """Steps needed to upgrade from Scenario B to A."""
        return [
            "(i) Derive D_eff(ρ) from the grid action (done: companion paper 31942800 → B+)",
            "(ii) Recalibrate survival valley with Γ ∝ ρ^(3/2)/(ρ+ρ_crit)",
        ]


# =====================================================================
#  6. Predictions
# =====================================================================
@dataclass
class Prediction:
    id: str
    description: str
    status: str = "structural"


class Predictions:
    """
    Structural implications from the derivation (Section 6).

    >>> p = Predictions()
    >>> len(p.predictions)
    4
    """

    def __init__(self):
        self.predictions: List[Prediction] = [
            Prediction(
                id="S1",
                description="Γ(ρ) is derived, not postulated — from BE + vN entropy + mode activation",
            ),
            Prediction(
                id="S2",
                description="ρ_crit = a₀/(G_N l_g) — testable: given a₀ and l_g, ρ_crit is fixed",
            ),
            Prediction(
                id="S3",
                description="Cosmological predictions shift quantitatively with ρ^(3/2) vs ρ exponent",
            ),
            Prediction(
                id="S4",
                description="R(k) acquires slow density dependence at high ρ (ρ^(1/2) vs const)",
            ),
        ]

    def get(self, pid: str) -> Prediction:
        return next(p for p in self.predictions if p.id == pid)

    def summary(self) -> Dict[str, str]:
        return {p.id: p.description for p in self.predictions}
