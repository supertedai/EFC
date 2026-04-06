"""
H0 and S8 Tensions Module

Models the entropy-dependent gravitational coupling that resolves
the Hubble tension and S8 tension within the EFC framework.
"""

import math
from dataclasses import dataclass
from typing import List


@dataclass
class EffectiveGravity:
    """
    Entropy-dependent effective gravitational coupling.

    G_eff(S) = G_N * (1 + beta * S)

    Attributes:
        g_n: Newton's gravitational constant (normalised to 1)
        beta: Entropy coupling parameter (negative for suppression)
    """
    g_n: float = 1.0
    beta: float = -0.02

    def g_eff(self, s: float) -> float:
        """
        Effective gravitational coupling at entropy S.

        Args:
            s: Local entropy value

        Returns:
            G_eff(S)
        """
        return self.g_n * (1.0 + self.beta * s)

    def suppression_factor(self, s: float) -> float:
        """
        Gravitational suppression factor relative to G_N.

        Returns:
            G_eff / G_N = 1 + beta * S
        """
        return 1.0 + self.beta * s


@dataclass
class HubbleTension:
    """
    Model for the Hubble tension resolution.

    The tension arises from inferring global H0 from local
    measurements in the presence of entropy gradients.

    Attributes:
        h0_local: Local measurement of H0 (km/s/Mpc)
        h0_cmb: CMB-inferred H0 (km/s/Mpc)
        sigma_local: Uncertainty on local H0
        sigma_cmb: Uncertainty on CMB H0
    """
    h0_local: float = 73.0
    h0_cmb: float = 67.4
    sigma_local: float = 1.0
    sigma_cmb: float = 0.5

    def tension_sigma(self) -> float:
        """
        Compute tension in units of sigma.

        Returns:
            Number of sigma between local and CMB H0
        """
        sigma_combined = math.sqrt(self.sigma_local ** 2 + self.sigma_cmb ** 2)
        return abs(self.h0_local - self.h0_cmb) / sigma_combined

    def corrected_h0(self, gravity: EffectiveGravity, s_local: float) -> float:
        """
        Correct local H0 for entropy-dependent gravity.

        H0_corrected = H0_local * sqrt(G_N / G_eff(S_local))

        Args:
            gravity: Effective gravity model
            s_local: Local entropy value

        Returns:
            Corrected H0
        """
        ratio = gravity.g_n / gravity.g_eff(s_local)
        return self.h0_local * math.sqrt(ratio)

    def chi2_improvement(
        self, gravity: EffectiveGravity, s_local: float
    ) -> float:
        """
        Chi-squared improvement from entropy correction.

        Args:
            gravity: Effective gravity model
            s_local: Local entropy value

        Returns:
            Delta chi-squared
        """
        h0_corr = self.corrected_h0(gravity, s_local)
        chi2_before = ((self.h0_local - self.h0_cmb) / self.sigma_cmb) ** 2
        chi2_after = ((h0_corr - self.h0_cmb) / self.sigma_cmb) ** 2
        return chi2_before - chi2_after


@dataclass
class S8Tension:
    """
    Model for the S8 tension resolution.

    S8 suppression from entropy-dependent growth damping.

    Attributes:
        s8_lcdm: LCDM predicted S8
        s8_observed: Late-universe observed S8
        sigma_obs: Observational uncertainty
    """
    s8_lcdm: float = 0.832
    s8_observed: float = 0.766
    sigma_obs: float = 0.020

    def tension_sigma(self) -> float:
        """Tension in sigma units."""
        return abs(self.s8_lcdm - self.s8_observed) / self.sigma_obs

    def corrected_s8(self, gravity: EffectiveGravity, s_growth: float) -> float:
        """
        Correct LCDM S8 with entropy-dependent growth damping.

        S8_corrected = S8_lcdm * (G_eff(S) / G_N)^0.5

        Args:
            gravity: Effective gravity model
            s_growth: Entropy value relevant for growth

        Returns:
            Corrected S8
        """
        ratio = gravity.g_eff(s_growth) / gravity.g_n
        return self.s8_lcdm * math.sqrt(abs(ratio))

    def residual_tension(
        self, gravity: EffectiveGravity, s_growth: float
    ) -> float:
        """
        Residual tension after correction in sigma.

        Args:
            gravity: Effective gravity model
            s_growth: Entropy for growth

        Returns:
            Residual tension in sigma
        """
        s8_corr = self.corrected_s8(gravity, s_growth)
        return abs(s8_corr - self.s8_observed) / self.sigma_obs


class TensionResolver:
    """
    Combined resolver for H0 and S8 tensions using
    entropy-dependent effective gravity.
    """

    def __init__(
        self,
        beta: float = -0.02,
        h0_local: float = 73.0,
        h0_cmb: float = 67.4,
        s8_lcdm: float = 0.832,
        s8_observed: float = 0.766,
    ):
        self.gravity = EffectiveGravity(g_n=1.0, beta=beta)
        self.hubble = HubbleTension(
            h0_local=h0_local, h0_cmb=h0_cmb
        )
        self.s8 = S8Tension(
            s8_lcdm=s8_lcdm, s8_observed=s8_observed
        )

    def resolve(
        self, s_local: float, s_growth: float
    ) -> dict:
        """
        Attempt simultaneous resolution of both tensions.

        Args:
            s_local: Local entropy for H0 correction
            s_growth: Growth-era entropy for S8 correction

        Returns:
            Dict with all tension metrics
        """
        h0_corr = self.hubble.corrected_h0(self.gravity, s_local)
        s8_corr = self.s8.corrected_s8(self.gravity, s_growth)
        return {
            "h0_original_tension_sigma": self.hubble.tension_sigma(),
            "h0_corrected": h0_corr,
            "h0_chi2_improvement": self.hubble.chi2_improvement(
                self.gravity, s_local
            ),
            "s8_original_tension_sigma": self.s8.tension_sigma(),
            "s8_corrected": s8_corr,
            "s8_residual_sigma": self.s8.residual_tension(
                self.gravity, s_growth
            ),
            "g_eff_local": self.gravity.g_eff(s_local),
            "g_eff_growth": self.gravity.g_eff(s_growth),
        }

    def summary(self) -> str:
        """Return human-readable summary."""
        return (
            "H0-S8 Tension Resolver (EFC)\n"
            f"  beta        = {self.gravity.beta}\n"
            f"  H0_local    = {self.hubble.h0_local} km/s/Mpc\n"
            f"  H0_CMB      = {self.hubble.h0_cmb} km/s/Mpc\n"
            f"  H0 tension  = {self.hubble.tension_sigma():.1f} sigma\n"
            f"  S8_LCDM     = {self.s8.s8_lcdm}\n"
            f"  S8_observed = {self.s8.s8_observed}\n"
            f"  S8 tension  = {self.s8.tension_sigma():.1f} sigma"
        )
