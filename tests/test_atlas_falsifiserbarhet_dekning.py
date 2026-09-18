"""FALSIFISERBARHET: alle 126 noder skal ha en eksplisitt avgjoerelse.

En node kan ha en konkret falsifikator, en faktisk falsifiserbarhet-status,
eller en skriftlig grunn til at den ikke kan felles av en observasjon.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
ATLAS = ROT / "schema" / "regime_nodes.jsonld"


@pytest.fixture(scope="module")
def noder() -> list[dict]:
    return json.loads(ATLAS.read_text(encoding="utf-8"))["nodes"]


def _har_falsifikator(n: dict) -> bool:
    """Tell en konkret falsifikator, enten som tekst eller liste."""
    verdi = n.get("ville_falsifisere")
    if isinstance(verdi, list):
        return bool(verdi) and all(isinstance(x, str) and x.strip() for x in verdi)
    return isinstance(verdi, str) and bool(verdi.strip())


def _har_status(n: dict) -> bool:
    """Tell bare en faktisk, ikke-tom statusverdi."""
    status = (n.get("falsifiserbarhet") or {}).get("status")
    return isinstance(status, str) and bool(status.strip())


def test_alle_noder_har_falsifiserbarhetsavgjoerelse(noder: list[dict]) -> None:
    """Avgjorelser skal dekke 126 av 126 noder, ikke bare feltkapasiteten."""
    avgjort = [
        n for n in noder
        if _har_falsifikator(n)
        or _har_status(n)
        or bool(((n.get("stipulasjoner") or {}).get("ikke_falsifiserbar_grunn") or "").strip())
    ]
    uten = [n["id"] for n in noder if n not in avgjort]
    assert len(avgjort) == len(noder) == 126, (
        f"{len(avgjort)}/{len(noder)} noder har falsifiserbarhetsavgjoerelse; "
        f"mangler: {uten[:8]}"
    )


def test_ikke_falsifiserbar_grunn_er_skriftlig(noder: list[dict]) -> None:
    """En grunn kan ikke være en tom plassholder."""
    for n in noder:
        grunn = (n.get("stipulasjoner") or {}).get("ikke_falsifiserbar_grunn")
        if grunn is not None:
            assert isinstance(grunn, str) and grunn.strip(), (
                f"{n['id']}.stipulasjoner.ikke_falsifiserbar_grunn er tom"
            )
