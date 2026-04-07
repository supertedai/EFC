"""
EFC DES Y6 lensing validation — reproducible numerical core.

Implements Equations (1)–(5) of EFC-VAL-2026-002 and the pre-registered
pass/fail logic for the P3 lensing consistency test.

DOI: 10.6084/m9.figshare.31951992
"""
from __future__ import annotations
from dataclasses import dataclass, field
from math import sqrt
from typing import Optional


@dataclass
class Measurement:
    value: float
    uncertainty: float
    label: str = ""

    def __truediv__(self, other: "Measurement") -> "Measurement":
        v = self.value / other.value
        # uncorrelated relative errors in quadrature
        rel = sqrt((self.uncertainty / self.value) ** 2 + (other.uncertainty / other.value) ** 2)
        return Measurement(v, v * rel, f"({self.label})/({other.label})")


@dataclass
class DESY6Result:
    """DES Year 6 3x2pt cosmic shear analysis (arXiv:2601.14559)."""
    S8: Measurement = field(default_factory=lambda: Measurement(0.789, 0.012, "S8 DES Y6"))
    area_deg2: float = 5000.0
    source_galaxies_M: float = 140.0
    lens_galaxies_M: float = 9.0
    n_eff_arcmin2: float = 8.22


@dataclass
class CMB2026Baseline:
    """Joint Planck + ACT DR6 + SPT-3G CMB lensing (Qu et al. 2026, SNR=61)."""
    S8: Measurement = field(default_factory=lambda: Measurement(0.836, 0.012, "S8 CMB 2026"))


@dataclass
class EFCLensingPrediction:
    """EFC pre-registered prediction for the lensing-to-CMB S8 ratio.

    Derived from:
      - eta = 1 (gravitational slip ansatz A3)
      - k = 0.415 ± 0.05 (SPARC Phase 3 screening exponent)
      - aG = 0.094 ± 0.01 (cosmological coupling from H0)
    """
    ratio: Measurement = field(default_factory=lambda: Measurement(0.95, 0.03, "EFC ratio prediction"))
    Sigma_EFC: float = 0.95
    eta: float = 1.0
    k_screening: Measurement = field(default_factory=lambda: Measurement(0.415, 0.05, "k SPARC"))
    aG: Measurement = field(default_factory=lambda: Measurement(0.094, 0.01, "aG"))
    pre_registered_doi: str = "10.6084/m9.figshare.31188193"
    pass_window: tuple = (0.90, 1.00)


@dataclass
class ValidationStatus:
    name: str
    passed: bool
    sigma: float
    note: str = ""


@dataclass
class P3LensingTest:
    des: DESY6Result = field(default_factory=DESY6Result)
    cmb: CMB2026Baseline = field(default_factory=CMB2026Baseline)
    efc: EFCLensingPrediction = field(default_factory=EFCLensingPrediction)

    def observed_ratio(self) -> Measurement:
        """Equation (5): S8_DES / S8_CMB with uncorrelated error propagation."""
        return self.des.S8 / self.cmb.S8

    def agreement_sigma(self) -> float:
        obs = self.observed_ratio()
        diff = abs(obs.value - self.efc.ratio.value)
        sig = sqrt(obs.uncertainty ** 2 + self.efc.ratio.uncertainty ** 2)
        return diff / sig

    def evaluate(self) -> ValidationStatus:
        obs = self.observed_ratio()
        lo, hi = self.efc.pass_window
        in_window = lo <= obs.value <= hi
        return ValidationStatus(
            name="P3 lensing consistency",
            passed=in_window,
            sigma=self.agreement_sigma(),
            note=f"observed {obs.value:.3f} ± {obs.uncertainty:.3f} in window [{lo}, {hi}]",
        )


@dataclass
class ValidationLedgerRow:
    test: str
    name: str
    prediction: str
    observed: Optional[str]
    status: str


def current_ledger() -> list[ValidationLedgerRow]:
    """EFC empirical validation status — April 2026 (post DES Y6)."""
    return [
        ValidationLedgerRow("P1", "Closure g† = cH0/e", "2.5e-10 m/s^2", "2.51 ± 0.60", "consistent"),
        ValidationLedgerRow("P2", "Cross-scale C stability", "C ≈ 4.4", None, "untested"),
        ValidationLedgerRow("P3", "Lensing S8 ratio", "0.95 ± 0.03", "0.944 ± 0.018", "PASS"),
        ValidationLedgerRow("A3", "η = 1 assumption", "η = 1", None, "not tested here"),
    ]
