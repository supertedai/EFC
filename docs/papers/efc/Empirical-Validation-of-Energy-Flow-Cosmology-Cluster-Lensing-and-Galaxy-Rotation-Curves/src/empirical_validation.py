"""
Empirical Validation of Energy-Flow Cosmology:
Cluster Lensing and Galaxy Rotation Curves

Implements the core EFC models for cluster gravitational lensing
(Bullet Cluster, MACS J0025) and galaxy rotation curves (SPARC-style).

Key equations:
  v_total^2(r) = v_baryon^2(r) + v_entropy^2(r)
  v_entropy^2  = v_h^2 * (1 - (r_h/r) * arctan(r/r_h))

Lambda scaling: lambda/R ~ 0.5-1.0 across regimes.
"""

from dataclasses import dataclass, field
import math
from typing import List, Optional


@dataclass
class LambdaScaling:
    """Entropy coupling scale lambda and its relationship to system size."""
    system_name: str
    lambda_kpc: float
    system_size_kpc: float

    @property
    def ratio(self) -> float:
        """lambda / R ratio (dimensionless consistency parameter)."""
        if self.system_size_kpc == 0:
            return float("inf")
        return self.lambda_kpc / self.system_size_kpc


@dataclass
class LensingResult:
    """Result from a cluster lensing analysis."""
    cluster_name: str
    log_likelihood_full: float
    log_likelihood_gal_only: float
    p_value_gas: float

    @property
    def delta_log_likelihood(self) -> float:
        return self.log_likelihood_full - self.log_likelihood_gal_only

    @property
    def gas_term_significant(self) -> bool:
        return self.p_value_gas < 0.05


@dataclass
class RotationCurvePoint:
    """Single point on a rotation curve."""
    r_kpc: float
    v_obs_km_s: float
    v_err_km_s: float


@dataclass
class RotationCurveModel:
    """EFC rotation curve model with entropy contribution.

    v_total^2(r) = v_baryon^2(r) + v_entropy^2(r)
    v_entropy^2  = v_h^2 * (1 - (r_h / r) * arctan(r / r_h))

    Parameters
    ----------
    v_h : float
        Asymptotic entropy velocity [km/s].
    r_h : float
        Entropy coupling scale [kpc] (i.e. lambda).
    """
    v_h: float
    r_h: float

    def v_entropy_squared(self, r: float) -> float:
        """Entropy velocity squared at radius r [kpc]."""
        if r <= 0:
            return 0.0
        return self.v_h ** 2 * (1.0 - (self.r_h / r) * math.atan(r / self.r_h))

    def v_total(self, r: float, v_baryon: float) -> float:
        """Total rotation velocity at radius r.

        Parameters
        ----------
        r : float
            Galactocentric radius [kpc].
        v_baryon : float
            Baryonic contribution to velocity [km/s].

        Returns
        -------
        float
            Total rotation velocity [km/s].
        """
        v2 = v_baryon ** 2 + self.v_entropy_squared(r)
        return math.sqrt(max(v2, 0.0))

    def chi_squared(self, data: List[RotationCurvePoint],
                    v_baryon_func) -> float:
        """Compute chi-squared for a set of observed rotation curve points.

        Parameters
        ----------
        data : list of RotationCurvePoint
            Observed data points.
        v_baryon_func : callable
            Function that returns v_baryon(r) in km/s.
        """
        chi2 = 0.0
        for pt in data:
            v_pred = self.v_total(pt.r_kpc, v_baryon_func(pt.r_kpc))
            if pt.v_err_km_s > 0:
                chi2 += ((pt.v_obs_km_s - v_pred) / pt.v_err_km_s) ** 2
        return chi2


@dataclass
class NewtonianModel:
    """Pure Newtonian model (no entropy term) for comparison."""

    def v_total(self, r: float, v_baryon: float) -> float:
        return v_baryon

    def chi_squared(self, data: List[RotationCurvePoint],
                    v_baryon_func) -> float:
        chi2 = 0.0
        for pt in data:
            v_pred = v_baryon_func(pt.r_kpc)
            if pt.v_err_km_s > 0:
                chi2 += ((pt.v_obs_km_s - v_pred) / pt.v_err_km_s) ** 2
        return chi2


@dataclass
class ValidationResult:
    """Summary of EFC vs Newtonian validation on a dataset."""
    dataset_name: str
    chi2_efc: float
    chi2_newton: float
    n_points: int
    efc_params: dict = field(default_factory=dict)

    @property
    def improvement_percent(self) -> float:
        if self.chi2_newton == 0:
            return 0.0
        return (1.0 - self.chi2_efc / self.chi2_newton) * 100.0

    @property
    def chi2_per_dof_efc(self) -> float:
        dof = self.n_points - 2  # v_h, r_h
        return self.chi2_efc / max(dof, 1)

    @property
    def chi2_per_dof_newton(self) -> float:
        return self.chi2_newton / max(self.n_points, 1)


def yukawa_kernel(r: float, lam: float) -> float:
    """Yukawa-type kernel for entropy coupling.

    K(r) = exp(-r / lambda) / r

    Parameters
    ----------
    r : float
        Distance [same units as lambda].
    lam : float
        Entropy coupling scale.
    """
    if r <= 0 or lam <= 0:
        return 0.0
    return math.exp(-r / lam) / r


def gaussian_kernel(r: float, lam: float) -> float:
    """Gaussian kernel for entropy coupling.

    K(r) = exp(-r^2 / (2 lambda^2))

    Parameters
    ----------
    r : float
        Distance.
    lam : float
        Entropy coupling scale.
    """
    if lam <= 0:
        return 0.0
    return math.exp(-r ** 2 / (2.0 * lam ** 2))


# --------------- Paper key results (structured) ---------------

BULLET_CLUSTER_LENSING = LensingResult(
    cluster_name="Bullet Cluster (1E 0657-56)",
    log_likelihood_full=268170.8,
    log_likelihood_gal_only=268170.8,
    p_value_gas=0.99,
)

LAMBDA_SCALING_BULLET = LambdaScaling(
    system_name="Bullet Cluster",
    lambda_kpc=250.0,
    system_size_kpc=500.0,
)

LAMBDA_SCALING_GALAXY = LambdaScaling(
    system_name="Galaxy (SPARC-style)",
    lambda_kpc=2.4,
    system_size_kpc=2.5,
)

ROTATION_CURVE_RESULT = ValidationResult(
    dataset_name="SPARC-style galaxy",
    chi2_efc=4.5,
    chi2_newton=296.0,
    n_points=20,
    efc_params={"v_h_km_s": 160.0, "r_h_kpc": 2.4},
)
