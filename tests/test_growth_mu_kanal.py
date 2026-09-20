"""Tests for the mu channel in the growth engine (step 13).

The sealed prediction fσ8(z=0.7)=0.430 rests on mu<1 ("linear
growth with entropy damping"). CosmologyModel already has the channel —
EFCVariantC: mu(a) = 1 + (mu_0 - 1) * g(a) — but the growth engine API
lacked mu_0. These tests establish that the channel is wired up,
backward compatible and reproduces the sealed value.
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
    """Without mu_0 (or with mu_0=1.0) the curve must be identical to
    the current one — no surprises for existing runs."""
    g = EFCGrowth()
    uten = g.compute(KANONISKE, Z_07)[0]
    med_default = g.compute({**KANONISKE, "mu_0": 1.0}, Z_07)[0]
    assert np.isfinite(uten)
    assert uten == med_default


def test_mu_kanal_demper_veksten_monotont():
    """mu_0 < 1 must give a LOWER fσ8, monotonically falling in mu_0 —
    that is the suppression channel itself in the sealed prediction."""
    g = EFCGrowth(cosmology=EFCVariantC())
    verdier = [g.compute({**KANONISKE, "mu_0": mu}, Z_07)[0]
               for mu in (1.0, 0.9, 0.8, 0.7, 0.5)]
    assert all(np.isfinite(v) for v in verdier)
    assert verdier == sorted(verdier, reverse=True), verdier
    assert verdier[-1] < verdier[0]  # actual damping


def test_mu_kanal_reproduserer_forseglet_prediksjon():
    """At mu_0=0.5 (canonical parameters) the engine gives 0.4301 — the
    sealed prediction 0.430 is reproduced within 0.5 %."""
    g = EFCGrowth(cosmology=EFCVariantC())
    v = g.compute({**KANONISKE, "mu_0": 0.5}, Z_07)[0]
    assert abs(v - FORSEGLET_0430) < 0.005, v


def test_mu0_ugyldig_avvises():
    """mu_0 outside [0, 2] is unphysical (mu can become negative) and must
    be rejected with NaN — not silently miscalculated."""
    g = EFCGrowth(cosmology=EFCVariantC())
    for mu in (-0.5, 2.5):
        v = g.compute({**KANONISKE, "mu_0": mu}, Z_07)[0]
        assert np.isnan(v), mu


def test_mu0_ugyldig_type_avvises_uten_exception():
    """Strings — ALSO numeric ones — None and bool are not valid mu_0
    values. They must be rejected under control (NaN), never crash or
    be converted silently."""
    g = EFCGrowth(cosmology=EFCVariantC())
    for mu in ("bad", "0.5", "1.0", None, True, False):
        v = g.compute({**KANONISKE, "mu_0": mu}, Z_07)[0]
        assert np.isnan(v), mu


def test_varianta_har_ingen_mu_kanal_og_endres_ikke():
    """EFCVariantA has μ=1 hardcoded — mu_0 must NOT change the curve there,
    and the engine self-description must say the variant lacks the channel."""
    g = EFCGrowth(cosmology=EFCVariantA())
    without_mu = g.compute(KANONISKE, Z_07)[0]
    with_mu = g.compute({**KANONISKE, "mu_0": 0.5}, Z_07)[0]
    assert without_mu == with_mu
    node = g.regime_node({**KANONISKE, "mu_0": 1.0})
    assert "mu" in node["regime"]["validity"].lower() or \
           "uten" in node["regime"]["validity"].lower()
