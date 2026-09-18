#!/usr/bin/env python3
"""efc_bro_synk — regenererer de motoreide feltene i motorenes atlas-noder
FRA motorene, og maaler den atlas-eide siden av den samme broen.

Kilden er motoren: `regime_node(params)` er selvbeskrivelsen, og
atlas-noden i `schema/regime_nodes.jsonld` er den AVLEDEDE siden.
Vedlikeholdt for haand på begge sider oppsto drift-klassen maalt
2026-09-17: `efc.water_phase_engine` bar en ELDRE validity-tekst enn
`WaterPhaseEngine` (motoren ble skjerpet i review 2026-09-16 og atlaset
ble ikke regenerert), mens testen bare sammenlignet tekstbiter og sa
«maskinelt verifisert». Klassen var større enn vann: 20 motorer, 20 noder,
avvik i BEGGE retninger.

  MOTOR-EIDE felt skrives FRA motoren (--skriv).
  ATLAS-EIDE felt rettes i MOTOREN — atlaset er kilden.

Hvem eier hva staar i `efc_bro_konvensjon.py`, og er den ENESTE kilden til
det: baade synken, auditen og testen leser den samme tabellen.

Kanoniske parametre leses fra testmodulen som eier dem, ikke duplisert her:
én kilde gjelder for baade testen og synken.

Bruk:
    efc_bro_synk.py --sjekk     # rapportér avvik (exit 1 naar det finnes)
    efc_bro_synk.py --skriv     # skriv de motoreide feltene tilbake
    efc_bro_synk.py --json      # maskinlesbar rapport paa stdout
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import efc_bro_konvensjon as K  # noqa: E402

ROT = Path(__file__).resolve().parents[2]
ATLAS = ROT / K.ATLAS[0] / K.ATLAS[1]

#: Filformatet atlaset er skrevet i. Skriving som IKKE reproduserer de
#: eksisterende bytes nektes — en generator skal ikke reformatere 289 kB
#: for aa endre to felt.
FORMAT = dict(indent=2, ensure_ascii=False)

#: node-id -> (motormodul, motorklasse, testmodul med de kanoniske
#: parametrene). Registeret ER registeret: enhver EFCEngine med
#: regime_node() skal staa her, og en ny motor som ikke gjoer det er et
#: hull auditen melder. Hvilke parametre som er kanoniske pekes det ikke
#: paa her — konvensjonsmodulen finner dem i testmodulen, slik at testen
#: og synken har ÉN kilde.
BROER = {
    "efc.cluster_engine": (
        "efc_inference/engine/cluster.py", "EFCCluster",
        "tests/test_cosmology_engine_bridges.py"),
    "efc.efc_background_engine": (
        "efc_inference/engine/efc_background.py", "EFCBackgroundEngine",
        "tests/test_efc_background.py"),
    "efc.enerflyt_engine": (
        "efc_inference/engine/enerflyt.py", "EnerFlytEngine",
        "tests/test_enerflyt_engine.py"),
    "efc.grid_mikro_engine": (
        "efc_inference/engine/grid_mikro.py", "GridMikroEngine",
        "tests/test_grid_mikro_engine.py"),
    "efc.growth_engine": (
        "efc_inference/engine/growth.py", "EFCGrowth",
        "tests/test_cosmology_engine_bridges.py"),
    "efc.hubble_engine": (
        "efc_inference/engine/hubble.py", "EFCHubble",
        "tests/test_cosmology_engine_bridges.py"),
    "efc.jordskjelv_engine": (
        "efc_inference/engine/jordskjelv.py", "JordskjelvEngine",
        "tests/test_holding_release_motorer.py"),
    "efc.klima_engine": (
        "efc_inference/engine/klima.py", "KlimaEngine",
        "tests/test_klima_engine.py"),
    "efc.lensing_engine": (
        "efc_inference/engine/lensing.py", "EFCLensing",
        "tests/test_cosmology_engine_bridges.py"),
    "efc.mu_kz_engine": (
        "efc_inference/engine/mu_kz.py", "MuKZEngine",
        "tests/test_mu_kz_module.py"),
    "efc.oekonomi_engine": (
        "efc_inference/engine/oekonomi.py", "OekonomiEngine",
        "tests/test_oekonomi_engine.py"),
    "efc.orbital_engine": (
        "efc_inference/engine/orbital.py", "OrbitalEngine",
        "tests/test_orbital_engine.py"),
    "efc.romvaer_engine": (
        "efc_inference/engine/romvaer.py", "RomvaerEngine",
        "tests/test_romvaer_engine.py"),
    "efc.rotation_engine": (
        "efc_inference/engine/rotation.py", "EFCRotation",
        "tests/test_cosmology_engine_bridges.py"),
    "efc.samfunn_engine": (
        "efc_inference/engine/samfunn.py", "SamfunnEngine",
        "tests/test_samfunn_engine.py"),
    "efc.solar_flare_engine": (
        "efc_inference/engine/solar_flare.py", "SolarFlareEngine",
        "tests/test_holding_release_motorer.py"),
    "efc.tidevann_engine": (
        "efc_inference/engine/tidevann.py", "TidevannEngine",
        "tests/test_tidevann_engine.py"),
    "efc.transient_engine": (
        "efc_inference/engine/transient.py", "TransientEngine",
        "tests/test_holding_release_motorer.py"),
    "efc.victron_cccv_engine": (
        "efc_inference/engine/victron.py", "VictronChargeEngine",
        "tests/test_victron_engine.py"),
    "efc.water_phase_engine": (
        "efc_inference/engine/water.py", "WaterPhaseEngine",
        "tests/test_engine_manifest_bridge.py"),
}


def _sti(sti: str) -> tuple:
    return tuple(p for p in sti.strip("/").split("/") if p)


_MANGEL = object()


def _hent(node: dict, sti: tuple):
    for n in sti:
        if not isinstance(node, dict) or n not in node:
            return _MANGEL
        node = node[n]
    return node


def _sett(node: dict, sti: tuple) -> bool:
    """Setter bladet naar FORELDEREN finnes. Synken lager ikke nye
    undertrær — den vedlikeholder noder som finnes."""
    for n in sti[:-1]:
        if not isinstance(node, dict) or n not in node:
            return False
        node = node[n]
    return True


def _hull(fe: dict, fa: dict) -> list:
    """Motor-eide stier som bare finnes i ATLASET. Motoren utsteder dem ikke,
    saa synken kan ikke vedlikeholde dem — og en side som stille blir
    staaende igjen er nettopp den driften broen finnes for aa stoppe."""
    ut = []
    for sti in sorted(set(fa) - set(fe)):
        if K.eier(sti) == "motor":
            ut.append(sti)
    return ut


def avvik(tekst: str) -> dict:
    """Feltvis avvik, delt paa eier — hva synken kan rette (motoreide), og
    hva motoren maa rettes paa (atlaseide)."""
    funn: dict = {}
    for nid, b in broer(tekst).items():
        atlas = b["atlas"]
        if atlas is None:
            funn[nid] = {"klasse": b["klasse"], "kilde": b["kilde"],
                         "atlas": f"noden {nid!r} finnes ikke i atlaset"}
            continue
        fe, fa = K.flat(b["motor"]), K.flat(atlas)
        motoreide, atlaseide, uklassifisert, mangler = {}, {}, [], []
        for sti in sorted(set(fe) | set(fa)):
            eier = K.eier(sti)
            if eier is None:
                if sti in fe:
                    uklassifisert.append(sti)
                continue
            i_fe, i_fa = sti in fe, sti in fa
            if eier == "motor":
                if i_fe and not i_fa:
                    mangler.append(sti)
                elif i_fe and i_fa and fe[sti] != fa[sti]:
                    motoreide[sti] = {"atlas": fa[sti], "motor": fe[sti]}
            elif i_fe:
                if not i_fa:
                    atlaseide[sti] = {"atlas": "—", "motor": fe[sti]}
                elif sti in K.DELMENGDE:
                    if [x for x in fe[sti] if x not in fa[sti]]:
                        atlaseide[sti] = {"atlas": fa[sti], "motor": fe[sti]}
                elif fe[sti] != fa[sti]:
                    atlaseide[sti] = {"atlas": fa[sti], "motor": fe[sti]}
        hull = _hull(fe, fa)
        if motoreide or atlaseide or uklassifisert or mangler or hull:
            funn[nid] = {"klasse": b["klasse"], "kilde": b["kilde"],
                         "motoreide": motoreide, "atlaseide": atlaseide,
                         "uklassifisert": uklassifisert,
                         "mangler_i_atlaset": mangler, "hull": hull}
    return funn


def skriv(tekst: str) -> tuple:
    """Skriver de motoreide feltene tilbake — ogsaa felt atlaset ikke har
    fra foer, men bare naar forelderen finnes. Returnerer (tekst, antall)."""
    data = json.loads(tekst)
    noder = {n["id"]: n for n in data["nodes"]}
    endret = 0
    for nid, b in sorted(broer(tekst).items()):
        if nid not in noder:
            raise SystemExit(f"{nid}: noden finnes ikke i atlaset — "
                             "synken skriver ikke nye noder")
        for sti in K.MOTOR_EIDE:
            i_sti = _sti(sti)
            m = _hent(b["motor"], i_sti)
            if m is _MANGEL:
                continue
            a = _hent(noder[nid], i_sti)
            if a is not _MANGEL and a == m:
                continue
            if not _sett(noder[nid], i_sti):
                print(f"  {nid}: {sti} — forelderen finnes ikke, ikke skrevet")
                continue
            _sett_verdi(noder[nid], i_sti, m)
            endret += 1
    return json.dumps(data, **FORMAT) + "\n", endret


def _sett_verdi(node: dict, sti: tuple, verdi) -> None:
    for n in sti[:-1]:
        node = node[n]
    node[sti[-1]] = verdi


def motoren(modul_sti: str, klassenavn: str):
    """Motoren importeres som PAKKE-modul: motorfilene bruker relativ
    import (``from .base_engine import EFCEngine``), og en
    filsti-lasting gir «attempted relative import with no known parent
    package»."""
    if str(ROT) not in sys.path:
        sys.path.insert(0, str(ROT))
    mod = importlib.import_module(modul_sti[:-3].replace("/", "."))
    return getattr(mod, klassenavn)()


def broer(tekst: str) -> dict:
    """Motor-node og atlas-node for hver registrerte bro."""
    data = json.loads(tekst)
    noder = {n["id"]: n for n in data["nodes"]}
    ut = {}
    for nid, (modul_sti, klasse, test_sti) in sorted(BROER.items()):
        kilde, params = K.kanoniske_parametre(ROT, modul_sti, klasse, test_sti)
        motor_node = motoren(modul_sti, klasse).regime_node(params)
        ut[nid] = {
            "motor": motor_node,
            "atlas": noder.get(nid),
            "kilde": kilde,
            "klasse": klasse,
        }
    return ut


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sjekk", action="store_true",
                    help="rapportér avvik, skriv ingenting")
    ap.add_argument("--skriv", action="store_true",
                    help="skriv de motoreide feltene tilbake")
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
        for nid, u in funn.items():
            print(f"  {nid}")
            for gruppe in ("motoreide", "atlaseide", "uklassifisert",
                           "mangler_i_atlaset", "hull"):
                v = u.get(gruppe)
                if not v:
                    continue
                print(f"    [{gruppe}]")
                if isinstance(v, dict):
                    for felt, par in v.items():
                        print(f"      {felt}")
                        print(f"        atlas : {par.get('atlas')}")
                        print(f"        motor : {par.get('motor')}")
                elif isinstance(v, list):
                    for x in v:
                        print(f"      {x}")
                else:
                    print(f"      {v}")
    else:
        print("  ingen avvik mellom motor og atlas")
    return 1 if funn else 0


if __name__ == "__main__":
    sys.exit(main())
