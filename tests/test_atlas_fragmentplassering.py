"""Fragment placement: the neighbours must come from words that DESCRIBE something.

Measured 2026-09-18: a Norwegian probe naming a heat pump answered
«svakt» and proposed `homo.fluxus, homo.homeostase_buffer, homo.hjerte_syklus,
homo.cellesyklus` — a heat pump got the heart cycle as its neighbour. The cause
was that the matcher filtered only on word length > 2, so the two function
words in the fragment became search words. They stand in almost every node
text, and the list that came out LOOKED like a placement suggestion.

The class is the same as elsewhere in the house: a fallback that answers. The
tests below lock that the neighbours are either carried by a word that means
something, or that the list is tagged as word similarity — not as a suggestion.
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
    """A fragment of only function words has no neighbours and no home."""
    svar = _plasser("med som under mellom")
    naboer = [n for f in svar["forslag"] for n in f.get("noder", [])]
    assert not naboer, f"function words gave neighbours: {naboer}"
    assert svar["status"] == "uten_hjem", svar
    assert svar["domene_visshet"] == "ingen_anelse", svar


def test_varmepumpe_faar_ikke_hjertesyklusen_som_nabo() -> None:
    """The measured error, directly."""
    svar = _plasser("varmepumpe med CO2 som kjolemiddel")
    naboer = [n for f in svar["forslag"] for n in f.get("noder", [])]
    falske = [n for n in naboer if n.startswith(("homo.hjerte", "homo.cellesyk",
                                                 "homo.fluxus"))]
    assert not falske, f"function words gave false neighbours: {falske}"


def test_ordet_som_beskriver_noe_finner_fortsatt_noden() -> None:
    """The fix must not kill the signal."""
    svar = _plasser("vulkansk aske")
    naboer = [n for f in svar["forslag"] for n in f.get("noder", [])]
    assert "kosmos.jord.vulkan" in naboer, svar


def test_batterifragmentet_finner_batterinodene() -> None:
    svar = _plasser("energiflyt i batteriet under lading")
    naboer = [n for f in svar["forslag"] for n in f.get("noder", [])]
    assert any(n.startswith("batteri.") for n in naboer), svar


def test_ordlikhet_merkes_som_ikke_forslag() -> None:
    """When the list is only word similarity, it must say so — not read as a
    suggestion."""
    svar = _plasser("vulkansk aske")
    avledet = [f for f in svar["forslag"] if f["domene"] == "(avledet)"]
    assert avledet, svar
    kobling = avledet[0]["kobling"]
    assert "WORD SIMILARITY" in kobling and "not a placement suggestion" in kobling, kobling


def test_stoppordlista_spiser_ikke_innholdsord() -> None:
    """A stopword list that swallows content words makes the atlas blind, not
    stricter."""
    for ordet in ("energi", "flyt", "entropi", "buffer", "regime", "varme",
                  "motor", "felt", "gradient", "masse", "node", "kraft"):
        assert ordet not in atlas_lesing.STOPPORD, ordet
