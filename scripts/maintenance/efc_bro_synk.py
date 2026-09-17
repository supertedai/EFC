#!/usr/bin/env python3
"""efc_bro_synk — regenererer de parameteravledede feltene i motorenes
atlas-noder FRA motorene.

Kilden er motoren: `regime_node(params)` er selvbeskrivelsen, og
atlas-noden i `schema/regime_nodes.jsonld` er den AVLEDEDE siden.
Vedlikeholdt for haand på begge sider oppsto drift-klassen maalt
2026-09-17: `efc.water_phase_engine` bar en ELDRE validity-tekst enn
`WaterPhaseEngine` (motoren ble skjerpet i review 2026-09-16, atlaset ble
ikke regenerert), mens testen bare sammenlignet tekstbiter og sa «maskinelt
verifisert».

**Feltvalget er med vilje smalt.** Bare feltene motoren EIER skrives:
den parameteravledede teksten (`regime.validity`, `regime.law_form`).
Resten av noden er kuratert i atlaset — `nivaa` (plateauet), `buss_domene`,
`stipulasjoner`, epistemikk-tekstene — og skal ikke skrives av en motor.
Motorenes avvik i de feltene er målt og ligger i eget kort.

Kanoniske parametre leses fra testmodulen som eier dem, ikke duplisert her:
én kilde gjelder for både testen og synken.

Bruk:
    efc_bro_synk.py --sjekk     # rapportér avvik (exit 1 naar det finnes)
    efc_bro_synk.py --skriv     # skriv de avledede feltene tilbake
    efc_bro_synk.py --json      # maskinlesbar rapport paa stdout
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[2]
ATLAS = ROT / "schema" / "regime_nodes.jsonld"

#: Filformatet atlaset er skrevet i. Skriving som IKKE reproduserer de
#: eksisterende bytes nektes — en generator skal ikke reformatere 289 kB
#: for aa endre to felt.
FORMAT = dict(indent=1, ensure_ascii=False)

#: node-id -> (motormodul, motorklasse, testmodul med de kanoniske
#: parametrene, variabelnavnet der). Nye broer legges til her naar
#: kortet for dem lander; mekanismen er den samme for alle EFCEngine.
BROER = {
    "efc.water_phase_engine": (
        "efc_inference/engine/water.py", "WaterPhaseEngine",
        "tests/test_engine_manifest_bridge.py", "PARAMS"),
}

#: Feltene motoren eier, som sti i noden.
AVLEDEDE = (("regime", "validity"), ("regime", "law_form"))


def _last(sti: str, navn: str):
    spec = importlib.util.spec_from_file_location(navn, ROT / sti)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[navn] = mod
    spec.loader.exec_module(mod)
    return mod


def motoren(modul_sti: str, klassenavn: str):
    """Motoren importeres som PAKKE-modul: motorfilene bruker relativ
    import (``from .base_engine import EFCEngine``), og en
    filsti-lasting gir «attempted relative import with no known parent
    package»."""
    if str(ROT) not in sys.path:
        sys.path.insert(0, str(ROT))
    modul = modul_sti[:-3].replace("/", ".")
    mod = importlib.import_module(modul)
    return getattr(mod, klassenavn)()


def kanoniske(test_sti: str, variabel: str) -> dict:
    mod = _last(test_sti, "bro_kanon_" + Path(test_sti).stem)
    return getattr(mod, variabel)


def sett(node: dict, sti: tuple, verdi) -> None:
    for nokkel in sti[:-1]:
        node = node[nokkel]
    node[sti[-1]] = verdi


def hent(node: dict, sti: tuple):
    for nokkel in sti:
        node = node[nokkel]
    return node


def avvik(tekst: str) -> dict:
    data = json.loads(tekst)
    noder = {n["id"]: n for n in data["nodes"]}
    funn = {}
    for nid, (modul_sti, klasse, test_sti, variabel) in sorted(BROER.items()):
        if nid not in noder:
            funn[nid] = {"feil": "noden finnes ikke i atlaset"}
            continue
        motor_node = motoren(modul_sti, klasse).regime_node(
            kanoniske(test_sti, variabel))
        ulike = {}
        for sti in AVLEDEDE:
            naa = hent(noder[nid], sti)
            skal = hent(motor_node, sti)
            if naa != skal:
                ulike["/".join(sti)] = {"atlas": naa, "motor": skal}
        if ulike:
            funn[nid] = ulike
    return funn


def skriv(tekst: str) -> tuple:
    """Skriver de avledede feltene tilbake. Returnerer (ny tekst, antall felt)."""
    data = json.loads(tekst)
    noder = {n["id"]: n for n in data["nodes"]}
    endret = 0
    for nid, (modul_sti, klasse, test_sti, variabel) in sorted(BROER.items()):
        if nid not in noder:
            raise SystemExit(f"{nid}: noden finnes ikke i atlaset — "
                             "synken skriver ikke nye noder")
        motor_node = motoren(modul_sti, klasse).regime_node(
            kanoniske(test_sti, variabel))
        for sti in AVLEDEDE:
            skal = hent(motor_node, sti)
            if hent(noder[nid], sti) != skal:
                sett(noder[nid], sti, skal)
                endret += 1
    return json.dumps(data, **FORMAT) + "\n", endret


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sjekk", action="store_true",
                    help="rapportér avvik, skriv ingenting")
    ap.add_argument("--skriv", action="store_true",
                    help="skriv de avledede feltene tilbake")
    ap.add_argument("--json", action="store_true",
                    help="maskinlesbar rapport paa stdout")
    a = ap.parse_args()

    tekst = ATLAS.read_text(encoding="utf-8")
    kanonisk = json.dumps(json.loads(tekst), **FORMAT) + "\n"
    if kanonisk != tekst:
        # Nekter heller enn aa reformatere hele fila: en generator som
        # skriver et annet format enn fila staar i, lager en diff som
        # skjuler hva som faktisk ble endret.
        raise SystemExit(
            f"{ATLAS.name}: fila staar ikke i kanonisk format "
            f"({len(tekst)} bytes mot {len(kanonisk)}) — "
            "synken skriver ikke for aa unngaa formatstøy")

    if a.skriv:
        ny, endret = skriv(tekst)
        if endret:
            ATLAS.write_text(ny, encoding="utf-8")
        if a.json:
            print(json.dumps({"endret": endret}, ensure_ascii=False))
        else:
            print(f"  {endret} felt skrevet til {ATLAS.name}")
        if not endret:
            print("  (ingen avvik — synken er idempotent)")
        return 0

    funn = avvik(tekst)
    if a.json:
        print(json.dumps(funn, ensure_ascii=False, indent=1))
    elif funn:
        for nid, ulike in funn.items():
            print(f"  {nid}")
            for felt, v in ulike.items():
                if isinstance(v, dict) and "atlas" in v:
                    print(f"    {felt}\n      atlas : {v['atlas']}"
                          f"\n      motor : {v['motor']}")
                else:
                    print(f"    {felt}: {v}")
    else:
        print("  ingen avvik mellom motor og atlas")
    return 1 if funn else 0


if __name__ == "__main__":
    sys.exit(main())
