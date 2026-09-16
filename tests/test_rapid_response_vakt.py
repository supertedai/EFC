"""Tester for rapid-response-vakten (trinn 14).

Vakten er det siste leddet i den forseglede kjeden: når DESI DR2
full-shape galakse-RSD fσ8(z~0.7) publiseres, skal dommen felles
automatisk — ikke vente på manuell kjøring.

Vakten er REN: den tar inn den siste buss-meldingen og prosesserer
den — buss-hentingen er kallens ansvar (injiserbar kilde).
"""
from __future__ import annotations

import json
from pathlib import Path

from efc_inference.arbiter.rapid_response import RapidResponseVakt

# Den faktiske forseglede baseline-meldingen slik den ligger på bussen
# (anonymisert): DESI DR1 QSO ved z=1.491 — IKKE arbiter-målingen.
BASELINE_MELDING = {
    "hoder": {
        "Nats-Msg-Id": "efc-fs8.v1.DESI_DR1.QSO.1.4910.040249dce30b",
        "kilde": "efc-sealed-baseline",
        "observabel": "fsigma8",
        "survey": "DESI DR1",
        "tracer": "QSO",
        "arbiter": "nei",
        "arbiter_venter_paa": "DESI DR2 full-shape",
    },
    "maalt": {"fsigma8": 0.318, "fsigma8_sigma": 0.076, "z_eff": 1.491},
}


def _vakt(tmp_path: Path) -> RapidResponseVakt:
    return RapidResponseVakt(artefakt_sti=str(tmp_path / "dom.json"))


def test_gjenkjenner_galakse_rsd_maaling():
    """LRG/ELG med full DR2-proveniens, z i vinduet og fsigma8+sigma
    er arbiter-målingen."""
    melding = {
        "hoder": {"tracer": "LRG", "survey": "DESI DR2",
                  "observabel": "fsigma8",
                  "kilde": "desi-dr2-full-shape"},
        "maalt": {"fsigma8": 0.440, "fsigma8_sigma": 0.030, "z_eff": 0.7},
    }
    m = _vakt(Path("/tmp")).gjenkjenn(melding)
    assert m == {"fsigma8": 0.440, "sigma": 0.030, "z_eff": 0.7,
                 "tracer": "LRG", "kilde": "desi-dr2-full-shape"}


def test_baseline_er_ikke_maaling():
    """Den forseglede baselinen (DR1 QSO, z=1.491) skal IKKE felle dom —
    det er referanseverdier, ikke arbiter-målingen."""
    assert _vakt(Path("/tmp")).gjenkjenn(BASELINE_MELDING) is None


def test_avviser_lya():
    melding = {
        "hoder": {"tracer": "LyA", "survey": "DESI DR2",
                  "kilde": "desi-dr2-lya"},
        "maalt": {"fsigma8": 0.440, "fsigma8_sigma": 0.030, "z_eff": 0.7},
    }
    assert _vakt(Path("/tmp")).gjenkjenn(melding) is None


def test_avviser_z_utenfor_vindu():
    melding = {
        "hoder": {"tracer": "ELG", "survey": "DESI DR2",
                  "kilde": "desi-dr2-full-shape"},
        "maalt": {"fsigma8": 0.440, "fsigma8_sigma": 0.030, "z_eff": 1.4},
    }
    assert _vakt(Path("/tmp")).gjenkjenn(melding) is None


def test_avviser_maaling_uten_sigma():
    melding = {
        "hoder": {"tracer": "LRG", "survey": "DESI DR2",
                  "kilde": "desi-dr2-full-shape"},
        "maalt": {"fsigma8": 0.440, "z_eff": 0.7},
    }
    assert _vakt(Path("/tmp")).gjenkjenn(melding) is None


def test_baseline_gir_venter_dom_og_artefakt(tmp_path):
    """Kjøring mot den ekte baselinen: VENTER med årsak, artefakt
    skrevet med proveniens."""
    vakt = _vakt(tmp_path)
    payload = vakt.sjekk(BASELINE_MELDING)
    assert payload["rapport"]["dom"]["status"] == "VENTER"
    artefakt = json.loads((tmp_path / "dom.json").read_text())
    assert artefakt["rapport"]["dom"]["status"] == "VENTER"
    assert artefakt["proveniens"]["generert_av"] == "RapidResponseVakt"
    assert artefakt["proveniens"]["generert_tid"]


def test_maaling_feller_dom(tmp_path):
    """En ekte galakse-RSD-måling i vinduet feller dommen."""
    melding = {
        "hoder": {"tracer": "LRG", "survey": "DESI DR2",
                  "observabel": "fsigma8",
                  "kilde": "desi-dr2-full-shape"},
        "maalt": {"fsigma8": 0.510, "fsigma8_sigma": 0.020, "z_eff": 0.7},
    }
    vakt = _vakt(tmp_path)
    payload = vakt.sjekk(melding)
    assert payload["rapport"]["dom"]["status"] == "FAIL"  # >0.449 ved >3σ
    artefakt = json.loads((tmp_path / "dom.json").read_text())
    assert artefakt["rapport"]["dom"]["status"] == "FAIL"


def test_melding_uten_hoder_avvises(tmp_path):
    """Ugyldig/ukjent meldingsform skal ikke krasje vakten."""
    vakt = _vakt(tmp_path)
    payload = vakt.sjekk({"ukjent": "struktur"})
    assert payload["rapport"]["dom"]["status"] == "VENTER"


def _dr2_melding(**endringer):
    melding = {
        "hoder": {"tracer": "LRG", "survey": "DESI DR2",
                  "observabel": "fsigma8",
                  "kilde": "desi-dr2-full-shape",
                  "Nats-Msg-Id": "dr2-full-shape.lrg.0.7.test"},
        "maalt": {"fsigma8": 0.440, "fsigma8_sigma": 0.030, "z_eff": 0.7},
    }
    for k, v in endringer.items():
        if k in ("tracer", "survey", "observabel", "kilde", "Nats-Msg-Id"):
            melding["hoder"][k] = v
        else:
            melding["maalt"][k] = v
    return melding


def test_ugyldig_z_eff_krasjer_ikke(tmp_path):
    """Streng, NaN og uendelig z_eff skal gi VENTER med årsak — aldri
    ValueError fra diagnoseveien."""
    vakt = _vakt(tmp_path)
    for z in ("not-a-number", float("nan"), float("inf")):
        payload = vakt.sjekk(_dr2_melding(z_eff=z))
        assert payload["rapport"]["dom"]["status"] == "VENTER", z
        assert "z_eff" in payload["rapport"]["dom"]["årsak"]


def test_falsk_lrg_uten_dr2_proveniens_avvises(tmp_path):
    """En vilkårlig LRG-melding uten DESI DR2 full-shape-survey/kilde
    er ikke kriteriets måling."""
    vakt = _vakt(tmp_path)
    # Feil survey
    p1 = vakt.sjekk(_dr2_melding(survey="BOSS DR12"))
    assert p1["rapport"]["dom"]["status"] == "VENTER"
    assert "DR2" in p1["rapport"]["dom"]["årsak"]
    # Feil observabel
    p2 = vakt.sjekk(_dr2_melding(observabel="fz8"))
    assert p2["rapport"]["dom"]["status"] == "VENTER"
    # Baseline-markert (arbiter: nei) selv med riktig alt annet
    melding = _dr2_melding()
    melding["hoder"]["arbiter"] = "nei"
    p3 = vakt.sjekk(melding)
    assert p3["rapport"]["dom"]["status"] == "VENTER"
    assert "baseline" in p3["rapport"]["dom"]["årsak"]


def test_artefakt_baerer_full_input_proveniens(tmp_path):
    """Artefakten skal kunne knytte dommen tilbake til konkret
    bussmelding: meldings-ID, hash, gjenkjent måling og params."""
    melding = _dr2_melding()
    params = {"Omega_m": 0.3, "H0": 70.0, "sigma8": 0.8,
              "alpha_cosmo": 0.0, "mu_0": 0.5}
    vakt = _vakt(tmp_path)
    payload = vakt.sjekk(melding, params=params)
    inp = payload["input"]
    assert inp["meldings_id"] == "dr2-full-shape.lrg.0.7.test"
    assert len(inp["meldings_hash_sha256"]) == 64
    assert inp["gjenkjent_maaling"]["tracer"] == "LRG"
    assert inp["params"] == params

    artefakt = json.loads((tmp_path / "dom.json").read_text())
    assert artefakt["input"]["meldings_id"] == "dr2-full-shape.lrg.0.7.test"
    assert artefakt["input"]["meldings_hash_sha256"] == \
        inp["meldings_hash_sha256"]


def test_gyldig_dr2_maaling_gjenkjennes(tmp_path):
    """Full DR2-proveniens i hodene → målingen gjenkjennes og dommen
    felles (her: PASS, innen ~1σ av ankeret)."""
    melding = _dr2_melding(fsigma8=0.430, fsigma8_sigma=0.030)
    vakt = _vakt(tmp_path)
    payload = vakt.sjekk(melding)
    assert payload["rapport"]["dom"]["status"] == "PASS"
