"""Tester for den forseglede fσ8-arbiteren (trinn 12).

Arbiteren er den maskinelle dommeren mot den forseglede EFC-
prediksjonen P2: fσ8(z=0.7) = 0.430 (EFC) vs 0.449 (ΛCDM),
forseglet 2026-04-14, DOI 10.6084/m9.figshare.32013156.

Dommelogikken er treverdig — PASS / FAIL / VENTER — og hver dom
skal baere regelen som felte den, med kilde.
"""
from __future__ import annotations

import numpy as np

from efc_inference.arbiter.sealed_fs8 import SealedFs8Arbiter


def _arbiter() -> SealedFs8Arbiter:
    return SealedFs8Arbiter()


def test_nullmodellen_gir_lcdm_innen_toleranse():
    """ΛCDM-nullmodellen (alpha_cosmo=0) skal gi fσ8(z=0.7) nær den
    forseglede ΛCDM-verdien 0.449. Dette er arbiterens kalibrering:
    uten den er dommene uforankret."""
    arb = _arbiter()
    null = arb.nullmodell()
    assert abs(null - 0.449) < 0.02, (
        f"nullmodellen ga {null}, forventet nær 0.449")


def test_prediksjon_er_parameter_avledet():
    """Prediksjonen skal komme fra motoren med gitte parametre — ikke
    vaere hardkodet 0.430."""
    arb = _arbiter()
    pred = arb.prediksjon_efc({"Omega_m": 0.3, "H0": 70.0,
                               "sigma8": 0.8, "alpha_cosmo": 0.1})
    assert isinstance(pred, float)
    assert np.isfinite(pred)
    # Parameterforskjell skal gi ulik verdi (ikke en konstant).
    pred2 = arb.prediksjon_efc({"Omega_m": 0.3, "H0": 70.0,
                                "sigma8": 0.8, "alpha_cosmo": 0.2})
    assert pred != pred2


def test_uten_maaling_venter_arbiteren():
    """Uten DESI DR2 full-shape-målingen skal arbiteren si VENTER —
    og si HVORFOR (hva som mangler)."""
    dom = _arbiter().vurder(None)
    assert dom["status"] == "VENTER"
    assert "DR2" in dom["årsak"] and "full-shape" in dom["årsak"]


def test_maaling_innen_1sigma_av_0430_gir_pass():
    """Bekreftelseskriteriet: innen ~1σ av 0.430 → PASS."""
    måling = {"fsigma8": 0.430, "sigma": 0.030, "z_eff": 0.7,
              "kilde": "DESI DR2 full-shape (syntetisk test)"}
    dom = _arbiter().vurder(måling)
    assert dom["status"] == "PASS"
    assert dom["regel"]  # hvilken regel som felte dommen
    assert dom["kilde"]  # hvor regelen står


def test_maaling_over_0449_ved_mer_enn_3sigma_gir_fail():
    """Falsifikasjon A: >0.449 ved >3σ → FAIL (P2 damage-test)."""
    måling = {"fsigma8": 0.510, "sigma": 0.020, "z_eff": 0.7,
              "kilde": "DESI DR2 full-shape (syntetisk test)"}
    dom = _arbiter().vurder(måling)
    assert dom["status"] == "FAIL"


def test_maaling_konsistent_med_lcdm_innen_1sigma_gir_fail():
    """Falsifikasjon B: konsistent med 0.449 innen <1σ → FAIL.
    (Målingen maa IKKE samtidig vaere innen 1σ av 0.430 — da vinner
    bekreftelsen.)"""
    måling = {"fsigma8": 0.455, "sigma": 0.020, "z_eff": 0.7,
              "kilde": "DESI DR2 full-shape (syntetisk test)"}
    dom = _arbiter().vurder(måling)
    assert dom["status"] == "FAIL"


def test_mellomliggende_maaling_venter():
    """Måling som verken bekrefter eller falsifiserer → VENTER.
    (Ikke innen 1σ av 0.430, ikke >3σ over 0.449, ikke <1σ fra 0.449,
    ikke ekskluderer 0.430 ved ≥2σ.)"""
    måling = {"fsigma8": 0.500, "sigma": 0.040, "z_eff": 0.7,
              "kilde": "DESI DR2 full-shape (syntetisk test)"}
    dom = _arbiter().vurder(måling)
    assert dom["status"] == "VENTER"


def test_rapporten_sier_arlig_at_mu_kanalen_mangler():
    """Den forseglede prediksjonen hviler på μ<1 (B-kanalen i
    perturbasjonen). Motorlagets growth-API har per i dag mu=1 —
    arbiteren skal si det ÅPENLYST, ikke late som prediksjonen er
    maskinelt reprodusert."""
    rapport = _arbiter().rapport()
    assert rapport["mu_kanal_i_motorlaget"] is False
    assert "0.430" in rapport["ærlighet"]


def test_payload_har_kriterium_og_proveniens():
    """Busspayloaden skal baere kriteriet og full proveniens."""
    p = _arbiter().payload()
    assert p["emne"] == "kosmos.kosmologi.utfall.efc-fs8-arbiter"
    assert p["kriterium"]["prediksjon_efc"] == 0.430
    assert p["kriterium"]["forseglet_doi"] == "10.6084/m9.figshare.32013156"
    assert p["proveniens"]["generert_av"] == "SealedFs8Arbiter"
