"""
EFC CMB Thermodynamic Interpretation -- Core Implementation

Compatibility and null-test framework for CMB observables under
entropy-constrained structure formation.

Causal chain: JWST -> S(z) -> CMB consequences
No parameter fitting; no circular inference.

DOI: 10.6084/m9.figshare.31064929
Author: Morten Magnusson
"""

import math


class EntropyProfile:
    """Redshift-dependent entropy profile S(z) constrained by JWST.

    S(z) = S_0 * (1 + z)^n_S * exp(-alpha_S * z)

    Parameters
    ----------
    S_0 : float
        Entropy at z=0 (constrained by SPARC rotation curves).
    alpha_S : float
        Entropy coupling strength (constrained by JWST sSFR).
    n_S : float
        Entropy profile exponent (cross-scale consistency).
    S_eq : float or None
        Entropy at matter-radiation equality (CMB peak structure).
    """

    def __init__(self, S_0=1.0, alpha_S=0.5, n_S=1.5, S_eq=None):
        self.S_0 = S_0
        self.alpha_S = alpha_S
        self.n_S = n_S
        self.S_eq = S_eq

    def S(self, z):
        """Evaluate entropy profile at redshift z."""
        return self.S_0 * (1.0 + z) ** self.n_S * math.exp(-self.alpha_S * z)

    def dS_dz(self, z):
        """Derivative dS/dz via product rule."""
        base = (1.0 + z) ** self.n_S * math.exp(-self.alpha_S * z)
        d_power = self.n_S * (1.0 + z) ** (self.n_S - 1.0) * math.exp(-self.alpha_S * z)
        d_exp = (1.0 + z) ** self.n_S * (-self.alpha_S) * math.exp(-self.alpha_S * z)
        return self.S_0 * (d_power + d_exp)

    def z_peak(self):
        """Redshift at which S(z) peaks (dS/dz = 0).

        n_S / (1+z) - alpha_S = 0  =>  z_peak = n_S / alpha_S - 1
        """
        if self.alpha_S <= 0:
            return float("inf")
        return self.n_S / self.alpha_S - 1.0

    def info(self):
        return {
            "S_0": self.S_0,
            "alpha_S": self.alpha_S,
            "n_S": self.n_S,
            "S_eq": self.S_eq,
            "z_peak": self.z_peak(),
        }


class CompatibilityTest:
    """Test CMB observables against EFC compatibility constraints.

    Each test checks whether an observed value falls within the
    required tolerance of the EFC prediction.
    """

    # Table from paper: compatibility constraints
    CONSTRAINTS = {
        "theta_s": {
            "value": 100.09,
            "uncertainty": 0.30,
            "unit": "arcmin",
            "requirement": "within_uncertainty",
        },
        "peak_ratio_R": {
            "value": 0.42,
            "uncertainty": 0.05,
            "unit": "dimensionless",
            "requirement": "within_2sigma",
        },
        "damping_lD": {
            "value": None,
            "requirement": "standard_functional_form",
            "description": "Silk damping form preserved",
        },
        "TE_EE_correlation": {
            "value": None,
            "requirement": "sign_preserved",
            "description": "Positive TE/EE correlation",
        },
    }

    def __init__(self):
        self.results = {}

    def test(self, observable, observed_value, observed_uncertainty=None):
        """Test observed value against constraint.

        Parameters
        ----------
        observable : str
            One of 'theta_s', 'peak_ratio_R'.
        observed_value : float
            Measured value.
        observed_uncertainty : float or None
            Measurement uncertainty.

        Returns
        -------
        dict with keys: observable, within_tolerance, deviation_sigma
        """
        if observable not in self.CONSTRAINTS:
            raise ValueError(f"Unknown observable: {observable}")

        c = self.CONSTRAINTS[observable]
        if c["value"] is None:
            return {
                "observable": observable,
                "within_tolerance": None,
                "note": c["description"],
            }

        diff = abs(observed_value - c["value"])
        total_unc = c["uncertainty"]
        if observed_uncertainty is not None:
            total_unc = math.sqrt(c["uncertainty"] ** 2 + observed_uncertainty ** 2)

        deviation_sigma = diff / total_unc if total_unc > 0 else float("inf")

        if c["requirement"] == "within_uncertainty":
            within = deviation_sigma <= 1.0
        elif c["requirement"] == "within_2sigma":
            within = deviation_sigma <= 2.0
        else:
            within = deviation_sigma <= 2.0

        result = {
            "observable": observable,
            "predicted": c["value"],
            "observed": observed_value,
            "deviation_sigma": round(deviation_sigma, 3),
            "within_tolerance": within,
        }
        self.results[observable] = result
        return result


class NullTest:
    """Falsifiable null tests for EFC-CMB consistency.

    If any null test is violated, EFC predictions are falsified.

    Parameters
    ----------
    name : str
        Test identifier.
    threshold_percent : float
        Maximum allowed deviation in percent.
    """

    TESTS = {
        "peak_position": {
            "description": "theta_s within 0.5%",
            "threshold_percent": 0.5,
            "reference_value": 100.09,
        },
        "damping_consistency": {
            "description": "l_D within 5%",
            "threshold_percent": 5.0,
            "reference_value": 1050.0,
        },
        "lensing_growth": {
            "description": "A_L in 0.9-0.95 range",
            "threshold_percent": None,
            "A_L_min": 0.9,
            "A_L_max": 0.95,
        },
    }

    def __init__(self, name):
        if name not in self.TESTS:
            raise ValueError(f"Unknown null test: {name}. Available: {list(self.TESTS.keys())}")
        self.name = name
        self.spec = self.TESTS[name]

    def evaluate(self, observed_value):
        """Evaluate null test.

        Returns
        -------
        dict with keys: name, observed, falsified, deviation_percent or A_L info
        """
        if self.name == "lensing_growth":
            # A_L >= 1.0 at high significance -> falsified
            falsified = observed_value >= 1.0
            return {
                "name": self.name,
                "observed_A_L": observed_value,
                "predicted_range": [self.spec["A_L_min"], self.spec["A_L_max"]],
                "falsified": falsified,
                "note": "A_L >= 1.0 falsifies EFC prediction",
            }

        ref = self.spec["reference_value"]
        deviation_pct = abs(observed_value - ref) / ref * 100.0
        threshold = self.spec["threshold_percent"]
        falsified = deviation_pct > threshold

        return {
            "name": self.name,
            "reference": ref,
            "observed": observed_value,
            "deviation_percent": round(deviation_pct, 4),
            "threshold_percent": threshold,
            "falsified": falsified,
        }


class PredictionZone:
    """EFC prediction zones that may deviate from LCDM.

    These are not null tests but specific predictions.
    """

    PREDICTIONS = {
        "A_L": {
            "predicted_value": 0.925,
            "range": [0.9, 0.95],
            "mechanism": "smoother halos from entropy-modified structure formation",
        },
        "ISW_phase": {
            "predicted_range_rad": [0.01, 0.1],
            "ell_threshold": 1000,
            "mechanism": "energy-flow coupling to gravitational potential evolution",
        },
        "lensing_evolution": {
            "predicted": "z-dependent C_l^{phi phi} at high l",
            "mechanism": "entropy gradient evolution modifies lensing kernel",
        },
    }

    def __init__(self, name):
        if name not in self.PREDICTIONS:
            raise ValueError(f"Unknown prediction: {name}")
        self.name = name
        self.spec = self.PREDICTIONS[name]

    def info(self):
        return {"prediction": self.name, **self.spec}

    def check(self, observed_value):
        """Check if observation matches EFC prediction zone."""
        if self.name == "A_L":
            lo, hi = self.spec["range"]
            matches = lo <= observed_value <= hi
            return {
                "prediction": self.name,
                "observed": observed_value,
                "predicted_range": [lo, hi],
                "matches_efc": matches,
            }
        elif self.name == "ISW_phase":
            lo, hi = self.spec["predicted_range_rad"]
            matches = lo <= observed_value <= hi
            return {
                "prediction": self.name,
                "observed_rad": observed_value,
                "predicted_range_rad": [lo, hi],
                "matches_efc": matches,
            }
        return {"prediction": self.name, "note": "qualitative prediction"}


class JWSTExcess:
    """JWST/COSMOS-Web galaxy excess analysis.

    Documents the empirical tension with LCDM that motivates
    the EFC entropy-constrained framework.
    """

    # Table from paper
    EXCESS_DATA = [
        {"z_bin": "5-6", "ratio_vs_lcdm": 23.0, "ratio_vs_halo": 3.1,
         "status": "within_baryonic_physics"},
        {"z_bin": "7-8", "ratio_vs_lcdm": 124.0, "ratio_vs_halo": 7.7,
         "status": "exceeds_standard_models"},
        {"z_bin": "8-9", "ratio_vs_lcdm": 259.0, "ratio_vs_halo": 10.4,
         "status": "exceeds_epsilon1_limit"},
        {"z_bin": "9-10", "ratio_vs_lcdm": 529.0, "ratio_vs_halo": 10.6,
         "status": "exceeds_epsilon1_limit"},
    ]

    CHI2 = 47.3
    DF = 4
    P_VALUE = 1e-9  # upper bound

    def __init__(self):
        self.data = self.EXCESS_DATA

    def summary(self):
        """Return summary statistics."""
        return {
            "n_bins": len(self.data),
            "chi2": self.CHI2,
            "df": self.DF,
            "p_value_upper_bound": self.P_VALUE,
            "max_excess_vs_lcdm": max(d["ratio_vs_lcdm"] for d in self.data),
            "bins": self.data,
        }

    def tension_level(self, z_bin):
        """Get tension level for a specific redshift bin."""
        for d in self.data:
            if d["z_bin"] == z_bin:
                return d
        raise ValueError(f"Unknown z_bin: {z_bin}")


class CMBFramework:
    """Complete CMB compatibility framework combining all components.

    Implements the full causal chain: JWST -> S(z) -> CMB consequences.
    """

    def __init__(self, entropy_profile=None):
        self.entropy = entropy_profile or EntropyProfile()
        self.compatibility = CompatibilityTest()
        self.jwst = JWSTExcess()

    def run_null_tests(self, theta_s_obs=100.09, lD_obs=1050.0, A_L_obs=0.93):
        """Run all three null tests.

        Parameters
        ----------
        theta_s_obs : float
            Observed angular sound horizon [arcmin].
        lD_obs : float
            Observed damping multipole.
        A_L_obs : float
            Observed lensing amplitude.

        Returns
        -------
        dict with all null test results and overall status.
        """
        results = {}

        nt_peak = NullTest("peak_position")
        results["peak_position"] = nt_peak.evaluate(theta_s_obs)

        nt_damp = NullTest("damping_consistency")
        results["damping_consistency"] = nt_damp.evaluate(lD_obs)

        nt_lens = NullTest("lensing_growth")
        results["lensing_growth"] = nt_lens.evaluate(A_L_obs)

        any_falsified = any(r["falsified"] for r in results.values())

        return {
            "tests": results,
            "any_falsified": any_falsified,
            "framework_status": "falsified" if any_falsified else "consistent",
        }

    def prediction_summary(self):
        """Return all prediction zone summaries."""
        zones = {}
        for name in PredictionZone.PREDICTIONS:
            pz = PredictionZone(name)
            zones[name] = pz.info()
        return zones

    def full_report(self, theta_s_obs=100.09, lD_obs=1050.0, A_L_obs=0.93):
        """Generate complete framework report."""
        return {
            "entropy_profile": self.entropy.info(),
            "null_tests": self.run_null_tests(theta_s_obs, lD_obs, A_L_obs),
            "predictions": self.prediction_summary(),
            "jwst_excess": self.jwst.summary(),
        }
