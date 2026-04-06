"""
Consciousness Field Resonance Module
======================================
Implements the CEM (Consciousness-Ego-Mirror) framework measures:
  - Omega: Spectral differentiation (spectral entropy)
  - kappa: Causal integration (transfer entropy)
  - C = Omega x kappa: Product measure (falsified F1)
  - Balance constraint: corr(Omega, kappa) < 0

Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
Affiliation: Symbiose Research, Sandnes, Norway
License: CC-BY-4.0
"""

import math


class SpectralDifferentiation:
    """Spectral differentiation measure Omega.

    Omega quantifies the spectral entropy of neural signals,
    measuring internal differentiation / structured complexity.

    Typical ranges:
      - Anaesthetised brain: 0.52 - 0.72
      - Waking brain: 0.78 - 0.88

    Parameters
    ----------
    power_spectrum : list of float
        Power spectral density values across frequency bands.
    """

    def __init__(self, power_spectrum):
        self.power_spectrum = [float(p) for p in power_spectrum]

    @property
    def omega(self):
        """Compute spectral entropy Omega.

        Returns normalized Shannon entropy of the power spectrum.
        """
        total = sum(self.power_spectrum)
        if total <= 0:
            return 0.0
        probs = [p / total for p in self.power_spectrum if p > 0]
        n = len(probs)
        if n <= 1:
            return 0.0
        entropy = -sum(p * math.log2(p) for p in probs)
        max_entropy = math.log2(n)
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def __repr__(self):
        return f"SpectralDifferentiation(Omega={self.omega:.3f})"


class CausalIntegration:
    """Causal integration measure kappa.

    kappa quantifies the transfer entropy between brain regions,
    measuring regional causal closure.

    Parameters
    ----------
    transfer_entropies : list of float
        Transfer entropy values between region pairs.
    """

    def __init__(self, transfer_entropies):
        self.transfer_entropies = [float(t) for t in transfer_entropies]

    @property
    def kappa(self):
        """Compute global causal integration kappa.

        Returns the mean transfer entropy across region pairs.
        """
        if not self.transfer_entropies:
            return 0.0
        return sum(self.transfer_entropies) / len(self.transfer_entropies)

    @property
    def kappa_regional(self):
        """Return per-region transfer entropy values."""
        return list(self.transfer_entropies)

    def __repr__(self):
        return f"CausalIntegration(kappa={self.kappa:.3f})"


class ProductMeasure:
    """Product measure C = Omega x kappa.

    This measure was pre-registered as a consciousness predictor
    but was FALSIFIED (F1) -- it does not improve over Omega alone.

    Parameters
    ----------
    omega : float
        Spectral differentiation value.
    kappa : float
        Causal integration value.
    """

    STATUS = "FALSIFIED"

    def __init__(self, omega, kappa):
        self.omega = float(omega)
        self.kappa = float(kappa)

    @property
    def C(self):
        """Compute C = Omega x kappa."""
        return self.omega * self.kappa

    @property
    def is_falsified(self):
        """The product model is falsified (F1)."""
        return True

    def __repr__(self):
        return f"ProductMeasure(C={self.C:.4f}, status={self.STATUS})"


class ResonanceRegime:
    """Resonance regime classification along the continuum.

    Systems are classified by their resonance level:
      - stone:             near zero (thermodynamic field)
      - cell:              low (metabolic field)
      - anaesthetised:     reduced (neural field, Omega 0.52-0.72)
      - waking:            extreme (neural field, Omega 0.78-0.88)

    Parameters
    ----------
    omega : float
        Spectral differentiation value.
    kappa : float
        Causal integration value (optional context).
    region : str
        Brain region label (e.g., 'global', 'parietal', 'frontal').
    """

    THRESHOLDS = {
        "near_zero": (0.0, 0.10),
        "low": (0.10, 0.50),
        "reduced": (0.50, 0.75),
        "extreme": (0.75, 1.00),
    }

    FIELD_MAP = {
        "near_zero": "thermodynamic",
        "low": "metabolic",
        "reduced": "neural",
        "extreme": "neural",
    }

    def __init__(self, omega, kappa=0.0, region="global"):
        self.omega = float(omega)
        self.kappa = float(kappa)
        self.region = region

    @property
    def resonance_level(self):
        """Classify the resonance level based on Omega."""
        for level, (lo, hi) in self.THRESHOLDS.items():
            if lo <= self.omega < hi:
                return level
        return "extreme"

    @property
    def field_type(self):
        """Return the field type for this resonance level."""
        return self.FIELD_MAP.get(self.resonance_level, "unknown")

    @property
    def regional_C(self):
        """Compute regional product measure C for this region."""
        return self.omega * self.kappa

    def cohens_d(self, other):
        """Compute Cohen's d effect size between two regimes.

        Uses a simplified pooled standard deviation estimate.

        Parameters
        ----------
        other : ResonanceRegime
            The comparison regime.

        Returns
        -------
        float
            Cohen's d effect size estimate.
        """
        diff = abs(self.omega - other.omega)
        # Approximate pooled SD from typical EEG variability
        pooled_sd = 0.08
        return diff / pooled_sd if pooled_sd > 0 else 0.0

    def __repr__(self):
        return (
            f"ResonanceRegime(omega={self.omega:.3f}, "
            f"level={self.resonance_level}, "
            f"field={self.field_type})"
        )


class BalanceConstraint:
    """Balance constraint: corr(Omega, kappa) < 0.

    Higher differentiation correlates with lower integration,
    suggesting a balance regime rather than maximisation.

    Parameters
    ----------
    omega_values : list of float
        Omega values across subjects/conditions.
    kappa_values : list of float
        Corresponding kappa values.
    """

    def __init__(self, omega_values, kappa_values):
        assert len(omega_values) == len(kappa_values), (
            "Omega and kappa lists must be the same length"
        )
        self.omega_values = [float(o) for o in omega_values]
        self.kappa_values = [float(k) for k in kappa_values]

    @property
    def correlation(self):
        """Compute Pearson correlation between Omega and kappa."""
        n = len(self.omega_values)
        if n < 2:
            return 0.0
        mean_o = sum(self.omega_values) / n
        mean_k = sum(self.kappa_values) / n
        cov = sum(
            (o - mean_o) * (k - mean_k)
            for o, k in zip(self.omega_values, self.kappa_values)
        ) / n
        std_o = math.sqrt(sum((o - mean_o) ** 2 for o in self.omega_values) / n)
        std_k = math.sqrt(sum((k - mean_k) ** 2 for k in self.kappa_values) / n)
        if std_o == 0 or std_k == 0:
            return 0.0
        return cov / (std_o * std_k)

    @property
    def is_balanced(self):
        """Check if the balance constraint holds (negative correlation)."""
        return self.correlation < 0

    def __repr__(self):
        return (
            f"BalanceConstraint(r={self.correlation:.3f}, "
            f"balanced={self.is_balanced})"
        )
