"""Effective Phenomenological Law for Gravitational Response -- core classes.

Implements the central result: mu(a) = 1 + beta * S(a), where S(a) is the
entropy field governing the L1->L2 regime transition.

Author: Morten Magnusson (ORCID 0009-0002-4860-5095)
License: CC-BY-4.0
"""

import math


class EntropyField:
    """The entropy field S(a) that drives gravitational enhancement.

    S(a) = (S_inf / 2) * [1 + tanh((ln a - ln a_t) / sigma)]

    Parameters
    ----------
    S_inf : float
        Asymptotic entropy saturation value. Default 1.0.
    a_t : float
        Transition scale factor. Default 0.55 (z_t ~ 0.82).
    sigma : float
        Transition width. Default 0.10.
    """

    def __init__(self, S_inf: float = 1.0, a_t: float = 0.55, sigma: float = 0.10):
        self.S_inf = S_inf
        self.a_t = a_t
        self.sigma = sigma

    def S(self, a: float) -> float:
        """Evaluate the entropy field at scale factor a."""
        if a <= 0:
            return 0.0
        x = (math.log(a) - math.log(self.a_t)) / self.sigma
        return (self.S_inf / 2.0) * (1.0 + math.tanh(x))

    def S_from_z(self, z: float) -> float:
        """Evaluate entropy at redshift z (a = 1/(1+z))."""
        a = 1.0 / (1.0 + z)
        return self.S(a)

    def dS_da(self, a: float) -> float:
        """Derivative dS/da at scale factor a."""
        if a <= 0:
            return 0.0
        x = (math.log(a) - math.log(self.a_t)) / self.sigma
        sech2 = 1.0 / math.cosh(x) ** 2
        return (self.S_inf / 2.0) * sech2 / (self.sigma * a)

    def transition_redshift(self) -> float:
        """Return the transition redshift z_t = 1/a_t - 1."""
        return 1.0 / self.a_t - 1.0

    def __repr__(self) -> str:
        return (f"EntropyField(S_inf={self.S_inf}, a_t={self.a_t}, "
                f"sigma={self.sigma})")


class EffectiveGravitationalCoupling:
    """The effective gravitational coupling mu(a) = 1 + beta * S(a).

    Parameters
    ----------
    beta : float
        EFC coupling constant. Default 0.16 (~16% enhancement).
    entropy_field : EntropyField
        The entropy field. Default uses standard parameters.
    """

    def __init__(self, beta: float = 0.16, entropy_field: EntropyField = None):
        self.beta = beta
        self.entropy_field = entropy_field or EntropyField()

    def mu(self, a: float) -> float:
        """Effective gravitational coupling at scale factor a.

        mu(a) = G_eff / G = 1 + beta * S(a)
        """
        return 1.0 + self.beta * self.entropy_field.S(a)

    def mu_from_z(self, z: float) -> float:
        """Effective coupling at redshift z."""
        a = 1.0 / (1.0 + z)
        return self.mu(a)

    def G_eff(self, a: float, G: float = 1.0) -> float:
        """Effective gravitational constant at scale factor a."""
        return G * self.mu(a)

    def enhancement_percent(self, a: float) -> float:
        """Gravitational enhancement in percent at scale factor a."""
        return (self.mu(a) - 1.0) * 100.0

    def is_gr_limit(self, a: float, threshold: float = 1e-6) -> bool:
        """Check if mu is effectively 1 (GR limit)."""
        return abs(self.mu(a) - 1.0) < threshold

    def __repr__(self) -> str:
        return f"EffectiveGravitationalCoupling(beta={self.beta})"


class RegimeClassifier:
    """Classifies the cosmological regime at a given scale factor.

    L0: GR limit (mu ~ 1), very early universe
    L1: Linear perturbations, transition beginning
    L2: Structure-dominated, mu > 1
    L3: Deep non-linear, full enhancement
    """

    THRESHOLDS = {
        "L0": 0.001,   # mu - 1 < 0.001
        "L1": 0.01,    # 0.001 <= mu - 1 < 0.01
        "L2": 0.10,    # 0.01 <= mu - 1 < 0.10
    }

    def __init__(self, coupling: EffectiveGravitationalCoupling = None):
        self.coupling = coupling or EffectiveGravitationalCoupling()

    def classify(self, a: float) -> str:
        """Return the regime label at scale factor a."""
        delta_mu = self.coupling.mu(a) - 1.0
        if delta_mu < self.THRESHOLDS["L0"]:
            return "L0"
        elif delta_mu < self.THRESHOLDS["L1"]:
            return "L1"
        elif delta_mu < self.THRESHOLDS["L2"]:
            return "L2"
        else:
            return "L3"

    def classify_z(self, z: float) -> str:
        """Return regime at redshift z."""
        a = 1.0 / (1.0 + z)
        return self.classify(a)

    def __repr__(self) -> str:
        return f"RegimeClassifier(coupling={self.coupling})"
