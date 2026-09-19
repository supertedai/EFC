"""The requirements on a new node: where they come from, and what kind of answer
they demand.

Measured 2026-09-18: `plasser()` computed «what must be filled» as every field
in the bank minus seven hard-coded exceptions — and among the exceptions lay
`buss_domene` and `falsifiserbarhet`. A new node was therefore asked for
`coupling.empathy_note`, but NOT for bus domain or falsifier: the two fields the
rest of the house judges by. This test locks that the requirements come from the
schema, that the house's own requirements are tagged as the house's, and that a
structure field never gets a value without a reason.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts"))

import atlas_lesing  # noqa: E402


@pytest.fixture(scope="module")
def atlas() -> dict:
    return atlas_lesing.les_atlas(ROT, ref="HEAD")


def _krav(p: dict, felt: str) -> dict:
    treff = [k for k in p["krav"] if k["felt"] == felt]
    assert treff, f"{felt} is absent from the requirements: {[k['felt'] for k in p['krav']]}"
    return treff[0]


def test_kravene_kommer_fra_skjemaet(atlas):
    p = atlas_lesing.plasser(atlas, "BAO maaling i galakser")
    fra_skjemaet = atlas_lesing.skjema_krav(atlas)
    skjema = [k for k in p["krav"] if k["kilde"] == "skjema"]
    assert len(skjema) == len(fra_skjemaet), p["krav"]
    assert {k["felt"] for k in skjema} == set(fra_skjemaet)


def test_buss_domene_og_falsifikator_er_med(atlas):
    """The two fields that wrongly lay on the exception list."""
    p = atlas_lesing.plasser(atlas, "BAO maaling i galakser")
    for felt in ("buss_domene", "ville_falsifisere", "falsifiserbarhet",
                 "prediction", "settlement"):
        k = _krav(p, felt)
        assert k["kilde"] == "huset", k
        assert felt not in atlas_lesing.skjema_krav(atlas), k


def test_mangler_og_krav_er_samme_liste(atlas):
    p = atlas_lesing.plasser(atlas, "BAO maaling i galakser")
    assert p["mangler"] == [k["felt"] for k in p["krav"]]


def test_hvert_krav_har_en_av_tre_klasser(atlas):
    p = atlas_lesing.plasser(atlas, "BAO maaling i galakser")
    for k in p["krav"]:
        assert k["klasse"] in ("struktur", "vurdering", "paastand"), k
    o = p["oppsummering"]
    assert o["struktur"] + o["vurdering"] + o["paastand"] == len(p["krav"])


def test_synlighet_foreslaas_fra_banken_ikke_fra_koden(atlas):
    """The default value must be read, not written in."""
    p = atlas_lesing.plasser(atlas, "BAO maaling i galakser")
    k = _krav(p, "synlighet")
    verdier = [n.get("synlighet") for n in atlas["noder"] if n.get("synlighet")]
    vanligst = max(set(verdier), key=verdier.count)
    assert k["forslag"] == vanligst, k
    assert str(verdier.count(vanligst)) in k["grunn"], k


def test_buss_domene_foreslaas_naar_fragmentet_nevner_ett_domene(atlas):
    p = atlas_lesing.plasser(atlas, "BAO maaling i galakser")
    k = _krav(p, "buss_domene")
    assert k["forslag"] == "kosmos.galakser", k


def test_strukturfelt_uten_grunnlag_faar_ingen_verdi(atlas):
    """`phase` is not a closed set — it is core + rest."""
    p = atlas_lesing.plasser(atlas, "xylofonstemning i mars")
    k = _krav(p, "phase")
    assert k["forslag"] is None, k
    assert "kjerne" in k["grunn"], k


def test_alle_strukturfelt_har_enten_verdi_eller_grunn(atlas):
    for tekst in ("BAO maaling i galakser", "xylofonstemning i mars",
                  "vulkansk aske"):
        p = atlas_lesing.plasser(atlas, tekst)
        for k in p["krav"]:
            if k["klasse"] == "struktur":
                # A value must be justified, and a missing value must be
                # explained. Never a value without a reason.
                assert k["grunn"], (tekst, k)
                if k["forslag"] is None:
                    assert k["klasse"] == "struktur", k


def test_uten_kravkilde_feiler_plasser_hoyt(atlas):
    """An empty requirement looks as if nothing is required."""
    uten = {k: v for k, v in atlas.items()
            if k not in ("skjema_krav", "repo", "ref")}
    with pytest.raises(atlas_lesing.AtlasLesingFeil):
        atlas_lesing.plasser(uten, "BAO maaling i galakser")


def test_skjema_krav_kan_leses_last_naar_det_mangler(atlas):
    """The atlas can exist without a schema — but the requirements reading must
    happen somewhere."""
    uten = {k: v for k, v in atlas.items() if k != "skjema_krav"}
    assert atlas_lesing.skjema_krav(uten) == atlas_lesing.skjema_krav(atlas)


def test_skjema_krav_leses_fra_refen_ikke_arbeidsstreet(atlas):
    """The requirements must come from the same ref as the atlas, and be named."""
    krav = atlas_lesing.skjema_krav(atlas)
    assert krav and "id" in krav, krav
    assert atlas["commit"], atlas
    assert atlas["ref"] == "HEAD"
