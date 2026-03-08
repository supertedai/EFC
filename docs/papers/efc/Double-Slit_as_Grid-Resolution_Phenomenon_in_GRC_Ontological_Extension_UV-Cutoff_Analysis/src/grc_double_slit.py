"""
GRC Double-Slit — Reference Implementation

Grid-Rendering Cosmology: double-slit as grid-resolution phenomenon.
UV-cutoff derivation, entropy-clarity function, predictions and gaps.

Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
Version: Working Note v0.2 (Revised), March 8, 2026
"""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np


# =============================================================================
# Axioms (Section 2)
# =============================================================================

GRC_AXIOMS = [
    ("A1", "Grid (G)", "Discrete geometric substrate with fundamental node scale l_g"),
    ("A2", "Energy Flow (E)", "Energy as distributed flow through G; localized=particle, distributed=field"),
    ("A3", "Clarity Function C(S)", "C(S) = exp(-S/S_max); low S = high clarity"),
    ("A4", "Manifest Structure", "Psi_manifest = G(x) tensor E(x,t) . C(S(x,t))"),
    ("A5", "Grid-Resolution Limit", "Position limited by l_g"),
    ("A6", "Registration", "Measurement = local selection and stabilization of Psi_manifest"),
]


class GRCAxioms:
    """GRC axiom set (Section 2)."""
    def __init__(self):
        self.axioms = GRC_AXIOMS

    def summary(self):
        lines = ["GRC Axioms (Section 2)", "=" * 60]
        for aid, name, content in self.axioms:
            lines.append(f"  {aid}: {name}")
            lines.append(f"      {content}")
        return "\n".join(lines)


# =============================================================================
# Entropy-Clarity Function (Axiom A3)
# =============================================================================

class EntropyClarity:
    """Clarity function C(S) = exp(-S/S_max) — Eq. (1).

    Parameters
    ----------
    S_max : float
        Maximum entropy scale (default 1.0).
    """
    def __init__(self, S_max: float = 1.0):
        self.S_max = S_max

    def __call__(self, S):
        """Evaluate C(S) = exp(-S/S_max)."""
        S = np.asarray(S, dtype=float)
        return np.exp(-S / self.S_max)

    def decoherence_time_factor(self, S):
        """tau_d proportional to C(S) — Eq. (7)."""
        return self.__call__(S)


# =============================================================================
# UV-Cutoff Model (Section 7)
# =============================================================================

class UVCutoffModel:
    """UV-cutoff realization of GRC grid-resolution — Eqs. (8)-(14).

    Parameters
    ----------
    l_g : float
        Grid node scale (fundamental length).
    sigma : float
        Gaussian slit width.
    D : float
        Slit separation (default 1e-4 m).
    """
    def __init__(self, l_g: float = 1e-35, sigma: float = 1e-6, D: float = 1e-4):
        self.l_g = l_g
        self.sigma = sigma
        self.D = D

    @property
    def k_max(self) -> float:
        """UV cutoff: k_max = pi / l_g."""
        return np.pi / self.l_g

    def gaussian_fourier(self, k):
        """Fourier amplitude for double-Gaussian slit — Eq. (11)."""
        k = np.asarray(k, dtype=float)
        return np.exp(-self.sigma**2 * k**2 / 2) * np.cos(k * self.D / 2)

    def deviation_bound(self) -> float:
        """Upper bound on |Delta A| for Gaussian slit — Eq. (14).

        |Delta A| <= (l_g / pi sigma^2) exp(-pi^2 sigma^2 / 2 l_g^2)
        """
        ratio = self.sigma / self.l_g
        exponent = -np.pi**2 * ratio**2 / 2
        if exponent < -700:
            return 0.0
        prefactor = self.l_g / (np.pi * self.sigma**2)
        return prefactor * np.exp(exponent)

    def is_accessible(self, threshold: float = 1e-100) -> bool:
        """True if deviation is above threshold (practically measurable)."""
        return self.deviation_bound() > threshold

    def grc_amplitude(self, x, n_points: int = 10000):
        """Compute A_GRC(x) via numerical integration with UV cutoff — Eq. (8)."""
        x = np.asarray(x, dtype=float)
        k = np.linspace(-self.k_max, self.k_max, n_points)
        dk = k[1] - k[0]
        a_k = self.gaussian_fourier(k)
        A = np.array([np.sum(a_k * np.exp(1j * k * xi)) * dk for xi in x])
        return A

    def qm_amplitude(self, x):
        """Standard QM amplitude (analytic for Gaussian slits)."""
        x = np.asarray(x, dtype=float)
        env = np.exp(-x**2 / (2 * self.sigma**2))
        return env * np.cos(np.pi * x * self.D / (2 * self.sigma**2))

    def summary(self):
        dev = self.deviation_bound()
        lines = [
            "UV-Cutoff Model (Section 7)",
            "=" * 50,
            f"l_g   = {self.l_g:.2e} m",
            f"sigma = {self.sigma:.2e} m",
            f"D     = {self.D:.2e} m",
            f"k_max = pi/l_g = {self.k_max:.2e} m^-1",
            f"sigma/l_g = {self.sigma/self.l_g:.2e}",
            f"|Delta A| bound = {dev:.2e}",
            f"Accessible: {self.is_accessible()}",
        ]
        if dev == 0.0:
            lines.append("(Deviation underflows to zero — exponential suppression)")
        return "\n".join(lines)


# =============================================================================
# Predictions (Section 5)
# =============================================================================

@dataclass
class GRCPrediction:
    """One prediction from Section 5."""
    id: str
    name: str
    status: str
    content: str
    prediction_type: str
    blocked_by: Optional[str] = None


PREDICTIONS = [
    GRCPrediction("P1", "Backward compatibility", "Required (analytic)",
                  "Recover QM as C->1 and l_g/d->0", "consistency"),
    GRCPrediction("P2", "Geometric cutoff deviation", "Downgraded",
                  "Exponentially suppressed; principled but inaccessible", "principled"),
    GRCPrediction("P3", "S-sensitive decoherence", "Open (primary)",
                  "tau_d ~ C(S); distinct from Lindblad if S definable independently of T",
                  "empirical", "G2"),
    GRCPrediction("P4", "Gradual which-path suppression", "Open (secondary)",
                  "Distinguishable via higher-order statistics under partial measurement",
                  "empirical"),
    GRCPrediction("P5", "No prediction for d >> l_g", "Explicit no-claim",
                  "GRC makes no deviation prediction when d >> l_g and S is low",
                  "scope_limit"),
]


class PredictionStatus:
    """Prediction register for GRC double-slit (Section 5)."""
    def __init__(self):
        self.predictions = PREDICTIONS

    def summary(self):
        lines = ["Predictions (Section 5)", "=" * 60,
                 f"{'ID':<5} {'Name':<30} {'Status':<25}",
                 "-" * 60]
        for p in self.predictions:
            lines.append(f"{p.id:<5} {p.name:<30} {p.status:<25}")
        return "\n".join(lines)


# =============================================================================
# Falsification Points (Section 6)
# =============================================================================

FALSIFICATION_POINTS = [
    ("F1", "Backward compatibility fails", "analytic"),
    ("F2", "No scale-deviation where GRC predicts one", "principled (not operative)"),
    ("F3", "Decoherence fully reduced to T + environment; no S-component", "nearest-term empirical"),
    ("F4", "Higher-order statistics identical to QM under partial measurement", "empirical"),
    ("F5", "Delta P(x) doesn't decrease with d/l_g", "analytic"),
    ("F6", "Standard QM results at d >> l_g do NOT falsify GRC", "scope boundary"),
]


# =============================================================================
# Open Gaps (Section 8)
# =============================================================================

@dataclass
class OpenGap:
    """One open gap from Table 1."""
    id: str
    priority: int
    description: str
    blocks: str


OPEN_GAPS = [
    OpenGap("G2", 1, "Operational definition of local S", "P3 testability"),
    OpenGap("P3", 2, "Formal decoherence model via C(S)", "Main test candidate"),
    OpenGap("P4", 3, "Concrete higher-order observable", "Secondary test"),
    OpenGap("G3", 4, "Explicit P(x) for concrete geometry", "Numerical check"),
    OpenGap("G5", 5, "Closure Condition 3 vs mode basis", "Internal consistency"),
]

G2_CANDIDATES = [
    ("A", "von Neumann entropy of subsystem", "Weakest; likely reduces to standard QM"),
    ("B", "Entanglement entropy against environment", "Requires different rate than Lindblad"),
    ("C", "Free-energy or structural complexity proxy", "Most EFC-native; hardest; highest priority"),
]


class OpenGaps:
    """Open gaps and priorities (Section 8, Table 1)."""
    def __init__(self):
        self.gaps = OPEN_GAPS
        self.g2_candidates = G2_CANDIDATES

    def summary(self):
        lines = [
            "Open Gaps (Table 1)", "=" * 60,
            f"{'Pri':<5} {'Gap':<5} {'Description':<35} {'Blocks':<20}",
            "-" * 60,
        ]
        for g in self.gaps:
            lines.append(f"{g.priority:<5} {g.id:<5} {g.description:<35} {g.blocks:<20}")
        lines.append("")
        lines.append("G2 Candidates for operational S:")
        for cid, name, assess in self.g2_candidates:
            lines.append(f"  {cid}: {name}")
            lines.append(f"     {assess}")
        return "\n".join(lines)
