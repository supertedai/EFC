"""
EFC-BIC Pipeline v0.1
=====================

Operational pipeline for evaluating the EFC Bar Instability Criterion (Π_EFC)
from SPARC-style rotation curve data.

Implements (per validation candidate vc_2f367f3bfc86 / EFCValidation
test_id conv_efc_bar_instability_criterion_efc_bic_v0_2_modification_with):

    g(r) = v² / r                                     [m/s²]
    ∇S ≡ d(v²)/dr   (primary proxy)                   [m/s²]
    g_EFC ≡ α · ∇S                                    [m/s²]
    κ² = (2v/r) · (v/r + dv/dr)                       [s⁻²]
    κ²_eff = κ² + ζ · g_EFC / r                       [s⁻²]
    Π_EFC = σ_R · κ_eff / (3.36 · G · Σ)              [dimensionless]

Design decisions (Morten sign-off):
  - Derivatives: central differencing (raw) AND Savitzky-Golay (window=5,
    order=2) computed in parallel. Spline rejected (edge artifacts).
  - ∇S form: linear (d(v²)/dr). Logarithmic version reserved as separate
    robustness check.
  - Evaluation radius: R_eval = 2.2·R_d primary; median(r) fallback.
  - Π_EFC binary criterion uses min Π over R ∈ [R_d, 3·R_d].
  - RAR-degeneracy: always computed at sample level, classified
    (independent / partially_degenerate / degenerate_with_RAR), never
    blocks output.
  - ζ universal across L3, NOT calibrated yet. Default ζ=1.0 used for
    pipeline verification only — absolute Π values are unanchored
    until ζ-lock on N=20 SPARC pilot.

This file is the pipeline only. No real SPARC data shipped here.
The __main__ block runs synthetic test galaxies for code verification.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Optional

import numpy as np
from scipy.signal import savgol_filter
from scipy.stats import linregress

# -- Unit conversions: SPARC convention is r in kpc, v in km/s, Σ in M_sun/pc²
KPC_TO_M = 3.0857e19
KMS_TO_MS = 1.0e3
MSUN_PER_PC2_TO_KG_PER_M2 = 1.989e30 / (3.0857e16) ** 2  # ~ 2.09e-3
G_SI = 6.6743e-11

# --------------------------------------------------------------------------
# Data containers
# --------------------------------------------------------------------------

@dataclass
class GalaxyInput:
    """SPARC-style input for one galaxy. Arrays must be co-sampled in r."""
    name: str
    r_kpc: np.ndarray
    v_kms: np.ndarray
    sigma_R_kms: np.ndarray
    Sigma_Msun_pc2: np.ndarray
    R_d_kpc: float
    alpha: float
    bar_classification: str = "unknown"  # "bar" | "no_bar" | "unknown"

    def __post_init__(self):
        for arr_name in ("r_kpc", "v_kms", "sigma_R_kms", "Sigma_Msun_pc2"):
            arr = np.asarray(getattr(self, arr_name), dtype=float)
            object.__setattr__(self, arr_name, arr)
        n = len(self.r_kpc)
        for arr_name in ("v_kms", "sigma_R_kms", "Sigma_Msun_pc2"):
            if len(getattr(self, arr_name)) != n:
                raise ValueError(f"{self.name}: array length mismatch for {arr_name}")


@dataclass
class GalaxyResult:
    name: str
    bar_classification: str

    R_eval_kpc: float
    R_eval_method: str  # "2.2_Rd" | "median_fallback"

    # Π_EFC at R_eval, both derivative methods
    Pi_EFC_raw: float
    Pi_EFC_SG: float
    # min over [R_d, 3 R_d]
    Pi_min_R_raw: float
    Pi_min_R_SG: float

    # Diagnostics at R_eval (raw method)
    g_obs_at_eval: float          # v²/r        [m/s²]
    nablaS_at_eval: float         # d(v²)/dr    [m/s²]
    g_EFC_at_eval: float          # α·∇S        [m/s²]
    kappa2: float                 # κ²          [s⁻²]
    kappa2_eff: float             # κ² + ζ·g_EFC/r  [s⁻²]

    # Robustness flags
    derivative_consistency: bool  # raw vs SG within tolerance at R_eval
    edge_evaluation: bool         # R_eval near array boundary
    sg_applied: bool              # False if N<5
    kappa2_eff_sign: str          # "positive" | "negative_at_eval"


# --------------------------------------------------------------------------
# Numerical primitives
# --------------------------------------------------------------------------

def central_diff(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Central difference on possibly non-uniform grid; NaN at endpoints."""
    out = np.full_like(y, np.nan, dtype=float)
    out[1:-1] = (y[2:] - y[:-2]) / (x[2:] - x[:-2])
    return out


def savgol_deriv(x: np.ndarray, y: np.ndarray, window: int = 5, order: int = 2) -> np.ndarray:
    """SG first derivative, assumes near-uniform spacing.

    Falls back to NaN array if N < window.

    Implementation note: scipy.signal.savgol_filter becomes numerically
    unstable when `delta` spans many orders of magnitude (e.g. delta ~ 1e19 m
    for galactocentric radius in SI). The polynomial fit's normal equations
    become ill-conditioned. We avoid this by computing the SG derivative on
    unit-spaced indices (delta=1, dimensionless) and dividing the output by
    the true mean spacing in physical units afterward. Verified against
    central differencing and analytical d(x²)/dx tests.
    """
    if len(y) < window:
        return np.full_like(y, np.nan, dtype=float)
    dr_phys = float(np.median(np.diff(x)))
    if dr_phys <= 0:
        return np.full_like(y, np.nan, dtype=float)
    # SG on unit-spaced grid → result is dy / d(index)
    sg_unit = savgol_filter(y, window_length=window, polyorder=order, deriv=1, delta=1.0)
    # Convert to dy/dx = (dy/d index) / (dx/d index)
    return sg_unit / dr_phys


# --------------------------------------------------------------------------
# Per-galaxy processing
# --------------------------------------------------------------------------

def _interp_at(x: np.ndarray, y: np.ndarray, x0: float) -> float:
    """1D linear interpolation, ignoring NaNs."""
    mask = np.isfinite(y)
    if mask.sum() < 2:
        return float("nan")
    return float(np.interp(x0, x[mask], y[mask]))


def process_galaxy(g: GalaxyInput, zeta: float = 1.0,
                   proxy_mode: str = "v_squared") -> GalaxyResult:
    """Run pipeline on one galaxy. Returns GalaxyResult.

    proxy_mode selects the ∇S proxy:
      "v_squared" (default, v0.1 spec):   ∇S ≡ d(v²)/dr
      "shear":                             ∇S ≡ v·r·(dΩ/dr),  Ω = v/r
                                           (equivalently v²·d(ln Ω)/dr)
    Both forms have units of acceleration [m/s²]. Shear gives the negative
    sign expected for a destabilizing contribution in differentially
    rotating disks (dΩ/dr < 0 → ∇S < 0 → g_EFC < 0 → κ²_eff < κ²).
    """
    # SI unit arrays
    r = g.r_kpc * KPC_TO_M
    v = g.v_kms * KMS_TO_MS
    sigma_R = g.sigma_R_kms * KMS_TO_MS
    Sigma = g.Sigma_Msun_pc2 * MSUN_PER_PC2_TO_KG_PER_M2
    R_d = g.R_d_kpc * KPC_TO_M

    # g(r) = v²/r — stored explicitly for inspection
    g_obs = v ** 2 / r  # [m/s²]

    # ∇S proxy
    if proxy_mode == "v_squared":
        v_sq = v ** 2
        nablaS_raw = central_diff(r, v_sq)
        nablaS_sg = savgol_deriv(r, v_sq)
    elif proxy_mode == "shear":
        omega = v / r                                  # [1/s]
        dOmega_raw = central_diff(r, omega)            # [1/(m·s)]
        dOmega_sg = savgol_deriv(r, omega)
        nablaS_raw = v * r * dOmega_raw                # [m/s²]
        nablaS_sg = v * r * dOmega_sg
    else:
        raise ValueError(f"unknown proxy_mode: {proxy_mode!r}")

    # dv/dr for κ²
    dvdr_raw = central_diff(r, v)
    dvdr_sg = savgol_deriv(r, v)

    # κ² = (2v/r)(v/r + dv/dr)
    base_omega2 = (2.0 * v / r) * (v / r)  # = 2 v²/r²
    kappa2_raw = base_omega2 + (2.0 * v / r) * dvdr_raw
    kappa2_sg = base_omega2 + (2.0 * v / r) * dvdr_sg

    # g_EFC and κ²_eff
    g_EFC_raw = g.alpha * nablaS_raw
    g_EFC_sg = g.alpha * nablaS_sg
    kappa2_eff_raw = kappa2_raw + zeta * g_EFC_raw / r
    kappa2_eff_sg = kappa2_sg + zeta * g_EFC_sg / r

    # Π_EFC. If κ²_eff < 0, take sqrt of absolute and flag (mode is unstable
    # in a stronger sense than Q < 1 — flag separately).
    def _pi(kappa2_eff_arr):
        kappa_eff = np.sqrt(np.abs(kappa2_eff_arr)) * np.sign(kappa2_eff_arr)
        # σ·κ_eff/(3.36 G Σ); negative κ² → negative Π means "stiffness lost"
        return sigma_R * kappa_eff / (3.36 * G_SI * Sigma)

    Pi_raw = _pi(kappa2_eff_raw)
    Pi_sg = _pi(kappa2_eff_sg)

    # Evaluation radius
    R_eval = 2.2 * R_d
    if R_eval < r.min() or R_eval > r.max():
        R_eval = float(np.median(r))
        R_eval_method = "median_fallback"
    else:
        R_eval_method = "2.2_Rd"

    # Per-radius diagnostics at R_eval
    pi_raw_eval = _interp_at(r, Pi_raw, R_eval)
    pi_sg_eval = _interp_at(r, Pi_sg, R_eval) if len(r) >= 5 else float("nan")
    g_obs_eval = _interp_at(r, g_obs, R_eval)
    nablaS_eval = _interp_at(r, nablaS_raw, R_eval)
    g_EFC_eval = _interp_at(r, g_EFC_raw, R_eval)
    kappa2_eval = _interp_at(r, kappa2_raw, R_eval)
    kappa2_eff_eval = _interp_at(r, kappa2_eff_raw, R_eval)

    # min Π over [R_d, 3 R_d]
    mask = (r >= R_d) & (r <= 3.0 * R_d)
    if not mask.any():
        mask = np.ones_like(r, dtype=bool)
    finite_mask_raw = mask & np.isfinite(Pi_raw)
    finite_mask_sg = mask & np.isfinite(Pi_sg)
    Pi_min_raw = float(np.min(Pi_raw[finite_mask_raw])) if finite_mask_raw.any() else float("nan")
    Pi_min_sg = float(np.min(Pi_sg[finite_mask_sg])) if finite_mask_sg.any() else float("nan")

    # Consistency flag (30% tolerance)
    if np.isnan(pi_sg_eval) or np.isnan(pi_raw_eval):
        consistency = True
    else:
        denom = max(abs(pi_raw_eval), abs(pi_sg_eval), 1e-30)
        consistency = abs(pi_raw_eval - pi_sg_eval) / denom < 0.30

    # Edge flag — within 1 sample of array boundary
    idx_eval = int(np.searchsorted(r, R_eval))
    edge_flag = idx_eval <= 1 or idx_eval >= len(r) - 1

    return GalaxyResult(
        name=g.name,
        bar_classification=g.bar_classification,
        R_eval_kpc=R_eval / KPC_TO_M,
        R_eval_method=R_eval_method,
        Pi_EFC_raw=pi_raw_eval,
        Pi_EFC_SG=pi_sg_eval,
        Pi_min_R_raw=Pi_min_raw,
        Pi_min_R_SG=Pi_min_sg,
        g_obs_at_eval=g_obs_eval,
        nablaS_at_eval=nablaS_eval,
        g_EFC_at_eval=g_EFC_eval,
        kappa2=kappa2_eval,
        kappa2_eff=kappa2_eff_eval,
        derivative_consistency=bool(consistency),
        edge_evaluation=bool(edge_flag),
        sg_applied=len(r) >= 5,
        kappa2_eff_sign="positive" if (kappa2_eff_eval > 0) else "negative_at_eval",
    )


# --------------------------------------------------------------------------
# Sample-level RAR-degeneracy diagnostic
# --------------------------------------------------------------------------

def rar_degeneracy_test(results: list[GalaxyResult]) -> dict:
    """Regress Π_EFC vs g_obs across the sample.

    Output flags:
      R² > 0.9   → degenerate_with_RAR
      0.7 ≤ R² ≤ 0.9 → partially_degenerate
      R² < 0.7   → independent_signal
    """
    pi = np.array([r.Pi_EFC_raw for r in results])
    g_obs = np.array([r.g_obs_at_eval for r in results])
    mask = np.isfinite(pi) & np.isfinite(g_obs)
    n = int(mask.sum())
    if n < 3:
        return {"status": "insufficient_data", "n": n}
    slope, intercept, r_val, p_val, _ = linregress(g_obs[mask], pi[mask])
    r2 = float(r_val ** 2)
    if r2 > 0.9:
        flag = "degenerate_with_RAR"
    elif r2 >= 0.7:
        flag = "partially_degenerate"
    else:
        flag = "independent_signal"
    return {
        "n": n,
        "r_squared": r2,
        "slope": float(slope),
        "intercept": float(intercept),
        "p_value": float(p_val),
        "degeneracy_flag": flag,
    }


# --------------------------------------------------------------------------
# Top-level run
# --------------------------------------------------------------------------

def run_pipeline(galaxies: list[GalaxyInput], zeta: float = 1.0,
                 proxy_mode: str = "v_squared") -> dict:
    """Run the full pipeline on a list of GalaxyInput. Returns serializable dict."""
    results = [process_galaxy(g, zeta=zeta, proxy_mode=proxy_mode) for g in galaxies]
    rar = rar_degeneracy_test(results)
    return {
        "version": "efc_bic_pipeline_v0.1",
        "validation_test_id": "conv_efc_bar_instability_criterion_efc_bic_v0_2_modification_with",
        "zeta_used": zeta,
        "proxy_mode": proxy_mode,
        "zeta_status": "REFERENCE_VALUE_NOT_CALIBRATED",
        "n_galaxies": len(galaxies),
        "rar_degeneracy_test": rar,
        "per_galaxy": [asdict(r) for r in results],
    }


# --------------------------------------------------------------------------
# Synthetic test data — for code verification ONLY, NOT real SPARC
# --------------------------------------------------------------------------

def _synthetic_galaxy(
    name: str,
    v_flat: float,
    R_d: float,
    sigma_R0: float,
    Sigma0: float,
    alpha: float,
    bar_class: str,
    n_pts: int = 30,
) -> GalaxyInput:
    r = np.linspace(0.5, 4.0 * R_d, n_pts)
    v = v_flat * np.tanh(r / R_d)
    Sigma = Sigma0 * np.exp(-r / R_d)
    sigma_R = np.full_like(r, sigma_R0)
    return GalaxyInput(
        name=name,
        r_kpc=r,
        v_kms=v,
        sigma_R_kms=sigma_R,
        Sigma_Msun_pc2=Sigma,
        R_d_kpc=R_d,
        alpha=alpha,
        bar_classification=bar_class,
    )


if __name__ == "__main__":
    # SYNTHETIC galaxies — code verification only.
    # NOT real SPARC. Do NOT interpret as evidence for or against EFC-BIC.
    test = [
        _synthetic_galaxy("NGC6503_synthetic", v_flat=115, R_d=2.2, sigma_R0=30,
                          Sigma0=200, alpha=0.65, bar_class="no_bar"),
        _synthetic_galaxy("NGC3198_synthetic", v_flat=150, R_d=3.1, sigma_R0=35,
                          Sigma0=180, alpha=0.60, bar_class="no_bar"),
        _synthetic_galaxy("NGC2841_synthetic", v_flat=280, R_d=4.0, sigma_R0=80,
                          Sigma0=400, alpha=0.25, bar_class="bar"),
    ]
    out = run_pipeline(test, zeta=1.0)
    print(json.dumps(out, indent=2, default=str))
