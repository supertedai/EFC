"""
Cosmology Model — Ontological Abstraction Layer

Decouples physics engines (Hubble, Growth ODE) from cosmological assumptions
(flatness, curvature, gate parameters, dark energy equation of state, etc.).

Each CosmologyModel encapsulates:
    - E²(a) = H²(a) / H0²  (background expansion)
    - d(E²)/da              (needed for growth ODE friction)
    - Growth source term     (Poisson side of growth ODE)
    - assumptions dict       (ontological audit, logged per MCMC cycle)

Models:
    FlatLCDM     — Standard flat ΛCDM. Makes implicit LCDM assumptions explicit.
    EFCVariantA  — EFC with logistic-gated α deformation of E²(a).
                   Gate parameters (a_t, δ_a) are owned by the model,
                   eliminating duplication between hubble.py and growth.py.
    EFCVariantB  — EFC with FREE gate parameters (a_t, δ_a read from params dict).
                   Tests whether α survives gate freedom — key internal EFC test.
    EFCVariantC  — EFC VariantA expansion + modified Poisson (μ ≠ 1).
                   μ(a) = 1 + (μ_0 − 1) · g(a) — late-time gravitational coupling.
                   Tests whether EFC modifies structure formation, not just expansion.
    EFCVariantE  — EFC with power-law gate g(a) = 1/(1+(a_t/a)^n), n=2 locked
                   from Lorentzian W(k) in L0. Ontologically correct gate form.
                   Core Derivation Note v0.2, Eq. (6)-(8).
    EFCVariantF  — EFC VariantA background + GRAV-locked G_eff growth source.
                   G_eff(k,a)/G = 1 + (C²−1)·gate(a)·screen(k) with C=2.32 frozen
                   from KT2. First coupling of discrete gravity to cosmological
                   likelihood. N7 "Domstolen" diagnostic.
    EFCVariantG  — Constitutive law: growth-only μ from entropy gradients.
                   Pure ΛCDM background, zero extra free parameters.
                   μ(z) = 1 + ε_eff·F(χ(z)) where χ = |dŜ/dz| from Axiom 0
                   and ε_eff = (C²−1)·screen(k_eff) from KT2.
                   Tests whether entropy-driven growth signal exists.

Usage:
    from efc_inference.core.cosmology_model import (
        EFCVariantA, EFCVariantB, EFCVariantC, EFCVariantE, EFCVariantF,
        EFCVariantG, FlatLCDM
    )

    model = EFCVariantA()          # default gate: a_t=0.5, δ_a=0.1
    model = EFCVariantA(a_t=0.6)   # custom gate transition
    model = EFCVariantB()          # gate params from MCMC params dict
    model = EFCVariantC()          # modified Poisson (μ ≠ 1)
    model = FlatLCDM()             # pure ΛCDM

    E2 = model.e_squared(a, {"Omega_m": 0.315, "alpha_cosmo": -0.995})
    E2 = model.e_squared(a, {"Omega_m": 0.315, "alpha_cosmo": -0.995,
                              "a_t": 0.45, "delta_a": 0.08})  # VariantB
    src = model.growth_source(a, {"Omega_m": 0.315, "alpha_cosmo": -0.995,
                                   "mu_0": 1.1})  # VariantC
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Mapping

import numpy as np


Params = Mapping[str, float]


def _as_array(a: Any) -> np.ndarray:
    """Ensure input is a float ndarray."""
    return np.asarray(a, dtype=float)


# ═══════════════════════════════════════════════════════════════
#  ABSTRACT BASE
# ═══════════════════════════════════════════════════════════════

class CosmologyModel(ABC):
    """
    Abstract cosmological model — ontology carrier + forward model.

    Contract:
        - e_squared(a, params)      → E²(a) = H²/H0²
        - de_squared_da(a, params)  → d(E²)/da
        - growth_source(a, params)  → source term for growth ODE
        - name                      → identifier for logging
        - assumptions               → audit dict (logged per run in Neo4j)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Model identifier for logging/Neo4j."""
        ...

    @property
    @abstractmethod
    def assumptions(self) -> Dict[str, Any]:
        """Ontological assumptions dict for audit trail."""
        ...

    @abstractmethod
    def e_squared(self, a: Any, params: Params) -> np.ndarray:
        """E²(a) = H²(a) / H0². Core background expansion equation."""
        ...

    @abstractmethod
    def de_squared_da(self, a: Any, params: Params) -> np.ndarray:
        """d(E²)/da — needed for growth ODE friction term."""
        ...

    @abstractmethod
    def growth_source(self, a: Any, params: Params) -> np.ndarray:
        """Source coefficient for growth ODE.

        Default (unmodified Poisson, μ=1):
            (3/2) · Ωm · a⁻³ / E²(a)
        """
        ...


# ═══════════════════════════════════════════════════════════════
#  FLAT ΛCDM
# ═══════════════════════════════════════════════════════════════

class FlatLCDM(CosmologyModel):
    """
    Standard flat FLRW ΛCDM with unmodified Poisson.

    E²(a) = Ωm · a⁻³ + (1 − Ωm)

    Makes all implicit LCDM assumptions explicit and loggable.
    """

    @property
    def name(self) -> str:
        return "flat_lcdm"

    @property
    def assumptions(self) -> Dict[str, Any]:
        return {
            "geometry": {"type": "FLRW", "curvature": "flat", "status": "assumed"},
            "redshift": {"formula": "a = 1/(1+z)", "status": "standard"},
            "propagation": {"c": "constant", "status": "implicit"},
            "sound_horizon": {"source": "planck_lcdm", "value_mpc": 147.09, "status": "proxy"},
            "poisson": {"mu": 1.0, "status": "unmodified"},
            "dark_energy": {"type": "cosmological_constant", "w": -1, "status": "assumed"},
        }

    def e_squared(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        return Om * a**(-3.0) + (1.0 - Om)

    def de_squared_da(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        return -3.0 * Om * a**(-4.0)

    def growth_source(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        E2 = self.e_squared(a, params)
        # (3/2) · Ωm / (a⁵ · E²)  —  unmodified Poisson (μ=1)
        return np.where(E2 > 0, 1.5 * Om / (a**5.0 * E2), 0.0)


# ═══════════════════════════════════════════════════════════════
#  EFC VARIANT A
# ═══════════════════════════════════════════════════════════════

class EFCVariantA(CosmologyModel):
    """
    EFC Variant A: LCDM background + gated flow coupling in E²(a).

    E²(a) = Ωm · a⁻³ + (1 − Ωm) + α · [g(a) − g(1)]

    where g(a) is a logistic gate:
        g(a) = 1 / (1 + exp(−(a − a_t) / δ_a))

    Normalization [g(a) − g(1)] ensures:
        - α does NOT change H(z=0)
        - LCDM is exact when α = 0

    Gate parameters are OWNED by this model (not duplicated in engine files).

    Parameters:
        a_t:      Scale factor at transition (default: 0.5, z ~ 1)
        delta_a:  Width of logistic gate (default: 0.1, smooth)
    """

    def __init__(self, a_t: float = 0.5, delta_a: float = 0.1):
        self._a_t = float(a_t)
        self._delta_a = float(delta_a)
        # Pre-compute gate at a=1 for normalization
        self._g1 = float(self._gate_scalar(1.0))

    @property
    def name(self) -> str:
        return "efc_variant_a"

    @property
    def assumptions(self) -> Dict[str, Any]:
        return {
            "geometry": {"type": "FLRW", "curvature": "flat", "status": "assumed"},
            "redshift": {"formula": "a = 1/(1+z)", "status": "standard"},
            "propagation": {"c": "constant", "status": "implicit"},
            "sound_horizon": {"source": "planck_lcdm", "value_mpc": 147.09, "status": "proxy"},
            "poisson": {"mu": 1.0, "status": "unmodified_mvp_g1"},
            "dark_energy": {"efc": "flow_coupling_alpha", "status": "primary_test_target"},
            "gate": {"a_t": self._a_t, "delta_a": self._delta_a, "status": "fixed_variant_a"},
        }

    # ── Gate functions (owned by model) ──────────────────────

    def _gate_scalar(self, a: float) -> float:
        """Logistic gate for scalar input."""
        x = (a - self._a_t) / self._delta_a
        x = max(-50.0, min(50.0, x))
        return 1.0 / (1.0 + np.exp(-x))

    def _gate(self, a: Any) -> np.ndarray:
        """Logistic gate: g(a) = 1 / (1 + exp(−(a − a_t) / δ_a))."""
        a = _as_array(a)
        x = (a - self._a_t) / self._delta_a
        x = np.clip(x, -50, 50)
        return 1.0 / (1.0 + np.exp(-x))

    def _gate_deriv(self, a: Any) -> np.ndarray:
        """dg/da = g(a) · (1 − g(a)) / δ_a."""
        g = self._gate(a)
        return g * (1.0 - g) / self._delta_a

    # ── CosmologyModel interface ─────────────────────────────

    def e_squared(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        alpha = float(params.get("alpha_cosmo", 0.0))
        OL = 1.0 - Om

        g_a = self._gate(a)
        return Om * a**(-3.0) + OL + alpha * (g_a - self._g1)

    def de_squared_da(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        alpha = float(params.get("alpha_cosmo", 0.0))
        return -3.0 * Om * a**(-4.0) + alpha * self._gate_deriv(a)

    def growth_source(self, a: Any, params: Params) -> np.ndarray:
        """Poisson unmodified (μ=1): same form as LCDM but E² includes EFC.

        source = (3/2) · Ωm / (a⁵ · E²)
        """
        a = _as_array(a)
        Om = float(params["Omega_m"])
        E2 = self.e_squared(a, params)
        return np.where(E2 > 0, 1.5 * Om / (a**5.0 * E2), 0.0)


# ═══════════════════════════════════════════════════════════════
#  EFC VARIANT B — FREE GATE (a_t, δ_a as MCMC parameters)
# ═══════════════════════════════════════════════════════════════

class EFCVariantB(CosmologyModel):
    """
    EFC Variant B: Same physics as VariantA, but gate parameters are FREE.

    E²(a) = Ωm · a⁻³ + (1 − Ωm) + α · [g(a; a_t, δ_a) − g(1; a_t, δ_a)]

    Gate parameters a_t and δ_a are read from the params dict at each call,
    enabling MCMC sampling over them. This tests whether the α signal is
    physical or an artifact of the fixed gate shape.

    Default gate values (if not in params): a_t=0.5, δ_a=0.1 (matches VariantA).

    Expected params:
        Omega_m:      matter density
        alpha_cosmo:  flow coupling strength
        a_t:          gate transition scale factor  [0.3, 0.8]
        delta_a:      gate width                    [0.02, 0.3]
    """

    def __init__(self, a_t_default: float = 0.5, delta_a_default: float = 0.1):
        """Initialize with defaults used when params dict lacks gate values."""
        self._a_t_default = float(a_t_default)
        self._delta_a_default = float(delta_a_default)

    @property
    def name(self) -> str:
        return "efc_variant_b"

    @property
    def assumptions(self) -> Dict[str, Any]:
        return {
            "geometry": {"type": "FLRW", "curvature": "flat", "status": "assumed"},
            "redshift": {"formula": "a = 1/(1+z)", "status": "standard"},
            "propagation": {"c": "constant", "status": "implicit"},
            "sound_horizon": {"source": "planck_lcdm", "value_mpc": 147.09, "status": "proxy"},
            "poisson": {"mu": 1.0, "status": "unmodified_mvp_g1"},
            "dark_energy": {"efc": "flow_coupling_alpha", "status": "primary_test_target"},
            "gate": {"a_t": "free", "delta_a": "free", "status": "free_variant_b"},
        }

    # ── Gate functions (params-driven) ────────────────────────

    @staticmethod
    def _gate_static(a: np.ndarray, a_t: float, delta_a: float) -> np.ndarray:
        """Logistic gate with explicit parameters."""
        x = (a - a_t) / delta_a
        x = np.clip(x, -50, 50)
        return 1.0 / (1.0 + np.exp(-x))

    @staticmethod
    def _gate_deriv_static(a: np.ndarray, a_t: float, delta_a: float) -> np.ndarray:
        """dg/da with explicit parameters."""
        x = (a - a_t) / delta_a
        x = np.clip(x, -50, 50)
        g = 1.0 / (1.0 + np.exp(-x))
        return g * (1.0 - g) / delta_a

    def _get_gate_params(self, params: Params):
        """Extract gate parameters from params dict or use defaults."""
        a_t = float(params.get("a_t", self._a_t_default))
        delta_a = float(params.get("delta_a", self._delta_a_default))
        return a_t, delta_a

    # ── CosmologyModel interface ─────────────────────────────

    def e_squared(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        alpha = float(params.get("alpha_cosmo", 0.0))
        OL = 1.0 - Om

        a_t, delta_a = self._get_gate_params(params)
        g_a = self._gate_static(a, a_t, delta_a)
        g_1 = self._gate_static(np.array(1.0), a_t, delta_a)
        return Om * a**(-3.0) + OL + alpha * (g_a - g_1)

    def de_squared_da(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        alpha = float(params.get("alpha_cosmo", 0.0))
        a_t, delta_a = self._get_gate_params(params)
        return -3.0 * Om * a**(-4.0) + alpha * self._gate_deriv_static(a, a_t, delta_a)

    def growth_source(self, a: Any, params: Params) -> np.ndarray:
        """Poisson unmodified (μ=1): same form as LCDM but E² includes EFC.

        source = (3/2) · Ωm / (a⁵ · E²)
        """
        a = _as_array(a)
        Om = float(params["Omega_m"])
        E2 = self.e_squared(a, params)
        return np.where(E2 > 0, 1.5 * Om / (a**5.0 * E2), 0.0)


# ═══════════════════════════════════════════════════════════════
#  EFC VARIANT C — MODIFIED POISSON (μ ≠ 1)
# ═══════════════════════════════════════════════════════════════

class EFCVariantC(CosmologyModel):
    """
    EFC Variant C: VariantA background + modified Poisson growth source.

    E²(a) = Ωm · a⁻³ + (1 − Ωm) + α · [g(a) − g(1)]        (same as VariantA)

    Growth source (MODIFIED Poisson, μ ≠ 1):
        source = (3/2) · μ(a) · Ωm / (a⁵ · E²)

    where:
        μ(a) = 1 + (μ_0 − 1) · g(a)

    This means:
        - At early times (a ≪ a_t): g(a) ≈ 0  → μ(a) ≈ 1  (standard GR)
        - At late times  (a ≫ a_t): g(a) ≈ 1  → μ(a) ≈ μ_0 (modified gravity)

    Gate parameters are fixed (same as VariantA). μ_0 comes from params dict.

    Scientific purpose (D1):
        Tests whether EFC modifies structure formation (perturbations),
        not just the expansion history (background). If μ_0 ≈ 1: EFC is
        background-only. If μ_0 ≠ 1: deeper physical signal.

    Parameters:
        a_t:      Scale factor at gate transition (default: 0.5)
        delta_a:  Gate width (default: 0.1)
        μ_0:      Late-time gravitational coupling (default: 1.0 = GR)

    Expected params dict keys:
        Omega_m, alpha_cosmo, mu_0 (optional, default 1.0)
    """

    def __init__(self, a_t: float = 0.5, delta_a: float = 0.1):
        self._a_t = float(a_t)
        self._delta_a = float(delta_a)
        self._g1 = float(self._gate_scalar(1.0))

    @property
    def name(self) -> str:
        return "efc_variant_c"

    @property
    def assumptions(self) -> Dict[str, Any]:
        return {
            "geometry": {"type": "FLRW", "curvature": "flat", "status": "assumed"},
            "redshift": {"formula": "a = 1/(1+z)", "status": "standard"},
            "propagation": {"c": "constant", "status": "implicit"},
            "sound_horizon": {"source": "planck_lcdm", "value_mpc": 147.09, "status": "proxy"},
            "poisson": {"mu": "mu_0_from_params", "status": "modified_variant_c",
                        "formula": "mu(a) = 1 + (mu_0 - 1) * g(a)"},
            "dark_energy": {"efc": "flow_coupling_alpha", "status": "primary_test_target"},
            "gate": {"a_t": self._a_t, "delta_a": self._delta_a, "status": "fixed_variant_a"},
        }

    # ── Gate functions (same as VariantA) ──────────────────────

    def _gate_scalar(self, a: float) -> float:
        x = (a - self._a_t) / self._delta_a
        x = max(-50.0, min(50.0, x))
        return 1.0 / (1.0 + np.exp(-x))

    def _gate(self, a: Any) -> np.ndarray:
        a = _as_array(a)
        x = (a - self._a_t) / self._delta_a
        x = np.clip(x, -50, 50)
        return 1.0 / (1.0 + np.exp(-x))

    def _gate_deriv(self, a: Any) -> np.ndarray:
        g = self._gate(a)
        return g * (1.0 - g) / self._delta_a

    # ── μ(a) — gravitational coupling modification ─────────────

    def mu_of_a(self, a: Any, params: Params) -> np.ndarray:
        """Modified gravitational coupling: μ(a) = 1 + (μ_0 − 1) · g(a).

        At early times: μ → 1 (GR). At late times: μ → μ_0.
        """
        mu_0 = float(params.get("mu_0", 1.0))
        g_a = self._gate(a)
        return 1.0 + (mu_0 - 1.0) * g_a

    # ── CosmologyModel interface ─────────────────────────────

    def e_squared(self, a: Any, params: Params) -> np.ndarray:
        """Same as VariantA — μ only affects growth, not expansion."""
        a = _as_array(a)
        Om = float(params["Omega_m"])
        alpha = float(params.get("alpha_cosmo", 0.0))
        OL = 1.0 - Om
        g_a = self._gate(a)
        return Om * a**(-3.0) + OL + alpha * (g_a - self._g1)

    def de_squared_da(self, a: Any, params: Params) -> np.ndarray:
        """Same as VariantA — μ only affects growth, not expansion."""
        a = _as_array(a)
        Om = float(params["Omega_m"])
        alpha = float(params.get("alpha_cosmo", 0.0))
        return -3.0 * Om * a**(-4.0) + alpha * self._gate_deriv(a)

    def growth_source(self, a: Any, params: Params) -> np.ndarray:
        """Modified Poisson growth source.

        source = (3/2) · μ(a) · Ωm / (a⁵ · E²)

        where μ(a) = 1 + (μ_0 − 1) · g(a).
        When μ_0 = 1: identical to VariantA (standard GR Poisson).
        """
        a = _as_array(a)
        Om = float(params["Omega_m"])
        E2 = self.e_squared(a, params)
        mu_a = self.mu_of_a(a, params)
        return np.where(E2 > 0, 1.5 * mu_a * Om / (a**5.0 * E2), 0.0)


# ═══════════════════════════════════════════════════════════════
#  EFC VARIANT D — A_eff REPARAMETERIZED FREE GATE
# ═══════════════════════════════════════════════════════════════

class EFCVariantD(CosmologyModel):
    """
    EFC Variant D: A_eff reparameterized free gate (breaks α×gate degeneracy).

    E²(a) = Ωm · a⁻³ + (1 − Ωm) + A_eff · [g̃(a; a_t, δ_a) − g̃(1; a_t, δ_a)]

    where g̃(a) = g(a) / G is the NORMALIZED gate,
    and G = (1/N) Σᵢ g(aᵢ) is the gate mass over data points.

    This makes A_eff = α · G the identifiable "effective amplitude at data
    coverage", while (a_t, δ_a) are pure shape parameters.

    When G changes (gate shape changes), A_eff stays stable because
    the normalization absorbs the scale. This is the structural fix
    for the N3 COLLAPSED verdict.

    Expected params:
        Omega_m:      matter density
        A_eff:        effective flow coupling amplitude  (replaces alpha_cosmo)
        a_t:          gate transition scale factor  [0.3, 0.8]
        delta_a:      gate width                    [0.02, 0.3]
    """

    # Data z-points for gate mass computation (all 4 probes combined)
    _DATA_Z = np.array([
        0.014, 0.0194, 0.02, 0.0264, 0.0329, 0.0396, 0.0475, 0.056, 0.064,
        0.07, 0.0721, 0.0811, 0.0889, 0.1001, 0.1071, 0.12, 0.1195, 0.1278,
        0.1396, 0.15, 0.1519, 0.1635, 0.1778, 0.1906, 0.20, 0.2067, 0.2216,
        0.2405, 0.2558, 0.2762, 0.28, 0.2972, 0.3215, 0.3453, 0.3708, 0.38,
        0.40, 0.4049, 0.4355, 0.4738, 0.48, 0.51, 0.5174, 0.5742, 0.61,
        0.6299, 0.70, 0.724, 0.77, 0.821, 0.85, 0.88, 0.9511, 1.2336,
        1.30, 1.43, 1.48, 1.6123, 2.33,
    ])
    _A_GRID = np.sort(1.0 / (1.0 + _DATA_Z))  # scale factors, ascending

    def __init__(self, a_t_default: float = 0.5, delta_a_default: float = 0.1):
        self._a_t_default = float(a_t_default)
        self._delta_a_default = float(delta_a_default)

    @property
    def name(self) -> str:
        return "efc_variant_d"

    @property
    def assumptions(self) -> Dict[str, Any]:
        return {
            "geometry": {"type": "FLRW", "curvature": "flat", "status": "assumed"},
            "redshift": {"formula": "a = 1/(1+z)", "status": "standard"},
            "propagation": {"c": "constant", "status": "implicit"},
            "sound_horizon": {"source": "planck_lcdm", "value_mpc": 147.09, "status": "proxy"},
            "poisson": {"mu": 1.0, "status": "unmodified_mvp_g1"},
            "dark_energy": {"efc": "flow_coupling_A_eff", "status": "reparameterized"},
            "gate": {"a_t": "free", "delta_a": "free",
                     "normalization": "data_mean", "status": "aeff_variant_d"},
        }

    # ── Gate functions ────────────────────────────────────────

    @staticmethod
    def _gate_static(a: np.ndarray, a_t: float, delta_a: float) -> np.ndarray:
        x = (a - a_t) / delta_a
        x = np.clip(x, -50, 50)
        return 1.0 / (1.0 + np.exp(-x))

    @staticmethod
    def _gate_deriv_static(a: np.ndarray, a_t: float, delta_a: float) -> np.ndarray:
        x = (a - a_t) / delta_a
        x = np.clip(x, -50, 50)
        g = 1.0 / (1.0 + np.exp(-x))
        return g * (1.0 - g) / delta_a

    def _get_gate_params(self, params: Params):
        a_t = float(params.get("a_t", self._a_t_default))
        delta_a = float(params.get("delta_a", self._delta_a_default))
        return a_t, delta_a

    def _gate_mass(self, a_t: float, delta_a: float) -> float:
        """G = mean(gate(a_i)) over data points."""
        g = self._gate_static(self._A_GRID, a_t, delta_a)
        return max(float(np.mean(g)), 1e-8)

    # ── CosmologyModel interface ─────────────────────────────

    def e_squared(self, a: Any, params: Params) -> np.ndarray:
        """E²(a) = Ωm·a⁻³ + (1−Ωm) + A_eff·[g̃(a) − g̃(1)]."""
        a = _as_array(a)
        Om = float(params["Omega_m"])
        A_eff = float(params.get("A_eff", params.get("alpha_cosmo", 0.0)))
        OL = 1.0 - Om

        a_t, delta_a = self._get_gate_params(params)
        G = self._gate_mass(a_t, delta_a)

        gn_a = self._gate_static(a, a_t, delta_a) / G
        gn_1 = self._gate_static(np.array(1.0), a_t, delta_a) / G
        return Om * a**(-3.0) + OL + A_eff * (gn_a - gn_1)

    def de_squared_da(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        A_eff = float(params.get("A_eff", params.get("alpha_cosmo", 0.0)))

        a_t, delta_a = self._get_gate_params(params)
        G = self._gate_mass(a_t, delta_a)
        dgn_da = self._gate_deriv_static(a, a_t, delta_a) / G
        return -3.0 * Om * a**(-4.0) + A_eff * dgn_da

    def growth_source(self, a: Any, params: Params) -> np.ndarray:
        """Unmodified Poisson (μ=1) with A_eff E²."""
        a = _as_array(a)
        Om = float(params["Omega_m"])
        E2 = self.e_squared(a, params)
        return np.where(E2 > 0, 1.5 * Om / (a**5.0 * E2), 0.0)


# ═══════════════════════════════════════════════════════════════
#  EFC VARIANT E — POWER-LAW GATE (n=2, Lorentzian-derived from L0)
# ═══════════════════════════════════════════════════════════════

class EFCVariantE(CosmologyModel):
    """
    EFC Variant E: Lorentzian-derived power-law gate.

    g(a) = 1 / (1 + (a_t / a)^n)    with n = 2 locked from L0.

    Derivation (Core Derivation Note v0.2, Eq. 6-8):
        - Start from spectral window W(k) = 1 / (1 + (k/k_Λ)²)  [Lorentzian]
        - Horizon crossing k*(a) ∝ a⁻¹
        - Substitute: g(a) = W(k*(a)) = 1 / (1 + (a_t/a)²)

    This is the ontologically correct gate form:
        - n = 2 is locked by the Lorentzian shape of W(k) in L0
        - a_t is the only free gate parameter (transition scale)
        - No δ_a needed (width is determined by n)

    Behavior:
        - a << a_t:  g → 0  (early universe, no modification)
        - a >> a_t:  g → 1  (late universe, full modification)
        - a = a_t:   g = 0.5 (half-activation)

    Comparison with VariantA (logistic gate):
        The power-law gate has HEAVIER tails — it activates more gradually
        at early times and saturates more slowly. This is physical: the
        Lorentzian window has algebraic (not exponential) falloff.

    Parameters:
        a_t:  Scale factor at transition (default: 0.5, z ~ 1)
        n:    Power-law index (default: 2, locked by L0 derivation)
    """

    def __init__(self, a_t: float = 0.5, n: int = 2):
        self._a_t = float(a_t)
        self._n = int(n)  # Locked at 2 by L0 derivation
        # Pre-compute gate at a=1 for normalization
        self._g1 = float(self._gate_scalar(1.0))

    @property
    def name(self) -> str:
        return "efc_variant_e"

    @property
    def assumptions(self) -> Dict[str, Any]:
        return {
            "geometry": {"type": "FLRW", "curvature": "flat", "status": "assumed"},
            "redshift": {"formula": "a = 1/(1+z)", "status": "standard"},
            "propagation": {"c": "constant", "status": "implicit"},
            "sound_horizon": {"source": "planck_lcdm", "value_mpc": 147.09, "status": "proxy"},
            "poisson": {"mu": 1.0, "status": "unmodified_mvp_g1"},
            "dark_energy": {"efc": "flow_coupling_alpha", "status": "primary_test_target"},
            "gate": {"type": "power_law", "a_t": self._a_t, "n": self._n,
                     "derivation": "lorentzian_W(k)_L0", "status": "locked_variant_e"},
        }

    # ── Gate functions (power-law, owned by model) ────────────

    def _gate_scalar(self, a: float) -> float:
        """Power-law gate for scalar input: g(a) = 1 / (1 + (a_t/a)^n)."""
        a = max(a, 1e-10)
        return 1.0 / (1.0 + (self._a_t / a) ** self._n)

    def _gate(self, a: Any) -> np.ndarray:
        """Power-law gate: g(a) = 1 / (1 + (a_t / a)^n).

        From W(k) = 1/(1+(k/k_Λ)²) via k*(a) ∝ a⁻¹.
        """
        a = _as_array(a)
        a_safe = np.maximum(a, 1e-10)
        return 1.0 / (1.0 + (self._a_t / a_safe) ** self._n)

    def _gate_deriv(self, a: Any) -> np.ndarray:
        """dg/da = n · (a_t/a)^n · g(a)² / a.

        Derivation:
            g = 1/(1 + r^n)  where r = a_t/a
            dg/da = n · r^n · g² / a
        """
        a = _as_array(a)
        a_safe = np.maximum(a, 1e-10)
        r = self._a_t / a_safe
        g = 1.0 / (1.0 + r ** self._n)
        return self._n * r ** self._n * g ** 2.0 / a_safe

    # ── CosmologyModel interface ─────────────────────────────

    def e_squared(self, a: Any, params: Params) -> np.ndarray:
        """E²(a) = Ωm·a⁻³ + (1−Ωm) + α·[g(a) − g(1)]."""
        a = _as_array(a)
        Om = float(params["Omega_m"])
        alpha = float(params.get("alpha_cosmo", 0.0))
        OL = 1.0 - Om

        g_a = self._gate(a)
        return Om * a**(-3.0) + OL + alpha * (g_a - self._g1)

    def de_squared_da(self, a: Any, params: Params) -> np.ndarray:
        a = _as_array(a)
        Om = float(params["Omega_m"])
        alpha = float(params.get("alpha_cosmo", 0.0))
        return -3.0 * Om * a**(-4.0) + alpha * self._gate_deriv(a)

    def growth_source(self, a: Any, params: Params) -> np.ndarray:
        """Poisson unmodified (μ=1): same form as LCDM but E² includes EFC.

        source = (3/2) · Ωm / (a⁵ · E²)
        """
        a = _as_array(a)
        Om = float(params["Omega_m"])
        E2 = self.e_squared(a, params)
        return np.where(E2 > 0, 1.5 * Om / (a**5.0 * E2), 0.0)


# ═══════════════════════════════════════════════════════════════
#  EFC VARIANT F — GRAV-LOCKED G_eff GROWTH SOURCE (N7 TEST)
# ═══════════════════════════════════════════════════════════════

class EFCVariantF(CosmologyModel):
    """
    EFC Variant F: Background α deformation + GRAV-locked G_eff growth source.

    This is the "Domstolen" model — the global parameter-lock cross-probe test.
    It couples the discrete gravity sector (Graph-AQUAL) to the cosmological
    growth equations for the FIRST TIME in the inference pipeline.

    Background (expansion):
        E²(a) = Ωm · a⁻³ + (1 − Ωm) + α · [g(a) − g(1)]
        Same as VariantA — late-time Hubble friction via α.

    Growth source (GRAV-locked):
        source = (3/2) · G_eff(k_eff, a)/G · Ωm / (a⁵ · E²)

    where:
        G_eff(k,a)/G = 1 + (C² − 1) · gate(a) · screen(k)
        gate(a) = 1 / (1 + exp(-(a - a_t) / δ_a))       [logistic]
        screen(k) = 1 / (1 + (k / k_Λ)²)                [Fourier]

    FROZEN parameters (from GRAV pipeline):
        C = 2.32        (KT2 prefactor, discrete IR renormalization)
        k_lambda = 0.0014 h/Mpc  (Hubble-scale screening — SURVIVES regime bridge)
        a_t = 0.5       (gate transition)
        delta_a = 0.1   (gate width)
        k_eff = 0.1 h/Mpc  (representative scale for fσ₈ data)

    FREE MCMC parameters:
        Omega_m, H0, sigma8, alpha_cosmo

    Key property:
        - When α = 0: G_eff contribution vanishes because gate enters via α·g(a)
          in expansion, and the growth modification is proportional to the gate.
        - When C = 1: G_eff = 1 everywhere, reduces to VariantA.
        - At k >> k_lambda: screen(k) → 0, G_eff → 1 (GR recovered).

    Scientific purpose (N7 diagnostic):
        First test coupling GRAV sector to cosmological likelihood.
        Frozen C from KT2 — no rescue parameters. Either the joint
        BAO+H(z)+fσ₈+SNIa fit holds, or the model explodes.
    """

    # GRAV-locked constants (frozen from Graph-AQUAL pipeline)
    C_GRAV = 2.32           # KT2 prefactor convergence
    K_LAMBDA = 0.0014       # h/Mpc — Hubble-scale screening (regime bridge SURVIVES)
    K_EFF = 0.1             # h/Mpc — representative scale for fσ₈

    def __init__(self, a_t: float = 0.5, delta_a: float = 0.1,
                 C: float = 2.32, k_lambda: float = 0.0014,
                 k_eff: float = 0.1):
        self._a_t = float(a_t)
        self._delta_a = float(delta_a)
        self._C = float(C)
        self._k_lambda = float(k_lambda)
        self._k_eff = float(k_eff)
        self._g1 = float(self._gate_scalar(1.0))
        # Precompute screen factor at k_eff (constant for all a)
        self._screen_k_eff = 1.0 / (1.0 + (self._k_eff / self._k_lambda) ** 2)

    @property
    def name(self) -> str:
        return "efc_variant_f"

    @property
    def assumptions(self) -> Dict[str, Any]:
        return {
            "geometry": {"type": "FLRW", "curvature": "flat", "status": "assumed"},
            "redshift": {"formula": "a = 1/(1+z)", "status": "standard"},
            "propagation": {"c": "constant", "status": "implicit"},
            "sound_horizon": {"source": "planck_lcdm", "value_mpc": 147.09, "status": "proxy"},
            "poisson": {
                "mu": "G_eff(k_eff,a)/G",
                "status": "grav_locked_variant_f",
                "formula": "G_eff/G = 1 + (C²-1)·gate(a)·screen(k)",
                "C": self._C,
                "k_lambda": self._k_lambda,
                "k_eff": self._k_eff,
            },
            "dark_energy": {"efc": "flow_coupling_alpha", "status": "primary_test_target"},
            "gate": {"a_t": self._a_t, "delta_a": self._delta_a, "status": "frozen"},
            "grav_coupling": {
                "C": self._C, "source": "KT2_grid_aqual",
                "k_lambda": self._k_lambda, "source_k": "regime_bridge_survives",
                "status": "frozen_from_grav_pipeline",
            },
        }

    # ── Gate functions (same as VariantA) ──────────────────────

    def _gate_scalar(self, a: float) -> float:
        x = (a - self._a_t) / self._delta_a
        x = max(-50.0, min(50.0, x))
        return 1.0 / (1.0 + np.exp(-x))

    def _gate(self, a: Any) -> np.ndarray:
        a = _as_array(a)
        x = (a - self._a_t) / self._delta_a
        x = np.clip(x, -50, 50)
        return 1.0 / (1.0 + np.exp(-x))

    def _gate_deriv(self, a: Any) -> np.ndarray:
        g = self._gate(a)
        return g * (1.0 - g) / self._delta_a

    # ── G_eff from GRAV sector ─────────────────────────────────

    def g_eff_over_G(self, a: Any) -> np.ndarray:
        """G_eff(k_eff, a) / G at the representative scale k_eff.

        G_eff/G = 1 + (C² − 1) · gate(a) · screen(k_eff)

        At early times: gate ≈ 0 → G_eff ≈ G (GR)
        At late times:  gate ≈ 1 → G_eff/G ≈ 1 + (C²-1)·screen(k_eff) ≈ 1 + small
        """
        gate_a = self._gate(a)
        return 1.0 + (self._C ** 2 - 1.0) * gate_a * self._screen_k_eff

    # ── CosmologyModel interface ──────────────────────────────

    def e_squared(self, a: Any, params: Params) -> np.ndarray:
        """Same as VariantA — GRAV coupling only affects growth, not expansion."""
        a = _as_array(a)
        Om = float(params["Omega_m"])
        alpha = float(params.get("alpha_cosmo", 0.0))
        OL = 1.0 - Om
        g_a = self._gate(a)
        return Om * a**(-3.0) + OL + alpha * (g_a - self._g1)

    def de_squared_da(self, a: Any, params: Params) -> np.ndarray:
        """Same as VariantA."""
        a = _as_array(a)
        Om = float(params["Omega_m"])
        alpha = float(params.get("alpha_cosmo", 0.0))
        return -3.0 * Om * a**(-4.0) + alpha * self._gate_deriv(a)

    def growth_source(self, a: Any, params: Params) -> np.ndarray:
        """GRAV-locked growth source with G_eff from Graph-AQUAL.

        source = (3/2) · G_eff(k_eff, a)/G · Ωm / (a⁵ · E²)

        This is the ONLY difference from VariantA: the standard (3/2)·Ωm/(a⁵·E²)
        is multiplied by G_eff/G from the discrete gravity sector.

        When C = 1: G_eff = 1, reduces to VariantA.
        When α = 0: E² is LCDM, but growth still sees G_eff modification.
        """
        a = _as_array(a)
        Om = float(params["Omega_m"])
        E2 = self.e_squared(a, params)
        g_eff = self.g_eff_over_G(a)
        return np.where(E2 > 0, 1.5 * g_eff * Om / (a**5.0 * E2), 0.0)


# ═══════════════════════════════════════════════════════════════
#  EFC VARIANT G — CONSTITUTIVE LAW (GROWTH-ONLY, ZERO FREE PARAMS)
# ═══════════════════════════════════════════════════════════════

class EFCVariantG(CosmologyModel):
    """
    EFC Variant G: Constitutive law — growth-only mu from entropy gradients.

    THIS IS NOT:
        - A full model-independent test
        - Scale-dependent (it is z-only via cosmological proxy)
        - The final EFC formulation (that requires eps(k) from Grid-AQUAL)

    THIS IS:
        - A zero-free-parameter growth-only diagnostic
        - A test of whether entropy-gradient-driven mu can produce DlogL_growth
        - Falsifiable by DlogL_growth ~ 0 over multiple cycles

    Background (expansion):
        E^2(a) = Om * a^-3 + (1 - Om)
        Pure LCDM. No alpha. No gate. DESI DR2 compatible by construction.

    Growth source (constitutive law):
        source = (3/2) * mu(z) * Om / (a^5 * E^2)

    where:
        mu(z)  = 1 + eps_eff * F(chi(z))
        chi(z) = |dS_hat/dz| from Axiom 0 locked sources
        F(chi) = chi^2 / (chi^2 + chi_c^2)  Hill function, n=2
        eps_eff = (C^2 - 1) * screen(k_eff)

    ALL parameters frozen:
        C        = 2.32      (KT2 Grid-AQUAL convergence)
        k_lambda = 0.0014    h/Mpc  (Hubble-scale screening)
        k_eff    = 0.1       h/Mpc  (representative f*sigma_8 scale)
        chi_c    = median(chi(z)) over z in [0.2, 2.4]
        n        = 2         (Hill exponent, locked)

    FREE MCMC parameters:
        Omega_m, H0, sigma8  (same as LCDM -- no extra freedom)

    Falsification:
        If DlogL_growth ~ 0 across multiple cycles, VariantG is dead.
    """

    # GRAV-locked constants (frozen from Graph-AQUAL)
    C_GRAV = 2.32
    K_LAMBDA = 0.0014       # h/Mpc
    K_EFF = 0.1             # h/Mpc
    HILL_N = 2              # locked Hill exponent

    # Three pre-registered instrument scenarios (k_eff sweep)
    # G10: nulltest (expect UNDETECTABLE), G02: plausible, G01: strong
    SCENARIOS = {
        "G10": 0.10,   # screen=2e-4,  mu_amp~0.06%  → nulltest
        "G02": 0.02,   # screen=5e-3,  mu_amp~1.4%   → plausible
        "G01": 0.01,   # screen=2e-2,  mu_amp~5.5%   → strong
    }

    @classmethod
    def for_scenario(cls, scenario: str) -> 'EFCVariantG':
        """Factory: create VariantG for a named k_eff scenario."""
        if scenario not in cls.SCENARIOS:
            raise ValueError(f"Unknown scenario '{scenario}'. Use: {list(cls.SCENARIOS.keys())}")
        return cls(k_eff=cls.SCENARIOS[scenario])

    def __init__(self, C: float = 2.32, k_lambda: float = 0.0014,
                 k_eff: float = 0.1):
        self._C = float(C)
        self._k_lambda = float(k_lambda)
        self._k_eff = float(k_eff)

        # Precompute screening at representative scale
        self._screen_k_eff = 1.0 / (1.0 + (self._k_eff / self._k_lambda) ** 2)
        self._epsilon_eff = (self._C ** 2 - 1.0) * self._screen_k_eff

        # Load chi(z) from Axiom 0 (deterministic, cycle-independent)
        from efc_inference.data.chi_of_z_axiom0 import (
            chi_at_z as _chi_interp, CHI_C as _chi_c
        )
        self._chi_interp = _chi_interp
        self._chi_c = _chi_c

    @property
    def name(self) -> str:
        return "efc_variant_g"

    @property
    def assumptions(self) -> Dict[str, Any]:
        return {
            "geometry": {"type": "FLRW", "curvature": "flat", "status": "assumed"},
            "redshift": {"formula": "a = 1/(1+z)", "status": "standard"},
            "propagation": {"c": "constant", "status": "implicit"},
            "sound_horizon": {"source": "planck_lcdm", "value_mpc": 147.09,
                              "status": "proxy"},
            "poisson": {
                "mu": "constitutive_law_variant_g",
                "status": "growth_only_zero_free_params",
                "formula": "mu(z) = 1 + eps_eff * F(chi(z))",
                "F": "Hill function chi^n / (chi^n + chi_c^n), n=2",
                "chi": "|dS_hat/dz| from Axiom 0 locked sources",
                "epsilon_eff": round(self._epsilon_eff, 8),
                "chi_c": round(self._chi_c, 4),
                "C": self._C,
                "k_lambda": self._k_lambda,
                "k_eff": self._k_eff,
            },
            "dark_energy": {"type": "cosmological_constant", "w": -1,
                            "status": "lcdm_background"},
            "background": {"type": "pure_lcdm", "alpha": 0.0, "status": "no_gate"},
        }

    # -- mu(z) from constitutive law --------------------------

    def _F_of_chi(self, chi: np.ndarray) -> np.ndarray:
        """Hill function: F(chi) = chi^n / (chi^n + chi_c^n), n=2."""
        n = self.HILL_N
        chi_n = chi ** n
        chi_c_n = self._chi_c ** n
        return chi_n / (chi_n + chi_c_n)

    def mu_of_z(self, z: np.ndarray) -> np.ndarray:
        """mu(z) = 1 + eps_eff * F(chi(z)). Zero free parameters."""
        chi = self._chi_interp(z)
        F = self._F_of_chi(chi)
        return 1.0 + self._epsilon_eff * F

    def mu_of_a(self, a: np.ndarray) -> np.ndarray:
        """mu(a) -- convenience wrapper. a = 1/(1+z)."""
        a = _as_array(a)
        z = 1.0 / a - 1.0
        z = np.clip(z, 0.0, 10.0)
        return self.mu_of_z(z)

    def mu_diagnostics(self) -> Dict[str, float]:
        """Return diagnostic mu values at key redshifts for logging."""
        z_diag = np.array([0.3, 0.5, 0.7, 1.0, 1.5, 2.3])
        mu_vals = self.mu_of_z(z_diag)
        result = {
            "chi_c": round(self._chi_c, 6),
            "epsilon_eff": round(self._epsilon_eff, 8),
            "C_grav": self._C,
            "k_lambda": self._k_lambda,
            "k_eff": self._k_eff,
            "screen_k_eff": round(self._screen_k_eff, 8),
            "mu_min": round(float(np.min(mu_vals)), 8),
            "mu_max": round(float(np.max(mu_vals)), 8),
        }
        for z, mu in zip(z_diag, mu_vals):
            result[f"mu_z{z:.1f}"] = round(float(mu), 8)
        return result

    # -- CosmologyModel interface -----------------------------

    def e_squared(self, a: Any, params: Params) -> np.ndarray:
        """Pure LCDM background. No alpha, no gate."""
        a = _as_array(a)
        Om = float(params["Omega_m"])
        return Om * a**(-3.0) + (1.0 - Om)

    def de_squared_da(self, a: Any, params: Params) -> np.ndarray:
        """Pure LCDM background derivative."""
        a = _as_array(a)
        Om = float(params["Omega_m"])
        return -3.0 * Om * a**(-4.0)

    def growth_source(self, a: Any, params: Params) -> np.ndarray:
        """Constitutive-law growth source.

        source = (3/2) * mu(z(a)) * Om / (a^5 * E^2)

        mu is the ONLY difference from FlatLCDM. No extra free parameters.
        Background E^2 is pure LCDM.
        """
        a = _as_array(a)
        Om = float(params["Omega_m"])
        E2 = self.e_squared(a, params)
        mu = self.mu_of_a(a)
        # Safety clamp (should never trigger with screened eps_eff ~ 8.6e-4)
        mu = np.clip(mu, 0.5, 10.0)
        return np.where(E2 > 0, 1.5 * mu * Om / (a**5.0 * E2), 0.0)


# ═══════════════════════════════════════════════════════════════
#  REGISTRY — for YAML-driven cosmology selection
# ═══════════════════════════════════════════════════════════════

_REGISTRY = {
    "flat_lcdm": FlatLCDM,
    "efc_variant_a": EFCVariantA,
    "efc_variant_b": EFCVariantB,
    "efc_variant_c": EFCVariantC,
    "efc_variant_d": EFCVariantD,
    "efc_variant_e": EFCVariantE,
    "efc_variant_f": EFCVariantF,
    "efc_variant_g": EFCVariantG,
}


def get_cosmology(name: str, **kwargs) -> CosmologyModel:
    """Instantiate a CosmologyModel by name.

    Args:
        name:    Model name (flat_lcdm, efc_variant_a, efc_variant_b, efc_variant_c)
        kwargs:  Passed to constructor (e.g. a_t, delta_a for EFCVariantA).
                 Extra keys not accepted by the constructor are silently ignored
                 (allows assumptions.yaml to carry extra metadata like variant_b_defaults).

    Returns:
        CosmologyModel instance
    """
    if name not in _REGISTRY:
        raise ValueError(f"Unknown cosmology model: {name!r}. "
                         f"Available: {list(_REGISTRY.keys())}")
    cls = _REGISTRY[name]
    # Filter kwargs to only those accepted by the constructor
    import inspect
    sig = inspect.signature(cls.__init__)
    valid_params = set(sig.parameters.keys()) - {"self"}
    filtered = {k: v for k, v in kwargs.items() if k in valid_params}
    return cls(**filtered)
