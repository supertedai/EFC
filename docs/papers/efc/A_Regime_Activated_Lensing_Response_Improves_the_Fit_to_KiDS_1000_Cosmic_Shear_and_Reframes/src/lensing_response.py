"""
Lensing Response Model - Reference Implementation

From: Magnusson (2026) "A Regime-Activated Lensing Response Improves the
Fit to KiDS-1000 Cosmic Shear and Reframes the S8 Tension"
DOI: 10.6084/m9.figshare.31271917

This module provides the reference implementation of the regime-activated
lensing response Σ(k,z) that modifies the effective matter power spectrum.
"""

import math
from dataclasses import dataclass
from typing import Tuple, Dict, Any, List
import numpy as np


@dataclass
class LensingResponseParams:
    """Parameters for the lensing response model."""
    alpha: float = 0.10      # Lensing response amplitude
    k_trans: float = 0.1     # Transition wavenumber [h/Mpc]
    z_activ: float = 0.5     # Activation redshift
    delta_k: float = 0.05    # Transition width [h/Mpc]


class LensingResponse:
    """
    Regime-Activated Lensing Response Model.

    The lensing response Σ(k,z) modifies the effective power spectrum:
        P_eff(k,z) = P_ΛCDM(k,z) × Σ²(k,z)

    where:
        Σ(k,z) = Σ_k(k) × Σ_z(z)

        Σ_k(k) = 1 + α × tanh((k - k_trans) / δk)

        Σ_z(z) = 1 + α × (1 - z/z_activ)  for z < z_activ
               = 1                          for z ≥ z_activ

    Physical motivation: In Energy-Flow Cosmology, entropy gradients modify
    the metric perturbation that couples matter to light. This produces
    scale- and redshift-dependent corrections that become significant only
    in the nonlinear regime (k > k_trans) at late times (z < z_activ).
    """

    def __init__(self,
                 alpha: float = 0.10,
                 k_trans: float = 0.1,
                 z_activ: float = 0.5,
                 delta_k: float = 0.05):
        """
        Initialize the lensing response model.

        Args:
            alpha: Lensing response amplitude (default: 0.10)
            k_trans: Transition wavenumber in h/Mpc (default: 0.1)
            z_activ: Activation redshift (default: 0.5)
            delta_k: Transition width in h/Mpc (default: 0.05)
        """
        self.params = LensingResponseParams(
            alpha=alpha,
            k_trans=k_trans,
            z_activ=z_activ,
            delta_k=delta_k
        )

    def sigma_k(self, k: float) -> float:
        """
        Scale-dependent component of lensing response.

        Args:
            k: Wavenumber in h/Mpc

        Returns:
            Σ_k(k) = 1 + α × tanh((k - k_trans) / δk)
        """
        x = (k - self.params.k_trans) / self.params.delta_k
        return 1.0 + self.params.alpha * math.tanh(x)

    def sigma_z(self, z: float) -> float:
        """
        Redshift-dependent component of lensing response.

        Args:
            z: Redshift

        Returns:
            Σ_z(z) = 1 + α × (1 - z/z_activ) for z < z_activ
                   = 1 for z ≥ z_activ
        """
        if z >= self.params.z_activ:
            return 1.0
        return 1.0 + self.params.alpha * (1.0 - z / self.params.z_activ)

    def sigma(self, k: float, z: float) -> float:
        """
        Full lensing response Σ(k,z).

        Args:
            k: Wavenumber in h/Mpc
            z: Redshift

        Returns:
            Σ(k,z) = Σ_k(k) × Σ_z(z)
        """
        return self.sigma_k(k) * self.sigma_z(z)

    def power_ratio(self, k: float, z: float) -> float:
        """
        Ratio of effective to ΛCDM power spectrum.

        Args:
            k: Wavenumber in h/Mpc
            z: Redshift

        Returns:
            P_eff/P_ΛCDM = Σ²(k,z)
        """
        s = self.sigma(k, z)
        return s * s

    def sigma_grid(self,
                   k_array: np.ndarray,
                   z_array: np.ndarray) -> np.ndarray:
        """
        Compute Σ on a (k, z) grid.

        Args:
            k_array: Array of wavenumbers [h/Mpc]
            z_array: Array of redshifts

        Returns:
            2D array of Σ values, shape (len(k_array), len(z_array))
        """
        result = np.zeros((len(k_array), len(z_array)))
        for i, k in enumerate(k_array):
            for j, z in enumerate(z_array):
                result[i, j] = self.sigma(k, z)
        return result


class S8Reframing:
    """
    S8 Tension Reframing Analysis.

    The S8 tension between weak lensing and CMB can be reframed as:

    Standard view:
        S8_WL = σ8 × √(Ωm/0.3)  (assumes Σ=1)
        Tension: S8_WL ≠ S8_CMB

    Reframed view:
        S_WL = σ8 × Σ (effective lensing amplitude)
        When Σ ≈ 1.13: S_WL = 0.734 × 1.13 ≈ 0.83 ≈ S8_CMB

    The apparent tension dissolves when the lensing response is accounted for.
    """

    # Reference values
    KIDS1000_S8 = 0.759
    KIDS1000_S8_ERR = 0.024
    PLANCK_S8 = 0.834
    PLANCK_S8_ERR = 0.016

    def __init__(self):
        pass

    def standard_tension(self, s8_wl: float = None, s8_cmb: float = None) -> Dict[str, float]:
        """
        Calculate standard S8 tension.

        Args:
            s8_wl: Weak lensing S8 (default: KiDS-1000)
            s8_cmb: CMB S8 (default: Planck)

        Returns:
            Dictionary with tension statistics
        """
        s8_wl = s8_wl or self.KIDS1000_S8
        s8_cmb = s8_cmb or self.PLANCK_S8

        diff = s8_wl - s8_cmb
        combined_err = math.sqrt(self.KIDS1000_S8_ERR**2 + self.PLANCK_S8_ERR**2)
        tension_sigma = abs(diff) / combined_err

        return {
            "s8_wl": s8_wl,
            "s8_cmb": s8_cmb,
            "difference": diff,
            "combined_error": combined_err,
            "tension_sigma": tension_sigma
        }

    def reconcile(self,
                  s8_wl: float = None,
                  sigma8_true: float = 0.734,
                  sigma_pivot: float = 1.13) -> Dict[str, float]:
        """
        Reconcile S8 tension using lensing response.

        Args:
            s8_wl: Observed weak lensing S8 (default: KiDS-1000)
            sigma8_true: True σ8 value from theory
            sigma_pivot: Σ value at pivot (k=0.3, z=0.3)

        Returns:
            Dictionary with reframed analysis
        """
        s8_wl = s8_wl or self.KIDS1000_S8

        # Reframed effective lensing amplitude
        s_wl_reframed = sigma8_true * sigma_pivot

        # Residual tension
        diff = s_wl_reframed - self.PLANCK_S8
        tension = abs(diff) / self.PLANCK_S8_ERR

        return {
            "s8_wl_observed": s8_wl,
            "sigma8_true": sigma8_true,
            "sigma_pivot": sigma_pivot,
            "s_wl_reframed": s_wl_reframed,
            "planck_s8": self.PLANCK_S8,
            "residual_difference": diff,
            "residual_tension_sigma": tension,
            "tension_resolved": tension < 1.0
        }

    def infer_sigma(self, s8_wl: float, sigma8_true: float) -> float:
        """
        Infer required Σ to reconcile S8 values.

        Args:
            s8_wl: Observed weak lensing S8
            sigma8_true: True σ8 value

        Returns:
            Required Σ value
        """
        return s8_wl / sigma8_true


class TomographicFingerprint:
    """
    Analysis of tomographic fingerprint in likelihood improvement.

    Key prediction: Improvement should be strongest at low redshift
    where structures are most evolved and entropy gradients largest.

    Results from KiDS-1000:
    - Low-z bins (z < 0.5): 3.2× average improvement per datapoint
    - High-z bins (z > 0.7): 0.4× average improvement per datapoint
    """

    def __init__(self):
        # Improvement factors from paper
        self.low_z_factor = 3.2
        self.high_z_factor = 0.4
        self.dividing_z = 0.5

    def expected_improvement(self, z_eff: float) -> float:
        """
        Expected improvement factor based on effective redshift.

        Args:
            z_eff: Effective redshift of tomographic bin pair

        Returns:
            Improvement factor relative to average
        """
        if z_eff < self.dividing_z:
            return self.low_z_factor
        else:
            # Linear interpolation
            if z_eff > 0.7:
                return self.high_z_factor
            # Between 0.5 and 0.7
            frac = (z_eff - 0.5) / 0.2
            return self.low_z_factor + frac * (self.high_z_factor - self.low_z_factor)

    def prediction_matches(self) -> Dict[str, Any]:
        """
        Check if tomographic fingerprint matches prediction.

        Returns:
            Dictionary with prediction comparison
        """
        return {
            "prediction": "Stronger improvement at low-z",
            "observed_low_z_factor": self.low_z_factor,
            "observed_high_z_factor": self.high_z_factor,
            "ratio": self.low_z_factor / self.high_z_factor,
            "matches_prediction": self.low_z_factor > self.high_z_factor
        }


class LikelihoodAnalysis:
    """
    Likelihood improvement analysis for KiDS-1000.
    """

    def __init__(self):
        # Results from paper
        self.delta_minus2lnL = -50.9
        self.additional_params = 3

    def delta_chi2(self) -> float:
        """Return Δχ² improvement."""
        return self.delta_minus2lnL

    def delta_aic(self) -> float:
        """
        Calculate ΔAIC (Akaike Information Criterion).

        AIC = -2lnL + 2k
        ΔAIC = Δ(-2lnL) + 2×Δk
        """
        return self.delta_minus2lnL + 2 * self.additional_params

    def delta_bic(self, n_data: int = 770) -> float:
        """
        Calculate ΔBIC (Bayesian Information Criterion).

        BIC = -2lnL + k×ln(n)
        ΔBIC = Δ(-2lnL) + Δk×ln(n)

        Args:
            n_data: Number of data points (KiDS-1000 ~770)
        """
        return self.delta_minus2lnL + self.additional_params * math.log(n_data)

    def summary(self, n_data: int = 770) -> Dict[str, float]:
        """
        Full likelihood summary.

        Args:
            n_data: Number of data points

        Returns:
            Dictionary with all likelihood metrics
        """
        return {
            "delta_minus2lnL": self.delta_minus2lnL,
            "delta_chi2": self.delta_chi2(),
            "additional_parameters": self.additional_params,
            "delta_AIC": self.delta_aic(),
            "delta_BIC": self.delta_bic(n_data),
            "preferred_model": "ΛCDM+Σ" if self.delta_minus2lnL < 0 else "ΛCDM"
        }


def demonstrate():
    """Demonstrate the lensing response model."""
    print("=" * 60)
    print("LENSING RESPONSE MODEL DEMONSTRATION")
    print("=" * 60)

    # Initialize with best-fit parameters
    model = LensingResponse(alpha=0.10, k_trans=0.1, z_activ=0.5)

    # Calculate at pivot point
    k_pivot, z_pivot = 0.3, 0.3
    sigma = model.sigma(k_pivot, z_pivot)
    print(f"\nAt pivot (k={k_pivot}, z={z_pivot}):")
    print(f"  Σ = {sigma:.4f}")
    print(f"  P_eff/P_ΛCDM = {model.power_ratio(k_pivot, z_pivot):.4f}")

    # Show scale dependence
    print("\nScale dependence Σ_k(k):")
    for k in [0.01, 0.05, 0.1, 0.2, 0.5, 1.0]:
        print(f"  k={k:.2f} h/Mpc: Σ_k = {model.sigma_k(k):.4f}")

    # Show redshift dependence
    print("\nRedshift dependence Σ_z(z):")
    for z in [0.0, 0.2, 0.4, 0.5, 0.7, 1.0]:
        print(f"  z={z:.1f}: Σ_z = {model.sigma_z(z):.4f}")

    # S8 reframing
    print("\n" + "=" * 60)
    print("S8 TENSION REFRAMING")
    print("=" * 60)

    reframe = S8Reframing()

    # Standard tension
    tension = reframe.standard_tension()
    print(f"\nStandard analysis:")
    print(f"  S8_WL (KiDS-1000) = {tension['s8_wl']:.3f}")
    print(f"  S8_CMB (Planck) = {tension['s8_cmb']:.3f}")
    print(f"  Tension = {tension['tension_sigma']:.1f}σ")

    # Reframed
    reconciled = reframe.reconcile()
    print(f"\nReframed analysis:")
    print(f"  σ8_true = {reconciled['sigma8_true']:.3f}")
    print(f"  Σ(pivot) = {reconciled['sigma_pivot']:.3f}")
    print(f"  S_WL = σ8 × Σ = {reconciled['s_wl_reframed']:.3f}")
    print(f"  S8_CMB = {reconciled['planck_s8']:.3f}")
    print(f"  Residual tension = {reconciled['residual_tension_sigma']:.1f}σ")
    print(f"  Tension resolved: {reconciled['tension_resolved']}")

    # Likelihood
    print("\n" + "=" * 60)
    print("LIKELIHOOD IMPROVEMENT")
    print("=" * 60)

    like = LikelihoodAnalysis()
    summary = like.summary()
    print(f"\n  Δ(-2lnL) = {summary['delta_minus2lnL']:.1f}")
    print(f"  Additional parameters = {summary['additional_parameters']}")
    print(f"  ΔAIC = {summary['delta_AIC']:.1f}")
    print(f"  ΔBIC = {summary['delta_BIC']:.1f}")
    print(f"  Preferred: {summary['preferred_model']}")


if __name__ == "__main__":
    demonstrate()
