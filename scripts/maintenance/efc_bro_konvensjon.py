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
    "/analogi",
    "/falsifiserbarhet",
    "/prediction",
    "/settlement",
)

#: Paths where the engine may emit a SUBSET of the atlas's list.
DELMENGDE: tuple[str, ...] = ("/ontology/assumes", "/maale_paradigme/alternativer")

#: Schema families that belong to node TYPES other than engine nodes, and
#: that therefore have no owner in the bridge convention: `/settlement/*`
#: (settlement nodes), `/revisjon` (the house's own bookkeeping) and
#: `/observer/maalepavirkning`. They are named here because an uncovered
#: field must be a DECLARED omission, not a silent one (rule 64).
UTENFOR_BROEN: tuple[str, ...] = (
    "/settlement/", "/revisjon", "/observer/maalepavirkning",
 "/lagdeling/",
 "/stipulasjoner/alene_status",
 "/stipulasjoner/buss_status",
 "/stipulasjoner/ikke_falsifiserbar_grunn",
 "/stipulasjoner/motor_status",
 )

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
