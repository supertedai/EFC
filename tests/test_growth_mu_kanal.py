"""Tester for μ-kanalen i growth-motoren (trinn 13).

Den forseglede prediksjonen fσ8(z=0.7)=0.430 hviler på μ<1 («linear
growth with entropy damping»). CosmologyModel har kanalen allerede —
EFCVariantC: mu(a) = 1 + (mu_0 - 1) * g(a) — men growth-motorens API
manglet mu_0. Disse testene fastslår at kanalen er koblet, bakover-
kompatibel og reproduserer den forseglede verdien.
"""
from __future__ import annotations

import numpy as np

from efc_inference.engine.growth import EFCGrowth
from efc_inference.core.cosmology_model import EFCVariantA, EFCVariantC

FORSEGLET_0430 = 0.430
KANONISKE = {"Omega_m": 0.3, "H0": 70.0, "sigma8": 0.8,
             "alpha_cosmo": 0.0}
Z_07 = np.array([0.7])


def test_mu0_default_er_bakoverkompatibel():
    """Uten mu_0 (eller mu_0=1.0) skal kurven vaere identisk med
    dagens — ingen overraskelser for eksisterende kjoeringer."""
    g = EFCGrowth()
    uten = g.compute(KANONISKE, Z_07)[0]
    med_default = g.compute({**KANONISKE, "mu_0": 1.0}, Z_07)[0]
    assert np.isfinite(uten)
    assert uten == med_default


def test_mu_kanal_demper_veksten_monotont():
    """mu_0 < 1 skal gi LAVERE fσ8, monotont fallende i mu_0 — det er
    selve suppressjonskanalen i den forseglede prediksjonen."""
    g = EFCGrowth(cosmology=EFCVariantC())
    verdier = [g.compute({**KANONISKE, "mu_0": mu}, Z_07)[0]
               for mu in (1.0, 0.9, 0.8, 0.7, 0.5)]
    assert all(np.isfinite(v) for v in verdier)
    assert verdier == sorted(verdier, reverse=True), verdier
    assert verdier[-1] < verdier[0]  # faktisk demping


def test_mu_kanal_reproduserer_forseglet_prediksjon():
    """Ved mu_0=0.5 (kanoniske parametre) gir motoren 0.4301 — den
    forseglede prediksjonen 0.430 er reprodusert innen 0.5 %."""
    g = EFCGrowth(cosmology=EFCVariantC())
    v = g.compute({**KANONISKE, "mu_0": 0.5}, Z_07)[0]
    assert abs(v - FORSEGLET_0430) < 0.005, v


def test_mu0_ugyldig_avvises():
    """mu_0 utenfor [0, 2] er ufysisk (μ kan bli negativ) og skal
    avvises med NaN — ikke stille feilberegnes."""
    g = EFCGrowth(cosmology=EFCVariantC())
    for mu in (-0.5, 2.5):
        v = g.compute({**KANONISKE, "mu_0": mu}, Z_07)[0]
        assert np.isnan(v), mu


def test_varianta_har_ingen_mu_kanal_og_endres_ikke():
    """EFCVariantA har μ=1 hardkodet — mu_0 skal IKKE endre kurven der,
    og motorens selvbeskrivelse skal si at varianten mangler kanalen."""
    g = EFCGrowth(cosmology=EFCVariantA())
    uten = g.compute(KANONISKE, Z_07)[0]
    med = g.compute({**KANONISKE, "mu_0": 0.5}, Z_07)[0]
    assert uten == med
    node = g.regime_node({**KANONISKE, "mu_0": 1.0})
    assert "mu" in node["regime"]["validity"].lower() or \
           "uten" in node["regime"]["validity"].lower()
