"""
WP4 — Cross-Survey Parameter Transfer Validation.

Reproducible numerical core for EFC parameters frozen from DESI DR2 and
applied to BOSS DR12 BAO without refitting.

DOI: 10.6084/m9.figshare.31954125
"""
from __future__ import annotations
from dataclasses import dataclass, field
from math import sqrt
from typing import List


@dataclass(frozen=True)
class EFCRegimeGate:
    """H_EFC(z) = H_LCDM(z) * sqrt(1 + alpha_L2 * Theta(z < z_L1L2))."""
    z_L1L2: float = 1.01
    alpha_L2: float = 0.045

    def factor(self, z: float) -> float:
        return sqrt(1.0 + (self.alpha_L2 if z < self.z_L1L2 else 0.0))


def H_efc(H_lcdm: float, z: float, gate: EFCRegimeGate = EFCRegimeGate()) -> float:
    return H_lcdm * gate.factor(z)


@dataclass(frozen=True)
class TransferTestResult:
    chi2_LCDM: float
    chi2_EFC: float
    k_eff: int = 0

    @property
    def delta_chi2(self) -> float:
        return self.chi2_EFC - self.chi2_LCDM

    @property
    def efc_wins(self) -> bool:
        return self.delta_chi2 < 0


@dataclass(frozen=True)
class CovarianceDiagnostics:
    """Three diagnostics from §4.2 of WP4."""
    whitened: List[tuple] = field(default_factory=list)  # [(label, chi2_LCDM, chi2_EFC), ...]
    eigenmode_strong: float = -5.50
    eigenmode_weak: float = -2.27

    @property
    def strong_fraction(self) -> float:
        return self.eigenmode_strong / (self.eigenmode_strong + self.eigenmode_weak)

    def whitened_total(self) -> tuple[float, float, float]:
        L = sum(c for _, c, _ in self.whitened)
        E = sum(c for _, _, c in self.whitened)
        return L, E, E - L


@dataclass(frozen=True)
class BestFit:
    dataset: str
    N: int
    k_eff: int
    z_L1L2: float | None
    alpha_L2: float
    dAICc: float
    dBIC: float
    note: str = ""


# ── Frozen results from WP4 (Tables 1–4) ────────────────────────────────────

WP4_RESULT = TransferTestResult(chi2_LCDM=20.83, chi2_EFC=13.06, k_eff=0)

WHITENED_COMPONENTS = [
    ("w1", 1.27,  2.29),
    ("w2", 1.09,  2.14),
    ("w3", 0.01,  2.82),
    ("w4", 1.50,  0.48),
    ("w5", 15.30, 3.91),  # dominant: Δχ² = −11.39
    ("w6", 1.65,  1.43),
]

ROBUSTNESS_SWEEP = [
    (0.00, 16.37, 12.13),
    (0.25, 15.27, 10.68),
    (0.50, 14.82,  9.87),
    (0.75, 16.52, 10.82),
    (1.00, 20.83, 13.06),
]

BEST_FITS = [
    BestFit("BOSS",       6, 1, None, 0.036, -6.4,  -7.6,  "z_L1L2 unidentifiable for >0.6"),
    BestFit("BOSS+eBOSS", 14, 2, 1.60, 0.036, -19.3, -19.1),
    BestFit("DESI DR2",   13, 2, 1.01, 0.045, -1.0,  -1.0),
]


def covariance_diagnostics() -> CovarianceDiagnostics:
    return CovarianceDiagnostics(whitened=WHITENED_COMPONENTS)
