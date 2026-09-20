"""Guards explicit ownership of the paradigm claims in the atlas."""

import json
import re
from pathlib import Path


ATLAS = Path(__file__).parents[1] / "schema" / "regime_nodes.jsonld"


def _atlas():
    return json.loads(ATLAS.read_text(encoding="utf-8"))


def _tekst(verdi):
    if isinstance(verdi, str):
        return [verdi]
    if isinstance(verdi, dict):
        return [tekst for delverdi in verdi.values() for tekst in _tekst(delverdi)]
    if isinstance(verdi, list):
        return [tekst for delverdi in verdi for tekst in _tekst(delverdi)]
    return []


def test_paradigme_spesialtilfelle_baerer_eierskap():
    """A special-case claim shall be EFC's claim, not a fact.

    The two patterns are the bank's own wording, so they move with the bank
    (measured 2026-09-20, after t_648190ca translated it): the Norwegian
    patterns matched zero nodes, i.e. this test passed by absence.
    """
    eierskap = re.compile(r"\bEFC\s+(?:predicts|places|claims)\b", re.I)
    krav = re.compile(r"special\s+case\s+of", re.I)
    brudd = []
    for node in _atlas()["nodes"]:
        if node.get("perspektiv") != "paradigme":
            continue
        tekst = " ".join(_tekst(node))
        if krav.search(tekst) and not eierskap.search(tekst):
            brudd.append(node["id"])
    assert not brudd, f"paradigm claim without ownership: {brudd}"


def test_desi_nullmaaling_kalles_ikke_motbevis():
    """DESI DR2 0.52 sigma shall be described as untested/non-discriminating."""
    for node in _atlas()["nodes"]:
        tekst = " ".join(_tekst(node)).lower()
        if node["id"] == "obs.bao" and re.search(r"0[.,]52\s*(?:sigma|σ)", tekst):
            assert not re.search(r"counter[- ]?evidence", tekst)
            assert any(uttrykk in tekst for uttrykk in ("untested", "non-discriminating"))


def test_efc_l1_baerer_ontologisk_eierskap():
    """L1 shall say who claims it, and what the retrofitting means."""
    node = next(node for node in _atlas()["nodes"] if node["id"] == "efc.l1")
    tekst = " ".join(_tekst(node))
    assert "EFC predicts" in tekst
    assert "ontologically" in tekst.lower()
