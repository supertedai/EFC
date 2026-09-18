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
    "/ontology/assumes",
    "/maale_paradigme/alternativer",
    "/maale_paradigme/s_regime",
    "/maale_paradigme/sektor",
    "/maale_paradigme/ebe_function",
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
 "/lagdeling/",
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

# The biology engines have their own atlas contracts; they are not EFC bridges.
IKKE_BRO_MOTORER = frozenset({
    "ActionPotentialEngine", "CardiacCycleEngine", "CellCycleEngine",
    "EvolusjonEngine", "FeberRegimeEngine", "FluxusEngine",
    "GenreguleringEngine", "HomeostaseBufferEngine", "ImmunologiEngine",
    "MetabolismEngine", "OkologiEngine", "SovnVaakenEngine",
})

ATLAS = ("schema", "regime_nodes.jsonld")


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
