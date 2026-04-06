"""
Regime-Dependent Breakdown of LCDM Across Cosmic Time

Systematic analysis combining low-redshift galaxy dynamics (SPARC, z~0)
with high-redshift galaxy abundances (COSMOS-Web/JWST, z>6).

Key result: Deviations cluster systematically
(chi2 = 47.3, df = 4, p < 1e-8).

JWST/COSMOS galaxies exceed LCDM predictions by 23-529x
depending on redshift.
"""

from dataclasses import dataclass, field
import math
from typing import List, Optional


@dataclass
class HighZExcess:
    """High-redshift galaxy excess relative to LCDM predictions."""
    z_min: float
    z_max: float
    ratio_behroozi: float
    ratio_halo_limit: float

    @property
    def z_label(self) -> str:
        return f"z={self.z_min:.0f}-{self.z_max:.0f}"

    @property
    def excess_significant(self) -> bool:
        """Significant if ratio > 3 against halo limit."""
        return self.ratio_halo_limit > 3.0


@dataclass
class DataSource:
    """Observational data source."""
    name: str
    n_objects: int
    z_range: str
    description: str = ""


@dataclass
class StatisticalTest:
    """Chi-squared test for regime-dependent clustering."""
    chi2: float
    df: int
    p_value: float

    @property
    def confidence_percent(self) -> float:
        return (1.0 - self.p_value) * 100.0

    @property
    def significant(self) -> bool:
        return self.p_value < 0.001


@dataclass
class RegimeBreakdownSummary:
    """Full analysis summary."""
    statistical_test: StatisticalTest
    high_z_excess: List[HighZExcess]
    data_sources: List[DataSource]
    disclaimers: List[str]

    @property
    def max_excess_behroozi(self) -> float:
        return max(e.ratio_behroozi for e in self.high_z_excess)

    @property
    def max_excess_halo(self) -> float:
        return max(e.ratio_halo_limit for e in self.high_z_excess)

    @property
    def n_significant_bins(self) -> int:
        return sum(1 for e in self.high_z_excess if e.excess_significant)


def behroozi_smhm_ratio(z: float, M_halo_log: float = 12.0) -> float:
    """Approximate Behroozi+2019 stellar-mass-to-halo-mass ratio.

    Simplified parametric form for illustration.

    Parameters
    ----------
    z : float
        Redshift.
    M_halo_log : float
        log10 of halo mass in solar masses.

    Returns
    -------
    float
        M_star / M_halo ratio.
    """
    # Peak efficiency at M_halo ~ 10^12 at z=0, declining at high z
    peak_ratio = 0.023  # ~2.3% at z=0 for M_halo=10^12
    z_suppression = (1.0 + z) ** (-1.5)
    return peak_ratio * z_suppression


def halo_mass_function_excess(z: float, n_observed: float,
                              n_predicted: float) -> float:
    """Ratio of observed to predicted galaxy number density.

    Parameters
    ----------
    z : float
        Redshift of the bin.
    n_observed : float
        Observed cumulative number density.
    n_predicted : float
        LCDM-predicted cumulative number density.

    Returns
    -------
    float
        Excess ratio (>1 means more galaxies than expected).
    """
    if n_predicted <= 0:
        return float("inf")
    return n_observed / n_predicted


def chi_squared_regime_test(observed_ratios: List[float],
                            expected_ratio: float = 1.0,
                            errors: Optional[List[float]] = None) -> float:
    """Chi-squared test for regime-dependent deviation.

    Parameters
    ----------
    observed_ratios : list of float
        Observed excess ratios per bin.
    expected_ratio : float
        Expected ratio under null (LCDM) hypothesis.
    errors : list of float, optional
        Uncertainties on each ratio. Defaults to sqrt(ratio).

    Returns
    -------
    float
        Chi-squared statistic.
    """
    chi2 = 0.0
    for i, obs in enumerate(observed_ratios):
        if errors and i < len(errors):
            sigma = errors[i]
        else:
            sigma = max(math.sqrt(abs(obs)), 1.0)
        chi2 += ((obs - expected_ratio) / sigma) ** 2
    return chi2


# ---- Paper reference data ----

HIGH_Z_EXCESS_DATA = [
    HighZExcess(z_min=5, z_max=6,  ratio_behroozi=23.0,  ratio_halo_limit=3.1),
    HighZExcess(z_min=7, z_max=8,  ratio_behroozi=124.0, ratio_halo_limit=7.7),
    HighZExcess(z_min=8, z_max=9,  ratio_behroozi=259.0, ratio_halo_limit=10.4),
    HighZExcess(z_min=9, z_max=10, ratio_behroozi=529.0, ratio_halo_limit=10.6),
]

STATISTICAL_TEST = StatisticalTest(
    chi2=47.3,
    df=4,
    p_value=1.3e-9,
)

DATA_SOURCES = [
    DataSource("SPARC", 175, "z~0", "175 disk galaxies (Lelli+ 2016)"),
    DataSource("COSMOS2025", 26288, "z>5", "26,288 galaxies (Shuntov+ 2025)"),
]

DISCLAIMERS = [
    "Does NOT falsify LCDM",
    "Does NOT propose alternative dynamics",
    "Does NOT identify unique mechanism",
]

SUMMARY = RegimeBreakdownSummary(
    statistical_test=STATISTICAL_TEST,
    high_z_excess=HIGH_Z_EXCESS_DATA,
    data_sources=DATA_SOURCES,
    disclaimers=DISCLAIMERS,
)
