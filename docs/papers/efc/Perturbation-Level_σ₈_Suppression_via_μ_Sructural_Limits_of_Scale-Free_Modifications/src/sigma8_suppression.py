"""
Perturbation-Level sigma_8 Suppression via mu(a) < 1:
Structural Limits of Scale-Free Modifications

Implements the EFC perturbation channel where mu(a) = 1 - B g(a)
weakens the gravitational source term in the growth equation.

Core equations:
  Growth: f' + f^2 + (1/2 - 3/2 Omega_m_tilde) f = 3/2 mu(a) Omega_m_tilde
  Gate:   g(a) = 1 / (1 + (a_t / a)^n)
  Calib:  B = (1 - mu_0) / g(1; n)
"""

from dataclasses import dataclass, field
import math
from typing import List, Optional


@dataclass
class GateFunction:
    """Sigmoid gate function g(a) = 1 / (1 + (a_t/a)^n).

    Parameters
    ----------
    a_t : float
        Transition scale factor.
    n : float
        Gate steepness exponent.
    """
    a_t: float = 0.4975
    n: float = 2.0

    def __call__(self, a: float) -> float:
        """Evaluate g(a)."""
        if a <= 0:
            return 0.0
        return 1.0 / (1.0 + (self.a_t / a) ** self.n)

    def at_present(self) -> float:
        """g(a=1)."""
        return self(1.0)


@dataclass
class MuModel:
    """Perturbation-level modification mu(a) = 1 - B g(a).

    Parameters
    ----------
    mu_0 : float
        Present-day mu value.
    n : float
        Gate steepness exponent.
    z_t : float
        Transition redshift.
    """
    mu_0: float = 0.85
    n: float = 2.0
    z_t: float = 1.01

    def __post_init__(self):
        self._a_t = 1.0 / (1.0 + self.z_t)
        self._gate = GateFunction(a_t=self._a_t, n=self.n)
        g1 = self._gate.at_present()
        self._B = (1.0 - self.mu_0) / g1 if g1 != 0 else 0.0

    @property
    def a_t(self) -> float:
        return self._a_t

    @property
    def B(self) -> float:
        """Calibrated perturbation amplitude."""
        return self._B

    def gate(self, a: float) -> float:
        """Gate function g(a)."""
        return self._gate(a)

    def mu(self, a: float) -> float:
        """Effective gravitational coupling mu(a)."""
        return 1.0 - self._B * self._gate(a)

    def mu_at_z(self, z: float) -> float:
        """mu at redshift z."""
        return self.mu(1.0 / (1.0 + z))


@dataclass
class GrowthParameters:
    """Cosmological parameters for the growth equation."""
    Omega_m: float = 0.3134
    H0: float = 67.4
    sigma_8_lcdm: float = 0.811


@dataclass
class SuppressionResult:
    """Result of a sigma_8 suppression computation."""
    mu_0: float
    n: int
    B: float
    sigma_8: float
    S_8: float
    delta_sigma_8: float = 0.0
    chi2_RSD: Optional[float] = None
    gap_closed_percent: Optional[float] = None
    planck_status: str = ""


@dataclass
class UniversalFactorTwo:
    """The universal factor-2 result: delta_sigma8(n=2) / delta_sigma8(n=6) ~ 2.0."""
    mu_0: float
    delta_sigma8_n6: float
    delta_sigma8_n2: float

    @property
    def ratio(self) -> float:
        if self.delta_sigma8_n6 == 0:
            return float("inf")
        return self.delta_sigma8_n2 / self.delta_sigma8_n6


def compute_S8(sigma_8: float, Omega_m: float) -> float:
    """S_8 = sigma_8 * sqrt(Omega_m / 0.3)."""
    return sigma_8 * math.sqrt(Omega_m / 0.3)


def gap_closure_percent(sigma_8: float, sigma_8_planck: float = 0.811,
                        sigma_8_lensing: float = 0.759) -> float:
    """Fraction of S8 gap closed (in percent).

    Gap = sigma8_planck - sigma8_lensing.
    Closure = (sigma8_planck - sigma_8) / gap * 100.
    """
    gap = sigma_8_planck - sigma_8_lensing
    if gap == 0:
        return 0.0
    return (sigma_8_planck - sigma_8) / gap * 100.0


def suppression_integral_ratio(n1: int, n2: int,
                               a_t: float = 0.4975,
                               a_min: float = 0.01) -> float:
    """Numerical ratio of suppression integrals for two gate widths.

    integral g(a; n) d(ln a)  from ln(a_min) to 0.

    Parameters
    ----------
    n1, n2 : int
        Gate steepness exponents.
    a_t : float
        Transition scale factor.
    a_min : float
        Lower integration bound (scale factor).

    Returns
    -------
    float
        Ratio integral(n2) / integral(n1).
    """
    n_steps = 2000
    ln_a_min = math.log(a_min)
    ln_a_max = 0.0
    d_ln_a = (ln_a_max - ln_a_min) / n_steps

    def integrate_gate(n_exp):
        total = 0.0
        for i in range(n_steps):
            ln_a = ln_a_min + (i + 0.5) * d_ln_a
            a = math.exp(ln_a)
            g = 1.0 / (1.0 + (a_t / a) ** n_exp)
            total += g * d_ln_a
        return total

    i1 = integrate_gate(n1)
    i2 = integrate_gate(n2)
    if i1 == 0:
        return float("inf")
    return i2 / i1


# ---- Paper reference data ----

REFERENCE_MODEL_WP1A = SuppressionResult(
    mu_0=0.85, n=2, B=0.187,
    sigma_8=0.773, S_8=0.790,
    delta_sigma_8=-0.038,
    chi2_RSD=-19.8,
    gap_closed_percent=73,
    planck_status="~1.5 sigma",
)

UNIVERSAL_FACTOR_2_DATA = [
    UniversalFactorTwo(mu_0=0.913, delta_sigma8_n6=-0.011, delta_sigma8_n2=-0.022),
    UniversalFactorTwo(mu_0=0.850, delta_sigma8_n6=-0.019, delta_sigma8_n2=-0.038),
    UniversalFactorTwo(mu_0=0.800, delta_sigma8_n6=-0.025, delta_sigma8_n2=-0.050),
]

S8_CLOSURE_DATA = [
    SuppressionResult(mu_0=0.913, n=6, B=0.088, sigma_8=0.800, S_8=0.818,
                      gap_closed_percent=21, planck_status="OK"),
    SuppressionResult(mu_0=0.913, n=2, B=0.109, sigma_8=0.789, S_8=0.806,
                      gap_closed_percent=43, planck_status="OK"),
    SuppressionResult(mu_0=0.850, n=2, B=0.187, sigma_8=0.773, S_8=0.790,
                      gap_closed_percent=73, planck_status="~1.5 sigma"),
    SuppressionResult(mu_0=0.800, n=2, B=0.250, sigma_8=0.761, S_8=0.777,
                      gap_closed_percent=97, planck_status="2 sigma"),
]
