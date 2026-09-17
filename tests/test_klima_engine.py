"""Tester for KlimaEngine — strålingsbalanse som energiflyt (L-040).

Klimaets energibalansemodell er EFC i ren form på jorden: energi inn
(sol), buffer (havets varmekapasitet), terskeloverganger. Motoren koder
ÉN av bryterne kortet navngir: is-albedo-bryteren med hysterese mot
snøballjord. AMOC er navngitt i kortet, men er IKKE kodet — den står
som åpen rest, ikke som påstand i denne motoren. Motoren er en
IDEALISERT 0D-energibalansemodell — IKKE en klimamodell-konkurrent, og
det står i selvbeskrivelsen.

Klima-motoren har UTSATT atlas-kobling: schema/regime_nodes.jsonld
roeres ikke for kollisjonsrekkefolgen er landet (t_bdf8e82f). Vakten
nederst gjor utsettelsen maskinelt synlig.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pytest

from efc_inference.engine.klima import TILSTANDER, KlimaEngine

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

_ATLAS = Path(__file__).resolve().parents[1] / "schema" / "regime_nodes.jsonld"
_SKJEMA = Path(__file__).resolve().parents[1] / "schema" / "regime_node.schema.json"

PARAMS = {
    "solarkonstant": 1361.0,       # W/m^2
    "albedo": 0.30,                # jordas gjennomsnitt
    "emissivitet": 0.61,           # effektiv (drivhuseffekt inkludert)
    "stefan_boltzmann": 5.670374419e-8,  # W/(m^2 K^4)
    "hav_varmekapasitet": 1.0e8,   # J/(m^2 K) — blandingslaget
}


def test_likevektstemperatur_maten():
    """Jordas effektive likevektstemperatur: ~288 K med drivhus."""
    e = KlimaEngine()
    t = e.likevektstemperatur(PARAMS)
    assert 280.0 < t < 295.0  # jorda ligger her med drivhus


def test_likevektstemperatur_uten_drivhus_kaldere():
    """Med emissivitet 1 (svart legeme) og albedo 0.3: ~255 K."""
    params_uten = {**PARAMS, "emissivitet": 1.0}
    e = KlimaEngine()
    t = e.likevektstemperatur(params_uten)
    forventet = (PARAMS["solarkonstant"] * (1 - PARAMS["albedo"])
                 / (4 * PARAMS["stefan_boltzmann"])) ** 0.25
    assert np.isclose(t, forventet, rtol=1e-9)


def test_is_albedo_tilbakekobling_er_positiv():
    """Is-albedo: kaldere -> mer is -> høyere albedo -> enda kaldere.
    Positiv tilbakekobling (forsterkning)."""
    e = KlimaEngine()
    forsterkning = e.albedo_tilbakekobling(PARAMS, delta_t=-1.0)
    assert forsterkning > 1.0  # forsterker, demper ikke


def test_bufferen_demper_forstyrrelser():
    """Havets varmekapasitet er bufferen: responsen på en
    strålingsforstyrrelse er treg — dempet og forsinket."""
    e = KlimaEngine()
    respons = e.tidskonstant(PARAMS)
    # tidskonstant = C / (4 eps sigma T^3) — år i praksis
    assert respons > 0
    assert respons / (365.25 * 86400) < 100  # under 100 år


def test_regimeskifte_ved_albedo_terskel():
    """Is-albedo-bryteren: over en terskel-albedo finnes ingen varm
    likevekt — systemet faller til snøballjord."""
    e = KlimaEngine()
    albedoer = np.linspace(0.3, 0.9, 7)
    stabile = [e.har_varm_likevekt({**PARAMS, "albedo": a})
               for a in albedoer]
    # ved høy albedo forsvinner den varme likevekten
    assert stabile[-1] is False
    assert stabile[0] is True


def test_hysterese_to_tilstandsavhengige_terskler():
    """Ekte hysterese: systemet faller fra «varm» ved alpha_fall,
    men returnerer fra «snøball» først ved alpha_retur (< alpha_fall).
    I vinduet mellom dem avhenger svaret av TILSTANDEN."""
    e = KlimaEngine()
    alpha_fall = e._alpha_ved_frysepunkt(PARAMS)
    alpha_retur = PARAMS.get("alpha_retur", 0.35)
    assert alpha_retur < alpha_fall
    # I hysteresebåndet: varm-tilstand sier «varm», snøball-tilstand
    # sier «ingen varm likevekt»
    midt = (alpha_fall + alpha_retur) / 2
    p = {**PARAMS, "albedo": midt}
    assert e.har_varm_likevekt(p, tilstand="varm") is True
    assert e.har_varm_likevekt(p, tilstand="snøball") is False


@pytest.mark.parametrize("ugyldig", [
    "snoball",     # ASCII-transliterasjon av «snøball»
    "snowball",
    "kald",
    "varm ",       # hale-space
    "SNØBALL",     # store bokstaver
    "",
    None,          # type utenfor kontrakten
    1,
])
def test_ukjent_tilstand_feiler_lukket(ugyldig):
    """En tilstand utenfor de kanoniske to skal FEILE — ikke leses som «varm».

    Målt før fiksen: hver av disse ga «varm»-svaret (True) midt i
    hysteresebåndet, der den kanoniske «snøball»-tilstanden sier False.
    Altså motsatt regime, uten et ord. Feilen er ikke akademisk: husets
    egen regel om kanonisk stavemåte finnes nettopp fordi
    translitterasjoner forekommer i praksis, og bryteren er den delen av
    motoren et kall utenfra treffer.
    """
    e = KlimaEngine()
    p = {**PARAMS, "albedo": 0.392}   # midt i hysteresebåndet
    with pytest.raises(ValueError):
        e.har_varm_likevekt(p, tilstand=ugyldig)


def test_tersklene_har_kjent_side():
    """Grensene skal ha KJENT side: «varm» faller ved alpha_fall (<=),
    «snøball» returnerer først UNDER alpha_retur (<). Verdiene settes
    eksakt fra de beregnede tersklene — ikke som alpha +/- en avrunding
    (husets egen erfaring: «nøyaktig 2 sigma» lander på 1.999999999).
    """
    e = KlimaEngine()
    alpha_fall = e._alpha_ved_frysepunkt(PARAMS)
    alpha_retur = PARAMS.get("alpha_retur", 0.35)
    assert alpha_retur < alpha_fall, "hysteresebåndet må ha positiv bredde"

    # på alpha_fall: varm likevekt finnes (<=), snøball-tilstanden sier nei
    p_fall = {**PARAMS, "albedo": alpha_fall}
    assert e.har_varm_likevekt(p_fall, "varm") is True
    assert e.har_varm_likevekt(p_fall, "snøball") is False

    # på alpha_retur: snøball-tilstanden sier fortsatt nei (streng <)
    assert e.har_varm_likevekt({**PARAMS, "albedo": alpha_retur},
                               "snøball") is False
    # like under: snøballen smelter tilbake
    assert e.har_varm_likevekt({**PARAMS, "albedo": alpha_retur - 1e-9},
                               "snøball") is True


def test_kanoniske_tilstander_er_de_eneste_godtatte():
    """Kontrakten skal vaere eksplisitt navngitt i koden, ikke bare i prosa."""
    assert set(TILSTANDER) == {"varm", "snøball"}
    e = KlimaEngine()
    p = {**PARAMS, "albedo": 0.392}
    for tilstand in TILSTANDER:
        assert isinstance(e.har_varm_likevekt(p, tilstand=tilstand), bool)


def test_regime_node_selvbeskrivelse():
    e = KlimaEngine()
    node = e.regime_node(PARAMS)
    assert node["id"] == "efc.klima_engine"
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "idealiser" in tekst or "0d" in tekst
    assert "ikke en klimamodell" in tekst or \
           "ikke klimamodell" in tekst
    assert node["regime"]["law_form"].strip()


@pytest.mark.parametrize("varmekapasitet", [1.0e8, 4.0e8, 6.3e9])
def test_selvbeskrivelsen_baerer_effektive_parametre(varmekapasitet):
    """Tallet i selvbeskrivelsen skal vaere UTTRYKT av parameterne, ikke
    skrevet inn. Testen leser tallet ut av teksten og sammenligner med
    den handregnede tidskonstanten for tre ulike varmekapasiteter — en
    hardkodet «tau ~ 1 år» faller på de to andre.
    """
    e = KlimaEngine()
    p = {**PARAMS, "hav_varmekapasitet": varmekapasitet}
    tau_aar = e.tidskonstant(p) / (365.25 * 86400)
    tekst = e.regime_node(p)["regime"]["validity"]
    treff = re.search(r"tau ~ (\d+) år", tekst)
    assert treff, f"selvbeskrivelsen mangler tidskonstanten: {tekst}"
    assert int(treff.group(1)) == round(tau_aar)


def test_regime_node_er_skjemavalid():
    """Selvbeskrivelsen skal vaere en gyldig RegimeNode etter skjemaet —
    samme maskinelle sjekk som bro-testene for de kosmologiske motorene.
    """
    if jsonschema is None:
        pytest.skip("jsonschema ikke installert")
    skjema = json.loads(_SKJEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(skjema["$defs"]["RegimeNode"])
    node = KlimaEngine().regime_node(PARAMS)
    feil = sorted(validator.iter_errors(node), key=lambda e: list(e.path))
    meldinger = "; ".join(f"{list(e.path)}: {e.message}" for e in feil[:3])
    assert not feil, f"efc.klima_engine feiler skjemaet: {meldinger}"


def test_klima_atlas_node_venter_paa_kollisjonsrekkefolgen():
    """Atlas-koblingen er UTSATT: schema/regime_nodes.jsonld røres ikke
    for kollisjonsrekkefølgen er landet (t_bdf8e82f, μ(k,z)-noden).

    Denne testen er en VAKT, ikke en påstand om at noe mangler: den
    feiler den dagen noden legges — med instruksen om hva som da skal
    gjøres. Uten den er utsettelsen bare prosa, og en manglende
    atlas-node ser lik ut som en glemt en.
    """
    atlas = json.loads(_ATLAS.read_text(encoding="utf-8"))
    if "efc.klima_engine" in {n["id"] for n in atlas["nodes"]}:
        pytest.fail(
            "efc.klima_engine finnes nå i atlaset: bytt denne vakten mot "
            "bro-testen (regime_node() == atlas-noden, maskinelt) og legg "
            "inn relasjonene til homo.okologi, homo.homeostase_buffer og "
            "homo.fluxus i schema/regime_nodes.jsonld.")
    assert KlimaEngine().regime_node(PARAMS)["id"] == "efc.klima_engine"
