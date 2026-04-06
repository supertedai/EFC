"""EFC Unified Analysis of BAO, SN Ia, and RSD -- Python implementation.

Implements the EFC effective gravitational coupling mu(a), entropy field
S(a), chi-squared analysis framework, and results from the unified
cosmological analysis.

Reference: Magnusson (2026), DOI: 10.6084/m9.figshare.31215613
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# EFC Parameters for the Unified Analysis
# ---------------------------------------------------------------------------

@dataclass
class UnifiedAnalysisParameters:
    """Parameters used in the unified BAO+SN+RSD analysis."""
    beta: float = 0.16        # EFC coupling constant
    a_t: float = 0.55         # Transition scale factor
    z_t: float = 0.82         # Transition redshift
    sigma: float = 0.10       # Transition width
    gamma: float = 0.0        # Background modification (disabled)
    S_inf: float = 1.0        # Asymptotic entropy (normalised)

    # LCDM baseline
    H0: float = 67.4          # km/s/Mpc
    Omega_m: float = 0.315
    Omega_Lambda: float = 0.685

    def as_dict(self) -> Dict[str, float]:
        return {k: v for k, v in self.__dict__.items()}


# ---------------------------------------------------------------------------
# Entropy Field
# ---------------------------------------------------------------------------

def entropy_field(a: float, S_inf: float = 1.0, a_t: float = 0.55,
                  sigma: float = 0.10) -> float:
    """S(a) = (S_inf/2)[1 + tanh((ln a - ln a_t)/sigma)]."""
    if a <= 0:
        return 0.0
    x = (math.log(a) - math.log(a_t)) / sigma
    return (S_inf / 2.0) * (1.0 + math.tanh(x))


def mu_eff(a: float, beta: float = 0.16, **kwargs) -> float:
    """Effective gravitational coupling: mu(a) = G_eff/G = 1 + beta*S(a)."""
    return 1.0 + beta * entropy_field(a, **kwargs)


def a_from_z(z: float) -> float:
    """Convert redshift to scale factor."""
    return 1.0 / (1.0 + z)


# ---------------------------------------------------------------------------
# Data Sources
# ---------------------------------------------------------------------------

@dataclass
class DataSource:
    """A cosmological data source used in the analysis."""
    probe: str
    survey: str
    N: int
    z_min: float
    z_max: float

    def z_range(self) -> str:
        return f"{self.z_min:.2f} -- {self.z_max:.2f}"


def data_sources() -> List[DataSource]:
    """The three data sources used in the unified analysis."""
    return [
        DataSource("BAO", "DESI DR2", 6, 0.51, 2.33),
        DataSource("SN Ia", "Pantheon+", 16, 0.01, 1.00),
        DataSource("RSD", "BOSS+eBOSS+DESI", 11, 0.30, 1.52),
    ]


def total_data_points() -> int:
    return sum(ds.N for ds in data_sources())


# ---------------------------------------------------------------------------
# Chi-squared Results
# ---------------------------------------------------------------------------

@dataclass
class ChiSquaredResult:
    """Chi-squared results for a model against combined probes."""
    model: str
    chi2_BAO: float
    chi2_SN: float
    chi2_RSD: float

    @property
    def chi2_total(self) -> float:
        return self.chi2_BAO + self.chi2_SN + self.chi2_RSD

    def summary(self) -> str:
        return (
            f"{self.model}: BAO={self.chi2_BAO:.2f}, SN={self.chi2_SN:.2f}, "
            f"RSD={self.chi2_RSD:.2f}, Total={self.chi2_total:.2f}"
        )


def lcdm_result() -> ChiSquaredResult:
    return ChiSquaredResult("LCDM", 9.81, 28.98, 10.56)


def efc_result() -> ChiSquaredResult:
    return ChiSquaredResult("EFC", 9.81, 28.98, 12.28)


def delta_chi2() -> float:
    """Difference in total chi2: EFC - LCDM."""
    return efc_result().chi2_total - lcdm_result().chi2_total


# ---------------------------------------------------------------------------
# Key Findings
# ---------------------------------------------------------------------------

def key_findings() -> List[str]:
    return [
        "mu(a) derived from EFC field equations, not phenomenologically fitted",
        "BAO and SN identical to LCDM by construction (gamma=0)",
        "RSD slightly worse (Delta chi2=+1.7) but within statistical fluctuations",
        "Same S(a) describes geometry and growth without internal tension",
    ]


# ---------------------------------------------------------------------------
# Unified Analysis Container
# ---------------------------------------------------------------------------

@dataclass
class UnifiedAnalysis:
    """Top-level container for the unified BAO+SN+RSD analysis."""
    params: UnifiedAnalysisParameters = field(
        default_factory=UnifiedAnalysisParameters
    )
    sources: List[DataSource] = field(default_factory=data_sources)
    lcdm: ChiSquaredResult = field(default_factory=lcdm_result)
    efc: ChiSquaredResult = field(default_factory=efc_result)
    findings: List[str] = field(default_factory=key_findings)

    def delta_chi2(self) -> float:
        return self.efc.chi2_total - self.lcdm.chi2_total

    def total_data_points(self) -> int:
        return sum(s.N for s in self.sources)

    def mu_at(self, a: float) -> float:
        return mu_eff(a, self.params.beta, S_inf=self.params.S_inf,
                      a_t=self.params.a_t, sigma=self.params.sigma)

    def entropy_at(self, a: float) -> float:
        return entropy_field(a, self.params.S_inf, self.params.a_t,
                             self.params.sigma)

    def verdict(self) -> str:
        dchi2 = self.delta_chi2()
        if abs(dchi2) < 3.84:  # 95% CL for 1 DOF
            return "Compatible within statistical fluctuations, no internal tension"
        else:
            return f"Significant difference: Delta chi2 = {dchi2:.2f}"

    def summary(self) -> str:
        lines = [
            "=== EFC Unified Analysis: BAO + SN Ia + RSD ===",
            f"DOI: 10.6084/m9.figshare.31215613",
            "",
            "PARAMETERS:",
            f"  beta={self.params.beta}, a_t={self.params.a_t} (z_t={self.params.z_t}), "
            f"sigma={self.params.sigma}, gamma={self.params.gamma}",
            "",
            "DATA SOURCES:",
        ]
        for s in self.sources:
            lines.append(f"  {s.probe}: {s.survey} ({s.N} points, z={s.z_range()})")
        lines.append(f"  Total: {self.total_data_points()} data points")
        lines.append("")
        lines.append("CHI-SQUARED RESULTS:")
        lines.append(f"  {self.lcdm.summary()}")
        lines.append(f"  {self.efc.summary()}")
        lines.append(f"  Delta chi2 = {self.delta_chi2():.2f}")
        lines.append(f"  Verdict: {self.verdict()}")
        lines.append("")
        lines.append("KEY FINDINGS:")
        for f in self.findings:
            lines.append(f"  - {f}")
        return "\n".join(lines)
