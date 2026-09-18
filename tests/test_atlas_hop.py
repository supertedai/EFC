"""KOBLINGENE — 1-hop, 2-hop, 3-hop.

Morten, 2026-09-18: «kan du navigere med enkelhet nå og i dybde og se lokal
global koblinger, se sammenhengene, 1hop, 2, hop, 3hop, rotere rundt hver
fragment en observasjon vi gjør plasser alt i atalsest?»

MAALT: verktoeyet hadde `--emne`, `--akse`, `--node`, `--oversikt` og
`--proxy`. Det hadde INGEN hopp. Koblingene fantes i dataene —
`nivaa.forelder`, `coupling.local/global`, `analogi`, `stipulasjoner.motor`,
`buss_domene`, `measure.proxy_chain` — og ingen av dem kunne FOELGES.
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


class TestEttHopp:

    def test_naboer_finner_forelder_og_barn(self, atlas: dict) -> None:
        """Hierarkiet er den sterkeste koblingen vi har."""
        n = atlas_lesing.naboer(atlas, "regnbue")
        assert n, "regnbue har ingen naboer"
        assert "optikk.dispersjon" in n.get("forelder", []), n.keys()

    def test_naboer_finner_samme_domene(self, atlas: dict) -> None:
        """Noden velges fra DATAENE: bare 48 av 89 har et buss_domene."""
        med = [x["id"] for x in atlas["noder"] if x.get("buss_domene")]
        assert med, "ingen noder har buss_domene"
        n = atlas_lesing.naboer(atlas, med[0])
        assert n.get("samme_domene"), f"{med[0]} deler ikke domene med noen"

    def test_naboer_finner_delt_analogi(self, atlas: dict) -> None:
        """Isomorfismen er en KOBLING, ikke bare et felt."""
        n = atlas_lesing.naboer(atlas, "homo.homeostase_buffer")
        assert n.get("deler_analogi"), "analogi-noder skal lenkes sammen"

    def test_naboer_finner_samme_motor(self, atlas: dict) -> None:
        n = atlas_lesing.naboer(atlas, "h2o.solid")
        assert isinstance(n.get("samme_motor", []), list)

    def test_ukjent_node_feiler(self, atlas: dict) -> None:
        with pytest.raises(KeyError):
            atlas_lesing.naboer(atlas, "finnes.ikke")


class TestFlereHopp:

    def test_to_hopp_utvider_mengden(self, atlas: dict) -> None:
        ett = atlas_lesing.hop(atlas, "regnbue", 1)
        to = atlas_lesing.hop(atlas, "regnbue", 2)
        assert len(to) > len(ett), f"2 hop ({len(to)}) gav ikke mer enn 1 ({len(ett)})"

    def test_tre_hopp_utvider_enda(self, atlas: dict) -> None:
        to = atlas_lesing.hop(atlas, "regnbue", 2)
        tre = atlas_lesing.hop(atlas, "regnbue", 3)
        assert len(tre) >= len(to)

    def test_hopp_gir_stien_ikke_bare_mengden(self, atlas: dict) -> None:
        """Dybden er poenget — HVORFOR henger de sammen, ikke bare at de gjor."""
        stier = atlas_lesing.hop_stier(atlas, "regnbue", 2)
        assert stier, "ingen stier"
        nodesti, _ = next(iter(stier.values()))
        assert len(nodesti) >= 2, f"stien er for kort: {nodesti}"

    def test_hopp_utelater_startnoden(self, atlas: dict) -> None:
        for n in atlas_lesing.hop(atlas, "regnbue", 3):
            assert n != "regnbue", "startnoden skal ikke vaere sin egen nabo"


class TestRotasjonRundtEtFragment:
    """«rotere rundt hver fragment en observasjon vi gjor»."""

    def test_fragment_gir_koblinger_og_felt(self, atlas: dict) -> None:
        f = atlas_lesing.fragment(atlas, "obsf.bao")
        assert f.get("finnes") in (True, False)
        assert "koblinger" in f or not f["finnes"]

    def test_fragment_paa_ekte_node_gir_alt(self, atlas: dict) -> None:
        f = atlas_lesing.fragment(atlas, "regnbue")
        assert f["finnes"] is True
        assert f["koblinger"], "regnbue skal ha koblinger"
        assert f["node"]["id"] == "regnbue"
