"""
Variable Effective Light Speed in Entropic Transition States:
s0/s1 Structure in Energy-Flow Cosmology (EFC)

The effective speed of light is not a primitive constant but an emergent
propagation limit determined by the entropic state of the grid.

Two fundamental entropic phases:
  s0: low-entropy constraining state
  s1: high-entropy dissipative state

c_eff(S) varies as a function of the entropic gradient, governing
information capacity, local curvature, and energy-flow geometry.
"""

from dataclasses import dataclass
import math
from typing import Optional


# Physical constants
C_VACUUM = 299792458.0  # m/s, vacuum speed of light


@dataclass
class EntropicState:
    """An entropic state on the EFC grid.

    Parameters
    ----------
    label : str
        State label (e.g. 's0', 's1').
    entropy : float
        Normalized entropy value in [0, 1].
    description : str
        Physical description of the state.
    """
    label: str
    entropy: float
    description: str

    def __post_init__(self):
        if not 0 <= self.entropy <= 1:
            raise ValueError(f"Entropy must be in [0,1], got {self.entropy}")


@dataclass
class VariableLightModel:
    """Model for effective light speed as a function of entropy.

    c_eff(S) = c_0 * f(S)

    where f(S) is the entropic modulation function.

    Parameters
    ----------
    c_0 : float
        Vacuum speed of light [m/s].
    s_transition : float
        Entropy value at the s0/s1 transition boundary.
    sharpness : float
        Sharpness of the transition (higher = sharper).
    c_min_fraction : float
        Minimum c_eff / c_0 ratio in the deep s1 regime.
    """
    c_0: float = C_VACUUM
    s_transition: float = 0.5
    sharpness: float = 10.0
    c_min_fraction: float = 0.1

    def modulation(self, S: float) -> float:
        """Entropic modulation function f(S).

        f(S) = c_min + (1 - c_min) / (1 + exp(sharpness * (S - s_t)))

        In s0 (low S): f -> 1 (full light speed)
        In s1 (high S): f -> c_min_fraction (reduced propagation)

        Parameters
        ----------
        S : float
            Normalized entropy in [0, 1].

        Returns
        -------
        float
            Modulation factor in [c_min_fraction, 1].
        """
        c_min = self.c_min_fraction
        x = self.sharpness * (S - self.s_transition)
        if x > 50:
            return c_min
        if x < -50:
            return 1.0
        return c_min + (1.0 - c_min) / (1.0 + math.exp(x))

    def c_eff(self, S: float) -> float:
        """Effective speed of light at entropy S [m/s]."""
        return self.c_0 * self.modulation(S)

    def c_eff_ratio(self, S: float) -> float:
        """c_eff / c_0 ratio."""
        return self.modulation(S)

    def information_capacity(self, S: float) -> float:
        """Relative information propagation capacity.

        Proportional to c_eff^2 (area of causal diamond).
        """
        return self.modulation(S) ** 2

    def horizon_scale(self, S: float, t: float) -> float:
        """Causal horizon scale at entropy S after time t.

        d_horizon = c_eff(S) * t

        Parameters
        ----------
        S : float
            Normalized entropy.
        t : float
            Proper time [seconds].

        Returns
        -------
        float
            Horizon distance [meters].
        """
        return self.c_eff(S) * t


@dataclass
class CollapseRegime:
    """Collapse mechanism at extreme entropy values.

    At S -> 0 (deep s0): gravitational collapse / black hole formation
    At S -> 1 (deep s1): information horizon collapse / de Sitter limit
    """
    regime: str  # 's0_collapse' or 's1_collapse'
    description: str
    entropy_threshold: float
    observable_signature: str

    @property
    def is_s0(self) -> bool:
        return self.regime == "s0_collapse"


@dataclass
class RedshiftCorrection:
    """Redshift modification from variable c_eff.

    Observed redshift includes contribution from c_eff variation:
    1 + z_total = (1 + z_expansion) * (c_emit / c_obs)
    """
    z_expansion: float
    S_emit: float
    S_obs: float

    def z_corrected(self, model: VariableLightModel) -> float:
        """Total observed redshift including c_eff variation."""
        c_emit = model.c_eff(self.S_emit)
        c_obs = model.c_eff(self.S_obs)
        return (1.0 + self.z_expansion) * (c_emit / c_obs) - 1.0


def entropy_gradient(S1: float, S2: float, dr: float) -> float:
    """Spatial entropy gradient dS/dr.

    Parameters
    ----------
    S1, S2 : float
        Entropy at two points.
    dr : float
        Spatial separation.

    Returns
    -------
    float
        Entropy gradient.
    """
    if dr == 0:
        return float("inf") if S1 != S2 else 0.0
    return (S2 - S1) / dr


def curvature_from_entropy(S: float, model: VariableLightModel) -> float:
    """Local curvature contribution from entropic state.

    In EFC, curvature arises from gradients in c_eff:
    kappa ~ (1/c_eff) * d^2(c_eff)/dS^2

    Simplified: larger entropy gradient -> more curvature.
    """
    # Numerical second derivative of c_eff w.r.t. S
    dS = 0.001
    if S - dS < 0 or S + dS > 1:
        return 0.0
    c_minus = model.c_eff(S - dS)
    c_center = model.c_eff(S)
    c_plus = model.c_eff(S + dS)
    d2c = (c_plus - 2 * c_center + c_minus) / (dS ** 2)
    if c_center == 0:
        return 0.0
    return abs(d2c / c_center)


# ---- Reference states ----

S0_STATE = EntropicState(
    label="s0",
    entropy=0.1,
    description="Low-entropy constraining state: full light speed, "
                "gravitational dominance, structure formation",
)

S1_STATE = EntropicState(
    label="s1",
    entropy=0.9,
    description="High-entropy dissipative state: reduced propagation, "
                "information horizon limits, de Sitter approach",
)

S0_COLLAPSE = CollapseRegime(
    regime="s0_collapse",
    description="Deep s0: gravitational collapse, black hole formation",
    entropy_threshold=0.01,
    observable_signature="Event horizons, singularities",
)

S1_COLLAPSE = CollapseRegime(
    regime="s1_collapse",
    description="Deep s1: information horizon collapse, de Sitter limit",
    entropy_threshold=0.99,
    observable_signature="Cosmological horizon, accelerated expansion",
)

DEFAULT_MODEL = VariableLightModel()
