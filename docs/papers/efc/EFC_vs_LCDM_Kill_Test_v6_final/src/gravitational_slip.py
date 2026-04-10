"""
Gravitational slip from δλ counter-term — Section 5 of the Kill-Test v6 paper.

    δλ = (V''/a²) · δφ − (K · k²/a²) · δφ + ...

    f = 1 − V''(φ̄) / (K(ρ̄) · k²/a²)

Sweet spot: f = 0.15 ⇒ η = 1.23 ⇒ Σ = 1.05.

Viable window: f ∈ [0.12, 0.18] (25% wide, not fine-tuned).
At full strength f = 1: η = 2.34 (excluded).

The function (f → η → Σ) is calibrated against Table 4 of the paper.
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional


# Calibration anchor values from Table 4 of the paper.
# Column headings: f, η, Σ, Δχ²(est.), Status
TABLE_4: List[Dict[str, float]] = [
    {"f": 0.00, "eta": 1.04, "Sigma": 0.96, "delta_chi2": 30.0, "status": "Excluded"},
    {"f": 0.12, "eta": 1.20, "Sigma": 1.03, "delta_chi2": 4.0, "status": "Entering window"},
    {"f": 0.15, "eta": 1.23, "Sigma": 1.05, "delta_chi2": -0.45, "status": "Sweet spot"},
    {"f": 0.18, "eta": 1.27, "Sigma": 1.07, "delta_chi2": 0.5, "status": "Edge of window"},
    {"f": 1.00, "eta": 2.34, "Sigma": 1.57, "delta_chi2": 100.0, "status": "Excluded"},
]

# Derived window from Table 4
SWEET_SPOT_F = 0.15
SWEET_SPOT_ETA = 1.23
SWEET_SPOT_SIGMA = 1.05
F_WINDOW_LOWER = 0.12
F_WINDOW_UPPER = 0.18


def _linear_interp(x: float, x_lo: float, x_hi: float, y_lo: float, y_hi: float) -> float:
    """Linear interpolation helper."""
    if x_hi == x_lo:
        return y_lo
    return y_lo + (y_hi - y_lo) * (x - x_lo) / (x_hi - x_lo)


def eta_from_f(f: float) -> float:
    """
    Interpolate η(f) from Table 4.

    Parameters
    ----------
    f : float
        Slip strength, f ∈ [0, 1].

    Returns
    -------
    float
        Gravitational slip η.
    """
    if f <= TABLE_4[0]["f"]:
        return TABLE_4[0]["eta"]
    if f >= TABLE_4[-1]["f"]:
        return TABLE_4[-1]["eta"]
    for i in range(len(TABLE_4) - 1):
        lo, hi = TABLE_4[i], TABLE_4[i + 1]
        if lo["f"] <= f <= hi["f"]:
            return _linear_interp(f, lo["f"], hi["f"], lo["eta"], hi["eta"])
    return TABLE_4[-1]["eta"]


def Sigma_from_f(f: float) -> float:
    """
    Interpolate Σ(f) from Table 4.

    Parameters
    ----------
    f : float
        Slip strength.

    Returns
    -------
    float
        Lensing modification Σ.
    """
    if f <= TABLE_4[0]["f"]:
        return TABLE_4[0]["Sigma"]
    if f >= TABLE_4[-1]["f"]:
        return TABLE_4[-1]["Sigma"]
    for i in range(len(TABLE_4) - 1):
        lo, hi = TABLE_4[i], TABLE_4[i + 1]
        if lo["f"] <= f <= hi["f"]:
            return _linear_interp(f, lo["f"], hi["f"], lo["Sigma"], hi["Sigma"])
    return TABLE_4[-1]["Sigma"]


def in_window(f: float) -> bool:
    """Return True if f is inside the sweet-spot window [0.12, 0.18]."""
    return F_WINDOW_LOWER <= f <= F_WINDOW_UPPER


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------

@dataclass
class GravSlip:
    """
    Gravitational slip calculator at a given m².

    With m² = 0.0035 (reference), the counter-term yields f = 0.15 which
    hits the sweet spot (η = 1.23, Σ = 1.05).

    Attributes
    ----------
    m2 : float
        Mass-squared parameter (e.g. 0.0035).
    f : float
        Slip strength derived from m² (linear approximation around reference).
    eta : float
        Gravitational slip η.
    Sigma : float
        Lensing modification Σ.
    """
    m2: float = 0.0035

    @property
    def f(self) -> float:
        """
        Slip strength f from m², calibrated against reference m² = 0.0035 → f = 0.15.

        A simple linear scaling: f ∝ m² around the reference point.
        """
        return 0.15 * (self.m2 / 0.0035)

    @property
    def eta(self) -> float:
        return eta_from_f(self.f)

    @property
    def Sigma(self) -> float:
        return Sigma_from_f(self.f)

    @property
    def status(self) -> str:
        """Return window status: 'sweet spot', 'window', or 'excluded'."""
        f = self.f
        if abs(f - SWEET_SPOT_F) < 1e-6:
            return "Sweet spot"
        if F_WINDOW_LOWER <= f <= F_WINDOW_UPPER:
            return "Inside window"
        return "Outside window"


def slip_scan(f_values: Optional[List[float]] = None) -> List[Dict[str, float]]:
    """
    Evaluate (η, Σ) for a list of f values using Table 4 interpolation.

    Parameters
    ----------
    f_values : list of float, optional
        f-values to evaluate; defaults to the canonical Table 4 points.

    Returns
    -------
    list of dict
        One entry per f with keys 'f', 'eta', 'Sigma', 'in_window'.
    """
    if f_values is None:
        f_values = [row["f"] for row in TABLE_4]
    return [
        {
            "f": round(f, 4),
            "eta": round(eta_from_f(f), 4),
            "Sigma": round(Sigma_from_f(f), 4),
            "in_window": in_window(f),
        }
        for f in f_values
    ]


# ---------------------------------------------------------------------------
# Demonstration / self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Gravitational slip — Table 4 reproduction:")
    print(f"{'f':>6} {'η':>6} {'Σ':>6} {'in window?':>12}")
    for row in slip_scan():
        print(
            f"{row['f']:>6.2f} {row['eta']:>6.2f} {row['Sigma']:>6.2f} "
            f"{'yes' if row['in_window'] else 'no':>12}"
        )
    print()
    slip = GravSlip(m2=0.0035)
    print(f"Reference m² = 0.0035 → f = {slip.f:.3f}, "
          f"η = {slip.eta:.3f}, Σ = {slip.Sigma:.3f}  ({slip.status})")
