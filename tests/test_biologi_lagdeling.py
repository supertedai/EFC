"""BIOLOGIEN: skill fysiologien fra analogien.

Maalt 2026-09-18: alle 12 `homo.*`-noder bar IDENTISK epistemisk signatur —
`paradigme / hypotese / minoritet / proxy`. Det er feil for de fleste:

  homo.hjerte_syklus er ikke en EFC-hypotese. Det er kardiologi.
  homo.metabolisme er biokjemi. homo.immunologi er Janeway/Matzinger.
  homo.sovn_vaaken er Borbely. homo.okologi er Scheffer.

Nodene SIER det selv i `ontology.source`: «<fag> (standard);
analogi-merkingen er atlasets egen». Det er to lag, og de skal ha hver
sin epistemiske status.

En node som sier «hypotese» om Krebs-syklusen gjor atlaset mer
revolusjonert enn det er — den farligste retningen aa ta feil i.
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
    """Tolv like signaturer var feilen. De skal naa skille seg."""
    sig = {(n["perspektiv"], n["epistemikk"]["sannhetsstatus"]) for n in noder}
    assert len(sig) > 1, f"alle biologinoder har fortsatt samme signatur: {sig}"


def test_larebok_fysiologi_er_stottet(noder: list[dict]) -> None:
    """Kardiologi, biokjemi og immunologi er etablert kunnskap, ikke vaar."""
    for nid in ("homo.hjerte_syklus", "homo.metabolisme", "homo.immunologi",
                "homo.genregulering", "homo.cellesyklus", "homo.sovn_vaaken",
                "homo.okologi", "homo.aksjonspotensial", "homo.feber_regime"):
        n = next(x for x in noder if x["id"] == nid)
        assert n["epistemikk"]["sannhetsstatus"] == "stottet", (
            f"{nid}: fysiologien er etablert, ikke en hypotese")
        assert n["epistemikk"]["konsensusstatus"] == "institusjonell", nid


def test_analogien_er_fortsatt_vaar(noder: list[dict]) -> None:
    """Aa rette fysiologien maa IKKE gjore EFC-analogien til etablert."""
    for n in noder:
        if not n.get("analogi"):
            continue
        a = n["analogi"]
        assert "avbildning" in a and "bryter_der" in a, (
            f"{n['id']}: analogien mangler avbildning eller bryter_der")


def test_fluksprosessen_er_fortsatt_paradigme(noder: list[dict]) -> None:
    """Homo Fluxus selv — R, refleksjonskoeffisienten — ER vaar ramme."""
    n = next(x for x in noder if x["id"] == "homo.fluxus")
    assert n["perspektiv"] == "paradigme"
    assert n["epistemikk"]["sannhetsstatus"] == "hypotese"


def test_ingen_analogi_uten_lagdeling(noder: list[dict]) -> None:
    """Har noden en analogi, skal lagdelingen staa skriftlig."""
    for n in noder:
        if n.get("analogi"):
            assert "lagdeling" in n, f"{n['id']}: analogi uten lagdeling"
            assert n["lagdeling"]["fysiologi"]["status"] == "akademia"
            assert n["lagdeling"]["analogi"]["status"] == "paradigme"
