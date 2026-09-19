"""THE ENGINE THREAD: node -> engine file -> what the engine answers.

Measured 2026-09-19 (t_c015b6ee) across the 116 public nodes:
`stipulasjoner.motor` carried 8 forms for ONE concept —

    70  empty        ("")                     -> no engine
     4  absent       (efc.l0-l3, motor_status) -> no engine
    20  module name  ("water", "hubble", ...) -> THE FORM
    17  node id      ("efc.water_solid", ...) -> names a node that is ABSENT
     3  node id      ("efc.klima_engine", ...) -> names a node that exists
     2  free text    ("efc.orbital_engine (banemekanikk)", "ingen egen motor ...")

The form is now named in ``scripts/maintenance/efc_bro_konvensjon.py``: the
value is the engine's MODULE NAME, i.e. ``efc_inference/engine/<value>.py``.
This test kills the other forms, and runs the chain end to end for every node
that names an engine.

What the chain does, and what it does not guess:

  * parameters come from the bridge pointing at the SAME engine file, through
    the house loader (``K.kanoniske_parametre``). With no such bridge, ``{}``
    is used and the engine's ``REQUIRED_PARAMS`` must be empty — otherwise the
    node must sit in ``K.MOTOR_UTEN_PARAMKILDE``.
  * which node the engine is, is the answer from ``regime_node()["id"]`` — not
    an assumption. When the engine answers a DIFFERENT node than the one that
    named it, the relation must sit in ``K.MOTOR_DELT``.
  * when the answer IS the node, the engine's ``regime.name``/``validity`` are
    compared with the atlas node's. When those differ and the atlas is not an
    older copy, the node must sit in ``K.MOTOR_TEKSTAVVIK``.

All three sets are pinned EXACTLY: a deviation cannot slide in unseen. That is
the point — a list that only grows is the silent tolerance the convention
exists to prevent.
"""
from __future__ import annotations

import copy
import importlib
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
for _sti in (REPO, REPO / "scripts" / "maintenance"):
    if str(_sti) not in sys.path:
        sys.path.insert(0, str(_sti))

import efc_bro_konvensjon as K  # noqa: E402
import efc_bro_synk as S  # noqa: E402


def _bank() -> dict:
    return json.loads((REPO / K.ATLAS[0] / K.ATLAS[1]).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def noder() -> dict:
    return {n["id"]: n for n in _bank()["nodes"]}


@pytest.fixture(scope="module")
def offentlige(noder: dict) -> dict:
    return {i: n for i, n in noder.items() if n.get("synlighet") == "offentlig"}


# ---------------------------------------------------------------------------
# The form
# ---------------------------------------------------------------------------

def _form(verdi) -> str:
    if verdi is None:
        return "absent"
    if verdi == "":
        return "empty"
    if K.har_motorform(verdi) and K.motorfil(REPO, verdi).exists():
        return "module name"
    if isinstance(verdi, str) and verdi.startswith("efc."):
        return "node id"
    return "free text"


def test_motor_er_motorens_modulnavn(offentlige: dict) -> None:
    """«Which engine» has ONE form: the module name, which must have a file.

    The form is not the node id (17 of 20 node-id values named a node that was
    absent, and NO node id is a file) and not free text (a sentence cannot be
    looked up). Empty or absent means "no engine", which is declared: those
    nodes say why in ``motor_status``.
    """
    feil = []
    for nid, n in sorted(offentlige.items()):
        stip = n.get("stipulasjoner") or {}
        if "motor" not in stip:
            continue
        if not K.har_motorform(stip["motor"]):
            feil.append((nid, stip["motor"], _form(stip["motor"])))
            continue
        if stip["motor"] and not K.motorfil(REPO, stip["motor"]).exists():
            feil.append((nid, stip["motor"], "module name, no file"))
    linjer = "\n".join(f"  {nid:<28} {v!r:<44} [{f}]" for nid, v, f in feil)
    assert not feil, (
        f"{len(feil)} nodes do not name their engine by module name "
        f"(<value> [form]):\n{linjer}")


def test_motor_og_motor_status_utelukker_hverandre(noder: dict) -> None:
    """A node has ITS engine, or it says WHY it has none.

    The schema states it as either/or ("Either the node has an engine, OR it
    says here why it does not"). Both at once is a hole, not a third form: then
    the node asserts two things and neither one binds.
    """
    begge = sorted(nid for nid, n in noder.items()
                   if ((n.get("stipulasjoner") or {}).get("motor")
                       and (n.get("stipulasjoner") or {}).get("motor_status")))
    assert not begge, f"nodes carrying both motor and motor_status: {begge}"


# ---------------------------------------------------------------------------
# The chain: node -> engine file -> what the engine answers
# ---------------------------------------------------------------------------

def _klasse_i(modul_sti: str) -> type:
    """The ONLY EFCEngine subclass defined in the engine file. Doubt FAILS."""
    base = importlib.import_module("efc_inference.engine.base_engine").EFCEngine
    modul = importlib.import_module(modul_sti[:-3].replace("/", "."))
    kand = [v for v in vars(modul).values()
            if isinstance(v, type) and issubclass(v, base)
            and v.__module__ == modul.__name__ and hasattr(v, "regime_node")
            and v.__name__ not in K.VARIANTER]
    assert len(kand) == 1, (
        f"{modul_sti}: {len(kand)} engine classes "
        f"({[c.__name__ for c in kand]}) — the choice is not obvious, and then "
        "this test does not guess")
    return kand[0]


def _kanonisk(repo: Path, motormodul: str) -> dict | None:
    """The canonical parameters for the engine in `motormodul`, or None.

    The source is the bridge pointing at the SAME engine file — the house
    loader, not a new one. An engine without a bridge has no canonical source
    here; then this answers None, and the call must have empty REQUIRED_PARAMS.
    """
    for nid, (modul, klasse, test) in sorted(S.BROER.items()):
        if modul == motormodul:
            return K.kanoniske_parametre(repo, modul, klasse, test)[1]
    return None


def _traad(repo: Path, offentlige: dict) -> dict:
    """Measures the chain for every node that names an engine."""
    ut: dict = {"lukker": [], "delt": [], "avvik": []}
    for nid, n in sorted(offentlige.items()):
        motor = (n.get("stipulasjoner") or {}).get("motor")
        if not motor:
            continue
        motormodul = f"efc_inference/engine/{motor}.py"
        if not (repo / motormodul).exists():
            ut["avvik"].append((nid, motor, "ENGINE_FILE_ABSENT"))
            continue
        klasse = _klasse_i(motormodul)
        params = _kanonisk(repo, motormodul)
        instans = klasse()
        krav = sorted(set(getattr(instans, "REQUIRED_PARAMS", []) or []))
        if params is None and krav:
            if nid not in K.MOTOR_UTEN_PARAMKILDE:
                ut["avvik"].append((nid, motor, f"NO_PARAMETER_SOURCE {krav}"))
            continue
        try:
            svar = instans.regime_node(params or {})
        except Exception as exc:  # noqa: BLE001 — must be FORWARDED, not swallowed
            ut["avvik"].append((nid, motor, f"ERROR {type(exc).__name__}: {exc}"))
            continue
        svar_id = svar.get("id")
        if svar_id == nid:
            tekst = svar.get("regime") or {}
            atlas = n.get("regime") or {}
            ulike = sorted(f for f in ("name", "validity")
                           if tekst.get(f) != atlas.get(f))
            if ulike and nid not in K.MOTOR_TEKSTAVVIK:
                ut["avvik"].append(
                    (nid, motor, f"TEXT_DEVIATION {ulike}: engine="
                                 f"{tekst.get(ulike[0])!r} "
                                 f"atlas={atlas.get(ulike[0])!r}"))
            else:
                ut["lukker"].append(nid)
        elif svar_id in offentlige:
            ut["delt"].append((nid, svar_id))
        else:
            ut["avvik"].append((nid, motor, f"ANSWERS_UNKNOWN_NODE {svar_id!r}"))
    return ut


@pytest.fixture(scope="module")
def traad(offentlige: dict) -> dict:
    return _traad(REPO, offentlige)


def test_motoren_svarer_noden_sin(traad: dict) -> None:
    """The chain end to end: the node names a file, the engine answers its node.

    "The engine answers ``regime_node()['id']``; the atlas node owns
    ``regime.validity``" — and where those part ways, this fails.
    """
    assert not traad["avvik"], (
        f"{len(traad['avvik'])} nodes where the chain does not close: "
        f"{traad['avvik']}")


def test_kjeden_er_kjort_for_hele_klassen(traad: dict, offentlige: dict) -> None:
    """A measured list, not an impression: how many close, how many ride.

    The test above could go green by the class shrinking. This one states how
    many were actually measured, and how they split.
    """
    med_motor = sorted(nid for nid, n in offentlige.items()
                       if (n.get("stipulasjoner") or {}).get("motor"))
    maalt = len(traad["lukker"]) + len(traad["delt"])
    assert maalt + len(K.MOTOR_UTEN_PARAMKILDE) >= len(med_motor), (
        f"{len(med_motor)} public nodes name an engine, but only {maalt} were "
        "measured along the chain")
    assert len(traad["lukker"]) >= 1, (
        "no node has a chain that closes — then this test proves nothing")


def test_de_delte_forholdene_er_deklarer(traad: dict) -> None:
    """"Computed by" is a relation, not a tolerance.

    A node naming an engine that answers a DIFFERENT node asserts that the
    engine's code holds its boundaries. That must sit in ``K.MOTOR_DELT`` —
    with WHICH node the engine answers. When the engine answers something else
    than the declaration says, the link has moved without anyone saying so.
    """
    maalt = dict(traad["delt"])
    feil = [f"{nid}: the answer is {svar!r}, the declaration says "
            f"{K.MOTOR_DELT[nid][0]!r}"
            for nid, svar in maalt.items()
            if nid in K.MOTOR_DELT and K.MOTOR_DELT[nid][0] != svar]
    assert not feil, f"shared relations that have moved: {feil}"
    assert set(maalt) == set(K.MOTOR_DELT), (
        "K.MOTOR_DELT and the measurement are not the same set: "
        f"measured without a declaration={sorted(set(maalt) - set(K.MOTOR_DELT))}, "
        f"declared without a measurement={sorted(set(K.MOTOR_DELT) - set(maalt))}")


def test_paramkilden_er_maalt_og_pinnet(offentlige: dict) -> None:
    """Every node in ``MOTOR_UTEN_PARAMKILDE`` exists, and names an engine.

    The exemption must name a REAL lack — a node naming an engine whose
    parameters we cannot reach from the bank — not a node that was forgotten.
    """
    for nid in K.MOTOR_UTEN_PARAMKILDE:
        assert nid in offentlige, f"{nid}: named, but not public"
        motor = (offentlige[nid].get("stipulasjoner") or {}).get("motor")
        assert motor, f"{nid}: listed as having no source, without an engine"
        assert K.motorfil(REPO, motor).exists(), f"{nid}: {motor}.py is absent"


# ---------------------------------------------------------------------------
# The chain must KILL — otherwise it measures nothing
# ---------------------------------------------------------------------------

def test_kjeden_feller_naar_den_gaar_fra_hverandre(offentlige: dict) -> None:
    """The mutant is built in memory: one node's declared validity changes.

    A comparison that only reports "no deviations" is green even when it
    compares nothing. Here the atlas node's validity moves away from the
    engine's, and the chain must name exactly that node — untouched file, no
    write.
    """
    nid = "efc.hubble_engine"
    mutert = copy.deepcopy(offentlige)
    mutert[nid]["regime"]["validity"] = "A DIFFERENT VALIDITY THAN THE ENGINE'S"
    ut = _traad(REPO, mutert)
    navngitt = [a for a in ut["avvik"] if a[0] == nid]
    assert navngitt, (
        f"the chain does not kill {nid} when the atlas node's validity takes a "
        f"value other than the engine's — then it does not compare "
        f"(deviations: {ut['avvik'][:3]})")
    assert "TEXT_DEVIATION" in navngitt[0][2], navngitt
