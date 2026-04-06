"""
EFC Gradient-Coupled Grid Action — Core Implementation

Derives E ∝ √g from a minimal three-term Lagrangian:
  S_grid = ∫ dt d³x [½m_eff(∂_t ξ)² − ½κ₀(∇ξ)² − ½α|∇Φ|(∇ξ)²]

DOI: 10.6084/m9.figshare.31941465
Author: Morten Magnusson
"""

import numpy as np

# Physical constants
HBAR = 1.0545718e-34    # Reduced Planck constant [J·s]
K_B = 1.380649e-23      # Boltzmann constant [J/K]
A_0 = 1.2e-10           # MOND acceleration scale [m/s²]


class GridAction:
    """Three-term minimal Lagrangian for the EFC grid (Eq. 2).

    S_grid = ∫ dt d³x [½m_eff(∂_t ξ)² − ½κ₀(∇ξ)² − ½α|∇Φ|(∇ξ)²]

    Parameters
    ----------
    m_eff : float
        Effective mass of grid degree of freedom.
    kappa_0 : float
        Bare elastic stiffness constant (≥ 0).
    alpha : float
        Gradient coupling constant (> 0).
    """

    def __init__(self, m_eff=1.0, kappa_0=1e-12, alpha=1.0):
        self.m_eff = m_eff
        self.kappa_0 = kappa_0
        self.alpha = alpha

    def lagrangian_density(self, dxi_dt, grad_xi_sq, g_local):
        """Compute Lagrangian density L at a point.

        Parameters
        ----------
        dxi_dt : float
            Time derivative of grid displacement ∂_t ξ.
        grad_xi_sq : float
            Squared spatial gradient |∇ξ|².
        g_local : float
            Local gravitational acceleration |∇Φ|.

        Returns
        -------
        float
            Lagrangian density L = T - V_bare - V_coupling.
        """
        T = 0.5 * self.m_eff * dxi_dt**2
        V_bare = 0.5 * self.kappa_0 * grad_xi_sq
        V_coupling = 0.5 * self.alpha * g_local * grad_xi_sq
        return T - V_bare - V_coupling

    def lagrangian(self, dxi_dt, grad_xi, g_local):
        """Convenience: compute L from scalar gradient magnitude."""
        return self.lagrangian_density(dxi_dt, grad_xi**2, g_local)

    def effective_stiffness(self, g_local):
        """Return κ_eff(x) = κ₀ + α g(x) (Eq. 5)."""
        return self.kappa_0 + self.alpha * g_local

    def info(self):
        """Return summary dict."""
        return {
            "action": "S_grid",
            "terms": 3,
            "m_eff": self.m_eff,
            "kappa_0": self.kappa_0,
            "alpha": self.alpha,
            "equation": "S = ∫[½m(∂_t ξ)² − ½κ₀(∇ξ)² − ½α|∇Φ|(∇ξ)²]",
        }


class EffectiveStiffness:
    """Effective stiffness κ_eff(x) = κ₀ + α g(x) (Eq. 5).

    Emergent from Euler-Lagrange variation of S_grid.
    """

    def __init__(self, kappa_0=1e-12, alpha=1.0):
        self.kappa_0 = kappa_0
        self.alpha = alpha

    def kappa_eff(self, g):
        """Compute effective stiffness at gravitational acceleration g.

        Parameters
        ----------
        g : float or array
            Local gravitational acceleration |∇Φ| [m/s²].

        Returns
        -------
        float or array
            κ_eff = κ₀ + αg.
        """
        g = np.asarray(g)
        return self.kappa_0 + self.alpha * g

    def crossover_acceleration(self):
        """Return g_cross = κ₀/α where bare and gravitational terms balance."""
        return self.kappa_0 / self.alpha

    def gravitational_fraction(self, g):
        """Fraction of stiffness from gravitational coupling: αg/κ_eff."""
        g = np.asarray(g)
        keff = self.kappa_eff(g)
        return self.alpha * g / keff


class DispersionRelation:
    """Local dispersion relation ω²(k,g) = κ_eff/m_eff · k² (Eq. 6-7).

    Parameters
    ----------
    m_eff : float
        Effective mass.
    kappa_0 : float
        Bare elastic stiffness.
    alpha : float
        Gradient coupling constant.
    """

    def __init__(self, m_eff=1.0, kappa_0=1e-12, alpha=1.0):
        self.m_eff = m_eff
        self.kappa_0 = kappa_0
        self.alpha = alpha
        self._stiffness = EffectiveStiffness(kappa_0, alpha)

    def omega_squared(self, k, g):
        """Compute ω²(k,g).

        Parameters
        ----------
        k : float or array
            Wavenumber.
        g : float or array
            Local gravitational acceleration.

        Returns
        -------
        float or array
            ω² = (κ₀ + αg)/m_eff · k².
        """
        k = np.asarray(k, dtype=float)
        g = np.asarray(g, dtype=float)
        return self._stiffness.kappa_eff(g) / self.m_eff * k**2

    def omega(self, k, g):
        """Compute ω(k,g)."""
        return np.sqrt(self.omega_squared(k, g))

    def energy(self, k, g):
        """Compute E = ℏω(k,g)."""
        return HBAR * self.omega(k, g)

    def phase_velocity(self, g):
        """Phase velocity v_ph = ω/k = √(κ_eff/m_eff)."""
        g = np.asarray(g, dtype=float)
        return np.sqrt(self._stiffness.kappa_eff(g) / self.m_eff)


class GradientCouplingTheorem:
    """Theorem 1: E ∝ √g in the gravitational regime (αg ≫ κ₀).

    In this limit κ_eff ≈ αg, so:
        ω = √(αg/m_eff) · k
        E = ℏω = ℏ√(αg/m_eff) · k ∝ √g

    Parameters
    ----------
    alpha : float
        Gradient coupling constant.
    m_eff : float
        Effective mass.
    """

    def __init__(self, alpha=1.0, m_eff=1.0):
        self.alpha = alpha
        self.m_eff = m_eff

    def energy(self, g, k=1.0):
        """Compute E in the gravitational limit (Theorem 1, Eq. 8).

        E = ℏ √(αg/m_eff) · k
        """
        g = np.asarray(g, dtype=float)
        return HBAR * np.sqrt(self.alpha * g / self.m_eff) * k

    def verify_scaling(self, g_values, k=1.0):
        """Verify E ∝ √g by computing E/√g ratio (should be constant).

        Returns
        -------
        dict
            ratios: E/√g for each g value, std: standard deviation of ratios.
        """
        g_values = np.asarray(g_values, dtype=float)
        E_values = self.energy(g_values, k)
        ratios = E_values / np.sqrt(g_values)
        return {
            "g_values": g_values.tolist(),
            "E_values": E_values.tolist(),
            "ratios": ratios.tolist(),
            "ratio_mean": float(np.mean(ratios)),
            "ratio_std": float(np.std(ratios)),
            "scaling_verified": bool(np.std(ratios) / np.mean(ratios) < 1e-10),
        }

    def info(self):
        return {
            "theorem": "Theorem 1",
            "statement": "E ∝ √g when αg ≫ κ₀",
            "equation": "E = ℏ√(αg/m_eff)·k",
            "regime": "gravitational (αg ≫ κ₀)",
        }


class OperatorElimination:
    """Operator uniqueness analysis (Table 1).

    Systematically evaluates five coupling operator candidates C1-C5.
    Only C5 = |∇Φ| survives all constraints.
    """

    CANDIDATES = [
        {
            "id": "C1",
            "operator": "ρ(x)",
            "description": "Local mass density",
            "survives": False,
            "failure_reason": "Not a gravitational invariant; depends on matter distribution, not field",
        },
        {
            "id": "C2",
            "operator": "Φ(x)",
            "description": "Gravitational potential",
            "survives": False,
            "failure_reason": "Gauge-dependent (Φ → Φ + const); violates shift symmetry",
        },
        {
            "id": "C3",
            "operator": "g² = |∇Φ|²",
            "description": "Squared acceleration",
            "survives": False,
            "failure_reason": "Wrong scaling; produces E ∝ g, not E ∝ √g",
        },
        {
            "id": "C4",
            "operator": "∇²Φ",
            "description": "Laplacian of potential",
            "survives": False,
            "failure_reason": "Vanishes in vacuum (∇²Φ = 0 outside sources); non-local proxy",
        },
        {
            "id": "C5",
            "operator": "|∇Φ| = g",
            "description": "Gravitational acceleration magnitude",
            "survives": True,
            "failure_reason": None,
        },
    ]

    def evaluate_all(self):
        """Return full evaluation table."""
        return self.CANDIDATES.copy()

    def survivors(self):
        """Return only surviving operators."""
        return [c for c in self.CANDIDATES if c["survives"]]

    def eliminated(self):
        """Return eliminated operators with reasons."""
        return [c for c in self.CANDIDATES if not c["survives"]]

    def summary(self):
        """Return summary of operator uniqueness analysis."""
        n_elim = len(self.eliminated())
        n_surv = len(self.survivors())
        return {
            "total_candidates": len(self.CANDIDATES),
            "eliminated": n_elim,
            "survivors": n_surv,
            "unique_operator": self.survivors()[0]["operator"],
            "conclusion": f"{n_elim} operators eliminated; "
                          f"only {self.survivors()[0]['operator']} survives all constraints",
        }


class RegimeAnalysis:
    """Three physical regimes of the dispersion relation.

    1. Bare elastic: κ₀ ≫ αg → ω ≈ √(κ₀/m_eff)·k
    2. Gravitational: αg ≫ κ₀ → ω ≈ √(αg/m_eff)·k → E ∝ √g
    3. Transition: αg ~ κ₀ → full κ_eff = κ₀ + αg

    Crossover at g_cross = κ₀/α.
    """

    def __init__(self, kappa_0=1e-12, alpha=1.0, m_eff=1.0):
        self.kappa_0 = kappa_0
        self.alpha = alpha
        self.m_eff = m_eff

    def g_cross(self):
        """Crossover acceleration g_cross = κ₀/α."""
        return self.kappa_0 / self.alpha

    def classify(self, g):
        """Classify a gravitational acceleration into a regime.

        Parameters
        ----------
        g : float
            Local gravitational acceleration.

        Returns
        -------
        str
            Regime name: 'bare_elastic', 'transition', or 'gravitational'.
        """
        gc = self.g_cross()
        ratio = self.alpha * g / self.kappa_0 if self.kappa_0 > 0 else np.inf
        if ratio < 0.1:
            return "bare_elastic"
        elif ratio > 10:
            return "gravitational"
        else:
            return "transition"

    def regime_table(self, g_values):
        """Classify an array of accelerations.

        Returns
        -------
        list of dict
            Each with g, regime, αg/κ₀ ratio, ω/k.
        """
        g_values = np.asarray(g_values, dtype=float)
        results = []
        for g in g_values:
            keff = self.kappa_0 + self.alpha * g
            omega_over_k = np.sqrt(keff / self.m_eff)
            results.append({
                "g": float(g),
                "regime": self.classify(float(g)),
                "alpha_g_over_kappa0": float(self.alpha * g / self.kappa_0) if self.kappa_0 > 0 else float("inf"),
                "kappa_eff": float(keff),
                "omega_over_k": float(omega_over_k),
            })
        return results

    def info(self):
        return {
            "regimes": ["bare_elastic", "transition", "gravitational"],
            "g_cross": self.g_cross(),
            "bare_elastic": "κ₀ ≫ αg → ω ≈ √(κ₀/m_eff)·k",
            "gravitational": "αg ≫ κ₀ → ω ≈ √(αg/m_eff)·k → E ∝ √g",
            "transition": "αg ~ κ₀ → full dispersion",
        }


class BosonicQuantisation:
    """Standard bosonic quantisation of grid excitations.

    Canonical: [a_k, a†_k'] = δ_{kk'}
    Hamiltonian: H = Σ_k ℏω_k (a†_k a_k + ½)
    Thermal: ⟨n_k⟩ = 1/(exp(ℏω_k / k_B T) - 1)
    """

    def __init__(self, m_eff=1.0, kappa_0=1e-12, alpha=1.0):
        self.dispersion = DispersionRelation(m_eff, kappa_0, alpha)

    def zero_point_energy(self, k, g):
        """Zero-point energy E_0 = ½ℏω for mode k at acceleration g."""
        return 0.5 * HBAR * self.dispersion.omega(k, g)

    def thermal_occupation(self, k, g, T):
        """Bose-Einstein occupation number ⟨n_k⟩.

        Parameters
        ----------
        k : float
            Wavenumber.
        g : float
            Local gravitational acceleration.
        T : float
            Grid temperature [K].

        Returns
        -------
        float
            Mean occupation number.
        """
        omega = self.dispersion.omega(k, g)
        x = HBAR * omega / (K_B * T)
        if x > 500:
            return 0.0
        if x < 1e-15:
            return K_B * T / (HBAR * omega)  # Classical limit
        return 1.0 / (np.exp(x) - 1.0)

    def mean_energy(self, k, g, T):
        """Mean energy per mode: ℏω(⟨n⟩ + ½)."""
        omega = self.dispersion.omega(k, g)
        n = self.thermal_occupation(k, g, T)
        return HBAR * omega * (n + 0.5)

    def partition_function_mode(self, k, g, T):
        """Single-mode partition function Z_k = 1/(1 - exp(-ℏω/kT))."""
        omega = self.dispersion.omega(k, g)
        x = HBAR * omega / (K_B * T)
        if x > 500:
            return 1.0
        if x < 1e-15:
            return K_B * T / (HBAR * omega)  # Classical limit
        return 1.0 / (1.0 - np.exp(-x))


class FalsifiablePredictions:
    """Two falsifiable predictions from the gradient-coupled grid action.

    P1: Bare stiffness bound — κ₀/(α·a₀) ≪ 1
    P2: Dispersion signature at sub-kpc scales
    """

    def __init__(self, kappa_0=1e-12, alpha=1.0):
        self.kappa_0 = kappa_0
        self.alpha = alpha

    def p1_stiffness_bound(self):
        """Evaluate P1: bare stiffness ratio κ₀/(α·a₀).

        Must satisfy κ₀/(α·a₀) ≪ 1 for EFC to reproduce RAR.
        """
        ratio = self.kappa_0 / (self.alpha * A_0)
        return {
            "prediction": "P1",
            "description": "Bare stiffness bound",
            "condition": "κ₀/(α·a₀) ≪ 1",
            "ratio": float(ratio),
            "satisfied": ratio < 0.01,
            "kappa_0": self.kappa_0,
            "alpha": self.alpha,
            "a_0": A_0,
        }

    def p2_dispersion_signature(self):
        """Describe P2: sub-kpc dispersion signature.

        At sub-kpc scales near g_cross = κ₀/α, the full dispersion
        ω² = (κ₀ + αg)/m_eff · k² should show deviation from pure √g scaling.
        """
        g_cross = self.kappa_0 / self.alpha
        return {
            "prediction": "P2",
            "description": "Dispersion signature at sub-kpc scales",
            "g_cross": float(g_cross),
            "g_cross_over_a0": float(g_cross / A_0),
            "observable": "Deviation from E ∝ √g near g_cross",
            "scale": "sub-kpc (where g approaches g_cross)",
            "status": "testable",
        }

    def summary(self):
        """Return summary of both predictions."""
        return {
            "P1": self.p1_stiffness_bound(),
            "P2": self.p2_dispersion_signature(),
        }
