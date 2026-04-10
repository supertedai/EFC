"""
A_sig 2D PIEMD pipeline for the Bullet Cluster (EFC-VAL-2026-004)

Implements the baseline directional lensing residual operator A_sig on a
PIEMD (Pseudo-Isothermal Elliptical Mass Distribution) convergence map.

Reference: Magnusson (2026), DOI 10.6084/m9.figshare.31963668
           Kassiola & Kovner (1993), ApJ 417, 450
           Kneib et al. (1996), ApJ 471, 643
           Markevitch (2006), ESA SP-604

The A_sig operator measures shock-locked asymmetry in lensing convergence:

    A_sig = <kappa>_front - <kappa>_back

where `front` is the pre-shock strip (toward the main cluster) and `back` is
the post-shock strip (behind the bullet). Under a parametric PIEMD model
with no directional physics, A_sig ~ 0 (null hypothesis). Under EFC's
entropy-gradient coupling, A_sig != 0 is predicted for the full δκ residual
δκ = κ_obs − κ_PIEMD, produced by the scalar field φ coupling to the shock
front.

This module provides:

  - ``piemd_kappa``: analytical elliptical PIEMD convergence field
  - ``sum_halos``: convergence from a list of PIEMD halos
  - ``asig_2d``: A_sig operator (front − back means over two strips)
  - ``bootstrap_null``: random-rotation bootstrap null distribution
  - ``default_halos``: the placeholder halo list used for the baseline

Usage (baseline reproduction):

    from asig_2d_piemd import run_baseline
    run_baseline()

"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict
from typing import List, Tuple

import numpy as np


# ---------------------------------------------------------------------------
#   Grid + geometry (fixed to the paper's conventions)
# ---------------------------------------------------------------------------

GRID_NX = 512
GRID_NY = 512
EXTENT_X_KPC = 1800.0  # total x extent
EXTENT_Y_KPC = 1200.0  # total y extent
SIGMA_CRIT_MSUN_PER_KPC2 = 2.84e9  # z_lens = 0.296, z_source = 1.0

SHOCK_X_KPC = 480.0
SHOCK_NORMAL = np.array([-1.0, 0.0])  # pointing westward toward main cluster
STRIP_WIDTH_KPC = 200.0  # perpendicular strip width
STRIP_LENGTH_KPC = 400.0  # along-shock strip length


@dataclass
class PIEMDHalo:
    """Parameters of a single PIEMD halo component."""

    name: str
    x0_kpc: float        # centre x
    y0_kpc: float        # centre y
    sigma0_km_s: float   # velocity dispersion
    r_core_kpc: float    # core radius
    r_cut_kpc: float     # truncation radius
    ellipticity: float   # eps = (a - b) / (a + b)
    pa_deg: float        # position angle (deg, CCW from +x)


# ---------------------------------------------------------------------------
#   PIEMD convergence (analytical, Kassiola & Kovner 1993 circular form;
#   elliptical extension via the standard (x', y') coordinate rotation).
# ---------------------------------------------------------------------------

G_KPC_KMS = 4.3009e-6  # G in (kpc * (km/s)^2) / M_sun


def _rotate_to_halo_frame(
    x: np.ndarray, y: np.ndarray, halo: PIEMDHalo
) -> Tuple[np.ndarray, np.ndarray]:
    dx = x - halo.x0_kpc
    dy = y - halo.y0_kpc
    theta = math.radians(halo.pa_deg)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    xp =  cos_t * dx + sin_t * dy
    yp = -sin_t * dx + cos_t * dy
    return xp, yp


def piemd_kappa(
    x_kpc: np.ndarray,
    y_kpc: np.ndarray,
    halo: PIEMDHalo,
    sigma_crit_Msun_per_kpc2: float = SIGMA_CRIT_MSUN_PER_KPC2,
) -> np.ndarray:
    """
    Convergence field kappa(x, y) for a single PIEMD halo.

    The projected surface density for the circular PIEMD (Kassiola & Kovner
    1993, eq. 2) is

        Sigma(R) = (sigma0^2 / (2 G)) *
                   (r_cut / (r_cut - r_core)) *
                   ( 1 / sqrt(r_core^2 + R^2)
                   - 1 / sqrt(r_cut^2 + R^2) ).

    Elliptical extension uses

        R_eps^2 = x'^2 / (1 - eps)^2 + y'^2 / (1 + eps)^2

    where (x', y') are rotated by the position angle theta (Kneib et al. 1996).

    We divide by sigma_crit to get the dimensionless convergence kappa.
    """
    xp, yp = _rotate_to_halo_frame(x_kpc, y_kpc, halo)
    eps = halo.ellipticity
    R = np.sqrt((xp / (1.0 - eps)) ** 2 + (yp / (1.0 + eps)) ** 2)

    sigma0_sq = halo.sigma0_km_s ** 2
    prefactor = sigma0_sq / (2.0 * G_KPC_KMS)
    truncation = halo.r_cut_kpc / max(halo.r_cut_kpc - halo.r_core_kpc, 1e-9)
    radial = 1.0 / np.sqrt(halo.r_core_kpc ** 2 + R ** 2) \
           - 1.0 / np.sqrt(halo.r_cut_kpc ** 2 + R ** 2)

    Sigma = prefactor * truncation * radial
    return Sigma / sigma_crit_Msun_per_kpc2


def sum_halos(
    x_kpc: np.ndarray,
    y_kpc: np.ndarray,
    halos: List[PIEMDHalo],
    sigma_crit_Msun_per_kpc2: float = SIGMA_CRIT_MSUN_PER_KPC2,
) -> np.ndarray:
    k = np.zeros_like(x_kpc, dtype=float)
    for h in halos:
        k += piemd_kappa(x_kpc, y_kpc, h, sigma_crit_Msun_per_kpc2)
    return k


def make_grid(
    nx: int = GRID_NX,
    ny: int = GRID_NY,
    extent_x_kpc: float = EXTENT_X_KPC,
    extent_y_kpc: float = EXTENT_Y_KPC,
) -> Tuple[np.ndarray, np.ndarray]:
    """Return 2D meshgrid in kpc centred at (0, 0)."""
    xs = np.linspace(-extent_x_kpc / 2.0, extent_x_kpc / 2.0, nx)
    ys = np.linspace(-extent_y_kpc / 2.0, extent_y_kpc / 2.0, ny)
    X, Y = np.meshgrid(xs, ys, indexing="xy")
    return X, Y


# ---------------------------------------------------------------------------
#   A_sig operator
# ---------------------------------------------------------------------------

def _strip_mask(
    X: np.ndarray,
    Y: np.ndarray,
    shock_x_kpc: float,
    normal: np.ndarray,
    strip_width_kpc: float,
    strip_length_kpc: float,
    side: str,
) -> np.ndarray:
    """
    Boolean mask for a rectangular strip either in front of (``side='front'``,
    pre-shock, toward main cluster) or behind (``side='back'``, post-shock)
    the shock line.

    Signed perpendicular distance from the shock line in the direction of
    the normal is d_perp = (p − p_shock) · n. With normal = (−1, 0), d_perp
    is positive west of the shock line (toward the main cluster) and
    negative east of the shock line (behind the bullet subcluster).
    """
    shock_origin = np.array([shock_x_kpc, 0.0])
    d_perp = (X - shock_origin[0]) * normal[0] + (Y - shock_origin[1]) * normal[1]
    if side == "front":
        in_depth = (d_perp > 0) & (d_perp < strip_width_kpc)
    elif side == "back":
        in_depth = (d_perp < 0) & (d_perp > -strip_width_kpc)
    else:
        raise ValueError(f"side must be 'front' or 'back', got {side!r}")
    # along-shock extent: project onto tangent direction (orthogonal to normal)
    tangent = np.array([-normal[1], normal[0]])
    d_tan = (X - shock_origin[0]) * tangent[0] + (Y - shock_origin[1]) * tangent[1]
    in_length = np.abs(d_tan) < strip_length_kpc / 2.0
    return in_depth & in_length


def asig_2d(
    kappa: np.ndarray,
    X: np.ndarray,
    Y: np.ndarray,
    shock_x_kpc: float = SHOCK_X_KPC,
    normal: np.ndarray = SHOCK_NORMAL,
    strip_width_kpc: float = STRIP_WIDTH_KPC,
    strip_length_kpc: float = STRIP_LENGTH_KPC,
) -> Tuple[float, float, float]:
    """
    Compute A_sig = <kappa>_front - <kappa>_back and return
    (A_sig, kappa_front_mean, kappa_back_mean).
    """
    front = _strip_mask(X, Y, shock_x_kpc, normal, strip_width_kpc, strip_length_kpc, "front")
    back  = _strip_mask(X, Y, shock_x_kpc, normal, strip_width_kpc, strip_length_kpc, "back")
    kf = float(kappa[front].mean())
    kb = float(kappa[back].mean())
    return kf - kb, kf, kb


# ---------------------------------------------------------------------------
#   Bootstrap null test: random rotations of the strip orientation
# ---------------------------------------------------------------------------

def bootstrap_null(
    kappa: np.ndarray,
    X: np.ndarray,
    Y: np.ndarray,
    n_samples: int = 5000,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """
    Null distribution of A_sig under random rotation of the strip normal
    around the shock centre. Returns an array of sampled A_sig values.
    """
    if rng is None:
        rng = np.random.default_rng(42)
    angles = rng.uniform(0.0, 2.0 * math.pi, size=n_samples)
    out = np.empty(n_samples, dtype=float)
    for i, phi in enumerate(angles):
        n = np.array([math.cos(phi), math.sin(phi)])
        a, _, _ = asig_2d(kappa, X, Y, shock_x_kpc=SHOCK_X_KPC, normal=n)
        out[i] = a
    return out


# ---------------------------------------------------------------------------
#   Placeholder halo list (matches the baseline numbers in the paper)
# ---------------------------------------------------------------------------

def default_halos() -> List[PIEMDHalo]:
    """
    Placeholder halos. These are **not** the Rihtarsic et al. (2026) Table 4
    best-fit parameters — the Table 4 values will be dropped in for the final
    paper, as stated in the caveats section. The positions are chosen so
    that the bullet subcluster sits in the back strip (east of shock at
    x_shock = 480 kpc) and the main-cluster double-peaked mass sits in the
    front strip (west of shock), matching Markevitch (2006) and Rihtarsic
    et al. (2026). Peak kappa values are roughly consistent with the paper
    (Main-NW 0.62, Main-SE 0.49, Subcluster 0.49, Group-NE 0.16) but the
    exact kappa_front / kappa_back balance reported in the paper
    (0.1824 / 0.1831 → A_sig = -6.9e-4) depends sensitively on the exact
    best-fit parameters, which this placeholder is not calibrated to
    reproduce numerically.
    """
    return [
        PIEMDHalo("Main-NW",    x0_kpc= 350.0, y0_kpc=  60.0, sigma0_km_s=1250.0, r_core_kpc=60.0, r_cut_kpc=1500.0, ellipticity=0.25, pa_deg= 40.0),
        PIEMDHalo("Main-SE",    x0_kpc= 380.0, y0_kpc= -60.0, sigma0_km_s=1120.0, r_core_kpc=60.0, r_cut_kpc=1500.0, ellipticity=0.25, pa_deg= 40.0),
        PIEMDHalo("Subcluster", x0_kpc= 580.0, y0_kpc=   0.0, sigma0_km_s=1100.0, r_core_kpc=50.0, r_cut_kpc=1000.0, ellipticity=0.10, pa_deg=  0.0),
        PIEMDHalo("Group-NE",   x0_kpc= 600.0, y0_kpc= 300.0, sigma0_km_s= 700.0, r_core_kpc=50.0, r_cut_kpc= 800.0, ellipticity=0.15, pa_deg= 20.0),
    ]


# ---------------------------------------------------------------------------
#   End-to-end baseline
# ---------------------------------------------------------------------------

def run_baseline(n_bootstrap: int = 5000, verbose: bool = True) -> dict:
    """
    Run the PIEMD A_sig 2D baseline with the placeholder halos and report
    the result.

    NOTE: the placeholder halos in ``default_halos`` are not tuned to the
    Rihtarsic et al. (2026) Table 4 best-fit parameters and therefore do
    NOT numerically reproduce the paper's A_sig = -6.9e-4, p = 0.98
    balance. They show the *mechanism* of the A_sig operator only. The
    published result in the paper (EFC-VAL-2026-004) uses a tuned
    parameter set; it can be reproduced in full by replacing
    ``default_halos`` with the Rihtarsic et al. values.
    """
    halos = default_halos()
    X, Y = make_grid()
    kappa = sum_halos(X, Y, halos)

    asig, kf, kb = asig_2d(kappa, X, Y)
    null = bootstrap_null(kappa, X, Y, n_samples=n_bootstrap)
    sigma_null = float(null.std(ddof=1))
    # two-sided p-value: fraction with |null| >= |asig|
    p = float((np.abs(null) >= abs(asig)).mean())
    asig_over_sigma = asig / sigma_null if sigma_null > 0 else 0.0

    result = {
        "kappa_front_mean": kf,
        "kappa_back_mean": kb,
        "asig_baseline": asig,
        "bootstrap_n_samples": n_bootstrap,
        "bootstrap_p_value": p,
        "null_std": sigma_null,
        "asig_over_sigma_null": asig_over_sigma,
        "halos": [asdict(h) for h in halos],
        "note": (
            "Placeholder halos; does NOT numerically reproduce the paper's "
            "A_sig = -6.9e-4, p = 0.98 balance (which requires the "
            "Rihtarsic et al. 2026 Table 4 best-fit parameters). Shows "
            "the mechanism of the A_sig operator only."
        ),
    }
    if verbose:
        print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    run_baseline()
