"""
SPARC175 Regime-Dependent Validity Analysis
============================================
Core classes for EFC rotation curve fitting, NFW comparison,
latent proxy computation, and regime classification.

Model: v(r) = v_flat * sqrt(1 - exp(-(r / r_turnon)^sharpness))
Comparison: LCDM-NFW with concentration c=10.

Classification criteria:
  FLOW:       delta_AIC <= -10  AND  chi2_red < 20
  TRANSITION: -10 < delta_AIC < +10  OR  20 < chi2_red < 50
  LATENT:     delta_AIC >= +10  OR  chi2_red > 50

Latent proxy:
  L = 0.4 * |rho_radial| + 0.3 * sign_rate + 0.3 * (chi2_red / 10)

Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
Affiliation: Symbiose Research, Sandnes, Norway
License: CC-BY-4.0
"""

import math

# Regime constants
REGIME_FLOW = "FLOW"
REGIME_TRANSITION = "TRANSITION"
REGIME_LATENT = "LATENT"


class EFCRotationCurve:
    """EFC ultra-phenomenological rotation curve model.

    v(r) = v_flat * sqrt(1 - exp(-(r / r_turnon)^sharpness))

    Parameters
    ----------
    v_flat : float
        Asymptotic flat velocity [km/s]. Range: [50, 200].
    r_turnon : float
        Turn-on radius [kpc]. Range: [0.1, 30].
    sharpness : float
        Transition sharpness exponent. Range: [0.5, 5.0].
    """

    PARAM_BOUNDS = {
        "v_flat": (50.0, 200.0),
        "r_turnon": (0.1, 30.0),
        "sharpness": (0.5, 5.0),
    }

    def __init__(self, v_flat, r_turnon, sharpness):
        self.v_flat = float(v_flat)
        self.r_turnon = float(r_turnon)
        self.sharpness = float(sharpness)

    def velocity(self, r):
        """Compute rotation velocity at radius r [kpc].

        Returns velocity in km/s.
        """
        x = (r / self.r_turnon) ** self.sharpness
        return self.v_flat * math.sqrt(1.0 - math.exp(-x))

    def velocity_array(self, radii):
        """Compute velocities for a list of radii."""
        return [self.velocity(r) for r in radii]

    def chi2(self, r_obs, v_obs, v_err):
        """Compute chi-squared statistic against observations.

        Parameters
        ----------
        r_obs : list of float
            Observed radii [kpc].
        v_obs : list of float
            Observed velocities [km/s].
        v_err : list of float
            Velocity uncertainties [km/s].

        Returns
        -------
        float
            Chi-squared value.
        """
        total = 0.0
        for r, vo, ve in zip(r_obs, v_obs, v_err):
            if ve > 0:
                residual = (vo - self.velocity(r)) / ve
                total += residual ** 2
        return total

    def chi2_reduced(self, r_obs, v_obs, v_err):
        """Compute reduced chi-squared (chi2 / dof)."""
        n = len(r_obs)
        k = 3  # number of parameters
        dof = n - k
        if dof <= 0:
            return float("inf")
        return self.chi2(r_obs, v_obs, v_err) / dof

    def aic(self, r_obs, v_obs, v_err):
        """Compute Akaike Information Criterion.

        AIC = chi2 + 2*k where k=3.
        """
        return self.chi2(r_obs, v_obs, v_err) + 2 * 3

    def __repr__(self):
        return (
            f"EFCRotationCurve(v_flat={self.v_flat:.1f}, "
            f"r_turnon={self.r_turnon:.2f}, "
            f"sharpness={self.sharpness:.2f})"
        )


class NFWRotationCurve:
    """NFW (Navarro-Frenk-White) dark matter halo rotation curve.

    v^2(r) = V_200^2 * [ln(1+x) - x/(1+x)] / [ln(1+c) - c/(1+c)]
    where x = c * r / r_200, and r_200 = V_200 / (10 * H0).

    Parameters
    ----------
    v_200 : float
        Virial velocity [km/s].
    r_s : float
        Scale radius [kpc].
    concentration : float
        NFW concentration parameter (default: 10).
    """

    def __init__(self, v_200, r_s, concentration=10.0):
        self.v_200 = float(v_200)
        self.r_s = float(r_s)
        self.concentration = float(concentration)

    def _g(self, c):
        """NFW normalization function g(c) = ln(1+c) - c/(1+c)."""
        return math.log(1.0 + c) - c / (1.0 + c)

    def velocity(self, r):
        """Compute NFW rotation velocity at radius r [kpc]."""
        x = r / self.r_s
        if x <= 0:
            return 0.0
        g_x = math.log(1.0 + x) - x / (1.0 + x)
        g_c = self._g(self.concentration)
        v_sq = self.v_200 ** 2 * g_x / g_c
        return math.sqrt(max(v_sq, 0.0))

    def velocity_array(self, radii):
        """Compute velocities for a list of radii."""
        return [self.velocity(r) for r in radii]

    def chi2(self, r_obs, v_obs, v_err):
        """Compute chi-squared statistic."""
        total = 0.0
        for r, vo, ve in zip(r_obs, v_obs, v_err):
            if ve > 0:
                residual = (vo - self.velocity(r)) / ve
                total += residual ** 2
        return total

    def chi2_reduced(self, r_obs, v_obs, v_err):
        """Compute reduced chi-squared (chi2 / dof)."""
        n = len(r_obs)
        k = 2  # number of parameters
        dof = n - k
        if dof <= 0:
            return float("inf")
        return self.chi2(r_obs, v_obs, v_err) / dof

    def aic(self, r_obs, v_obs, v_err):
        """Compute AIC. AIC = chi2 + 2*k where k=2."""
        return self.chi2(r_obs, v_obs, v_err) + 2 * 2

    def __repr__(self):
        return (
            f"NFWRotationCurve(v_200={self.v_200:.1f}, "
            f"r_s={self.r_s:.2f}, c={self.concentration:.0f})"
        )


class LatentProxy:
    """Latent complexity proxy L for regime classification.

    L = 0.4 * |rho_radial| + 0.3 * sign_rate + 0.3 * (chi2_red / 10)

    Components:
      - rho_radial: Spearman correlation (residuals vs radius)
      - sign_rate: sign changes per data point in residuals
      - chi2_red: reduced chi-squared of the fit (normalized by 10)
    """

    WEIGHTS = {"radial_trend": 0.4, "oscillation": 0.3, "chi2_norm": 0.3}

    def __init__(self, rho_radial, sign_rate, chi2_red):
        self.rho_radial = float(rho_radial)
        self.sign_rate = float(sign_rate)
        self.chi2_red = float(chi2_red)

    @property
    def L(self):
        """Compute the latent proxy value L in [0, 1]."""
        raw = (
            self.WEIGHTS["radial_trend"] * abs(self.rho_radial)
            + self.WEIGHTS["oscillation"] * self.sign_rate
            + self.WEIGHTS["chi2_norm"] * (self.chi2_red / 10.0)
        )
        return min(max(raw, 0.0), 1.0)

    @property
    def components(self):
        """Return individual component contributions."""
        return {
            "radial_trend": self.WEIGHTS["radial_trend"] * abs(self.rho_radial),
            "oscillation": self.WEIGHTS["oscillation"] * self.sign_rate,
            "chi2_normalized": self.WEIGHTS["chi2_norm"] * (self.chi2_red / 10.0),
        }

    def __repr__(self):
        return f"LatentProxy(L={self.L:.3f})"


class RegimeClassifier:
    """Classify galaxies into FLOW, TRANSITION, or LATENT regimes.

    Classification criteria:
      FLOW:       delta_AIC <= -10  AND  chi2_red < 20
      TRANSITION: -10 < delta_AIC < +10  OR  20 < chi2_red < 50
      LATENT:     delta_AIC >= +10  OR  chi2_red > 50

    Parameters
    ----------
    delta_aic_flow : float
        AIC threshold for FLOW (default: -10).
    delta_aic_latent : float
        AIC threshold for LATENT (default: +10).
    chi2_flow_max : float
        Maximum chi2_red for FLOW (default: 20).
    chi2_latent_min : float
        Minimum chi2_red for LATENT (default: 50).
    """

    def __init__(
        self,
        delta_aic_flow=-10.0,
        delta_aic_latent=10.0,
        chi2_flow_max=20.0,
        chi2_latent_min=50.0,
    ):
        self.delta_aic_flow = delta_aic_flow
        self.delta_aic_latent = delta_aic_latent
        self.chi2_flow_max = chi2_flow_max
        self.chi2_latent_min = chi2_latent_min

    def classify(self, delta_aic, chi2_red):
        """Classify a galaxy into a regime.

        Parameters
        ----------
        delta_aic : float
            AIC(EFC) - AIC(LCDM). Negative favors EFC.
        chi2_red : float
            Reduced chi-squared of the EFC fit.

        Returns
        -------
        str
            One of REGIME_FLOW, REGIME_TRANSITION, REGIME_LATENT.
        """
        if delta_aic >= self.delta_aic_latent or chi2_red > self.chi2_latent_min:
            return REGIME_LATENT
        if delta_aic <= self.delta_aic_flow and chi2_red < self.chi2_flow_max:
            return REGIME_FLOW
        return REGIME_TRANSITION

    def classify_batch(self, entries):
        """Classify multiple galaxies.

        Parameters
        ----------
        entries : list of dict
            Each dict must have 'delta_aic' and 'chi2_red' keys.

        Returns
        -------
        dict
            Mapping of regime -> list of entry indices.
        """
        results = {REGIME_FLOW: [], REGIME_TRANSITION: [], REGIME_LATENT: []}
        for i, entry in enumerate(entries):
            regime = self.classify(entry["delta_aic"], entry["chi2_red"])
            results[regime].append(i)
        return results

    def summary(self, entries):
        """Return regime distribution summary.

        Parameters
        ----------
        entries : list of dict
            Each dict must have 'delta_aic' and 'chi2_red' keys.

        Returns
        -------
        dict
            Counts and percentages per regime.
        """
        classified = self.classify_batch(entries)
        n_total = len(entries)
        summary = {}
        for regime, indices in classified.items():
            count = len(indices)
            pct = (count / n_total * 100.0) if n_total > 0 else 0.0
            summary[regime] = {"count": count, "percentage": round(pct, 1)}
        return summary
