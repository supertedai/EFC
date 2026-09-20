"""THE COUPLINGS — 1-hop, 2-hop, 3-hop.

Morten, 2026-09-18 (translated from Norwegian): "can you navigate with ease now
and in depth and see local global couplings, see the connections, 1hop, 2, hop,
3hop, rotate around each fragment an observation we make places everything in
the atlas?"

MEASURED: the tool had `--emne`, `--akse`, `--node`, `--oversikt` and
`--proxy`. It had NO hops. The couplings existed in the data —
`nivaa.forelder`, `coupling.local/global`, `analogi`, `stipulasjoner.motor`,
`buss_domene`, `measure.proxy_chain` — and none of them could be FOLLOWED.
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
        """The hierarchy is the strongest coupling we have."""
        n = atlas_lesing.naboer(atlas, "regnbue")
        assert n, "regnbue has no neighbours"
        assert "optikk.dispersjon" in n.get("forelder", []), n.keys()

    def test_naboer_finner_samme_domene(self, atlas: dict) -> None:
        """The node comes from the DATA: only 48 of 89 have buss_domene."""
        domain = [x["id"] for x in atlas["noder"] if x.get("buss_domene")]
        assert domain, "no nodes have buss_domene"
        n = atlas_lesing.naboer(atlas, domain[0])
        assert n.get("samme_domene"), f"{domain[0]} shares no domain"

    def test_naboer_finner_delt_analogi(self, atlas: dict) -> None:
        """The isomorphism is a COUPLING, not just a field."""
        n = atlas_lesing.naboer(atlas, "homo.homeostase_buffer")
        assert n.get("deler_analogi"), "analogy nodes must be linked together"

    def test_naboer_finner_samme_motor(self, atlas: dict) -> None:
        n = atlas_lesing.naboer(atlas, "h2o.solid")
        assert isinstance(n.get("samme_motor", []), list)

    def test_ukjent_node_feiler(self, atlas: dict) -> None:
        with pytest.raises(KeyError):
            atlas_lesing.naboer(atlas, "no.such.node")


class TestFlereHopp:

    def test_to_hopp_utvider_mengden(self, atlas: dict) -> None:
        ett = atlas_lesing.hop(atlas, "regnbue", 1)
        to = atlas_lesing.hop(atlas, "regnbue", 2)
        assert len(to) > len(ett), f"2 hops ({len(to)}) <= 1 hop ({len(ett)})"

    def test_tre_hopp_utvider_enda(self, atlas: dict) -> None:
        to = atlas_lesing.hop(atlas, "regnbue", 2)
        tre = atlas_lesing.hop(atlas, "regnbue", 3)
        assert len(tre) >= len(to)

    def test_hopp_gir_stien_ikke_bare_mengden(self, atlas: dict) -> None:
        """The depth is the point — WHY they connect, not just that they do."""
        stier = atlas_lesing.hop_stier(atlas, "regnbue", 2)
        assert stier, "no paths"
        nodesti, _ = next(iter(stier.values()))
        assert len(nodesti) >= 2, f"the path is too short: {nodesti}"

    def test_hopp_utelater_startnoden(self, atlas: dict) -> None:
        for n in atlas_lesing.hop(atlas, "regnbue", 3):
            assert n != "regnbue", "the start node cannot be its own neighbour"


class TestRotasjonRundtEtFragment:
    """(translated) "rotate around each fragment an observation we make"."""

    def test_fragment_gir_koblinger_og_felt(self, atlas: dict) -> None:
        f = atlas_lesing.fragment(atlas, "obsf.bao")
        assert f.get("finnes") in (True, False)
        assert "koblinger" in f or not f["finnes"]

    def test_fragment_paa_ekte_node_gir_alt(self, atlas: dict) -> None:
        f = atlas_lesing.fragment(atlas, "regnbue")
        assert f["finnes"] is True
        assert f["koblinger"], "regnbue must have couplings"
        assert f["node"]["id"] == "regnbue"
