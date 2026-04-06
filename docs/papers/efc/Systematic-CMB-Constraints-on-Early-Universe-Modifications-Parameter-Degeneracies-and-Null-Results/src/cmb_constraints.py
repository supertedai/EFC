"""
Systematic CMB Constraints on EFC:
Parameter Degeneracies and Null Results

Both kappa-dot and H(z) EFC mechanisms REJECTED against Planck 2018 CMB.
1D 'signal' was parameter degeneracy artifact.
CMB epoch = L0-L1 regime where standard physics expected.

Key finding: Initial 1D scan suggested epsilon ~ +3% (delta_chi2 ~ -65),
but 2D grid (epsilon vs h) revealed this was a degeneracy artifact.
True minimum at epsilon ~ 0 (delta_chi2 ~ -1).
"""

from dataclasses import dataclass, field
import math
from typing import List, Optional, Tuple


@dataclass
class CMBData:
    """Planck 2018 TT spectrum summary."""
    source: str = "Planck 2018 TT"
    n_points: int = 2507
    ell_min: int = 2
    ell_max: int = 2508


@dataclass
class KappaDotResult:
    """Result of kappa-dot mechanism test.

    Implementation: kappa_dot *= (1 + boost * tanh((z - 700) / 200))
    """
    boost_percent: float
    chi2_per_dof: float
    delta_chi2: float

    @property
    def rejected(self) -> bool:
        """Any non-zero boost worsens chi2."""
        return self.delta_chi2 > 0 or self.boost_percent == 0.0


@dataclass
class HzGridPoint:
    """Single point in the 2D H(z) parameter grid."""
    epsilon_percent: float
    h: float
    delta_chi2: float


@dataclass
class HzSweepResult:
    """Result of the H(z) mechanism test.

    Implementation: rho_EFC = epsilon * rho_tot(a) * window_function
    """
    epsilon_1d_artifact: float = 3.0
    delta_chi2_1d_artifact: float = -65.0
    epsilon_true_min: float = -0.5
    h_true_min: float = 0.6736
    delta_chi2_true_min: float = -1.26
    status: str = "REJECTED"

    @property
    def is_artifact(self) -> bool:
        """The 1D signal was a parameter degeneracy artifact."""
        return True


@dataclass
class RegimeInterpretation:
    """EFC-R regime interpretation of CMB null results."""
    cmb_epoch: str = "L0-L1"
    expected_physics: str = "Standard (LCDM dominant)"
    result: str = "LCDM provides best fit"
    implication: str = "Consistent with EFC-R framework"

    def describe(self) -> str:
        return (f"CMB epoch = {self.cmb_epoch} regime. "
                f"Expected: {self.expected_physics}. "
                f"Result: {self.result}. "
                f"Implication: {self.implication}.")


@dataclass
class CMBConstraintsSummary:
    """Full summary of CMB constraints on EFC modifications."""
    kappa_dot_status: str = "REJECTED"
    hz_status: str = "REJECTED"
    key_lesson: str = ("Parameter degeneracies can create false signals. "
                       "Multi-dimensional analysis essential.")

    kappa_dot_results: List[KappaDotResult] = field(default_factory=list)
    hz_result: HzSweepResult = field(default_factory=HzSweepResult)
    regime: RegimeInterpretation = field(default_factory=RegimeInterpretation)

    @property
    def both_rejected(self) -> bool:
        return (self.kappa_dot_status == "REJECTED" and
                self.hz_status == "REJECTED")


def chi2_per_dof(chi2: float, n_points: int = 2507, n_params: int = 1) -> float:
    """chi2 per degree of freedom."""
    dof = n_points - n_params
    if dof <= 0:
        return float("inf")
    return chi2 / dof


def kappa_dot_modification(z: float, boost: float) -> float:
    """Kappa-dot modification factor.

    kappa_dot_modified = kappa_dot * (1 + boost * tanh((z - 700) / 200))

    Parameters
    ----------
    z : float
        Redshift.
    boost : float
        Fractional modification (e.g. 0.01 = 1%).

    Returns
    -------
    float
        Modification factor (multiply onto kappa_dot).
    """
    return 1.0 + boost * math.tanh((z - 700.0) / 200.0)


def hz_energy_injection(a: float, epsilon: float, a_t: float = 9.1e-4,
                        delta: float = 5e-5) -> float:
    """EFC H(z) energy injection fraction.

    rho_EFC / rho_tot = epsilon * exp(-0.5 * ((a - a_t) / delta)^2)

    Parameters
    ----------
    a : float
        Scale factor.
    epsilon : float
        Fractional energy injection at peak.
    a_t : float
        Scale factor at recombination (~1/1100).
    delta : float
        Width of the Gaussian window.

    Returns
    -------
    float
        Fractional energy injection.
    """
    if delta <= 0:
        return 0.0
    return epsilon * math.exp(-0.5 * ((a - a_t) / delta) ** 2)


# ---- Paper reference data ----

KAPPA_DOT_RESULTS = [
    KappaDotResult(boost_percent=-2.0, chi2_per_dof=1.1905, delta_chi2=13.0),
    KappaDotResult(boost_percent=-1.0, chi2_per_dof=1.1875, delta_chi2=5.4),
    KappaDotResult(boost_percent=0.0,  chi2_per_dof=1.1853, delta_chi2=0.0),
    KappaDotResult(boost_percent=1.0,  chi2_per_dof=1.1875, delta_chi2=5.4),
    KappaDotResult(boost_percent=2.0,  chi2_per_dof=1.1905, delta_chi2=13.0),
]

HZ_RESULT = HzSweepResult()

CMB_DATA = CMBData()

REGIME = RegimeInterpretation()

SUMMARY = CMBConstraintsSummary(
    kappa_dot_results=KAPPA_DOT_RESULTS,
    hz_result=HZ_RESULT,
    regime=REGIME,
)
