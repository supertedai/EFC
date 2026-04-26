"""
SPARC Loader for EFC-BIC Pipeline
==================================

Loads SPARC-175 rotation curves into GalaxyInput objects for efc_bic_pipeline.

Per galaxy:
  V(R), Σ(R), R_d, σ_R(R), α, regime

Conventions (Lelli+2016 SPARC paper):
  V_obs in km/s, R in kpc, SB in L_sun/pc² @ 3.6μm
  Υ_disk  = 0.5 M_sun/L_sun  (stellar M/L for disk)
  Υ_bulge = 0.7 M_sun/L_sun  (stellar M/L for bulge)
  Σ(R) = Υ_disk·SBdisk(R) + Υ_bulge·SBbulge(R)   [M_sun/pc²]

R_d (radial disk scale length):
  Independent tanh fit to V(R): V(R) = V_flat·tanh(R/R_d).
  Robust, doesn't depend on previous SPARC-175 fit conventions.

σ_R (radial velocity dispersion):
  PRIMARY  (Σ-based):  σ_R(R) = √(π·G·Σ(R)·R_d)    [Jeans-inspired]
  FALLBACK (constant): σ_R(R) = 30 km/s             [if Σ unavailable / fit failed]

α (EFC flow fraction):
  α = 1 - L  where L = latent fraction from sparc175_classified.json
  Bounded to [0.05, 0.95] to avoid degenerate edges.

Diagnostic:
  σ_R/v ratio logged per galaxy. Flag if outside [0.05, 0.5].
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
from scipy.optimize import curve_fit

# Pipeline import (sibling file)
from efc_bic_pipeline import GalaxyInput

# -- Constants
G_SI = 6.6743e-11                                    # m³ / (kg·s²)
KPC_TO_M = 3.0857e19                                 # m / kpc
MSUN_PER_PC2_TO_KG_PER_M2 = 1.989e30 / (3.0857e16)**2   # ~2.09e-3

# -- Lelli+2016 stellar M/L at 3.6μm (SPARC convention)
UPSILON_DISK = 0.5     # M_sun / L_sun
UPSILON_BULGE = 0.7    # M_sun / L_sun

SIGMA_FALLBACK_KMS = 30.0    # constant fallback dispersion


@dataclass
class GalaxyLoadInfo:
    """Diagnostic info from loading. Travels alongside the GalaxyInput."""
    name: str
    n_points: int
    R_d_kpc: float
    R_d_method: str               # "tanh_fit" | "median_radius_fallback"
    V_flat_kms: Optional[float]   # asymptotic v from tanh fit
    alpha: float
    L_latent: float
    regime: str                   # FLOW | TRANSITION | LATENT | UNKNOWN
    sigma_mode: str               # "sigma_jeans" | "fallback_constant"
    sigma_over_v_median: float    # diagnostic: median σ_R/V across radius
    sigma_over_v_flag: str        # "ok" | "very_low" | "very_high"


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def parse_sparc_dat(path: Path) -> dict[str, dict]:
    """
    Parse the SPARC rotation curves .dat file into a per-galaxy dict.

    Columns (whitespace-separated):
       0: name
       1: D (Mpc)
       2: R (kpc)
       3: V_obs (km/s)
       4: V_err (km/s)
       5: V_gas (km/s)
       6: V_disk (km/s)
       7: V_bulge (km/s)
       8: SBdisk (L_sun/pc²)
       9: SBbulge (L_sun/pc²)
    """
    galaxies: dict[str, dict] = {}
    with open(path, "r") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 10:
                continue
            name = parts[0]
            try:
                row = {
                    "D_Mpc":    float(parts[1]),
                    "R_kpc":    float(parts[2]),
                    "V_obs":    float(parts[3]),
                    "V_err":    float(parts[4]),
                    "V_gas":    float(parts[5]),
                    "V_disk":   float(parts[6]),
                    "V_bulge":  float(parts[7]),
                    "SBdisk":   float(parts[8]),
                    "SBbulge":  float(parts[9]),
                }
            except ValueError:
                continue
            g = galaxies.setdefault(name, {"D_Mpc": row["D_Mpc"], "rows": []})
            g["rows"].append(row)
    # convert to arrays
    out = {}
    for name, g in galaxies.items():
        rows = sorted(g["rows"], key=lambda r: r["R_kpc"])
        if len(rows) < 3:
            continue
        out[name] = {
            "D_Mpc":   g["D_Mpc"],
            "R_kpc":   np.array([r["R_kpc"]   for r in rows]),
            "V_obs":   np.array([r["V_obs"]   for r in rows]),
            "V_err":   np.array([r["V_err"]   for r in rows]),
            "V_gas":   np.array([r["V_gas"]   for r in rows]),
            "V_disk":  np.array([r["V_disk"]  for r in rows]),
            "V_bulge": np.array([r["V_bulge"] for r in rows]),
            "SBdisk":  np.array([r["SBdisk"]  for r in rows]),
            "SBbulge": np.array([r["SBbulge"] for r in rows]),
        }
    return out


def load_classification(path: Path) -> dict[str, dict]:
    """Returns {name: {regime, L, alpha}} from sparc175_classified.json."""
    with open(path) as fh:
        cls = json.load(fh)
    out = {}
    for name, entry in cls["results"].items():
        L = float(entry.get("latent", {}).get("L", np.nan))
        regime = entry.get("regime", "UNKNOWN")
        # α = 1 - L, bounded to (0.05, 0.95)
        alpha = max(0.05, min(0.95, 1.0 - L)) if np.isfinite(L) else 0.5
        out[name] = {"regime": regime, "L": L, "alpha": alpha}
    return out


# --------------------------------------------------------------------------
# Per-galaxy derivations
# --------------------------------------------------------------------------

def fit_R_d_via_tanh(R_kpc: np.ndarray, V_kms: np.ndarray) -> tuple[float, float, str]:
    """
    Fit V(R) = V_flat·tanh(R/R_d), return (R_d, V_flat, method).
    On failure → (median(R), nan, 'median_radius_fallback').
    """
    try:
        # Initial guesses: V_flat ≈ max(V_obs), R_d ≈ R where V ≈ 0.7·V_max
        V_max = float(np.max(V_kms))
        idx_half = int(np.argmin(np.abs(V_kms - 0.7 * V_max)))
        R_d0 = float(R_kpc[idx_half])
        if R_d0 <= 0:
            R_d0 = float(np.median(R_kpc))
        popt, _ = curve_fit(
            lambda r, vf, rd: vf * np.tanh(r / rd),
            R_kpc, V_kms,
            p0=[V_max, R_d0],
            bounds=([0.1, 0.05], [2000.0, 100.0]),
            maxfev=5000,
        )
        V_flat, R_d = float(popt[0]), float(popt[1])
        if not (0.1 < R_d < 100.0):
            raise ValueError("R_d out of physical range")
        return R_d, V_flat, "tanh_fit"
    except Exception:
        return float(np.median(R_kpc)), float("nan"), "median_radius_fallback"


def compute_Sigma(SBdisk: np.ndarray, SBbulge: np.ndarray) -> np.ndarray:
    """
    Σ(R) [M_sun/pc²] = Υ_disk·SBdisk + Υ_bulge·SBbulge.
    Lelli+2016 stellar M/L convention at 3.6μm.
    """
    return UPSILON_DISK * SBdisk + UPSILON_BULGE * SBbulge


def sigma_R_jeans(Sigma_Msun_pc2: np.ndarray, R_d_kpc: float) -> np.ndarray:
    """
    Jeans-inspired radial dispersion:
       σ_R(R) = √(π·G·Σ(R)·R_d)
    Inputs in SPARC units → result in km/s.
    Returns NaN where Σ ≤ 0.
    """
    Sigma_SI = Sigma_Msun_pc2 * MSUN_PER_PC2_TO_KG_PER_M2   # kg/m²
    R_d_SI = R_d_kpc * KPC_TO_M                              # m
    safe = np.where(Sigma_SI > 0, Sigma_SI, np.nan)
    sigma_ms = np.sqrt(np.pi * G_SI * safe * R_d_SI)         # m/s
    return sigma_ms / 1000.0                                 # km/s


def sigma_over_v_diagnostic(sigma_R: np.ndarray, V: np.ndarray) -> tuple[float, str]:
    mask = np.isfinite(sigma_R) & np.isfinite(V) & (V > 0)
    if not mask.any():
        return float("nan"), "no_data"
    ratio = np.median(sigma_R[mask] / V[mask])
    if ratio < 0.05:
        flag = "very_low"
    elif ratio > 0.5:
        flag = "very_high"
    else:
        flag = "ok"
    return float(ratio), flag


# --------------------------------------------------------------------------
# Top-level loader
# --------------------------------------------------------------------------

def build_galaxy(
    name: str,
    raw: dict,
    cls_entry: dict,
    sigma_mode: str,
    bar_classification: str = "unknown",
) -> tuple[GalaxyInput, GalaxyLoadInfo]:
    """
    Build GalaxyInput + diagnostics for one galaxy.
    sigma_mode: 'sigma_jeans' or 'fallback_constant'.
    """
    R = raw["R_kpc"]
    V = raw["V_obs"]
    SBdisk = raw["SBdisk"]
    SBbulge = raw["SBbulge"]

    # R_d via independent tanh fit
    R_d, V_flat, R_d_method = fit_R_d_via_tanh(R, V)

    # Σ from surface brightness
    Sigma = compute_Sigma(SBdisk, SBbulge)

    # σ_R per requested mode
    if sigma_mode == "sigma_jeans":
        sigma_arr = sigma_R_jeans(Sigma, R_d)
        # If too many NaNs (Σ=0 outer), fill with constant fallback locally
        if not np.isfinite(sigma_arr).any():
            sigma_arr = np.full_like(R, SIGMA_FALLBACK_KMS, dtype=float)
            sigma_mode_used = "fallback_constant"
        else:
            # leave NaNs; pipeline interp_at handles them
            sigma_mode_used = "sigma_jeans"
    elif sigma_mode == "fallback_constant":
        sigma_arr = np.full_like(R, SIGMA_FALLBACK_KMS, dtype=float)
        sigma_mode_used = "fallback_constant"
    else:
        raise ValueError(f"unknown sigma_mode: {sigma_mode}")

    # Diagnostic: σ_R/V ratio
    ratio, flag = sigma_over_v_diagnostic(sigma_arr, V)

    galaxy_input = GalaxyInput(
        name=name,
        r_kpc=R,
        v_kms=V,
        sigma_R_kms=sigma_arr,
        Sigma_Msun_pc2=Sigma,
        R_d_kpc=R_d,
        alpha=cls_entry["alpha"],
        bar_classification=bar_classification,
    )

    info = GalaxyLoadInfo(
        name=name,
        n_points=len(R),
        R_d_kpc=R_d,
        R_d_method=R_d_method,
        V_flat_kms=V_flat,
        alpha=cls_entry["alpha"],
        L_latent=cls_entry["L"],
        regime=cls_entry["regime"],
        sigma_mode=sigma_mode_used,
        sigma_over_v_median=ratio,
        sigma_over_v_flag=flag,
    )
    return galaxy_input, info


def load_sparc_pilot(
    dat_path: Path,
    classified_path: Path,
    galaxy_names: list[str],
    sigma_mode: str = "sigma_jeans",
) -> tuple[list[GalaxyInput], list[GalaxyLoadInfo]]:
    """
    Load a list of named galaxies from SPARC.

    Returns parallel lists (GalaxyInput, GalaxyLoadInfo).
    Galaxies missing from the .dat or classification are silently skipped.
    """
    raw_data = parse_sparc_dat(dat_path)
    cls_data = load_classification(classified_path)

    inputs: list[GalaxyInput] = []
    infos: list[GalaxyLoadInfo] = []
    for name in galaxy_names:
        if name not in raw_data:
            print(f"[skip] {name}: not in SPARC .dat")
            continue
        if name not in cls_data:
            print(f"[skip] {name}: not in classified.json")
            continue
        g, info = build_galaxy(name, raw_data[name], cls_data[name], sigma_mode)
        inputs.append(g)
        infos.append(info)
    return inputs, infos
