"""Vokter eksplisitt eierskap til paradigme-paastander i atlaset."""

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
    """Et spesialtilfellekrav skal vaere EFCs paastand, ikke et faktum."""
    eierskap = re.compile(r"\bEFC\s+(?:predikerer|plasserer|hevder)\b", re.I)
    krav = re.compile(r"er\s+spesialtilfelle\s+av", re.I)
    brudd = []
    for node in _atlas()["nodes"]:
        if node.get("perspektiv") != "paradigme":
            continue
        tekst = " ".join(_tekst(node))
        if krav.search(tekst) and not eierskap.search(tekst):
            brudd.append(node["id"])
    assert not brudd, f"paradigme-paastand uten eierskap: {brudd}"


def test_desi_nullmaaling_kalles_ikke_motbevis():
    """DESI DR2 0.52 sigma skal beskrives som utestet/ikke-diskriminerende."""
    for node in _atlas()["nodes"]:
        tekst = " ".join(_tekst(node)).lower()
        if node["id"] == "obs.bao" and re.search(r"0[.,]52\s*(?:sigma|σ)", tekst):
            assert not re.search(r"counter[- ]?evidence", tekst)
            assert any(uttrykk in tekst for uttrykk in ("untested", "non-discriminating"))


def test_efc_l1_baerer_ontologisk_eierskap():
    """L1 skal si hvem som paastaar og hva retrofittingen betyr."""
    node = next(node for node in _atlas()["nodes"] if node["id"] == "efc.l1")
    tekst = " ".join(_tekst(node))
    assert "EFC predicts" in tekst
    assert "ontologically" in tekst.lower()
