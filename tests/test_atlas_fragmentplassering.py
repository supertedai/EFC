"""Fragmentplassering: naboene skal komme fra ord som BESKRIVER noe.

Maalt 2026-09-18: `--plasser "varmepumpe med CO2 som kjolemiddel"` svarte
«svakt» og foreslo `homo.fluxus, homo.homeostase_buffer, homo.hjerte_syklus,
homo.cellesyklus` — en varmepumpe fikk hjertesyklusen som nabo. Aarsaken var
at matcheren bare filtrerte paa ordlengde > 2, saa «med» og «som» ble
soekeord. De staar i nesten hver nodetekst, og listen som kom ut SA ut som et
plasseringsforslag.

Klassen er den samme som ellers i huset: en fallback som svarer. Testene under
laaser at naboene enten er baaret av et ord som betyr noe, eller at listen er
merket som ordlikhet — ikke som et forslag.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts"))

import atlas_lesing  # noqa: E402


def _plasser(tekst: str) -> dict:
    atlas = atlas_lesing.les_atlas(ROT, "HEAD", sti="schema/regime_nodes.jsonld")
    return atlas_lesing.plasser(atlas, tekst)


def test_funksjonsord_baerer_ikke_plassering() -> None:
    """Et fragment av bare funksjonsord har ingen naboer og ingen hjem."""
    svar = _plasser("med som under mellom")
    naboer = [n for f in svar["forslag"] for n in f.get("noder", [])]
    assert not naboer, f"funksjonsord ga naboer: {naboer}"
    assert svar["status"] == "uten_hjem", svar
    assert svar["domene_visshet"] == "ingen_anelse", svar


def test_varmepumpe_faar_ikke_hjertesyklusen_som_nabo() -> None:
    """Den maalte feilen, direkte."""
    svar = _plasser("varmepumpe med CO2 som kjolemiddel")
    naboer = [n for f in svar["forslag"] for n in f.get("noder", [])]
    falske = [n for n in naboer if n.startswith(("homo.hjerte", "homo.cellesyk",
                                                 "homo.fluxus"))]
    assert not falske, f"funksjonsord ga falske naboer: {falske}"


def test_ordet_som_beskriver_noe_finner_fortsatt_noden() -> None:
    """Rettingen skal ikke drepe signalet."""
    svar = _plasser("vulkansk aske")
    naboer = [n for f in svar["forslag"] for n in f.get("noder", [])]
    assert "kosmos.jord.vulkan" in naboer, svar


def test_batterifragmentet_finner_batterinodene() -> None:
    svar = _plasser("energiflyt i batteriet under lading")
    naboer = [n for f in svar["forslag"] for n in f.get("noder", [])]
    assert any(n.startswith("batteri.") for n in naboer), svar


def test_ordlikhet_merkes_som_ikke_forslag() -> None:
    """Naar lista bare er ordlikhet, skal den si det — ikke se ut som et forslag."""
    svar = _plasser("vulkansk aske")
    avledet = [f for f in svar["forslag"] if f["domene"] == "(avledet)"]
    assert avledet, svar
    kobling = avledet[0]["kobling"]
    assert "ORDLIKHET" in kobling and "ikke et plasseringsforslag" in kobling, kobling


def test_stoppordlista_spiser_ikke_innholdsord() -> None:
    """En stoppordliste som tar innholdsord gjoer atlaset blindt, ikke strengere."""
    for ordet in ("energi", "flyt", "entropi", "buffer", "regime", "varme",
                  "motor", "felt", "gradient", "masse", "node", "kraft"):
        assert ordet not in atlas_lesing.STOPPORD, ordet
