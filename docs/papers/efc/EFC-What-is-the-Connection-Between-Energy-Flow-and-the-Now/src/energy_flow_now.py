"""Energy Flow and the Now -- core classes.

Models the connection between energy flow, entropy gradients, and the
emergent present moment in EFC.

Author: Morten Magnusson (ORCID 0009-0002-4860-5095)
License: CC-BY-4.0
"""

import math


class EntropyGradient:
    """Represents a local entropy gradient dS/dt at a point in spacetime.

    Parameters
    ----------
    dS_dt : float
        Rate of entropy change (positive = forward arrow of time).
    S_local : float
        Local entropy value.
    """

    def __init__(self, dS_dt: float, S_local: float = 0.0):
        self.dS_dt = dS_dt
        self.S_local = S_local

    def arrow_direction(self) -> str:
        """Return the direction of the local arrow of time."""
        if self.dS_dt > 0:
            return "forward"
        elif self.dS_dt < 0:
            return "backward"
        return "equilibrium"

    def __repr__(self) -> str:
        return f"EntropyGradient(dS_dt={self.dS_dt}, S_local={self.S_local})"


class TemporalState:
    """A snapshot of the temporal state at a given point.

    Parameters
    ----------
    t : float
        Coordinate time.
    S : float
        Entropy value at this time.
    energy_flow : float
        Magnitude of energy flow (positive definite).
    """

    def __init__(self, t: float, S: float, energy_flow: float):
        self.t = t
        self.S = S
        self.energy_flow = energy_flow

    def now_intensity(self) -> float:
        """Compute the intensity of the Now as the product of entropy
        gradient magnitude and energy flow.

        The Now is most vivid where energy is flowing and entropy is
        increasing -- i.e., at active state transitions.

        Returns
        -------
        float
            Non-negative intensity measure.
        """
        return abs(self.energy_flow) * self.S

    def __repr__(self) -> str:
        return (f"TemporalState(t={self.t}, S={self.S}, "
                f"energy_flow={self.energy_flow})")


class EnergyFlowNow:
    """Models the connection between energy flow and the experience of Now.

    The central idea: the present moment is not a point on a timeline
    but the locus of maximal energy-flow activity within an entropy
    gradient. The Now emerges wherever state transitions are occurring.

    Parameters
    ----------
    S_max : float
        Maximum entropy (sets the scale). Default 1.0.
    tau : float
        Characteristic timescale of entropy evolution. Default 1.0.
    """

    def __init__(self, S_max: float = 1.0, tau: float = 1.0):
        self.S_max = S_max
        self.tau = tau

    def entropy(self, t: float) -> float:
        """Entropy as a function of time: S(t) = S_max * sigmoid(t/tau).

        Uses a logistic curve to model the monotonic increase of entropy
        from near-zero (early universe) to saturation.
        """
        return self.S_max / (1.0 + math.exp(-t / self.tau))

    def dS_dt(self, t: float) -> float:
        """Time derivative of entropy: dS/dt.

        This is the entropy gradient that defines the local arrow of time.
        """
        s = self.entropy(t)
        return s * (1.0 - s / self.S_max) / self.tau

    def energy_flow_magnitude(self, t: float) -> float:
        """Energy flow magnitude at time t.

        Proportional to dS/dt -- energy flows where entropy changes.
        """
        return self.dS_dt(t)

    def now_profile(self, t: float) -> float:
        """The Now profile: product of entropy and its gradient.

        Peaks at the epoch of maximal state transition activity.
        """
        return self.entropy(t) * self.dS_dt(t)

    def peak_now_time(self) -> float:
        """Approximate time at which the Now profile peaks.

        For the logistic model this occurs slightly after t=0.
        """
        # Numerical search over a grid
        best_t = 0.0
        best_val = 0.0
        for i in range(-100, 101):
            t = i * self.tau * 0.1
            val = self.now_profile(t)
            if val > best_val:
                best_val = val
                best_t = t
        return best_t

    def gradient_at(self, t: float) -> EntropyGradient:
        """Return the EntropyGradient at time t."""
        return EntropyGradient(dS_dt=self.dS_dt(t), S_local=self.entropy(t))

    def state_at(self, t: float) -> TemporalState:
        """Return the full TemporalState at time t."""
        return TemporalState(
            t=t,
            S=self.entropy(t),
            energy_flow=self.energy_flow_magnitude(t),
        )

    def __repr__(self) -> str:
        return f"EnergyFlowNow(S_max={self.S_max}, tau={self.tau})"
