"""Usikkerhetslaget (ADR-086 §3.1): valgfritt, lukket, additivt — alltid med kilde.

Kort `t_af77c6da` (K4). Diagnosen som begrunner feltet er MÅLT: hodetallene
står med feilgrense i sine egne kilder — `k = 0.415 ± 0.029` står i
`docs/papers/efc/EFC_Phase_3__SPARC_Validation/index.json:5` — mens atlaset
hadde 0 strukturerte usikkerhetsfelt. Atlaset kastet altså informasjon kilden
hadde. Ingen skal skaffe NY usikkerhet; feltet skal bare slutte å miste den.

To regler holdes av DENNE filen og ikke av skjemaet, med vilje (ADR-086 §3.4:
C10-gaten melder underskjema med `properties` som åpent, så obligatoriskhet må
holdes av tester inntil gaten endres med menneskeord — `t_2e60afa6`):

1. **En verdi har alltid en kilde.** Hver post navngir fil OG linje, og linjen
   leses tilbake: verdien skal stå der, feilgrensen skal være den kilden
   oppgir, og sitatet skal finnes. En gjetning kan derfor ikke skrives inn —
   den finnes ikke i kilden. `null` er et svar; 0 og gjetting er det ikke.
2. **β = 0.16 står uten feilgrense i sitt eget paper** og skal stå som HULL.
   «Kilden oppgir den ikke» er svaret, ikke en mangel — og hullet skal ikke
   kunne fylles av en senere edit uten at denne filen blir rød.

Testene muterer banken i minnet og krever at sjekkeren FELLER. En test som
bare ser at ordet «kilde» finnes i en fil, ser formen og ikke meningen.
"""
from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts"))
sys.path.insert(0, str(ROT / "scripts" / "maintenance"))

from atlas_lesing import (AtlasLesingFeil, plasser,  # noqa: E402
                          sjekk_usikkerhet)
import efc_schema_check  # noqa: E402

SKJEMA_STI = ROT / "schema" / "regime_node.schema.json"
BANK_STI = ROT / "schema" / "regime_nodes.jsonld"

# Noden og posten de målte tilfellene peker på. De står her fordi testene
# under navngir dem i feilmeldingen — et tall uten sitt fil:linje er en
# påstand uten proveniens.
NODE_MED_GRENSE = "obs.rar"
NODE_MED_HULL = "obs.bao"

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

requires_jsonschema = pytest.mark.skipif(
    jsonschema is None, reason="jsonschema ikke installert")


def _skjema() -> dict:
    return json.loads(SKJEMA_STI.read_text(encoding="utf-8"))


def _bank() -> dict:
    return json.loads(BANK_STI.read_text(encoding="utf-8"))


def _node(bank: dict, node_id: str) -> dict:
    return next(n for n in bank["nodes"] if n["id"] == node_id)


def _poster(bank: dict):
    """(node, post) for hver post i usikkerhetslaget."""
    for n in bank["nodes"]:
        for post in ((n.get("usikkerhet") or {}).get("poster") or []):
            yield n, post


def _linje(fil: str, nr: int) -> str:
    return (ROT / fil).read_text(encoding="utf-8").splitlines()[nr - 1]


def _grenser(linje: str) -> list[str]:
    """Tallene som står rett etter et ± på linjen — kildens egne feilgrenser."""
    return re.findall(r"±\s*([0-9]+(?:\.[0-9]+)?)", linje)


def _dok(bank: dict, noder: list) -> dict:
    d = {k: v for k, v in bank.items() if k not in ("nodes", "relations")}
    d["nodes"] = noder
    d["relations"] = []
    return d


def _mutert(bank: dict, node_id: str, endre) -> dict:
    """Banken med ÉN post endret — mutasjonen testen feller."""
    ny = copy.deepcopy(bank)
    endre(_node(ny, node_id)["usikkerhet"]["poster"][0])
    return ny


# ---------------------------------------------------------------------------
# Feltet: valgfritt, lukket, additivt
# ---------------------------------------------------------------------------

def test_feltet_er_valgfritt_og_lukket():
    """Krav 1 og 2: deklarert, lukket — og ALDRI i `required`."""
    s = _skjema()
    rn = s["$defs"]["RegimeNode"]
    assert "usikkerhet" in rn["properties"], "feltet er ikke deklarert i skjemaet"
    assert "usikkerhet" not in rn["required"], (
        "feltet staar i RegimeNode.required — da er det ikke additivt, og "
        "ingen eksisterende node kan vaere uendret")
    felt = rn["properties"]["usikkerhet"]
    assert felt.get("type") == "object"
    assert felt.get("additionalProperties") is False, (
        "feltets eget objekt er ikke lukket — C10-gaten melder det som aapent")

    # C10-gatens eget svar, ikke min lesning av skjemaet.
    aapne = efc_schema_check.open_schemas(s)
    assert aapne == [], f"skjemaet har aapne underskjemaer: {aapne[:3]}"


@requires_jsonschema
def test_ny_node_uten_feltet_validerer_og_plasser_krever_det_ikke():
    """Krav 2: additivt. En node UTEN feltet skal fortsatt vaere gyldig."""
    s, bank = _skjema(), _bank()
    node = copy.deepcopy(_node(bank, NODE_MED_GRENSE))
    node.pop("usikkerhet", None)
    jsonschema.Draft202012Validator(s).validate(_dok(bank, [node]))

    krav = plasser({"skjema_krav": list(s["$defs"]["RegimeNode"]["required"]),
                    "noder": bank["nodes"]},
                   "en fiskestim i Nordsjoen")
    felt = [k["felt"] for k in krav["krav"]]
    assert "usikkerhet" not in felt, (
        "plasser krever det nye feltet av en ny node — obligatoriskhet skal "
        "holdes av tester, ikke legges paa nye noder (t_2e60afa6)")


@requires_jsonschema
def test_skjemaet_avviser_post_uten_kilde():
    """Krav 3 i skjemaet: en post uten kilde er ikke en post."""
    s, bank = _skjema(), _bank()
    node = copy.deepcopy(_node(bank, NODE_MED_GRENSE))
    node["usikkerhet"]["poster"][0].pop("kilde")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(s).validate(_dok(bank, [node]))


# ---------------------------------------------------------------------------
# Kilden: fil, linje — lest tilbake
# ---------------------------------------------------------------------------

def test_hver_post_har_kilde_og_linjen_leses_tilbake():
    """Krav 3, maalt mot banken: hver post staar i sin egen kildefil."""
    bank = _bank()
    problemer = sjekk_usikkerhet(bank, ROT)
    assert problemer == [], problemer

    poster = list(_poster(bank))
    assert poster, (
        f"ingen node baerer usikkerhetslaget — feltet finnes, men er tomt, og "
        f"svaret «0» ser da ut som kunnskap")


def test_minst_en_node_baerer_feilgrense_fra_sin_egen_kilde():
    """Akseptansen: et tall MED feilgrense, lest fra sin egen kildefil."""
    bank = _bank()
    med_grense = [(n["id"], p) for n, p in _poster(bank)
                  if isinstance(p.get("feilgrense"), (int, float))]
    assert med_grense, (
        "ingen node baerer et tall med feilgrense — da er laget bare nuller")

    node_id, post = med_grense[0]
    kilde = post["kilde"]
    linje = _linje(kilde["fil"], kilde["linje"])
    assert kilde["ordrett"] in linje, (
        f"{node_id}: sitatet staar ikke paa "
        f"{kilde['fil']}:{kilde['linje']}")
    grenser = [float(g) for g in _grenser(linje)]
    assert any(post["feilgrense"] == g for g in grenser), (
        f"{node_id}: feilgrensen {post['feilgrense']} er ikke den "
        f"{kilde['fil']}:{kilde['linje']} oppgir ({grenser})")


def test_beta_staar_som_hull_og_ikke_som_gjetning():
    """Krav 4: β = 0.16 har ingen feilgrense i sin egen kilde. Det er svaret."""
    bank = _bank()
    node = _node(bank, NODE_MED_HULL)
    post = next((p for p in (node.get("usikkerhet") or {}).get("poster") or []
                 if p.get("storrelse") in ("β", "beta")), None)
    assert post is not None, f"{NODE_MED_HULL} baerer ikke β-posten"
    assert post["verdi"] == 0.16
    assert post["feilgrense"] is None, "β er fylt med en feilgrense — det er en gjetning"
    assert post["feilgrense"] != 0, "0 er ikke «ikke oppgitt»"

    linje = _linje(post["kilde"]["fil"], post["kilde"]["linje"])
    assert "±" not in linje, (
        f"kilden {post['kilde']['fil']}:{post['kilde']['linje']} oppgir en "
        f"feilgrense — da er ikke dette et hull")
    # «Ikke oppgitt» er et SVAR: sjekkeren skal godta posten, ikke melde den.
    assert sjekk_usikkerhet(bank, ROT) == []


def test_sjekkeren_svarer_ikke_alt_vel_paa_et_atlas_uten_noder():
    """En sjekk som ikke finner nodene, maa REISE — ikke svare «ingen problemer».

    Maalt under byggingen: sjekkeren leste `noder` mens raafila har `nodes`, og
    svarte `[]` paa en bank der en post nettopp hadde mistet kilden sin. Et tomt
    svar som ser ut som «alt vel» er den samme feilklassen som feltet selv skal
    hindre — derfor pinnes den her.
    """
    with pytest.raises(AtlasLesingFeil):
        sjekk_usikkerhet({"usikkerhet": {}}, ROT)


# ---------------------------------------------------------------------------
# Mutasjonene: en gjetning skal ikke kunne skrives inn
# ---------------------------------------------------------------------------

def _fjern_kilde(post: dict) -> None:
    post.pop("kilde")


def _grense_er_null(post: dict) -> None:
    post["feilgrense"] = 0


def _grense_er_gjettet(post: dict) -> None:
    post["feilgrense"] = 0.05


def _grense_er_fjernet(post: dict) -> None:
    post["feilgrense"] = None


def _sitat_er_oppdiktet(post: dict) -> None:
    post["kilde"]["ordrett"] = "k = 0.415 ± 0.001"


def _fil_finnes_ikke(post: dict) -> None:
    post["kilde"]["fil"] = "docs/papers/efc/finnes-ikke/index.json"


def _linje_finnes_ikke(post: dict) -> None:
    post["kilde"]["linje"] = 99999


def _verdi_er_endret(post: dict) -> None:
    post["verdi"] = 0.42


MUTASJONER = [
    ("usikkerhet uten kilde", _fjern_kilde, "mangler kilde"),
    ("feilgrense = 0 der kilden sier 0.029", _grense_er_null,
     "ikke den kilden oppgir"),
    ("feilgrense gjetter 0.05", _grense_er_gjettet, "ikke den kilden oppgir"),
    ("feilgrense fjernet der kilden oppgir en", _grense_er_fjernet, "OPPGIR"),
    ("sitat som ikke staar i kilden", _sitat_er_oppdiktet, "ordrett"),
    ("kildefil som ikke finnes", _fil_finnes_ikke, "ikke sporet"),
    ("linjenummer utenfor filen", _linje_finnes_ikke, "linjer"),
    ("verdi som ikke staar i kilden", _verdi_er_endret, "verdi"),
]


@pytest.mark.parametrize("navn,endre,ord", MUTASJONER,
                         ids=[m[0] for m in MUTASJONER])
def test_gjetning_felles(navn, endre, ord):
    bank = _bank()
    problemer = sjekk_usikkerhet(_mutert(bank, NODE_MED_GRENSE, endre), ROT)
    assert problemer, f"«{navn}» slapp gjennom sjekkeren"
    assert any(ord in p for p in problemer), (
        f"«{navn}» ble felt, men ikke med grunn: {problemer}")


def test_hullet_kan_ikke_fylles_uten_at_testen_blir_roed():
    """Krav 4 som REGRESJON: en gjetning paa β skal felle."""
    bank = _bank()

    def fyll(post: dict) -> None:
        post["feilgrense"] = 0.02

    problemer = sjekk_usikkerhet(_mutert(bank, NODE_MED_HULL, fyll), ROT)
    assert problemer, "β-hullet ble fylt med en gjetning uten at noe felt det"
