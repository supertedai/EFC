"""
Robustness of the EFC Growth-Sector Signal:
Leave-One-Out, Sound-Horizon, and Amplitude-Prior Controls
for the Hubble-Friction Channel

Joint Bayesian fit to 14 BAO + 7 f*sigma_8 points yields
alpha = -1.00 +/- 0.46 (2.20 sigma).

Core equation:
  E^2(a) = E^2_LCDM(a) * [1 + alpha * T(a)]
"""

from dataclasses import dataclass, field
import math
from typing import List, Optional


@dataclass
class FsigmaDataPoint:
    """A single f*sigma_8 measurement."""
    survey: str
    z: float
    fsigma8: float
    error: float


@dataclass
class LeaveOneOutResult:
    """Result of dropping one f*sigma_8 point and refitting."""
    drop_index: int
    z: float
    survey: str
    alpha: float
    sigma: float
    delta_AIC: float
    r_alpha_Omega_m: float

    @property
    def significance(self) -> float:
        """abs(alpha) / sigma."""
        if self.sigma == 0:
            return float("inf")
        return abs(self.alpha) / self.sigma

    @property
    def passes(self) -> bool:
        """Pass criterion: |alpha|/sigma >= 1.7 AND delta_AIC <= 0."""
        return self.significance >= 1.7 and self.delta_AIC <= 0


@dataclass
class BaseSignal:
    """Base EFC fit result with all data included."""
    alpha: float = -1.00
    sigma: float = 0.46
    delta_AIC: float = -2.91
    delta_BIC: float = -0.91
    p_value_one_sided: float = 0.028

    @property
    def significance_sigma(self) -> float:
        if self.sigma == 0:
            return float("inf")
        return abs(self.alpha) / self.sigma


@dataclass
class EFCFriedmann:
    """EFC modified Friedmann equation: E^2(a) = E^2_LCDM(a) * [1 + alpha T(a)].

    Parameters
    ----------
    alpha : float
        EFC coupling constant (negative = growth suppression).
    Omega_m : float
        Matter density parameter.
    a_transition : float
        Scale factor where late-time gate activates.
    gate_width : float
        Width of the transition gate.
    """
    alpha: float = -1.0
    Omega_m: float = 0.315
    a_transition: float = 0.5
    gate_width: float = 0.15

    def gate(self, a: float) -> float:
        """Late-time activation gate T(a).

        Sigmoid turning on at a ~ a_transition.
        """
        x = (a - self.a_transition) / self.gate_width
        if x > 20:
            return 1.0
        if x < -20:
            return 0.0
        return 1.0 / (1.0 + math.exp(-x))

    def E_squared_lcdm(self, a: float) -> float:
        """Standard LCDM E^2(a) = Omega_m a^-3 + (1 - Omega_m)."""
        if a <= 0:
            return float("inf")
        return self.Omega_m * a ** (-3) + (1.0 - self.Omega_m)

    def E_squared(self, a: float) -> float:
        """EFC-modified E^2(a).

        The coupling alpha enters perturbatively through the Hubble
        friction channel. The effective modification to E^2 is scaled
        so that |alpha| ~ 1 produces percent-level changes:

        E^2(a) = E^2_LCDM(a) * [1 + (alpha/100) * T(a)]
        """
        return self.E_squared_lcdm(a) * (1.0 + (self.alpha / 100.0) * self.gate(a))

    def H(self, a: float, H0: float = 67.4) -> float:
        """Hubble parameter H(a) in km/s/Mpc."""
        E2 = self.E_squared(a)
        if E2 <= 0:
            return 0.0
        return H0 * math.sqrt(E2)

    def H_at_z(self, z: float, H0: float = 67.4) -> float:
        """H(z)."""
        return self.H(1.0 / (1.0 + z), H0)

    def fsigma8_predicted(self, z: float, sigma_8: float = 0.81) -> float:
        """Approximate f*sigma_8(z) prediction.

        Uses linear growth approximation:
        f ~ Omega_m(a)^0.55 with perturbative alpha correction.
        """
        a = 1.0 / (1.0 + z)
        E2 = self.E_squared(a)
        if E2 <= 0:
            return 0.0
        Omega_m_a = self.Omega_m * a ** (-3) / E2
        f = Omega_m_a ** 0.55
        # Growth suppression from alpha < 0 (perturbative)
        growth_factor = 1.0 + 0.02 * self.alpha * self.gate(a)
        return f * sigma_8 * growth_factor


@dataclass
class DegeneracyStructure:
    """Parameter correlation structure."""
    r_alpha_Omega_m: float = 0.59
    r_alpha_sigma8: float = -0.27

    def describe(self) -> str:
        parts = []
        parts.append(f"r(alpha, Omega_m) = +{self.r_alpha_Omega_m:.2f} "
                      "(geometric degeneracy)")
        parts.append(f"r(alpha, sigma_8) = {self.r_alpha_sigma8:.2f} "
                      "(growth suppression trades off against lower sigma_8)")
        return "; ".join(parts)


def compute_loo_score(results: List[LeaveOneOutResult]) -> str:
    """Compute leave-one-out pass score."""
    n_pass = sum(1 for r in results if r.passes)
    return f"{n_pass}/{len(results)}"


# ---- Paper reference data ----

FSIGMA8_DATA = [
    FsigmaDataPoint("6dFGS",      0.02, 0.360, 0.040),
    FsigmaDataPoint("SDSS MGS",   0.15, 0.490, 0.055),
    FsigmaDataPoint("BOSS DR12",  0.38, 0.430, 0.054),
    FsigmaDataPoint("BOSS DR12",  0.51, 0.452, 0.057),
    FsigmaDataPoint("BOSS DR12",  0.61, 0.457, 0.052),
    FsigmaDataPoint("VIPERS",     0.77, 0.420, 0.060),
    FsigmaDataPoint("FastSound",  0.85, 0.380, 0.080),
]

LOO_RESULTS = [
    LeaveOneOutResult(0, 0.02, "6dFGS",     -0.88, 0.48, -1.59, 0.622),
    LeaveOneOutResult(1, 0.15, "SDSS MGS",   -1.11, 0.46, -3.97, 0.598),
    LeaveOneOutResult(2, 0.38, "BOSS DR12",  -0.98, 0.46, -2.58, 0.586),
    LeaveOneOutResult(3, 0.51, "BOSS DR12",  -1.03, 0.47, -2.97, 0.588),
    LeaveOneOutResult(4, 0.61, "BOSS DR12",  -1.04, 0.48, -3.20, 0.608),
    LeaveOneOutResult(5, 0.77, "VIPERS",     -1.00, 0.47, -2.70, 0.583),
    LeaveOneOutResult(6, 0.85, "FastSound",  -0.97, 0.46, -2.54, 0.594),
]

BASE_SIGNAL = BaseSignal()
DEGENERACY = DegeneracyStructure()
