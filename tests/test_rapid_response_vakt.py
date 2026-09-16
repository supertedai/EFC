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
    """LRG/ELG med z i vinduet og fsigma8+sigma er arbiter-målingen."""
    melding = {
        "hoder": {"tracer": "LRG", "survey": "DESI DR2",
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
