#!/usr/bin/env python3
"""efc_bro_konvensjon — the ownership convention for the engine↔atlas bridges.

ONE source for who owns which field when an engine's ``regime_node()`` and
the atlas node in ``schema/regime_nodes.jsonld`` disagree. Read by

    scripts/maintenance/efc_bro_synk.py     (writes the engine's fields)
    scripts/maintenance/bro_drift_audit.py  (measures the whole class)
    tests/test_bro_konvensjon.py            (binds them mechanically)

Background (measured 2026-09-17, t_2dcd2d82): 20 engines, 20 nodes, drift
across the whole class, and the deviations went in BOTH directions. "The
engine wins" is therefore not an answer. The rule is:

  THE ENGINE OWNS fields derived from the engine's parameters or from the way
  the engine computes. They are written FROM the engine to the atlas
  (efc_bro_synk).

  THE ATLAS OWNS fields that are curated claims ABOUT the node in the atlas:
  where it belongs in the plateau, how the consensus is carried, which
  analogies it is tied to, what it does not say, and which source the
  placement rests on. The engine cannot derive them from its parameters; when
  it emits them anyway, it must say the SAME thing as the atlas — and when the
  two drift apart, it is the engine that is corrected.

No third owner. A field the engine emits that is in neither table is a HOLE,
not a third convention: then both the audit and the test stop until someone
has taken a position.
"""
from __future__ import annotations

import importlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

#: Field paths the engine owns. A list is ONE value here — the whole list
#: is compared and written as a unit; only dicts are flattened further.
MOTOR_EIDE: tuple[str, ...] = (
    "/synlighet",
    "/regime/name",
    "/regime/validity",
    "/regime/law_form",
    "/phase",
    "/episenter",
    "/buffer/role",
    "/buffer/note",
    "/measure/instrument",
    "/measure/measurer",
    "/measure/target",
    "/measure/placement",
    "/measure/compression",
    "/measure/proxy_chain",
    "/emergence/loop",
    "/emergence/properties",
    "/fractal/pattern",
    "/fractal/note",
    "/coupling/local",
    "/coupling/global",
    "/coupling/empathy_note",
    "/observer/awareness",
    "/observer/bandwidth",
    "/observer/er_del_av_systemet",
    "/maale_paradigme/koordinater",
    "/maale_paradigme/enheter",
    "/maale_paradigme/status",
    "/stipulasjoner/stipulert_av_oss",
    "/stipulasjoner/terskler",
    "/stipulasjoner/motor",
)

#: Field paths the atlas owns. If the engine emits the field, the value must
#: be the atlas's; if it does not, the atlas carries it alone.
#: Exception from equality: `/ontology/assumes` is a SUBSET — the atlas may
#: carry curated assumptions the engine does not know, but the engine may not
#: claim anything the atlas has not taken a position on.
ATLAS_EIDE: tuple[str, ...] = (
    "/id",
    "/nivaa",
    "/epistemikk",
    "/perspektiv",
    "/ontology/source",
    "/ontology/proveniens",
    "/ontology/assumes",
    "/observer/c_s_posisjon",
    "/maale_paradigme/alternativer",
    "/maale_paradigme/s_regime",
    "/maale_paradigme/sektor",
    "/maale_paradigme/ebe_function",
    "/maale_paradigme/klarhetsfunksjon",
    "/rcmp",
    "/rcmp/instrument",
    "/rcmp/observabel",
    "/rcmp/teori",
    "/rcmp/overlap",
    "/rcmp/deklarasjon",
    "/stipulasjoner/alene_status",
    "/stipulasjoner/buss_status",
    "/stipulasjoner/ikke_falsifiserbar_grunn",
    "/stipulasjoner/motor_status",
    "/buss_domene",
    "/ville_falsifisere",
    "/stipulasjoner/ikke_falsifiserbar_grunn",
    "/analogi",
    "/falsifiserbarhet",
    "/usikkerhet",
    "/prediction",
    "/settlement",
)

#: Paths where the engine may emit a SUBSET of the atlas's list.
DELMENGDE: tuple[str, ...] = ("/ontology/assumes", "/maale_paradigme/alternativer")

#: Field paths the SCHEMA can express that NO bridge owns — each with the
#: REASON written down. An omission must be named AND justified (rule 64):
#: a name without a reason is a silent omission with one extra step, and the
#: next reader cannot tell whether it still holds.
#:
#: Measured 2026-09-19 (t_c8d06315) for `/open_questions`: 21 nodes in the
#: bank carry it and 0 of the 20 registered bridges do; no engine emits it (0
#: hits in `efc_inference/`); the generator never writes it — the schema says
#: so itself ("the ONLY source of questions in the atlas: the generator never
#: writes a question itself"); what writes it is the NODE'S OWN text, the
#: migration (`migrer_buss_status_til_open_questions.py`) and curation in the
#: bank. It is therefore not an engine field, and it must not have a bridge.
#:
#: FIVE entries were REMOVED here on 2026-09-19 (t_c8d06315) because they
#: contradicted the tables above: `/settlement/` and the four
#: `/stipulasjoner/*` paths stood in BOTH places, and `eier()` answered
#: "atlas" for all five. Measured: 11 field paths in registered bridges hit
#: them (`efc.growth_engine` carried `/settlement/*`, seven nodes carried
#: `/stipulasjoner/alene_status`). An omission that contradicts ownership is
#: not an omission, it is a claim that the field stands without a rule — and
#: that claim was false. `test_hver_utelatelse_er_navngitt_og_begrunnet` keeps
#: it out from here on.
UTENFOR_BROEN: dict[str, str] = {
    # Reconciliation and revision: the house's own bookkeeping, not bridges.
    "/revisjon": (
        "the house's own bookkeeping node type, never an engine node; 0 bank "
        "nodes carry it today — declared so the schema field stays usable "
        "without pretending it has an owner"),
    # Measured 2026-09-19: 33 bank nodes carry it — all layered biology and
    # human nodes — and 0 of the 20 registered bridges do.
    "/lagdeling/": (
        "belongs to the layered biology nodes (33 bank nodes, 0 of the 20 "
        "registered bridges): the engine side has no layer partition to "
        "publish"),
    "/observer/maalepavirkning": (
        "a curated meta-question about the observer, not derivable from any "
        "engine parameter; 0 bank nodes carry it today"),
    "/open_questions": (
        "the NODE'S OWN text in the bank: written by the migration from "
        "stipulasjoner.buss_status and by curation, never by an engine and "
        "never by the generator; 21 bank nodes carry it, 0 of the 20 "
        "registered bridges do"),
}

#: Engine classes that are VARIANTS of a registered bridge's node: they
#: inherit regime_node() and emit the SAME node id, so they cannot each have
#: their own bridge. The declaration is checkable — the variant must point at
#: the node it varies, not at one of its own.
VARIANTER: dict[str, str] = {
    "SolarFlareEngineBrakdel": "efc.solar_flare_engine",
}

# The biology engines have their own atlas contracts; they are not EFC bridges.
IKKE_BRO_MOTORER = frozenset({
    "ActionPotentialEngine", "CardiacCycleEngine", "CellCycleEngine",
    "EvolusjonEngine", "FeberRegimeEngine", "FluxusEngine",
    "GenreguleringEngine", "HomeostaseBufferEngine", "ImmunologiEngine",
    "MetabolismEngine", "OkologiEngine", "SovnVaakenEngine",
})

ATLAS = ("schema", "regime_nodes.jsonld")

#: The file format the bank is written in — ONE source, read by BOTH
#: writers (``efc_bro_synk.py``, ``bygg_kildenoder.py``) and by the format
#: guard inside the sync. It lives here because it is the same convention as
#: ownership: how the bank is written is not each writer's taste.
#:
#: Measured 2026-09-18 (t_2bc25575): the format had drifted from the
#: declaration. The file was indent=1 from 2026-09-17T19:37 until #545
#: (d826235b, 2026-09-18T14:10) rewrote the WHOLE file as indent=2 as a side
#: effect of adding nodes. The sync refuses to write when the file is not in
#: the declared format, and it refused in silence: `--sjekk` failed for ALL
#: 20 bridges, not just the three someone was looking for, and no CI job ran
#: it.
#:
#: The indent was chosen to AVOID reformatting 605 kB (14 300 lines, every
#: line changed), which would have collided with every open atlas branch:
#: the file stands in indent=2, the format is pinned to what the file
#: actually is, and the guard is unchanged — if anyone rewrites the bank
#: again, `--sjekk` goes red again, and then the file is the wrong side.
FORMAT: dict[str, Any] = dict(indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# "Which engine" — ONE form, named 2026-09-19 (t_c015b6ee)
#
# The form is the MODULE NAME: the value X means the engine file is
# `efc_inference/engine/X.py`. Not a node id. Not free text.
#
# Measured 2026-09-19 across the 116 public nodes: 8 forms for ONE concept.
#
#   70  empty        ("")                       -> no engine (declared)
#    4  absent       (efc.l0-l3, with status)   -> no engine (declared)
#   20  module name  ("water", "hubble", ...)   -> THE FORM
#   17  node id      ("efc.water_solid", ...)   -> names a node that is ABSENT
#    3  node id      ("efc.klima_engine", ...)  -> names a node that exists
#    2  free text    ("efc.orbital_engine (banemekanikk)", "ingen egen motor ...")
#
# The form is measured, not chosen:
#   * `/stipulasjoner/motor` sits in MOTOR_EIDE — the engine owns that field and
#     writes it (efc_bro_synk --skriv). An engine can answer its own module
#     name; it cannot answer which atlas node drives a phase node.
#   * 20 of 20 registered bridges already carried the module name (measured).
#   * the node-id form does not resolve: 17 of those 20 values name a node that
#     is absent from the bank, and NO node id is a file.
#
# The form is not the engine's `name` either: victron.py declares
# name='victron_cccv' against file stem 'victron' — and it is the FILE that
# must exist. The file stem is therefore the only value checkable for every
# engine.
#
# A node naming an engine must have an engine file. A node without an engine
# says WHY in `motor_status` (the schema: "Either the node has an engine, OR it
# says here why it does not"). Both at once is a hole, not a third form —
# measured 2026-09-19: 0 of 126 nodes did that; the regression is pinned by
# tests/test_motor_traaden.py.
MOTOR_MONSTER = re.compile(r"^[a-z0-9][a-z0-9_]*$")

#: Nodes naming an engine that answers a DIFFERENT node than themselves. The
#: relation is "computed by", not "is": the engine issues its own node, and
#: these nodes carry that engine. Each value is (the engine's node, the
#: reason). The test pins the declaration — a new node cannot slip in unseen.
#:
#: t_c015b6ee named the relation and normalised THE FORM; it did not settle
#: whether each link holds physically. One is flagged uncertain below, and the
#: doubt sits where it belongs: at the declaration.
MOTOR_DELT: dict[str, tuple[str, str]] = {
    "h2o.liquid": (
        "efc.water_phase_engine",
        "phase node: the bank points at water.py for its thresholds"),
    "h2o.triple_point": (
        "efc.water_phase_engine",
        "the phase map's reference point; inherits the boundaries"),
    "h2o.solid": (
        "efc.water_phase_engine",
        "phase node under h2o.triple_point; inherits the boundaries"),
    "h2o.gas": (
        "efc.water_phase_engine",
        "phase node under h2o.triple_point; inherits the boundaries"),
    "h2o.supercritical": (
        "efc.water_phase_engine",
        "phase node under h2o.triple_point; inherits the boundaries"),
    "h2o.droplet": (
        "efc.water_phase_engine",
        "phase node under h2o.triple_point; inherits the boundaries"),
    "efc.lag_s": (
        "efc.rotation_engine",
        "the structure layer (halos, rotation curves) — the rotation engine "
        "computes it"),
    "efc.lag_d": (
        "efc.efc_background_engine",
        "the dynamics layer (expansion, g+) — the background engine computes it"),
    "efc.lag_c0": (
        "efc.klima_engine",
        "UNCERTAIN: the bank named the climate engine when THE FORM was "
        "normalised, but a 0D energy balance does not hold the boundaries of a "
        "clarity layer (C(S), propofol EEG). The form is fixed; the link is "
        "NOT verified — measured 2026-09-19 (t_c015b6ee)"),
    "kosmos.asteroider": (
        "efc.orbital_engine",
        "the instrument node reads JPL's impact risk; orbital mechanics is the "
        "orbital engine's (the parenthesis from the old free-text value)"),
}

#: Nodes where the chain node -> engine file -> the engine's answer can NOT be
#: run from the bank: the engine requires parameters, and it is not registered
#: as a bridge, so the canonical parameter source (K.kanoniske_parametre, read
#: from a bridge's test module) does not exist. Pinned by the test so the count
#: cannot grow unseen — every new line here is an engine without a bridge.
#:
#: Measured 2026-09-19 (t_c015b6ee): 11 of 12 biology engines. Only
#: HomeostaseBufferEngine has empty REQUIRED_PARAMS and runs on {}.
#: Closing this means registering those engines as bridges, not guessing their
#: parameters here.
MOTOR_UTEN_PARAMKILDE: dict[str, str] = {
    "homo.aksjonspotensial": "ActionPotentialEngine: 6 parameters, no bridge",
    "homo.cellesyklus": "CellCycleEngine: 7 parameters, no bridge",
    "homo.evolusjon": "EvolusjonEngine: 2 parameters, no bridge",
    "homo.feber_regime": "FeberRegimeEngine: 1 parameter, no bridge",
    "homo.fluxus": "FluxusEngine: 4 parameters, no bridge",
    "homo.genregulering": "GenreguleringEngine: 6 parameters, no bridge",
    "homo.hjerte_syklus": "CardiacCycleEngine: 6 parameters, no bridge",
    "homo.immunologi": "ImmunologiEngine: 6 parameters, no bridge",
    "homo.metabolisme": "MetabolismEngine: 5 parameters, no bridge",
    "homo.okologi": "OkologiEngine: 7 parameters, no bridge",
    "homo.sovn_vaaken": "SovnVaakenEngine: 7 parameters, no bridge",
}

#: Nodes where the engine's `regime` and the atlas node's do NOT agree, and the
#: atlas is not an older copy of the engine. This is a hole in the convention,
#: not in the data: MOTOR_EIDE says the engine owns `/regime/validity`, yet
#: here the atlas node carries CURATED text with a source and an analogy
#: caveat — text the engine cannot issue. Who owns that field when the text is
#: curated rather than derived is NOT settled. Named, not tolerated: the test
#: pins the set exactly, so a further conflict cannot slide in.
MOTOR_TEKSTAVVIK: dict[str, str] = {
    "homo.homeostase_buffer":
        "the atlas carries Levin 2019-curated validity + an ANALOGY caveat "
        "(the battery's SOC buffer, the latent heat of ice); the engine issues "
        "a parameter window. Measured 2026-09-19 (t_c015b6ee) — the text was "
        "NOT overwritten, since that would delete the curation",
}


def motorfil(repo: Path, motor: str) -> Path:
    """The engine file `stipulasjoner.motor` points at. ONE form, ONE place.

    Readers must not build that path themselves: two places guessing the same
    path is exactly the drift the form exists to stop.
    """
    return repo / "efc_inference" / "engine" / f"{motor}.py"


def har_motorform(motor: Any) -> bool:
    """Is the value in the named form? Empty or absent means "no engine"."""
    if motor in (None, ""):
        return True
    return isinstance(motor, str) and bool(MOTOR_MONSTER.match(motor))


def _normaliser(sti: str) -> str:
    """`/a[0]` -> `/a[]`; leaves subtree paths alone."""
    ut, i = [], 0
    while i < len(sti):
        if sti[i] == "[":
            j = sti.find("]", i)
            i = j + 1
            ut.append("[]")
            continue
        ut.append(sti[i])
        i += 1
    return "".join(ut)


def eier(sti: str) -> str | None:
    """Who owns the field path — "motor", "atlas", or None when unclassified.

    An entry with no trailing slash also owns its subtree: `/nivaa` covers
    `/nivaa/indeks`. `additionalProperties: false` in the schema means a field
    not named here is a hole — not a third owner.
    """
    n = _normaliser(sti)
    for sti_liste, navn in ((MOTOR_EIDE, "motor"), (ATLAS_EIDE, "atlas")):
        for oppfoering in sti_liste:
            if n == oppfoering or n.startswith(oppfoering.rstrip("/") + "/"):
                return navn
    return None


def flat(node: Any, sti: str = "") -> dict:
    """Leaf path -> value. Dicts are flattened; LISTS are leaves — a list is
    one value, so two nodes with different element counts give a real
    deviation instead of an index collapse."""
    ut: dict = {}
    if isinstance(node, dict):
        for k, v in node.items():
            ut.update(flat(v, f"{sti}/{k}"))
    else:
        ut[sti] = node
    return ut


def uklassifiserte(node: dict) -> list[str]:
    """Field paths in `node` that no owner has taken a position on."""
    return sorted(p for p in set(flat(node)) if eier(p) is None)


# --------------------------------------------------------------------------
# Canonical parameters: the test module that owns them is the source — the
# sync uses it too
# --------------------------------------------------------------------------

#: Elements in a module-level list we can read parameters out of.
def _kandidat(v: Any, krav: set) -> dict | None:
    if isinstance(v, dict) and all(isinstance(k, str) for k in v) and krav <= set(v):
        return v
    return None


def _last_modul(sti: Path, navn: str):
    """Loads a module from a file. Returns (module, error) — the error is kept
    instead of swallowed: a resolver that reports "could not be imported"
    without saying what failed sends the next reader hunting the wrong thing.
    """
    spec = importlib.util.spec_from_file_location(navn, sti)
    if spec is None or spec.loader is None:
        return None, f"{sti}: could not build a module spec"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[navn] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:  # noqa: BLE001 — the error must be PASSED ON
        return None, f"{sti}: {type(exc).__name__}: {exc}"
    return mod, None


def kanoniske_parametre(repo: Path, modul_sti: str, klasse: str,
                        test_sti: str) -> tuple[str, dict]:
    """(source name, parameters) for an engine, read from the test module.

    The order is deliberately explicit, not a guess:

      1. ``bro_kanoniske()`` — the test module's own zero-argument builder.
         That form exists for engines whose parameters are CONSTRUCTED
         (victron: series -> params_for), and for engines whose canonical dict
         sits inside another (the background: EFC = {**LCDM, ...}).
      2. ``BRO_KANONISKE`` — the name of a module-level dict, when
         auto-discovery does not point at the right one.
      3. module-level dict holding ALL of engine.REQUIRED_PARAMS (fewest keys
         wins — a random dict such as "builtins" cannot be used).
      4. member of a module-level list/tuple (the five cosmological ones sit
         like that, as ``KANONISKE = [(engine, params, node_id), ...]``).

    Raises SystemExit when none is found: then the source is missing, and it
    must be reported, not guessed.
    """
    if str(repo) not in sys.path:
        # The test modules import the engines as package modules
        # (efc_inference.engine.*), so the root must be on the path BEFORE the
        # test module is loaded — not just before the engine is imported.
        sys.path.insert(0, str(repo))
    mod, feil = _last_modul(repo / test_sti, "bro_kanon_" + Path(test_sti).stem)
    if mod is None:
        raise SystemExit(
            f"{test_sti}: could not be imported — {feil}\n"
            "  (the test modules own the canonical parameters and import the "
            "engines: run with the test venv, not a bare python3)")

    motor = getattr(importlib.import_module(modul_sti[:-3].replace("/", ".")), klasse)()
    krav = set(getattr(motor, "REQUIRED_PARAMS", []) or [])

    bygger = getattr(mod, "bro_kanoniske", None)
    if callable(bygger):
        p = bygger()
        if isinstance(p, dict) and krav <= set(p):
            return f"bro_kanoniske() ({test_sti})", p

    navn = getattr(mod, "BRO_KANONISKE", None)
    if isinstance(navn, str):
        p = _kandidat(getattr(mod, navn, None), krav)
        if p is None:
            raise SystemExit(f"{test_sti}: BRO_KANONISKE={navn!r} does not "
                             f"contain {sorted(krav)}")
        return f"{navn} ({test_sti})", p

    dict_kand: list[tuple[str, dict]] = []
    liste_kand: list[tuple[str, dict]] = []
    for felt, v in vars(mod).items():
        if felt.startswith("__"):
            continue
        k = _kandidat(v, krav)
        if k is not None:
            dict_kand.append((felt, k))
        elif isinstance(v, (list, tuple)):
            for i, el in enumerate(v):
                dikt = None
                if isinstance(el, (list, tuple, set)):
                    for sub in el:
                        if _kandidat(sub, krav) is not None:
                            dikt = sub
                            break
                if dikt is not None:
                    liste_kand.append((f"{felt}[{i}]", dikt))
    dict_kand.sort(key=lambda kv: len(kv[1]))
    if dict_kand:
        return f"{dict_kand[0][0]} ({test_sti})", dict_kand[0][1]
    if liste_kand:
        return f"{liste_kand[0][0]} ({test_sti})", liste_kand[0][1]
    raise SystemExit(
        f"{klasse}: found no canonical parameters in {test_sti} "
        f"(requires {sorted(krav)}) — add a bro_kanoniske() there")


def les_atlas(repo: Path) -> dict:
    return json.loads((repo / ATLAS[0] / ATLAS[1]).read_text(encoding="utf-8"))


def atlas_noder(repo: Path) -> dict:
    return {n["id"]: n for n in les_atlas(repo)["nodes"]}


def main() -> int:
    """--dekning: which field paths the engines emit, and who owns them."""
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dekning", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--repo", default=".")
    a = ap.parse_args()

    repo = Path(a.repo).resolve()
    sys.path.insert(0, str(repo / "scripts" / "maintenance"))
    import efc_bro_synk  # noqa: E402  (same directory as this file)

    brukt: dict[str, list[str]] = {}
    for nid in sorted(efc_bro_synk.BROER):
        modul, klasse, test = efc_bro_synk.BROER[nid]
        kilde, params = kanoniske_parametre(repo, modul, klasse, test)
        node = getattr(importlib.import_module(
            modul[:-3].replace("/", ".")), klasse)().regime_node(params)
        for sti in flat(node):
            brukt.setdefault(_normaliser(sti), []).append(nid)
    if a.json:
        print(json.dumps(brukt, ensure_ascii=False, indent=1))
        return 0
    for sti in sorted(brukt):
        e = eier(sti) or "UNCLASSIFIED"
        print(f"  {e:<14} {sti}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
