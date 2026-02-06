#!/usr/bin/env python3
"""
Entropy-Structure Coupling Analysis

Reference implementation for:
Magnusson (2026) "A Pre-Registered Test of Entropy–Structure Coupling
in Simulated and Observed Galaxy Clusters"
DOI: 10.6084/m9.figshare.31286368

This module provides tools for analyzing entropy profiles in galaxy clusters
and comparing simulation results with observational data.
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, List, Optional, Dict
from enum import Enum


class CoolCoreClass(Enum):
    """Cool-core classification following Hudson et al. (2010)."""
    SCC = "Strong Cool-Core"  # K0 <= 22 keV cm^2
    WCC = "Weak Cool-Core"    # 22 < K0 <= 150 keV cm^2
    NCC = "Non-Cool-Core"     # K0 > 150 keV cm^2


@dataclass
class EntropyProfileParams:
    """Parameters for Cavagnolo et al. (2009) entropy profile model."""
    K0: float       # Central entropy [keV cm^2]
    K100: float     # Entropy normalisation at 100 kpc [keV cm^2]
    alpha: float    # Power-law index


@dataclass
class CorrelationResult:
    """Result of a Spearman correlation analysis."""
    rho: float
    p_value: float
    N: int
    description: str = ""


class EntropyProfileModel:
    """
    Cavagnolo et al. (2009) entropy profile model.

    K(r) = K0 + K100 × (r / 100 kpc)^α

    This is the standard parametric form for cluster entropy profiles
    used in the ACCEPT sample analysis.
    """

    def __init__(self, K0: float, K100: float, alpha: float):
        """
        Initialize entropy profile model.

        Parameters
        ----------
        K0 : float
            Central entropy [keV cm^2]
        K100 : float
            Entropy normalisation at 100 kpc [keV cm^2]
        alpha : float
            Power-law index (entropy gradient steepness)
        """
        self.params = EntropyProfileParams(K0=K0, K100=K100, alpha=alpha)

    def entropy(self, r: float) -> float:
        """
        Compute entropy at radius r.

        Parameters
        ----------
        r : float
            Radius [kpc]

        Returns
        -------
        K : float
            Entropy [keV cm^2]
        """
        return self.params.K0 + self.params.K100 * (r / 100.0) ** self.params.alpha

    def entropy_profile(self, r_array: np.ndarray) -> np.ndarray:
        """
        Compute entropy profile over array of radii.

        Parameters
        ----------
        r_array : np.ndarray
            Radii [kpc]

        Returns
        -------
        K_array : np.ndarray
            Entropy values [keV cm^2]
        """
        return self.params.K0 + self.params.K100 * (r_array / 100.0) ** self.params.alpha

    def log_slope(self, r: float) -> float:
        """
        Compute logarithmic slope d ln K / d ln r at radius r.

        Parameters
        ----------
        r : float
            Radius [kpc]

        Returns
        -------
        slope : float
            Logarithmic slope
        """
        K = self.entropy(r)
        dK_dr = self.params.K100 * self.params.alpha / 100.0 * (r / 100.0) ** (self.params.alpha - 1)
        return r * dK_dr / K

    @staticmethod
    def from_gas_properties(T: float, n_e: float) -> float:
        """
        Compute entropy from temperature and electron density.

        K = k_B T × n_e^(-2/3)

        Parameters
        ----------
        T : float
            Temperature [keV]
        n_e : float
            Electron density [cm^-3]

        Returns
        -------
        K : float
            Entropy [keV cm^2]
        """
        return T * n_e ** (-2.0 / 3.0)


class AlphaProxy:
    """
    Proxy for entropy gradient α based on density slope.

    α_proxy = (2/3) × n_e-slope

    This represents the density contribution to the entropy gradient
    and is a lower bound on α under the physical expectation that
    temperature rises with radius in cluster cores.
    """

    @staticmethod
    def compute(ne_slope: float) -> float:
        """
        Compute α_proxy from electron density slope.

        Parameters
        ----------
        ne_slope : float
            Logarithmic electron density slope (-d ln n_e / d ln r)

        Returns
        -------
        alpha_proxy : float
            Proxy for entropy power-law index
        """
        return (2.0 / 3.0) * ne_slope

    @staticmethod
    def entropy_slope_decomposition(T_slope: float, ne_slope: float) -> float:
        """
        Compute full entropy slope from temperature and density slopes.

        α = d ln T / d ln r + (2/3) × n_e-slope

        Parameters
        ----------
        T_slope : float
            Logarithmic temperature slope (d ln T / d ln r)
        ne_slope : float
            Logarithmic density slope contribution ((2/3) × (-d ln n_e / d ln r))

        Returns
        -------
        alpha : float
            Full entropy power-law index
        """
        return T_slope + (2.0 / 3.0) * ne_slope


class CoolCoreClassifier:
    """
    Galaxy cluster cool-core classification following Hudson et al. (2010).

    Thresholds based on central entropy K0:
    - SCC (Strong Cool-Core): K0 ≤ 22 keV cm²
    - WCC (Weak Cool-Core): 22 < K0 ≤ 150 keV cm²
    - NCC (Non-Cool-Core): K0 > 150 keV cm²
    """

    SCC_THRESHOLD = 22.0   # keV cm^2
    WCC_THRESHOLD = 150.0  # keV cm^2

    def classify(self, K0: float) -> CoolCoreClass:
        """
        Classify cluster based on central entropy.

        Parameters
        ----------
        K0 : float
            Central entropy [keV cm^2]

        Returns
        -------
        cc_class : CoolCoreClass
            Cool-core classification
        """
        if K0 <= self.SCC_THRESHOLD:
            return CoolCoreClass.SCC
        elif K0 <= self.WCC_THRESHOLD:
            return CoolCoreClass.WCC
        else:
            return CoolCoreClass.NCC

    def classify_str(self, K0: float) -> str:
        """Return classification as string."""
        return self.classify(K0).name

    @staticmethod
    def tng_population() -> Dict[str, Dict[str, float]]:
        """
        Return TNG-Cluster cool-core population statistics.

        Returns
        -------
        population : dict
            Counts and fractions for each CC class
        """
        return {
            "SCC": {"count": 28, "fraction": 0.08},
            "WCC": {"count": 206, "fraction": 0.59},
            "NCC": {"count": 118, "fraction": 0.34},
            "total": {"count": 352}
        }


class CorrelationAnalysis:
    """
    Correlation analysis for entropy-structure coupling.

    Compares TNG-Cluster simulation results with ACCEPT observations.
    """

    # TNG-Cluster results from Lehle et al. (2024) catalogue
    TNG_RESULTS = {
        "ne_slope_vs_K0": CorrelationResult(
            rho=-0.872, p_value=8e-111, N=352,
            description="Electron density slope vs central entropy"
        ),
        "ne_slope_vs_tcool": CorrelationResult(
            rho=-0.878, p_value=7e-114, N=352,
            description="Electron density slope vs cooling time"
        ),
        "Cphys_vs_K0": CorrelationResult(
            rho=-0.927, p_value=0.0, N=352,
            description="X-ray concentration vs central entropy"
        ),
        "Cphys_vs_ne_slope": CorrelationResult(
            rho=0.875, p_value=0.0, N=352,
            description="X-ray concentration vs density slope"
        ),
    }

    # Mass-controlled results
    PARTIAL_CORRELATIONS = {
        "ne_slope_vs_K0_given_M": CorrelationResult(
            rho=-0.880, p_value=2e-115, N=352,
            description="Density slope vs K0, controlling for mass"
        ),
        "alpha_proxy_vs_K0_given_M": CorrelationResult(
            rho=-0.880, p_value=2e-115, N=352,
            description="Alpha proxy vs K0, controlling for mass"
        ),
        "alpha_proxy_vs_tcool_given_M": CorrelationResult(
            rho=-0.876, p_value=1e-112, N=352,
            description="Alpha proxy vs tcool, controlling for mass"
        ),
    }

    # ACCEPT observational reference
    ACCEPT_RESULT = CorrelationResult(
        rho=0.36, p_value=0.0, N=239,
        description="ACCEPT: alpha vs y_CCT (Cavagnolo et al. 2009)"
    )

    def tng_correlation(self, variable: str = "ne_slope_vs_K0") -> CorrelationResult:
        """
        Get TNG-Cluster correlation result.

        Parameters
        ----------
        variable : str
            Correlation to retrieve

        Returns
        -------
        result : CorrelationResult
        """
        return self.TNG_RESULTS.get(variable, self.TNG_RESULTS["ne_slope_vs_K0"])

    def accept_correlation(self) -> CorrelationResult:
        """Get ACCEPT observational correlation."""
        return self.ACCEPT_RESULT

    def sign_flip_detected(self) -> bool:
        """
        Check if sign flip is detected between TNG and ACCEPT.

        Returns
        -------
        sign_flip : bool
            True if correlations have opposite signs
        """
        tng_rho = self.TNG_RESULTS["ne_slope_vs_K0"].rho
        accept_rho = self.ACCEPT_RESULT.rho
        return (tng_rho * accept_rho) < 0

    def mass_binned_results(self) -> List[Dict]:
        """
        Get mass-binned correlation results.

        Returns
        -------
        results : list of dict
            Correlation results for each mass bin
        """
        return [
            {"bin": "[14.0, 14.3)", "N": 41, "rho": -0.790, "p_value": 9e-10},
            {"bin": "[14.3, 14.6)", "N": 118, "rho": -0.860, "p_value": 1e-35},
            {"bin": "[14.6, 14.9)", "N": 121, "rho": -0.901, "p_value": 5e-45},
            {"bin": "[14.9, 15.5)", "N": 71, "rho": -0.897, "p_value": 4e-26},
        ]

    def summary(self) -> Dict:
        """
        Get summary of correlation analysis.

        Returns
        -------
        summary : dict
            Key results and comparison
        """
        return {
            "tng_rho": self.TNG_RESULTS["ne_slope_vs_K0"].rho,
            "accept_rho": self.ACCEPT_RESULT.rho,
            "sign_flip": self.sign_flip_detected(),
            "partial_rho_mass_controlled": self.PARTIAL_CORRELATIONS["ne_slope_vs_K0_given_M"].rho,
            "mass_contribution": "0%",
            "all_mass_bins_negative": True,
            "interpretation": "Complete sign reversal, not driven by mass confounding"
        }


class PreRegisteredTest:
    """
    Pre-registered test design for entropy-structure coupling.

    Two-stage approach:
    - Path B: Proxy-based pre-test (completed)
    - Path A: Full Cavagnolo-model fit (awaiting execution)
    """

    @dataclass
    class PathAParams:
        """Locked parameters for Path A decisive test."""
        centre: str = "SUBFIND-determined"
        fit_range_kpc: Tuple[float, float] = (20.0, 400.0)
        initial_alpha_guess: float = 1.1  # ACCEPT median
        binning: str = "mass-weighted"
        n_radial_bins: int = 30
        min_bin_occupancy: int = 5
        gas_selection: str = "non-star-forming, T > 1e6 K"

    def __init__(self):
        self.path_a_params = self.PathAParams()
        self.path_b_completed = True
        self.path_b_result = "Sign flip confirmed"

    def stop_go_criterion(self, rho_alpha_K0: float, rho_alpha_tcool: Optional[float] = None) -> str:
        """
        Evaluate pre-registered stop/go criterion.

        Parameters
        ----------
        rho_alpha_K0 : float
            Correlation between fitted alpha and K0
        rho_alpha_tcool : float, optional
            Correlation between fitted alpha and tcool

        Returns
        -------
        decision : str
            "STOP", "GO", or "PARTIAL"
        """
        if rho_alpha_K0 < 0:
            return "GO"  # Sign flip survives → genuine mismatch
        elif rho_alpha_tcool is not None and rho_alpha_K0 > 0 and rho_alpha_tcool > 0:
            return "STOP"  # Sign flip reverses under definition matching
        else:
            return "PARTIAL"  # Mixed signs require further investigation

    def path_b_summary(self) -> Dict:
        """Get Path B (proxy-based pre-test) summary."""
        return {
            "status": "completed",
            "proxy": "alpha_proxy = (2/3) × ne_slope",
            "result": self.path_b_result,
            "correlations": {
                "alpha_proxy_vs_K0": -0.872,
                "alpha_proxy_vs_K0_partial_M": -0.880,
                "alpha_proxy_vs_tcool": -0.878,
                "alpha_proxy_vs_tcool_partial_M": -0.876,
            },
            "verdict": "GO - Sign flip survives definition matching"
        }

    def path_a_summary(self) -> Dict:
        """Get Path A (decisive full profile fit) summary."""
        return {
            "status": "pre-registered, awaiting execution",
            "description": "Full Cavagnolo-model K(r) = K0 + K100(r/100)^alpha fit",
            "parameters": {
                "centre": self.path_a_params.centre,
                "fit_range_kpc": self.path_a_params.fit_range_kpc,
                "initial_alpha_guess": self.path_a_params.initial_alpha_guess,
                "binning": self.path_a_params.binning,
                "n_radial_bins": self.path_a_params.n_radial_bins,
                "min_bin_occupancy": self.path_a_params.min_bin_occupancy,
            },
            "purpose": "Eliminate systematic ambiguities: T-slope variation, local vs global slope, radius mismatch"
        }


class InterpretationFramework:
    """
    Framework for interpreting entropy-structure coupling results.

    If sign flip is confirmed, three explanations must be considered.
    """

    POSSIBLE_EXPLANATIONS = [
        {
            "name": "Subgrid modelling",
            "description": "AGN feedback in TNG may produce overly mechanical CC/NCC transitions that couple structure and entropy too tightly and in the wrong direction.",
            "testable": "Compare with FLAMINGO, SIMBA, MillenniumTNG"
        },
        {
            "name": "Observational systematics",
            "description": "Projection effects, spectral fitting biases, or selection effects in ACCEPT could weaken or reverse the intrinsic correlation.",
            "testable": "Forward-modelled mock X-ray observations of TNG-Cluster"
        },
        {
            "name": "Missing physics",
            "description": "Physical processes not captured by TNG (cosmic ray transport, anisotropic conduction, magnetic draping) may be required.",
            "testable": "Simulations with additional physics modules"
        },
    ]

    SYSTEMATIC_DIFFERENCES = [
        "TNG profiles: intrinsic 3D mass-weighted quantities",
        "ACCEPT profiles: deprojected X-ray spectroscopic with emission weighting",
        "TNG sample: mass-selected",
        "ACCEPT sample: X-ray selected, flux-limited",
        "These affect absolute normalisation but not expected to reverse rank-order correlations"
    ]

    def get_implications(self) -> str:
        """Get key implication of confirmed sign flip."""
        return (
            "Framework-independent question: Why do modern ΛCDM hydrodynamic "
            "simulations not reproduce the observed relationship between core "
            "entropy and structural gradients in galaxy clusters? This is an "
            "ICM physics question with implications for AGN feedback modelling, "
            "thermal conduction prescriptions, and CC/NCC demographics."
        )


# Convenience functions

def compute_entropy(T: float, n_e: float) -> float:
    """
    Compute entropy from temperature and electron density.

    K = k_B T × n_e^(-2/3)

    Parameters
    ----------
    T : float
        Temperature [keV]
    n_e : float
        Electron density [cm^-3]

    Returns
    -------
    K : float
        Entropy [keV cm^2]
    """
    return EntropyProfileModel.from_gas_properties(T, n_e)


def classify_cool_core(K0: float) -> str:
    """
    Classify cluster cool-core state from central entropy.

    Parameters
    ----------
    K0 : float
        Central entropy [keV cm^2]

    Returns
    -------
    classification : str
        "SCC", "WCC", or "NCC"
    """
    return CoolCoreClassifier().classify_str(K0)


def compute_alpha_proxy(ne_slope: float) -> float:
    """
    Compute entropy gradient proxy from density slope.

    Parameters
    ----------
    ne_slope : float
        Electron density logarithmic slope

    Returns
    -------
    alpha_proxy : float
        Proxy for entropy power-law index
    """
    return AlphaProxy.compute(ne_slope)
