#!/usr/bin/env python3
"""efc_bro_konvensjon — eierkonvensjonen for motor↔atlas-broene.

ÉN kilde for hvem som eier hvilket felt når en motors ``regime_node()`` og
atlas-noden i ``schema/regime_nodes.jsonld`` er uenige. Lest av

    scripts/maintenance/efc_bro_synk.py     (skriver motorens felt)
    scripts/maintenance/bro_drift_audit.py  (maaler hele klassen)
    tests/test_bro_konvensjon.py            (binder dem maskinelt)

Bakgrunn (maalt 2026-09-17, t_2dcd2d82): 20 motorer, 20 noder, drift paa
tvers av hele klassen, og avvikene gikk i BEGGE retninger. «Motoren vinner»
er derfor ikke et svar. Regelen er:

  MOTOREN EIER felt som er avledet av motorens parametre eller av maaten
  motoren regner paa. De skrives FRA motoren til atlaset (efc_bro_synk).

  ATLASET EIER felt som er kuraterte paastander OM noden i atlaset: hvor
  den hoerer i plataaet, hvordan konsensusen baeres, hvilke analogier den
  er knyttet til, hva den ikke sier, og hvilken kilde plasseringen hviler
  paa. Motoren kan ikke utlede dem av parametrene sine; naar den likevel
  utsteder dem, maa den si det SAMME som atlaset — og naar de to gaar fra
  hverandre, er det motoren som rettes.

Ingen tredje eier. Et felt motoren utsteder som ikke staar i noen av
tabellene er et HULL, ikke en tredje konvensjon: da stopper baade audit og
test til noen har tatt stilling.
"""
from __future__ import annotations

import importlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

#: Feltstier motoren eier. En liste er EEN verdi her — hele lista
#: sammenlignes og skrives som enhet; bare dict-er flattenes videre.
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

#: Feltstier atlaset eier. Utsteder motoren feltet, maa verdien vaere
#: atlasets; utsteder den det ikke, er det atlaset som baerer det alene.
#: Unntak fra likhet: `/ontology/assumes` er en DELMENGDE — atlaset faar
#: baere kuraterte antakelser motoren ikke kjenner, men motoren faar ikke
#: paastaa noe atlaset ikke har tatt stilling til.
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

#: Stier der motoren faar utstede en DELMENGDE av atlasets liste.
DELMENGDE: tuple[str, ...] = ("/ontology/assumes", "/maale_paradigme/alternativer")

#: Skjema-familier som hoerer til ANDRE node-typer enn motornoder, og som
#: derfor ikke har noen eier i bro-konvensjonen: `/settlement/*` (oppgjoer-
#: noder), `/revisjon` (husets egen bokfoering) og
#: `/observer/maalepavirkning`. De er navngitt her fordi et udekket felt
#: skal vaere en DEKLARERT utelatelse, ikke en stille (regel 64).
UTENFOR_BROEN: tuple[str, ...] = (
    "/settlement/", "/revisjon", "/observer/maalepavirkning",
    "/lagdeling/", "/open_questions",
    "/stipulasjoner/alene_status",
 "/stipulasjoner/buss_status",
 "/stipulasjoner/ikke_falsifiserbar_grunn",
 "/stipulasjoner/motor_status",
 )

#: Motor-klasser som er VARIANTER av en registrert bros node: de arver
#: regime_node() og utsteder SAMME node-id, saa de kan ikke faa hver sin
#: bro. Deklarasjonen er sjekkbar — varianten skal peke paa den noden den
#: varierer, ikke paa en egen.
VARIANTER: dict[str, str] = {
    "SolarFlareEngineBrakdel": "efc.solar_flare_engine",
}

#: Engines DECLARED as non-bridges: they have their own atlas contracts and are
#: not EFC bridges (#527, kept through the language work).
#:
#: A name list is not a declaration by itself — an exemption states WHY, and
#: this one is measured (2026-09-19, t_1f95225a). Each of the twelve:
#:
#:   * points at exactly ONE node in the bank: the engine file's stem is that
#:     node's `stipulasjoner.motor`. That node carries the reason it is not
#:     field-compared — 11 sit in ``MOTOR_UTEN_PARAMKILDE`` (no bridge names
#:     their engine file, so the convention has no canonical parameter SOURCE
#:     for them), and the twelfth (``HomeostaseBufferEngine``) sits in
#:     ``MOTOR_TEKSTAVVIK``.
#:   * is NOT field-compared by ``efc_bro_synk.py``, which measures the 20
#:     registered bridges. That gap is DECLARED and COUNTED: ``--sjekk`` prints
#:     the coverage line and names the twelve, and the count stands in the
#:     sync's own docstring.
#:
#: Registering them was the alternative, and it was measured and rejected HERE:
#: it is not that the engines cannot run or that their parameters would be
#: invented — all 12 are exercised by test_biologi*_engines.py, and 8 of the 12
#: answer ``regime_node({})`` (measured 2026-09-19, t_1f95225a). It is that
#: ``--skriv`` would then write the engine's terse strings over the bank's
#: CURATED prose (``homo.hjerte_syklus``: ``/regime/validity`` is a paragraph in
#: the bank, ``t in [0, 0.8] s; NaN outside`` in the engine), and that a source
#: would have to be named for each of the twelve. Both are the owner's decision,
#: not the sync's.
#:
#: Pinned from BOTH sides by ``tests/test_bro_konvensjon.py``: a class named
#: here that no engine file defines fails, and so does an engine with
#: ``regime_node()`` that no table names.
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
#:
#: PRECISION, measured 2026-09-19 (t_1f95225a): "no source" is not the same as
#: "cannot run". 7 of these 11 do answer `regime_node({})` (evolusjon,
#: feber_regime, fluxus, genregulering, immunologi, okologi, sovn_vaaken —
#: 8 of the 12 engines in all, counting the homeostase buffer above); the
#: remaining 4 raise KeyError without their parameters (aksjonspotensial,
#: cellesyklus, hjerte_syklus, metabolisme), and those values sit in their test
#: modules. The exemption is about the missing SOURCE, and closing it means
#: registering a bridge AND naming a source per engine.
#:
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
    """`/a[0]` -> `/a[]`; lar undertre-stier staa."""
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
    """Hvem eier feltstien — «motor», «atlas», eller None naar den er uklassifisert.

    En oppfoering uten skraastrek eier ogsaa undertreet sitt: `/nivaa` dekker
    `/nivaa/indeks`. `additionalProperties: false` i skjemaet betyr at et
    felt som ikke er navngitt her, er et hull — ikke en tredje eier.
    """
    n = _normaliser(sti)
    for sti_liste, navn in ((MOTOR_EIDE, "motor"), (ATLAS_EIDE, "atlas")):
        for oppfoering in sti_liste:
            if n == oppfoering or n.startswith(oppfoering.rstrip("/") + "/"):
                return navn
    return None


def flat(node: Any, sti: str = "") -> dict:
    """Bladsti -> verdi. Dict-er flattenes; LISTER er blad — en liste er én
    verdi, slik at to noder med ulikt antall elementer gir et ekte avvik i
    stedet for et indekssammenfalt."""
    ut: dict = {}
    if isinstance(node, dict):
        for k, v in node.items():
            ut.update(flat(v, f"{sti}/{k}"))
    else:
        ut[sti] = node
    return ut


def uklassifiserte(node: dict) -> list[str]:
    """Feltstier i `node` som ingen eier tar stilling til."""
    return sorted(p for p in set(flat(node)) if eier(p) is None)


# --------------------------------------------------------------------------
# Kanoniske parametre: testmodulen som eier dem er kilden — ogsaa for synken
# --------------------------------------------------------------------------

#: Elementer i en modulnivaa-liste vi kan lese parametre ut av.
def _kandidat(v: Any, krav: set) -> dict | None:
    if isinstance(v, dict) and all(isinstance(k, str) for k in v) and krav <= set(v):
        return v
    return None


def _last_modul(sti: Path, navn: str):
    """Laster en modul fra fil. Returnerer (modul, feil) — feilen beholdes i
    stedet for aa svelges: en resolver som melder «kunne ikke importeres»
    uten aa si hva som feilet, sender neste leser paa jakt etter feil ting.
    """
    spec = importlib.util.spec_from_file_location(navn, sti)
    if spec is None or spec.loader is None:
        return None, f"{sti}: kunne ikke lages en modulspesifikasjon"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[navn] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:  # noqa: BLE001 — feilen skal VIDEREFORMIDLES
        return None, f"{sti}: {type(exc).__name__}: {exc}"
    return mod, None


def kanoniske_parametre(repo: Path, modul_sti: str, klasse: str,
                        test_sti: str) -> tuple[str, dict]:
    """(kildenavn, parametre) for en motor, lest fra testmodulen.

    Rekkefoelgen er med vilje eksplisitt, ikke en gjetning:

      1. ``bro_kanoniske()`` — testmodulens egen nullargument-bygger. Den
         formen finnes for motorer der parametrene KONSTRUERES (victron:
         serier -> params_for), og for motorer hvis kanoniske dict ligger
         inne i en annen (bakgrunnen: EFC = {**LCDM, ...}).
      2. ``BRO_KANONISKE`` — navnet paa en modulnivaa-dict, naar
         auto-finn ikke peker paa den riktige.
      3. modulnivaa-dict som inneholder ALLE motor.noekler (faerrest
         noekler vinner — et tilfeldig dict som «builtins» kan ikke brukes).
      4. element i en modulnivaa-liste/tuppel (de fem kosmologiske ligger
         slik, som ``KANONISKE = [(motor, params, node_id), ...]``).

    Kaster SystemExit naar ingen finnes: da mangler kilden, og den skal
    meldes, ikke gjettes.
    """
    if str(repo) not in sys.path:
        # Testmodulene importerer motorene som pakkemoduler
        # (efc_inference.engine.*), saa roten maa ligge paa stien FOER
        # testmodulen lastes — ikke bare foer motoren importeres.
        sys.path.insert(0, str(repo))
    mod, feil = _last_modul(repo / test_sti, "bro_kanon_" + Path(test_sti).stem)
    if mod is None:
        raise SystemExit(
            f"{test_sti}: kunne ikke importeres — {feil}\n"
            "  (testmodulene eier de kanoniske parametrene og importerer "
            "motorene: kjør med testvenv-en, ikke en bar python3)")

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
            raise SystemExit(f"{test_sti}: BRO_KANONISKE={navn!r} inneholder "
                             f"ikke {sorted(krav)}")
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
        f"{klasse}: fant ingen kanoniske parametre i {test_sti} "
        f"(krever {sorted(krav)}) — legg til en bro_kanoniske() der")


def les_atlas(repo: Path) -> dict:
    return json.loads((repo / ATLAS[0] / ATLAS[1]).read_text(encoding="utf-8"))


def atlas_noder(repo: Path) -> dict:
    return {n["id"]: n for n in les_atlas(repo)["nodes"]}


def main() -> int:
    """--dekning: hvilke feltstier motorene utsteder, og hvem som eier dem."""
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dekning", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--repo", default=".")
    a = ap.parse_args()

    repo = Path(a.repo).resolve()
    sys.path.insert(0, str(repo / "scripts" / "maintenance"))
    import efc_bro_synk  # noqa: E402  (samme katalog som denne fila)

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
        e = eier(sti) or "UKLASSIFISERT"
        print(f"  {e:<14} {sti}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
