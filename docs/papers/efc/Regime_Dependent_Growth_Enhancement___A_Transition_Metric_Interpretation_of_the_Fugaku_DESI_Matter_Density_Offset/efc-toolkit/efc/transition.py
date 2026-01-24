"""
EFC Transition Functions and Estimators
=======================================

Implements the regime-dependent effective gravitational coupling μ(a)
and the transition estimator Δ_F.

Core equations:
    μ(a) = G_eff(a) / G
    μ(a) = 1 + Δμ · R((ln a - ln a_t) / σ)
    Δ_F = ∫ W(a) · [μ(a) - 1] d(ln a)

Reference: DOI 10.6084/m9.figshare.31096951

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
"""

import numpy as np
from typing import Callable, Optional, Tuple
from dataclasses import dataclass


def sigmoid(x: np.ndarray) -> np.ndarray:
    """Standard sigmoid function: 1 / (1 + exp(-x))"""
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))


def tanh_regulator(x: np.ndarray) -> np.ndarray:
    """Tanh-based regulator mapped to [0, 1]: (tanh(x) + 1) / 2"""
    return (np.tanh(x) + 1.0) / 2.0


@dataclass
class TransitionFunction:
    """
    The regime-dependent effective gravitational coupling μ(a).
    
    μ(a) = 1 + Δμ · R((ln a - ln a_t) / σ)
    
    Where:
        - a: scale factor
        - a_t: transition epoch (scale factor at transition center)
        - σ: transition width in ln(a)
        - Δμ: amplitude of enhancement (μ_final - 1)
        - R(x): monotonic regulator function with R(-∞)=0, R(+∞)=1
    
    Attributes:
        delta_mu: Enhancement amplitude (default: 0.1 from Fugaku)
        a_transition: Central transition epoch (default: 0.1, z~9)
        sigma: Transition width (default: 0.5 in ln(a))
        regulator: Regulator function (default: sigmoid)
    
    Example:
        >>> mu = TransitionFunction(delta_mu=0.1)
        >>> mu(1.0)  # μ at present day
        1.0999...
        >>> mu(0.001)  # μ at early times
        1.0000...
    """
    delta_mu: float = 0.1
    a_transition: float = 0.1
    sigma: float = 0.5
    regulator: Callable[[np.ndarray], np.ndarray] = sigmoid
    
    def __call__(self, a: float | np.ndarray) -> float | np.ndarray:
        """
        Evaluate μ(a) at given scale factor(s).
        
        Args:
            a: Scale factor (0 < a ≤ 1, where a=1 is today)
            
        Returns:
            μ(a) = G_eff(a) / G
        """
        a = np.asarray(a)
        
        # Argument to regulator
        x = (np.log(a) - np.log(self.a_transition)) / self.sigma
        
        # μ(a) = 1 + Δμ · R(x)
        mu = 1.0 + self.delta_mu * self.regulator(x)
        
        return float(mu) if mu.ndim == 0 else mu
    
    def derivative(self, a: float | np.ndarray) -> float | np.ndarray:
        """
        Compute dμ/d(ln a) at given scale factor(s).
        
        For sigmoid regulator: dμ/d(ln a) = (Δμ/σ) · R(x) · (1 - R(x))
        """
        a = np.asarray(a)
        x = (np.log(a) - np.log(self.a_transition)) / self.sigma
        R = self.regulator(x)
        
        # For sigmoid: dR/dx = R(1-R)
        dmu_dlna = (self.delta_mu / self.sigma) * R * (1.0 - R)
        
        return float(dmu_dlna) if dmu_dlna.ndim == 0 else dmu_dlna
    
    def get_parameters(self) -> dict:
        """Return dictionary of transition parameters."""
        return {
            "delta_mu": self.delta_mu,
            "a_transition": self.a_transition,
            "z_transition": 1.0 / self.a_transition - 1.0,
            "sigma": self.sigma,
            "regulator": self.regulator.__name__
        }


@dataclass  
class TransitionEstimator:
    """
    The Fugaku/DESI transition estimator Δ_F.
    
    Δ_F ≡ ∫ W(a) · [μ(a) - 1] d(ln a)
    
    Where W(a) is the observational sensitivity kernel for DESI growth/BAO.
    
    The Fugaku-class simulations under DESI-calibrated parameter sets
    yield Δ_F ≈ 0.1, constraining the integrated transition strength.
    
    Reference: DOI 10.6084/m9.figshare.31127380
    
    Attributes:
        mu_function: TransitionFunction instance
        sensitivity_kernel: W(a) function (default: uniform)
    """
    mu_function: TransitionFunction
    sensitivity_kernel: Optional[Callable[[np.ndarray], np.ndarray]] = None
    
    def __post_init__(self):
        if self.sensitivity_kernel is None:
            # Default: uniform sensitivity in DESI window (z ~ 0.1-2, a ~ 0.33-0.9)
            self.sensitivity_kernel = self._default_kernel
    
    @staticmethod
    def _default_kernel(a: np.ndarray) -> np.ndarray:
        """
        Default DESI-like sensitivity kernel.
        
        Peaked around z~0.5-1 (a~0.5-0.67), falls off outside DESI range.
        """
        # Gaussian centered at a=0.5 with width 0.2
        return np.exp(-((a - 0.5) ** 2) / (2 * 0.2 ** 2))
    
    def compute(
        self,
        a_min: float = 0.01,
        a_max: float = 1.0,
        n_points: int = 1000
    ) -> float:
        """
        Compute the transition estimator Δ_F.
        
        Args:
            a_min: Lower integration bound (scale factor)
            a_max: Upper integration bound (scale factor)
            n_points: Number of integration points
            
        Returns:
            Δ_F value (dimensionless)
        """
        # Integration grid in ln(a)
        ln_a = np.linspace(np.log(a_min), np.log(a_max), n_points)
        a = np.exp(ln_a)
        d_ln_a = ln_a[1] - ln_a[0]
        
        # Integrand: W(a) · [μ(a) - 1]
        W = self.sensitivity_kernel(a)
        mu_minus_1 = self.mu_function(a) - 1.0
        
        integrand = W * mu_minus_1
        
        # Trapezoidal integration
        delta_F = np.trapz(integrand, dx=d_ln_a)
        
        # Normalize by integral of W
        W_integral = np.trapz(W, dx=d_ln_a)
        if W_integral > 0:
            delta_F /= W_integral
        
        return delta_F
    
    def fugaku_consistency(self, tolerance: float = 0.03) -> Tuple[bool, float]:
        """
        Check if the estimator is consistent with Fugaku offset (~0.1).
        
        Args:
            tolerance: Allowed deviation from 0.1
            
        Returns:
            (is_consistent, delta_F_value)
        """
        delta_F = self.compute()
        is_consistent = abs(delta_F - 0.1) <= tolerance
        return is_consistent, delta_F


# =============================================================================
# Convenience Functions
# =============================================================================

def create_fugaku_consistent_mu(
    delta_mu: float = 0.1,
    a_transition: float = 0.1,
    sigma: float = 0.5
) -> TransitionFunction:
    """
    Create a transition function consistent with Fugaku/DESI constraints.
    
    Default parameters yield Δ_F ≈ 0.1.
    """
    return TransitionFunction(
        delta_mu=delta_mu,
        a_transition=a_transition,
        sigma=sigma
    )


def mu_at_redshift(z: float, mu_func: TransitionFunction) -> float:
    """
    Evaluate μ at a given redshift.
    
    Args:
        z: Redshift
        mu_func: TransitionFunction instance
        
    Returns:
        μ(z) = μ(a=1/(1+z))
    """
    a = 1.0 / (1.0 + z)
    return mu_func(a)


def check_cmb_consistency(
    mu_func: TransitionFunction,
    z_cmb: float = 1089.0,
    tolerance: float = 0.001
) -> Tuple[bool, float]:
    """
    Check if μ ≈ 1 at CMB epoch (recombination).
    
    Args:
        mu_func: TransitionFunction instance
        z_cmb: CMB redshift (default: 1089)
        tolerance: Maximum allowed deviation from 1
        
    Returns:
        (is_consistent, mu_value)
    """
    mu_cmb = mu_at_redshift(z_cmb, mu_func)
    is_consistent = abs(mu_cmb - 1.0) <= tolerance
    return is_consistent, mu_cmb
