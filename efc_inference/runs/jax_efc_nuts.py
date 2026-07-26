#!/usr/bin/env python3
"""
JAX/numpyro EFC NUTS Sampler — GPU-accelerated MCMC.

Reimplements the EFC 4-probe inference pipeline as pure JAX functions
for GPU-accelerated HMC/NUTS sampling via numpyro.

Key differences from emcee version:
    - All computations in JAX (jit-compilable, auto-differentiable)
    - Growth ODE via fixed-step RK4 (JAX-friendly, no scipy)
    - Comoving distances via JAX trapezoid
    - NUTS sampler (gradient-based) instead of ensemble (random walk)
    - Runs on GPU (RTX 5080: 55 TFLOPS measured)

Expected speedup: 10-50× vs emcee CPU for same effective samples.

Usage (GPU):
    python jax_efc_nuts.py

Usage (from emcee environment for comparison):
    from jax_efc_nuts import run_nuts_efc
    result = run_nuts_efc(num_warmup=500, num_samples=2000)
"""

import os
import sys
import time
from dataclasses import dataclass
from typing import Optional

import jax
# CRITICAL: float64 required for cosmological precision.
# float32 causes Hessian corruption (wrong signs) in H(z) integrals
# and SNIa covariance → NUTS step size collapse.
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS

# ═══════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════

C_KM_S = 299792.458       # speed of light km/s
RD_FIXED = 147.09          # Planck 2018 sound horizon (Mpc)

# EFC gate parameters (Variant A)
A_T = 0.5
DELTA_A = 0.1
G1 = 1.0 / (1.0 + jnp.exp(-(1.0 - A_T) / DELTA_A))  # gate at a=1

# Growth ODE settings
A_INI = 1e-3
N_ODE_STEPS = 50           # 50 RK4 steps suffice (smooth ODE, <0.1% error vs 500)

# ── A_GRID: scale factors at ALL likelihood data points ──────────
# Used for gate normalization (A_eff reparameterization).
# Unique z-values from all 4 probes (BAO, H(z), fσ8, SNIa), sorted.
# a = 1/(1+z), converting to scale factor.
_ALL_DATA_Z = jnp.array([
    # BAO (bao_starter.csv)
    0.15, 0.38, 0.51, 0.61, 0.70, 0.85, 1.48, 2.33,
    # H(z) (hz_cosmic_chronometers.csv)
    0.07, 0.12, 0.20, 0.28, 0.40, 0.48, 0.88, 1.30, 1.43,
    # fσ8 (fs8_extended.csv)
    0.02, 0.77,  # unique z not already above
    # SNIa (pantheon_binned.csv — 40 unique z, some overlap with above)
    0.014, 0.0194, 0.0264, 0.0329, 0.0396, 0.0475, 0.056, 0.064,
    0.0721, 0.0811, 0.0889, 0.1001, 0.1071, 0.1195, 0.1278, 0.1396,
    0.1519, 0.1635, 0.1778, 0.1906, 0.2067, 0.2216, 0.2405, 0.2558,
    0.2762, 0.2972, 0.3215, 0.3453, 0.3708, 0.4049, 0.4355, 0.4738,
    0.5174, 0.5742, 0.6299, 0.724, 0.821, 0.9511, 1.2336, 1.6123,
])
# Convert z → a and sort ascending (note: jnp.unique sorts)
A_GRID = jnp.sort(1.0 / (1.0 + _ALL_DATA_Z))  # ~60 points, a ∈ [0.30, 0.99]



# ═══════════════════════════════════════════════════════════════
#  DATA LOADING (numpy, done once on CPU)
# ═══════════════════════════════════════════════════════════════

@dataclass
class ProbeData:
    """Holds all observational data as JAX arrays (on device)."""
    # BAO
    bao_z: jnp.ndarray          # (N_bao,)
    bao_obs: jnp.ndarray        # (N_bao,) observed values
    bao_err: jnp.ndarray        # (N_bao,) 1-sigma errors
    bao_types: list             # ['DV_over_rd', 'DM_over_rd', ...]
    # Masks for BAO types (precomputed for JAX)
    bao_is_dh: jnp.ndarray     # (N_bao,) bool
    bao_is_dm: jnp.ndarray     # (N_bao,) bool
    bao_is_dv: jnp.ndarray     # (N_bao,) bool
    # Growth
    growth_z: jnp.ndarray       # (N_growth,)
    growth_obs: jnp.ndarray
    growth_err: jnp.ndarray
    # Hz
    hz_z: jnp.ndarray           # (N_hz,)
    hz_obs: jnp.ndarray
    hz_err: jnp.ndarray
    # SNIa
    snia_z: jnp.ndarray         # (N_snia,)
    snia_mb: jnp.ndarray        # apparent magnitudes
    snia_cov_inv: jnp.ndarray   # (N_snia, N_snia) inverse covariance
    snia_cov_logdet: float      # log determinant
    n_total: int
    # BAO covariance (None → diagonal, set → full covariance from e.g. DESI DR2)
    bao_cov_inv: jnp.ndarray = None    # (N_bao, N_bao) inverse covariance
    bao_cov_logdet: float = 0.0        # log|C| for normalization


def _load_bao_csv(path: str):
    """Load BAO data from CSV (z,observable,value,sigma)."""
    bao_z, bao_obs, bao_err, bao_types = [], [], [], []
    with open(path) as f:
        f.readline()  # skip header
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 4:
                continue
            bao_z.append(float(parts[0]))
            bao_types.append(parts[1].strip())
            bao_obs.append(float(parts[2]))
            bao_err.append(float(parts[3]))
    return bao_z, bao_obs, bao_err, bao_types, None  # no covariance


def _load_bao_json(path: str):
    """Load BAO data from JSON with optional covariance matrix.

    JSON format: {"measurements": [{"z_eff":, "observable":, "value":, "error":}, ...],
                  "covariance": [[...], ...]}
    """
    import json
    with open(path) as f:
        data = json.load(f)
    measurements = data["measurements"]
    bao_z = [m["z_eff"] for m in measurements]
    bao_obs = [m["value"] for m in measurements]
    bao_err = [m["error"] for m in measurements]
    bao_types = [m["observable"] for m in measurements]
    cov = np.array(data["covariance"]) if "covariance" in data else None
    return bao_z, bao_obs, bao_err, bao_types, cov


def load_data(
    bao_path: str = "efc_inference/data/bao/bao_starter.csv",
    growth_path: str = "efc_inference/data/growth/fs8_extended.csv",
    hz_path: str = "efc_inference/data/hubble/hz_cosmic_chronometers.csv",
    snia_path: str = "efc_inference/data/snia/pantheon_binned.csv",
    snia_cov_path: str = "efc_inference/data/snia/pantheon_binned_covtotal.npy",
) -> ProbeData:
    """Load all probe data from disk (CPU) and transfer to JAX arrays.

    BAO: auto-detects CSV vs JSON by extension. JSON may include covariance.
    """

    # ── BAO (CSV or JSON) ──
    if bao_path.endswith(".json"):
        bao_z, bao_obs, bao_err, bao_types, bao_cov = _load_bao_json(bao_path)
    else:
        bao_z, bao_obs, bao_err, bao_types, bao_cov = _load_bao_csv(bao_path)

    bao_is_dh = jnp.array([t == "DH_over_rd" for t in bao_types], dtype=jnp.float32)
    bao_is_dm = jnp.array([t == "DM_over_rd" for t in bao_types], dtype=jnp.float32)
    bao_is_dv = jnp.array([t == "DV_over_rd" for t in bao_types], dtype=jnp.float32)

    # BAO covariance → inverse + logdet (if provided)
    bao_cov_inv = None
    bao_cov_logdet = 0.0
    if bao_cov is not None:
        L_bao = np.linalg.cholesky(bao_cov)
        bao_cov_inv = jnp.array(np.linalg.solve(bao_cov, np.eye(bao_cov.shape[0])))
        bao_cov_logdet = float(2.0 * np.sum(np.log(np.diag(L_bao))))
        print(f"  BAO: {len(bao_z)} pts with FULL {len(bao_z)}×{len(bao_z)} covariance")
    else:
        print(f"  BAO: {len(bao_z)} pts with diagonal errors")

    # ── Growth ──
    # Use pandas to robustly handle '#'-prefixed DOI comment headers + column header
    import pandas as _pd
    growth_raw = _pd.read_csv(growth_path, comment="#").values

    # ── Hz ──
    hz_raw = _pd.read_csv(hz_path, comment="#").values

    # ── SNIa ──
    snia_raw = _pd.read_csv(snia_path, comment="#").values
    snia_cov = np.load(snia_cov_path)
    L = np.linalg.cholesky(snia_cov)
    cov_inv = np.linalg.solve(snia_cov, np.eye(snia_cov.shape[0]))
    cov_logdet = 2.0 * np.sum(np.log(np.diag(L)))

    n_total = len(bao_z) + len(growth_raw) + len(hz_raw) + len(snia_raw)

    return ProbeData(
        bao_z=jnp.array(bao_z),
        bao_obs=jnp.array(bao_obs),
        bao_err=jnp.array(bao_err),
        bao_types=bao_types,
        bao_is_dh=bao_is_dh,
        bao_is_dm=bao_is_dm,
        bao_is_dv=bao_is_dv,
        bao_cov_inv=bao_cov_inv,
        bao_cov_logdet=bao_cov_logdet,
        growth_z=jnp.array(growth_raw[:, 0]),
        growth_obs=jnp.array(growth_raw[:, 1]),
        growth_err=jnp.array(growth_raw[:, 2]),
        hz_z=jnp.array(hz_raw[:, 0]),
        hz_obs=jnp.array(hz_raw[:, 1]),
        hz_err=jnp.array(hz_raw[:, 2]),
        snia_z=jnp.array(snia_raw[:, 0]),
        snia_mb=jnp.array(snia_raw[:, 1]),
        snia_cov_inv=jnp.array(cov_inv),
        snia_cov_logdet=float(cov_logdet),
        n_total=n_total,
    )


# ═══════════════════════════════════════════════════════════════
#  EFC PHYSICS (pure JAX)
# ═══════════════════════════════════════════════════════════════

def gate(a):
    """Logistic gate: g(a) = 1 / (1 + exp(-(a - a_t) / delta_a))."""
    x = (a - A_T) / DELTA_A
    x = jnp.clip(x, -50.0, 50.0)
    return 1.0 / (1.0 + jnp.exp(-x))


def gate_deriv(a):
    """dg/da = g(a) * (1 - g(a)) / delta_a."""
    g = gate(a)
    return g * (1.0 - g) / DELTA_A


# ── Parameterized gate (N3: free a_t, delta_a) ──────────────────

def gate_param(a, a_t, delta_a):
    """Logistic gate with explicit parameters (for N3 gate freedom test)."""
    x = (a - a_t) / delta_a
    x = jnp.clip(x, -50.0, 50.0)
    return 1.0 / (1.0 + jnp.exp(-x))


def gate_deriv_param(a, a_t, delta_a):
    """dg/da with explicit parameters."""
    g = gate_param(a, a_t, delta_a)
    return g * (1.0 - g) / delta_a


# ── Power-law gate (N7: Lorentzian-derived from L0, n=2) ─────────
#
# g(a) = 1 / (1 + (a_t/a)^n)   with n = 2 locked from L0
# From W(k) = 1/(1+(k/k_Λ)²) via k*(a) ∝ a⁻¹
# Core Derivation Note v0.2, Eq. (6)-(8)

N7_N_POWER = 2   # Locked by Lorentzian W(k) in L0

# Pre-compute power-law gate at a=1 for normalization
G1_PL = 1.0 / (1.0 + (A_T / 1.0) ** N7_N_POWER)


def gate_powerlaw(a):
    """Power-law gate (fixed a_t): g(a) = 1 / (1 + (a_t/a)^n), n=2."""
    a_safe = jnp.maximum(a, 1e-10)
    return 1.0 / (1.0 + (A_T / a_safe) ** N7_N_POWER)


def gate_deriv_powerlaw(a):
    """dg/da for power-law gate: n · (a_t/a)^n · g² / a."""
    a_safe = jnp.maximum(a, 1e-10)
    r = A_T / a_safe
    g = 1.0 / (1.0 + r ** N7_N_POWER)
    return N7_N_POWER * r ** N7_N_POWER * g ** 2.0 / a_safe


# ── A_eff gate normalization (breaks α × gate degeneracy) ──────────
#
# Key idea: G = mean(gate(a_i)) over data points.
# A_eff = α · G is the "effective amplitude seen by data".
# g̃(a) = gate(a) / G is a shape function with unit data-average.
# Model uses: A_eff · [g̃(a) − g̃(1)] instead of α · [g(a) − g(1)].
#
# This decouples amplitude from shape: when gate params change,
# G absorbs the scale change, leaving A_eff stable.

def gate_mass(a_t, delta_a):
    """G = mean of gate over all data points (gate normalization constant).

    Returns scalar >= eps.  A_GRID is a module constant (not sampled).
    """
    g = gate_param(A_GRID, a_t, delta_a)
    return jnp.maximum(jnp.mean(g), 1e-8)


def gate_norm(a, a_t, delta_a):
    """Normalized gate: g̃(a) = gate(a) / G.

    g̃ has unit data-average by construction.
    """
    G = gate_mass(a_t, delta_a)
    return gate_param(a, a_t, delta_a) / G


def e_squared_aeff(a, Om, A_eff, a_t, delta_a):
    """E²(a) with A_eff reparameterization (breaks α×gate degeneracy).

    E²(a) = Ωm·a⁻³ + (1−Ωm) + A_eff·[g̃(a) − g̃(1)]

    where g̃(a) = gate(a)/G is the normalized gate.
    A_eff is the identifiable "effective amplitude at data coverage".
    """
    OL = 1.0 - Om
    gn_a = gate_norm(a, a_t, delta_a)
    gn_1 = gate_norm(1.0, a_t, delta_a)
    return Om * a**(-3.0) + OL + A_eff * (gn_a - gn_1)


def de_squared_da_aeff(a, Om, A_eff, a_t, delta_a):
    """d(E²)/da with A_eff reparameterization."""
    G = gate_mass(a_t, delta_a)
    # d(g̃)/da = (dg/da) / G
    dgn_da = gate_deriv_param(a, a_t, delta_a) / G
    return -3.0 * Om * a**(-4.0) + A_eff * dgn_da


def Hz_aeff(z, H0, Om, A_eff, a_t, delta_a):
    """H(z) with A_eff reparameterization."""
    a = 1.0 / (1.0 + z)
    E2 = e_squared_aeff(a, Om, A_eff, a_t, delta_a)
    return H0 * jnp.sqrt(jnp.maximum(E2, 1e-30))


def e_squared_n3(a, Om, alpha, a_t, delta_a):
    """E²(a) with free gate parameters."""
    OL = 1.0 - Om
    g_a = gate_param(a, a_t, delta_a)
    g_1 = gate_param(1.0, a_t, delta_a)
    return Om * a**(-3.0) + OL + alpha * (g_a - g_1)


def de_squared_da_n3(a, Om, alpha, a_t, delta_a):
    """d(E²)/da with free gate parameters."""
    return -3.0 * Om * a**(-4.0) + alpha * gate_deriv_param(a, a_t, delta_a)


def Hz_n3(z, H0, Om, alpha, a_t, delta_a):
    """H(z) with free gate parameters."""
    a = 1.0 / (1.0 + z)
    E2 = e_squared_n3(a, Om, alpha, a_t, delta_a)
    return H0 * jnp.sqrt(jnp.maximum(E2, 1e-30))


def e_squared(a, Om, alpha):
    """E²(a) = Ωm·a⁻³ + (1−Ωm) + α·[g(a) − g(1)]."""
    OL = 1.0 - Om
    return Om * a**(-3.0) + OL + alpha * (gate(a) - G1)


def e_squared_lcdm(a, Om):
    """E²(a) = Ωm·a⁻³ + (1−Ωm) for flat ΛCDM."""
    return Om * a**(-3.0) + (1.0 - Om)


def de_squared_da(a, Om, alpha):
    """d(E²)/da for EFC."""
    return -3.0 * Om * a**(-4.0) + alpha * gate_deriv(a)


def Hz(z, H0, Om, alpha):
    """H(z) = H0 * E(z)."""
    a = 1.0 / (1.0 + z)
    E2 = e_squared(a, Om, alpha)
    return H0 * jnp.sqrt(jnp.maximum(E2, 1e-30))


def Hz_lcdm(z, H0, Om):
    """H(z) for LCDM."""
    a = 1.0 / (1.0 + z)
    E2 = e_squared_lcdm(a, Om)
    return H0 * jnp.sqrt(jnp.maximum(E2, 1e-30))


# ── N7: Power-law gate physics (Lorentzian-derived, n=2) ─────────

def e_squared_n7(a, Om, alpha):
    """E²(a) with power-law gate: g(a) = 1/(1+(a_t/a)²)."""
    OL = 1.0 - Om
    return Om * a**(-3.0) + OL + alpha * (gate_powerlaw(a) - G1_PL)


def de_squared_da_n7(a, Om, alpha):
    """d(E²)/da for N7 power-law gate."""
    return -3.0 * Om * a**(-4.0) + alpha * gate_deriv_powerlaw(a)


def Hz_n7(z, H0, Om, alpha):
    """H(z) with power-law gate."""
    a = 1.0 / (1.0 + z)
    E2 = e_squared_n7(a, Om, alpha)
    return H0 * jnp.sqrt(jnp.maximum(E2, 1e-30))


# ═══════════════════════════════════════════════════════════════
#  COMOVING DISTANCE (shared grid, cumulative trapezoid)
# ═══════════════════════════════════════════════════════════════

# Pre-compute a SHARED z-grid covering all data (max z ~ 2.33, pad to 2.5)
N_SHARED_GRID = 201
Z_MAX_GRID = 2.5
Z_SHARED = jnp.linspace(0.0, Z_MAX_GRID, N_SHARED_GRID)
DZ = Z_MAX_GRID / (N_SHARED_GRID - 1)


def _cumulative_comoving(H0, Om, alpha):
    """Compute cumulative DM(z) on shared grid — ONE H(z) evaluation.

    Key optimization: instead of 54 separate integrals (one per data point),
    compute ONE set of H(z) values and ONE cumulative sum.
    Reduces gradient graph from ~5000 nodes to ~200.
    """
    Hz_grid = Hz(Z_SHARED, H0, Om, alpha)
    integrand = C_KM_S / Hz_grid
    pair_avg = 0.5 * (integrand[:-1] + integrand[1:])
    cum_dm = jnp.concatenate([jnp.array([0.0]), jnp.cumsum(pair_avg * DZ)])
    return cum_dm


def _cumulative_comoving_lcdm(H0, Om):
    """Cumulative DM for LCDM."""
    Hz_grid = Hz_lcdm(Z_SHARED, H0, Om)
    integrand = C_KM_S / Hz_grid
    pair_avg = 0.5 * (integrand[:-1] + integrand[1:])
    cum_dm = jnp.concatenate([jnp.array([0.0]), jnp.cumsum(pair_avg * DZ)])
    return cum_dm


def comoving_at_z(z_pts, H0, Om, alpha):
    """Get DM at specific z values via interpolation on shared grid."""
    cum_dm = _cumulative_comoving(H0, Om, alpha)
    return jnp.interp(z_pts, Z_SHARED, cum_dm)


def comoving_at_z_lcdm(z_pts, H0, Om):
    """Get DM for LCDM at specific z values."""
    cum_dm = _cumulative_comoving_lcdm(H0, Om)
    return jnp.interp(z_pts, Z_SHARED, cum_dm)


# ═══════════════════════════════════════════════════════════════
#  GROWTH ODE (fixed-step RK4 in JAX)
# ═══════════════════════════════════════════════════════════════

def _growth_rhs(a, D, Dp, Om, alpha):
    """RHS of growth ODE: D'' = -friction*D' + source*D."""
    E2 = e_squared(a, Om, alpha)
    E_a = jnp.sqrt(jnp.maximum(E2, 1e-30))
    dE2_da = de_squared_da(a, Om, alpha)
    dE_da = dE2_da / (2.0 * E_a)

    friction = 3.0 / a + dE_da / E_a
    source = 1.5 * Om / (a**5.0 * E2)

    return Dp, -friction * Dp + source * D


def _solve_growth_raw(Om, alpha, a_eval):
    """Raw growth ODE solver (forward only, no custom gradients).

    Uses fixed-step RK4 via jax.lax.scan.
    """
    a_grid = jnp.linspace(A_INI, 1.0, N_ODE_STEPS + 1)
    h = (1.0 - A_INI) / N_ODE_STEPS

    D0 = A_INI
    Dp0 = 1.0

    def rk4_step(state, a):
        D, Dp = state
        k1_D, k1_Dp = _growth_rhs(a, D, Dp, Om, alpha)
        k2_D, k2_Dp = _growth_rhs(a + h/2, D + h/2*k1_D, Dp + h/2*k1_Dp, Om, alpha)
        k3_D, k3_Dp = _growth_rhs(a + h/2, D + h/2*k2_D, Dp + h/2*k2_Dp, Om, alpha)
        k4_D, k4_Dp = _growth_rhs(a + h, D + h*k3_D, Dp + h*k3_Dp, Om, alpha)
        D_new = D + (h/6) * (k1_D + 2*k2_D + 2*k3_D + k4_D)
        Dp_new = Dp + (h/6) * (k1_Dp + 2*k2_Dp + 2*k3_Dp + k4_Dp)
        return (D_new, Dp_new), (D_new, Dp_new)

    _, (D_all, Dp_all) = jax.lax.scan(rk4_step, (D0, Dp0), a_grid[:-1])

    D_full = jnp.concatenate([jnp.array([D0]), D_all])
    Dp_full = jnp.concatenate([jnp.array([Dp0]), Dp_all])

    D_vals = jnp.interp(a_eval, a_grid, D_full)
    Dp_vals = jnp.interp(a_eval, a_grid, Dp_full)
    D_at_1 = D_full[-1]

    return D_vals, Dp_vals, D_at_1


@jax.custom_vjp
def solve_growth_rk4(Om, alpha, a_eval):
    """Solve growth ODE with custom VJP for stable NUTS gradients.

    Forward: standard RK4 ODE integration.
    Backward: finite-difference gradients (avoids autodiff through 50 scan steps).

    This is the key fix for NUTS step size collapse — autodiff through
    sequential scan creates ill-conditioned Jacobians, but the actual
    parameter sensitivities dD/dOm and dD/dalpha are smooth and simple.
    """
    return _solve_growth_raw(Om, alpha, a_eval)


def _solve_growth_fwd(Om, alpha, a_eval):
    """Forward pass: compute and save residuals for backward."""
    result = _solve_growth_raw(Om, alpha, a_eval)
    return result, (Om, alpha, a_eval, result)


def _solve_growth_bwd(res, g):
    """Backward pass: finite-difference gradients (numerically stable).

    dD/dOm ≈ [D(Om+eps) - D(Om-eps)] / (2*eps)
    dD/dalpha ≈ [D(alpha+eps) - D(alpha-eps)] / (2*eps)
    """
    Om, alpha, a_eval, (D_vals, Dp_vals, D_at_1) = res
    g_D, g_Dp, g_D1 = g

    eps_Om = 1e-5
    eps_alpha = 1e-5

    # Gradient w.r.t. Om
    D_p, Dp_p, D1_p = _solve_growth_raw(Om + eps_Om, alpha, a_eval)
    D_m, Dp_m, D1_m = _solve_growth_raw(Om - eps_Om, alpha, a_eval)
    dD_dOm = (D_p - D_m) / (2 * eps_Om)
    dDp_dOm = (Dp_p - Dp_m) / (2 * eps_Om)
    dD1_dOm = (D1_p - D1_m) / (2 * eps_Om)
    grad_Om = jnp.sum(g_D * dD_dOm) + jnp.sum(g_Dp * dDp_dOm) + g_D1 * dD1_dOm

    # Gradient w.r.t. alpha
    D_p, Dp_p, D1_p = _solve_growth_raw(Om, alpha + eps_alpha, a_eval)
    D_m, Dp_m, D1_m = _solve_growth_raw(Om, alpha - eps_alpha, a_eval)
    dD_dalpha = (D_p - D_m) / (2 * eps_alpha)
    dDp_dalpha = (Dp_p - Dp_m) / (2 * eps_alpha)
    dD1_dalpha = (D1_p - D1_m) / (2 * eps_alpha)
    grad_alpha = jnp.sum(g_D * dD_dalpha) + jnp.sum(g_Dp * dDp_dalpha) + g_D1 * dD1_dalpha

    # No gradient w.r.t. a_eval (evaluation points are fixed data)
    grad_a_eval = jnp.zeros_like(a_eval)

    return grad_Om, grad_alpha, grad_a_eval


solve_growth_rk4.defvjp(_solve_growth_fwd, _solve_growth_bwd)


def compute_fs8(z, Om, H0, s8, alpha):
    """Compute f*sigma8(z) for EFC.

    f(a) = a * D'(a) / D(a)
    sigma8(z) = s8 * D(z) / D(0)
    fs8(z) = f(z) * sigma8(z)
    """
    a_eval = 1.0 / (1.0 + z)
    D_vals, Dp_vals, D_at_1 = solve_growth_rk4(Om, alpha, a_eval)

    f = a_eval * Dp_vals / jnp.maximum(D_vals, 1e-30)
    sigma8_z = s8 * D_vals / jnp.maximum(D_at_1, 1e-30)
    return f * sigma8_z


# ── N3: Growth ODE + fs8 with parameterized gate ─────────────

def _growth_rhs_n3(a, D, Dp, Om, alpha, a_t, delta_a):
    """RHS of growth ODE with parameterized gate."""
    E2 = e_squared_n3(a, Om, alpha, a_t, delta_a)
    E_a = jnp.sqrt(jnp.maximum(E2, 1e-30))
    dE2_da = de_squared_da_n3(a, Om, alpha, a_t, delta_a)
    dE_da = dE2_da / (2.0 * E_a)
    friction = 3.0 / a + dE_da / E_a
    source = 1.5 * Om / (a**5.0 * E2)
    return Dp, -friction * Dp + source * D


def _solve_growth_raw_n3(Om, alpha, a_t, delta_a, a_eval):
    """Raw growth ODE solver with parameterized gate (no custom gradients)."""
    a_grid = jnp.linspace(A_INI, 1.0, N_ODE_STEPS + 1)
    h = (1.0 - A_INI) / N_ODE_STEPS
    D0 = A_INI
    Dp0 = 1.0

    def rk4_step(state, a):
        D, Dp = state
        k1_D, k1_Dp = _growth_rhs_n3(a, D, Dp, Om, alpha, a_t, delta_a)
        k2_D, k2_Dp = _growth_rhs_n3(a + h/2, D + h/2*k1_D, Dp + h/2*k1_Dp, Om, alpha, a_t, delta_a)
        k3_D, k3_Dp = _growth_rhs_n3(a + h/2, D + h/2*k2_D, Dp + h/2*k2_Dp, Om, alpha, a_t, delta_a)
        k4_D, k4_Dp = _growth_rhs_n3(a + h, D + h*k3_D, Dp + h*k3_Dp, Om, alpha, a_t, delta_a)
        D_new = D + (h/6) * (k1_D + 2*k2_D + 2*k3_D + k4_D)
        Dp_new = Dp + (h/6) * (k1_Dp + 2*k2_Dp + 2*k3_Dp + k4_Dp)
        return (D_new, Dp_new), (D_new, Dp_new)

    _, (D_all, Dp_all) = jax.lax.scan(rk4_step, (D0, Dp0), a_grid[:-1])
    D_full = jnp.concatenate([jnp.array([D0]), D_all])
    Dp_full = jnp.concatenate([jnp.array([Dp0]), Dp_all])
    D_vals = jnp.interp(a_eval, a_grid, D_full)
    Dp_vals = jnp.interp(a_eval, a_grid, Dp_full)
    D_at_1 = D_full[-1]
    return D_vals, Dp_vals, D_at_1


@jax.custom_vjp
def solve_growth_rk4_n3(Om, alpha, a_t, delta_a, a_eval):
    """Growth ODE with custom VJP for 4 parameters (Om, alpha, a_t, delta_a)."""
    return _solve_growth_raw_n3(Om, alpha, a_t, delta_a, a_eval)


def _solve_growth_fwd_n3(Om, alpha, a_t, delta_a, a_eval):
    result = _solve_growth_raw_n3(Om, alpha, a_t, delta_a, a_eval)
    return result, (Om, alpha, a_t, delta_a, a_eval, result)


def _solve_growth_bwd_n3(res, g):
    """Finite-difference gradients for Om, alpha, a_t, delta_a."""
    Om, alpha, a_t, delta_a, a_eval, (D_vals, Dp_vals, D_at_1) = res
    g_D, g_Dp, g_D1 = g

    eps = 1e-5

    def _grad_for_param(param_idx, eps_val):
        """Compute gradient via finite differences for param_idx."""
        args = [Om, alpha, a_t, delta_a]
        args_p = list(args); args_p[param_idx] = args_p[param_idx] + eps_val
        args_m = list(args); args_m[param_idx] = args_m[param_idx] - eps_val
        D_p, Dp_p, D1_p = _solve_growth_raw_n3(*args_p, a_eval)
        D_m, Dp_m, D1_m = _solve_growth_raw_n3(*args_m, a_eval)
        dD = (D_p - D_m) / (2 * eps_val)
        dDp = (Dp_p - Dp_m) / (2 * eps_val)
        dD1 = (D1_p - D1_m) / (2 * eps_val)
        return jnp.sum(g_D * dD) + jnp.sum(g_Dp * dDp) + g_D1 * dD1

    grad_Om = _grad_for_param(0, eps)
    grad_alpha = _grad_for_param(1, eps)
    grad_a_t = _grad_for_param(2, eps)
    grad_delta_a = _grad_for_param(3, eps)
    grad_a_eval = jnp.zeros_like(a_eval)

    return grad_Om, grad_alpha, grad_a_t, grad_delta_a, grad_a_eval


solve_growth_rk4_n3.defvjp(_solve_growth_fwd_n3, _solve_growth_bwd_n3)


def compute_fs8_n3(z, Om, H0, s8, alpha, a_t, delta_a):
    """f*sigma8(z) with parameterized gate."""
    a_eval = 1.0 / (1.0 + z)
    D_vals, Dp_vals, D_at_1 = solve_growth_rk4_n3(Om, alpha, a_t, delta_a, a_eval)
    f = a_eval * Dp_vals / jnp.maximum(D_vals, 1e-30)
    sigma8_z = s8 * D_vals / jnp.maximum(D_at_1, 1e-30)
    return f * sigma8_z


def _cumulative_comoving_n3(H0, Om, alpha, a_t, delta_a):
    """Cumulative DM(z) on shared grid with parameterized gate."""
    Hz_grid = Hz_n3(Z_SHARED, H0, Om, alpha, a_t, delta_a)
    integrand = C_KM_S / Hz_grid
    pair_avg = 0.5 * (integrand[:-1] + integrand[1:])
    cum_dm = jnp.concatenate([jnp.array([0.0]), jnp.cumsum(pair_avg * DZ)])
    return cum_dm


def comoving_at_z_n3(z_pts, H0, Om, alpha, a_t, delta_a):
    """DM at specific z with parameterized gate."""
    cum_dm = _cumulative_comoving_n3(H0, Om, alpha, a_t, delta_a)
    return jnp.interp(z_pts, Z_SHARED, cum_dm)


def predict_bao_n3(z_arr, H0, Om, alpha, r_d, a_t, delta_a, is_dh, is_dm, is_dv):
    """BAO predictions with parameterized gate."""
    Hz_vals = Hz_n3(z_arr, H0, Om, alpha, a_t, delta_a)
    dh_pred = C_KM_S / (Hz_vals * r_d)
    dm_mpc = comoving_at_z_n3(z_arr, H0, Om, alpha, a_t, delta_a)
    dm_pred = dm_mpc / r_d
    dh_mpc = C_KM_S / Hz_vals
    dv_pred = (z_arr * dh_mpc * dm_mpc**2)**(1.0/3.0) / r_d
    return is_dh * dh_pred + is_dm * dm_pred + is_dv * dv_pred


def predict_mu_th_n3(z_arr, H0, Om, alpha, a_t, delta_a):
    """Distance modulus with parameterized gate."""
    DM = comoving_at_z_n3(z_arr, H0, Om, alpha, a_t, delta_a)
    dL = (1.0 + z_arr) * DM
    return 5.0 * jnp.log10(jnp.maximum(dL, 1e-30)) + 25.0


# ═══════════════════════════════════════════════════════════════
#  A_eff PHYSICS — amplitude-normalized gate (N3 identifiability fix)
# ═══════════════════════════════════════════════════════════════
#
# Replaces α with A_eff = α·G in the N3 free-gate test.
# Uses g̃(a) = gate(a)/G so that model = A_eff · [g̃(a) − g̃(1)].
# Growth ODE, comoving distance, BAO, SNIa all use A_eff.

def _growth_rhs_aeff(a, D, Dp, Om, A_eff, a_t, delta_a):
    """RHS of growth ODE with A_eff reparameterization."""
    E2 = e_squared_aeff(a, Om, A_eff, a_t, delta_a)
    E_a = jnp.sqrt(jnp.maximum(E2, 1e-30))
    dE2_da = de_squared_da_aeff(a, Om, A_eff, a_t, delta_a)
    dE_da = dE2_da / (2.0 * E_a)
    friction = 3.0 / a + dE_da / E_a
    source = 1.5 * Om / (a**5.0 * E2)
    return Dp, -friction * Dp + source * D


def _solve_growth_raw_aeff(Om, A_eff, a_t, delta_a, a_eval):
    """Raw growth ODE solver with A_eff reparameterization."""
    a_grid = jnp.linspace(A_INI, 1.0, N_ODE_STEPS + 1)
    h = (1.0 - A_INI) / N_ODE_STEPS
    D0 = A_INI
    Dp0 = 1.0

    def rk4_step(state, a):
        D, Dp = state
        k1_D, k1_Dp = _growth_rhs_aeff(a, D, Dp, Om, A_eff, a_t, delta_a)
        k2_D, k2_Dp = _growth_rhs_aeff(a + h/2, D + h/2*k1_D, Dp + h/2*k1_Dp, Om, A_eff, a_t, delta_a)
        k3_D, k3_Dp = _growth_rhs_aeff(a + h/2, D + h/2*k2_D, Dp + h/2*k2_Dp, Om, A_eff, a_t, delta_a)
        k4_D, k4_Dp = _growth_rhs_aeff(a + h, D + h*k3_D, Dp + h*k3_Dp, Om, A_eff, a_t, delta_a)
        D_new = D + (h/6) * (k1_D + 2*k2_D + 2*k3_D + k4_D)
        Dp_new = Dp + (h/6) * (k1_Dp + 2*k2_Dp + 2*k3_Dp + k4_Dp)
        return (D_new, Dp_new), (D_new, Dp_new)

    _, (D_all, Dp_all) = jax.lax.scan(rk4_step, (D0, Dp0), a_grid[:-1])
    D_full = jnp.concatenate([jnp.array([D0]), D_all])
    Dp_full = jnp.concatenate([jnp.array([Dp0]), Dp_all])
    D_vals = jnp.interp(a_eval, a_grid, D_full)
    Dp_vals = jnp.interp(a_eval, a_grid, Dp_full)
    D_at_1 = D_full[-1]
    return D_vals, Dp_vals, D_at_1


@jax.custom_vjp
def solve_growth_rk4_aeff(Om, A_eff, a_t, delta_a, a_eval):
    """Growth ODE with A_eff + custom VJP (4 params: Om, A_eff, a_t, delta_a)."""
    return _solve_growth_raw_aeff(Om, A_eff, a_t, delta_a, a_eval)


def _solve_growth_fwd_aeff(Om, A_eff, a_t, delta_a, a_eval):
    result = _solve_growth_raw_aeff(Om, A_eff, a_t, delta_a, a_eval)
    return result, (Om, A_eff, a_t, delta_a, a_eval, result)


def _solve_growth_bwd_aeff(res, g):
    """Finite-difference gradients for Om, A_eff, a_t, delta_a."""
    Om, A_eff, a_t, delta_a, a_eval, (D_vals, Dp_vals, D_at_1) = res
    g_D, g_Dp, g_D1 = g
    eps = 1e-5

    def _grad_for_param(param_idx, eps_val):
        args = [Om, A_eff, a_t, delta_a]
        args_p = list(args); args_p[param_idx] = args_p[param_idx] + eps_val
        args_m = list(args); args_m[param_idx] = args_m[param_idx] - eps_val
        D_p, Dp_p, D1_p = _solve_growth_raw_aeff(*args_p, a_eval)
        D_m, Dp_m, D1_m = _solve_growth_raw_aeff(*args_m, a_eval)
        dD = (D_p - D_m) / (2 * eps_val)
        dDp = (Dp_p - Dp_m) / (2 * eps_val)
        dD1 = (D1_p - D1_m) / (2 * eps_val)
        return jnp.sum(g_D * dD) + jnp.sum(g_Dp * dDp) + g_D1 * dD1

    grad_Om = _grad_for_param(0, eps)
    grad_Aeff = _grad_for_param(1, eps)
    grad_a_t = _grad_for_param(2, eps)
    grad_delta_a = _grad_for_param(3, eps)
    grad_a_eval = jnp.zeros_like(a_eval)
    return grad_Om, grad_Aeff, grad_a_t, grad_delta_a, grad_a_eval


solve_growth_rk4_aeff.defvjp(_solve_growth_fwd_aeff, _solve_growth_bwd_aeff)


def compute_fs8_aeff(z, Om, H0, s8, A_eff, a_t, delta_a):
    """f*sigma8(z) with A_eff reparameterization."""
    a_eval = 1.0 / (1.0 + z)
    D_vals, Dp_vals, D_at_1 = solve_growth_rk4_aeff(Om, A_eff, a_t, delta_a, a_eval)
    f = a_eval * Dp_vals / jnp.maximum(D_vals, 1e-30)
    sigma8_z = s8 * D_vals / jnp.maximum(D_at_1, 1e-30)
    return f * sigma8_z


def _cumulative_comoving_aeff(H0, Om, A_eff, a_t, delta_a):
    """Cumulative DM(z) on shared grid with A_eff reparameterization."""
    Hz_grid = Hz_aeff(Z_SHARED, H0, Om, A_eff, a_t, delta_a)
    integrand = C_KM_S / Hz_grid
    pair_avg = 0.5 * (integrand[:-1] + integrand[1:])
    cum_dm = jnp.concatenate([jnp.array([0.0]), jnp.cumsum(pair_avg * DZ)])
    return cum_dm


def comoving_at_z_aeff(z_pts, H0, Om, A_eff, a_t, delta_a):
    """DM at specific z with A_eff reparameterization."""
    cum_dm = _cumulative_comoving_aeff(H0, Om, A_eff, a_t, delta_a)
    return jnp.interp(z_pts, Z_SHARED, cum_dm)


def predict_bao_aeff(z_arr, H0, Om, A_eff, r_d, a_t, delta_a, is_dh, is_dm, is_dv):
    """BAO predictions with A_eff reparameterization."""
    Hz_vals = Hz_aeff(z_arr, H0, Om, A_eff, a_t, delta_a)
    dh_pred = C_KM_S / (Hz_vals * r_d)
    dm_mpc = comoving_at_z_aeff(z_arr, H0, Om, A_eff, a_t, delta_a)
    dm_pred = dm_mpc / r_d
    dh_mpc = C_KM_S / Hz_vals
    dv_pred = (z_arr * dh_mpc * dm_mpc**2)**(1.0/3.0) / r_d
    return is_dh * dh_pred + is_dm * dm_pred + is_dv * dv_pred


def predict_mu_th_aeff(z_arr, H0, Om, A_eff, a_t, delta_a):
    """Distance modulus with A_eff reparameterization."""
    DM = comoving_at_z_aeff(z_arr, H0, Om, A_eff, a_t, delta_a)
    dL = (1.0 + z_arr) * DM
    return 5.0 * jnp.log10(jnp.maximum(dL, 1e-30)) + 25.0


# ═══════════════════════════════════════════════════════════════
#  BAO PREDICTIONS (vectorized per type)
# ═══════════════════════════════════════════════════════════════

def predict_bao(z_arr, H0, Om, alpha, r_d, is_dh, is_dm, is_dv):
    """Compute BAO predictions for all data points.

    Uses shared cumulative comoving distance grid (one H(z) eval).
    """
    # DH/rd = c / (H(z) * r_d)
    Hz_vals = Hz(z_arr, H0, Om, alpha)
    dh_pred = C_KM_S / (Hz_vals * r_d)

    # DM/rd via shared grid interpolation (NOT per-point vmap)
    dm_mpc = comoving_at_z(z_arr, H0, Om, alpha)
    dm_pred = dm_mpc / r_d

    # DV/rd = (z * DH * DM^2)^(1/3) / r_d
    dh_mpc = C_KM_S / Hz_vals  # DH in Mpc
    dv_pred = (z_arr * dh_mpc * dm_mpc**2)**(1.0/3.0) / r_d

    # Select prediction based on type
    pred = is_dh * dh_pred + is_dm * dm_pred + is_dv * dv_pred
    return pred


# ═══════════════════════════════════════════════════════════════
#  SNIa LIKELIHOOD (M_B marginalized)
# ═══════════════════════════════════════════════════════════════

def predict_mu_th(z_arr, H0, Om, alpha):
    """Compute distance modulus mu_th(z) = 5*log10(dL) + 25.

    dL = (1+z) * DM(z)
    """
    DM = comoving_at_z(z_arr, H0, Om, alpha)
    dL = (1.0 + z_arr) * DM
    mu_th = 5.0 * jnp.log10(jnp.maximum(dL, 1e-30)) + 25.0
    return mu_th


def snia_log_likelihood(mu_th, mb, cov_inv, cov_logdet):
    """SNIa log-likelihood with M_B analytically marginalized.

    Conley et al. (2011):
        ln L = -0.5 * [chi2 - B²/D + ln(D/(2π))]
    """
    delta = mb - mu_th  # residuals before M_B
    Cinv_delta = cov_inv @ delta
    chi2 = delta @ Cinv_delta

    ones = jnp.ones_like(delta)
    B = ones @ Cinv_delta
    D = ones @ (cov_inv @ ones)

    log_like = -0.5 * (chi2 - B**2 / D + jnp.log(D / (2 * jnp.pi)))
    log_like -= 0.5 * cov_logdet
    return log_like


# ═══════════════════════════════════════════════════════════════
#  CHI2 LOG-LIKELIHOOD
# ═══════════════════════════════════════════════════════════════

def chi2_log_likelihood(obs, pred, err):
    """Standard chi2 log-likelihood (diagonal covariance)."""
    residuals = obs - pred
    chi2 = jnp.sum((residuals / err)**2)
    log_det = jnp.sum(jnp.log(2 * jnp.pi * err**2))
    return -0.5 * (chi2 + log_det)


def bao_log_likelihood(data: ProbeData, bao_pred):
    """BAO log-likelihood: full covariance if available, else diagonal.

    Automatically selects based on data.bao_cov_inv:
      - If set (e.g. DESI DR2): -0.5 * (Δ^T C^{-1} Δ + log|C|)
      - If None (CSV diagonal):  chi2_log_likelihood(obs, pred, err)
    """
    if data.bao_cov_inv is not None:
        delta = data.bao_obs - bao_pred
        chi2 = delta @ data.bao_cov_inv @ delta
        return -0.5 * (chi2 + data.bao_cov_logdet)
    return chi2_log_likelihood(data.bao_obs, bao_pred, data.bao_err)


# ═══════════════════════════════════════════════════════════════
#  NUMPYRO MODEL
# ═══════════════════════════════════════════════════════════════

def efc_model(data: ProbeData):
    """Numpyro probabilistic model for 4-probe EFC inference.

    Reparametrized for NUTS: sample in standardized (z-score) space
    where all parameters have ~N(0,1) scale. This prevents step size
    collapse from scale mismatch (H0~67 vs alpha~-0.8).

    Physical parameters:
        Om    = 0.30 + 0.05 * z_Om        [~N(0.30, 0.05)]
        H0    = 67.5 + 5.0 * z_H0         [~N(67.5, 5.0)]
        s8    = 0.80 + 0.04 * z_s8         [~N(0.80, 0.04)]  D3: honest prior
        alpha = 0.0 + 3.0 * z_alpha        [~N(0.0, 3.0)]
    """
    # Sample in standardized space (all ~N(0,1))
    z_Om = numpyro.sample("z_Om", dist.Normal(0.0, 1.0))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0.0, 1.0))
    z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))
    z_alpha = numpyro.sample("z_alpha", dist.Normal(0.0, 1.0))

    # Transform to physical parameters
    Om = 0.30 + 0.05 * z_Om
    H0 = 67.5 + 5.0 * z_H0
    s8 = 0.80 + 0.04 * z_s8    # D3: honest prior (was 0.81 + 0.02)
    alpha = 0.0 + 3.0 * z_alpha

    # Soft bounds (penalty for unphysical values)
    numpyro.factor("Om_bound", -1e6 * jnp.where((Om < 0.05) | (Om > 0.8), 1.0, 0.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 < 40.0) | (H0 > 100.0), 1.0, 0.0))

    r_d = RD_FIXED

    # ── BAO ──
    bao_pred = predict_bao(
        data.bao_z, H0, Om, alpha, r_d,
        data.bao_is_dh, data.bao_is_dm, data.bao_is_dv,
    )
    ll_bao = bao_log_likelihood(data, bao_pred)

    # ── Hz ──
    hz_pred = Hz(data.hz_z, H0, Om, alpha)
    ll_hz = chi2_log_likelihood(data.hz_obs, hz_pred, data.hz_err)

    # ── Growth ──
    fs8_pred = compute_fs8(data.growth_z, Om, H0, s8, alpha)
    ll_growth = chi2_log_likelihood(data.growth_obs, fs8_pred, data.growth_err)

    # ── SNIa ──
    mu_th = predict_mu_th(data.snia_z, H0, Om, alpha)
    ll_snia = snia_log_likelihood(
        mu_th, data.snia_mb,
        data.snia_cov_inv, data.snia_cov_logdet,
    )

    # Total log-likelihood as factor
    numpyro.factor("log_likelihood", ll_bao + ll_hz + ll_growth + ll_snia)


def predict_bao_lcdm(z_arr, H0, Om, r_d, is_dh, is_dm, is_dv):
    """BAO predictions for LCDM (no gate evaluation)."""
    Hz_vals = Hz_lcdm(z_arr, H0, Om)
    dh_pred = C_KM_S / (Hz_vals * r_d)
    dm_mpc = comoving_at_z_lcdm(z_arr, H0, Om)
    dm_pred = dm_mpc / r_d
    dh_mpc = C_KM_S / Hz_vals
    dv_pred = (z_arr * dh_mpc * dm_mpc**2)**(1.0/3.0) / r_d
    pred = is_dh * dh_pred + is_dm * dm_pred + is_dv * dv_pred
    return pred


def predict_mu_th_lcdm(z_arr, H0, Om):
    """Distance modulus for LCDM (no gate evaluation)."""
    DM = comoving_at_z_lcdm(z_arr, H0, Om)
    dL = (1.0 + z_arr) * DM
    mu_th = 5.0 * jnp.log10(jnp.maximum(dL, 1e-30)) + 25.0
    return mu_th


def compute_fs8_lcdm(z, Om, H0, s8):
    """f*sigma8(z) for LCDM (alpha=0)."""
    a_eval = 1.0 / (1.0 + z)
    D_vals, Dp_vals, D_at_1 = solve_growth_rk4(Om, 0.0, a_eval)
    f = a_eval * Dp_vals / jnp.maximum(D_vals, 1e-30)
    sigma8_z = s8 * D_vals / jnp.maximum(D_at_1, 1e-30)
    return f * sigma8_z


def lcdm_model(data: ProbeData):
    """Numpyro model for LCDM (3 params, no gate).

    Reparametrized to standardized space for stable NUTS.
    D3: σ8 ~ N(0.80, 0.04) honest prior.
    """
    z_Om = numpyro.sample("z_Om", dist.Normal(0.0, 1.0))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0.0, 1.0))
    z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))

    Om = 0.30 + 0.05 * z_Om
    H0 = 67.5 + 5.0 * z_H0
    s8 = 0.80 + 0.04 * z_s8    # D3: honest prior

    numpyro.factor("Om_bound", -1e6 * jnp.where((Om < 0.05) | (Om > 0.8), 1.0, 0.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 < 40.0) | (H0 > 100.0), 1.0, 0.0))

    r_d = RD_FIXED

    bao_pred = predict_bao_lcdm(
        data.bao_z, H0, Om, r_d,
        data.bao_is_dh, data.bao_is_dm, data.bao_is_dv,
    )
    ll_bao = bao_log_likelihood(data, bao_pred)

    hz_pred = Hz_lcdm(data.hz_z, H0, Om)
    ll_hz = chi2_log_likelihood(data.hz_obs, hz_pred, data.hz_err)

    fs8_pred = compute_fs8_lcdm(data.growth_z, Om, H0, s8)
    ll_growth = chi2_log_likelihood(data.growth_obs, fs8_pred, data.growth_err)

    mu_th = predict_mu_th_lcdm(data.snia_z, H0, Om)
    ll_snia = snia_log_likelihood(
        mu_th, data.snia_mb,
        data.snia_cov_inv, data.snia_cov_logdet,
    )

    numpyro.factor("log_likelihood", ll_bao + ll_hz + ll_growth + ll_snia)


# ═══════════════════════════════════════════════════════════════
#  RUNNER
# ═══════════════════════════════════════════════════════════════

@dataclass
class NUTSResult:
    """Result from a NUTS run."""
    alpha_mean: float
    alpha_std: float
    alpha_significance: float
    alpha_p_negative: float
    om_mean: float
    om_std: float
    h0_mean: float
    h0_std: float
    s8_mean: float
    s8_std: float
    ll_max_efc: float
    ll_max_lcdm: float
    daic: float
    dbic: float
    n_data: int
    time_efc: float
    time_lcdm: float
    n_eff_min: float
    r_hat_max: float
    # Full posterior chain: shape (n_samples, 4) = [Om, H0, s8, alpha]
    # Thinned to max ~1000 samples for storage. None if not saved.
    posterior_chain: Optional[np.ndarray] = None
    # Diagnostic metadata (for N3/N4/N7 runs)
    diagnostic_name: Optional[str] = None
    verdict: Optional[str] = None


def run_nuts_efc(
    data: Optional[ProbeData] = None,
    num_warmup: int = 500,
    num_samples: int = 2000,
    num_chains: int = 1,
    seed: int = 42,
    target_accept: float = 0.8,
) -> NUTSResult:
    """Run NUTS MCMC for both EFC and LCDM models.

    Args:
        data:           ProbeData (loaded if None)
        num_warmup:     warmup/burnin steps
        num_samples:    post-warmup samples
        num_chains:     parallel chains (1 per GPU is typical)
        seed:           PRNG seed
        target_accept:  NUTS target acceptance (0.8 is standard)

    Returns:
        NUTSResult with alpha statistics and model comparison
    """
    if data is None:
        print("Loading data...")
        data = load_data()

    print(f"Data: {data.n_total} total points")
    print(f"  BAO: {len(data.bao_z)}, Growth: {len(data.growth_z)}, "
          f"Hz: {len(data.hz_z)}, SNIa: {len(data.snia_z)}")
    print(f"NUTS: {num_warmup} warmup + {num_samples} samples, "
          f"{num_chains} chain(s), target_accept={target_accept}")
    print(f"Device: {jax.devices()}")
    print()

    key = jax.random.PRNGKey(seed)

    # ── EFC run ──
    print("Running EFC NUTS (float64, dense mass, reparametrized)...")
    kernel_efc = NUTS(
        efc_model,
        target_accept_prob=target_accept,
        max_tree_depth=10,
        dense_mass=True,    # CRITICAL: condition number ~1000, need full mass matrix
        init_strategy=numpyro.infer.init_to_value(
            values={
                "z_Om": -0.18,     # Om ≈ 0.29 (near MAP)
                "z_H0": -0.10,     # H0 ≈ 67.0
                "z_s8": 0.0,     # s8 ≈ 0.80
                "z_alpha": -0.27,  # alpha ≈ -0.8
            }
        ),
    )
    chain_method = "parallel" if num_chains > 1 else "sequential"
    mcmc_efc = MCMC(kernel_efc, num_warmup=num_warmup,
                     num_samples=num_samples, num_chains=num_chains,
                     chain_method=chain_method,
                     progress_bar=True,
)

    t0 = time.time()
    mcmc_efc.run(key, data, extra_fields=("potential_energy",))
    dt_efc = time.time() - t0

    samples_efc = mcmc_efc.get_samples()
    # Transform back to physical parameters
    alpha_samples = np.array(0.0 + 3.0 * samples_efc["z_alpha"])
    om_samples = np.array(0.30 + 0.05 * samples_efc["z_Om"])
    h0_samples = np.array(67.5 + 5.0 * samples_efc["z_H0"])
    s8_samples = np.array(0.80 + 0.04 * samples_efc["z_s8"])  # D3: honest prior

    # Alpha statistics
    alpha_mean = float(np.mean(alpha_samples))
    alpha_std = float(np.std(alpha_samples))
    alpha_sig = abs(alpha_mean) / alpha_std if alpha_std > 0 else 0.0
    alpha_pneg = float(np.mean(alpha_samples < 0))

    print(f"  EFC: {dt_efc:.1f}s")
    print(f"  alpha = {alpha_mean:.3f} ± {alpha_std:.3f} ({alpha_sig:.2f}σ)")
    print(f"  Om = {np.mean(om_samples):.4f} ± {np.std(om_samples):.4f}")
    print(f"  H0 = {np.mean(h0_samples):.2f} ± {np.std(h0_samples):.2f}")
    print(f"  s8 = {np.mean(s8_samples):.4f} ± {np.std(s8_samples):.4f}")
    print()

    # ── LCDM run ──
    print("Running LCDM NUTS (float64, dense mass, reparametrized)...")
    key2 = jax.random.PRNGKey(seed + 1)
    kernel_lcdm = NUTS(
        lcdm_model,
        target_accept_prob=target_accept,
        max_tree_depth=10,
        dense_mass=True,
        init_strategy=numpyro.infer.init_to_value(
            values={"z_Om": -0.18, "z_H0": -0.10, "z_s8": 0.0}
        ),
    )
    mcmc_lcdm = MCMC(kernel_lcdm, num_warmup=num_warmup,
                      num_samples=num_samples, num_chains=num_chains,
                      chain_method=chain_method,
                      progress_bar=True,
 )

    t0 = time.time()
    mcmc_lcdm.run(key2, data, extra_fields=("potential_energy",))
    dt_lcdm = time.time() - t0

    samples_lcdm = mcmc_lcdm.get_samples()
    print(f"  LCDM: {dt_lcdm:.1f}s")
    print()

    # ── Model comparison ──
    # Estimate max log-likelihood from samples
    # For proper comparison, evaluate log_prob at MAP
    extra_fields_efc = mcmc_efc.get_extra_fields()
    extra_fields_lcdm = mcmc_lcdm.get_extra_fields()

    # numpyro stores potential energy = -log_prob
    if "potential_energy" in extra_fields_efc:
        ll_max_efc = float(-np.min(np.array(extra_fields_efc["potential_energy"])))
    else:
        ll_max_efc = float("nan")
    if "potential_energy" in extra_fields_lcdm:
        ll_max_lcdm = float(-np.min(np.array(extra_fields_lcdm["potential_energy"])))
    else:
        ll_max_lcdm = float("nan")

    k_efc = 4   # Om, H0, s8, alpha
    k_lcdm = 3  # Om, H0, s8
    n_data = data.n_total

    aic_efc = -2 * ll_max_efc + 2 * k_efc
    aic_lcdm = -2 * ll_max_lcdm + 2 * k_lcdm
    bic_efc = -2 * ll_max_efc + k_efc * np.log(n_data)
    bic_lcdm = -2 * ll_max_lcdm + k_lcdm * np.log(n_data)

    daic = float(aic_efc - aic_lcdm)
    dbic = float(bic_efc - bic_lcdm)

    # Diagnostics: n_eff and r_hat (only meaningful with multiple chains)
    n_eff_min = float("nan")
    r_hat_max = float("nan")
    if num_chains > 1:
        try:
            from numpyro.diagnostics import summary as numpyro_summary
            chain_samples = mcmc_efc.get_samples(group_by_chain=True)
            summ = numpyro_summary(chain_samples)
            n_effs = [float(v["n_eff"]) for v in summ.values()]
            r_hats = [float(v["r_hat"]) for v in summ.values()]
            n_eff_min = min(n_effs)
            r_hat_max = max(r_hats)
            print(f"  n_eff_min = {n_eff_min:.0f}")
            print(f"  r_hat_max = {r_hat_max:.4f}")
        except Exception as e:
            print(f"  Diagnostics failed: {e}")

    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"alpha = {alpha_mean:.3f} ± {alpha_std:.3f} ({alpha_sig:.2f}σ)")
    print(f"P(alpha < 0) = {alpha_pneg:.3f}")
    print(f"ΔAIC = {daic:.2f}  (negative = EFC favored)")
    print(f"ΔBIC = {dbic:.2f}")
    print(f"Time: EFC {dt_efc:.1f}s, LCDM {dt_lcdm:.1f}s")
    print(f"Total: {dt_efc + dt_lcdm:.1f}s")
    print()

    # Build full posterior chain: (n_samples, 4) = [Om, H0, s8, alpha]
    # Thin if needed (keep max ~1000 samples for storage)
    full_chain = np.column_stack([om_samples, h0_samples, s8_samples, alpha_samples])
    n_total_samples = len(full_chain)
    max_chain_size = 1000
    if n_total_samples > max_chain_size:
        thin_factor = n_total_samples // max_chain_size
        chain_thinned = full_chain[::thin_factor][:max_chain_size]
    else:
        chain_thinned = full_chain
    print(f"  Posterior chain: {full_chain.shape} → thinned to {chain_thinned.shape}")

    return NUTSResult(
        alpha_mean=alpha_mean,
        alpha_std=alpha_std,
        alpha_significance=alpha_sig,
        alpha_p_negative=alpha_pneg,
        om_mean=float(np.mean(om_samples)),
        om_std=float(np.std(om_samples)),
        h0_mean=float(np.mean(h0_samples)),
        h0_std=float(np.std(h0_samples)),
        s8_mean=float(np.mean(s8_samples)),
        s8_std=float(np.std(s8_samples)),
        ll_max_efc=ll_max_efc,
        ll_max_lcdm=ll_max_lcdm,
        daic=daic,
        dbic=dbic,
        n_data=n_data,
        time_efc=dt_efc,
        time_lcdm=dt_lcdm,
        n_eff_min=n_eff_min,
        r_hat_max=r_hat_max,
        posterior_chain=chain_thinned,
    )


# ═══════════════════════════════════════════════════════════════
#  DIAGNOSTIC MODELS (N1 / N2 / T7)
# ═══════════════════════════════════════════════════════════════

# ── N1b: EFC with r_d as free parameter ──

def efc_model_n1b(data: ProbeData):
    """EFC model with r_d ~ N(147.1, 4.0) (5 params: Om, H0, r_d, s8, alpha).

    D3: σ8 ~ N(0.80, 0.04) honest prior.
    """
    z_Om = numpyro.sample("z_Om", dist.Normal(0.0, 1.0))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0.0, 1.0))
    z_rd = numpyro.sample("z_rd", dist.Normal(0.0, 1.0))   # rd ~ N(147.1, 4.0)
    z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))
    z_alpha = numpyro.sample("z_alpha", dist.Normal(0.0, 1.0))

    Om = 0.30 + 0.05 * z_Om
    H0 = 67.5 + 5.0 * z_H0
    r_d = 147.1 + 4.0 * z_rd
    s8 = 0.80 + 0.04 * z_s8    # D3: honest prior
    alpha = 0.0 + 3.0 * z_alpha

    numpyro.factor("Om_bound", -1e6 * jnp.where((Om < 0.05) | (Om > 0.8), 1.0, 0.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 < 40.0) | (H0 > 100.0), 1.0, 0.0))
    numpyro.factor("rd_bound", -1e6 * jnp.where((r_d < 100.0) | (r_d > 200.0), 1.0, 0.0))

    bao_pred = predict_bao(data.bao_z, H0, Om, alpha, r_d,
                           data.bao_is_dh, data.bao_is_dm, data.bao_is_dv)
    ll_bao = bao_log_likelihood(data, bao_pred)
    hz_pred = Hz(data.hz_z, H0, Om, alpha)
    ll_hz = chi2_log_likelihood(data.hz_obs, hz_pred, data.hz_err)
    fs8_pred = compute_fs8(data.growth_z, Om, H0, s8, alpha)
    ll_growth = chi2_log_likelihood(data.growth_obs, fs8_pred, data.growth_err)
    mu_th = predict_mu_th(data.snia_z, H0, Om, alpha)
    ll_snia = snia_log_likelihood(mu_th, data.snia_mb, data.snia_cov_inv, data.snia_cov_logdet)

    numpyro.factor("log_likelihood", ll_bao + ll_hz + ll_growth + ll_snia)


def lcdm_model_n1b(data: ProbeData):
    """LCDM model with r_d ~ N(147.1, 4.0) (4 params: Om, H0, r_d, s8).

    D3: σ8 ~ N(0.80, 0.04) honest prior.
    """
    z_Om = numpyro.sample("z_Om", dist.Normal(0.0, 1.0))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0.0, 1.0))
    z_rd = numpyro.sample("z_rd", dist.Normal(0.0, 1.0))
    z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))

    Om = 0.30 + 0.05 * z_Om
    H0 = 67.5 + 5.0 * z_H0
    r_d = 147.1 + 4.0 * z_rd
    s8 = 0.80 + 0.04 * z_s8    # D3: honest prior

    numpyro.factor("Om_bound", -1e6 * jnp.where((Om < 0.05) | (Om > 0.8), 1.0, 0.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 < 40.0) | (H0 > 100.0), 1.0, 0.0))
    numpyro.factor("rd_bound", -1e6 * jnp.where((r_d < 100.0) | (r_d > 200.0), 1.0, 0.0))

    bao_pred = predict_bao_lcdm(data.bao_z, H0, Om, r_d,
                                data.bao_is_dh, data.bao_is_dm, data.bao_is_dv)
    ll_bao = bao_log_likelihood(data, bao_pred)
    hz_pred = Hz_lcdm(data.hz_z, H0, Om)
    ll_hz = chi2_log_likelihood(data.hz_obs, hz_pred, data.hz_err)
    fs8_pred = compute_fs8_lcdm(data.growth_z, Om, H0, s8)
    ll_growth = chi2_log_likelihood(data.growth_obs, fs8_pred, data.growth_err)
    mu_th = predict_mu_th_lcdm(data.snia_z, H0, Om)
    ll_snia = snia_log_likelihood(mu_th, data.snia_mb, data.snia_cov_inv, data.snia_cov_logdet)

    numpyro.factor("log_likelihood", ll_bao + ll_hz + ll_growth + ll_snia)


# ── N2: sigma8 sweep models ──

def efc_model_n2(data: ProbeData, s8_mode: str = "stram"):
    """EFC with variable sigma8 prior. 4 params: Om, H0, s8, alpha."""
    z_Om = numpyro.sample("z_Om", dist.Normal(0.0, 1.0))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0.0, 1.0))
    z_alpha = numpyro.sample("z_alpha", dist.Normal(0.0, 1.0))

    Om = 0.30 + 0.05 * z_Om
    H0 = 67.5 + 5.0 * z_H0
    alpha = 0.0 + 3.0 * z_alpha

    # sigma8 prior depends on mode (D3: honest priors)
    if s8_mode == "stram":
        z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))
        s8 = 0.80 + 0.04 * z_s8          # N(0.80, 0.04) D3: honest
    elif s8_mode == "middels":
        z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))
        s8 = 0.80 + 0.06 * z_s8          # N(0.80, 0.06)
    else:  # flat
        s8 = numpyro.sample("s8", dist.Uniform(0.6, 1.0))

    numpyro.factor("Om_bound", -1e6 * jnp.where((Om < 0.05) | (Om > 0.8), 1.0, 0.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 < 40.0) | (H0 > 100.0), 1.0, 0.0))

    r_d = RD_FIXED
    bao_pred = predict_bao(data.bao_z, H0, Om, alpha, r_d,
                           data.bao_is_dh, data.bao_is_dm, data.bao_is_dv)
    ll_bao = bao_log_likelihood(data, bao_pred)
    hz_pred = Hz(data.hz_z, H0, Om, alpha)
    ll_hz = chi2_log_likelihood(data.hz_obs, hz_pred, data.hz_err)
    fs8_pred = compute_fs8(data.growth_z, Om, H0, s8, alpha)
    ll_growth = chi2_log_likelihood(data.growth_obs, fs8_pred, data.growth_err)
    mu_th = predict_mu_th(data.snia_z, H0, Om, alpha)
    ll_snia = snia_log_likelihood(mu_th, data.snia_mb, data.snia_cov_inv, data.snia_cov_logdet)

    numpyro.factor("log_likelihood", ll_bao + ll_hz + ll_growth + ll_snia)


def lcdm_model_n2(data: ProbeData, s8_mode: str = "stram"):
    """LCDM with variable sigma8 prior. 3 params: Om, H0, s8."""
    z_Om = numpyro.sample("z_Om", dist.Normal(0.0, 1.0))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0.0, 1.0))

    Om = 0.30 + 0.05 * z_Om
    H0 = 67.5 + 5.0 * z_H0

    if s8_mode == "stram":
        z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))
        s8 = 0.80 + 0.04 * z_s8    # D3: honest prior
    elif s8_mode == "middels":
        z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))
        s8 = 0.80 + 0.06 * z_s8    # D3: honest center
    else:
        s8 = numpyro.sample("s8", dist.Uniform(0.6, 1.0))

    numpyro.factor("Om_bound", -1e6 * jnp.where((Om < 0.05) | (Om > 0.8), 1.0, 0.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 < 40.0) | (H0 > 100.0), 1.0, 0.0))

    r_d = RD_FIXED
    bao_pred = predict_bao_lcdm(data.bao_z, H0, Om, r_d,
                                data.bao_is_dh, data.bao_is_dm, data.bao_is_dv)
    ll_bao = bao_log_likelihood(data, bao_pred)
    hz_pred = Hz_lcdm(data.hz_z, H0, Om)
    ll_hz = chi2_log_likelihood(data.hz_obs, hz_pred, data.hz_err)
    fs8_pred = compute_fs8_lcdm(data.growth_z, Om, H0, s8)
    ll_growth = chi2_log_likelihood(data.growth_obs, fs8_pred, data.growth_err)
    mu_th = predict_mu_th_lcdm(data.snia_z, H0, Om)
    ll_snia = snia_log_likelihood(mu_th, data.snia_mb, data.snia_cov_inv, data.snia_cov_logdet)

    numpyro.factor("log_likelihood", ll_bao + ll_hz + ll_growth + ll_snia)


# ═══════════════════════════════════════════════════════════════
#  DIAGNOSTIC RUNNERS (N1 / N2 / T7)
# ═══════════════════════════════════════════════════════════════

def _run_single_nuts(model_fn, data, num_warmup, num_samples, num_chains,
                     seed, target_accept, init_values=None):
    """Run a single NUTS MCMC and return (mcmc, samples, dt, ll_max)."""
    key = jax.random.PRNGKey(seed)
    init_strat = (numpyro.infer.init_to_value(values=init_values)
                  if init_values else numpyro.infer.init_to_median())
    kernel = NUTS(model_fn, target_accept_prob=target_accept,
                  max_tree_depth=10, dense_mass=True, init_strategy=init_strat)
    chain_method = "parallel" if num_chains > 1 else "sequential"
    mcmc = MCMC(kernel, num_warmup=num_warmup, num_samples=num_samples,
                num_chains=num_chains, chain_method=chain_method,
                progress_bar=False)
    t0 = time.time()
    mcmc.run(key, data, extra_fields=("potential_energy",))
    dt = time.time() - t0

    samples = mcmc.get_samples()
    extra = mcmc.get_extra_fields()
    ll_max = float(-np.min(np.array(extra["potential_energy"])))
    return mcmc, samples, dt, ll_max


def _extract_alpha_nuts(samples, s8_mode=None) -> dict:
    """Extract alpha stats from NUTS samples dict (z-parametrized)."""
    alpha_samples = np.array(0.0 + 3.0 * samples["z_alpha"])
    mean = float(np.mean(alpha_samples))
    std = float(np.std(alpha_samples))
    sig = abs(mean) / std if std > 0 else 0.0
    pneg = float(np.mean(alpha_samples < 0))
    return {
        "mean": mean, "std": std, "significance": sig,
        "p_negative": pneg,
        "median": float(np.median(alpha_samples)),
        "ci95_lo": float(np.percentile(alpha_samples, 2.5)),
        "ci95_hi": float(np.percentile(alpha_samples, 97.5)),
    }


def run_n1_nuts(
    data: ProbeData,
    num_warmup: int = 300,
    num_samples: int = 1000,
    num_chains: int = 2,
    seed: int = 42,
    target_accept: float = 0.8,
    pass_sigma: float = 1.7,
    pass_daic: float = 0.0,
) -> dict:
    """N1: rd diagnostic via NUTS. Returns same structure as emcee N1.

    N1a: rd = 147.09 fixed (same as baseline)
    N1b: rd ~ N(147.1, 4.0) (5-param EFC vs 4-param LCDM)
    """
    print("=== N1: rd DIAGNOSTIC (NUTS) ===")
    n_data = data.n_total
    total_time = 0.0

    init_efc = {"z_Om": -0.18, "z_H0": -0.10, "z_s8": 0.0, "z_alpha": -0.27}
    init_lcdm = {"z_Om": -0.18, "z_H0": -0.10, "z_s8": 0.0}

    # ── N1a: rd FIXED (= baseline model, 4-param EFC vs 3-param LCDM) ──
    print("-- N1a: rd=147.09 fixed --")
    _, samp_n1a_efc, dt, ll_n1a_efc = _run_single_nuts(
        efc_model, data, num_warmup, num_samples, num_chains,
        seed + 10, target_accept, init_efc)
    total_time += dt

    _, _, dt, ll_n1a_lcdm = _run_single_nuts(
        lcdm_model, data, num_warmup, num_samples, num_chains,
        seed + 11, target_accept, init_lcdm)
    total_time += dt

    alpha_n1a = _extract_alpha_nuts(samp_n1a_efc)
    daic_n1a = float((-2 * ll_n1a_efc + 2 * 4) - (-2 * ll_n1a_lcdm + 2 * 3))
    dbic_n1a = float((-2 * ll_n1a_efc + 4 * np.log(n_data)) -
                     (-2 * ll_n1a_lcdm + 3 * np.log(n_data)))
    print(f"  N1a: alpha = {alpha_n1a['mean']:.3f} ± {alpha_n1a['std']:.3f} "
          f"({alpha_n1a['significance']:.2f}σ), ΔAIC={daic_n1a:.2f}")

    # ── N1b: rd ~ N(147.1, 4.0) (5-param EFC vs 4-param LCDM) ──
    print("-- N1b: rd prior N(147.1, 4.0) --")
    init_n1b_efc = {**init_efc, "z_rd": 0.0}
    init_n1b_lcdm = {**init_lcdm, "z_rd": 0.0}

    _, samp_n1b_efc, dt, ll_n1b_efc = _run_single_nuts(
        efc_model_n1b, data, num_warmup, num_samples, num_chains,
        seed + 20, target_accept, init_n1b_efc)
    total_time += dt

    _, samp_n1b_lcdm, dt, ll_n1b_lcdm = _run_single_nuts(
        lcdm_model_n1b, data, num_warmup, num_samples, num_chains,
        seed + 21, target_accept, init_n1b_lcdm)
    total_time += dt

    alpha_n1b = _extract_alpha_nuts(samp_n1b_efc)
    daic_n1b = float((-2 * ll_n1b_efc + 2 * 5) - (-2 * ll_n1b_lcdm + 2 * 4))
    dbic_n1b = float((-2 * ll_n1b_efc + 5 * np.log(n_data)) -
                     (-2 * ll_n1b_lcdm + 4 * np.log(n_data)))

    # rd posterior from N1b
    rd_samples = np.array(147.1 + 4.0 * samp_n1b_efc["z_rd"])
    rd_ci_lo = float(np.percentile(rd_samples, 2.5))
    rd_ci_hi = float(np.percentile(rd_samples, 97.5))
    rd_ci_width_95 = rd_ci_hi - rd_ci_lo

    print(f"  N1b: alpha = {alpha_n1b['mean']:.3f} ± {alpha_n1b['std']:.3f} "
          f"({alpha_n1b['significance']:.2f}σ), ΔAIC={daic_n1b:.2f}")
    print(f"  N1b: rd = {float(np.mean(rd_samples)):.1f} ± {float(np.std(rd_samples)):.1f} "
          f"CI=[{rd_ci_lo:.1f}, {rd_ci_hi:.1f}] width={rd_ci_width_95:.1f}")

    # Verdict
    n1a_pass = alpha_n1a["significance"] >= pass_sigma and daic_n1a <= pass_daic
    n1b_pass = alpha_n1b["significance"] >= pass_sigma and daic_n1b <= pass_daic

    if n1a_pass and n1b_pass:
        verdict = "PASS"
    elif n1a_pass and not n1b_pass:
        verdict = "PARTIAL"
    else:
        verdict = "COLLAPSED"

    print(f"  N1 VERDICT: {verdict}")

    return {
        "n1a": {
            "alpha": alpha_n1a, "daic": daic_n1a, "dbic": dbic_n1a,
        },
        "n1b": {
            "alpha": alpha_n1b, "daic": daic_n1b, "dbic": dbic_n1b,
            "rd_mean": float(np.mean(rd_samples)),
            "rd_std": float(np.std(rd_samples)),
            "rd_ci_width_95": rd_ci_width_95,
        },
        "verdict": verdict,
        "alpha_survives_n1a": n1a_pass,
        "alpha_survives_n1b": n1b_pass,
        "total_time_seconds": total_time,
    }


def run_n2_nuts(
    data: ProbeData,
    num_warmup: int = 300,
    num_samples: int = 1000,
    num_chains: int = 2,
    seed: int = 42,
    target_accept: float = 0.8,
    pass_sigma: float = 1.7,
    pass_daic: float = 0.0,
    collapse_sigma: float = 1.3,
) -> dict:
    """N2: sigma8 prior sweep via NUTS. Returns same structure as emcee N2."""
    print("=== N2: sigma8 SWEEP (NUTS) ===")
    n_data = data.n_total
    total_time = 0.0

    variants = {}
    for i, (label, s8_mode) in enumerate([
        ("N2a stram", "stram"),
        ("N2b middels", "middels"),
        ("N2c flat", "flat"),
    ]):
        print(f"-- {label} (sigma8 {s8_mode}) --")
        s_off = seed + 30 + i * 10

        # EFC
        init_efc = {"z_Om": -0.18, "z_H0": -0.10, "z_alpha": -0.27}
        if s8_mode != "flat":
            init_efc["z_s8"] = 0.0    # s8 = 0.80 (prior center)
        else:
            init_efc["s8"] = 0.80

        def efc_n2_fn(data, _mode=s8_mode):
            return efc_model_n2(data, _mode)

        _, samp_efc, dt, ll_efc = _run_single_nuts(
            efc_n2_fn, data, num_warmup, num_samples, num_chains,
            s_off, target_accept, init_efc)
        total_time += dt

        # LCDM
        init_lcdm = {"z_Om": -0.18, "z_H0": -0.10}
        if s8_mode != "flat":
            init_lcdm["z_s8"] = 0.0    # s8 = 0.80 (prior center)
        else:
            init_lcdm["s8"] = 0.80

        def lcdm_n2_fn(data, _mode=s8_mode):
            return lcdm_model_n2(data, _mode)

        _, _, dt, ll_lcdm = _run_single_nuts(
            lcdm_n2_fn, data, num_warmup, num_samples, num_chains,
            s_off + 1, target_accept, init_lcdm)
        total_time += dt

        alpha = _extract_alpha_nuts(samp_efc)
        daic = float((-2 * ll_efc + 2 * 4) - (-2 * ll_lcdm + 2 * 3))

        print(f"  {label}: alpha = {alpha['mean']:.3f} ± {alpha['std']:.3f} "
              f"({alpha['significance']:.2f}σ), ΔAIC={daic:.2f}")

        variants[s8_mode] = {
            "alpha": alpha,
            "daic": daic,
        }

    stram = variants["stram"]
    stram_pass = (stram["alpha"]["significance"] >= pass_sigma and
                  stram["daic"] <= pass_daic)

    if stram_pass:
        verdict = "PASS"
    elif stram["alpha"]["significance"] < collapse_sigma:
        verdict = "COLLAPSED"
    else:
        verdict = "MARGINAL"

    print(f"  N2 VERDICT: {verdict}")

    return {
        "variants": variants,
        "verdict": verdict,
        "alpha_survives_stram": stram_pass,
        "total_time_seconds": total_time,
    }


def run_t7_nuts(
    data: ProbeData,
    growth_path: str = "efc_inference/data/growth/fs8_extended.csv",
    num_warmup: int = 200,
    num_samples: int = 800,
    num_chains: int = 2,
    seed: int = 42,
    target_accept: float = 0.8,
    pass_sigma: float = .7,            # DEPRECATED — kept for backward compat
    pass_daic: float = 0.0,             # DEPRECATED
    loo_min_pass: int = 5,
    pass_p_negative: float = 0.80,      # NEW: sign-consistency criterion
) -> dict:
    """T7: Leave-One-Out on growth data via NUTS.

    For each of N growth points, re-run NUTS with that point excluded.

    Pass criterion (v2 — sign-consistency):
        P(α < 0) >= pass_p_negative (default 0.80) per LOO channel.
        Strength tags: strong (>0.95), medium (0.90-0.95), weak (0.80-0.90).

    Returns same structure as emcee T7 + new p_negative and strength fields.
    """
    print("=== T7: LEAVE-ONE-OUT (NUTS) ===")
    total_time = 0.0

    # Read raw growth data for LOO — pandas handles '#' comment headers robustly
    import pandas as _pd
    raw = _pd.read_csv(growth_path, comment="#").values
    n_growth = raw.shape[0]
    print(f"  Growth data: {n_growth} points")

    init_efc = {"z_Om": -0.18, "z_H0": -0.10, "z_s8": 0.0, "z_alpha": -0.27}
    init_lcdm = {"z_Om": -0.18, "z_H0": -0.10, "z_s8": 0.0}

    loo_results = []
    for idx in range(n_growth):
        excluded_z = float(raw[idx, 0])
        excluded_fs8 = float(raw[idx, 1])
        excluded_sig = float(raw[idx, 2])
        print(f"  LOO-{idx}: drop z={excluded_z:.2f} "
              f"(fs8={excluded_fs8:.3f}±{excluded_sig:.3f})")

        # Create LOO data — mask out one growth point
        mask = np.ones(n_growth, dtype=bool)
        mask[idx] = False
        loo_growth_z = jnp.array(raw[mask, 0])
        loo_growth_obs = jnp.array(raw[mask, 1])
        loo_growth_err = jnp.array(raw[mask, 2])

        # Build LOO ProbeData (replace growth arrays, keep everything else)
        loo_data = ProbeData(
            bao_z=data.bao_z, bao_obs=data.bao_obs, bao_err=data.bao_err,
            bao_types=data.bao_types,
            bao_is_dh=data.bao_is_dh, bao_is_dm=data.bao_is_dm, bao_is_dv=data.bao_is_dv,
            growth_z=loo_growth_z, growth_obs=loo_growth_obs, growth_err=loo_growth_err,
            hz_z=data.hz_z, hz_obs=data.hz_obs, hz_err=data.hz_err,
            snia_z=data.snia_z, snia_mb=data.snia_mb,
            snia_cov_inv=data.snia_cov_inv, snia_cov_logdet=data.snia_cov_logdet,
            n_total=data.n_total - 1,
        )
        n_data_loo = loo_data.n_total
        s_off = seed + 100 + idx * 10

        # EFC
        _, samp_efc, dt, ll_efc = _run_single_nuts(
            efc_model, loo_data, num_warmup, num_samples, num_chains,
            s_off, target_accept, init_efc)
        total_time += dt

        # LCDM
        _, _, dt, ll_lcdm = _run_single_nuts(
            lcdm_model, loo_data, num_warmup, num_samples, num_chains,
            s_off + 1, target_accept, init_lcdm)
        total_time += dt

        alpha = _extract_alpha_nuts(samp_efc)
        daic = float((-2 * ll_efc + 2 * 4) - (-2 * ll_lcdm + 2 * 3))

        # Sign-consistency criterion (v2):
        # Pass if P(α<0) >= pass_p_negative (default 0.80)
        pneg = alpha["p_negative"]
        passed = pneg >= pass_p_negative

        # Strength tag
        if pneg >= 0.95:
            strength = "strong"
        elif pneg >= 0.90:
            strength = "medium"
        elif pneg >= 0.80:
            strength = "weak"
        else:
            strength = "fail"

        print(f"    alpha = {alpha['mean']:.3f} ± {alpha['std']:.3f} "
              f"({alpha['significance']:.2f}σ) P(α<0)={pneg:.3f} [{strength}] "
              f"ΔAIC={daic:.2f} {'PASS' if passed else 'FAIL'}")

        loo_results.append({
            "idx": idx,
            "z_excluded": excluded_z,
            "fs8_excluded": excluded_fs8,
            "sig_excluded": excluded_sig,
            "alpha": alpha,
            "daic": daic,
            "passed": passed,
            "p_negative": pneg,
            "strength": strength,
        })

    # Summary
    pass_count = sum(1 for r in loo_results if r["passed"])
    robustness_score = pass_count / n_growth if n_growth > 0 else 0.0

    p_negs = [r["p_negative"] for r in loo_results]
    sigs = [r["alpha"]["significance"] for r in loo_results]
    most_influential_idx = int(np.argmin(p_negs))  # lowest P(α<0)
    alpha_means = [r["alpha"]["mean"] for r in loo_results]
    alpha_range = (min(alpha_means), max(alpha_means))

    # Strength distribution
    strength_counts = {}
    for r in loo_results:
        s = r["strength"]
        strength_counts[s] = strength_counts.get(s, 0) + 1

    if pass_count >= loo_min_pass:
        verdict = "PASS"
    elif pass_count >= 3:
        verdict = "PARTIAL"
    else:
        verdict = "NOT_ROBUST"

    print(f"  T7 SUMMARY: {pass_count}/{n_growth} sign-consistent "
          f"= {robustness_score:.0%}")
    print(f"  Strength: {strength_counts}")
    print(f"  P(α<0) range: [{min(p_negs):.3f}, {max(p_negs):.3f}]")
    print(f"  T7 VERDICT: {verdict}")

    return {
        "loo_results": loo_results,
        "pass_count": pass_count,
        "n_total": n_growth,
        "robustness_score": robustness_score,
        "verdict": verdict,
        "most_influential_idx": most_influential_idx,
        "alpha_range": alpha_range,
        "total_time_seconds": total_time,
        # New sign-consistency fields
        "criterion": "sign_consistency",
        "pass_p_negative": pass_p_negative,
        "p_negative_range": (min(p_negs), max(p_negs)) if p_negs else (0.0, 0.0),
        "strength_counts": strength_counts,
    }


# ═══════════════════════════════════════════════════════════════
#  N3: GATE FREEDOM MODEL (6 params: Om, H0, s8, alpha, a_t, delta_a)
# ═══════════════════════════════════════════════════════════════

# N3 gate sweep grid: (label, a_t, delta_a)
N3_GATE_SWEEP = [
    ("early",    0.35, 0.10),
    ("baseline", 0.50, 0.10),
    ("late",     0.65, 0.10),
    ("narrow",   0.50, 0.05),
    ("wide",     0.50, 0.20),
]


def efc_model_n3(data: ProbeData):
    """EFC model with FREE gate parameters (6 params).

    Reparametrized for NUTS: all in z-score space.
        Om    = 0.30 + 0.05 * z_Om
        H0    = 67.5 + 5.0 * z_H0
        s8    = 0.80 + 0.04 * z_s8         [~N(0.80, 0.04)]  D3: honest prior
        alpha = 0.0 + 3.0 * z_alpha
        a_t   = 0.50 + 0.15 * z_at       [~N(0.50, 0.15)]
        delta_a = 0.10 + 0.06 * z_da     [~N(0.10, 0.06)]
    """
    z_Om = numpyro.sample("z_Om", dist.Normal(0.0, 1.0))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0.0, 1.0))
    z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))
    z_alpha = numpyro.sample("z_alpha", dist.Normal(0.0, 1.0))
    z_at = numpyro.sample("z_at", dist.Normal(0.0, 1.0))
    z_da = numpyro.sample("z_da", dist.Normal(0.0, 1.0))

    Om = 0.30 + 0.05 * z_Om
    H0 = 67.5 + 5.0 * z_H0
    s8 = 0.80 + 0.04 * z_s8    # D3: honest prior
    alpha = 0.0 + 3.0 * z_alpha
    a_t = 0.50 + 0.15 * z_at
    delta_a = 0.10 + 0.06 * z_da

    # Soft bounds
    numpyro.factor("Om_bound", -1e6 * jnp.where((Om < 0.05) | (Om > 0.8), 1.0, 0.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 < 40.0) | (H0 > 100.0), 1.0, 0.0))
    numpyro.factor("at_bound", -1e6 * jnp.where((a_t < 0.15) | (a_t > 0.85), 1.0, 0.0))
    numpyro.factor("da_bound", -1e6 * jnp.where((delta_a < 0.01) | (delta_a > 0.40), 1.0, 0.0))

    r_d = RD_FIXED

    # BAO (N3 functions with parameterized gate)
    bao_pred = predict_bao_n3(
        data.bao_z, H0, Om, alpha, r_d, a_t, delta_a,
        data.bao_is_dh, data.bao_is_dm, data.bao_is_dv,
    )
    ll_bao = bao_log_likelihood(data, bao_pred)

    # Hz
    hz_pred = Hz_n3(data.hz_z, H0, Om, alpha, a_t, delta_a)
    ll_hz = chi2_log_likelihood(data.hz_obs, hz_pred, data.hz_err)

    # Growth
    fs8_pred = compute_fs8_n3(data.growth_z, Om, H0, s8, alpha, a_t, delta_a)
    ll_growth = chi2_log_likelihood(data.growth_obs, fs8_pred, data.growth_err)

    # SNIa
    mu_th = predict_mu_th_n3(data.snia_z, H0, Om, alpha, a_t, delta_a)
    ll_snia = snia_log_likelihood(
        mu_th, data.snia_mb,
        data.snia_cov_inv, data.snia_cov_logdet,
    )

    numpyro.factor("log_likelihood", ll_bao + ll_hz + ll_growth + ll_snia)


def efc_model_n3_aeff(data: ProbeData):
    """EFC model with A_eff reparameterized free gate (6 params).

    Samples A_eff (identifiable effective amplitude) instead of α.
    Gate normalization: g̃(a) = gate(a)/G where G = mean(gate(a_i)).
    Model: A_eff · [g̃(a) − g̃(1)].

    Breaks the α × gate-shape degeneracy that caused N3 COLLAPSED.

    D3: σ8 ~ N(0.80, 0.04) honest prior.
    """
    z_Om = numpyro.sample("z_Om", dist.Normal(0.0, 1.0))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0.0, 1.0))
    z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))
    z_Aeff = numpyro.sample("z_Aeff", dist.Normal(0.0, 1.0))
    z_at = numpyro.sample("z_at", dist.Normal(0.0, 1.0))
    z_da = numpyro.sample("z_da", dist.Normal(0.0, 1.0))

    Om = 0.30 + 0.05 * z_Om
    H0 = 67.5 + 5.0 * z_H0
    s8 = 0.80 + 0.04 * z_s8    # D3: honest prior
    A_eff = 0.0 + 3.0 * z_Aeff  # same prior scale as α (neutral)
    a_t = 0.50 + 0.15 * z_at
    delta_a = 0.10 + 0.06 * z_da

    # Soft bounds
    numpyro.factor("Om_bound", -1e6 * jnp.where((Om < 0.05) | (Om > 0.8), 1.0, 0.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 < 40.0) | (H0 > 100.0), 1.0, 0.0))
    numpyro.factor("at_bound", -1e6 * jnp.where((a_t < 0.15) | (a_t > 0.85), 1.0, 0.0))
    numpyro.factor("da_bound", -1e6 * jnp.where((delta_a < 0.01) | (delta_a > 0.40), 1.0, 0.0))

    r_d = RD_FIXED

    # All predictions use A_eff physics (normalized gate)
    bao_pred = predict_bao_aeff(
        data.bao_z, H0, Om, A_eff, r_d, a_t, delta_a,
        data.bao_is_dh, data.bao_is_dm, data.bao_is_dv,
    )
    ll_bao = bao_log_likelihood(data, bao_pred)

    hz_pred = Hz_aeff(data.hz_z, H0, Om, A_eff, a_t, delta_a)
    ll_hz = chi2_log_likelihood(data.hz_obs, hz_pred, data.hz_err)

    fs8_pred = compute_fs8_aeff(data.growth_z, Om, H0, s8, A_eff, a_t, delta_a)
    ll_growth = chi2_log_likelihood(data.growth_obs, fs8_pred, data.growth_err)

    mu_th = predict_mu_th_aeff(data.snia_z, H0, Om, A_eff, a_t, delta_a)
    ll_snia = snia_log_likelihood(
        mu_th, data.snia_mb,
        data.snia_cov_inv, data.snia_cov_logdet,
    )

    numpyro.factor("log_likelihood", ll_bao + ll_hz + ll_growth + ll_snia)


def efc_model_n3_fixed(data: ProbeData, a_t_fixed: float = 0.5,
                       delta_a_fixed: float = 0.1):
    """EFC model with FIXED gate (for N3 discrete sweep). 4 params: Om, H0, s8, alpha.

    D3: σ8 ~ N(0.80, 0.04) honest prior.
    """
    z_Om = numpyro.sample("z_Om", dist.Normal(0.0, 1.0))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0.0, 1.0))
    z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))
    z_alpha = numpyro.sample("z_alpha", dist.Normal(0.0, 1.0))

    Om = 0.30 + 0.05 * z_Om
    H0 = 67.5 + 5.0 * z_H0
    s8 = 0.80 + 0.04 * z_s8    # D3: honest prior
    alpha = 0.0 + 3.0 * z_alpha

    numpyro.factor("Om_bound", -1e6 * jnp.where((Om < 0.05) | (Om > 0.8), 1.0, 0.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 < 40.0) | (H0 > 100.0), 1.0, 0.0))

    r_d = RD_FIXED
    a_t = a_t_fixed
    delta_a = delta_a_fixed

    bao_pred = predict_bao_n3(
        data.bao_z, H0, Om, alpha, r_d, a_t, delta_a,
        data.bao_is_dh, data.bao_is_dm, data.bao_is_dv,
    )
    ll_bao = bao_log_likelihood(data, bao_pred)
    hz_pred = Hz_n3(data.hz_z, H0, Om, alpha, a_t, delta_a)
    ll_hz = chi2_log_likelihood(data.hz_obs, hz_pred, data.hz_err)
    fs8_pred = compute_fs8_n3(data.growth_z, Om, H0, s8, alpha, a_t, delta_a)
    ll_growth = chi2_log_likelihood(data.growth_obs, fs8_pred, data.growth_err)
    mu_th = predict_mu_th_n3(data.snia_z, H0, Om, alpha, a_t, delta_a)
    ll_snia = snia_log_likelihood(mu_th, data.snia_mb, data.snia_cov_inv, data.snia_cov_logdet)

    numpyro.factor("log_likelihood", ll_bao + ll_hz + ll_growth + ll_snia)


def run_n3_nuts(
    data: ProbeData,
    num_warmup: int = 300,
    num_samples: int = 1000,
    num_chains: int = 2,
    seed: int = 42,
    target_accept: float = 0.8,
    pass_sigma: float = 1.7,
    pass_daic: float = 0.0,
    collapse_sigma: float = 1.3,
) -> dict:
    """N3: Gate Freedom diagnostic via NUTS.

    Part 1: Discrete sweep — run baseline EFC at 5 fixed (a_t, delta_a) configs.
    Part 2: Free gate — run 6-param EFC with a_t, delta_a as MCMC params.

    Returns:
        dict with sweep_results, free_gate_result, correlations, verdict
    """
    print("=== N3: GATE FREEDOM (NUTS) ===")
    n_data = data.n_total
    total_time = 0.0

    init_efc = {"z_Om": -0.18, "z_H0": -0.10, "z_s8": 0.0, "z_alpha": -0.27}
    init_lcdm = {"z_Om": -0.18, "z_H0": -0.10, "z_s8": 0.0}

    # ── Part 1: Discrete sweep ──────────────────────────────────
    print("\n-- Part 1: Discrete gate sweep --")
    sweep_results = {}

    for label, a_t_val, da_val in N3_GATE_SWEEP:
        print(f"  [{label}] a_t={a_t_val}, delta_a={da_val}")
        s_off = seed + 50 + hash(label) % 100

        # EFC with fixed gate
        def _model_efc_fixed(data, _at=a_t_val, _da=da_val):
            return efc_model_n3_fixed(data, a_t_fixed=_at, delta_a_fixed=_da)

        _, samp_efc, dt, ll_efc = _run_single_nuts(
            _model_efc_fixed, data, num_warmup, num_samples, num_chains,
            s_off, target_accept, init_efc)
        total_time += dt

        # LCDM reference
        _, _, dt, ll_lcdm = _run_single_nuts(
            lcdm_model, data, num_warmup, num_samples, num_chains,
            s_off + 1, target_accept, init_lcdm)
        total_time += dt

        alpha = _extract_alpha_nuts(samp_efc)
        daic = float((-2 * ll_efc + 2 * 4) - (-2 * ll_lcdm + 2 * 3))

        print(f"    alpha = {alpha['mean']:.3f} ± {alpha['std']:.3f} "
              f"({alpha['significance']:.2f}σ), ΔAIC={daic:.2f}")

        sweep_results[label] = {
            "a_t": a_t_val,
            "delta_a": da_val,
            "alpha": alpha,
            "daic": daic,
        }

    # Sweep verdict: check if alpha is stable across gate configs
    sweep_sigs = [r["alpha"]["significance"] for r in sweep_results.values()]
    sweep_means = [r["alpha"]["mean"] for r in sweep_results.values()]
    sweep_stable = all(s >= collapse_sigma for s in sweep_sigs)
    sweep_range = max(sweep_means) - min(sweep_means) if sweep_means else 0.0
    print(f"  Sweep sigma range: [{min(sweep_sigs):.2f}, {max(sweep_sigs):.2f}]")
    print(f"  Sweep alpha range: {sweep_range:.3f}")

    # ── Part 2: Free gate (6-param) ────────────────────────────
    print("\n-- Part 2: Free gate (6-param) --")
    init_n3 = {
        "z_Om": -0.18, "z_H0": -0.10, "z_s8": 0.0, "z_alpha": -0.27,
        "z_at": 0.0, "z_da": 0.0,  # center of prior
    }

    _, samp_n3, dt, ll_n3 = _run_single_nuts(
        efc_model_n3, data, num_warmup, num_samples, num_chains,
        seed + 200, target_accept, init_n3)
    total_time += dt

    # LCDM comparison (3 params)
    _, _, dt, ll_lcdm_free = _run_single_nuts(
        lcdm_model, data, num_warmup, num_samples, num_chains,
        seed + 201, target_accept, init_lcdm)
    total_time += dt

    alpha_free = _extract_alpha_nuts(samp_n3)
    daic_free = float((-2 * ll_n3 + 2 * 6) - (-2 * ll_lcdm_free + 2 * 3))
    dbic_free = float((-2 * ll_n3 + 6 * np.log(n_data)) -
                      (-2 * ll_lcdm_free + 3 * np.log(n_data)))

    # Gate posteriors
    at_samples = np.array(0.50 + 0.15 * samp_n3["z_at"])
    da_samples = np.array(0.10 + 0.06 * samp_n3["z_da"])
    alpha_samples = np.array(0.0 + 3.0 * samp_n3["z_alpha"])

    at_mean = float(np.mean(at_samples))
    at_std = float(np.std(at_samples))
    da_mean = float(np.mean(da_samples))
    da_std = float(np.std(da_samples))

    print(f"  FREE: alpha = {alpha_free['mean']:.3f} ± {alpha_free['std']:.3f} "
          f"({alpha_free['significance']:.2f}σ), ΔAIC={daic_free:.2f}")
    print(f"  a_t = {at_mean:.3f} ± {at_std:.3f}")
    print(f"  delta_a = {da_mean:.4f} ± {da_std:.4f}")

    # Correlations
    corr_alpha_at = float(np.corrcoef(alpha_samples, at_samples)[0, 1])
    corr_alpha_da = float(np.corrcoef(alpha_samples, da_samples)[0, 1])
    corr_at_da = float(np.corrcoef(at_samples, da_samples)[0, 1])
    print(f"  Correlations: α-a_t={corr_alpha_at:.3f}, α-δ_a={corr_alpha_da:.3f}, "
          f"a_t-δ_a={corr_at_da:.3f}")

    correlations = {
        "alpha_at": corr_alpha_at,
        "alpha_da": corr_alpha_da,
        "at_da": corr_at_da,
    }

    free_gate_result = {
        "alpha": alpha_free,
        "daic": daic_free,
        "dbic": dbic_free,
        "a_t_mean": at_mean,
        "a_t_std": at_std,
        "delta_a_mean": da_mean,
        "delta_a_std": da_std,
        "correlations": correlations,
    }

    # ── Verdict ────────────────────────────────────────────────
    free_pass = alpha_free["significance"] >= pass_sigma and daic_free <= pass_daic
    high_degeneracy = abs(corr_alpha_at) > 0.8 or abs(corr_alpha_da) > 0.8

    if free_pass and sweep_stable and not high_degeneracy:
        verdict = "PASS"
    elif alpha_free["significance"] < collapse_sigma:
        verdict = "COLLAPSED"
    elif high_degeneracy:
        verdict = "DEGENERACY_LIMITED"
    elif sweep_stable and not free_pass:
        verdict = "MARGINAL"
    else:
        verdict = "MARGINAL"

    print(f"\n  N3 VERDICT: {verdict}")
    print(f"  (sweep_stable={sweep_stable}, free_pass={free_pass}, "
          f"high_degeneracy={high_degeneracy})")

    return {
        "sweep_results": sweep_results,
        "free_gate": free_gate_result,
        "verdict": verdict,
        "sweep_stable": sweep_stable,
        "alpha_survives_freedom": free_pass,
        "high_degeneracy": high_degeneracy,
        "total_time_seconds": total_time,
    }


# ═══════════════════════════════════════════════════════════════
#  N3-AEFF: GATE FREEDOM with A_eff REPARAMETERIZATION (NUTS)
# ═══════════════════════════════════════════════════════════════

def _extract_aeff_nuts(samples) -> dict:
    """Extract A_eff stats from NUTS samples (z-parametrized).

    Also computes derived α = A_eff / G for each posterior sample.
    """
    Aeff_samples = np.array(0.0 + 3.0 * samples["z_Aeff"])
    at_samples = np.array(0.50 + 0.15 * samples["z_at"])
    da_samples = np.array(0.10 + 0.06 * samples["z_da"])

    mean = float(np.mean(Aeff_samples))
    std = float(np.std(Aeff_samples))
    sig = abs(mean) / std if std > 0 else 0.0
    pneg = float(np.mean(Aeff_samples < 0))

    # Derive α = A_eff / G for each posterior sample
    # G = mean(gate(A_GRID, a_t, delta_a))
    a_grid_np = np.array(A_GRID)
    alpha_derived = []
    for i in range(len(Aeff_samples)):
        x = (a_grid_np - at_samples[i]) / da_samples[i]
        x = np.clip(x, -50, 50)
        g = 1.0 / (1.0 + np.exp(-x))
        G = max(np.mean(g), 1e-8)
        alpha_derived.append(Aeff_samples[i] / G)
    alpha_derived = np.array(alpha_derived)

    return {
        # A_eff (sampled parameter — identifiable)
        "mean": mean, "std": std, "significance": sig,
        "p_negative": pneg,
        "median": float(np.median(Aeff_samples)),
        "ci95_lo": float(np.percentile(Aeff_samples, 2.5)),
        "ci95_hi": float(np.percentile(Aeff_samples, 97.5)),
        # α (derived — for comparison with non-A_eff runs)
        "alpha_derived_mean": float(np.mean(alpha_derived)),
        "alpha_derived_std": float(np.std(alpha_derived)),
        "alpha_derived_p_negative": float(np.mean(alpha_derived < 0)),
    }


def run_n3_aeff_nuts(
    data: ProbeData,
    num_warmup: int = 300,
    num_samples: int = 1000,
    num_chains: int = 2,
    seed: int = 42,
    target_accept: float = 0.8,
    pass_sigma: float = 1.7,
    pass_daic: float = 0.0,
    collapse_sigma: float = 1.3,
) -> dict:
    """N3-AEFF: Gate Freedom with A_eff reparameterization (NUTS).

    Like run_n3_nuts but uses efc_model_n3_aeff which samples A_eff
    instead of α, breaking the α×gate degeneracy.

    Part 1: Discrete gate sweep (same as original N3 — uses α).
    Part 2: Free gate with A_eff (6-param, reparameterized).

    Expected improvement: σ(A_eff) should be MUCH smaller than σ(α)
    was in the original N3 free-gate, because A_eff is identifiable.
    """
    print("=== N3-AEFF: GATE FREEDOM with A_eff (NUTS) ===")
    n_data = data.n_total
    total_time = 0.0

    init_lcdm = {"z_Om": -0.18, "z_H0": -0.10, "z_s8": 0.0}

    # ── Part 1: Discrete gate sweep (α, for reference) ──────────
    # Keep the same discrete sweep as original N3 for comparison.
    print("\n-- Part 1: Discrete gate sweep (α, reference) --")
    init_efc = {"z_Om": -0.18, "z_H0": -0.10, "z_s8": 0.0, "z_alpha": -0.27}
    sweep_results = {}

    for label, a_t_val, da_val in N3_GATE_SWEEP:
        print(f"  [{label}] a_t={a_t_val}, delta_a={da_val}")
        s_off = seed + 50 + hash(label) % 100

        def _model_efc_fixed(data, _at=a_t_val, _da=da_val):
            return efc_model_n3_fixed(data, a_t_fixed=_at, delta_a_fixed=_da)

        _, samp_efc, dt, ll_efc = _run_single_nuts(
            _model_efc_fixed, data, num_warmup, num_samples, num_chains,
            s_off, target_accept, init_efc)
        total_time += dt

        _, _, dt, ll_lcdm = _run_single_nuts(
            lcdm_model, data, num_warmup, num_samples, num_chains,
            s_off + 1, target_accept, init_lcdm)
        total_time += dt

        alpha = _extract_alpha_nuts(samp_efc)
        daic = float((-2 * ll_efc + 2 * 4) - (-2 * ll_lcdm + 2 * 3))
        print(f"    alpha = {alpha['mean']:.3f} ± {alpha['std']:.3f} "
              f"({alpha['significance']:.2f}σ), ΔAIC={daic:.2f}")

        sweep_results[label] = {
            "a_t": a_t_val, "delta_a": da_val,
            "alpha": alpha, "daic": daic,
        }

    sweep_sigs = [r["alpha"]["significance"] for r in sweep_results.values()]
    sweep_stable = all(s >= collapse_sigma for s in sweep_sigs)

    # ── Part 2: Free gate with A_eff (6-param, reparameterized) ─
    print("\n-- Part 2: Free gate with A_eff (6-param) --")
    init_aeff = {
        "z_Om": -0.18, "z_H0": -0.10, "z_s8": 0.0, "z_Aeff": -0.27,
        "z_at": 0.0, "z_da": 0.0,
    }

    _, samp_aeff, dt, ll_aeff = _run_single_nuts(
        efc_model_n3_aeff, data, num_warmup, num_samples, num_chains,
        seed + 300, target_accept, init_aeff)
    total_time += dt

    # LCDM comparison
    _, _, dt, ll_lcdm_free = _run_single_nuts(
        lcdm_model, data, num_warmup, num_samples, num_chains,
        seed + 301, target_accept, init_lcdm)
    total_time += dt

    aeff_stats = _extract_aeff_nuts(samp_aeff)
    daic_aeff = float((-2 * ll_aeff + 2 * 6) - (-2 * ll_lcdm_free + 2 * 3))
    dbic_aeff = float((-2 * ll_aeff + 6 * np.log(n_data)) -
                       (-2 * ll_lcdm_free + 3 * np.log(n_data)))

    # Gate posteriors
    at_samples = np.array(0.50 + 0.15 * samp_aeff["z_at"])
    da_samples = np.array(0.10 + 0.06 * samp_aeff["z_da"])
    Aeff_samples = np.array(0.0 + 3.0 * samp_aeff["z_Aeff"])

    at_mean = float(np.mean(at_samples))
    at_std = float(np.std(at_samples))
    da_mean = float(np.mean(da_samples))
    da_std = float(np.std(da_samples))

    print(f"  A_eff = {aeff_stats['mean']:.3f} ± {aeff_stats['std']:.3f} "
          f"({aeff_stats['significance']:.2f}σ), ΔAIC={daic_aeff:.2f}")
    print(f"  α(derived) = {aeff_stats['alpha_derived_mean']:.3f} "
          f"± {aeff_stats['alpha_derived_std']:.3f}")
    print(f"  a_t = {at_mean:.3f} ± {at_std:.3f}")
    print(f"  delta_a = {da_mean:.4f} ± {da_std:.4f}")

    # Correlations (A_eff should be LESS correlated with gate than α was)
    corr_aeff_at = float(np.corrcoef(Aeff_samples, at_samples)[0, 1])
    corr_aeff_da = float(np.corrcoef(Aeff_samples, da_samples)[0, 1])
    corr_at_da = float(np.corrcoef(at_samples, da_samples)[0, 1])
    print(f"  Correlations: A_eff-a_t={corr_aeff_at:.3f}, "
          f"A_eff-δ_a={corr_aeff_da:.3f}, a_t-δ_a={corr_at_da:.3f}")

    correlations = {
        "aeff_at": corr_aeff_at,
        "aeff_da": corr_aeff_da,
        "at_da": corr_at_da,
    }

    free_gate_result = {
        "aeff": aeff_stats,
        "daic": daic_aeff,
        "dbic": dbic_aeff,
        "a_t_mean": at_mean, "a_t_std": at_std,
        "delta_a_mean": da_mean, "delta_a_std": da_std,
        "correlations": correlations,
    }

    # ── Verdict ────────────────────────────────────────────────
    free_pass = aeff_stats["significance"] >= pass_sigma and daic_aeff <= pass_daic
    high_degeneracy = abs(corr_aeff_at) > 0.8 or abs(corr_aeff_da) > 0.8

    if free_pass and sweep_stable and not high_degeneracy:
        verdict = "PASS"
    elif aeff_stats["significance"] < collapse_sigma:
        verdict = "COLLAPSED"
    elif high_degeneracy:
        verdict = "DEGENERACY_LIMITED"
    elif sweep_stable and not free_pass:
        verdict = "MARGINAL"
    else:
        verdict = "MARGINAL"

    print(f"\n  N3-AEFF VERDICT: {verdict}")
    print(f"  (sweep_stable={sweep_stable}, free_pass={free_pass}, "
          f"high_degeneracy={high_degeneracy})")

    return {
        "sweep_results": sweep_results,
        "free_gate": free_gate_result,
        "verdict": verdict,
        "sweep_stable": sweep_stable,
        "aeff_survives_freedom": free_pass,
        "high_degeneracy": high_degeneracy,
        "total_time_seconds": total_time,
        "reparameterized": True,  # flag to distinguish from old N3
    }


# ═══════════════════════════════════════════════════════════════
#  N4: MODIFIED POISSON (μ ≠ 1) — D1 diagnostic
# ═══════════════════════════════════════════════════════════════

# μ(a) = 1 + (μ_0 − 1) · g(a)
# At early times: g(a) ≈ 0 → μ ≈ 1 (GR). At late times: g(a) ≈ 1 → μ ≈ μ_0.
# Uses the FIXED gate (a_t, delta_a from module constants, same as baseline).

def mu_of_a(a, mu_0):
    """Modified gravitational coupling: μ(a) = 1 + (μ_0 − 1) · g(a)."""
    g_a = gate(a)
    return 1.0 + (mu_0 - 1.0) * g_a


def _growth_rhs_n4(a, D, Dp, Om, alpha, mu_0):
    """RHS of growth ODE with modified Poisson coupling μ(a).

    D'' = -friction * D' + source * D
    source = (3/2) · μ(a) · Ωm / (a⁵ · E²)
    """
    E2 = e_squared(a, Om, alpha)
    E_a = jnp.sqrt(jnp.maximum(E2, 1e-30))
    dE2_da = de_squared_da(a, Om, alpha)
    dE_da = dE2_da / (2.0 * E_a)

    friction = 3.0 / a + dE_da / E_a
    mu_a = mu_of_a(a, mu_0)
    source = 1.5 * mu_a * Om / (a**5.0 * E2)

    return Dp, -friction * Dp + source * D


def _solve_growth_raw_n4(Om, alpha, mu_0, a_eval):
    """Raw growth ODE solver with modified Poisson μ(a)."""
    a_grid = jnp.linspace(A_INI, 1.0, N_ODE_STEPS + 1)
    h = (1.0 - A_INI) / N_ODE_STEPS
    D0 = A_INI
    Dp0 = 1.0

    def rk4_step(state, a):
        D, Dp = state
        k1_D, k1_Dp = _growth_rhs_n4(a, D, Dp, Om, alpha, mu_0)
        k2_D, k2_Dp = _growth_rhs_n4(a + h/2, D + h/2*k1_D, Dp + h/2*k1_Dp, Om, alpha, mu_0)
        k3_D, k3_Dp = _growth_rhs_n4(a + h/2, D + h/2*k2_D, Dp + h/2*k2_Dp, Om, alpha, mu_0)
        k4_D, k4_Dp = _growth_rhs_n4(a + h, D + h*k3_D, Dp + h*k3_Dp, Om, alpha, mu_0)
        D_new = D + (h/6) * (k1_D + 2*k2_D + 2*k3_D + k4_D)
        Dp_new = Dp + (h/6) * (k1_Dp + 2*k2_Dp + 2*k3_Dp + k4_Dp)
        return (D_new, Dp_new), (D_new, Dp_new)

    _, (D_all, Dp_all) = jax.lax.scan(rk4_step, (D0, Dp0), a_grid[:-1])
    D_full = jnp.concatenate([jnp.array([D0]), D_all])
    Dp_full = jnp.concatenate([jnp.array([Dp0]), Dp_all])
    D_vals = jnp.interp(a_eval, a_grid, D_full)
    Dp_vals = jnp.interp(a_eval, a_grid, Dp_full)
    D_at_1 = D_full[-1]
    return D_vals, Dp_vals, D_at_1


@jax.custom_vjp
def solve_growth_rk4_n4(Om, alpha, mu_0, a_eval):
    """Growth ODE with modified Poisson + custom VJP (3 physics params)."""
    return _solve_growth_raw_n4(Om, alpha, mu_0, a_eval)


def _solve_growth_n4_fwd(Om, alpha, mu_0, a_eval):
    result = _solve_growth_raw_n4(Om, alpha, mu_0, a_eval)
    return result, (Om, alpha, mu_0, a_eval, result)


def _solve_growth_n4_bwd(res, g):
    """Backward: finite-difference gradients for Om, alpha, mu_0."""
    Om, alpha, mu_0, a_eval, (D_vals, Dp_vals, D_at_1) = res
    g_D, g_Dp, g_D1 = g

    eps = 1e-5

    # dD/dOm
    D_p, Dp_p, D1_p = _solve_growth_raw_n4(Om + eps, alpha, mu_0, a_eval)
    D_m, Dp_m, D1_m = _solve_growth_raw_n4(Om - eps, alpha, mu_0, a_eval)
    grad_Om = (jnp.sum(g_D * (D_p - D_m)) + jnp.sum(g_Dp * (Dp_p - Dp_m))
               + g_D1 * (D1_p - D1_m)) / (2 * eps)

    # dD/dalpha
    D_p, Dp_p, D1_p = _solve_growth_raw_n4(Om, alpha + eps, mu_0, a_eval)
    D_m, Dp_m, D1_m = _solve_growth_raw_n4(Om, alpha - eps, mu_0, a_eval)
    grad_alpha = (jnp.sum(g_D * (D_p - D_m)) + jnp.sum(g_Dp * (Dp_p - Dp_m))
                  + g_D1 * (D1_p - D1_m)) / (2 * eps)

    # dD/dmu_0
    D_p, Dp_p, D1_p = _solve_growth_raw_n4(Om, alpha, mu_0 + eps, a_eval)
    D_m, Dp_m, D1_m = _solve_growth_raw_n4(Om, alpha, mu_0 - eps, a_eval)
    grad_mu0 = (jnp.sum(g_D * (D_p - D_m)) + jnp.sum(g_Dp * (Dp_p - Dp_m))
                + g_D1 * (D1_p - D1_m)) / (2 * eps)

    grad_a_eval = jnp.zeros_like(a_eval)
    return grad_Om, grad_alpha, grad_mu0, grad_a_eval


solve_growth_rk4_n4.defvjp(_solve_growth_n4_fwd, _solve_growth_n4_bwd)


def compute_fs8_n4(z, Om, H0, s8, alpha, mu_0):
    """f*sigma8(z) with modified Poisson coupling μ(a).

    Only the growth ODE is affected — H(z), BAO, SNIa are unchanged.
    """
    a_eval = 1.0 / (1.0 + z)
    D_vals, Dp_vals, D_at_1 = solve_growth_rk4_n4(Om, alpha, mu_0, a_eval)
    f = a_eval * Dp_vals / jnp.maximum(D_vals, 1e-30)
    sigma8_z = s8 * D_vals / jnp.maximum(D_at_1, 1e-30)
    return f * sigma8_z


# ── N4 discrete sweep configs ────────────────────────────────

N4_MU_SWEEP = [
    ("mu_0.80", 0.80),    # sub-GR coupling
    ("mu_0.90", 0.90),    # mild sub-GR
    ("mu_1.00", 1.00),    # standard GR (baseline)
    ("mu_1.10", 1.10),    # mild super-GR
    ("mu_1.20", 1.20),    # super-GR coupling
]


def efc_model_n4(data: ProbeData):
    """EFC model with modified Poisson (5 params: Om, H0, s8, alpha, mu_0).

    Reparametrized for NUTS:
        Om    = 0.30 + 0.05 * z_Om
        H0    = 67.5 + 5.0 * z_H0
        s8    = 0.80 + 0.04 * z_s8         D3: honest prior
        alpha = 0.0 + 3.0 * z_alpha
        mu_0  = 1.0 + 0.3 * z_mu0          ~N(1.0, 0.3) centered on GR
    """
    z_Om = numpyro.sample("z_Om", dist.Normal(0.0, 1.0))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0.0, 1.0))
    z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))
    z_alpha = numpyro.sample("z_alpha", dist.Normal(0.0, 1.0))
    z_mu0 = numpyro.sample("z_mu0", dist.Normal(0.0, 1.0))

    Om = 0.30 + 0.05 * z_Om
    H0 = 67.5 + 5.0 * z_H0
    s8 = 0.80 + 0.04 * z_s8        # D3: honest prior
    alpha = 0.0 + 3.0 * z_alpha
    mu_0 = 1.0 + 0.3 * z_mu0       # N(1.0, 0.3) centered on GR

    # Soft bounds
    numpyro.factor("Om_bound", -1e6 * jnp.where((Om < 0.05) | (Om > 0.8), 1.0, 0.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 < 40.0) | (H0 > 100.0), 1.0, 0.0))
    numpyro.factor("mu0_bound", -1e6 * jnp.where((mu_0 < 0.3) | (mu_0 > 2.0), 1.0, 0.0))

    r_d = RD_FIXED

    # BAO — standard (μ does NOT affect expansion/distance)
    bao_pred = predict_bao(
        data.bao_z, H0, Om, alpha, r_d,
        data.bao_is_dh, data.bao_is_dm, data.bao_is_dv,
    )
    ll_bao = bao_log_likelihood(data, bao_pred)

    # Hz — standard (μ does NOT affect expansion)
    hz_pred = Hz(data.hz_z, H0, Om, alpha)
    ll_hz = chi2_log_likelihood(data.hz_obs, hz_pred, data.hz_err)

    # Growth — MODIFIED POISSON (only growth is affected by μ)
    fs8_pred = compute_fs8_n4(data.growth_z, Om, H0, s8, alpha, mu_0)
    ll_growth = chi2_log_likelihood(data.growth_obs, fs8_pred, data.growth_err)

    # SNIa — standard (μ does NOT affect luminosity distance)
    mu_th = predict_mu_th(data.snia_z, H0, Om, alpha)
    ll_snia = snia_log_likelihood(
        mu_th, data.snia_mb,
        data.snia_cov_inv, data.snia_cov_logdet,
    )

    numpyro.factor("log_likelihood", ll_bao + ll_hz + ll_growth + ll_snia)


def efc_model_n4_fixed(data: ProbeData, mu_0_fixed: float = 1.0):
    """EFC with FIXED mu_0 (for N4 discrete sweep). 4 params: Om, H0, s8, alpha.

    D3: σ8 ~ N(0.80, 0.04) honest prior.
    """
    z_Om = numpyro.sample("z_Om", dist.Normal(0.0, 1.0))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0.0, 1.0))
    z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))
    z_alpha = numpyro.sample("z_alpha", dist.Normal(0.0, 1.0))

    Om = 0.30 + 0.05 * z_Om
    H0 = 67.5 + 5.0 * z_H0
    s8 = 0.80 + 0.04 * z_s8    # D3: honest prior
    alpha = 0.0 + 3.0 * z_alpha

    numpyro.factor("Om_bound", -1e6 * jnp.where((Om < 0.05) | (Om > 0.8), 1.0, 0.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 < 40.0) | (H0 > 100.0), 1.0, 0.0))

    r_d = RD_FIXED
    mu_0 = mu_0_fixed

    bao_pred = predict_bao(data.bao_z, H0, Om, alpha, r_d,
                           data.bao_is_dh, data.bao_is_dm, data.bao_is_dv)
    ll_bao = bao_log_likelihood(data, bao_pred)
    hz_pred = Hz(data.hz_z, H0, Om, alpha)
    ll_hz = chi2_log_likelihood(data.hz_obs, hz_pred, data.hz_err)
    fs8_pred = compute_fs8_n4(data.growth_z, Om, H0, s8, alpha, mu_0)
    ll_growth = chi2_log_likelihood(data.growth_obs, fs8_pred, data.growth_err)
    mu_th = predict_mu_th(data.snia_z, H0, Om, alpha)
    ll_snia = snia_log_likelihood(mu_th, data.snia_mb, data.snia_cov_inv, data.snia_cov_logdet)

    numpyro.factor("log_likelihood", ll_bao + ll_hz + ll_growth + ll_snia)


def run_n4_nuts(
    data: ProbeData,
    num_warmup: int = 300,
    num_samples: int = 1000,
    num_chains: int = 2,
    seed: int = 42,
    target_accept: float = 0.8,
    pass_sigma: float = 1.7,
    collapse_sigma: float = 1.3,
) -> dict:
    """N4: Modified Poisson diagnostic via NUTS.

    Part 1: Discrete sweep — run EFC at 5 fixed μ_0 values {0.8, 0.9, 1.0, 1.1, 1.2}.
    Part 2: Free μ_0 — run 5-param EFC with μ_0 as MCMC parameter.

    Returns:
        dict with sweep_results, free_mu_result, correlations, verdict

    Verdict logic:
        PASS: α survives with free μ_0 + sweep stable + no degeneracy
        COLLAPSED: α significance < collapse_sigma with free μ_0
        DEGENERACY_LIMITED: |corr(α, μ_0)| > 0.80
        MARGINAL: otherwise
    """
    print("=== N4: MODIFIED POISSON (NUTS) ===")
    total_time = 0.0
    sweep_results = []

    # ── Part 1: Discrete μ_0 sweep ──
    print("-- Part 1: Discrete μ_0 sweep --")
    for i, (label, mu_0_val) in enumerate(N4_MU_SWEEP):
        print(f"  [{label}] μ_0 = {mu_0_val:.2f}")
        s_off = seed + 40 + i * 10

        def model_fn(data, _mu=mu_0_val):
            return efc_model_n4_fixed(data, mu_0_fixed=_mu)

        init_vals = {"z_Om": 0.0, "z_H0": 0.0, "z_s8": 0.0, "z_alpha": -0.27}
        _, samp, dt, ll = _run_single_nuts(
            model_fn, data, num_warmup, num_samples, num_chains,
            s_off, target_accept, init_vals)
        total_time += dt

        alpha_samples = np.array(0.0 + 3.0 * samp["z_alpha"])
        alpha_mean = float(np.mean(alpha_samples))
        alpha_std = float(np.std(alpha_samples))
        alpha_sig = abs(alpha_mean) / alpha_std if alpha_std > 0 else 0.0

        sweep_results.append({
            "label": label,
            "mu_0": mu_0_val,
            "alpha_mean": alpha_mean,
            "alpha_std": alpha_std,
            "alpha_sig": alpha_sig,
        })
        print(f"    α = {alpha_mean:.3f} ± {alpha_std:.3f} ({alpha_sig:.2f}σ)")

    # Sweep stability: α significance range < 0.5σ across sweep
    sweep_sigs = [r["alpha_sig"] for r in sweep_results]
    sweep_range = max(sweep_sigs) - min(sweep_sigs)
    sweep_stable = sweep_range < 0.5
    print(f"  Sweep range: {sweep_range:.2f}σ — {'STABLE' if sweep_stable else 'UNSTABLE'}")

    # ── Part 2: Free μ_0 (5 params) ──
    print("-- Part 2: Free μ_0 (5 params) --")
    init_free = {
        "z_Om": 0.0, "z_H0": 0.0, "z_s8": 0.0,
        "z_alpha": -0.27, "z_mu0": 0.0,
    }
    _, samp_free, dt, ll_free = _run_single_nuts(
        efc_model_n4, data, num_warmup, num_samples, num_chains,
        seed + 99, target_accept, init_free)
    total_time += dt

    alpha_free = np.array(0.0 + 3.0 * samp_free["z_alpha"])
    mu0_free = np.array(1.0 + 0.3 * samp_free["z_mu0"])
    om_free = np.array(0.30 + 0.05 * samp_free["z_Om"])
    s8_free = np.array(0.80 + 0.04 * samp_free["z_s8"])

    alpha_mean = float(np.mean(alpha_free))
    alpha_std = float(np.std(alpha_free))
    alpha_sig = abs(alpha_mean) / alpha_std if alpha_std > 0 else 0.0
    mu0_mean = float(np.mean(mu0_free))
    mu0_std = float(np.std(mu0_free))

    free_mu_result = {
        "alpha_mean": alpha_mean,
        "alpha_std": alpha_std,
        "alpha_sig": alpha_sig,
        "alpha_p_negative": float(np.mean(alpha_free < 0)),
        "mu0_mean": mu0_mean,
        "mu0_std": mu0_std,
        "mu0_deviation_from_gr": abs(mu0_mean - 1.0) / mu0_std if mu0_std > 0 else 0.0,
    }

    print(f"  α = {alpha_mean:.3f} ± {alpha_std:.3f} ({alpha_sig:.2f}σ)")
    print(f"  μ_0 = {mu0_mean:.3f} ± {mu0_std:.3f}")

    # Correlations
    chain_5 = np.column_stack([om_free, s8_free, alpha_free, mu0_free])
    corrmat = np.corrcoef(chain_5.T)
    corr_alpha_mu0 = float(corrmat[2, 3])
    correlations = {
        "alpha_om": float(corrmat[0, 2]),
        "alpha_s8": float(corrmat[1, 2]),
        "alpha_mu0": corr_alpha_mu0,
        "mu0_om": float(corrmat[0, 3]),
        "mu0_s8": float(corrmat[1, 3]),
    }
    print(f"  corr(α, μ_0) = {corr_alpha_mu0:.3f}")

    # Verdict
    free_pass = alpha_sig >= pass_sigma
    high_degeneracy = abs(corr_alpha_mu0) > 0.80

    if alpha_sig < collapse_sigma:
        verdict = "COLLAPSED"
    elif free_pass and sweep_stable and not high_degeneracy:
        verdict = "PASS"
    elif high_degeneracy:
        verdict = "DEGENERACY_LIMITED"
    else:
        verdict = "MARGINAL"

    print(f"  N4 VERDICT: {verdict}")
    print(f"  Total time: {total_time:.1f}s")

    return {
        "sweep_results": sweep_results,
        "free_mu": free_mu_result,
        "correlations": correlations,
        "verdict": verdict,
        "sweep_stable": sweep_stable,
        "alpha_survives_freedom": free_pass,
        "high_degeneracy": high_degeneracy,
        "total_time_seconds": total_time,
    }


# ═══════════════════════════════════════════════════════════════
#  N5: SOUND HORIZON PRIOR SWEEP (D2a)
# ═══════════════════════════════════════════════════════════════

def efc_model_n5_gaussian(data: ProbeData, rd_mu: float = 147.0, rd_sigma: float = 5.0):
    """Numpyro model for EFC with free r_d (Gaussian prior).

    5 params: [Om, H0, rd, s8, alpha]
    r_d ~ N(rd_mu, rd_sigma)
    D3: σ8 ~ N(0.80, 0.04) honest prior.
    """
    z_Om = numpyro.sample("z_Om", dist.Normal(0.0, 1.0))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0.0, 1.0))
    z_rd = numpyro.sample("z_rd", dist.Normal(0.0, 1.0))
    z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))
    z_alpha = numpyro.sample("z_alpha", dist.Normal(0.0, 1.0))

    Om = 0.30 + 0.05 * z_Om
    H0 = 67.5 + 5.0 * z_H0
    r_d = rd_mu + rd_sigma * z_rd
    s8 = 0.80 + 0.04 * z_s8
    alpha = 0.0 + 3.0 * z_alpha

    numpyro.factor("Om_bound", -1e6 * jnp.where((Om < 0.05) | (Om > 0.8), 1.0, 0.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 < 40.0) | (H0 > 100.0), 1.0, 0.0))
    numpyro.factor("rd_bound", -1e6 * jnp.where((r_d < 50.0) | (r_d > 250.0), 1.0, 0.0))

    # ── BAO ──
    bao_pred = predict_bao(
        data.bao_z, H0, Om, alpha, r_d,
        data.bao_is_dh, data.bao_is_dm, data.bao_is_dv,
    )
    ll_bao = bao_log_likelihood(data, bao_pred)

    # ── Hz ──
    hz_pred = Hz(data.hz_z, H0, Om, alpha)
    ll_hz = chi2_log_likelihood(data.hz_obs, hz_pred, data.hz_err)

    # ── Growth ──
    fs8_pred = compute_fs8(data.growth_z, Om, H0, s8, alpha)
    ll_growth = chi2_log_likelihood(data.growth_obs, fs8_pred, data.growth_err)

    # ── SNIa ──
    mu_th = predict_mu_th(data.snia_z, H0, Om, alpha)
    ll_snia = snia_log_likelihood(
        mu_th, data.snia_mb,
        data.snia_cov_inv, data.snia_cov_logdet,
    )

    numpyro.factor("log_likelihood", ll_bao + ll_hz + ll_growth + ll_snia)


def efc_model_n5_flat(data: ProbeData):
    """Numpyro model for EFC with free r_d (flat prior U(100,200)).

    5 params: [Om, H0, rd, s8, alpha]
    r_d ~ U(100, 200)
    D3: σ8 ~ N(0.80, 0.04) honest prior.
    """
    z_Om = numpyro.sample("z_Om", dist.Normal(0.0, 1.0))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0.0, 1.0))
    z_rd = numpyro.sample("z_rd", dist.Uniform(-1.0, 1.0))
    z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))
    z_alpha = numpyro.sample("z_alpha", dist.Normal(0.0, 1.0))

    Om = 0.30 + 0.05 * z_Om
    H0 = 67.5 + 5.0 * z_H0
    r_d = 150.0 + 50.0 * z_rd      # maps [-1,1] → [100,200]
    s8 = 0.80 + 0.04 * z_s8
    alpha = 0.0 + 3.0 * z_alpha

    numpyro.factor("Om_bound", -1e6 * jnp.where((Om < 0.05) | (Om > 0.8), 1.0, 0.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 < 40.0) | (H0 > 100.0), 1.0, 0.0))

    # ── BAO ──
    bao_pred = predict_bao(
        data.bao_z, H0, Om, alpha, r_d,
        data.bao_is_dh, data.bao_is_dm, data.bao_is_dv,
    )
    ll_bao = bao_log_likelihood(data, bao_pred)

    # ── Hz ──
    hz_pred = Hz(data.hz_z, H0, Om, alpha)
    ll_hz = chi2_log_likelihood(data.hz_obs, hz_pred, data.hz_err)

    # ── Growth ──
    fs8_pred = compute_fs8(data.growth_z, Om, H0, s8, alpha)
    ll_growth = chi2_log_likelihood(data.growth_obs, fs8_pred, data.growth_err)

    # ── SNIa ──
    mu_th = predict_mu_th(data.snia_z, H0, Om, alpha)
    ll_snia = snia_log_likelihood(
        mu_th, data.snia_mb,
        data.snia_cov_inv, data.snia_cov_logdet,
    )

    numpyro.factor("log_likelihood", ll_bao + ll_hz + ll_growth + ll_snia)


# N5 prior configurations: (label, rd_mu, rd_sigma)
N5_RD_CONFIGS = [
    ("tight",    147.0,  2.0),   # BBN-informed
    ("standard", 147.0,  5.0),   # standard N1b-like
    ("broad",    147.0, 10.0),   # ΛCDM-independent
]


def run_n5_nuts(
    data: ProbeData,
    num_warmup: int = 300,
    num_samples: int = 1000,
    num_chains: int = 2,
    seed: int = 42,
    target_accept: float = 0.8,
    pass_sigma: float = 1.7,
    collapse_sigma: float = 1.3,
    degeneracy_corr_max: float = 0.80,
) -> dict:
    """N5/D2a: Sound horizon prior sweep via NUTS.

    Part 1: Gaussian r_d priors — tight/standard/broad N(147, {2,5,10}).
    Part 2: Flat r_d prior — U(100, 200).

    Tests whether α signal is robust to r_d prior choice.

    Returns:
        dict with sweep_results, verdict, stability, degeneracy info
    """
    print("=== N5/D2a: SOUND HORIZON PRIOR SWEEP (NUTS) ===")
    total_time = 0.0
    sweep_results = []

    # ── Part 1: Gaussian r_d prior sweep ──
    print("-- Part 1: Gaussian r_d prior sweep --")
    init_vals = {
        "z_Om": 0.0, "z_H0": 0.0, "z_rd": 0.0,
        "z_s8": 0.0, "z_alpha": -0.27,
    }

    for i, (label, rd_mu, rd_sigma) in enumerate(N5_RD_CONFIGS):
        print(f"  [{label}] r_d ~ N({rd_mu}, {rd_sigma})")
        s_off = seed + 50 + i * 10

        def model_fn(data, _mu=rd_mu, _sig=rd_sigma):
            return efc_model_n5_gaussian(data, rd_mu=_mu, rd_sigma=_sig)

        _, samp, dt, ll = _run_single_nuts(
            model_fn, data, num_warmup, num_samples, num_chains,
            s_off, target_accept, init_vals)
        total_time += dt

        alpha_samples = np.array(0.0 + 3.0 * samp["z_alpha"])
        rd_samples = np.array(rd_mu + rd_sigma * samp["z_rd"])

        alpha_mean = float(np.mean(alpha_samples))
        alpha_std = float(np.std(alpha_samples))
        alpha_sig = abs(alpha_mean) / alpha_std if alpha_std > 0 else 0.0
        alpha_pneg = float(np.mean(alpha_samples < 0))

        rd_mean = float(np.mean(rd_samples))
        rd_std = float(np.std(rd_samples))
        rd_ci_width = float(np.percentile(rd_samples, 97.5) -
                           np.percentile(rd_samples, 2.5))

        corr_alpha_rd = float(np.corrcoef(alpha_samples, rd_samples)[0, 1])

        print(f"    α = {alpha_mean:.3f} ± {alpha_std:.3f} ({alpha_sig:.2f}σ)")
        print(f"    r_d = {rd_mean:.1f} ± {rd_std:.1f}, 95%CI={rd_ci_width:.1f}")
        print(f"    corr(α, r_d) = {corr_alpha_rd:.3f}")

        sweep_results.append({
            "config": label,
            "rd_prior_mu": rd_mu,
            "rd_prior_sigma": rd_sigma,
            "alpha_mean": alpha_mean,
            "alpha_std": alpha_std,
            "alpha_sig": alpha_sig,
            "alpha_p_negative": alpha_pneg,
            "rd_mean": rd_mean,
            "rd_std": rd_std,
            "rd_ci_width_95": rd_ci_width,
            "corr_alpha_rd": corr_alpha_rd,
        })

    # ── Part 2: Flat r_d prior ──
    print("-- Part 2: Flat r_d prior U(100, 200) --")
    init_flat = {
        "z_Om": 0.0, "z_H0": 0.0, "z_rd": 0.0,
        "z_s8": 0.0, "z_alpha": -0.27,
    }
    _, samp_flat, dt, ll_flat = _run_single_nuts(
        efc_model_n5_flat, data, num_warmup, num_samples, num_chains,
        seed + 60, target_accept, init_flat)
    total_time += dt

    alpha_flat = np.array(0.0 + 3.0 * samp_flat["z_alpha"])
    rd_flat = np.array(150.0 + 50.0 * samp_flat["z_rd"])

    alpha_flat_mean = float(np.mean(alpha_flat))
    alpha_flat_std = float(np.std(alpha_flat))
    alpha_flat_sig = abs(alpha_flat_mean) / alpha_flat_std if alpha_flat_std > 0 else 0.0
    alpha_flat_pneg = float(np.mean(alpha_flat < 0))

    rd_flat_mean = float(np.mean(rd_flat))
    rd_flat_std = float(np.std(rd_flat))
    corr_flat = float(np.corrcoef(alpha_flat, rd_flat)[0, 1])

    print(f"    α = {alpha_flat_mean:.3f} ± {alpha_flat_std:.3f} ({alpha_flat_sig:.2f}σ)")
    print(f"    r_d = {rd_flat_mean:.1f} ± {rd_flat_std:.1f}")
    print(f"    corr(α, r_d) = {corr_flat:.3f}")

    sweep_results.append({
        "config": "flat",
        "rd_prior_mu": None,
        "rd_prior_sigma": None,
        "alpha_mean": alpha_flat_mean,
        "alpha_std": alpha_flat_std,
        "alpha_sig": alpha_flat_sig,
        "alpha_p_negative": alpha_flat_pneg,
        "rd_mean": rd_flat_mean,
        "rd_std": rd_flat_std,
        "rd_ci_width_95": float(np.percentile(rd_flat, 97.5) -
                                np.percentile(rd_flat, 2.5)),
        "corr_alpha_rd": corr_flat,
    })

    # ── Verdict ──
    sigs = [r["alpha_sig"] for r in sweep_results]
    sig_range = max(sigs) - min(sigs) if sigs else 0.0
    sweep_stable = sig_range < 1.0  # less than 1σ variation

    max_corr = max(abs(r["corr_alpha_rd"]) for r in sweep_results)
    high_degeneracy = max_corr > degeneracy_corr_max

    free_pass = alpha_flat_sig >= pass_sigma

    if alpha_flat_sig < collapse_sigma:
        verdict = "COLLAPSED"
    elif free_pass and sweep_stable and not high_degeneracy:
        verdict = "PASS"
    elif high_degeneracy:
        verdict = "DEGENERACY_LIMITED"
    else:
        verdict = "MARGINAL"

    print(f"  Sweep σ range: [{min(sigs):.2f}, {max(sigs):.2f}], range={sig_range:.2f}")
    print(f"  Max |corr(α,rd)| = {max_corr:.3f}")
    print(f"  N5 VERDICT: {verdict}")
    print(f"  Total time: {total_time:.1f}s")

    return {
        "sweep_results": sweep_results,
        "verdict": verdict,
        "sweep_stable": sweep_stable,
        "high_degeneracy": high_degeneracy,
        "sig_range": sig_range,
        "max_corr_alpha_rd": max_corr,
        "alpha_survives_flat": free_pass,
        "total_time_seconds": total_time,
    }


# ═══════════════════════════════════════════════════════════════
#  N6 / D2b: EFC SOUND HORIZON DIAGNOSTIC (NUTS)
# ═══════════════════════════════════════════════════════════════

def run_n6_nuts(
    posterior_samples: dict,
    R_max: float = 0.01,
    sigma_ln_a: float = 0.5,
    safety_threshold_pct: float = 0.5,
    Omega_b: float = 0.0493,
    sweep_R_max: list = None,
) -> dict:
    """N6/D2b: EFC-native sound horizon diagnostic (NUTS version).

    POST-FIT diagnostic — no MCMC. Takes posterior samples from the
    baseline NUTS fit and computes r_d^EFC for each, giving a
    posterior distribution of the EFC correction.

    Uses numpy (not JAX) since this is a post-processing step.

    Args:
        posterior_samples: Dict from NUTS with keys "z_Om", "z_H0", etc.
        R_max:           Peak grid resistance (default: 0.01)
        sigma_ln_a:      Gaussian window width
        safety_threshold_pct: Max |Delta r_d| [%]
        Omega_b:         Baryon density
        sweep_R_max:     R_max values for sweep

    Returns:
        dict matching emcee N6 format for unified publishing
    """
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from efc_inference.core.sound_horizon import compute_rd_efc as _compute_rd

    print("=== N6/D2b: EFC SOUND HORIZON DIAGNOSTIC (NUTS) ===")
    import time as _time
    t0 = _time.time()

    if sweep_R_max is None:
        sweep_R_max = [0.0, 0.001, 0.005, 0.01, 0.02, 0.05]

    # Reconstruct physical parameters from non-centered NUTS samples
    Om_samples = np.array(0.30 + 0.05 * posterior_samples["z_Om"])
    H0_samples = np.array(67.0 + 5.0 * posterior_samples["z_H0"])

    n_total = len(Om_samples)
    max_eval = 500
    if n_total > max_eval:
        rng = np.random.RandomState(42)
        idx = rng.choice(n_total, max_eval, replace=False)
        Om_sub = Om_samples[idx]
        H0_sub = H0_samples[idx]
    else:
        Om_sub = Om_samples
        H0_sub = H0_samples

    print(f"  Processing {len(Om_sub)} posterior samples (of {n_total})")

    # Per-sample r_d computation
    rd_efc_arr = []
    rd_gr_arr = []
    delta_arr = []
    R_drag_arr = []
    R_peak_arr = []

    for Om_i, H0_i in zip(Om_sub, H0_sub):
        result = _compute_rd(float(Om_i), float(H0_i), Omega_b,
                             R_max, sigma_ln_a, safety_threshold_pct)
        rd_efc_arr.append(result["rd_efc"])
        rd_gr_arr.append(result["rd_gr"])
        delta_arr.append(result["delta_rd_pct"])
        R_drag_arr.append(result["R_at_drag"])
        R_peak_arr.append(result["R_peak"])

    rd_efc_arr = np.array(rd_efc_arr)
    rd_gr_arr = np.array(rd_gr_arr)
    delta_arr = np.array(delta_arr)

    rd_efc_mean = float(np.mean(rd_efc_arr))
    rd_efc_std = float(np.std(rd_efc_arr))
    rd_gr_mean = float(np.mean(rd_gr_arr))
    rd_gr_std = float(np.std(rd_gr_arr))
    delta_mean = float(np.mean(delta_arr))
    delta_std = float(np.std(delta_arr))

    from efc_inference.core.sound_horizon import SAFETY_WARN_PCT
    abs_delta_max = float(np.max(np.abs(delta_arr)))
    safety_pass = abs_delta_max < safety_threshold_pct
    if abs_delta_max < SAFETY_WARN_PCT:
        safety_level = "pass"
    elif abs_delta_max < safety_threshold_pct:
        safety_level = "warning"
    else:
        safety_level = "fail"

    print(f"  r_d^EFC = {rd_efc_mean:.4f} +/- {rd_efc_std:.4f} Mpc")
    print(f"  r_d^GR  = {rd_gr_mean:.4f} +/- {rd_gr_std:.4f} Mpc")
    print(f"  Delta   = {delta_mean:+.4f} +/- {delta_std:.4f}%")
    print(f"  R(a_d)  = {np.mean(R_drag_arr):.6f}")
    print(f"  R_peak  = {np.mean(R_peak_arr):.6f}")
    print(f"  Safety  = {safety_level.upper()} (|D|_max={abs_delta_max:.3f}%, "
          f"warn={SAFETY_WARN_PCT}%, fail={safety_threshold_pct}%)")

    # Sensitivity sweep at posterior median
    Om_med = float(np.median(Om_samples))
    H0_med = float(np.median(H0_samples))

    sweep_results = []
    for R_m in sweep_R_max:
        sr = _compute_rd(Om_med, H0_med, Omega_b, R_m, sigma_ln_a, safety_threshold_pct)
        sweep_results.append({
            "R_max": R_m,
            "rd_efc": sr["rd_efc"],
            "rd_gr": sr["rd_gr"],
            "delta_rd_pct": sr["delta_rd_pct"],
            "delta_rd_vs_planck_pct": sr["delta_rd_vs_planck_pct"],
            "safety_pass": sr["safety_pass"],
        })
        print(f"  Sweep R_max={R_m:.4f}: rd={sr['rd_efc']:.4f}, "
              f"Delta={sr['delta_rd_pct']:+.4f}%")

    # Verdict (three-tier: PASS / WARN / FAIL)
    # PASS: |Δr_d| < 0.5%  (EFC correction negligible at drag epoch)
    # WARN: 0.5% ≤ |Δr_d| < 1.0%  (small correction, within BAO tolerance)
    # FAIL: |Δr_d| ≥ 1.0%  (correction exceeds BAO precision, proxy invalid)
    if safety_level == "fail":
        verdict = "FAIL"
    elif safety_level == "warning":
        verdict = "WARN"
    else:
        verdict = "PASS"

    dt = _time.time() - t0
    print(f"  N6 VERDICT: {verdict} ({dt:.1f}s)")

    return {
        "rd_efc_mean": rd_efc_mean,
        "rd_efc_std": rd_efc_std,
        "rd_gr_mean": rd_gr_mean,
        "rd_gr_std": rd_gr_std,
        "delta_rd_pct_mean": delta_mean,
        "delta_rd_pct_std": delta_std,
        "safety_pass": safety_pass,
        "safety_level": safety_level,
        "safety_threshold_pct": safety_threshold_pct,
        "R_at_drag_mean": float(np.mean(R_drag_arr)),
        "R_peak_mean": float(np.mean(R_peak_arr)),
        "c_eff_at_drag_mean": 1.0 / (1.0 + float(np.mean(R_drag_arr))),
        "R_max": R_max,
        "sigma_ln_a": sigma_ln_a,
        "Omega_b": Omega_b,
        "n_samples_evaluated": len(Om_sub),
        "sweep_results": sweep_results,
        "verdict": verdict,
        "total_time_seconds": dt,
    }


# ═══════════════════════════════════════════════════════════════
#  N7: POWER-LAW GATE DIAGNOSTIC (n=2, Lorentzian-derived from L0)
# ═══════════════════════════════════════════════════════════════
#
# Tests whether α-signal survives when the logistic gate is replaced
# by the ontologically correct power-law gate g(a) = 1/(1+(a_t/a)²).
# Compares logistic vs power-law: if α differs significantly, the
# signal is gate-shape dependent and not robust.

# ── N7: Growth ODE with power-law gate ─────────────────────────

def _growth_rhs_n7(a, D, Dp, Om, alpha):
    """RHS of growth ODE with power-law gate (fixed a_t, n=2)."""
    E2 = e_squared_n7(a, Om, alpha)
    E_a = jnp.sqrt(jnp.maximum(E2, 1e-30))
    dE2_da = de_squared_da_n7(a, Om, alpha)
    dE_da = dE2_da / (2.0 * E_a)
    friction = 3.0 / a + dE_da / E_a
    source = 1.5 * Om / (a**5.0 * E2)
    return Dp, -friction * Dp + source * D


def _solve_growth_raw_n7(Om, alpha, a_eval):
    """Raw growth ODE solver with power-law gate (no custom gradients)."""
    a_grid = jnp.linspace(A_INI, 1.0, N_ODE_STEPS + 1)
    h = (1.0 - A_INI) / N_ODE_STEPS
    D0 = A_INI
    Dp0 = 1.0

    def rk4_step(state, a):
        D, Dp = state
        k1_D, k1_Dp = _growth_rhs_n7(a, D, Dp, Om, alpha)
        k2_D, k2_Dp = _growth_rhs_n7(a + h/2, D + h/2*k1_D, Dp + h/2*k1_Dp, Om, alpha)
        k3_D, k3_Dp = _growth_rhs_n7(a + h/2, D + h/2*k2_D, Dp + h/2*k2_Dp, Om, alpha)
        k4_D, k4_Dp = _growth_rhs_n7(a + h, D + h*k3_D, Dp + h*k3_Dp, Om, alpha)
        D_new = D + (h/6) * (k1_D + 2*k2_D + 2*k3_D + k4_D)
        Dp_new = Dp + (h/6) * (k1_Dp + 2*k2_Dp + 2*k3_Dp + k4_Dp)
        return (D_new, Dp_new), (D_new, Dp_new)

    _, (D_all, Dp_all) = jax.lax.scan(rk4_step, (D0, Dp0), a_grid[:-1])
    D_full = jnp.concatenate([jnp.array([D0]), D_all])
    Dp_full = jnp.concatenate([jnp.array([Dp0]), Dp_all])
    D_vals = jnp.interp(a_eval, a_grid, D_full)
    Dp_vals = jnp.interp(a_eval, a_grid, Dp_full)
    D_at_1 = D_full[-1]
    return D_vals, Dp_vals, D_at_1


@jax.custom_vjp
def solve_growth_rk4_n7(Om, alpha, a_eval):
    """Growth ODE with power-law gate + custom VJP (2 params: Om, alpha)."""
    return _solve_growth_raw_n7(Om, alpha, a_eval)


def _solve_growth_fwd_n7(Om, alpha, a_eval):
    result = _solve_growth_raw_n7(Om, alpha, a_eval)
    return result, (Om, alpha, a_eval, result)


def _solve_growth_bwd_n7(res, g):
    """Finite-difference gradients for Om, alpha (power-law gate)."""
    Om, alpha, a_eval, (D_vals, Dp_vals, D_at_1) = res
    g_D, g_Dp, g_D1 = g

    eps = 1e-5

    def _grad_for_param(param_idx, eps_val):
        args = [Om, alpha]
        args_p = list(args); args_p[param_idx] = args_p[param_idx] + eps_val
        args_m = list(args); args_m[param_idx] = args_m[param_idx] - eps_val
        D_p, Dp_p, D1_p = _solve_growth_raw_n7(*args_p, a_eval)
        D_m, Dp_m, D1_m = _solve_growth_raw_n7(*args_m, a_eval)
        dD = (D_p - D_m) / (2 * eps_val)
        dDp = (Dp_p - Dp_m) / (2 * eps_val)
        dD1 = (D1_p - D1_m) / (2 * eps_val)
        return jnp.sum(g_D * dD) + jnp.sum(g_Dp * dDp) + g_D1 * dD1

    grad_Om = _grad_for_param(0, eps)
    grad_alpha = _grad_for_param(1, eps)
    grad_a_eval = jnp.zeros_like(a_eval)

    return grad_Om, grad_alpha, grad_a_eval


solve_growth_rk4_n7.defvjp(_solve_growth_fwd_n7, _solve_growth_bwd_n7)


def compute_fs8_n7(z, Om, H0, s8, alpha):
    """f*sigma8(z) with power-law gate."""
    a_eval = 1.0 / (1.0 + z)
    D_vals, Dp_vals, D_at_1 = solve_growth_rk4_n7(Om, alpha, a_eval)
    f = a_eval * Dp_vals / jnp.maximum(D_vals, 1e-30)
    sigma8_z = s8 * D_vals / jnp.maximum(D_at_1, 1e-30)
    return f * sigma8_z


def _cumulative_comoving_n7(H0, Om, alpha):
    """Cumulative DM(z) on shared grid with power-law gate."""
    Hz_grid = Hz_n7(Z_SHARED, H0, Om, alpha)
    integrand = C_KM_S / Hz_grid
    pair_avg = 0.5 * (integrand[:-1] + integrand[1:])
    cum_dm = jnp.concatenate([jnp.array([0.0]), jnp.cumsum(pair_avg * DZ)])
    return cum_dm


# ── N7: Comoving distance predictions ──────────────────────────

def predict_bao_n7(z_eff, H0, Om, alpha, r_d, is_dh, is_dm):
    """BAO predictions with power-law gate."""
    cum_dm = _cumulative_comoving_n7(H0, Om, alpha)
    DM = jnp.interp(z_eff, Z_SHARED, cum_dm)
    a = 1.0 / (1.0 + z_eff)
    E2 = e_squared_n7(a, Om, alpha)
    Hz_val = H0 * jnp.sqrt(jnp.maximum(E2, 1e-30))
    DH = C_KM_S / Hz_val
    DV = (z_eff * DM**2 * DH)**(1.0/3.0)
    pred = jnp.where(is_dh, DH / r_d,
           jnp.where(is_dm, DM / r_d,
                     DV / r_d))
    return pred


def predict_mu_th_n7(z, H0, Om, alpha):
    """Distance modulus with power-law gate (for SNIa)."""
    cum_dm = _cumulative_comoving_n7(H0, Om, alpha)
    DM = jnp.interp(z, Z_SHARED, cum_dm)
    DL = DM * (1.0 + z)
    return 5.0 * jnp.log10(jnp.maximum(DL, 1e-10)) + 25.0


# ── N7: numpyro model ──────────────────────────────────────────

def efc_model_n7(data: 'ProbeData'):
    """EFC model with power-law gate (n=2 locked from L0).

    Same parameter space as baseline (Om, H0, s8, alpha) — only the
    gate function changes from logistic to power-law.
    """
    z_Om = numpyro.sample("z_Om", dist.Normal(0, 1))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0, 1))
    z_s8 = numpyro.sample("z_s8", dist.Normal(0, 1))
    z_alpha = numpyro.sample("z_alpha", dist.Normal(0, 1))

    Om = 0.315 + 0.03 * z_Om
    H0 = 67.4 + 3.0 * z_H0
    s8 = 0.80 + 0.04 * z_s8
    alpha = 0.0 + 3.0 * z_alpha

    numpyro.factor("Om_bound", -1e6 * jnp.where((Om > 0.1) & (Om < 0.6), 0.0, 1.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 > 50) & (H0 < 90), 0.0, 1.0))
    numpyro.factor("s8_bound", -1e6 * jnp.where((s8 > 0.5) & (s8 < 1.2), 0.0, 1.0))

    r_d = RD_FIXED

    ll_bao = 0.0
    if data.bao_z is not None:
        bao_pred = predict_bao_n7(data.bao_z, H0, Om, alpha, r_d,
                                   data.bao_is_dh, data.bao_is_dm)
        ll_bao = -0.5 * jnp.sum(((data.bao_obs - bao_pred) / data.bao_err)**2)

    ll_hz = 0.0
    if data.hz_z is not None:
        hz_pred = Hz_n7(data.hz_z, H0, Om, alpha)
        ll_hz = -0.5 * jnp.sum(((data.hz_obs - hz_pred) / data.hz_err)**2)

    ll_growth = 0.0
    if data.growth_z is not None:
        fs8_pred = compute_fs8_n7(data.growth_z, Om, H0, s8, alpha)
        ll_growth = -0.5 * jnp.sum(((data.growth_obs - fs8_pred) / data.growth_err)**2)

    ll_snia = 0.0
    if data.snia_z is not None:
        mu_th = predict_mu_th_n7(data.snia_z, H0, Om, alpha)
        M_B = numpyro.sample("M_B", dist.Normal(-19.3, 0.1))
        mu_shifted = mu_th + (M_B - (-19.3))
        ll_snia = -0.5 * jnp.sum(((data.snia_obs - mu_shifted) / data.snia_err)**2)

    numpyro.factor("log_likelihood", ll_bao + ll_hz + ll_growth + ll_snia)


# ── N7: Runner ──────────────────────────────────────────────────

def run_n7_nuts(
    data: 'ProbeData' = None,
    num_warmup: int = 500,
    num_samples: int = 2000,
    num_chains: int = 2,
    seed: int = 42,
) -> dict:
    """Run N7 power-law gate diagnostic: logistic vs power-law gate comparison.

    Tests:
    1. EFC with power-law gate (n=2 from L0)
    2. LCDM (control)
    3. Compare α-significance between logistic baseline and power-law

    Returns dict with verdict: PASS/COLLAPSED/MARGINAL
    """
    import time as _time

    if data is None:
        data = load_data()

    t0 = _time.time()
    print("\n" + "=" * 60)
    print("N7: Power-law gate diagnostic (n=2, Lorentzian-derived)")
    print("=" * 60)

    target_accept = 0.8

    # ── 1. Run EFC with power-law gate ──
    print("\n--- N7: EFC power-law gate (n=2) ---")
    mcmc_n7, samples_n7, dt_n7, ll_n7 = _run_single_nuts(
        efc_model_n7, data,
        num_warmup=num_warmup, num_samples=num_samples,
        num_chains=num_chains, seed=seed,
        target_accept=target_accept,
    )

    # ── 2. Run LCDM (reuse standard lcdm_model) ──
    print("\n--- N7: LCDM reference ---")
    mcmc_lcdm, samples_lcdm, dt_lcdm, ll_lcdm = _run_single_nuts(
        lcdm_model, data,
        num_warmup=num_warmup, num_samples=num_samples,
        num_chains=num_chains, seed=seed + 100,
        target_accept=target_accept,
    )

    # ── 3. Extract alpha posterior ──
    alpha_samples = np.array(0.0 + 3.0 * samples_n7["z_alpha"])
    alpha_mean = float(np.mean(alpha_samples))
    alpha_std = float(np.std(alpha_samples))
    alpha_sig = abs(alpha_mean) / max(alpha_std, 1e-8)
    p_neg = float(np.mean(alpha_samples < 0))

    # ── 3b. Gate-mass normalized amplitude (A_eff) ──
    # Critical for cross-gate comparison: raw α is NOT comparable between
    # logistic and power-law because gate masses differ (~14%).
    # A_eff = α · G where G = mean(gate(a_i)) over data redshifts.
    # A_eff IS comparable across gate classes.
    a_data = np.sort(1.0 / (1.0 + np.array(A_GRID)))  # data scale factors
    g_pl_data = 1.0 / (1.0 + (float(A_T) / np.maximum(a_data, 1e-10)) ** N7_N_POWER)
    gate_mass_pl = float(np.mean(g_pl_data))
    # Logistic gate mass for reference
    x_log = (a_data - float(A_T)) / float(DELTA_A)
    x_log = np.clip(x_log, -50, 50)
    g_log_data = 1.0 / (1.0 + np.exp(-x_log))
    gate_mass_logistic = float(np.mean(g_log_data))

    A_eff_samples = alpha_samples * gate_mass_pl
    A_eff_mean = float(np.mean(A_eff_samples))
    A_eff_std = float(np.std(A_eff_samples))
    A_eff_sig = abs(A_eff_mean) / max(A_eff_std, 1e-8)

    # Convergence diagnostics
    summary_n7 = numpyro.diagnostics.summary(mcmc_n7.get_samples(group_by_chain=True))
    n_effs = [float(v["n_eff"]) for v in summary_n7.values() if "n_eff" in v]
    r_hats = [float(v["r_hat"]) for v in summary_n7.values() if "r_hat" in v]
    n_eff_min = min(n_effs) if n_effs else 0.0
    r_hat_max = max(r_hats) if r_hats else 99.0

    # ── 4. Model comparison ──
    n_data = data.n_total if hasattr(data, 'n_total') else 70
    n_params_efc = 4  # Om, H0, s8, alpha
    n_params_lcdm = 3  # Om, H0, s8
    chi2_efc = -2.0 * ll_n7
    chi2_lcdm = -2.0 * ll_lcdm
    aic_efc = chi2_efc + 2 * n_params_efc
    aic_lcdm = chi2_lcdm + 2 * n_params_lcdm
    bic_efc = chi2_efc + n_params_efc * np.log(n_data)
    bic_lcdm = chi2_lcdm + n_params_lcdm * np.log(n_data)
    daic = float(aic_efc - aic_lcdm)
    dbic = float(bic_efc - bic_lcdm)

    # ── 5. Verdict ──
    # PASS:      α survives at ≥1.5σ with power-law gate
    # COLLAPSED: α drops below 1.0σ → signal is gate-shape dependent
    # MARGINAL:  between 1.0σ and 1.5σ → inconclusive
    if alpha_sig >= 1.5:
        verdict = "PASS"
    elif alpha_sig < 1.0:
        verdict = "COLLAPSED"
    else:
        verdict = "MARGINAL"

    dt = _time.time() - t0

    print(f"\n--- N7 Results ---")
    print(f"  Power-law gate: α = {alpha_mean:.3f} ± {alpha_std:.3f} ({alpha_sig:.2f}σ)")
    print(f"  A_eff (gate-normalized): {A_eff_mean:.3f} ± {A_eff_std:.3f} ({A_eff_sig:.2f}σ)")
    print(f"  Gate mass: power-law={gate_mass_pl:.4f}, logistic={gate_mass_logistic:.4f} (ratio={gate_mass_pl/gate_mass_logistic:.3f})")
    print(f"  p(α < 0) = {p_neg:.3f}")
    print(f"  ΔAIC = {daic:.2f}, ΔBIC = {dbic:.2f}")
    print(f"  Verdict: {verdict}")
    print(f"  Time: {dt:.1f}s")

    return {
        "alpha_mean": alpha_mean,
        "alpha_std": alpha_std,
        "alpha_significance": alpha_sig,
        "alpha_p_negative": p_neg,
        "A_eff_mean": A_eff_mean,
        "A_eff_std": A_eff_std,
        "A_eff_significance": A_eff_sig,
        "gate_mass_powerlaw": gate_mass_pl,
        "gate_mass_logistic": gate_mass_logistic,
        "gate_mass_ratio": gate_mass_pl / max(gate_mass_logistic, 1e-8),
        "daic": daic,
        "dbic": dbic,
        "gate_type": "power_law",
        "gate_n": N7_N_POWER,
        "gate_a_t": float(A_T),
        "n_eff_min": n_eff_min,
        "r_hat_max": r_hat_max,
        "verdict": verdict,
        "total_time_seconds": dt,
    }


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
#  N7-GRAV: Global Parameter-Lock Cross-Probe ("Domstolen")
# ═══════════════════════════════════════════════════════════════
#
# Couples the EFC-GRAV discrete gravity sector into the cosmological
# likelihood via G_eff(k,a)/G = 1 + (C²−1)·gate(a)·screen(k_eff).
#
# FROZEN from GRAV sector:
#   C = 2.32 (KT2 prefactor), k_lambda = 0.0014 h/Mpc (Hubble screening)
#   k_eff = 0.1 h/Mpc (fσ₈ representative scale)
#   a_t = 0.5, delta_a = 0.1 (standard gate)
#
# FREE MCMC parameters: Omega_m, H0, sigma8, alpha_cosmo (4 params)
#
# Physics:
#   - E²(a): Same as baseline VariantA (logistic gate, α deformation)
#   - Growth source: (3/2) · G_eff(k_eff, a)/G · Ωm / (a⁵ · E²)
#   - G_eff enters ONLY in growth (Poisson source), NOT in background
#   - This is the "Hubble friction + GRAV source" channel

# GRAV frozen constants
_GRAV_C = 2.32              # from KT2 convergence
_GRAV_K_LAMBDA = 0.0014     # h/Mpc, Hubble-scale screening
_GRAV_K_EFF = 0.1           # h/Mpc, fσ₈ representative scale
_GRAV_SCREEN = 1.0 / (1.0 + (_GRAV_K_EFF / _GRAV_K_LAMBDA) ** 2)  # ≈ 0.000196


def g_eff_over_G_jax(a):
    """G_eff(k_eff, a) / G in JAX — uses standard logistic gate.

    G_eff / G = 1 + (C² − 1) · gate(a) · screen(k_eff)

    All GRAV parameters are frozen constants.
    Returns array of same shape as a.
    """
    gate_a = gate(a)  # reuse baseline logistic gate
    return 1.0 + (_GRAV_C ** 2 - 1.0) * gate_a * _GRAV_SCREEN


def _growth_rhs_grav(a, D, Dp, Om, alpha):
    """RHS of growth ODE with GRAV-locked G_eff in source term.

    source = (3/2) · G_eff(k_eff, a)/G · Ωm / (a⁵ · E²)
    friction = 3/a + E'(a)/E(a)

    E²(a) is the standard EFC expansion (same as baseline).
    G_eff modifies ONLY the source (Poisson equation side).
    """
    E2 = e_squared(a, Om, alpha)
    E_a = jnp.sqrt(jnp.maximum(E2, 1e-30))
    dE2_da_val = de_squared_da(a, Om, alpha)
    dE_da = dE2_da_val / (2.0 * E_a)

    friction = 3.0 / a + dE_da / E_a

    # G_eff modification of Poisson source
    geff = g_eff_over_G_jax(a)
    source = 1.5 * geff * Om / (a**5.0 * E2)

    return Dp, -friction * Dp + source * D


def _solve_growth_raw_grav(Om, alpha, a_eval):
    """Raw growth ODE solver with GRAV G_eff (no custom gradients).

    Uses fixed-step RK4 via jax.lax.scan, same structure as baseline.
    """
    a_grid = jnp.linspace(A_INI, 1.0, N_ODE_STEPS + 1)
    h = (1.0 - A_INI) / N_ODE_STEPS

    D0 = A_INI
    Dp0 = 1.0

    def rk4_step(state, a):
        D, Dp = state
        k1_D, k1_Dp = _growth_rhs_grav(a, D, Dp, Om, alpha)
        k2_D, k2_Dp = _growth_rhs_grav(a + h/2, D + h/2*k1_D, Dp + h/2*k1_Dp, Om, alpha)
        k3_D, k3_Dp = _growth_rhs_grav(a + h/2, D + h/2*k2_D, Dp + h/2*k2_Dp, Om, alpha)
        k4_D, k4_Dp = _growth_rhs_grav(a + h, D + h*k3_D, Dp + h*k3_Dp, Om, alpha)
        D_new = D + (h/6) * (k1_D + 2*k2_D + 2*k3_D + k4_D)
        Dp_new = Dp + (h/6) * (k1_Dp + 2*k2_Dp + 2*k3_Dp + k4_Dp)
        return (D_new, Dp_new), (D_new, Dp_new)

    _, (D_all, Dp_all) = jax.lax.scan(rk4_step, (D0, Dp0), a_grid[:-1])

    D_full = jnp.concatenate([jnp.array([D0]), D_all])
    Dp_full = jnp.concatenate([jnp.array([Dp0]), Dp_all])

    D_vals = jnp.interp(a_eval, a_grid, D_full)
    Dp_vals = jnp.interp(a_eval, a_grid, Dp_full)
    D_at_1 = D_full[-1]

    return D_vals, Dp_vals, D_at_1


@jax.custom_vjp
def solve_growth_rk4_grav(Om, alpha, a_eval):
    """Growth ODE with GRAV G_eff + custom VJP (2 params: Om, alpha)."""
    return _solve_growth_raw_grav(Om, alpha, a_eval)


def _solve_growth_fwd_grav(Om, alpha, a_eval):
    result = _solve_growth_raw_grav(Om, alpha, a_eval)
    return result, (Om, alpha, a_eval, result)


def _solve_growth_bwd_grav(res, g):
    """Finite-difference gradients for Om, alpha (GRAV growth)."""
    Om, alpha, a_eval, (D_vals, Dp_vals, D_at_1) = res
    g_D, g_Dp, g_D1 = g

    eps = 1e-5

    def _grad_for_param(param_idx, eps_val):
        args = [Om, alpha]
        args_p = list(args); args_p[param_idx] = args_p[param_idx] + eps_val
        args_m = list(args); args_m[param_idx] = args_m[param_idx] - eps_val
        D_p, Dp_p, D1_p = _solve_growth_raw_grav(*args_p, a_eval)
        D_m, Dp_m, D1_m = _solve_growth_raw_grav(*args_m, a_eval)
        dD = (D_p - D_m) / (2 * eps_val)
        dDp = (Dp_p - Dp_m) / (2 * eps_val)
        dD1 = (D1_p - D1_m) / (2 * eps_val)
        return jnp.sum(g_D * dD) + jnp.sum(g_Dp * dDp) + g_D1 * dD1

    grad_Om = _grad_for_param(0, eps)
    grad_alpha = _grad_for_param(1, eps)
    grad_a_eval = jnp.zeros_like(a_eval)

    return grad_Om, grad_alpha, grad_a_eval


solve_growth_rk4_grav.defvjp(_solve_growth_fwd_grav, _solve_growth_bwd_grav)


def compute_fs8_grav(z, Om, H0, s8, alpha):
    """f*sigma8(z) with GRAV G_eff in growth source."""
    a_eval = 1.0 / (1.0 + z)
    D_vals, Dp_vals, D_at_1 = solve_growth_rk4_grav(Om, alpha, a_eval)
    f = a_eval * Dp_vals / jnp.maximum(D_vals, 1e-30)
    sigma8_z = s8 * D_vals / jnp.maximum(D_at_1, 1e-30)
    return f * sigma8_z


# ── N7-GRAV: numpyro model ──────────────────────────────────────

def efc_model_n7_grav(data: 'ProbeData'):
    """EFC model with GRAV-locked G_eff in growth source.

    Same parameter space as baseline (Om, H0, s8, alpha).
    Background expansion: standard EFC logistic gate (baseline).
    Growth: G_eff(k_eff, a)/G modifies source term.

    Priors: D3 honest σ8 ~ N(0.80, 0.04).
    """
    # ── Reparameterized priors (same as baseline) ──
    z_Om = numpyro.sample("z_Om", dist.Normal(0, 1))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0, 1))
    z_s8 = numpyro.sample("z_s8", dist.Normal(0, 1))
    z_alpha = numpyro.sample("z_alpha", dist.Normal(0, 1))

    Om = 0.315 + 0.03 * z_Om
    H0 = 67.4 + 3.0 * z_H0
    s8 = 0.80 + 0.04 * z_s8      # D3 honest prior
    alpha = 0.0 + 3.0 * z_alpha

    # Flat bounds (soft penalty)
    numpyro.factor("Om_bound", -1e6 * jnp.where((Om > 0.1) & (Om < 0.6), 0.0, 1.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 > 50.0) & (H0 < 85.0), 0.0, 1.0))
    numpyro.factor("s8_bound", -1e6 * jnp.where((s8 > 0.5) & (s8 < 1.2), 0.0, 1.0))
    numpyro.factor("alpha_bound", -1e6 * jnp.where((alpha > -10.0) & (alpha < 10.0), 0.0, 1.0))

    r_d = RD_FIXED

    # ── BAO likelihood (uses standard background, no G_eff) ──
    if data.bao_z is not None and len(data.bao_z) > 0:
        pred_bao = predict_bao(data.bao_z, H0, Om, alpha, r_d,
                               data.bao_is_dh, data.bao_is_dm, data.bao_is_dv)
        numpyro.sample("bao_obs", dist.Normal(pred_bao, data.bao_err),
                        obs=data.bao_obs)

    # ── H(z) likelihood (uses standard background, no G_eff) ──
    if data.hz_z is not None and len(data.hz_z) > 0:
        pred_hz = Hz(data.hz_z, H0, Om, alpha)
        numpyro.sample("hz_obs", dist.Normal(pred_hz, data.hz_err),
                        obs=data.hz_obs)

    # ── Growth (fσ8) — uses GRAV G_eff in source term ──
    if data.growth_z is not None and len(data.growth_z) > 0:
        pred_fs8 = compute_fs8_grav(data.growth_z, Om, H0, s8, alpha)
        numpyro.sample("growth_obs", dist.Normal(pred_fs8, data.growth_err),
                        obs=data.growth_obs)

    # ── SNIa likelihood (uses standard background, no G_eff) ──
    if data.snia_z is not None and len(data.snia_z) > 0:
        mu_th = predict_mu_th(data.snia_z, H0, Om, alpha)
        M_B = numpyro.sample("M_B", dist.Normal(-19.3, 0.1))
        mu_obs_shifted = data.snia_mu - M_B
        if data.snia_cov is not None:
            numpyro.sample("snia_obs",
                           dist.MultivariateNormal(mu_th, covariance_matrix=data.snia_cov),
                           obs=mu_obs_shifted)
        else:
            numpyro.sample("snia_obs",
                           dist.Normal(mu_th, data.snia_err),
                           obs=mu_obs_shifted)

    # ── Deterministic outputs ──
    numpyro.deterministic("Om", Om)
    numpyro.deterministic("H0", H0)
    numpyro.deterministic("s8", s8)
    numpyro.deterministic("alpha", alpha)


# ═══════════════════════════════════════════════════════════════
#  VARIANT-G: CONSTITUTIVE LAW GROWTH-ONLY (JAX)
# ═══════════════════════════════════════════════════════════════

# Pre-compute chi(z) table as JAX arrays (deterministic, cycle-independent).
# Uses same sources as efc_inference/data/chi_of_z_axiom0.py.
# Loaded once at module import — NO dependency on MCMC cycles.

def _build_chi_table_jax():
    """Build deterministic chi(z) table as JAX arrays.

    Returns (z_grid, chi_vals, chi_c, epsilon_eff) — all JAX arrays/scalars.
    """
    try:
        from efc_inference.data.chi_of_z_axiom0 import (
            get_chi_table, CHI_C, EPSILON_KT2,
        )
        z_np, _, chi_np = get_chi_table()
        _z = jnp.array(z_np)
        _chi = jnp.array(chi_np)
        _chi_c = float(CHI_C)
        _eps_local = float(EPSILON_KT2)  # C^2 - 1 = 4.3824
        _screen = 1.0 / (1.0 + (_GRAV_K_EFF / _GRAV_K_LAMBDA) ** 2)
        _eps_eff = _eps_local * _screen
        return _z, _chi, _chi_c, _eps_eff
    except Exception as e:
        print(f"WARNING: Could not load chi table for VariantG: {e}")
        # Fallback: mu(z) = 1 everywhere (degrades to LCDM)
        _z = jnp.linspace(0.001, 3.0, 1000)
        _chi = jnp.zeros(1000)
        return _z, _chi, 1.0, 0.0


_VG_Z, _VG_CHI, _VG_CHI_C, _VG_EPS_EFF = _build_chi_table_jax()
_VG_HILL_N = 2  # locked


def _set_variant_g_k_eff(k_eff: float):
    """Reconfigure VariantG module globals for a different k_eff scenario.

    Must be called BEFORE run_variant_g_nuts() — changes module-level
    constants that the JIT-compiled mu/growth functions capture via closure.

    JAX will re-trace if needed (first call per k_eff value is slower).
    """
    global _GRAV_K_EFF, _GRAV_SCREEN, _VG_EPS_EFF
    _GRAV_K_EFF = k_eff
    _GRAV_SCREEN = 1.0 / (1.0 + (k_eff / _GRAV_K_LAMBDA) ** 2)
    # Recompute eps_eff with new screening
    from efc_inference.data.chi_of_z_axiom0 import EPSILON_KT2
    _VG_EPS_EFF = float(EPSILON_KT2) * _GRAV_SCREEN
    # Clear JAX compilation cache so new constants are picked up.
    # Global floats used as literals in traced functions will trigger re-compilation.
    try:
        jax.clear_caches()
    except Exception:
        pass  # Older JAX versions may not have clear_caches
    print(f"  VariantG k_eff reconfigured: k_eff={k_eff}, screen={_GRAV_SCREEN:.8f}, eps_eff={_VG_EPS_EFF:.8f}")


def _mu_of_a_variant_g(a):
    """mu(a) for VariantG: constitutive law from entropy gradients.

    mu(z) = 1 + eps_eff * F(chi(z))
    F(chi) = chi^n / (chi^n + chi_c^n)

    All parameters frozen. Zero free parameters.
    """
    z = 1.0 / a - 1.0
    z = jnp.clip(z, 0.0, 3.0)
    chi = jnp.interp(z, _VG_Z, _VG_CHI)
    chi_n = chi ** _VG_HILL_N
    chi_c_n = _VG_CHI_C ** _VG_HILL_N
    F = chi_n / (chi_n + chi_c_n + 1e-30)
    return 1.0 + _VG_EPS_EFF * F


def _growth_rhs_variant_g(a, D, Dp, Om):
    """RHS of growth ODE with VariantG mu(z) in source term.

    Background: pure LCDM (no alpha, no gate).
    Source: (3/2) * mu(a) * Om / (a^5 * E^2)
    """
    E2 = e_squared_lcdm(a, Om)
    E_a = jnp.sqrt(jnp.maximum(E2, 1e-30))
    dE2_da_val = -3.0 * Om * a**(-4.0)  # pure LCDM
    dE_da = dE2_da_val / (2.0 * E_a)

    friction = 3.0 / a + dE_da / E_a

    mu = _mu_of_a_variant_g(a)
    source = 1.5 * mu * Om / (a**5.0 * E2)

    return Dp, -friction * Dp + source * D


def _solve_growth_raw_variant_g(Om, a_eval):
    """Raw growth ODE solver with VariantG mu (1 free param: Om)."""
    a_grid = jnp.linspace(A_INI, 1.0, N_ODE_STEPS + 1)
    h = (1.0 - A_INI) / N_ODE_STEPS

    D0 = A_INI
    Dp0 = 1.0

    def rk4_step(state, a):
        D, Dp = state
        k1_D, k1_Dp = _growth_rhs_variant_g(a, D, Dp, Om)
        k2_D, k2_Dp = _growth_rhs_variant_g(a + h/2, D + h/2*k1_D, Dp + h/2*k1_Dp, Om)
        k3_D, k3_Dp = _growth_rhs_variant_g(a + h/2, D + h/2*k2_D, Dp + h/2*k2_Dp, Om)
        k4_D, k4_Dp = _growth_rhs_variant_g(a + h, D + h*k3_D, Dp + h*k3_Dp, Om)
        D_new = D + (h/6) * (k1_D + 2*k2_D + 2*k3_D + k4_D)
        Dp_new = Dp + (h/6) * (k1_Dp + 2*k2_Dp + 2*k3_Dp + k4_Dp)
        return (D_new, Dp_new), (D_new, Dp_new)

    _, (D_all, Dp_all) = jax.lax.scan(rk4_step, (D0, Dp0), a_grid[:-1])

    D_full = jnp.concatenate([jnp.array([D0]), D_all])
    Dp_full = jnp.concatenate([jnp.array([Dp0]), Dp_all])

    D_vals = jnp.interp(a_eval, a_grid, D_full)
    Dp_vals = jnp.interp(a_eval, a_grid, Dp_full)
    D_at_1 = D_full[-1]

    return D_vals, Dp_vals, D_at_1


@jax.custom_vjp
def solve_growth_rk4_variant_g(Om, a_eval):
    """Growth ODE with VariantG mu + custom VJP (1 param: Om)."""
    return _solve_growth_raw_variant_g(Om, a_eval)


def _solve_growth_fwd_variant_g(Om, a_eval):
    result = _solve_growth_raw_variant_g(Om, a_eval)
    return result, (Om, a_eval)


def _solve_growth_bwd_variant_g(res, g):
    """Finite-difference gradient for Om (VariantG growth)."""
    Om, a_eval = res
    g_D, g_Dp, g_D1 = g

    eps = 1e-5
    D_p, Dp_p, D1_p = _solve_growth_raw_variant_g(Om + eps, a_eval)
    D_m, Dp_m, D1_m = _solve_growth_raw_variant_g(Om - eps, a_eval)
    dD = (D_p - D_m) / (2 * eps)
    dDp = (Dp_p - Dp_m) / (2 * eps)
    dD1 = (D1_p - D1_m) / (2 * eps)
    grad_Om = jnp.sum(g_D * dD) + jnp.sum(g_Dp * dDp) + g_D1 * dD1

    grad_a_eval = jnp.zeros_like(a_eval)
    return grad_Om, grad_a_eval


solve_growth_rk4_variant_g.defvjp(
    _solve_growth_fwd_variant_g, _solve_growth_bwd_variant_g
)


def compute_fs8_variant_g(z, Om, H0, s8):
    """f*sigma8(z) with VariantG mu(z) in growth source."""
    a_eval = 1.0 / (1.0 + z)
    D_vals, Dp_vals, D_at_1 = solve_growth_rk4_variant_g(Om, a_eval)
    f = a_eval * Dp_vals / jnp.maximum(D_vals, 1e-30)
    sigma8_z = s8 * D_vals / jnp.maximum(D_at_1, 1e-30)
    return f * sigma8_z


def variant_g_model(data: 'ProbeData'):
    """Numpyro model for VariantG: 3 params [Om, H0, s8].

    Background: pure LCDM (no alpha, no gate).
    Growth: mu(z) from constitutive law (entropy gradients).
    BAO, Hz, SNIa: pure LCDM (no mu modification).

    This is IDENTICAL to lcdm_model except growth uses VariantG mu.
    D3 honest σ8 ~ N(0.80, 0.04) prior.
    """
    z_Om = numpyro.sample("z_Om", dist.Normal(0.0, 1.0))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0.0, 1.0))
    z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))

    Om = 0.30 + 0.05 * z_Om
    H0 = 67.5 + 5.0 * z_H0
    s8 = 0.80 + 0.04 * z_s8    # D3: honest prior

    numpyro.factor("Om_bound", -1e6 * jnp.where((Om < 0.05) | (Om > 0.8), 1.0, 0.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 < 40.0) | (H0 > 100.0), 1.0, 0.0))

    r_d = RD_FIXED

    # ── BAO: pure LCDM (no mu modification) ──
    bao_pred = predict_bao_lcdm(
        data.bao_z, H0, Om, r_d,
        data.bao_is_dh, data.bao_is_dm, data.bao_is_dv,
    )
    ll_bao = bao_log_likelihood(data, bao_pred)

    # ── Hz: pure LCDM ──
    hz_pred = Hz_lcdm(data.hz_z, H0, Om)
    ll_hz = chi2_log_likelihood(data.hz_obs, hz_pred, data.hz_err)

    # ── Growth (fσ8): VariantG mu(z) in source term ──
    fs8_pred = compute_fs8_variant_g(data.growth_z, Om, H0, s8)
    ll_growth = chi2_log_likelihood(data.growth_obs, fs8_pred, data.growth_err)

    # ── SNIa: pure LCDM ──
    mu_th = predict_mu_th_lcdm(data.snia_z, H0, Om)
    ll_snia = snia_log_likelihood(
        mu_th, data.snia_mb,
        data.snia_cov_inv, data.snia_cov_logdet,
    )

    numpyro.factor("log_likelihood", ll_bao + ll_hz + ll_growth + ll_snia)

    numpyro.deterministic("Om", Om)
    numpyro.deterministic("H0", H0)
    numpyro.deterministic("s8", s8)


def run_variant_g_nuts(
    data: 'ProbeData' = None,
    num_warmup: int = 500,
    num_samples: int = 2000,
    num_chains: int = 2,
    seed: int = 42,
    target_accept: float = 0.8,
    bao_path: str = None,
    growth_path: str = None,
    hz_path: str = None,
    snia_path: str = None,
    snia_cov_path: str = None,
    k_eff: float = None,
    scenario: str = None,
) -> dict:
    """Run VariantG diagnostic via NUTS: 3-param [Om, H0, s8].

    Compares VariantG (mu from chi) vs LCDM (mu=1).
    Both 3-param — same freedom, only growth source differs.

    Args:
        k_eff: Override k_eff (h/Mpc). If None, uses current module default.
        scenario: Named scenario ("G10", "G02", "G01"). Overrides k_eff.

    Returns dict with ΔlogL, mu_diagnostics, verdict.
    """
    import arviz as az

    # Resolve scenario → k_eff and reconfigure module globals
    from efc_inference.core.cosmology_model import EFCVariantG
    if scenario:
        if scenario not in EFCVariantG.SCENARIOS:
            raise ValueError(f"Unknown scenario '{scenario}'. Use: {list(EFCVariantG.SCENARIOS.keys())}")
        _set_variant_g_k_eff(EFCVariantG.SCENARIOS[scenario])
        scenario_name = scenario
    elif k_eff is not None:
        _set_variant_g_k_eff(k_eff)
        scenario_name = f"k{k_eff}"
    else:
        scenario_name = "G10"  # default (uses module-level k_eff=0.1)

    print("=" * 60)
    print(f"VARIANT-G: Constitutive Law Growth Diagnostic (NUTS) [{scenario_name}]")
    print(f"  eps_eff={_VG_EPS_EFF:.8f}, chi_c={_VG_CHI_C:.6f}")
    print(f"  C={_GRAV_C}, k_lambda={_GRAV_K_LAMBDA}, k_eff={_GRAV_K_EFF}")
    print(f"  mu(a=1) = {float(_mu_of_a_variant_g(jnp.array(1.0))):.8f}")
    print(f"  mu(a=0.5) = {float(_mu_of_a_variant_g(jnp.array(0.5))):.8f}")
    print("=" * 60)

    if data is None:
        data = load_data(
            bao_path=bao_path or "efc_inference/data/bao/bao_starter.csv",
            growth_path=growth_path or "efc_inference/data/growth/fs8_extended.csv",
            hz_path=hz_path or "efc_inference/data/hubble/hz_cosmic_chronometers.csv",
            snia_path=snia_path or "efc_inference/data/snia/pantheon_binned.csv",
            snia_cov_path=snia_cov_path or "efc_inference/data/snia/pantheon_binned_covtotal.npy",
        )

    print(f"Data: {data.n_total} points")

    # ── 1. Run VariantG (mu from chi) ──
    print(f"\n--- VariantG: 3p [Om, H0, s8] with mu(z) ---")
    rng_key = jax.random.PRNGKey(seed + 900)
    kernel = NUTS(variant_g_model, dense_mass=True, target_accept_prob=target_accept)
    mcmc = MCMC(kernel, num_warmup=num_warmup, num_samples=num_samples,
                num_chains=num_chains, progress_bar=True)

    t0 = time.time()
    mcmc.run(rng_key, data=data)
    dt_vg = time.time() - t0

    samples_vg = mcmc.get_samples()
    # VariantG uses numpyro.deterministic() for Om/H0/s8 — transform from z_* samples
    om_vg = np.array(0.30 + 0.05 * samples_vg["z_Om"])
    h0_vg = np.array(67.5 + 5.0 * samples_vg["z_H0"])
    s8_vg = np.array(0.80 + 0.04 * samples_vg["z_s8"])

    # ── 2. Run LCDM reference ──
    print(f"\n--- LCDM reference: 3p [Om, H0, s8] with mu=1 ---")
    rng_key_lcdm = jax.random.PRNGKey(seed + 901)
    kernel_lcdm = NUTS(lcdm_model, dense_mass=True, target_accept_prob=target_accept)
    mcmc_lcdm = MCMC(kernel_lcdm, num_warmup=num_warmup, num_samples=num_samples,
                     num_chains=num_chains, progress_bar=True)

    t0 = time.time()
    mcmc_lcdm.run(rng_key_lcdm, data=data)
    dt_lcdm = time.time() - t0

    samples_lcdm = mcmc_lcdm.get_samples()
    # LCDM model samples z_s8 (standardized) — transform to physical s8
    s8_lcdm = np.array(0.80 + 0.04 * samples_lcdm["z_s8"])

    # ── Convergence ──
    try:
        idata_vg = az.from_numpyro(mcmc)
        summary_vg = az.summary(idata_vg, var_names=["z_Om", "z_H0", "z_s8"])
        n_eff_min = float(summary_vg["ess_bulk"].min())
        r_hat_max = float(summary_vg["r_hat"].max())
    except Exception:
        n_eff_min = 0
        r_hat_max = 99.0

    # ── LogL comparison ──
    try:
        pe_vg = np.array(mcmc.get_extra_fields()["potential_energy"])
        pe_lcdm = np.array(mcmc_lcdm.get_extra_fields()["potential_energy"])
        ll_max_vg = float(-np.min(pe_vg))
        ll_max_lcdm = float(-np.min(pe_lcdm))
    except Exception:
        ll_max_vg = 0.0
        ll_max_lcdm = 0.0

    dll_total = ll_max_vg - ll_max_lcdm
    daic = -2.0 * dll_total  # same k=3

    s8_shift = float(np.mean(s8_vg)) - float(np.mean(s8_lcdm))

    # ── Verdict ──
    if abs(dll_total) < 0.1:
        verdict = "UNDETECTABLE"
    elif dll_total > 1.0:
        verdict = "SIGNAL"
    elif dll_total > 0.5:
        verdict = "MARGINAL_SIGNAL"
    elif dll_total < -1.0:
        verdict = "ANTI_SIGNAL"
    else:
        verdict = "WEAK"

    print(f"\n  ΔlogL_total: {dll_total:+.4f}")
    print(f"  ΔAIC (same k=3): {daic:+.3f}")
    print(f"  σ8 shift: {s8_shift:+.4f}")
    print(f"  n_eff_min: {n_eff_min:.0f}, r_hat_max: {r_hat_max:.4f}")
    print(f"  VERDICT: {verdict}")
    print(f"  Time: VG={dt_vg:.0f}s, LCDM={dt_lcdm:.0f}s")

    mu_vals = {
        "mu_z0.3": float(_mu_of_a_variant_g(jnp.array(1.0 / 1.3))),
        "mu_z0.5": float(_mu_of_a_variant_g(jnp.array(1.0 / 1.5))),
        "mu_z0.7": float(_mu_of_a_variant_g(jnp.array(1.0 / 1.7))),
        "mu_z1.0": float(_mu_of_a_variant_g(jnp.array(0.5))),
        "mu_z1.5": float(_mu_of_a_variant_g(jnp.array(1.0 / 2.5))),
        "mu_z2.3": float(_mu_of_a_variant_g(jnp.array(1.0 / 3.3))),
    }
    mu_max = max(mu_vals.values())
    mu_min = min(mu_vals.values())

    return {
        "verdict": verdict,
        "dll_total": dll_total,
        "daic_same_k": daic,
        "s8_vg_mean": float(np.mean(s8_vg)),
        "s8_vg_std": float(np.std(s8_vg)),
        "s8_lcdm_mean": float(np.mean(s8_lcdm)),
        "s8_lcdm_std": float(np.std(s8_lcdm)),
        "s8_shift": s8_shift,
        "om_vg_mean": float(np.mean(om_vg)),
        "h0_vg_mean": float(np.mean(h0_vg)),
        "n_eff_min": n_eff_min,
        "r_hat_max": r_hat_max,
        "scenario": scenario_name,
        "k_eff": _GRAV_K_EFF,
        "mu_amp": mu_max - 1.0,
        "mu_span": mu_max - mu_min,
        "mu_diagnostics": {
            "chi_c": _VG_CHI_C,
            "epsilon_eff": _VG_EPS_EFF,
            "C_grav": _GRAV_C,
            "k_lambda": _GRAV_K_LAMBDA,
            "k_eff": _GRAV_K_EFF,
            "screen_k_eff": _GRAV_SCREEN,
            "mu_min": mu_min,
            "mu_max": mu_max,
            **mu_vals,
        },
        "total_time_seconds": dt_vg + dt_lcdm,
    }


# ═══════════════════════════════════════════════════════════════
#  VARIANT H — ENTROPY-GRADIENT GROWTH, 2 FREE PARAMETERS (NUTS)
# ═══════════════════════════════════════════════════════════════

# Reuses _VG_Z, _VG_CHI, _VG_CHI_C from VariantG (same chi(z) data)
_VH_HILL_N = 2  # locked Hill exponent


def _mu_of_a_variant_h(a, S_bar_0, beta_0):
    """mu(a) for VariantH: entropy gradients with 2 free parameters.

    mu(z) = 1 + S_bar_0 * F(chi(z); beta_0)
    F(chi) = chi^n / (chi^n + beta_0^n)   n=2

    S_bar_0 and beta_0 are MCMC-sampled (not frozen).
    chi(z) comes from the same locked Axiom 0 table as VariantG.
    """
    z = 1.0 / jnp.maximum(a, 1e-10) - 1.0
    z = jnp.clip(z, 0.0, 3.0)
    chi = jnp.interp(z, _VG_Z, _VG_CHI)
    n = _VH_HILL_N
    chi_n = chi ** n
    beta_n = beta_0 ** n + 1e-30  # guard /0
    F = chi_n / (chi_n + beta_n)
    return 1.0 + S_bar_0 * F


def _growth_rhs_variant_h(a, D, Dp, Om, S_bar_0, beta_0):
    """RHS of growth ODE with VariantH mu(z) in source term.

    Background: pure LCDM (no alpha, no gate).
    Only the growth source is modified by mu.
    """
    E2 = Om * a**(-3.0) + (1.0 - Om)
    E_a = jnp.sqrt(jnp.maximum(E2, 1e-30))
    dE2_da = -3.0 * Om * a**(-4.0)
    dE_da = dE2_da / (2.0 * E_a)

    friction = 3.0 / a + dE_da / E_a
    mu = _mu_of_a_variant_h(a, S_bar_0, beta_0)
    source = 1.5 * mu * Om / (a**5.0 * E2)

    return Dp, -friction * Dp + source * D


def _solve_growth_raw_variant_h(Om, S_bar_0, beta_0, a_eval):
    """Raw growth ODE solver with VariantH mu (3 free physics params)."""
    a_grid = jnp.linspace(A_INI, 1.0, N_ODE_STEPS + 1)
    h = (1.0 - A_INI) / N_ODE_STEPS

    def step(carry, _):
        a, D, Dp = carry
        k1_D, k1_Dp = _growth_rhs_variant_h(a, D, Dp, Om, S_bar_0, beta_0)
        k2_D, k2_Dp = _growth_rhs_variant_h(a + h/2, D + h/2*k1_D, Dp + h/2*k1_Dp, Om, S_bar_0, beta_0)
        k3_D, k3_Dp = _growth_rhs_variant_h(a + h/2, D + h/2*k2_D, Dp + h/2*k2_Dp, Om, S_bar_0, beta_0)
        k4_D, k4_Dp = _growth_rhs_variant_h(a + h, D + h*k3_D, Dp + h*k3_Dp, Om, S_bar_0, beta_0)
        D_new = D + (h/6) * (k1_D + 2*k2_D + 2*k3_D + k4_D)
        Dp_new = Dp + (h/6) * (k1_Dp + 2*k2_Dp + 2*k3_Dp + k4_Dp)
        return (a + h, D_new, Dp_new), (D_new, Dp_new)

    init = (A_INI, A_INI, 1.0)
    _, (D_all, Dp_all) = jax.lax.scan(step, init, None, length=N_ODE_STEPS)

    D_at_1 = D_all[-1]
    a_all = a_grid[1:]

    D_vals = jnp.interp(a_eval, a_all, D_all)
    Dp_vals = jnp.interp(a_eval, a_all, Dp_all)
    return D_vals, Dp_vals, D_at_1


@jax.custom_vjp
def solve_growth_rk4_variant_h(Om, S_bar_0, beta_0, a_eval):
    """Growth ODE with VariantH mu + custom VJP (3 params: Om, S_bar_0, beta_0)."""
    return _solve_growth_raw_variant_h(Om, S_bar_0, beta_0, a_eval)


def _solve_growth_fwd_variant_h(Om, S_bar_0, beta_0, a_eval):
    result = _solve_growth_raw_variant_h(Om, S_bar_0, beta_0, a_eval)
    return result, (Om, S_bar_0, beta_0, a_eval)


def _solve_growth_bwd_variant_h(res, g):
    """Finite-difference gradients for Om, S_bar_0, beta_0 (VariantH growth)."""
    Om, S_bar_0, beta_0, a_eval = res
    g_D, g_Dp, g_D1 = g

    # Gradient w.r.t. Om
    eps_om = 1e-5
    D_p, Dp_p, D1_p = _solve_growth_raw_variant_h(Om + eps_om, S_bar_0, beta_0, a_eval)
    D_m, Dp_m, D1_m = _solve_growth_raw_variant_h(Om - eps_om, S_bar_0, beta_0, a_eval)
    grad_Om = (jnp.sum(g_D * (D_p - D_m)) +
               jnp.sum(g_Dp * (Dp_p - Dp_m)) +
               g_D1 * (D1_p - D1_m)) / (2 * eps_om)

    # Gradient w.r.t. S_bar_0
    eps_s = 1e-5
    D_p, Dp_p, D1_p = _solve_growth_raw_variant_h(Om, S_bar_0 + eps_s, beta_0, a_eval)
    D_m, Dp_m, D1_m = _solve_growth_raw_variant_h(Om, S_bar_0 - eps_s, beta_0, a_eval)
    grad_S = (jnp.sum(g_D * (D_p - D_m)) +
              jnp.sum(g_Dp * (Dp_p - Dp_m)) +
              g_D1 * (D1_p - D1_m)) / (2 * eps_s)

    # Gradient w.r.t. beta_0
    eps_b = 1e-5
    D_p, Dp_p, D1_p = _solve_growth_raw_variant_h(Om, S_bar_0, beta_0 + eps_b, a_eval)
    D_m, Dp_m, D1_m = _solve_growth_raw_variant_h(Om, S_bar_0, beta_0 - eps_b, a_eval)
    grad_B = (jnp.sum(g_D * (D_p - D_m)) +
              jnp.sum(g_Dp * (Dp_p - Dp_m)) +
              g_D1 * (D1_p - D1_m)) / (2 * eps_b)

    return grad_Om, grad_S, grad_B, jnp.zeros_like(a_eval)


solve_growth_rk4_variant_h.defvjp(
    _solve_growth_fwd_variant_h, _solve_growth_bwd_variant_h
)


def compute_fs8_variant_h(z, Om, H0, s8, S_bar_0, beta_0):
    """f*sigma8(z) with VariantH mu(z) in growth source.

    Background: pure LCDM (no alpha). Only growth modified by entropy gradients.
    """
    a_eval = 1.0 / (1.0 + z)
    D_vals, Dp_vals, D_at_1 = solve_growth_rk4_variant_h(Om, S_bar_0, beta_0, a_eval)
    f = a_eval * Dp_vals / jnp.maximum(D_vals, 1e-30)
    sigma8_z = s8 * D_vals / jnp.maximum(D_at_1, 1e-30)
    return f * sigma8_z


def variant_h_model(data: 'ProbeData'):
    """Numpyro model for VariantH: 5 params [Om, H0, s8, S_bar_0, beta_0].

    Background: pure LCDM (no alpha, no gate).
    Growth: mu(z) = 1 + S_bar_0 * F(chi(z); beta_0).

    All probes (BAO, Hz, SNIa) use pure LCDM. Only fσ₈ sees mu modification.
    """
    Om = numpyro.sample("Omega_m", dist.Uniform(0.1, 0.6))
    H0 = numpyro.sample("H0", dist.Uniform(50.0, 85.0))
    s8 = numpyro.sample("sigma8", dist.TruncatedNormal(0.80, 0.04, low=0.5, high=1.2))
    S_bar_0 = numpyro.sample("S_bar_0", dist.Uniform(0.0, 0.5))
    beta_0 = numpyro.sample("beta_0", dist.Uniform(0.05, 5.0))

    # ── BAO: pure LCDM (no alpha) ──
    r_d = RD_FIXED
    bao_pred = predict_bao_lcdm(data.bao_z, H0, Om, r_d,
                                data.bao_is_dh, data.bao_is_dm, data.bao_is_dv)
    ll_bao = bao_log_likelihood(data, bao_pred)

    # ── Hz: pure LCDM ──
    Hz_pred = Hz_lcdm(data.hz_z, H0, Om)
    ll_hz = chi2_log_likelihood(data.hz_obs, Hz_pred, data.hz_err)

    # ── fσ8: VariantH mu(z) from entropy gradients ──
    fs8_pred = compute_fs8_variant_h(data.growth_z, Om, H0, s8, S_bar_0, beta_0)
    ll_growth = chi2_log_likelihood(data.growth_obs, fs8_pred, data.growth_err)

    # ── SNIa: pure LCDM ──
    mu_th = predict_mu_th_lcdm(data.snia_z, H0, Om)
    ll_snia = snia_log_likelihood(
        mu_th, data.snia_mb,
        data.snia_cov_inv, data.snia_cov_logdet,
    )

    numpyro.factor("ll_total", ll_bao + ll_hz + ll_growth + ll_snia)


def run_variant_h_nuts(
    data: 'ProbeData' = None,
    num_warmup: int = 500,
    num_samples: int = 2000,
    num_chains: int = 2,
    seed: int = 42,
    target_accept: float = 0.8,
    bao_path: str = None,
    growth_path: str = None,
    hz_path: str = None,
    snia_path: str = None,
    snia_cov_path: str = None,
) -> dict:
    """Run VariantH diagnostic: entropy-gradient growth with 2 free params via NUTS.

    Tests core EFC mechanism: ∇S → μ → fσ₈.
    Background: pure LCDM (no alpha). Only growth sector modified.

    Returns dict with posteriors, ΔlogL, ΔAIC, verdict.
    """
    print("=" * 60)
    print("VARIANT-H: ENTROPY-GRADIENT GROWTH (2 FREE PARAMS)")
    print("  Testing core EFC mechanism: ∇S → μ → fσ₈")
    print("  Free params: [Ω_m, H0, σ8, S̄₀, β₀] (5p)")
    print("  Background: pure LCDM, DR2-compatible")
    print(f"  chi_c (reference): {_VG_CHI_C:.6f}")
    print("=" * 60)

    if data is None:
        data = load_data(
            bao_path=bao_path or "efc_inference/data/bao/desi_dr2/bao_desi_dr2.json",
            growth_path=growth_path or "efc_inference/data/growth/fs8_extended.csv",
            hz_path=hz_path or "efc_inference/data/hz/hz_cosmic_chronometers.csv",
            snia_path=snia_path or "efc_inference/data/snia/pantheon_plus_shoes.csv",
            snia_cov_path=snia_cov_path,
        )

    rng_key = jax.random.PRNGKey(seed)

    # ── VariantH: 5 params ──
    t0 = time.time()
    kernel_vh = NUTS(variant_h_model, dense_mass=True, target_accept_prob=target_accept)
    mcmc_vh = MCMC(kernel_vh, num_warmup=num_warmup, num_samples=num_samples,
                   num_chains=num_chains, progress_bar=True)
    mcmc_vh.run(rng_key, data)
    dt_vh = time.time() - t0
    samples_vh = mcmc_vh.get_samples()

    # ── LCDM reference: 3 params ──
    t0 = time.time()
    kernel_lcdm = NUTS(lcdm_model, dense_mass=True, target_accept_prob=target_accept)
    mcmc_lcdm = MCMC(kernel_lcdm, num_warmup=num_warmup, num_samples=num_samples,
                     num_chains=num_chains, progress_bar=True)
    mcmc_lcdm.run(jax.random.PRNGKey(seed + 1), data)
    dt_lcdm = time.time() - t0
    samples_lcdm = mcmc_lcdm.get_samples()

    # ── Extract posteriors ──
    om_vh = np.array(samples_vh["Omega_m"])
    h0_vh = np.array(samples_vh["H0"])
    s8_vh = np.array(samples_vh["sigma8"])
    S_bar_0_samples = np.array(samples_vh["S_bar_0"])
    beta_0_samples = np.array(samples_vh["beta_0"])

    # lcdm_model uses reparametrized z_Om, z_H0, z_s8 → transform back
    om_lcdm = np.array(0.30 + 0.05 * samples_lcdm["z_Om"])
    h0_lcdm = np.array(67.5 + 5.0 * samples_lcdm["z_H0"])
    s8_lcdm = np.array(0.80 + 0.04 * samples_lcdm["z_s8"])

    # ── Best-fit ΔlogL (median parameters) ──
    bf_Om_vh = float(np.median(om_vh))
    bf_H0_vh = float(np.median(h0_vh))
    bf_s8_vh = float(np.median(s8_vh))
    bf_S = float(np.median(S_bar_0_samples))
    bf_B = float(np.median(beta_0_samples))

    bf_Om_lcdm = float(np.median(om_lcdm))
    bf_H0_lcdm = float(np.median(h0_lcdm))
    bf_s8_lcdm = float(np.median(s8_lcdm))

    # Compute per-probe ΔlogL
    fs8_vh_pred = compute_fs8_variant_h(data.growth_z, bf_Om_vh, bf_H0_vh, bf_s8_vh, bf_S, bf_B)
    fs8_lcdm_pred = compute_fs8_lcdm(data.growth_z, bf_Om_lcdm, bf_H0_lcdm, bf_s8_lcdm)
    ll_growth_vh = float(chi2_log_likelihood(data.growth_obs, fs8_vh_pred, data.growth_err))
    ll_growth_lcdm = float(chi2_log_likelihood(data.growth_obs, fs8_lcdm_pred, data.growth_err))
    dll_growth = ll_growth_vh - ll_growth_lcdm

    # Total ΔlogL from all probes (both use LCDM background, only growth differs)
    r_d = RD_FIXED
    bao_vh = predict_bao_lcdm(data.bao_z, bf_H0_vh, bf_Om_vh, r_d,
                               data.bao_is_dh, data.bao_is_dm, data.bao_is_dv)
    bao_lcdm = predict_bao_lcdm(data.bao_z, bf_H0_lcdm, bf_Om_lcdm, r_d,
                                 data.bao_is_dh, data.bao_is_dm, data.bao_is_dv)
    ll_bao_vh = float(bao_log_likelihood(data, bao_vh))
    ll_bao_lcdm = float(bao_log_likelihood(data, bao_lcdm))

    Hz_vh_pred = Hz_lcdm(data.hz_z, bf_H0_vh, bf_Om_vh)
    Hz_lcdm_pred = Hz_lcdm(data.hz_z, bf_H0_lcdm, bf_Om_lcdm)
    ll_hz_vh = float(chi2_log_likelihood(data.hz_obs, Hz_vh_pred, data.hz_err))
    ll_hz_lcdm = float(chi2_log_likelihood(data.hz_obs, Hz_lcdm_pred, data.hz_err))

    dll_bao = ll_bao_vh - ll_bao_lcdm
    dll_hz = ll_hz_vh - ll_hz_lcdm

    # SNIa: both use LCDM background, so ΔlogL comes only from Om/H0 shift
    mu_th_vh = predict_mu_th_lcdm(data.snia_z, bf_H0_vh, bf_Om_vh)
    mu_th_lcdm_ref = predict_mu_th_lcdm(data.snia_z, bf_H0_lcdm, bf_Om_lcdm)
    ll_snia_vh = float(snia_log_likelihood(
        mu_th_vh, data.snia_mb, data.snia_cov_inv, data.snia_cov_logdet))
    ll_snia_lcdm = float(snia_log_likelihood(
        mu_th_lcdm_ref, data.snia_mb, data.snia_cov_inv, data.snia_cov_logdet))
    dll_snia = ll_snia_vh - ll_snia_lcdm

    dll_total = dll_bao + dll_hz + dll_growth + dll_snia

    # ── Model comparison (Δk = 2) ──
    delta_k = 2
    daic = 2.0 * delta_k - 2.0 * dll_total
    n_data = len(data.bao_z) + len(data.growth_z) + len(data.hz_z) + len(data.snia_z)
    dbic = delta_k * np.log(n_data) - 2.0 * dll_total

    # ── Key diagnostic: S_bar_0 significance ──
    S_bar_0_mean = float(np.mean(S_bar_0_samples))
    S_bar_0_std = float(np.std(S_bar_0_samples))
    S_bar_0_sigma = S_bar_0_mean / max(S_bar_0_std, 1e-10)
    beta_0_mean = float(np.mean(beta_0_samples))
    beta_0_std = float(np.std(beta_0_samples))
    s8_shift = float(np.mean(s8_vh)) - float(np.mean(s8_lcdm))

    # MCMC diagnostics
    diag = mcmc_vh.get_extra_fields() if hasattr(mcmc_vh, 'get_extra_fields') else {}
    summary = {}
    try:
        from numpyro.diagnostics import summary as np_summary
        summary = np_summary(mcmc_vh.get_samples(group_by_chain=True))
    except Exception:
        pass

    n_eff_min = float('inf')
    r_hat_max = 0.0
    for param_name in ["Omega_m", "H0", "sigma8", "S_bar_0", "beta_0"]:
        if param_name in summary:
            n_eff_min = min(n_eff_min, float(summary[param_name]["n_eff"].min()))
            r_hat_max = max(r_hat_max, float(summary[param_name]["r_hat"].max()))

    # ── Correlations ──
    all_samples = np.column_stack([om_vh, h0_vh, s8_vh, S_bar_0_samples, beta_0_samples])
    corrmat = np.corrcoef(all_samples.T)
    correlations = {
        "S_bar_0_vs_sigma8": float(corrmat[3, 2]),
        "S_bar_0_vs_beta_0": float(corrmat[3, 4]),
        "beta_0_vs_sigma8": float(corrmat[4, 2]),
        "S_bar_0_vs_Omega_m": float(corrmat[3, 0]),
    }

    # ── mu diagnostics at best-fit ──
    z_diag = np.array([0.02, 0.15, 0.38, 0.51, 0.61, 0.77, 0.85])
    mu_diag_vals = {}
    for z_val in z_diag:
        a_val = 1.0 / (1.0 + z_val)
        mu_val = float(_mu_of_a_variant_h(jnp.array(a_val), bf_S, bf_B))
        mu_diag_vals[f"mu_z{z_val:.2f}"] = mu_val

    # ── Verdict ──
    if S_bar_0_sigma < 1.0:
        verdict = "NULL_RESULT" if abs(dll_growth) < 0.5 else "WEAK_UNCONSTRAINED"
    elif S_bar_0_sigma < 2.0:
        verdict = "MARGINAL_SIGNAL" if daic < 0 else "MARGINAL_NOT_PREFERRED"
    elif S_bar_0_sigma >= 2.0:
        if daic < -2:
            verdict = "SIGNAL"
        elif daic < 0:
            verdict = "SIGNAL_MARGINAL_AIC"
        else:
            verdict = "STRONG_COUPLING_POOR_FIT"
    else:
        verdict = "INCONCLUSIVE"

    print(f"\n{'='*60}")
    print(f"VARIANT-H RESULTS:")
    print(f"  S̄₀ = {S_bar_0_mean:.6f} ± {S_bar_0_std:.6f} ({S_bar_0_sigma:.2f}σ)")
    print(f"  β₀ = {beta_0_mean:.4f} ± {beta_0_std:.4f}")
    print(f"  σ8 shift: {s8_shift:+.4f}")
    print(f"  ΔlogL_growth: {dll_growth:+.4f}")
    print(f"  ΔlogL_total:  {dll_total:+.4f}")
    print(f"  ΔAIC: {daic:+.3f}  ΔBIC: {dbic:+.3f}")
    print(f"  n_eff_min: {n_eff_min:.0f}, r_hat_max: {r_hat_max:.4f}")
    print(f"  VERDICT: {verdict}")
    print(f"  Time: VH={dt_vh:.0f}s, LCDM={dt_lcdm:.0f}s")
    print(f"{'='*60}\n")

    return {
        "verdict": verdict,
        "cosmology_model": "EFCVariantH",
        "S_bar_0_mean": S_bar_0_mean,
        "S_bar_0_std": S_bar_0_std,
        "S_bar_0_sigma": S_bar_0_sigma,
        "beta_0_mean": beta_0_mean,
        "beta_0_std": beta_0_std,
        "om_mean": float(np.mean(om_vh)),
        "om_std": float(np.std(om_vh)),
        "h0_mean": float(np.mean(h0_vh)),
        "h0_std": float(np.std(h0_vh)),
        "s8_mean": float(np.mean(s8_vh)),
        "s8_std": float(np.std(s8_vh)),
        "s8_shift": s8_shift,
        "s8_lcdm_mean": float(np.mean(s8_lcdm)),
        "dll_growth": dll_growth,
        "dll_bao": dll_bao,
        "dll_hz": dll_hz,
        "dll_snia": dll_snia,
        "dll_total": dll_total,
        "daic": daic,
        "dbic": dbic,
        "n_eff_min": n_eff_min,
        "r_hat_max": r_hat_max,
        "correlations": correlations,
        "mu_diagnostics": {
            "chi_c_ref": _VG_CHI_C,
            "S_bar_0": bf_S,
            "beta_0": bf_B,
            **mu_diag_vals,
        },
        "total_time_seconds": dt_vh + dt_lcdm,
        "priors": {
            "S_bar_0": "U(0, 0.5)",
            "beta_0": "U(0.05, 5.0)",
            "sigma8": "TruncN(0.80, 0.04)",
        },
    }


# ═══════════════════════════════════════════════════════════════
#  N7-GRAV DIAGNOSTIC — GRAV-LOCKED G_eff
# ═══════════════════════════════════════════════════════════════

def run_n7_grav_lock_nuts(
    data: 'ProbeData' = None,
    num_warmup: int = 500,
    num_samples: int = 2000,
    num_chains: int = 2,
    seed: int = 42,
    target_accept: float = 0.8,
    bao_path: str = None,
    growth_path: str = None,
    hz_path: str = None,
    snia_path: str = None,
    snia_cov_path: str = None,
) -> 'NUTSResult':
    """Run N7-GRAV diagnostic: GRAV-locked G_eff cross-probe test via NUTS.

    Uses efc_model_n7_grav which has G_eff in the growth source term.
    Background expansion is standard EFC (same as baseline).

    Returns NUTSResult with same structure as run_nuts_efc.
    """
    print("=" * 60)
    print("N7-GRAV: Global Parameter-Lock Cross-Probe ('Domstolen')")
    print(f"  GRAV: C={_GRAV_C}, k_lambda={_GRAV_K_LAMBDA}, k_eff={_GRAV_K_EFF}")
    print(f"  Screen factor: {_GRAV_SCREEN:.6f}")
    print(f"  G_eff/G at a=1: {float(g_eff_over_G_jax(jnp.array(1.0))):.6f}")
    print("=" * 60)

    # Load data if not provided
    if data is None:
        data = load_data(
            bao_path=bao_path or "efc_inference/data/bao/bao_starter.csv",
            growth_path=growth_path or "efc_inference/data/growth/fs8_extended.csv",
            hz_path=hz_path or "efc_inference/data/hubble/hz_cosmic_chronometers.csv",
            snia_path=snia_path or "efc_inference/data/snia/pantheon_binned.csv",
            snia_cov_path=snia_cov_path or "efc_inference/data/snia/pantheon_binned_covtotal.npy",
        )

    print(f"Data: {data.n_total} points ({len(data.bao_z)} BAO, {len(data.growth_z)} growth, "
          f"{len(data.hz_z)} Hz, {len(data.snia_z)} SNIa)")

    # ── 1. Run EFC with GRAV G_eff ──
    print(f"\n--- N7-GRAV: EFC (G_eff in growth) ---")
    print(f"  NUTS: {num_warmup}w + {num_samples}s, {num_chains} chains")

    rng_key = jax.random.PRNGKey(seed)
    kernel = NUTS(efc_model_n7_grav, dense_mass=True, target_accept_prob=target_accept)
    mcmc = MCMC(kernel, num_warmup=num_warmup, num_samples=num_samples,
                num_chains=num_chains, progress_bar=True)

    t0 = time.time()
    mcmc.run(rng_key, data=data)
    dt_efc = time.time() - t0

    samples = mcmc.get_samples()
    # N7-GRAV model uses reparametrized z_* samples — transform to physical
    alpha_samples = np.array(0.0 + 3.0 * samples["z_alpha"])
    om_samples = np.array(0.315 + 0.03 * samples["z_Om"])
    h0_samples = np.array(67.4 + 3.0 * samples["z_H0"])
    s8_samples = np.array(0.80 + 0.04 * samples["z_s8"])

    alpha_mean = float(np.mean(alpha_samples))
    alpha_std = float(np.std(alpha_samples))
    alpha_sig = abs(alpha_mean) / alpha_std if alpha_std > 0 else 0.0

    print(f"  α = {alpha_mean:.4f} ± {alpha_std:.4f} ({alpha_sig:.2f}σ)")
    print(f"  P(α<0) = {float(np.mean(alpha_samples < 0)):.3f}")
    print(f"  Ωm = {float(np.mean(om_samples)):.4f} ± {float(np.std(om_samples)):.4f}")
    print(f"  H0 = {float(np.mean(h0_samples)):.2f} ± {float(np.std(h0_samples)):.2f}")
    print(f"  σ8 = {float(np.mean(s8_samples)):.4f} ± {float(np.std(s8_samples)):.4f}")

    # Log-likelihood at best fit
    ll_efc = float(np.max(np.array(mcmc.get_extra_fields().get(
        "potential_energy", np.array([0.0])))) * -1) if hasattr(mcmc, 'get_extra_fields') else 0.0
    # Simple approximation: use median parameters
    # (proper way would need pointwise logL evaluation)

    # ── 2. Run LCDM reference (reuse baseline model) ──
    print(f"\n--- N7-GRAV: LCDM reference ---")

    rng_key_lcdm = jax.random.PRNGKey(seed + 1)
    kernel_lcdm = NUTS(lcdm_model, dense_mass=True, target_accept_prob=target_accept)
    mcmc_lcdm = MCMC(kernel_lcdm, num_warmup=num_warmup, num_samples=num_samples,
                     num_chains=num_chains, progress_bar=True)

    t0 = time.time()
    mcmc_lcdm.run(rng_key_lcdm, data=data)
    dt_lcdm = time.time() - t0

    samples_lcdm = mcmc_lcdm.get_samples()
    # LCDM model uses reparametrized z_* — transform to physical
    om_lcdm = np.array(0.30 + 0.05 * samples_lcdm["z_Om"])
    h0_lcdm = np.array(67.5 + 5.0 * samples_lcdm["z_H0"])
    s8_lcdm = np.array(0.80 + 0.04 * samples_lcdm["z_s8"])

    # ── Convergence diagnostics ──
    import arviz as az
    idata_efc = az.from_numpyro(mcmc)
    summary_efc = az.summary(idata_efc, var_names=["z_Om", "z_H0", "z_s8", "z_alpha"])
    n_eff_min = float(summary_efc["ess_bulk"].min())
    r_hat_max = float(summary_efc["r_hat"].max())

    idata_lcdm = az.from_numpyro(mcmc_lcdm)
    summary_lcdm = az.summary(idata_lcdm, var_names=["z_Om", "z_H0", "z_s8"])
    n_eff_min_lcdm = float(summary_lcdm["ess_bulk"].min())

    # ── Model comparison via WAIC or simple loglik ──
    # Use potential energy for approximate loglik
    try:
        pe_efc = np.array(mcmc.get_extra_fields()["potential_energy"])
        pe_lcdm = np.array(mcmc_lcdm.get_extra_fields()["potential_energy"])
        ll_max_efc = float(-np.min(pe_efc))
        ll_max_lcdm = float(-np.min(pe_lcdm))
    except Exception:
        ll_max_efc = 0.0
        ll_max_lcdm = 0.0

    k_efc = 4
    k_lcdm = 3
    n_data = data.n_total
    daic = (-2 * ll_max_efc + 2 * k_efc) - (-2 * ll_max_lcdm + 2 * k_lcdm)
    dbic = (-2 * ll_max_efc + k_efc * np.log(n_data)) - (-2 * ll_max_lcdm + k_lcdm * np.log(n_data))

    # ── Build posterior chain ──
    posterior_chain = np.column_stack([om_samples, h0_samples, s8_samples, alpha_samples])

    print(f"\n  ΔAIC = {daic:.2f}, ΔBIC = {dbic:.2f}")
    print(f"  n_eff_min = {n_eff_min:.0f}, r_hat_max = {r_hat_max:.4f}")
    print(f"  Time: EFC={dt_efc:.0f}s, LCDM={dt_lcdm:.0f}s")

    # ── Verdict ──
    if alpha_sig >= 2.0 and daic < -2.0:
        verdict = "SURVIVES"
    elif alpha_sig >= 1.5 and daic < 0.0:
        verdict = "MARGINAL"
    else:
        verdict = "NO_SIGNAL"

    print(f"\n  N7-GRAV VERDICT: {verdict}")

    return NUTSResult(
        alpha_mean=alpha_mean,
        alpha_std=alpha_std,
        alpha_significance=alpha_sig,
        alpha_p_negative=float(np.mean(alpha_samples < 0)),
        om_mean=float(np.mean(om_samples)),
        om_std=float(np.std(om_samples)),
        h0_mean=float(np.mean(h0_samples)),
        h0_std=float(np.std(h0_samples)),
        s8_mean=float(np.mean(s8_samples)),
        s8_std=float(np.std(s8_samples)),
        ll_max_efc=ll_max_efc,
        ll_max_lcdm=ll_max_lcdm,
        daic=float(daic),
        dbic=float(dbic),
        n_data=n_data,
        time_efc=dt_efc,
        time_lcdm=dt_lcdm,
        n_eff_min=n_eff_min,
        r_hat_max=r_hat_max,
        posterior_chain=posterior_chain,
        diagnostic_name="N7_GRAV_LOCK",
        verdict=verdict,
    )


# ═══════════════════════════════════════════════════════════════
#  D2: SELF-CONSISTENT SOUND HORIZON
#
#  Instead of RD_FIXED=147.09, compute r_d from (Ωm, H0) at each
#  MCMC sample using compute_rd_efc(). Uses jax.pure_callback
#  to call numpy-based sound_horizon.py from within JIT.
# ═══════════════════════════════════════════════════════════════

def _compute_rd_d2_numpy(Om_val: float, H0_val: float,
                         R_max: float = 0.01,
                         safety_threshold_pct: float = 1.0) -> float:
    """Numpy wrapper: compute self-consistent EFC r_d.
    Returns rd_efc [Mpc] or NaN if safety check fails."""
    try:
        from efc_inference.core.sound_horizon import compute_rd_efc
        result = compute_rd_efc(float(Om_val), float(H0_val),
                                R_max=R_max,
                                safety_threshold_pct=safety_threshold_pct)
        if result["safety_level"] == "fail":
            return float("nan")
        return float(result["rd_efc"])
    except Exception:
        return float("nan")


def _rd_callback(Om_H0_arr):
    """Pure callback for JAX: takes [Om, H0] array, returns scalar r_d."""
    Om_val = float(Om_H0_arr[0])
    H0_val = float(Om_H0_arr[1])
    return np.array(_compute_rd_d2_numpy(Om_val, H0_val))


def _rd_callback_scalar(Om, H0):
    """Call pure_callback for a single (Om, H0) pair. Not JVP-safe."""
    Om_H0 = jnp.stack([Om, H0])
    return jax.pure_callback(
        _rd_callback,
        jax.ShapeDtypeStruct((), jnp.float64),
        Om_H0,
    )


@jax.custom_jvp
def compute_rd_d2_jax(Om, H0):
    """JAX-compatible self-consistent r_d via pure_callback.

    Uses numpy compute_rd_efc under the hood (~2ms per call).
    Returns r_d in Mpc (or NaN if safety fails).
    Wrapped with custom_jvp for NUTS gradient support (finite-difference).
    """
    return _rd_callback_scalar(Om, H0)


@compute_rd_d2_jax.defjvp
def _compute_rd_d2_jvp(primals, tangents):
    """Finite-difference JVP for r_d(Om, H0).

    r_d varies slowly with Om/H0 (~0.5 Mpc per 0.01 in Om),
    so numerical gradients are stable and accurate.
    """
    Om, H0 = primals
    dOm, dH0 = tangents
    rd = _rd_callback_scalar(Om, H0)
    eps = 1e-4
    # Partial derivatives via central difference
    drd_dOm = (_rd_callback_scalar(Om + eps, H0) - _rd_callback_scalar(Om - eps, H0)) / (2 * eps)
    drd_dH0 = (_rd_callback_scalar(Om, H0 + eps) - _rd_callback_scalar(Om, H0 - eps)) / (2 * eps)
    tangent_out = drd_dOm * dOm + drd_dH0 * dH0
    return rd, tangent_out


def efc_model_d2(data: ProbeData):
    """Numpyro model for D2: EFC with self-consistent r_d(Ωm, H0).

    Same 4 params as baseline [Om, H0, s8, alpha], but r_d is computed
    dynamically from Om, H0 instead of using RD_FIXED=147.09.

    Reparametrized to standardized space for stable NUTS.
    D3: σ8 ~ N(0.80, 0.04) honest prior.
    """
    z_Om = numpyro.sample("z_Om", dist.Normal(0.0, 1.0))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0.0, 1.0))
    z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))
    z_alpha = numpyro.sample("z_alpha", dist.Normal(0.0, 1.0))

    Om = 0.30 + 0.05 * z_Om
    H0 = 67.5 + 5.0 * z_H0
    s8 = 0.80 + 0.04 * z_s8
    alpha = 0.0 + 3.0 * z_alpha

    # Soft bounds
    numpyro.factor("Om_bound", -1e6 * jnp.where((Om < 0.05) | (Om > 0.8), 1.0, 0.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 < 40.0) | (H0 > 100.0), 1.0, 0.0))

    # D2: self-consistent r_d from sound_horizon.py
    r_d = compute_rd_d2_jax(Om, H0)

    # Reject NaN (safety_fail) samples
    numpyro.factor("rd_safety", jnp.where(jnp.isnan(r_d), -1e10, 0.0))
    # Use a safe fallback for NaN in computations (will be rejected anyway)
    r_d = jnp.where(jnp.isnan(r_d), RD_FIXED, r_d)

    # Track r_d for posterior analysis
    numpyro.deterministic("r_d", r_d)

    # ── BAO ──
    bao_pred = predict_bao(
        data.bao_z, H0, Om, alpha, r_d,
        data.bao_is_dh, data.bao_is_dm, data.bao_is_dv,
    )
    ll_bao = bao_log_likelihood(data, bao_pred)

    # ── Hz ──
    hz_pred = Hz(data.hz_z, H0, Om, alpha)
    ll_hz = chi2_log_likelihood(data.hz_obs, hz_pred, data.hz_err)

    # ── Growth ──
    fs8_pred = compute_fs8(data.growth_z, Om, H0, s8, alpha)
    ll_growth = chi2_log_likelihood(data.growth_obs, fs8_pred, data.growth_err)

    # ── SNIa ──
    mu_th = predict_mu_th(data.snia_z, H0, Om, alpha)
    ll_snia = snia_log_likelihood(
        mu_th, data.snia_mb,
        data.snia_cov_inv, data.snia_cov_logdet,
    )

    numpyro.factor("log_likelihood", ll_bao + ll_hz + ll_growth + ll_snia)

    # Deterministics for diagnosis
    numpyro.deterministic("Om", Om)
    numpyro.deterministic("H0", H0)
    numpyro.deterministic("s8", s8)
    numpyro.deterministic("alpha", alpha)


def lcdm_model_d2(data: ProbeData):
    """Numpyro model for D2: LCDM with self-consistent r_d(Ωm, H0).

    Same as lcdm_model but r_d computed from Om, H0.
    """
    z_Om = numpyro.sample("z_Om", dist.Normal(0.0, 1.0))
    z_H0 = numpyro.sample("z_H0", dist.Normal(0.0, 1.0))
    z_s8 = numpyro.sample("z_s8", dist.Normal(0.0, 1.0))

    Om = 0.30 + 0.05 * z_Om
    H0 = 67.5 + 5.0 * z_H0
    s8 = 0.80 + 0.04 * z_s8

    numpyro.factor("Om_bound", -1e6 * jnp.where((Om < 0.05) | (Om > 0.8), 1.0, 0.0))
    numpyro.factor("H0_bound", -1e6 * jnp.where((H0 < 40.0) | (H0 > 100.0), 1.0, 0.0))

    r_d = compute_rd_d2_jax(Om, H0)
    numpyro.factor("rd_safety", jnp.where(jnp.isnan(r_d), -1e10, 0.0))
    r_d = jnp.where(jnp.isnan(r_d), RD_FIXED, r_d)
    numpyro.deterministic("r_d", r_d)

    bao_pred = predict_bao_lcdm(
        data.bao_z, H0, Om, r_d,
        data.bao_is_dh, data.bao_is_dm, data.bao_is_dv,
    )
    ll_bao = bao_log_likelihood(data, bao_pred)

    hz_pred = Hz_lcdm(data.hz_z, H0, Om)
    ll_hz = chi2_log_likelihood(data.hz_obs, hz_pred, data.hz_err)

    fs8_pred = compute_fs8_lcdm(data.growth_z, Om, H0, s8)
    ll_growth = chi2_log_likelihood(data.growth_obs, fs8_pred, data.growth_err)

    mu_th = predict_mu_th_lcdm(data.snia_z, H0, Om)
    ll_snia = snia_log_likelihood(
        mu_th, data.snia_mb,
        data.snia_cov_inv, data.snia_cov_logdet,
    )

    numpyro.factor("log_likelihood", ll_bao + ll_hz + ll_growth + ll_snia)


def run_d2_nuts(
    data: Optional[ProbeData] = None,
    baseline_alpha_sig: float = 0.0,
    num_warmup: int = 500,
    num_samples: int = 2000,
    num_chains: int = 1,
    seed: int = 42,
    target_accept: float = 0.8,
    pass_delta_alpha: float = 0.3,
) -> dict:
    """Run D2 self-consistent sound horizon comparison via NUTS.

    Runs EFC and LCDM with r_d computed from (Ωm, H0) via compute_rd_efc().
    Compares α significance to proxy baseline.

    NOTE: pure_callback disables JIT compilation of the model —
    each sample calls numpy compute_rd_efc (~2ms). For 2000 samples
    × 2 chains = 4000 calls → ~8 seconds of callback overhead.
    Acceptable for a diagnostic test.

    Args:
        data:               ProbeData (loaded if None)
        baseline_alpha_sig: α significance from proxy baseline (for comparison)
        num_warmup:         warmup steps
        num_samples:        post-warmup samples
        num_chains:         parallel chains
        seed:               PRNG seed
        target_accept:      NUTS target acceptance
        pass_delta_alpha:   threshold for |Δα_sig| verdict

    Returns:
        Dict with d2_verdict, alpha stats, r_d posterior, delta_alpha_sig
    """
    if data is None:
        data = load_data()

    import time as _time
    t0 = _time.time()

    key = jax.random.PRNGKey(seed + 9000)  # different seed from other diagnostics

    # ── D2 EFC run ──
    kernel_efc = NUTS(
        efc_model_d2,
        target_accept_prob=target_accept,
        max_tree_depth=10,
        dense_mass=True,
        init_strategy=numpyro.infer.init_to_value(
            values={"z_Om": -0.18, "z_H0": -0.10, "z_s8": 0.0, "z_alpha": -0.27}
        ),
    )
    chain_method = "parallel" if num_chains > 1 else "sequential"
    mcmc_efc = MCMC(kernel_efc, num_warmup=num_warmup,
                     num_samples=num_samples, num_chains=num_chains,
                     chain_method=chain_method, progress_bar=False)
    mcmc_efc.run(key, data, extra_fields=("potential_energy",))

    samples_efc = mcmc_efc.get_samples()
    alpha_d2 = np.array(0.0 + 3.0 * samples_efc["z_alpha"])
    rd_d2 = np.array(samples_efc["r_d"])

    alpha_d2_mean = float(np.mean(alpha_d2))
    alpha_d2_std = float(np.std(alpha_d2))
    alpha_d2_sig = abs(alpha_d2_mean) / alpha_d2_std if alpha_d2_std > 0 else 0.0
    alpha_d2_pneg = float(np.mean(alpha_d2 < 0))

    rd_mean = float(np.mean(rd_d2))
    rd_std = float(np.std(rd_d2))

    dt_efc = _time.time() - t0

    # ── D2 LCDM run ──
    t1 = _time.time()
    key2 = jax.random.PRNGKey(seed + 9001)
    kernel_lcdm = NUTS(
        lcdm_model_d2,
        target_accept_prob=target_accept,
        max_tree_depth=10,
        dense_mass=True,
        init_strategy=numpyro.infer.init_to_value(
            values={"z_Om": -0.18, "z_H0": -0.10, "z_s8": 0.0}
        ),
    )
    mcmc_lcdm = MCMC(kernel_lcdm, num_warmup=num_warmup,
                      num_samples=num_samples, num_chains=num_chains,
                      chain_method=chain_method, progress_bar=False)
    mcmc_lcdm.run(key2, data, extra_fields=("potential_energy",))

    # Model comparison
    extra_efc = mcmc_efc.get_extra_fields()
    extra_lcdm = mcmc_lcdm.get_extra_fields()

    if "potential_energy" in extra_efc:
        ll_max_efc = float(-np.min(np.array(extra_efc["potential_energy"])))
    else:
        ll_max_efc = float("nan")
    if "potential_energy" in extra_lcdm:
        ll_max_lcdm = float(-np.min(np.array(extra_lcdm["potential_energy"])))
    else:
        ll_max_lcdm = float("nan")

    k_efc, k_lcdm = 4, 3
    n_data = data.n_total
    daic = -2 * (ll_max_efc - ll_max_lcdm) + 2 * (k_efc - k_lcdm)
    dbic = -2 * (ll_max_efc - ll_max_lcdm) + (k_efc - k_lcdm) * np.log(n_data)

    dt_lcdm = _time.time() - t1
    total_time = _time.time() - t0

    # ── Verdict ──
    delta_alpha_sig = abs(alpha_d2_sig - baseline_alpha_sig) if baseline_alpha_sig > 0 else 0.0

    if alpha_d2_sig < 1.0 or (baseline_alpha_sig > 0 and delta_alpha_sig >= 0.6):
        verdict = "COLLAPSED"
    elif delta_alpha_sig < pass_delta_alpha:
        verdict = "PASS"
    elif delta_alpha_sig < 0.6:
        verdict = "MARGINAL"
    else:
        verdict = "COLLAPSED"

    return {
        "verdict": verdict,
        "alpha_mean": round(alpha_d2_mean, 4),
        "alpha_std": round(alpha_d2_std, 4),
        "alpha_sig": round(alpha_d2_sig, 3),
        "alpha_p_negative": round(alpha_d2_pneg, 4),
        "rd_mean": round(rd_mean, 2),
        "rd_std": round(rd_std, 2),
        "daic": round(float(daic), 2),
        "dbic": round(float(dbic), 2),
        "delta_alpha_sig": round(delta_alpha_sig, 3),
        "baseline_alpha_sig": round(baseline_alpha_sig, 3),
        "total_time_seconds": round(total_time, 1),
        "time_efc_s": round(dt_efc, 1),
        "time_lcdm_s": round(dt_lcdm, 1),
        "n_data": n_data,
    }


if __name__ == "__main__":
    # Set platform — if CUDA available, use it
    try:
        numpyro.set_platform("cuda")
        print("Platform: CUDA (GPU)")
    except Exception:
        print("Platform: CPU (no CUDA)")

    print(f"JAX version: {jax.__version__}")
    print(f"Devices: {jax.devices()}")
    print()

    n_gpus = len(jax.devices())
    num_chains = min(n_gpus, 2)  # 1 chain per GPU
    print(f"Using {num_chains} chain(s) on {n_gpus} GPU(s)")
    print()

    result = run_nuts_efc(
        num_warmup=500,
        num_samples=2000,
        num_chains=num_chains,
        seed=42,
    )

    # Save result
    import json
    result_dict = {
        "alpha_mean": result.alpha_mean,
        "alpha_std": result.alpha_std,
        "alpha_significance": result.alpha_significance,
        "alpha_p_negative": result.alpha_p_negative,
        "om_mean": result.om_mean,
        "h0_mean": result.h0_mean,
        "s8_mean": result.s8_mean,
        "daic": result.daic,
        "dbic": result.dbic,
        "time_efc_s": result.time_efc,
        "time_lcdm_s": result.time_lcdm,
        "time_total_s": result.time_efc + result.time_lcdm,
        "n_data": result.n_data,
        "num_chains": num_chains,
        "n_eff_min": result.n_eff_min,
        "r_hat_max": result.r_hat_max,
        "platform": str(jax.devices()),
    }
    with open("nuts_result.json", "w") as f:
        json.dump(result_dict, f, indent=2)
    print("Result saved to nuts_result.json")
