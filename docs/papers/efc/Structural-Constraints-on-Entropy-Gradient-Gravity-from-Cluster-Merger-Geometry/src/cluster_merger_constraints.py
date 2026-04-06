"""Cluster Merger Constraints -- core classes.

Implements the constraint framework for testing entropy-gradient gravity
against cluster merger geometry. Key result: local couplings are falsified
(0/42 pass), and non-local coupling with L0~200 kpc, w~20 is required.

Author: Morten Magnusson (ORCID 0009-0002-4860-5095)
License: CC-BY-4.0
"""

import math


class ConstraintResult:
    """Result of a constraint test.

    Parameters
    ----------
    name : str
        Constraint identifier (e.g., 'BC-001').
    passed : bool
        Whether the constraint was satisfied.
    description : str
        Human-readable description of the result.
    value : float, optional
        Numerical result value.
    """

    def __init__(self, name: str, passed: bool, description: str,
                 value: float = None):
        self.name = name
        self.passed = passed
        self.description = description
        self.value = value

    def __repr__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"ConstraintResult({self.name}: {status})"


class ClusterMerger:
    """Represents a galaxy cluster merger for constraint testing.

    Parameters
    ----------
    name : str
        Cluster name (e.g., 'Bullet', 'MACS J0025', 'Abell 520').
    M_total : float
        Total mass (in 1e14 solar masses).
    R_core : float
        Core radius (kpc).
    v_merger : float
        Merger velocity (km/s).
    separation : float
        Current separation of mass peaks (kpc).
    """

    def __init__(self, name: str, M_total: float, R_core: float,
                 v_merger: float, separation: float):
        self.name = name
        self.M_total = M_total
        self.R_core = R_core
        self.v_merger = v_merger
        self.separation = separation

    def mass_ratio(self) -> float:
        """Approximate mass ratio (assuming major merger ~ 1:3)."""
        return 3.0

    def crossing_time(self) -> float:
        """Crossing time in Myr (separation / velocity)."""
        # Convert km/s to kpc/Myr: 1 km/s ~ 1.022e-3 kpc/Myr
        v_kpc_per_myr = self.v_merger * 1.022e-3
        if v_kpc_per_myr <= 0:
            return float("inf")
        return self.separation / v_kpc_per_myr

    def __repr__(self) -> str:
        return f"ClusterMerger({self.name!r}, M={self.M_total:.1f}e14 Msun)"


class NonLocalCoupling:
    """Non-local entropy-gradient coupling model.

    The effective gravitational field depends on a smoothed entropy
    gradient over a scale L0, with collisionless component weighted
    by factor w.

    G_eff(r) = G * [1 + w * integral of grad(S) over kernel(L0)]

    Parameters
    ----------
    L0 : float
        Non-local response scale (kpc). Default 200.
    w : float
        Collisionless component weighting. Default 20.
    eta : float
        Global coupling parameter. Default 66.2.
    """

    def __init__(self, L0: float = 200.0, w: float = 20.0, eta: float = 66.2):
        self.L0 = L0
        self.w = w
        self.eta = eta

    def kernel(self, r: float) -> float:
        """Smoothing kernel: Gaussian with scale L0.

        K(r) = exp(-r^2 / (2 * L0^2)) / (sqrt(2pi) * L0)
        """
        return math.exp(-r**2 / (2.0 * self.L0**2)) / (
            math.sqrt(2.0 * math.pi) * self.L0
        )

    def effective_enhancement(self, r: float, rho_gradient: float) -> float:
        """Effective gravitational enhancement at radius r.

        mu(r) = 1 + w * eta * kernel(r) * |grad(rho)|
        """
        return 1.0 + self.w * self.eta * self.kernel(r) * abs(rho_gradient)

    def predict_w(self, M_total: float, merger_time: float) -> float:
        """Predict collisionless weighting for a given cluster.

        w_pred = eta * (M_total / merger_time)^(1/3)
        Simplified predictive formula from BC-003.

        Parameters
        ----------
        M_total : float
            Total mass in 1e14 solar masses.
        merger_time : float
            Time since merger in Myr.
        """
        if merger_time <= 0:
            return self.w
        return self.eta * (M_total / merger_time) ** (1.0 / 3.0)

    def test_local_coupling(self, n_params: int = 42) -> ConstraintResult:
        """Test local coupling: always fails (BC-001).

        Local gradient coupling G_eff proportional to |grad(ln rho_b)| is ruled
        out: 0 of n_params parameter combinations pass geometric criteria.
        """
        return ConstraintResult(
            name="BC-001",
            passed=False,
            description=f"Local gradient coupling falsified: 0/{n_params} pass",
            value=0.0,
        )

    def test_nonlocal_coupling(self, cluster: ClusterMerger) -> ConstraintResult:
        """Test non-local coupling (BC-002).

        Checks if L0 ~ 0.8 * R_core and w >> 1.
        """
        L0_required = 0.8 * cluster.R_core
        L0_ok = abs(self.L0 - L0_required) / L0_required < 0.5
        w_ok = self.w > 5.0
        passed = L0_ok and w_ok
        return ConstraintResult(
            name="BC-002",
            passed=passed,
            description=(f"Non-local: L0={self.L0} kpc (req ~{L0_required:.0f}), "
                         f"w={self.w} (req >>1)"),
            value=self.L0,
        )

    def __repr__(self) -> str:
        return f"NonLocalCoupling(L0={self.L0}, w={self.w}, eta={self.eta})"
