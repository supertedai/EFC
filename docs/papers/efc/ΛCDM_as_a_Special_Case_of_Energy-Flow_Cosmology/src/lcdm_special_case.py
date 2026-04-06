"""
LCDM as a Special Case of Energy-Flow Cosmology
=================================================

Reference implementation of the core equations, diagnostics, and
predictions from Magnusson (2026).

DOI: 10.6084/m9.figshare.31943361
License: CC-BY-4.0
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Eq. 1 -- Regime driver
# ---------------------------------------------------------------------------

class RegimeDriver:
    """Dimensionless entropy-gradient intensity (Eq. 1).

    chi = ell * |grad S| / S_*

    Parameters
    ----------
    ell : float
        Grid scale.
    S_star : float
        Normalisation constant.
    """

    def __init__(self, ell: float = 1.0, S_star: float = 1.0):
        self.ell = ell
        self.S_star = S_star

    def chi(self, grad_S_mag):
        """Compute the regime driver chi.

        Parameters
        ----------
        grad_S_mag : float or array
            Magnitude of the entropy gradient |nabla S|.

        Returns
        -------
        float or array
            Dimensionless regime driver chi.
        """
        return self.ell * np.abs(grad_S_mag) / self.S_star

    def classify_regime(self, chi_val: float) -> str:
        """Classify the physical regime from chi value.

        Parameters
        ----------
        chi_val : float
            Value of the regime driver.

        Returns
        -------
        str
            Regime label: L0, L1, L2, or L3.
        """
        if chi_val < 0.01:
            return "L0"  # Global background
        elif chi_val < 0.1:
            return "L1"  # Linear perturbations
        elif chi_val < 1.0:
            return "L2"  # Non-linear structure
        else:
            return "L3"  # Local dynamics


# ---------------------------------------------------------------------------
# Eq. 2 -- Constitutive law
# ---------------------------------------------------------------------------

class ConstitutiveLaw:
    """Energy-flow response to entropy gradients (Eq. 2).

    E_f = -kappa(chi) * grad S

    Analogous to Fourier's law in heat conduction.

    Parameters
    ----------
    kappa_0 : float
        Base transport coefficient.
    """

    def __init__(self, kappa_0: float = 1.0):
        self.kappa_0 = kappa_0

    def kappa(self, chi):
        """Regime-dependent transport coefficient.

        Parameters
        ----------
        chi : float or array
            Regime driver value.

        Returns
        -------
        float or array
            Transport coefficient kappa(chi).
        """
        return self.kappa_0 * (1.0 + chi**2)

    def energy_flow(self, chi, grad_S):
        """Compute the energy flow E_f = -kappa(chi) * grad S.

        Parameters
        ----------
        chi : float or array
            Regime driver.
        grad_S : float or array
            Entropy gradient.

        Returns
        -------
        float or array
            Energy flow magnitude.
        """
        return -self.kappa(chi) * grad_S


# ---------------------------------------------------------------------------
# Eq. 4 -- Effective coupling
# ---------------------------------------------------------------------------

class EffectiveCoupling:
    """Effective gravitational coupling mu (Eqs. 3-4).

    mu(chi, k, z) = 1 + epsilon(k) * F(chi)

    where epsilon(k) encodes scale-dependent amplitude and F(chi) is a
    monotonic activation function with F -> 0 in GR and F -> 1 in the
    deep-gradient regime.

    Parameters
    ----------
    C : float
        Cross-scale consistency constant (C^2 - 1 approx 4.4 from KT2).
    k_screen : float
        Screening parameter (k = 0.415 from SPARC).
    """

    def __init__(self, C: float = 2.32, k_screen: float = 0.415):
        self.C = C
        self.k_screen = k_screen

    def epsilon(self, k):
        """Scale-dependent amplitude epsilon(k).

        Parameters
        ----------
        k : float or array
            Wavenumber or scale parameter.

        Returns
        -------
        float or array
            Amplitude factor.
        """
        return (self.C**2 - 1.0) / (1.0 + (k / self.k_screen) ** 2)

    def F(self, chi):
        """Monotonic activation function F(chi).

        F -> 0 in the GR regime (chi -> 0).
        F -> 1 in the deep-gradient regime (chi -> inf).

        Parameters
        ----------
        chi : float or array
            Regime driver.

        Returns
        -------
        float or array
            Activation value.
        """
        return chi**2 / (1.0 + chi**2)

    def mu(self, chi, k=1.0, z=0.0):
        """Effective gravitational coupling mu(chi, k, z) (Eq. 4).

        Parameters
        ----------
        chi : float or array
            Regime driver.
        k : float or array
            Scale parameter.
        z : float
            Redshift (reserved for future redshift dependence).

        Returns
        -------
        float or array
            Effective coupling mu.
        """
        return 1.0 + self.epsilon(k) * self.F(chi)


# ---------------------------------------------------------------------------
# Eq. 6 -- LCDM reduction
# ---------------------------------------------------------------------------

class LCDMReduction:
    """Verifies the LCDM special-case limit (Eq. 6).

    K(rho) -> inf, T(a) -> 0, xi >> 1
      ==> mu, Sigma, eta -> 1
      ==> Friedmann + Poisson

    Three physical conditions (high density, early time, strong
    acceleration) collapse all EFC modifications to zero, recovering
    standard LCDM identically.
    """

    def __init__(
        self,
        K_rho: float = 1e10,
        T_a: float = 1e-10,
        xi: float = 1e4,
    ):
        self.K_rho = K_rho
        self.T_a = T_a
        self.xi = xi

    def suppression_factor(self) -> float:
        """Compute the total EFC suppression factor.

        In the LCDM limit, this approaches zero.

        Returns
        -------
        float
            Suppression factor (0 = full LCDM recovery).
        """
        return self.T_a / (1.0 + self.xi) * (1.0 / self.K_rho)

    def mu(self) -> float:
        """Effective gravitational coupling in the reduction limit."""
        return 1.0 + self.suppression_factor()

    def sigma(self) -> float:
        """Lensing response Sigma in the reduction limit."""
        return 1.0 + self.suppression_factor()

    def eta(self) -> float:
        """Gravitational slip eta in the reduction limit."""
        return 1.0 + self.suppression_factor()

    def verify_reduction(self, tol: float = 1e-6) -> Dict[str, object]:
        """Verify that all modification functions approach unity.

        Parameters
        ----------
        tol : float
            Tolerance for deviation from 1.

        Returns
        -------
        dict
            Verification results for mu, Sigma, and eta.
        """
        return {
            "mu_to_1": abs(self.mu() - 1.0) < tol,
            "sigma_to_1": abs(self.sigma() - 1.0) < tol,
            "eta_to_1": abs(self.eta() - 1.0) < tol,
            "suppression": self.suppression_factor(),
            "all_pass": (
                abs(self.mu() - 1.0) < tol
                and abs(self.sigma() - 1.0) < tol
                and abs(self.eta() - 1.0) < tol
            ),
        }

    @staticmethod
    def conditions() -> List[Dict[str, str]]:
        """Return the three reduction conditions."""
        return [
            {
                "parameter": "K(rho)",
                "limit": "infinity",
                "meaning": "High density (entropy-stiffness mechanism)",
            },
            {
                "parameter": "T(a)",
                "limit": "0",
                "meaning": "Early universe / linear regime",
            },
            {
                "parameter": "xi",
                "limit": ">> 1",
                "meaning": "Strong acceleration (UV regime)",
            },
        ]


# ---------------------------------------------------------------------------
# Eq. 7 -- Background modification
# ---------------------------------------------------------------------------

class BackgroundModification:
    """Modified Friedmann equation with logistic gate (Eq. 7).

    E^2(a) = Omega_m * a^{-3} + (1 - Omega_m) + alpha * [g(a) - g(1)]

    Parameters
    ----------
    Omega_m : float
        Matter density parameter.
    alpha : float
        Background coupling amplitude.
    a_gate : float
        Gate transition scale factor.
    delta_gate : float
        Gate width.
    """

    def __init__(
        self,
        Omega_m: float = 0.315,
        alpha: float = -0.14,
        a_gate: float = 0.5,
        delta_gate: float = 0.1,
    ):
        self.Omega_m = Omega_m
        self.alpha = alpha
        self.a_gate = a_gate
        self.delta_gate = delta_gate

    def gate(self, a):
        """Logistic gate function g(a).

        Parameters
        ----------
        a : float or array
            Scale factor.

        Returns
        -------
        float or array
            Gate value.
        """
        return 1.0 / (1.0 + np.exp(-(a - self.a_gate) / self.delta_gate))

    def E_squared(self, a):
        """Compute E^2(a) = (H(a)/H0)^2 (Eq. 7).

        Parameters
        ----------
        a : float or array
            Scale factor.

        Returns
        -------
        float or array
            Dimensionless Hubble parameter squared.
        """
        matter = self.Omega_m * a ** (-3)
        dark_energy = 1.0 - self.Omega_m
        modification = self.alpha * (self.gate(a) - self.gate(1.0))
        return matter + dark_energy + modification

    def E_squared_lcdm(self, a):
        """Standard LCDM E^2(a) for comparison.

        Parameters
        ----------
        a : float or array
            Scale factor.

        Returns
        -------
        float or array
            LCDM dimensionless Hubble parameter squared.
        """
        return self.Omega_m * a ** (-3) + (1.0 - self.Omega_m)

    def fractional_deviation(self, a):
        """Fractional deviation from LCDM: (E^2_EFC - E^2_LCDM) / E^2_LCDM.

        Parameters
        ----------
        a : float or array
            Scale factor.

        Returns
        -------
        float or array
            Fractional deviation.
        """
        e2_efc = self.E_squared(a)
        e2_lcdm = self.E_squared_lcdm(a)
        return (e2_efc - e2_lcdm) / e2_lcdm


# ---------------------------------------------------------------------------
# DESI DR2 result
# ---------------------------------------------------------------------------

@dataclass
class DESIDR2Result:
    """DESI DR2 multi-probe analysis result (Eq. 8).

    alpha = -0.14 +/- 0.21 (0.65 sigma from null)
    delta_AIC = +1.59 (LCDM preferred)
    """

    alpha: float = -0.14
    alpha_uncertainty: float = 0.21
    significance_sigma: float = 0.65
    delta_aic: float = 1.59
    lcdm_preferred: bool = True
    pre_dr2_alpha: float = -0.67
    pre_dr2_uncertainty: float = 0.40
    data_points: int = 69

    # Robustness diagnostics (Table 2)
    diagnostics: Dict[str, str] = field(default_factory=lambda: {
        "N1": "COLLAPSED",
        "N2": "COLLAPSED",
        "N3": "COLLAPSED",
        "N4": "COLLAPSED",
        "N5": "PASS",
        "N6": "SAFETY_FAIL",
        "N7": "MARGINAL",
        "VG": "WEAK",
    })

    diagnostic_details: Dict[str, str] = field(default_factory=lambda: {
        "N1": "Sound horizon freedom: alpha does not survive rd freedom",
        "N2": "sigma8 sweep: alpha unstable under sigma8 variation",
        "N3": "Gate freedom: gate parameters absorb alpha signal",
        "N4": "mu0 sweep: alpha moves <1sigma across mu0 in [0.8, 1.2]",
        "N5": "rd prior: corr(alpha, rd) approx 0; not rd-driven",
        "N6": "Safety delta_rd: delta_rd = -0.507% trips 0.5% threshold by 0.007%",
        "N7": "Geff growth: weak growth-sector signal",
        "VG": "Variant gravity: mu-amplitude 0.06-5.5%; delta log L_growth < 0",
    })

    def is_consistent_with_lcdm(self) -> bool:
        """Check whether alpha is consistent with zero (LCDM)."""
        return abs(self.alpha) < 2.0 * self.alpha_uncertainty

    def alpha_shift(self) -> float:
        """Shift from pre-DR2 to DR2 value."""
        return self.alpha - self.pre_dr2_alpha

    def summary(self) -> Dict[str, object]:
        """Return a summary dictionary."""
        return {
            "alpha": f"{self.alpha} +/- {self.alpha_uncertainty}",
            "significance": f"{self.significance_sigma} sigma",
            "delta_AIC": self.delta_aic,
            "lcdm_preferred": self.lcdm_preferred,
            "shift_from_pre_dr2": f"{self.alpha_shift():+.2f}",
            "consistent_with_lcdm": self.is_consistent_with_lcdm(),
            "collapsed_diagnostics": [
                k for k, v in self.diagnostics.items() if v == "COLLAPSED"
            ],
        }


# ---------------------------------------------------------------------------
# Perturbation survival valley (Eq. 9)
# ---------------------------------------------------------------------------

@dataclass
class PerturbationValley:
    """Narrow survival zone for EFC perturbation parameters (Eq. 9).

    mu in [0.93, 0.96]
    Sigma in [1.03, 1.07]
    eta != 1 (required)
    """

    mu_range: Tuple[float, float] = (0.93, 0.96)
    mu_central: float = 0.94
    sigma_range: Tuple[float, float] = (1.03, 1.07)
    sigma_central: float = 1.05
    eta_central: float = 1.10
    eta_not_one: bool = True

    def in_valley(self, mu: float, sigma: float) -> bool:
        """Check whether (mu, Sigma) falls within the survival valley.

        Parameters
        ----------
        mu : float
            Effective gravitational coupling.
        sigma : float
            Lensing response.

        Returns
        -------
        bool
            True if within the valley.
        """
        mu_ok = self.mu_range[0] <= mu <= self.mu_range[1]
        sigma_ok = self.sigma_range[0] <= sigma <= self.sigma_range[1]
        return mu_ok and sigma_ok

    def summary(self) -> Dict[str, object]:
        """Return a summary of the survival valley."""
        return {
            "mu_range": list(self.mu_range),
            "mu_central": self.mu_central,
            "sigma_range": list(self.sigma_range),
            "sigma_central": self.sigma_central,
            "eta_central": self.eta_central,
            "eta_neq_1": self.eta_not_one,
            "central_in_valley": self.in_valley(
                self.mu_central, self.sigma_central
            ),
        }


# ---------------------------------------------------------------------------
# Gas-law analogy (Table 5)
# ---------------------------------------------------------------------------

class GasLawAnalogy:
    """The special-case correspondence (Table 5).

    LCDM is to EFC what the ideal gas law (PV = nRT) is to statistical
    mechanics: a correct and useful special case valid in one regime,
    embedded within a richer structure.
    """

    TABLE: List[Dict[str, str]] = [
        {
            "aspect": "Effective theory",
            "thermodynamics": "Ideal gas law (PV = nRT)",
            "cosmology": "LCDM (Friedmann + Lambda)",
        },
        {
            "aspect": "Valid regime",
            "thermodynamics": "Gas phase (low density, high T)",
            "cosmology": "L0/L1 (linear, homogeneous, xi >> 1)",
        },
        {
            "aspect": "Deeper framework",
            "thermodynamics": "Statistical mechanics",
            "cosmology": "EFC (entropy-flow action)",
        },
        {
            "aspect": "Reduction mechanism",
            "thermodynamics": "Intermolecular forces -> 0",
            "cosmology": "K(rho) -> inf, T(a) -> 0, xi >> 1",
        },
        {
            "aspect": "New predictions",
            "thermodynamics": "Phase transitions, critical phenomena",
            "cosmology": "mu-Sigma valley, regime transitions, MOND-like emergence",
        },
        {
            "aspect": "Falsification of analogy",
            "thermodynamics": "Gas law works at all densities",
            "cosmology": "EFC predicts no L2/L3 deviations",
        },
    ]

    def get_table(self) -> List[Dict[str, str]]:
        """Return the full gas-law analogy table."""
        return self.TABLE

    def mapping(self, aspect: str) -> Optional[Dict[str, str]]:
        """Look up a specific row by aspect name.

        Parameters
        ----------
        aspect : str
            The aspect to look up (case-insensitive partial match).

        Returns
        -------
        dict or None
            Matching row, or None.
        """
        for row in self.TABLE:
            if aspect.lower() in row["aspect"].lower():
                return row
        return None

    def central_thesis(self) -> str:
        """Return the central thesis of the analogy."""
        return (
            "LCDM is to EFC what the ideal gas law is to statistical "
            "mechanics: a correct and useful special case valid in one "
            "regime, embedded within a richer structure that becomes "
            "necessary when the system moves outside that regime."
        )


# ---------------------------------------------------------------------------
# Kill-test suite (Table 3)
# ---------------------------------------------------------------------------

class KillTestSuite:
    """Discrete gravity sector kill-tests (Table 3).

    Five kill-tests define the structural integrity of Graph-AQUAL.
    """

    TESTS: List[Dict[str, str]] = [
        {
            "id": "KT1",
            "test": "Newton recovery (xi >> 1)",
            "status": "PASS",
            "result": "Slopes -2.03 (Newton), -1.05 (MOND)",
        },
        {
            "id": "KT2",
            "test": "Prefactor C (xi ~ 1)",
            "status": "PASS",
            "result": "C = 2.32 (structural; not fitted)",
        },
        {
            "id": "KT3",
            "test": "Mass scaling beta (xi < 1)",
            "status": "OPEN",
            "result": "Classical beta approx 0.29; BE predicts 0.50",
        },
        {
            "id": "KT4",
            "test": "Superposition (xi ~ 1)",
            "status": "PASS",
            "result": "Non-linear superposition handled",
        },
        {
            "id": "KT5",
            "test": "External field effect",
            "status": "PARTIAL",
            "result": "EFE present; amplitude partially reproduced",
        },
    ]

    def get_tests(self) -> List[Dict[str, str]]:
        """Return the full kill-test table."""
        return self.TESTS

    def status(self, kt_id: str) -> Optional[str]:
        """Get status for a specific kill-test.

        Parameters
        ----------
        kt_id : str
            Kill-test ID (e.g. 'KT1').

        Returns
        -------
        str or None
            Status string.
        """
        for t in self.TESTS:
            if t["id"] == kt_id:
                return t["status"]
        return None

    def pass_count(self) -> int:
        """Count the number of tests with PASS status."""
        return sum(1 for t in self.TESTS if t["status"] == "PASS")

    def summary(self) -> Dict[str, object]:
        """Return a summary of the kill-test suite."""
        statuses = {t["id"]: t["status"] for t in self.TESTS}
        return {
            "total": len(self.TESTS),
            "pass": self.pass_count(),
            "open": sum(1 for t in self.TESTS if t["status"] == "OPEN"),
            "partial": sum(1 for t in self.TESTS if t["status"] == "PARTIAL"),
            "statuses": statuses,
        }


# ---------------------------------------------------------------------------
# Historical falsifications (Table 4)
# ---------------------------------------------------------------------------

class HistoricalFalsifications:
    """Five documented historical falsifications (Table 4).

    Preserved in Validation Ledger section 3.2 as a permanent record.
    """

    FAILURES: List[Dict[str, str]] = [
        {
            "element": "EFC v1 Scalar Index",
            "failure": "Monotonic radial boost incompatible with RC diversity",
            "resolution": "Superseded by EBE regime framework",
        },
        {
            "element": "EFC-R on full SPARC",
            "failure": "Systematic residuals in Regime 2-3",
            "resolution": "Led to regime partitioning",
        },
        {
            "element": "ISW C-metric",
            "failure": "Mixed-channel spurious gradient",
            "resolution": "Superseded by self-consistent ODE",
        },
        {
            "element": "Poisson-sector mu > 1",
            "failure": "Disfavoured by RSD data",
            "resolution": "Architecture revised: background primary",
        },
        {
            "element": "Strong alpha in background",
            "failure": "alpha approx -0.67 collapsed under DR2 to -0.14 +/- 0.21",
            "resolution": "Signal locus updated to growth/structure",
        },
    ]

    def get_failures(self) -> List[Dict[str, str]]:
        """Return all historical falsifications."""
        return self.FAILURES

    def count(self) -> int:
        """Number of documented falsifications."""
        return len(self.FAILURES)

    def summary(self) -> Dict[str, object]:
        """Return summary information."""
        return {
            "count": self.count(),
            "elements": [f["element"] for f in self.FAILURES],
            "all_resolved": all("resolution" in f for f in self.FAILURES),
        }
