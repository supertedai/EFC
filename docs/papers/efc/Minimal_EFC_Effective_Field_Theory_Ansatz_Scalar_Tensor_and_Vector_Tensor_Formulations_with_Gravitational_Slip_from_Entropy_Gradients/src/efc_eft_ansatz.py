"""
EFC Effective Field Theory Ansatz — Reference Implementation

Two EFT formulations for Energy-Flow Cosmology:
  Ansatz I:  Scalar-tensor (Horndeski/EFT-DE)
  Ansatz II: Vector-tensor (dynamical energy flow)

Reference: DOI 10.6084/m9.figshare.31368433
Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
Version: Research Note v6
"""

from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np


# =============================================================================
# EFC Entropy Field (Section 3)
# =============================================================================

class EntropyField:
    """EFC sigmoid entropy field S(a) — Eq. (9).

    S(a) = [1 + exp(-(ln a - ln a_t) / Delta)]^{-1}

    Parameters
    ----------
    a_t : float
        Transition scale factor (default 0.30, z_t ~ 2.3).
    Delta : float
        Transition sharpness (default 0.3).
    """
    def __init__(self, a_t: float = 0.30, Delta: float = 0.3):
        self.a_t = a_t
        self.Delta = Delta

    def __call__(self, a):
        """Evaluate S(a)."""
        a = np.asarray(a, dtype=float)
        return 1.0 / (1.0 + np.exp(-(np.log(a) - np.log(self.a_t)) / self.Delta))

    def dS_dlna(self, a):
        """Derivative dS/d(ln a) — peaks at a = a_t."""
        S = self(a)
        return S * (1 - S) / self.Delta

    def mu_growth(self, a, delta_mu: float = -0.075):
        """Phenomenological mu(a) = 1 + delta_mu * S(a) — Eq. (13)."""
        return 1.0 + delta_mu * self(a)


# =============================================================================
# Target Signature (Section 2)
# =============================================================================

@dataclass
class TargetSignature:
    """EFC target observable signature — Eqs. (1)-(3), (8), (24).

    All three conditions must hold simultaneously in 0.5 < z < 1.5.
    """
    mu: float = 0.925
    sigma: float = 1.05
    delta_mu: float = -0.075

    @property
    def eta_required(self) -> float:
        """Required slip: eta > 2*Sigma/mu - 1 — Eq. (8)."""
        return 2.0 * self.sigma / self.mu - 1.0

    def sigma_from_mu_eta(self, mu: float, eta: float) -> float:
        """Sigma = mu * (1 + eta) / 2 — Eq. (7)."""
        return mu * (1.0 + eta) / 2.0

    def eta_from_mu_sigma(self, mu: float, sigma: float) -> float:
        """Invert Eq. (7): eta = 2*Sigma/mu - 1."""
        return 2.0 * sigma / mu - 1.0

    def summary(self):
        lines = [
            "EFC Target Signature",
            "=" * 50,
            f"mu    = {self.mu}  (< 1, weakened gravity)",
            f"Sigma = {self.sigma}  (> 1, enhanced lensing)",
            f"eta   = {self.eta_required:.3f}  (> 1, gravitational slip)",
            f"delta_mu = {self.delta_mu}",
            f"Regime: 0.5 < z < 1.5",
        ]
        return "\n".join(lines)


# =============================================================================
# Ansatz I: Scalar-Tensor EFT (Section 4)
# =============================================================================

class ScalarTensorEFT:
    """Scalar-tensor EFT in Bellini-Sawicki alpha basis — Eqs. (14)-(17).

    Action: L = M_Pl^2/2 R + K(S,X) + G3(S,X) box S

    Alpha parameters:
        alpha_T = 0          (GW170817)
        alpha_B ~ B0 * dS/d(ln a)  (braiding from entropy gradient)
        alpha_M ~ M0 * S(a)        (running Planck mass)

    Parameters
    ----------
    B0 : float
        Braiding amplitude (free parameter).
    M0 : float
        Planck-mass running amplitude (free parameter).
    a_t : float
        Transition scale factor.
    Delta : float
        Transition sharpness.
    """
    def __init__(self, B0: float = 1.0, M0: float = 1.0,
                 a_t: float = 0.30, Delta: float = 0.3):
        self.B0 = B0
        self.M0 = M0
        self.entropy = EntropyField(a_t, Delta)

    def alpha_T(self, a) -> float:
        """Tensor speed excess: alpha_T = 0 (GW170817)."""
        return 0.0

    def alpha_B(self, a):
        """Braiding: alpha_B = B0 * dS/d(ln a) — Eq. (16)."""
        return self.B0 * self.entropy.dS_dlna(a)

    def alpha_M(self, a):
        """Planck-mass running: alpha_M = M0 * S(a) — Eq. (17)."""
        return self.M0 * self.entropy(a)

    def no_ghost_QS(self, a, alpha_K: float = 1.0):
        """No-ghost condition: Q_S = alpha_K + 3/2 alpha_B^2 > 0 — Eq. (22)."""
        aB = self.alpha_B(a)
        return alpha_K + 1.5 * aB**2

    @property
    def free_parameters(self) -> list:
        return ["B0", "M0", "a_t", "Delta"]

    def summary(self):
        lines = [
            "Ansatz I: Scalar-Tensor EFT (Horndeski)",
            "=" * 50,
            f"B0 = {self.B0}  (braiding amplitude)",
            f"M0 = {self.M0}  (Planck-mass running)",
            f"a_t = {self.entropy.a_t}  (z_t = {1/self.entropy.a_t - 1:.1f})",
            f"Delta = {self.entropy.Delta}",
            f"alpha_T = 0  (GW170817)",
            f"alpha_B(a_t) = {self.alpha_B(self.entropy.a_t):.4f}",
            f"alpha_M(a_t) = {self.alpha_M(self.entropy.a_t):.4f}",
            "Implementation: hi_class + EFTCosmoMC",
            "Testability: High",
        ]
        return "\n".join(lines)


# =============================================================================
# Ansatz II: Vector-Tensor EFT (Section 5)
# =============================================================================

class VectorTensorEFT:
    """Vector-tensor EFT with dynamical energy flow J^mu — Eq. (18).

    Action: L = M_Pl^2/2 R - 1/4 F_{mn} F^{mn} - m^2/2 J_m J^m + beta J^m nabla_m S

    Anisotropic stress from entropy gradient:
        pi ~ beta^2 nabla S_bar . nabla delta_S
        eta - 1 ~ C_eta beta^2 (nabla S_bar)^2 / (k^2 rho_eff)

    Parameters
    ----------
    beta : float
        Entropy-flow coupling constant.
    m2 : float
        Vector field mass squared (m^2 > 0 required).
    a_t : float
        Transition scale factor.
    Delta : float
        Transition sharpness.
    """
    def __init__(self, beta: float = 1.0, m2: float = 1.0,
                 a_t: float = 0.30, Delta: float = 0.3):
        self.beta = beta
        self.m2 = m2
        self.entropy = EntropyField(a_t, Delta)

    def slip_estimate(self, a, k: float = 0.05, rho_eff: float = 1.0,
                      C_eta: float = 1.0):
        """Schematic slip estimate: eta - 1 ~ C_eta beta^2 (dS/dlna)^2 / (k^2 rho_eff) — Eq. (21).

        Note: C_eta > 0 is to be determined by full perturbation analysis.
        """
        dSdlna = self.entropy.dS_dlna(a)
        return C_eta * self.beta**2 * dSdlna**2 / (k**2 * rho_eff)

    def is_tachyon_free(self) -> bool:
        """Stability: m^2 > 0 — no tachyonic instability."""
        return self.m2 > 0

    @property
    def free_parameters(self) -> list:
        return ["beta", "m^2", "a_t", "Delta"]

    def summary(self):
        lines = [
            "Ansatz II: Vector-Tensor EFT (Energy Flow)",
            "=" * 50,
            f"beta = {self.beta}  (entropy-flow coupling)",
            f"m^2 = {self.m2}  (vector mass squared)",
            f"a_t = {self.entropy.a_t}  (z_t = {1/self.entropy.a_t - 1:.1f})",
            f"Delta = {self.entropy.Delta}",
            f"Tachyon-free: {self.is_tachyon_free()}",
            f"Slip at a_t (schematic): eta-1 ~ {self.slip_estimate(self.entropy.a_t):.4f}",
            "Implementation: Requires new Boltzmann code",
            "Testability: Low",
        ]
        return "\n".join(lines)


# =============================================================================
# Comparison table
# =============================================================================

@dataclass
class ComparisonRow:
    """One row of Table 2."""
    property: str
    scalar_tensor: str
    vector_tensor: str

COMPARISON_TABLE = [
    ComparisonRow("EFC ontology", "Indirect (S as effective scalar)", "Direct (J^mu as flow)"),
    ComparisonRow("Free parameters", "{B0, M0, a_t, Delta}", "{beta, m^2, a_t, Delta}"),
    ComparisonRow("mu < 1 mechanism", "Via alpha_B, alpha_M", "Via J^mu mass term"),
    ComparisonRow("eta > 1 mechanism", "Via braiding alpha_B != 0", "Via pi ~ (nabla S)^2"),
    ComparisonRow("Sigma > 1", "Numerical check required", "Numerical check required"),
    ComparisonRow("GR at high z", "Automatic (alpha -> 0)", "Automatic (nabla S -> 0)"),
    ComparisonRow("GW170817", "alpha_T = 0 imposed", "Naturally small c_T correction"),
    ComparisonRow("Numerical tools", "hi_class, EFTCosmoMC", "New Boltzmann code needed"),
    ComparisonRow("Testability", "High", "Low"),
]


def print_comparison():
    """Print Table 2 comparison."""
    lines = [
        "Comparison: Scalar-Tensor vs Vector-Tensor",
        "=" * 70,
        f"{'Property':<22} {'Scalar-Tensor':<26} {'Vector-Tensor':<22}",
        "-" * 70,
    ]
    for row in COMPARISON_TABLE:
        lines.append(f"{row.property:<22} {row.scalar_tensor:<26} {row.vector_tensor:<22}")
    return "\n".join(lines)
