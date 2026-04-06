"""
EFC c_eff Parameterization -- Core Implementation

Effective speed of sound:
    c_eff(a) = c_0 * [1 + epsilon * beta * T(a)]

First-order Taylor expansion in the grid response. Valid for
epsilon * beta * T << 1.

DOI: 10.6084/m9.figshare.31305421
Author: Morten Magnusson
"""

import math


class TransitionFunction:
    """EFC transition function T(a), normalized to peak at unity.

    T(z) represents the vacuum-sector transition, peaking near z_peak = 0.441
    where Omega_m ~ 0.5. Approaches zero at high z (matter domination)
    and at z=0 remains near but below unity.

    Uses a smooth form: T(z) = exp(-((z - z_peak)/sigma)^2 / 2) for a
    Gaussian-like transition, but we use the tabulated form from the paper
    for accuracy and provide an analytic approximation.

    Parameters
    ----------
    z_peak : float
        Redshift at which T peaks (default 0.441).
    Omega_m : float
        Matter density parameter (default 0.3).
    """

    def __init__(self, z_peak=0.441, Omega_m=0.3):
        self.z_peak = z_peak
        self.Omega_m = Omega_m

    def T(self, z):
        """Evaluate transition function at redshift z.

        Uses the functional form from the paper:
        T(z) is based on the matter fraction Omega_m(z) reaching 0.5
        at z_peak. We use a smooth approximation:
        T(z) = 2 * sqrt(f*(1-f)) where f = Omega_m(z)
        normalized so T(z_peak) = 1.
        """
        a = 1.0 / (1.0 + z)
        # Omega_m(z) = Omega_m * (1+z)^3 / E^2(z)
        # E^2(z) = Omega_m*(1+z)^3 + (1-Omega_m)
        E2 = self.Omega_m * (1.0 + z) ** 3 + (1.0 - self.Omega_m)
        f = self.Omega_m * (1.0 + z) ** 3 / E2

        # T = 2*sqrt(f*(1-f)), peaks at f=0.5
        T_raw = 2.0 * math.sqrt(max(f * (1.0 - f), 0.0))

        # Normalize so T_peak = 1
        # At z_peak, f should be ~0.5, so T_raw ~ 1.0
        # But compute normalization exactly
        E2_peak = self.Omega_m * (1.0 + self.z_peak) ** 3 + (1.0 - self.Omega_m)
        f_peak = self.Omega_m * (1.0 + self.z_peak) ** 3 / E2_peak
        T_norm = 2.0 * math.sqrt(max(f_peak * (1.0 - f_peak), 0.0))

        if T_norm <= 0:
            return 0.0
        return T_raw / T_norm

    def info(self):
        return {
            "z_peak": self.z_peak,
            "Omega_m": self.Omega_m,
            "T_at_peak": self.T(self.z_peak),
            "T_at_0": self.T(0.0),
            "T_at_1": self.T(1.0),
            "T_at_3": self.T(3.0),
        }


class CEffParameterization:
    """Effective speed of sound: c_eff(a) = c_0 * [1 + epsilon * beta * T(a)].

    Parameters
    ----------
    beta : float
        Background coupling amplitude (default 0.08 from BAO+RSD).
    epsilon : float
        Propagation-limit coupling strength (default 0.1).
    c_0 : float
        Laboratory speed of light (default 1.0 in natural units).
    z_peak : float
        Peak redshift of transition function.
    """

    def __init__(self, beta=0.08, epsilon=0.1, c_0=1.0, z_peak=0.441):
        self.beta = beta
        self.epsilon = epsilon
        self.c_0 = c_0
        self.transition = TransitionFunction(z_peak=z_peak)

    def c_eff(self, z):
        """Effective speed of light at redshift z.

        Returns
        -------
        float : c_eff(z) = c_0 * [1 + epsilon * beta * T(z)]
        """
        T = self.transition.T(z)
        return self.c_0 * (1.0 + self.epsilon * self.beta * T)

    def delta_c_over_c(self, z):
        """Fractional change in c: (c_eff - c_0) / c_0 = epsilon * beta * T(z)."""
        T = self.transition.T(z)
        return self.epsilon * self.beta * T

    def table(self, redshifts=None):
        """Reproduce numerical table from paper Section 2.3.

        Returns
        -------
        list of dict
        """
        if redshifts is None:
            redshifts = [0.0, 0.44, 0.51, 1.0, 2.0, 3.0]

        results = []
        for z in redshifts:
            T = self.transition.T(z)
            results.append({
                "z": z,
                "T_z": round(T, 3),
                "beta_T": round(self.beta * T, 4),
                "dc_over_c_percent": round(self.delta_c_over_c(z) * 100, 4),
                "c_eff_over_c0": round(self.c_eff(z) / self.c_0, 6),
            })
        return results

    def is_valid_expansion(self, z):
        """Check if first-order expansion is valid (epsilon*beta*T << 1)."""
        return abs(self.epsilon * self.beta * self.transition.T(z)) < 0.1

    def info(self):
        return {
            "beta": self.beta,
            "epsilon": self.epsilon,
            "c_0": self.c_0,
            "max_dc_over_c_percent": round(self.delta_c_over_c(self.transition.z_peak) * 100, 4),
        }


class DistanceModification:
    """Modified comoving distance from c_eff variation.

    d_C(z) = integral_0^z c_eff(z') / H(z') dz'

    Parameters
    ----------
    c_eff_param : CEffParameterization
        c_eff parameterization instance.
    H0 : float
        Hubble constant [km/s/Mpc].
    Omega_m : float
        Matter density parameter.
    """

    def __init__(self, c_eff_param=None, H0=70.0, Omega_m=0.3):
        self.c_eff_param = c_eff_param or CEffParameterization()
        self.H0 = H0
        self.Omega_m = Omega_m
        self.c_km_per_s = 299792.458  # speed of light

    def H(self, z):
        """Hubble parameter H(z) in km/s/Mpc."""
        E2 = self.Omega_m * (1.0 + z) ** 3 + (1.0 - self.Omega_m)
        return self.H0 * math.sqrt(E2)

    def comoving_distance(self, z, n_steps=1000):
        """Comoving distance via trapezoidal integration.

        Returns
        -------
        float : d_C in Mpc
        """
        dz = z / n_steps
        integral = 0.0
        for i in range(n_steps):
            z_i = i * dz
            z_ip1 = (i + 1) * dz
            f_i = self.c_eff_param.c_eff(z_i) * self.c_km_per_s / self.H(z_i)
            f_ip1 = self.c_eff_param.c_eff(z_ip1) * self.c_km_per_s / self.H(z_ip1)
            integral += 0.5 * (f_i + f_ip1) * dz
        return integral

    def comoving_distance_lcdm(self, z, n_steps=1000):
        """Standard LCDM comoving distance (c_eff = c_0)."""
        dz = z / n_steps
        integral = 0.0
        for i in range(n_steps):
            z_i = i * dz
            z_ip1 = (i + 1) * dz
            f_i = self.c_km_per_s / self.H(z_i)
            f_ip1 = self.c_km_per_s / self.H(z_ip1)
            integral += 0.5 * (f_i + f_ip1) * dz
        return integral

    def distance_shift_percent(self, z):
        """Fractional distance shift from c_eff variation."""
        d_efc = self.comoving_distance(z)
        d_lcdm = self.comoving_distance_lcdm(z)
        if d_lcdm == 0:
            return 0.0
        return (d_efc - d_lcdm) / d_lcdm * 100.0


class CDDRTest:
    """Cosmic Distance Duality Relation analysis.

    eta(z) = D_L / [D_A * (1+z)^2]

    Case (i) Metric VSL: eta = 1 exactly
    Case (ii) Optical-medium: eta != 1, sign change near z ~ 0.44
    """

    def __init__(self, c_eff_param=None):
        self.c_eff = c_eff_param or CEffParameterization()

    def eta_metric(self, z):
        """Case (i): CDDR always preserved."""
        return 1.0

    def eta_optical_medium(self, z):
        """Case (ii): CDDR violation from refractive index.

        In the optical-medium interpretation:
        eta(z) = c_eff(z_emit) / c_eff(z_obs)
        where z_obs = 0.

        This is a simplified model; the actual relation depends on
        the photon transport model.
        """
        c_emit = self.c_eff.c_eff(z)
        c_obs = self.c_eff.c_eff(0.0)
        return c_emit / c_obs

    def sign_change_analysis(self, z_values=None):
        """Analyze whether eta-1 changes sign near z_peak.

        Returns
        -------
        dict with sign change information
        """
        if z_values is None:
            z_values = [0.1, 0.2, 0.3, 0.4, 0.44, 0.5, 0.6, 0.8, 1.0]

        results = []
        for z in z_values:
            eta = self.eta_optical_medium(z)
            results.append({
                "z": z,
                "eta": round(eta, 6),
                "eta_minus_1": round(eta - 1.0, 6),
            })

        # Check for sign changes
        deviations = [r["eta_minus_1"] for r in results]
        sign_changes = sum(
            1 for i in range(len(deviations) - 1)
            if deviations[i] * deviations[i + 1] < 0
        )

        return {
            "values": results,
            "n_sign_changes": sign_changes,
            "has_sign_change": sign_changes > 0,
        }


class DegeneracyBreaker:
    """Four degeneracy-breaking tests from the paper.

    Test 1: CDDR (Case ii only)
    Test 2: ISW kernel shape
    Test 3: beta-split (distance vs growth)
    Test 4: Standard sirens (GW vs EM)
    """

    TESTS = {
        "CDDR": {
            "id": "Test 1",
            "description": "Sign-change in eta(z) near z~0.44",
            "applies_to": "Case ii only",
            "status": "Requires ~1% CDDR precision at multiple redshifts",
        },
        "ISW_kernel": {
            "id": "Test 2",
            "description": "ISW kernel shape modification from dc_eff/dt",
            "applies_to": "Both",
            "status": "Second-order probe, currently noise-limited at l < 60",
        },
        "beta_split": {
            "id": "Test 3",
            "description": "Distance-derived beta vs growth-derived beta",
            "applies_to": "Both",
            "status": "Cleanest test; beta_distance != beta_growth at >3 sigma indicates epsilon != 0",
        },
        "standard_sirens": {
            "id": "Test 4",
            "description": "GW luminosity distance vs EM luminosity distance",
            "applies_to": "Both",
            "status": "Future: Einstein Telescope + Cosmic Explorer -> ~1% at z~0.5",
        },
    }

    def __init__(self):
        pass

    def info(self, test_name=None):
        if test_name:
            if test_name not in self.TESTS:
                raise ValueError(f"Unknown test: {test_name}")
            return self.TESTS[test_name]
        return self.TESTS

    def beta_split_test(self, beta_distance, beta_growth, sigma_distance, sigma_growth):
        """Evaluate beta-split test.

        Parameters
        ----------
        beta_distance : float
            Beta from distance measurements (BAO/SN).
        beta_growth : float
            Beta from growth measurements (RSD/f*sigma8).
        sigma_distance, sigma_growth : float
            Uncertainties.

        Returns
        -------
        dict with split significance
        """
        diff = abs(beta_distance - beta_growth)
        sigma_combined = math.sqrt(sigma_distance ** 2 + sigma_growth ** 2)
        significance = diff / sigma_combined if sigma_combined > 0 else 0.0

        return {
            "beta_distance": beta_distance,
            "beta_growth": beta_growth,
            "difference": round(diff, 5),
            "significance_sigma": round(significance, 2),
            "epsilon_nonzero": significance > 3.0,
        }

    def siren_test(self, D_L_GW, D_L_EM, sigma_GW, sigma_EM):
        """Evaluate standard siren test.

        If D_L^GW != D_L^EM, the grid coupling is EM-specific.
        """
        diff = abs(D_L_GW - D_L_EM)
        sigma_combined = math.sqrt(sigma_GW ** 2 + sigma_EM ** 2)
        significance = diff / sigma_combined if sigma_combined > 0 else 0.0

        return {
            "D_L_GW": D_L_GW,
            "D_L_EM": D_L_EM,
            "difference_Mpc": round(diff, 2),
            "significance_sigma": round(significance, 2),
            "em_specific": significance > 3.0,
        }


class FalsificationCriteria:
    """Six falsification criteria from Table in Section 5.

    Each criterion, if met, falsifies a specific aspect of the c_eff model.
    """

    CRITERIA = [
        {"id": "F-ceff-1", "condition": "CDDR violation inconsistent with T(z) shape",
         "meaning": "c_eff not grid-driven", "applies_to": "Case ii"},
        {"id": "F-ceff-2", "condition": "beta_BAO and beta_RSD agree to <1%",
         "meaning": "epsilon ~ 0; no measurable variation", "applies_to": "Both"},
        {"id": "F-ceff-3", "condition": "CDDR violation monotonic (no sign change)",
         "meaning": "Not EFC-type new physics", "applies_to": "Case ii"},
        {"id": "F-ceff-4", "condition": "Local lab measurement of c variation",
         "meaning": "EFC predicts no local effect", "applies_to": "Both"},
        {"id": "F-ceff-5", "condition": "D_L^GW = D_L^EM to sub-percent (sirens)",
         "meaning": "No EM-specific modification", "applies_to": "Both"},
        {"id": "F-ceff-6", "condition": "Case ii derived but eta = 1 to <0.5%",
         "meaning": "Case ii ruled out", "applies_to": "Case ii"},
    ]

    def __init__(self):
        self.criteria = self.CRITERIA

    def evaluate(self, criterion_id, condition_met):
        """Evaluate whether a falsification criterion is triggered.

        Parameters
        ----------
        criterion_id : str
            E.g. 'F-ceff-1'.
        condition_met : bool
            Whether the falsification condition is observed.

        Returns
        -------
        dict
        """
        for c in self.criteria:
            if c["id"] == criterion_id:
                return {
                    **c,
                    "condition_met": condition_met,
                    "falsified": condition_met,
                }
        raise ValueError(f"Unknown criterion: {criterion_id}")

    def summary(self):
        return self.criteria
