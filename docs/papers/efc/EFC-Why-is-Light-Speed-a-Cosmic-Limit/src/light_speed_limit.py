"""Light Speed Limit -- core classes.

Models the entropy-flow interpretation of why light speed is a
cosmic limit in EFC. The key idea: the maximum propagation speed
corresponds to the maximum rate of entropy transport in the flow field.

Author: Morten Magnusson (ORCID 0009-0002-4860-5095)
License: CC-BY-4.0
"""

import math

# Speed of light in m/s
C_LIGHT = 299_792_458.0


class EntropyFlowField:
    """Represents the local entropy flow field.

    In EFC, the flow field has a maximum transport rate that corresponds
    to c. Energy cannot flow faster than the entropy field can propagate
    state changes.

    Parameters
    ----------
    flow_rate : float
        Local entropy flow rate (dimensionless, normalised to c=1).
    direction : tuple of float
        Unit direction vector (3D).
    """

    def __init__(self, flow_rate: float, direction: tuple = (1.0, 0.0, 0.0)):
        self.flow_rate = flow_rate
        norm = math.sqrt(sum(d**2 for d in direction))
        self.direction = tuple(d / norm for d in direction) if norm > 0 else (1.0, 0.0, 0.0)

    def velocity(self) -> tuple:
        """Return the flow velocity vector (normalised to c=1)."""
        return tuple(self.flow_rate * d for d in self.direction)

    def is_subluminal(self) -> bool:
        """Check if the flow is subluminal (|v| <= 1 in natural units)."""
        return self.flow_rate <= 1.0 + 1e-12

    def __repr__(self) -> str:
        return f"EntropyFlowField(flow_rate={self.flow_rate}, direction={self.direction})"


class PropagationBound:
    """Computes the maximum propagation speed from entropy field properties.

    The bound arises because the entropy field has a finite maximum
    gradient: no signal can propagate faster than the rate at which
    entropy can be redistributed.

    Parameters
    ----------
    S_max : float
        Maximum entropy density. Default 1.0.
    gradient_max : float
        Maximum sustainable entropy gradient. Default 1.0.
    """

    def __init__(self, S_max: float = 1.0, gradient_max: float = 1.0):
        self.S_max = S_max
        self.gradient_max = gradient_max

    def v_max(self) -> float:
        """Maximum propagation speed (normalised to c=1).

        v_max = S_max * gradient_max / S_max = gradient_max
        In natural units with proper normalisation, this equals 1 (= c).
        """
        return min(self.gradient_max, 1.0)

    def lorentz_factor(self, v: float) -> float:
        """Lorentz factor gamma for velocity v (in units of c).

        gamma = 1 / sqrt(1 - v^2)
        Diverges as v -> 1, enforcing the speed limit.
        """
        if abs(v) >= 1.0:
            return float("inf")
        return 1.0 / math.sqrt(1.0 - v**2)

    def time_dilation(self, v: float, dt_rest: float) -> float:
        """Time dilation: dt_moving = gamma * dt_rest."""
        gamma = self.lorentz_factor(v)
        if math.isinf(gamma):
            return float("inf")
        return gamma * dt_rest

    def __repr__(self) -> str:
        return f"PropagationBound(S_max={self.S_max}, gradient_max={self.gradient_max})"


class LightSpeedLimit:
    """Main model: why c is a cosmic limit in EFC.

    The speed of light emerges as the maximum rate at which the entropy
    flow field can propagate causal information. This is not an imposed
    boundary but a consequence of the field's structure.

    Parameters
    ----------
    c : float
        Speed of light in chosen units. Default 1.0 (natural units).
    """

    def __init__(self, c: float = 1.0):
        self.c = c
        self.bound = PropagationBound()

    def effective_speed(self, energy: float, rest_mass: float) -> float:
        """Compute the effective propagation speed for a particle.

        v = c * sqrt(1 - (mc^2/E)^2)

        Parameters
        ----------
        energy : float
            Total energy of the particle.
        rest_mass : float
            Rest mass (in energy units when c=1).
        """
        if rest_mass <= 0:
            return self.c  # massless -> travels at c
        if energy <= rest_mass * self.c**2:
            return 0.0
        ratio = (rest_mass * self.c**2 / energy) ** 2
        return self.c * math.sqrt(1.0 - ratio)

    def entropy_speed_relation(self, v: float) -> float:
        """Entropy production rate as a function of speed.

        As v -> c, the entropy cost of further acceleration diverges,
        making c an asymptotic limit.

        Returns dS/dv (normalised).
        """
        if abs(v) >= self.c:
            return float("inf")
        gamma = 1.0 / math.sqrt(1.0 - (v / self.c) ** 2)
        return gamma**3  # entropy cost scales as gamma^3

    def is_causal(self, v: float) -> bool:
        """Check if a given speed respects the causal bound."""
        return abs(v) <= self.c + 1e-12

    def __repr__(self) -> str:
        return f"LightSpeedLimit(c={self.c})"
