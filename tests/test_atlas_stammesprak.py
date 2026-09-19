"""Regresjonstester for atlasets eget begrepsrom."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
SCRIPTS = ROT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import atlas_lesing  # noqa: E402


KJERNEBEGREPER = (
    "Energy-Flow Cosmology",
    "Entropy Gradient",
    "GHF",
    "HME",
    "IMX",
)


def test_kjernebegrep_svarer_med_navngitt_grunn() -> None:
    """Et registrert begrep skal skilles fra et ekte hull."""
    for begrep in KJERNEBEGREPER:
        svar = atlas_lesing.finn(ROT, begrep, ref="HEAD")
        assert not svar["hull"], begrep
        assert svar["treff"][0]["trefftype"] == "navnerom"
        assert svar["treff"][0]["id"].startswith("efc:")
        assert svar["treff"][0]["grunn"]


def test_navneromstreff_er_ikke_dekning() -> None:
    """Et begrep uten node skal ikke kunne leses som «atlaset har dette».

    Review 2026-09-18: navneromstreffet ga en ikke-tom treffliste, og en
    nedstroemsleser kunne konkludere «dekt». Feltet `har_node` sier nei — og
    det er forskjellen mellom å ha begrepet og å ha noden.
    """
    svar = atlas_lesing.finn(ROT, "Entropy Gradient", ref="HEAD")
    treff = svar["treff"][0]
    assert treff["har_node"] is False
    assert treff["dekning"] == "navnerom_uten_node"

    # Navnet skal ikke finnes som node i banken — ellers er testen doed.
    bank = json.loads((ROT / "schema" / "regime_nodes.jsonld").read_text(
        encoding="utf-8"))
    ider = {n["id"] for n in bank["nodes"]}
    assert not any("EntropyGradient" in i for i in ider)

    # Et EKTE hull skal ikke faa navneromstreffet med seg.
    ukjent = atlas_lesing.finn(ROT, "finnes-ikke-som-begrep-eller-node",
                               ref="HEAD")
    assert ukjent["hull"] is True
    assert ukjent["treff"] == []


def test_fem_kjernebegreper_er_deklarert_i_registeret() -> None:
    """Testen skal ikke kunne passere fordi registeret ble tomt."""
    data = json.loads((ROT / "docs" / "concepts.jsonld").read_text(
        encoding="utf-8"))
    ider = {p.get("@id") for p in data.get("@graph", [])}
    for forventet in ("efc:EFC", "efc:EntropyGradient", "efc:GHF", "efc:HME",
                      "efc:IMX"):
        assert forventet in ider, forventet


def test_defekt_begrepsregister_feiler_hoeyt(monkeypatch, tmp_path) -> None:
    """Ugyldig JSON i registeret er en lesefeil, ikke «ikke funnet».

    Foerste utgave svelget baade JSONDecodeError og manglende fil. Da ble en
    defekt i registeret til svaret «atlaset vet ikke» — et svar som ser ut som
    kunnskap om innholdet. Testen bytter ut git-leseren: en midlertidig
    katalog er ikke et git-tre, saa `_git` ville feilet FOER json ble lest —
    og da maalte testen git, ikke lesefeilhaandteringen.
    """
    def falsk_git(repo, *args):
        if args[:2] == ("show", "HEAD:docs/concepts.jsonld"):
            return "{ ikke json"
        raise atlas_lesing.AtlasLesingFeil("finnes ikke i dette testtreet")

    monkeypatch.setattr(atlas_lesing, "_git", falsk_git)
    with pytest.raises(atlas_lesing.AtlasLesingFeil, match="valid JSON"):
        atlas_lesing._navnerom(tmp_path, "HEAD", "ghf")


def test_oppslag_er_deterministisk_paa_tvers_av_hashfroer() -> None:
    """Sortering skal ikke avhenge av prosessens hashfroe."""
    kode = (
        "import json,sys; sys.path.insert(0,'scripts'); import atlas_lesing; "
        "print(json.dumps(atlas_lesing.finn('.', 'Entropy Gradient', ref='HEAD'), "
        "sort_keys=True, ensure_ascii=False))"
    )
    svar = []
    for fro in ("0", "1", "12345"):
        env = {**os.environ, "PYTHONHASHSEED": fro}
        svar.append(subprocess.check_output(
            [sys.executable, "-c", kode], cwd=ROT, env=env, text=True))
    assert svar[0] == svar[1] == svar[2]
