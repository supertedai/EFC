"""
JWST δκ A_sig killtest for the Bullet Cluster (EFC-VAL-2026-004, P2).

Executes the next_step recorded in
``data/asig_baseline_result.json``:

    "Execute full A_sig test on delta_kappa residual using
     Cha et al. (2025) free-form kappa-map"

The PIEMD baseline (``asig_2d_piemd.run_baseline``) returns A_sig ≈ 0 by
construction — a parametric density-only halo model has no directional
physics. The killtest is on the residual

    δκ(x, y) = κ_obs(x, y) - κ_PIEMD(x, y)

evaluated with a JWST-era reconstruction κ_obs. Sealed prediction P2
(README.md, paper v3.11):

    Entropy-gradient lensing produces a non-zero A_sig aligned with the
    Chandra shock front after subtracting a density-only mass model.

Falsification criterion: a robust A_sig(δκ) ≈ 0 at high significance
falsifies P2.

Inputs (must be supplied locally; not redistributed in this repo):

    --kappa-fits PATH  FITS file of κ_obs on a WCS-tagged grid.
                       Cha et al. (2025): MARS free-form reconstruction
                       (MAST data products, ApJ 987 L15).
                       Rihtaršič et al. (2026): Lenstool parametric model
                       (arXiv:2601.22245 supplement).

Outputs (printed JSON; written to --out PATH if supplied):

    asig_residual           A_sig on δκ
    bootstrap_p_value       two-sided p under random-rotation null
    asig_over_sigma_null    Z-score versus null distribution
    verdict                 "P2 supported" | "P2 falsified" | "inconclusive"

The script does *not* download data; it loads a FITS file at the path
given. See README.md §Reproducibility for the data-acquisition protocol.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from asig_2d_piemd import (  # noqa: E402
    EXTENT_X_KPC,
    EXTENT_Y_KPC,
    GRID_NX,
    GRID_NY,
    SHOCK_NORMAL,
    SHOCK_NORMAL_RIHTARSIC,
    SHOCK_X_KPC,
    SHOCK_X_KPC_RIHTARSIC,
    STRIP_LENGTH_KPC,
    STRIP_WIDTH_KPC,
    asig_2d,
    bootstrap_null,
    default_halos,
    make_grid,
    rihtarsic2026_halos,
    sum_halos,
)


# Pre-registered baseline frames for the PIEMD subtraction:
#
#   "placeholder" — old paper-frame placeholders, baseline A_sig ≈ -6.9e-4
#                   (used in v3.11 paper for operator validation only)
#   "rihtarsic2026" — Table C.2 best-fit halos in BCG1-centred frame, with
#                     SHOCK_X_KPC_RIHTARSIC = 720 kpc. This is the calibrated
#                     baseline used for the actual JWST killtest.
DEFAULT_FRAME = "rihtarsic2026"


# ---------------------------------------------------------------------------
#   Significance thresholds (pre-registered in the paper)
# ---------------------------------------------------------------------------

# P2 is *supported* if |A_sig(δκ)| is large versus the null distribution
# (low two-sided p-value). P2 is *falsified* if A_sig(δκ) is statistically
# indistinguishable from zero. The thresholds below are the conventional
# 3σ / 2σ levels used throughout the EFC validation ledger; they are not
# project-specific tunings.
P_VALUE_SUPPORT = 0.0027        # ≥3σ to count as P2 support
P_VALUE_FALSIFY = 0.05          # p > 0.05 ⇒ A_sig consistent with zero ⇒ P2 falsified


# ---------------------------------------------------------------------------
#   FITS ingestion
# ---------------------------------------------------------------------------

@dataclass
class KappaMap:
    """A 2D convergence map on the paper's fixed (kpc, kpc) grid."""

    kappa: np.ndarray
    X: np.ndarray
    Y: np.ndarray
    source: str


def load_kappa_fits(path: str, source_label: str) -> KappaMap:
    """Load a JWST κ map from a FITS file and reproject onto the paper's
    fixed (1800 × 1200) kpc grid centred on the bullet shock geometry.

    The input FITS must carry a WCS describing sky coordinates and a
    keyword header providing either:

      - ``KPC_PER_PIX`` (kpc/pixel, already on a kpc-aligned grid), or
      - standard celestial WCS plus ``Z_LENS`` so kpc/arcmin can be
        derived from FlatLambdaCDM(H0=70, Om0=0.3).

    Reprojection uses ``reproject.reproject_interp``; bilinear by default.
    """
    try:
        from astropy.io import fits
        from astropy.wcs import WCS
    except ImportError as e:
        raise RuntimeError(
            "astropy is required to load FITS κ maps "
            "(pip install astropy)"
        ) from e

    with fits.open(path) as hdul:
        data = np.asarray(hdul[0].data, dtype=float)
        header = hdul[0].header

    if data.ndim != 2:
        raise ValueError(f"κ map must be 2D, got shape {data.shape}")

    X, Y = make_grid(GRID_NX, GRID_NY, EXTENT_X_KPC, EXTENT_Y_KPC)

    if "KPC_PER_PIX" in header:
        # already in kpc; assume the array is centred on the shock geometry.
        kpc_per_pix = float(header["KPC_PER_PIX"])
        ny, nx = data.shape
        xs_in = (np.arange(nx) - nx / 2) * kpc_per_pix
        ys_in = (np.arange(ny) - ny / 2) * kpc_per_pix
        # Bilinear interpolation onto the target grid via scipy.
        from scipy.interpolate import RegularGridInterpolator

        interp = RegularGridInterpolator(
            (ys_in, xs_in), data, bounds_error=False, fill_value=np.nan
        )
        sample_pts = np.stack([Y.ravel(), X.ravel()], axis=-1)
        kappa = interp(sample_pts).reshape(X.shape)
    else:
        # Use celestial WCS via reproject.
        try:
            from reproject import reproject_interp
        except ImportError as e:
            raise RuntimeError(
                "reproject is required for celestial-WCS κ maps "
                "(pip install reproject)"
            ) from e
        if "Z_LENS" not in header:
            raise ValueError(
                "FITS header lacks both KPC_PER_PIX and Z_LENS; cannot "
                "establish a physical kpc grid"
            )
        from astropy.cosmology import FlatLambdaCDM
        from astropy.io.fits import Header
        from astropy.wcs import WCS as _WCS

        cosmo = FlatLambdaCDM(H0=70.0, Om0=0.3)
        z = float(header["Z_LENS"])
        kpc_per_arcsec = cosmo.kpc_proper_per_arcmin(z).value / 60.0
        pixscale_arcsec = 1.0  # output target: 1 arcsec/pix (to be resampled)
        nx_out = int(EXTENT_X_KPC / (kpc_per_arcsec * pixscale_arcsec))
        ny_out = int(EXTENT_Y_KPC / (kpc_per_arcsec * pixscale_arcsec))

        # Build a target WCS centred on the input WCS reference pixel.
        wcs_in = _WCS(header)
        ra0, dec0 = wcs_in.wcs.crval[:2]
        target_header = Header()
        target_header["NAXIS"] = 2
        target_header["NAXIS1"] = nx_out
        target_header["NAXIS2"] = ny_out
        target_header["CTYPE1"] = "RA---TAN"
        target_header["CTYPE2"] = "DEC--TAN"
        target_header["CRPIX1"] = nx_out / 2
        target_header["CRPIX2"] = ny_out / 2
        target_header["CRVAL1"] = ra0
        target_header["CRVAL2"] = dec0
        target_header["CDELT1"] = -pixscale_arcsec / 3600.0
        target_header["CDELT2"] = pixscale_arcsec / 3600.0

        reprojected, _ = reproject_interp(
            (data, wcs_in), target_header, shape_out=(ny_out, nx_out)
        )
        # Resample onto fixed (GRID_NY, GRID_NX) grid.
        from scipy.ndimage import zoom

        kappa = zoom(
            reprojected,
            (GRID_NY / ny_out, GRID_NX / nx_out),
            order=1,
            mode="nearest",
        )

    return KappaMap(kappa=kappa, X=X, Y=Y, source=source_label)


# ---------------------------------------------------------------------------
#   Killtest
# ---------------------------------------------------------------------------

def compute_dkappa_residual(
    kappa_obs: np.ndarray, X, Y, frame: str = DEFAULT_FRAME
) -> np.ndarray:
    """δκ = κ_obs - κ_PIEMD.

    frame="rihtarsic2026" (default): subtract the Table C.2 best-fit halos
    in the BCG1-centred frame.
    frame="placeholder": subtract the legacy placeholder halos in the
    paper-frame (kept for back-compat with the v3.11 baseline).
    """
    if frame == "rihtarsic2026":
        kappa_piemd = sum_halos(X, Y, rihtarsic2026_halos())
    elif frame == "placeholder":
        kappa_piemd = sum_halos(X, Y, default_halos())
    else:
        raise ValueError(f"unknown frame {frame!r}")
    return kappa_obs - kappa_piemd


def killtest_on_residual(
    kappa_obs: np.ndarray,
    X: np.ndarray,
    Y: np.ndarray,
    n_bootstrap: int = 5000,
    frame: str = DEFAULT_FRAME,
) -> dict:
    dkappa = compute_dkappa_residual(kappa_obs, X, Y, frame=frame)
    if frame == "rihtarsic2026":
        shock_x = SHOCK_X_KPC_RIHTARSIC
        normal = SHOCK_NORMAL_RIHTARSIC
    else:
        shock_x = SHOCK_X_KPC
        normal = SHOCK_NORMAL
    asig, kf, kb = asig_2d(
        dkappa, X, Y,
        shock_x_kpc=shock_x,
        normal=normal,
        strip_width_kpc=STRIP_WIDTH_KPC,
        strip_length_kpc=STRIP_LENGTH_KPC,
    )
    null = bootstrap_null(dkappa, X, Y, n_samples=n_bootstrap)
    sigma_null = float(null.std(ddof=1))
    p = float((np.abs(null) >= abs(asig)).mean())
    z = asig / sigma_null if sigma_null > 0 else 0.0

    if p <= P_VALUE_SUPPORT:
        verdict = "P2 supported (≥3σ shock-aligned A_sig on δκ)"
    elif p >= P_VALUE_FALSIFY:
        verdict = "P2 falsified (A_sig on δκ consistent with zero)"
    else:
        verdict = "inconclusive (between 2σ and 3σ; need higher-resolution data)"

    return {
        "test_id": "EFC-VAL-2026-004",
        "sealed_prediction": "P2",
        "doi": "10.6084/m9.figshare.31963668",
        "frame": frame,
        "shock_x_kpc": float(shock_x),
        "kappa_dkappa_front_mean": kf,
        "kappa_dkappa_back_mean": kb,
        "asig_residual": float(asig),
        "bootstrap_n_samples": n_bootstrap,
        "bootstrap_p_value": p,
        "null_std": sigma_null,
        "asig_over_sigma_null": float(z),
        "p_threshold_support": P_VALUE_SUPPORT,
        "p_threshold_falsify": P_VALUE_FALSIFY,
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
#   CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--kappa-fits", required=True,
        help="Path to JWST κ_obs FITS map (Cha+2025 or Rihtaršič+2026).",
    )
    parser.add_argument(
        "--source", required=True,
        choices=["Cha2025", "Rihtarsic2026"],
        help="Provenance label for the κ map.",
    )
    parser.add_argument(
        "--n-bootstrap", type=int, default=5000,
        help="Number of random-rotation null samples.",
    )
    parser.add_argument(
        "--frame", default=DEFAULT_FRAME,
        choices=["rihtarsic2026", "placeholder"],
        help="PIEMD subtraction frame. Default: rihtarsic2026.",
    )
    parser.add_argument(
        "--out", default=None,
        help="Optional output JSON path; default: stdout only.",
    )
    args = parser.parse_args(argv)

    km = load_kappa_fits(args.kappa_fits, source_label=args.source)
    result = killtest_on_residual(
        km.kappa, km.X, km.Y,
        n_bootstrap=args.n_bootstrap,
        frame=args.frame,
    )
    result["kappa_source"] = km.source
    result["kappa_fits_path"] = os.path.abspath(args.kappa_fits)

    text = json.dumps(result, indent=2)
    print(text)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
