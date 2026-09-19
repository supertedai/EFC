"""The uncertainty layer (ADR-086 §3.1): optional, closed, additive — always with a source.

Card `t_af77c6da` (K4). The diagnosis that justifies the field is MEASURED: the
headline numbers stand with an error bound in their own sources —
`k = 0.415 ± 0.029` stands in
`docs/papers/efc/EFC_Phase_3__SPARC_Validation/index.json:5` — while the atlas
had 0 structured uncertainty fields. The atlas thus threw away information the
source had. Nothing is meant to procure NEW uncertainty; the field is only meant
to stop losing it.

Two rules are held by THIS file and not by the schema, deliberately (ADR-086
§3.4: the C10 gate reports a subschema with `properties` as open, so
requiredness must be held by tests until the gate is changed by human word —
`t_2e60afa6`):

1. **A value always has a source.** Every entry names a file AND a line, and the
   line is read back: the value must stand there, the error bound must be the one
   the source states, and the quote must be found. A guess can therefore not be
   written in — it does not exist in the source. `null` is an answer; 0 and a
   guess are not.
2. **β = 0.16 stands without an error bound in its own paper** and must stand as
   a HOLE. «The source does not state it» is the answer, not a defect — and the
   hole must not be fillable by a later edit without this file going red.

The tests mutate the bank in memory and require the checker to FAIL. A test that
only sees that the word «source» exists in a file sees the shape and not the
meaning.
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

from atlas_lesing import (AtlasLesingFeil, finn, plasser,  # noqa: E402
                          sjekk_usikkerhet)
import efc_schema_check  # noqa: E402

SKJEMA_STI = ROT / "schema" / "regime_node.schema.json"
BANK_STI = ROT / "schema" / "regime_nodes.jsonld"

# The node and the entry the measured cases point at. They stand here because
# the tests below name them in the failure message — a number without its
# file:line is a claim without provenance.
NODE_MED_GRENSE = "obs.rar"
NODE_MED_HULL = "obs.bao"

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

requires_jsonschema = pytest.mark.skipif(
    jsonschema is None, reason="jsonschema not installed")


def _skjema() -> dict:
    return json.loads(SKJEMA_STI.read_text(encoding="utf-8"))


def _bank() -> dict:
    return json.loads(BANK_STI.read_text(encoding="utf-8"))


def _node(bank: dict, node_id: str) -> dict:
    return next(n for n in bank["nodes"] if n["id"] == node_id)


def _poster(bank: dict):
    """(node, entry) for every entry in the uncertainty layer."""
    for n in bank["nodes"]:
        for post in ((n.get("usikkerhet") or {}).get("poster") or []):
            yield n, post


def _linje(fil: str, nr: int) -> str:
    return (ROT / fil).read_text(encoding="utf-8").splitlines()[nr - 1]


def _grenser(linje: str) -> list[str]:
    """The numbers that stand right after a ± on the line — the source's own error bounds."""
    return re.findall(r"±\s*([0-9]+(?:\.[0-9]+)?)", linje)


def _dok(bank: dict, noder: list) -> dict:
    d = {k: v for k, v in bank.items() if k not in ("nodes", "relations")}
    d["nodes"] = noder
    d["relations"] = []
    return d


def _mutert(bank: dict, node_id: str, endre) -> dict:
    """The bank with ONE entry changed — the mutation the test kills."""
    ny = copy.deepcopy(bank)
    endre(_node(ny, node_id)["usikkerhet"]["poster"][0])
    return ny


# ---------------------------------------------------------------------------
# The field: optional, closed, additive
# ---------------------------------------------------------------------------

def test_feltet_er_valgfritt_og_lukket():
    """Requirement 1 and 2: declared, closed — and NEVER in `required`."""
    s = _skjema()
    rn = s["$defs"]["RegimeNode"]
    assert "usikkerhet" in rn["properties"], "the field is not declared in the schema"
    assert "usikkerhet" not in rn["required"], (
        "the field stands in RegimeNode.required — then it is not additive, and "
        "no existing node can be unchanged")
    felt = rn["properties"]["usikkerhet"]
    assert felt.get("type") == "object"
    assert felt.get("additionalProperties") is False, (
        "the field's own object is not closed — the C10 gate reports it as open")

    # The C10 gate's own answer, not my reading of the schema.
    aapne = efc_schema_check.open_schemas(s)
    assert aapne == [], f"the schema has open subschemas: {aapne[:3]}"


@requires_jsonschema
def test_ny_node_uten_feltet_validerer_og_plasser_krever_det_ikke():
    """Requirement 2: additive. A node WITHOUT the field must still be valid."""
    s, bank = _skjema(), _bank()
    node = copy.deepcopy(_node(bank, NODE_MED_GRENSE))
    node.pop("usikkerhet", None)
    jsonschema.Draft202012Validator(s).validate(_dok(bank, [node]))

    krav = plasser({"skjema_krav": list(s["$defs"]["RegimeNode"]["required"]),
                    "noder": bank["nodes"]},
                   "en fiskestim i Nordsjoen")
    felt = [k["felt"] for k in krav["krav"]]
    assert "usikkerhet" not in felt, (
        "plasser demands the new field of a new node — requiredness must be "
        "held by tests, not put on new nodes (t_2e60afa6)")


@requires_jsonschema
def test_skjemaet_avviser_post_uten_kilde():
    """Requirement 3 in the schema: an entry without a source is not an entry."""
    s, bank = _skjema(), _bank()
    node = copy.deepcopy(_node(bank, NODE_MED_GRENSE))
    node["usikkerhet"]["poster"][0].pop("kilde")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(s).validate(_dok(bank, [node]))


# ---------------------------------------------------------------------------
# The source: file, line — read back
# ---------------------------------------------------------------------------

def test_hver_post_har_kilde_og_linjen_leses_tilbake():
    """Requirement 3, measured against the bank: every entry stands in its own source file."""
    bank = _bank()
    problemer = sjekk_usikkerhet(bank, ROT)
    assert problemer == [], problemer

    poster = list(_poster(bank))
    assert poster, (
        f"no node carries the uncertainty layer — the field exists, but is "
        f"empty, and the answer «0» then looks like knowledge")


def test_minst_en_node_baerer_feilgrense_fra_sin_egen_kilde():
    """The acceptance: a number WITH an error bound, read from its own source file."""
    bank = _bank()
    med_grense = [(n["id"], p) for n, p in _poster(bank)
                  if isinstance(p.get("feilgrense"), (int, float))]
    assert med_grense, (
        "no node carries a number with an error bound — then the layer is only zeros")

    node_id, post = med_grense[0]
    kilde = post["kilde"]
    linje = _linje(kilde["fil"], kilde["linje"])
    assert kilde["ordrett"] in linje, (
        f"{node_id}: the quote does not stand at "
        f"{kilde['fil']}:{kilde['linje']}")
    grenser = [float(g) for g in _grenser(linje)]
    assert any(post["feilgrense"] == g for g in grenser), (
        f"{node_id}: the error bound {post['feilgrense']} is not the one "
        f"{kilde['fil']}:{kilde['linje']} states ({grenser})")


def test_beta_staar_som_hull_og_ikke_som_gjetning():
    """Requirement 4: β = 0.16 has no error bound in its own source. That is the answer."""
    bank = _bank()
    node = _node(bank, NODE_MED_HULL)
    post = next((p for p in (node.get("usikkerhet") or {}).get("poster") or []
                 if p.get("storrelse") in ("β", "beta")), None)
    assert post is not None, f"{NODE_MED_HULL} does not carry the β entry"
    assert post["verdi"] == 0.16
    assert post["feilgrense"] is None, "β is filled with an error bound — that is a guess"
    assert post["feilgrense"] != 0, "0 is not «not stated»"

    linje = _linje(post["kilde"]["fil"], post["kilde"]["linje"])
    assert "±" not in linje, (
        f"the source {post['kilde']['fil']}:{post['kilde']['linje']} states an "
        f"error bound — then this is not a hole")
    # «Not stated» is an ANSWER: the checker must accept the entry, not report it.
    assert sjekk_usikkerhet(bank, ROT) == []


def test_sjekkeren_svarer_ikke_alt_vel_paa_et_atlas_uten_noder():
    """A check that does not find the nodes must RAISE — not answer «no problems».

    Measured during the build: the checker read `noder` while the raw file has
    `nodes`, and answered `[]` on a bank where an entry had just lost its own
    source. An empty answer that looks like «all well» is the same error class
    the field itself is meant to prevent — therefore it is pinned here.
    """
    with pytest.raises(AtlasLesingFeil):
        sjekk_usikkerhet({"usikkerhet": {}}, ROT)


def test_en_kildefil_i_en_node_gjoer_ikke_begrepsoppslaget_blindere():
    """The field must not cost the atlas an answer it had.

    Measured 2026-09-18: the `kilde.fil` of the BAO paper writes
    «Energy-Flow-Cosmology-…» into obs.bao, and the atlas's own lookup on
    «Energy-Flow Cosmology» then answered with a node instead of with the
    REGISTERED concept — the namespace hit was only added when no node matched.
    The registry is the atlas's answer to «do I own this concept?», and that
    answer must not depend on which nodes happen to cite a file.

    The consequence is measured, not guessed: before, `efc:EFC` was in the
    answer, after it was gone. Both must stand there — the registry first, the
    node after.
    """
    svar = finn(ROT, "Energy-Flow Cosmology", ref="HEAD")
    assert not svar["hull"]
    typer = [t["trefftype"] for t in svar["treff"]]
    assert "navnerom" in typer, (
        f"the registered concept is gone from the answer: {typer}")
    assert typer[0] == "navnerom", (
        f"a registered concept must answer as a concept, not as a loose word: {typer}")
    assert svar["treff"][0]["id"].startswith("efc:")
    assert "ord" in typer, (
        "the node hit disappeared — both answers must stand, not be swapped")
    assert "obs.bao" in [t["id"] for t in svar["treff"]]


# ---------------------------------------------------------------------------
# The mutations: a guess must not be writable in
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
    ("uncertainty without a source", _fjern_kilde, "missing kilde"),
    ("error bound = 0 where the source says 0.029", _grense_er_null,
     "not the one the source states"),
    ("error bound guesses 0.05", _grense_er_gjettet, "not the one the source states"),
    ("error bound removed where the source states one", _grense_er_fjernet, "STATES"),
    ("quote that does not stand in the source", _sitat_er_oppdiktet, "ordrett"),
    ("source file that does not exist", _fil_finnes_ikke, "is not tracked"),
    ("line number outside the file", _linje_finnes_ikke, "lines"),
    ("value that does not stand in the source", _verdi_er_endret, "verdi"),
]


@pytest.mark.parametrize("navn,endre,ord", MUTASJONER,
                         ids=[m[0] for m in MUTASJONER])
def test_gjetning_felles(navn, endre, ord):
    bank = _bank()
    problemer = sjekk_usikkerhet(_mutert(bank, NODE_MED_GRENSE, endre), ROT)
    assert problemer, f"«{navn}» slipped through the checker"
    assert any(ord in p for p in problemer), (
        f"«{navn}» was killed, but not with a reason: {problemer}")


def test_hullet_kan_ikke_fylles_uten_at_testen_blir_roed():
    """Requirement 4 as a REGRESSION: a guess on β must kill."""
    bank = _bank()

    def fyll(post: dict) -> None:
        post["feilgrense"] = 0.02

    problemer = sjekk_usikkerhet(_mutert(bank, NODE_MED_HULL, fyll), ROT)
    assert problemer, "the β hole was filled with a guess without anything killing it"
