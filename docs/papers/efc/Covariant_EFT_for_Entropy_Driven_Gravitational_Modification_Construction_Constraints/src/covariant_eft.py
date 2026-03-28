"""
Reference implementation: Covariant EFT for Entropy-Driven Gravitational Modification
Derivation, Falsification, and Structural Results from a 17-Iteration Construction Programme

Paper: Magnusson (2026), DOI: 10.6084/m9.figshare.31878334
Pedagogical implementation, not production-ready.
"""

from dataclasses import dataclass, field
from typing import List, Tuple
import numpy as np


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

a0 = 1.2e-10  # m/s^2, SPARC acceleration scale
G_N = 6.674e-11  # m^3 kg^-1 s^-2


# ---------------------------------------------------------------------------
# Bose-Einstein RAR (Structural Result V)
# ---------------------------------------------------------------------------

@dataclass
class BoseEinsteinRAR:
    """The RAR as Bose-Einstein occupation number (Eq. 2, 12).
    mu(g) = 1 / (exp(sqrt(g/a0)) - 1)
    """
    a0: float = 1.2e-10  # acceleration scale

    def mu(self, g: float) -> float:
        """Gravitational enhancement factor."""
        x = np.sqrt(np.abs(g) / self.a0)
        if x > 700:
            return np.exp(-x)  # avoid overflow
        return 1.0 / (np.exp(x) - 1.0)

    def mu_array(self, g: np.ndarray) -> np.ndarray:
        """Vectorised mu(g)."""
        x = np.sqrt(np.abs(g) / self.a0)
        result = np.where(x > 700, np.exp(-x), 1.0 / (np.exp(x) - 1.0))
        return result

    def g_obs(self, g_bar: float) -> float:
        """Eq. 1: g_obs = g_bar / (1 - exp(-sqrt(g_bar/a0)))"""
        x = np.sqrt(g_bar / self.a0)
        return g_bar / (1.0 - np.exp(-x))

    def G_eff(self, g: float) -> float:
        """Eq. 15: G_eff(g) = G_N * (1 + mu(g))"""
        return G_N * (1.0 + self.mu(g))


# ---------------------------------------------------------------------------
# Action
# ---------------------------------------------------------------------------

@dataclass
class CovEFTAction:
    """The EFC covariant action (Eq. 3).
    S = int d^4x sqrt(-g) [R/16piG + (1/2)(dS)^2 - V(S) - beta|dS|_eps S^2 + L_m]
    """
    beta: float = 1.0       # gradient-field coupling
    m_S: float = 1e-28      # field mass in eV (~50 kpc screening length)
    epsilon: float = 1e-30   # regulariser (vacuum floor)
    S0: float = 1.0          # potential minimum

    def V(self, S: float) -> float:
        """Quadratic potential V(S) = (1/2) m_S^2 (S - S0)^2"""
        return 0.5 * self.m_S ** 2 * (S - self.S0) ** 2

    def V_prime(self, S: float) -> float:
        return self.m_S ** 2 * (S - self.S0)

    def grad_norm_reg(self, dS: float) -> float:
        """|dS|_eps = sqrt(dS^2 + eps^2)"""
        return np.sqrt(dS ** 2 + self.epsilon ** 2)

    def departures_from_GR(self) -> List[str]:
        return [
            "One scalar field S with gradient-field coupling -beta|dS|S^2",
            "No f(S)R coupling — minimal coupling to gravity",
            "No higher-curvature terms, no Riemann coupling",
        ]


# ---------------------------------------------------------------------------
# Structural Result II: Gravitational Slip
# ---------------------------------------------------------------------------

@dataclass
class GravitationalSlip:
    """Eq. 9: eta = 1 + O(Phi * mu)
    Structural cancellation in T_rr leaves O(Phi) suppression."""

    def eta(self, Phi: float, mu: float) -> float:
        """Approximate slip. Exact value depends on detailed field configuration."""
        return 1.0 + Phi * mu

    def eta_deviation(self, Phi: float, mu: float) -> float:
        """|eta - 1| = O(Phi * mu)"""
        return abs(Phi * mu)


# ---------------------------------------------------------------------------
# Structural Result III: Solar System Compatibility
# ---------------------------------------------------------------------------

@dataclass
class SolarSystemTest:
    """Solar-system fifth-force suppression via exponential amplitude suppression."""
    rar: BoseEinsteinRAR = field(default_factory=BoseEinsteinRAR)

    LOCATIONS = [
        ("Sun surface", 274.0),
        ("Earth orbit", 5.9e-3),
        ("Saturn (Cassini)", 6.5e-5),
        ("Galaxy outskirts", 1.2e-10),
    ]

    def evaluate(self) -> List[Tuple[str, float, float, float]]:
        """Returns (name, g, sqrt(g/a0), mu) for each location."""
        results = []
        for name, g in self.LOCATIONS:
            x = np.sqrt(g / self.rar.a0)
            mu = self.rar.mu(g)
            results.append((name, g, x, mu))
        return results


# ---------------------------------------------------------------------------
# Structural Result IV: Stability
# ---------------------------------------------------------------------------

@dataclass
class StabilityAnalysis:
    """Ghost/tachyon/hyperbolicity analysis."""

    beta: float = 1.0
    S_bar: float = 1.0
    dS_bar: float = 1e-5
    epsilon: float = 1e-30
    m_S: float = 1e-28

    def Z(self) -> float:
        """Kinetic coefficient (Eq. 11): Z > 1 => no ghosts."""
        denom = (self.dS_bar ** 2 + self.epsilon ** 2) ** 1.5
        return 1.0 + self.beta * self.S_bar ** 2 * self.epsilon ** 2 / denom

    def m_eff_squared(self) -> float:
        """Effective mass squared: m_eff^2 > 0 => no tachyons."""
        return self.m_S ** 2 + 2.0 * self.beta * abs(self.dS_bar)

    def is_ghost_free(self) -> bool:
        return self.Z() > 0

    def is_tachyon_free(self) -> bool:
        return self.m_eff_squared() > 0

    def summary(self) -> dict:
        return {
            "Z": self.Z(),
            "ghost_free": self.is_ghost_free(),
            "m_eff_sq": self.m_eff_squared(),
            "tachyon_free": self.is_tachyon_free(),
            "hyperbolic": True,  # principal symbol = standard d'Alembertian
        }


# ---------------------------------------------------------------------------
# Self-Consistent Field Solution
# ---------------------------------------------------------------------------

@dataclass
class SelfConsistentSolution:
    """Tracking solution for S-field in NFW halo."""

    def tracking_deviation_without_potential(self) -> float:
        """v13 result: 225% deviation without potential."""
        return 2.25

    def tracking_deviation_with_potential(self) -> float:
        """v14 result: ~0.1% with V = (1/2) m_S^2 (S-S0)^2."""
        return 0.001

    def required_mass(self) -> float:
        """m_S ~ 10^-28 eV"""
        return 1e-28

    def screening_length(self) -> str:
        """lambda_S = 1/m_S ~ 50 kpc"""
        return "~50 kpc"


# ---------------------------------------------------------------------------
# 17-Iteration Programme
# ---------------------------------------------------------------------------

@dataclass
class ConstructionIteration:
    version: int
    test: str
    result: str
    passed: bool


ITERATIONS = [
    ConstructionIteration(1, "Wave-particle duality from grid+sampling", "Consistent", True),
    ConstructionIteration(2, "Particle-based measurement feedback", "Effect exists", True),
    ConstructionIteration(3, "Planck-scale coupling strength", "delta_rho ~ 10^-132; unmeasurable", True),
    ConstructionIteration(4, "Field-based continuous feedback", "Three regimes found", True),
    ConstructionIteration(5, "SI-unit mapping of coupling", "Grid is gravitational, not EM", True),
    ConstructionIteration(6, "RAR functional form", "Formally identical to Bose-Einstein", True),
    ConstructionIteration(7, "Which coupling reproduces RAR", "Acceleration g uniquely", True),
    ConstructionIteration(8, "Covariant action construction", "Minimal action found", True),
    ConstructionIteration(9, "GW speed (first analysis)", "c_gw = c (argument)", True),
    ConstructionIteration(10, "Full quadratic action L(2)", "No dh.dh from F", True),
    ConstructionIteration(11, "Generalised Z-tensor, arbitrary dS_bar", "Speed isotropic", True),
    ConstructionIteration(12, "Phi/Psi slip derivation", "eta = 1 + O(Phi*mu)", True),
    ConstructionIteration(13, "Self-consistent S_bar(r), V=0", "Tracking fails (225%)", False),
    ConstructionIteration(14, "Derive V(S) from tracking", "V = (1/2) m_S^2 S^2 restores it", True),
    ConstructionIteration(15, "Screening mechanism", "BE amplitude suppression", True),
    ConstructionIteration(16, "Fifth force / PPN", "All constraints satisfied (exp. suppressed)", True),
    ConstructionIteration(17, "Modified Poisson from field equations", "T_00^S proportional to g (wrong direction)", False),
]


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def run_eft_demo():
    print("=" * 65)
    print("Covariant EFT for Entropy-Driven Gravitational Modification")
    print("=" * 65)

    # --- RAR / Bose-Einstein ---
    print("\n--- 1. RAR as Bose-Einstein (Structural Result V) ---")
    rar = BoseEinsteinRAR()
    g_values = np.logspace(-12, 3, 10)
    print(f"  {'g [m/s^2]':>14s}  {'sqrt(g/a0)':>12s}  {'mu(g)':>14s}  {'G_eff/G_N':>10s}")
    for g in g_values:
        x = np.sqrt(g / rar.a0)
        mu = rar.mu(g)
        geff = rar.G_eff(g) / G_N
        print(f"  {g:14.4e}  {x:12.2f}  {mu:14.6e}  {geff:10.6f}")

    # --- Action ---
    print("\n--- 2. EFC Covariant Action ---")
    action = CovEFTAction()
    print(f"  beta   = {action.beta}")
    print(f"  m_S    = {action.m_S:.0e} eV")
    print(f"  V(S=1.1) = {action.V(1.1):.4e}")
    print("  Departures from GR:")
    for d in action.departures_from_GR():
        print(f"    - {d}")

    # --- GW Speed (Structural Result I) ---
    print("\n--- 3. GW Speed (Structural Result I) ---")
    print("  c_gw = c exactly (theorem)")
    print("  Delta_c/c ~ 10^-54 (10^39 below GW170817 bound)")
    print("  Proof: No metric derivatives in F => tensor kinetic operator = GR")

    # --- Gravitational Slip (Structural Result II) ---
    print("\n--- 4. Gravitational Slip (Structural Result II) ---")
    slip = GravitationalSlip()
    for Phi, mu_val in [(1e-6, 1.0), (1e-6, 0.1), (1e-4, 0.5)]:
        dev = slip.eta_deviation(Phi, mu_val)
        print(f"  Phi={Phi:.0e}, mu={mu_val:.1f}  =>  |eta-1| = {dev:.2e}")

    # --- Solar System (Structural Result III) ---
    print("\n--- 5. Solar-System Compatibility (Structural Result III) ---")
    ss = SolarSystemTest()
    print(f"  {'Location':<20s} {'g [m/s^2]':>12s} {'sqrt(g/a0)':>12s} {'mu':>14s}")
    for name, g, x, mu in ss.evaluate():
        if mu < 1e-300:
            mu_str = "~0"
        else:
            mu_str = f"{mu:.4e}"
        print(f"  {name:<20s} {g:12.2e} {x:12.1f} {mu_str:>14s}")
    print("  -> Exponential suppression, not chameleon/Vainshtein screening")

    # --- Stability (Structural Result IV) ---
    print("\n--- 6. Stability (Structural Result IV) ---")
    stab = StabilityAnalysis()
    s = stab.summary()
    print(f"  Z = {s['Z']:.6f}  (ghost-free: {s['ghost_free']})")
    print(f"  m_eff^2 = {s['m_eff_sq']:.4e}  (tachyon-free: {s['tachyon_free']})")
    print(f"  Hyperbolic: {s['hyperbolic']}")

    # --- Self-consistent solution ---
    print("\n--- 7. Self-Consistent Field Solution ---")
    scs = SelfConsistentSolution()
    print(f"  Without potential (v13): tracking deviation = {scs.tracking_deviation_without_potential()*100:.0f}% (FAILS)")
    print(f"  With V = (1/2)m_S^2(S-S0)^2 (v14): deviation = {scs.tracking_deviation_with_potential()*100:.1f}% (OK)")
    print(f"  Required mass: m_S ~ {scs.required_mass():.0e} eV")
    print(f"  Screening length: {scs.screening_length()}")

    # --- Critical Gap ---
    print("\n--- 8. Critical Gap: Classical Limit Failure ---")
    print("  Classical T_00^(S) = beta S_0^2 kappa g / c^2")
    print("  => Correction INCREASES with g (wrong direction)")
    print("  RAR requires mu(g) -> 0 as g -> infinity (DECREASING)")
    print("  Diagnosis: BE form = quantum statistics, not classical limit")
    print("  Resolution: quantum treatment or non-local coupling")

    # --- 17-Iteration Programme ---
    print("\n--- 9. Construction Programme (17 Iterations) ---")
    passed = sum(1 for it in ITERATIONS if it.passed)
    failed = sum(1 for it in ITERATIONS if not it.passed)
    print(f"  Total: {len(ITERATIONS)}, Passed: {passed}, Failed: {failed}")
    for it in ITERATIONS:
        status = "PASS" if it.passed else "FAIL"
        print(f"  v{it.version:2d} [{status}] {it.test}: {it.result}")

    # --- Comparison table ---
    print("\n--- 10. EFC-EFT in Context ---")
    theories = [
        ("LCDM",      "2", "N/A",    "Yes",       "N/A"),
        ("MOND",      "1", "chosen", "N/A",       "Problematic"),
        ("TeVeS",     "3+", "vector", "constrained", "partial"),
        ("f(R)",      "1+", "from f", "constrained", "chameleon"),
        ("Horndeski", "2+", "from Gi", "mostly killed", "Vainshtein"),
        ("EFC-EFT",   "1", "BE",     "Yes (shown)", "automatic"),
    ]
    print(f"  {'Theory':<12s} {'Params':<8s} {'mu form':<10s} {'c_gw=c':<15s} {'Solar safe'}")
    for t in theories:
        print(f"  {t[0]:<12s} {t[1]:<8s} {t[2]:<10s} {t[3]:<15s} {t[4]}")

    print("\n" + "=" * 65)
    print("Demo complete.")


if __name__ == "__main__":
    run_eft_demo()
