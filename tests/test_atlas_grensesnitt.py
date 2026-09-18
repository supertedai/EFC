"""GRENSESNITTET — kan en fremmed leser finne inngangene?

Maalt 2026-09-18: en leser (jeg) gjettet tre innganger feil fra husken.
  finn() ble indeksert som en liste — den er en dict
  plasser() ble lest med en noekkel som ikke finnes
  kjent_hull ble kalt — den het _kjent_hull og var privat

Ingen av dem var en feil i atlaset. Alle var en feil i grensesnittet.
Denne testen sjekker at inngangene finnes, er offentlige, og har den
formen modul-kartet lover.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts"))

import atlas_lesing  # noqa: E402


def test_modulkartet_nevner_faktiske_funksjoner() -> None:
    """Alt modul-docstringen lover skal finnes — og vaere offentlig."""
    dok = atlas_lesing.__doc__ or ""
    lovet = ["les_atlas", "finn", "akser", "roter_akse", "roter", "helhet",
             "plasser", "kjent_hull", "naboer", "hop", "fragment",
             "maaleformer", "proxy_kjeder"]
    mangler = [n for n in lovet if not hasattr(atlas_lesing, n)]
    assert not mangler, f"modulkartet lover navn som ikke finnes: {mangler}"
    assert "API-KARTET" in dok, "modulkartet er borte fra docstringen"


def test_kjent_hull_er_offentlig_og_tar_et_emne() -> None:
    """Inngangen en leser leter etter skal finnes uten understrek."""
    assert hasattr(atlas_lesing, "kjent_hull"), (
        "kjent_hull mangler — en leser som spor «er dette et kjent hull?» "
        "finner den ikke som _kjent_hull")
    # den skal ta (repo, emne), ikke (dekning, naal)
    import inspect
    p = list(inspect.signature(atlas_lesing.kjent_hull).parameters)
    assert p[:2] == ["repo", "emne"], f"feil parametre: {p[:2]}"


def test_finn_og_plasser_svarer_med_dict() -> None:
    """Returformen kartet lover — ikke en liste, ikke None."""
    f = atlas_lesing.finn(ROT, "trippelpunkt", ref="HEAD")
    assert isinstance(f, dict), f"finn() ga {type(f).__name__}, ikke dict"
    for nokkel in ("antall", "hull", "for_bredt"):
        assert nokkel in f, f"finn() mangler nøkkelen «{nokkel}»"

    a = atlas_lesing.les_atlas(ROT, ref="HEAD")
    p = atlas_lesing.plasser(a, "vulkansk aske i stratosfaeren")
    assert isinstance(p, dict), f"plasser() ga {type(p).__name__}, ikke dict"
    for nokkel in ("status", "naere_noder", "mangler"):
        assert nokkel in p, f"plasser() mangler nøkkelen «{nokkel}»"


def test_helhet_svarer_paa_de_seks() -> None:
    """Rotasjonen lover de seks delene — de skal komme."""
    a = atlas_lesing.les_atlas(ROT, ref="HEAD")
    h = atlas_lesing.helhet(a, "h2o.triple_point")
    for nokkel in ("episenter", "felt", "domene", "maal", "perspektiv",
                   "emergence"):
        assert nokkel in h, f"helhet() mangler «{nokkel}»"
