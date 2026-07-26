#!/usr/bin/env python3
"""
Precompute chi(z) = |dS_hat/dz| from Axiom 0 locked sources.

Produces: chi_of_z_axiom0.csv  (columns: z, s_hat, chi)

This table is DETERMINISTIC and CYCLE-INDEPENDENT:
    - Sources locked: Madau-Dickinson (SFR) + Tacconi/PHIBSS Table 3b beta=2
    - C0 locked: S_hat(z=0) = 0  (SPARC-anchored)
    - z-grid: 0.001 to 3.0 in 10000 steps
    - Smoothing: Savitzky-Golay (window=101, order=3) on dS/dz

The resulting chi(z) and chi_c are CONSTANTS used by EFCVariantG.
They do NOT depend on alpha, MCMC cycles, or any free parameter.

Usage:
    python chi_of_z_axiom0.py
    # => writes chi_of_z_axiom0.csv to same directory

Or import directly:
    from efc_inference.data.chi_of_z_axiom0 import get_chi_table, CHI_C
"""
from __future__ import annotations

import os
import csv
import numpy as np
from typing import Tuple

# ─────────────────────────────────────────────────────────
# Locked sources (identical to axiom0_s_hat.py — no re-fit)
# ─────────────────────────────────────────────────────────

def _rho_sfr_madau_dickinson(z: np.ndarray) -> np.ndarray:
    """Madau-Dickinson (2014) Eq. 15: psi(z) = 0.015*(1+z)^2.7 / [1+((1+z)/2.9)^5.6]"""
    zp1 = 1.0 + z
    return 0.015 * np.power(zp1, 2.7) / (1.0 + np.power(zp1 / 2.9, 5.6))


def _mu_gas_tacconi_beta2(z: np.ndarray) -> np.ndarray:
    """Tacconi/PHIBSS Table 3b, beta=2, MS pivot. Returns mu_gas = M_mol/M*."""
    A, B, F = 0.12, -1.19, -3.62
    x = np.log10(1.0 + z)
    return np.power(10.0, A + B * np.square(x - F))


def _f_gas(mu_gas: np.ndarray) -> np.ndarray:
    """mu_gas -> f_gas = mu/(1+mu)"""
    return mu_gas / (1.0 + mu_gas)


def _compute_c0() -> float:
    """C0 such that S_hat(z=0) = 0."""
    z0 = np.array([0.0])
    rho = _rho_sfr_madau_dickinson(z0)
    fg = _f_gas(_mu_gas_tacconi_beta2(z0))
    return float(-(np.log10(np.clip(rho, 1e-30, None))
                    + np.log10(np.clip(fg, 1e-30, 1.0)))[0])


def _s_hat(z: np.ndarray, c0: float) -> np.ndarray:
    """S_hat(z) = log10(rho_SFR) + log10(f_gas) + C0"""
    rho = np.clip(_rho_sfr_madau_dickinson(z), 1e-30, None)
    fg = np.clip(_f_gas(_mu_gas_tacconi_beta2(z)), 1e-30, 1.0)
    return np.log10(rho) + np.log10(fg) + c0


# ─────────────────────────────────────────────────────────
# Locked grid parameters
# ─────────────────────────────────────────────────────────

Z_MIN = 0.001       # avoid z=0 singularity in derivative
Z_MAX = 3.0         # extends past all current data coverage
N_GRID = 10000      # 10k points for smooth derivative
SG_WINDOW = 101     # Savitzky-Golay window (odd, ~1% of grid)
SG_ORDER = 3        # polynomial order


def _savgol_smooth(y: np.ndarray, window: int, order: int) -> np.ndarray:
    """Savitzky-Golay filter (no scipy dependency — pure numpy)."""
    if window % 2 == 0:
        window += 1
    half = window // 2
    # Vandermonde matrix for polynomial fit
    x = np.arange(-half, half + 1, dtype=float)
    A = np.vander(x, N=order + 1, increasing=True)
    # Least-squares coefficients (only need zeroth = smoothed value)
    coeffs = np.linalg.pinv(A)
    c0 = coeffs[0]  # row for 0th derivative
    # Convolve
    result = np.convolve(y, c0[::-1], mode='same')
    # Fix edges: use unsmoothed
    result[:half] = y[:half]
    result[-half:] = y[-half:]
    return result


def compute_chi_table() -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """
    Compute the deterministic chi(z) table.

    Returns:
        z_grid:  (N,) redshift values
        s_hat:   (N,) S_hat(z) values
        chi:     (N,) |dS_hat/dz| values (smoothed)
        chi_c:   scalar — median(chi) over [0.2, 2.4]
    """
    c0 = _compute_c0()

    z_grid = np.linspace(Z_MIN, Z_MAX, N_GRID)
    s_vals = _s_hat(z_grid, c0)

    # Numerical derivative: dS/dz
    dz = z_grid[1] - z_grid[0]
    ds_dz_raw = np.gradient(s_vals, dz)

    # Smooth with Savitzky-Golay to remove numerical noise
    ds_dz_smooth = _savgol_smooth(ds_dz_raw, SG_WINDOW, SG_ORDER)

    # chi = |dS_hat/dz|
    chi = np.abs(ds_dz_smooth)

    # chi_c = median(chi) over z in [0.2, 2.4]
    # This is the "midpoint" definition — deterministic, no free parameters
    mask = (z_grid >= 0.2) & (z_grid <= 2.4)
    chi_c = float(np.median(chi[mask]))

    return z_grid, s_vals, chi, chi_c


# ─────────────────────────────────────────────────────────
# Module-level constants (computed once at import time)
# ─────────────────────────────────────────────────────────

_z_grid, _s_hat_vals, _chi_vals, CHI_C = compute_chi_table()


def get_chi_table() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (z_grid, s_hat, chi) arrays."""
    return _z_grid.copy(), _s_hat_vals.copy(), _chi_vals.copy()


def chi_at_z(z: np.ndarray) -> np.ndarray:
    """Interpolate chi(z) at arbitrary redshifts. Linear interpolation."""
    return np.interp(z, _z_grid, _chi_vals)


def s_hat_at_z(z: np.ndarray) -> np.ndarray:
    """Interpolate S_hat(z) at arbitrary redshifts."""
    return np.interp(z, _z_grid, _s_hat_vals)


# ─────────────────────────────────────────────────────────
# KT2 constants (frozen from Grid-AQUAL)
# ─────────────────────────────────────────────────────────

EPSILON_KT2 = 2.32**2 - 1.0   # = 4.3824 — from C=2.32


# ─────────────────────────────────────────────────────────
# CLI: generate CSV
# ─────────────────────────────────────────────────────────

def write_csv(outpath: str) -> None:
    """Write chi_of_z_axiom0.csv."""
    z, s, c = get_chi_table()
    with open(outpath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['z', 's_hat', 'chi'])
        for i in range(len(z)):
            writer.writerow([f'{z[i]:.8f}', f'{s[i]:.10f}', f'{c[i]:.10f}'])
    print(f"Wrote {outpath} ({len(z)} rows)")
    print(f"CHI_C (median over z=[0.2, 2.4]) = {CHI_C:.6f}")
    print(f"EPSILON_KT2 (C²-1, C=2.32) = {EPSILON_KT2:.4f}")


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    write_csv(os.path.join(here, 'chi_of_z_axiom0.csv'))
