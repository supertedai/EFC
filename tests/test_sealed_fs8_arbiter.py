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


def _m(fs8, sigma, tracer="LRG", z_eff=0.7,
       kilde="DESI DR2 full-shape (syntetisk test)"):
    return {"fsigma8": fs8, "sigma": sigma, "z_eff": z_eff,
            "tracer": tracer, "kilde": kilde}


# ----------------------------------------------------------------------
# Kalibrering og parameter-avledethet
# ----------------------------------------------------------------------
def test_nullmodellen_gir_lcdm_innen_toleranse():
    """ΛCDM-nullmodellen (alpha_cosmo=0) skal gi fσ8(z=0.7) nær den
    forseglede ΛCDM-verdien 0.449. Uten den er dommene uforankret."""
    null = _arbiter().nullmodell()
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
    pred2 = arb.prediksjon_efc({"Omega_m": 0.3, "H0": 70.0,
                                "sigma8": 0.8, "alpha_cosmo": 0.2})
    assert pred != pred2


def test_vurder_rapporterer_motorprediksjon_separat():
    """Når parametre gis, skal dommen baere motorprediksjonen EKSPLISITT
    — og den skal vaere motorens verdi, ikke ankeret."""
    params = {"Omega_m": 0.3, "H0": 70.0, "sigma8": 0.8,
              "alpha_cosmo": 0.1}
    arb = _arbiter()
    dom = arb.vurder(_m(0.440, 0.03), params=params)
    assert dom["motorprediksjon"] == arb.prediksjon_efc(params)
    assert "avstand_motorprediksjon_sigma" in dom


# ----------------------------------------------------------------------
# VENTER uten måling / ugyldige målinger
# ----------------------------------------------------------------------
def test_uten_maaling_venter_arbiteren():
    dom = _arbiter().vurder(None)
    assert dom["status"] == "VENTER"
    assert "DR2" in dom["årsak"] and "full-shape" in dom["årsak"]


def test_manglende_felt_venter():
    for felt in ("fsigma8", "sigma", "z_eff", "tracer", "kilde"):
        m = _m(0.440, 0.03)
        m[felt] = None
        dom = _arbiter().vurder(m)
        assert dom["status"] == "VENTER", felt
        assert "invalid" in dom["årsak"]


def test_ugyldig_sigma_venter():
    for sigma in (0.0, -0.02, float("nan"), float("inf")):
        dom = _arbiter().vurder(_m(0.440, sigma))
        assert dom["status"] == "VENTER", sigma


def test_feil_tracer_venter():
    """Lyα er en annen tracer enn galakse-RSD — dommen skal ikke felles."""
    dom = _arbiter().vurder(_m(0.440, 0.03, tracer="LyA"))
    assert dom["status"] == "VENTER"
    assert "tracer" in dom["årsak"]


def test_feil_z_vindu_venter():
    for z in (0.3, 1.2):
        dom = _arbiter().vurder(_m(0.440, 0.03, z_eff=z))
        assert dom["status"] == "VENTER", z


# ----------------------------------------------------------------------
# Bekreftelse (innen ~1σ av 0.430)
# ----------------------------------------------------------------------
def test_innen_1sigma_av_anker_gir_pass():
    dom = _arbiter().vurder(_m(0.440, 0.03))   # 0.33σ
    assert dom["status"] == "PASS"
    assert dom["regel"] and dom["kilde"]


def test_akkurat_1sigma_gir_pass():
    """Grensen er ≤1σ (inklusive) — «~1σ»."""
    dom = _arbiter().vurder(_m(0.430 + 0.02, 0.02))  # nøyaktig 1.0σ
    assert dom["status"] == "PASS"


def test_over_1sigma_av_anker_gir_ikke_pass_alene():
    """1.25σ fra ankeret er ikke bekreftelse — dommen må komme fra en
    annen regel eller bli VENTER."""
    dom = _arbiter().vurder(_m(0.455, 0.02))  # 1.25σ fra 0.430
    # 0.455 er 0.3σ fra 0.449 → FAIL via P1 (konsistent med ΛCDM),
    # ikke PASS.
    assert dom["status"] != "PASS"


# ----------------------------------------------------------------------
# Falsifikasjon A (P2: >0.449 ved >3σ)
# ----------------------------------------------------------------------
def test_over_3sigma_over_lcdm_gir_fail():
    dom = _arbiter().vurder(_m(0.449 + 4 * 0.02, 0.02))  # 4.0σ over
    assert dom["status"] == "FAIL"
    assert "P2" in dom["regel"] or "damage" in dom["regel"]


def test_akkurat_3sigma_over_lcdm_gir_ikke_p2_fail():
    """Nøyaktig 3.0σ over 0.449 er IKKE «>3σ» — men 3.95σ fra ankeret
    utløser P1-eksklusjonen (≥2σ), så dommen er fortsatt FAIL — bare
    med en annen regel."""
    dom = _arbiter().vurder(_m(0.449 + 3 * 0.02, 0.02))
    assert dom["status"] == "FAIL"
    assert "P2" not in dom["regel"]


# ----------------------------------------------------------------------
# Falsifikasjon B (P1)
# ----------------------------------------------------------------------
def test_konsistent_med_lcdm_innen_1sigma_gir_fail():
    dom = _arbiter().vurder(_m(0.455, 0.02))  # 0.3σ fra 0.449
    assert dom["status"] == "FAIL"


def test_ekskluderer_anker_over_2sigma_gir_fail():
    dom = _arbiter().vurder(_m(0.430 + 2 * 0.02, 0.02))  # 2.0σ over
    assert dom["status"] == "FAIL"


def test_ekskluderer_anker_under_2sigma_gir_fail():
    """Eksklusjon er tosidig: en måling UNDER 0.430 ved ≥2σ
    ekskluderer ankeret like mye som en over."""
    dom = _arbiter().vurder(_m(0.430 - 2 * 0.02, 0.02))  # 2.0σ under
    assert dom["status"] == "FAIL"


def test_under_2sigma_fra_begge_ankre_venter():
    """1.75σ fra 0.430 og 1.25σ fra 0.449 (med m>0.449: ikke >3σ) —
    verken bekreftet, ekskludert eller ΛCDM-konsistent → VENTER."""
    dom = _arbiter().vurder(_m(0.500, 0.04))
    assert dom["status"] == "VENTER"


# ----------------------------------------------------------------------
# Rapporten og payloaden
# ----------------------------------------------------------------------
def test_rapporten_maaler_mu_kanalen_arlig():
    """Trinn 13 koblet μ-kanalen inn (EFCVariantC, mu_0). Rapporten
    skal MÅLE den faktiske tilstanden — både den injiserte motoren og
    motorlagets kapabilitet. Reproduksjonen skal vaere dokumentert med
    tall, og teksten skal skille reproduserbarhet fra bevis om
    forseglet parameterverdi."""
    rapport = _arbiter().rapport()
    # Default-motoren er EFCVariantA — den har IKKE kanalen...
    assert rapport["mu_kanal_i_injisert_motor"] is False
    # ...men motorlagets kapabilitet (VariantC) er målt og dokumentert.
    rep = rapport["mu_reproduksjon_variantc"]
    assert rep["variant"] == "EFCVariantC"
    assert abs(rep["fs8_mu_0_5"] - 0.430) < 0.005
    assert "reproducible" in rapport["ærlighet"]
    assert "NOT" in rapport["ærlighet"]  # beviser ikke forseglet mu_0
    assert "does NOT have the μ channel" in rapport["ærlighet"]  # injisert variant rapportert


def test_rapporten_med_variantc_sier_den_injiserte_har_kanalen():
    """Med EFCVariantC injisert skal statusen si det — variant-bevisst,
    ikke hardkodet."""
    from efc_inference.core.cosmology_model import EFCVariantC
    from efc_inference.engine.growth import EFCGrowth
    arb = SealedFs8Arbiter(growth=EFCGrowth(cosmology=EFCVariantC()))
    rapport = arb.rapport()
    assert rapport["mu_kanal_i_injisert_motor"] is True
    assert "HAS" in rapport["ærlighet"]


def test_payload_har_kriterium_og_proveniens():
    p = _arbiter().payload()
    assert p["emne"] == "kosmos.kosmologi.oppgjoer.efc-fs8-arbiter"
    assert p["kriterium"]["anker_efc"] == 0.430
    assert p["kriterium"]["forseglet_doi"] == "10.6084/m9.figshare.32013156"
    assert p["proveniens"]["generert_av"] == "SealedFs8Arbiter"
