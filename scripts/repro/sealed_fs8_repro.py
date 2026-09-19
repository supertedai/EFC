"""Reproduction kit: the sealed prediction fσ8(z=0.7)=0.430.

This script lets an external person reproduce the sealed EFC prediction
fσ8(z≈0.7) ≈ 0.430 (DOI 10.6084/m9.figshare.32013156) directly from the
repository's source code — without network, without data files.

Run:
    python scripts/repro/sealed_fs8_repro.py

Expected output: fσ8(0.7) = 0.4301 (deviation from the sealed 0.430:
0.0001, i.e. within 0.5 %).

What the script does:
    1. Builds EFCGrowth with EFCVariantC — the variant carrying the μ channel
       μ(a) = 1 + (μ_0 − 1)·g(a) ("linear growth with entropy
       damping"), μ_0 = 0.5.
    2. Runs the engine with canonical parameters (Ω_m=0.3, H0=70,
       σ8=0.8) at z=0.7.
    3. Compares against the sealed value and reports.

Honesty: this reproduction shows that the ENGINE returns the sealed value
with the declared inputs. It does NOT show that the prediction is right
against data — that is the arbiter's verdict (sealed_fs8.py in
efc_inference/arbiter/).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# Repo root: two levels up from scripts/repro/
ROT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROT))

from efc_inference.engine.growth import EFCGrowth  # noqa: E402
from efc_inference.core.cosmology_model import EFCVariantC  # noqa: E402

FORSEGLET = 0.430
FORSEGLET_DOI = "10.6084/m9.figshare.32013156"
TOLERANSE = 0.005  # RELATIVE: within 0.5 % of the sealed value

KANONISKE = {"Omega_m": 0.3, "H0": 70.0, "sigma8": 0.8,
             "alpha_cosmo": 0.0}
MU_0 = 0.5
Z_07 = np.array([0.7])


def main(compute_fn=None) -> int:
    if compute_fn is None:
        g = EFCGrowth(cosmology=EFCVariantC())
        compute_fn = lambda: g.compute({**KANONISKE, "mu_0": MU_0},  # noqa: E731
                                       Z_07)[0]
    verdi = compute_fn()
    if not np.isfinite(verdi):
        print("ERROR: the engine returned a non-finite value.")
        return 1
    avvik = abs(verdi - FORSEGLET) / FORSEGLET  # relative deviation
    ok = avvik < TOLERANSE
    print("=== EFC sealed prediction reproduction ===")
    print(f"Sealed value:          fσ8(z≈0.7) = {FORSEGLET:.3f}")
    print(f"Sealed source (DOI):   {FORSEGLET_DOI}")
    print(f"Computed:              fσ8(z=0.7) = {verdi:.4f}")
    print(f"Relative deviation:    {avvik:.5f} "
          f"({'OK — within 0.5 %' if ok else 'OUTSIDE the tolerance'})")
    print(f"Inputs:                Ω_m={KANONISKE['Omega_m']}, "
          f"H0={KANONISKE['H0']}, σ8={KANONISKE['sigma8']}, "
          f"mu_0={MU_0} (EFCVariantC)")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
