"""THE BIOLOGY: separate the physiology from the analogy.

Measured 2026-09-18: all 12 `homo.*` nodes carried an IDENTICAL epistemic
signature — `paradigme / hypotese / minoritet / proxy`. That is wrong for
most of them:

  homo.hjerte_syklus is not an EFC hypothesis. It is cardiology.
  homo.metabolisme is biochemistry. homo.immunologi is Janeway/Matzinger.
  homo.sovn_vaaken is Borbely. homo.okologi is Scheffer.

The nodes SAY so themselves in `ontology.source`: "<discipline> (standard);
the analogy marking is the atlas's own". There are two layers, and they
must each have their own epistemic status.

A node that says "hypotese" about the Krebs cycle makes the atlas more
revolutionary than it is — the most dangerous direction to be wrong in.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
ATLAS = ROT / "schema" / "regime_nodes.jsonld"


@pytest.fixture(scope="module")
def noder() -> list[dict]:
    d = json.loads(ATLAS.read_text(encoding="utf-8"))
    return [n for n in d["nodes"] if n["id"].startswith("homo.")]


def test_biologien_har_ikke_identisk_signatur(noder: list[dict]) -> None:
    """Twelve identical signatures were the error. They must now differ."""
    sig = {(n["perspektiv"], n["epistemikk"]["sannhetsstatus"]) for n in noder}
    assert len(sig) > 1, f"all biology nodes still have the same signature: {sig}"


def test_larebok_fysiologi_er_stottet(noder: list[dict]) -> None:
    """Cardiology, biochemistry and immunology are established knowledge, not ours."""
    for nid in ("homo.hjerte_syklus", "homo.metabolisme", "homo.immunologi",
                "homo.genregulering", "homo.cellesyklus", "homo.sovn_vaaken",
                "homo.okologi", "homo.aksjonspotensial", "homo.feber_regime"):
        n = next(x for x in noder if x["id"] == nid)
        assert n["epistemikk"]["sannhetsstatus"] == "stottet", (
            f"{nid}: the physiology is established, not a hypothesis")
        assert n["epistemikk"]["konsensusstatus"] == "institusjonell", nid


def test_analogien_er_fortsatt_vaar(noder: list[dict]) -> None:
    """Correcting the physiology must NOT make the EFC analogy established."""
    for n in noder:
        if not n.get("analogi"):
            continue
        a = n["analogi"]
        assert "avbildning" in a and "bryter_der" in a, (
            f"{n['id']}: the analogy lacks avbildning or bryter_der")


def test_fluksprosessen_er_fortsatt_paradigme(noder: list[dict]) -> None:
    """Homo Fluxus itself — R, the reflection coefficient — IS our framework."""
    n = next(x for x in noder if x["id"] == "homo.fluxus")
    assert n["perspektiv"] == "paradigme"
    assert n["epistemikk"]["sannhetsstatus"] == "hypotese"


def test_ingen_analogi_uten_lagdeling(noder: list[dict]) -> None:
    """If the node has an analogy, the layering must be in writing."""
    for n in noder:
        if n.get("analogi"):
            assert "lagdeling" in n, f"{n['id']}: analogy without lagdeling"
            assert n["lagdeling"]["fysiologi"]["status"] == "akademia"
            assert n["lagdeling"]["analogi"]["status"] == "paradigme"
