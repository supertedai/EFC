"""
Regime-Dependent Structure Formation Module
=============================================
Implements the EFC Paper III energy-flow framework:
  E_total = E_flow + E_latent

Regime classification:
  FLOW:       L < 0.25 (near-equilibrium, simple models valid)
  TRANSITION: 0.25 <= L <= 0.45 (mixed dynamics)
  LATENT:     L > 0.45 (non-equilibrium dominated)

Cross-scale correspondence between galactic (kpc) and cosmological (Gpc) scales.

Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
Affiliation: Symbiose Research, Sandnes, Norway
License: CC-BY-4.0
"""

import math

# Regime constants
REGIME_FLOW = "FLOW"
REGIME_TRANSITION = "TRANSITION"
REGIME_LATENT = "LATENT"


class EnergyDecomposition:
    """Phenomenological energy decomposition E_total = E_flow + E_latent.

    E_flow represents entropy-gradient-driven energy flow (observable dynamics).
    E_latent represents latent/hidden energy content (unresolved complexity).

    Parameters
    ----------
    E_total : float
        Total energy of the system (arbitrary units).
    flow_fraction : float
        Fraction of energy in the flow component [0, 1].
    """

    def __init__(self, E_total, flow_fraction):
        self.E_total = float(E_total)
        self.flow_fraction = max(0.0, min(1.0, float(flow_fraction)))

    @property
    def E_flow(self):
        """Energy in the flow (observable) component."""
        return self.E_total * self.flow_fraction

    @property
    def E_latent(self):
        """Energy in the latent (hidden complexity) component."""
        return self.E_total * (1.0 - self.flow_fraction)

    @property
    def latent_fraction(self):
        """Fraction of energy in the latent component."""
        return 1.0 - self.flow_fraction

    def entropy_gradient(self, scale_factor):
        """Estimate entropy gradient strength at a given cosmological scale.

        Higher redshift (smaller scale factor) implies steeper gradient.

        Parameters
        ----------
        scale_factor : float
            Cosmological scale factor a (a=1 at present, a<1 in the past).

        Returns
        -------
        float
            Relative entropy gradient strength.
        """
        if scale_factor <= 0:
            return float("inf")
        return self.E_flow / (scale_factor ** 2)

    def __repr__(self):
        return (
            f"EnergyDecomposition(E_total={self.E_total:.2f}, "
            f"E_flow={self.E_flow:.2f}, E_latent={self.E_latent:.2f})"
        )


class RegimeStructure:
    """Regime classification based on latent proxy L.

    Regimes:
      FLOW:       L < 0.25 (near-equilibrium)
      TRANSITION: 0.25 <= L <= 0.45 (mixed dynamics)
      LATENT:     L > 0.45 (non-equilibrium dominated)

    Parameters
    ----------
    L_flow_max : float
        Upper L boundary for FLOW regime (default: 0.25).
    L_latent_min : float
        Lower L boundary for LATENT regime (default: 0.45).
    """

    def __init__(self, L_flow_max=0.25, L_latent_min=0.45):
        self.L_flow_max = L_flow_max
        self.L_latent_min = L_latent_min

    def classify(self, L):
        """Classify a system into a regime based on L.

        Parameters
        ----------
        L : float
            Latent proxy value.

        Returns
        -------
        str
            Regime label: FLOW, TRANSITION, or LATENT.
        """
        if L < self.L_flow_max:
            return REGIME_FLOW
        elif L > self.L_latent_min:
            return REGIME_LATENT
        else:
            return REGIME_TRANSITION

    def expected_model_success(self, L):
        """Estimate model success rate as a function of L.

        Simple sigmoid: success decreases rapidly with increasing L.

        Parameters
        ----------
        L : float
            Latent proxy value.

        Returns
        -------
        float
            Expected success rate [0, 1].
        """
        midpoint = (self.L_flow_max + self.L_latent_min) / 2.0
        steepness = 15.0
        return 1.0 / (1.0 + math.exp(steepness * (L - midpoint)))

    def classify_batch(self, L_values):
        """Classify multiple systems.

        Returns
        -------
        dict
            Mapping of regime -> list of indices.
        """
        results = {REGIME_FLOW: [], REGIME_TRANSITION: [], REGIME_LATENT: []}
        for i, L in enumerate(L_values):
            regime = self.classify(L)
            results[regime].append(i)
        return results


class CrossScaleCorrespondence:
    """Cross-scale correspondence between galactic and cosmological phenomena.

    Maps entropy gradient steepness to observed phenomena at both scales:
      Steep gradient  -> LSB galaxies (100% success)  -> z>10 (1000x excess)
      Shallow gradient -> Barred galaxies (~4% success) -> z<3 (LCDM valid)

    Parameters
    ----------
    gradient_strength : float
        Relative entropy gradient strength.
    scale : str
        'galactic' or 'cosmological'.
    """

    # Empirical correspondence table
    GALACTIC_THRESHOLDS = {
        "steep": {"morphology": "LSB", "success_rate": 1.00},
        "moderate": {"morphology": "spiral", "success_rate": 0.35},
        "shallow": {"morphology": "barred", "success_rate": 0.04},
    }

    COSMOLOGICAL_THRESHOLDS = {
        "steep": {"redshift_range": "z > 10", "excess_factor": 1000.0},
        "moderate": {"redshift_range": "6 < z < 10", "excess_factor": 10.0},
        "shallow": {"redshift_range": "z < 3", "excess_factor": 1.0},
    }

    def __init__(self, gradient_strength):
        self.gradient_strength = float(gradient_strength)

    @property
    def gradient_class(self):
        """Classify the gradient as steep, moderate, or shallow."""
        if self.gradient_strength > 5.0:
            return "steep"
        elif self.gradient_strength > 1.0:
            return "moderate"
        else:
            return "shallow"

    @property
    def galactic_prediction(self):
        """Return galactic-scale prediction for this gradient."""
        return self.GALACTIC_THRESHOLDS[self.gradient_class]

    @property
    def cosmological_prediction(self):
        """Return cosmological-scale prediction for this gradient."""
        return self.COSMOLOGICAL_THRESHOLDS[self.gradient_class]

    def __repr__(self):
        return (
            f"CrossScaleCorrespondence(gradient={self.gradient_strength:.2f}, "
            f"class={self.gradient_class})"
        )


class StructureFormationRate:
    """Structure formation rate under EFC framework.

    At high redshift (steep entropy gradients), structure formation is
    enhanced relative to LCDM predictions due to entropy-gradient-driven
    energy flow.

    Parameters
    ----------
    redshift : float
        Cosmological redshift z.
    lcdm_rate : float
        Standard LCDM predicted formation rate.
    """

    def __init__(self, redshift, lcdm_rate=1.0):
        self.redshift = float(redshift)
        self.lcdm_rate = float(lcdm_rate)

    @property
    def scale_factor(self):
        """Cosmological scale factor a = 1/(1+z)."""
        return 1.0 / (1.0 + self.redshift)

    @property
    def efc_enhancement(self):
        """EFC enhancement factor over LCDM.

        Phenomenological model: enhancement grows with redshift
        as entropy gradients steepen.
        """
        if self.redshift <= 3.0:
            return 1.0  # No enhancement at low z
        return 1.0 + 0.1 * (self.redshift - 3.0) ** 2

    @property
    def efc_rate(self):
        """EFC-predicted structure formation rate."""
        return self.lcdm_rate * self.efc_enhancement

    @property
    def excess_factor(self):
        """Ratio of EFC rate to LCDM rate."""
        return self.efc_enhancement

    def __repr__(self):
        return (
            f"StructureFormationRate(z={self.redshift:.1f}, "
            f"enhancement={self.efc_enhancement:.1f}x)"
        )
