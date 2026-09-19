"""Can the atlas be ROTATED — not just looked up?

Morten, 2026-09-17: «you must immediately see epicentre, field, domain,
paradigm, consensus, academia, vector, goal, measurer, measuring instrument,
emergence, proxy, etc. in every link for everything that lies there, so that
you can navigate easily around».

Measured: `atlas_lesing.py` had four flags — `--emne`, `--ref`, `--hent`,
`--alle`. It could look up a topic and list everything. It could not filter
on `perspektiv`, not show proxy chains, not distinguish a measured node from a
derived one. The rotation did not exist.

This file locks it.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import atlas_lesing  # noqa: E402


@pytest.fixture(scope="module")
def atlas() -> dict:
    return atlas_lesing.les_atlas(REPO, ref="HEAD")


class TestRotasjon:

    def test_filtrer_paa_perspektiv(self, atlas: dict) -> None:
        p = atlas_lesing.roter(atlas, perspektiv="paradigme")
        assert p, "no nodes with perspektiv=paradigme"
        assert all(n.get("perspektiv") == "paradigme" for n in p)

    def test_filtrer_paa_fase(self, atlas: dict) -> None:
        f = atlas_lesing.roter(atlas, fase="instrument")
        assert f
        assert all(n.get("phase") == "instrument" for n in f)

    def test_filtrer_paa_domene(self, atlas: dict) -> None:
        d = atlas_lesing.roter(atlas, domene="kosmos.kosmologi")
        assert d
        assert all(n.get("buss_domene") == "kosmos.kosmologi" for n in d)

    def test_maaleform_skiller_maalt_fra_avledet(self, atlas: dict) -> None:
        """What you asked about: which MEASURE, and with what."""
        former = atlas_lesing.maaleformer(atlas)
        assert set(former) >= {"instrument", "avledet", "ingen"}, set(former)
        assert former["instrument"], "no instrument nodes found"

    def test_proxy_kjeder_kan_listes(self, atlas: dict) -> None:
        """What goes via what — in every link."""
        kjeder = atlas_lesing.proxy_kjeder(atlas)
        assert kjeder, "no proxy chains found"
        navn, ledd = next(iter(kjeder.items()))
        assert isinstance(ledd, list) and len(ledd) > 0

    def test_roter_rundt_en_node_gir_alle_felt(self, atlas: dict) -> None:
        """The core: one node, ALL fields — not just the three I remember."""
        r = atlas_lesing.roter(atlas, node="efc.growth_engine")
        assert r, "did not find the node"
        n = r[0]
        for felt in ("episenter", "regime", "measure", "emergence", "coupling",
                     "observer", "buffer", "fractal", "ontology", "epistemikk",
                     "maale_paradigme", "stipulasjoner", "nivaa"):
            assert felt in n, f"roter() hides {felt}"

    def test_ukjent_node_feiler_hoeyt(self, atlas: dict) -> None:
        with pytest.raises(KeyError):
            atlas_lesing.roter(atlas, node="no.such.node")

    def test_s_akse_roterer_med_regimer(self, atlas: dict) -> None:
        treff = atlas_lesing.roter_akse(atlas, "S")
        assert len(treff) > 0
        assert {n["maale_paradigme"]["s_regime"] for n in treff} >= {
            "S->0", "S~0", "S>0", "S->1"
        }
        assert atlas_lesing.roter_akse(atlas, "maale_paradigme.s_regime", "S~0")

    def test_l_kjeden_har_stigende_s_regimer(self, atlas: dict) -> None:
        forventet = [("efc.l0", "S->0"), ("efc.l1", "S~0"),
                     ("efc.l2", "S>0"), ("efc.l3", "S->1")]
        l_noder = {n["id"]: n for n in atlas["noder"] if n["id"] in
                   {"efc.l0", "efc.l1", "efc.l2", "efc.l3"}}
        assert [(i, l_noder[i]["maale_paradigme"]["s_regime"])
                for i, _ in forventet] == forventet

    def test_s_d_c_sektorer_og_ebe_er_deklarert(self, atlas: dict) -> None:
        noder = {n["id"]: n for n in atlas["noder"]}
        assert {noder[i]["maale_paradigme"]["sektor"] for i in
                ("efc.lag_s", "efc.lag_d", "efc.lag_c0")} == {"S", "D", "C"}
        assert all("claim validity = f(S, L, proxy-chain)" in n["maale_paradigme"]["ebe_function"]
                   for n in noder.values() if n["id"] in {"efc.l0", "efc.l1", "efc.l2", "efc.l3",
                                                           "efc.lag_s", "efc.lag_d", "efc.lag_c0"})

    def test_observasjoner_eksplisitt_rcmp_overlap(self, atlas: dict) -> None:
        observasjoner = [n for n in atlas["noder"] if n["id"].startswith("obs.")]
        assert observasjoner
        assert all(n["rcmp"]["overlap"] is True for n in observasjoner)
        assert all(set(n["rcmp"]) >= {"instrument", "observabel", "teori", "overlap"}
                   for n in observasjoner)
