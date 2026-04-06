"""R(k,S) Regime Response Surface -- core classes.

The response surface R(k,S) encodes gravitational deviation from GR as
a function of scale k and structural state S. The modified Poisson
equation becomes mu(k,S) = 1 + R(k,S).

Author: Morten Magnusson (ORCID 0009-0002-4860-5095)
License: CC-BY-4.0
"""

import math


class StructuralMaturity:
    """The structural maturity parameter S.

    S = ln[sigma^2(z) / sigma^2_lin(z)]

    Measures non-linear structure accumulation. S=0 in the CMB epoch
    (linear regime), S>0 in the late universe (non-linear).

    Parameters
    ----------
    z_mid : float
        Midpoint redshift for the sigmoid model. Default 0.8.
    """

    def __init__(self, z_mid: float = 0.8):
        self.z_mid = z_mid

    def S(self, z: float) -> float:
        """Structural maturity at redshift z.

        Simple sigmoid model: S = 1 / (1 + (z/z_mid)^2)
        """
        return 1.0 / (1.0 + (z / self.z_mid) ** 2)

    def is_linear(self, z: float, threshold: float = 0.05) -> bool:
        """Check if we are in the linear regime (S ~ 0)."""
        return self.S(z) < threshold

    def is_nonlinear(self, z: float, threshold: float = 0.5) -> bool:
        """Check if we are in the non-linear regime (S > threshold)."""
        return self.S(z) > threshold

    def __repr__(self) -> str:
        return f"StructuralMaturity(z_mid={self.z_mid})"


class ResponseCoordinate:
    """A single point on the R(k,S) surface.

    Parameters
    ----------
    k : float
        Wavenumber (h/Mpc).
    S : float
        Structural maturity value.
    R : float
        Response value (deviation from GR).
    """

    def __init__(self, k: float, S: float, R: float):
        self.k = k
        self.S = S
        self.R = R

    def mu(self) -> float:
        """Modified gravity parameter: mu = 1 + R."""
        return 1.0 + self.R

    def is_gr(self, threshold: float = 0.01) -> bool:
        """Check if this point is consistent with GR (R ~ 0)."""
        return abs(self.R) < threshold

    def __repr__(self) -> str:
        return f"ResponseCoordinate(k={self.k}, S={self.S}, R={self.R})"


class RegimeResponseSurface:
    """The full R(k,S) response surface.

    Models the gravitational deviation from GR as a function of scale
    and structural maturity.

    The S8 tension (~0.79 vs ~0.83) is interpreted as an L1->L2 regime
    transition rather than systematic error.

    Parameters
    ----------
    R_max : float
        Maximum response amplitude. Default 0.30.
    k_pivot : float
        Pivot wavenumber (h/Mpc). Default 0.13.
    S_pivot : float
        Pivot structural maturity. Default 0.30.
    n_k : float
        Scale dependence power index. Default 1.0.
    n_S : float
        Maturity dependence power index. Default 1.0.
    """

    def __init__(self, R_max: float = 0.30, k_pivot: float = 0.13,
                 S_pivot: float = 0.30, n_k: float = 1.0, n_S: float = 1.0):
        self.R_max = R_max
        self.k_pivot = k_pivot
        self.S_pivot = S_pivot
        self.n_k = n_k
        self.n_S = n_S

    def R(self, k: float, S: float) -> float:
        """Evaluate the response surface at (k, S).

        R(k,S) = R_max * (k/k_pivot)^n_k * (S/S_pivot)^n_S
                 * exp(-(k/k_pivot - 1)^2) * sigmoid(S)

        Simplified model that captures the key features:
        R ~ 0 when S ~ 0 (CMB), R > 0 when S > 0 (late universe).
        """
        if k <= 0 or S <= 0:
            return 0.0
        k_ratio = k / self.k_pivot
        S_factor = S / (S + self.S_pivot)  # sigmoid-like saturation
        scale_factor = math.exp(-0.5 * (k_ratio - 1.0) ** 2)
        return self.R_max * scale_factor * S_factor

    def mu(self, k: float, S: float) -> float:
        """Modified gravity parameter: mu(k,S) = 1 + R(k,S)."""
        return 1.0 + self.R(k, S)

    def coordinate(self, k: float, S: float) -> ResponseCoordinate:
        """Return a ResponseCoordinate at (k,S)."""
        return ResponseCoordinate(k=k, S=S, R=self.R(k, S))

    def s8_prediction(self, S8_cmb: float = 0.83, S: float = 0.30) -> float:
        """Predicted S8 from late-universe probes given CMB S8.

        S8_late = S8_cmb / sqrt(mu(k_pivot, S))
        Enhanced gravity means late probes measure lower S8.
        """
        mu_val = self.mu(self.k_pivot, S)
        return S8_cmb / math.sqrt(mu_val)

    def falsification_check(self, coordinates: list) -> dict:
        """Check falsification criteria against a set of coordinates.

        Parameters
        ----------
        coordinates : list of ResponseCoordinate
            Measured (k,S,R) points.

        Returns
        -------
        dict with criteria results.
        """
        if not coordinates:
            return {"tomographic_consistency": None, "trend_sign": None}

        # Tomographic consistency: all points should agree on R sign
        signs = [1 if c.R > 0 else (-1 if c.R < 0 else 0)
                 for c in coordinates]
        consistent = len(set(s for s in signs if s != 0)) <= 1

        # Trend sign matching
        positive_trend = all(c.R >= 0 for c in coordinates)

        return {
            "tomographic_consistency": consistent,
            "trend_sign_positive": positive_trend,
            "n_points": len(coordinates),
        }

    def __repr__(self) -> str:
        return (f"RegimeResponseSurface(R_max={self.R_max}, "
                f"k_pivot={self.k_pivot}, S_pivot={self.S_pivot})")
