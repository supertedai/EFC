"""THE INTERFACE — can an outside reader find the entry points?

Measured 2026-09-18: a reader (me) guessed three entry points wrong from memory.
  finn() was indexed as a list — it is a dict
  plasser() was read with a key that does not exist
  kjent_hull was called — it was named _kjent_hull and was private

None of them was an error in the atlas. All of them were an error in the interface.
This test checks that the entry points exist, are public, and have the
shape the module map promises.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts"))

import atlas_lesing  # noqa: E402


def test_modulkartet_nevner_faktiske_funksjoner() -> None:
    """Everything the module docstring promises shall exist — and be public."""
    dok = atlas_lesing.__doc__ or ""
    lovet = ["les_atlas", "finn", "akser", "roter_akse", "roter", "helhet",
             "plasser", "kjent_hull", "naboer", "hop", "fragment",
             "maaleformer", "proxy_kjeder"]
    mangler = [n for n in lovet if not hasattr(atlas_lesing, n)]
    assert not mangler, f"the module map promises names that do not exist: {mangler}"
    assert "API-KARTET" in dok, "the module map is gone from the docstring"


def test_kjent_hull_er_offentlig_og_tar_et_emne() -> None:
    """The entry point a reader looks for shall exist without an underscore."""
    assert hasattr(atlas_lesing, "kjent_hull"), (
        "kjent_hull is missing — a reader asking «is this a known gap?» "
        "does not find it as _kjent_hull")
    # it shall take (repo, emne), not (dekning, naal)
    import inspect
    p = list(inspect.signature(atlas_lesing.kjent_hull).parameters)
    assert p[:2] == ["repo", "emne"], f"wrong parameters: {p[:2]}"


def test_finn_og_plasser_svarer_med_dict() -> None:
    """The return shape the map promises — not a list, not None."""
    f = atlas_lesing.finn(ROT, "trippelpunkt", ref="HEAD")
    assert isinstance(f, dict), f"finn() gave {type(f).__name__}, not a dict"
    for nokkel in ("antall", "hull", "for_bredt"):
        assert nokkel in f, f"finn() is missing the key «{nokkel}»"

    a = atlas_lesing.les_atlas(ROT, ref="HEAD")
    p = atlas_lesing.plasser(a, "vulkansk aske i stratosfaeren")
    assert isinstance(p, dict), f"plasser() gave {type(p).__name__}, not a dict"
    for nokkel in ("status", "naere_noder", "mangler"):
        assert nokkel in p, f"plasser() is missing the key «{nokkel}»"


def test_helhet_svarer_paa_de_seks() -> None:
    """The rotation promises the six parts — they shall come."""
    a = atlas_lesing.les_atlas(ROT, ref="HEAD")
    h = atlas_lesing.helhet(a, "h2o.triple_point")
    for nokkel in ("episenter", "felt", "domene", "maal", "perspektiv",
                   "emergence"):
        assert nokkel in h, f"helhet() is missing «{nokkel}»"
