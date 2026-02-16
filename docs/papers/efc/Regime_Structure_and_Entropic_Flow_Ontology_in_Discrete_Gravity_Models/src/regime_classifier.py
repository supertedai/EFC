"""
Regime classifier for discrete entropic gravity.

Classifies field configurations into UV, IR, or Cosmological regimes
using the dimensionless ratios:

    ξ = |∇Φ| / a₀          (gradient strength)
    η = μ_Λ Φ / |∇²Φ|      (bulk strength)

Regime dominance map (Section 4, Eq. 9):
    UV (Newtonian):   ξ >> 1, η << 1  →  g ∝ r⁻²
    IR (MOND-like):   ξ << 1, η << 1  →  g ∝ r⁻¹
    Cosmological:     any ξ,  η >> 1   →  Yukawa screening
"""

import math
from dataclasses import dataclass
from typing import Optional


C_LIGHT = 2.998e8          # m/s
LAMBDA_PLANCK = 1.11e-52   # m⁻²
A0_DEFAULT = 1.2e-10       # m/s²


@dataclass
class RegimeResult:
    """Result of regime classification."""
    regime: str
    xi: float
    eta: float
    behaviour: str
    field_equation: str
    dominant_sector: str


def regime_ratios(grad_phi: float, a0: float, mu_lambda: float,
                  phi: float, laplacian_phi: float) -> tuple:
    """
    Compute dimensionless regime ratios (ξ, η).

    Parameters
    ----------
    grad_phi : float
        |∇Φ| — magnitude of potential gradient.
    a0 : float
        MOND acceleration scale.
    mu_lambda : float
        Bulk coupling strength (μ_Λ ∝ Λ).
    phi : float
        Local potential Φ.
    laplacian_phi : float
        |∇²Φ| — magnitude of Laplacian.

    Returns
    -------
    tuple of (float, float)
        (ξ, η) dimensionless ratios.
    """
    xi = grad_phi / a0
    if laplacian_phi == 0:
        eta = float('inf') if mu_lambda * phi != 0 else 0.0
    else:
        eta = abs(mu_lambda * phi / laplacian_phi)
    return xi, eta


def classify_regime(xi: float, eta: float, threshold: float = 1.0) -> RegimeResult:
    """
    Classify a field configuration into UV, IR, or Cosmological regime.

    Parameters
    ----------
    xi : float
        ξ = |∇Φ|/a₀ (gradient strength ratio).
    eta : float
        η = μ_Λ Φ/|∇²Φ| (bulk strength ratio).
    threshold : float
        Transition boundary (default 1.0).

    Returns
    -------
    RegimeResult
        Classification with regime name, ratios, and properties.
    """
    if eta > threshold:
        return RegimeResult(
            regime="Cosmological",
            xi=xi,
            eta=eta,
            behaviour="Yukawa screening",
            field_equation="∇²Φ − μ_Λ Φ = 4πGρ",
            dominant_sector="bulk"
        )
    elif xi > threshold:
        return RegimeResult(
            regime="UV (Newtonian)",
            xi=xi,
            eta=eta,
            behaviour="g ∝ r⁻²",
            field_equation="∇²Φ = 4πGρ",
            dominant_sector="gradient (linear)"
        )
    else:
        return RegimeResult(
            regime="IR (MOND-like)",
            xi=xi,
            eta=eta,
            behaviour="g ∝ r⁻¹",
            field_equation="∇·(|∇Φ|/a₀ ∇Φ) = 4πGρ",
            dominant_sector="gradient (nonlinear)"
        )


def transition_scales(Lambda: float = LAMBDA_PLANCK,
                      a0: float = A0_DEFAULT,
                      c: float = C_LIGHT) -> dict:
    """
    Compute the physical transition scales.

    Parameters
    ----------
    Lambda : float
        Cosmological constant in m⁻².
    a0 : float
        MOND acceleration scale in m/s².
    c : float
        Speed of light in m/s.

    Returns
    -------
    dict
        Transition scales and derived quantities.
    """
    L_Lambda_m = 1.0 / math.sqrt(Lambda)
    L_Lambda_Mpc = L_Lambda_m / 3.086e22
    L_Lambda_Gpc = L_Lambda_Mpc / 1000.0

    a0_from_Lambda = c * c * math.sqrt(Lambda)

    return {
        "UV_to_IR": {
            "condition": "ξ ~ 1, i.e., |∇Φ| ~ a₀",
            "a0_m_s2": a0,
            "description": "Gradient field strength equals MOND scale"
        },
        "IR_to_Cosmological": {
            "condition": "η ~ 1, i.e., scales approaching L_Λ",
            "L_Lambda_m": L_Lambda_m,
            "L_Lambda_Gpc": round(L_Lambda_Gpc, 1),
            "description": "Bulk term overtakes gradient sector"
        },
        "lambda_dual_role": {
            "a0_from_Lambda": a0_from_Lambda,
            "a0_observed": a0,
            "L_Lambda_Gpc": round(L_Lambda_Gpc, 1),
            "note": "a₀ ∝ c²√Λ and L_Λ ∝ Λ⁻¹/² both set by single parameter"
        }
    }


def screening_length(Lambda: float = LAMBDA_PLANCK) -> float:
    """
    Compute Λ-locked screening length L_Λ.

        L_Λ = 1/√Λ

    Parameters
    ----------
    Lambda : float
        Cosmological constant in m⁻².

    Returns
    -------
    float
        Screening length in Gpc.
    """
    L_m = 1.0 / math.sqrt(Lambda)
    return L_m / 3.086e25  # convert m to Gpc
