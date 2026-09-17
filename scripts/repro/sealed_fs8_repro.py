"""Reproduction kit: den forseglede prediksjonen fσ8(z=0.7)=0.430.

Dette skriptet lar en ekstern person reprodusere den forseglede EFC-
prediksjonen fσ8(z≈0.7) ≈ 0.430 (DOI 10.6084/m9.figshare.32013156)
direkte fra repoets kildekode — uten nettverk, uten datafiler.

Kjoring:
    python scripts/repro/sealed_fs8_repro.py

Forventet output: fσ8(0.7) = 0.4301 (avvik fra forseglet 0.430:
0.0001, dvs. innen 0.5 %).

Hva skriptet gjor:
    1. Bygger EFCGrowth med EFCVariantC — varianten med μ-kanalen
       μ(a) = 1 + (μ_0 − 1)·g(a) («linear growth with entropy
       damping»), μ_0 = 0.5.
    2. Kjorer motoren med kanoniske parametre (Ω_m=0.3, H0=70,
       σ8=0.8) ved z=0.7.
    3. Sammenligner med den forseglede verdien og rapporterer.

Aerlighet: denne reproduksjonen viser at MOTOREN gir den forseglede
verdien med de deklarerte inngangene. Den viser IKKE at prediksjonen
er riktig mot data — det er arbiterens dom (sealed_fs8.py i
efc_inference/arbiter/).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# Repo-rot: to nivaer opp fra scripts/repro/
ROT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROT))

from efc_inference.engine.growth import EFCGrowth  # noqa: E402
from efc_inference.core.cosmology_model import EFCVariantC  # noqa: E402

FORSEGLET = 0.430
FORSEGLET_DOI = "10.6084/m9.figshare.32013156"
TOLERANSE = 0.005  # innen 0.5 % av den forseglede verdien

KANONISKE = {"Omega_m": 0.3, "H0": 70.0, "sigma8": 0.8,
             "alpha_cosmo": 0.0}
MU_0 = 0.5
Z_07 = np.array([0.7])


def main() -> int:
    g = EFCGrowth(cosmology=EFCVariantC())
    verdi = g.compute({**KANONISKE, "mu_0": MU_0}, Z_07)[0]
    if not np.isfinite(verdi):
        print("FEIL: motoren ga ikke-finitt verdi.")
        return 1
    avvik = abs(verdi - FORSEGLET)
    ok = avvik < TOLERANSE
    print("=== EFC forseglet-prediksjonsreproduksjon ===")
    print(f"Forseglet verdi:       fσ8(z≈0.7) = {FORSEGLET:.3f}")
    print(f"Forseglet kilde (DOI): {FORSEGLET_DOI}")
    print(f"Beregnet:              fσ8(z=0.7) = {verdi:.4f}")
    print(f"Avvik:                 {avvik:.4f} "
          f"({'OK — innen 0.5 %' if ok else 'UTENFOR toleransen'})")
    print(f"Innganger:             Ω_m={KANONISKE['Omega_m']}, "
          f"H0={KANONISKE['H0']}, σ8={KANONISKE['sigma8']}, "
          f"mu_0={MU_0} (EFCVariantC)")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
