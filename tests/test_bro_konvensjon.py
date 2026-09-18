"""Eierkonvensjonen for motor↔atlas-broene — testet paa HELE klassen.

Maalt 2026-09-17 (t_2dcd2d82): 20 motorer, 20 atlas-noder, drift i BEGGE
retninger. Den gamle testen dekket vann alene
(``test_engine_node_and_its_atlas_node_agree_on_derived_fields``), og
trinn 11-testen dekket de fem kosmologiske paa ``validity``/``law_form``.
Resten av klassen hadde ingen vakt, og derfor drev den.

Denne testen maaler ALLE registrerte broer mot den SAMME tabellen som
synken bruker (``scripts/maintenance/efc_bro_konvensjon.py``):

  * MOTOR-EIDE felt: atlaset skal baere motorens verdi (synken skriver den).
  * ATLAS-EIDE felt: motoren skal baere atlasets verdi — atlaset er kilden.
  * Ingen tredje eier: et felt motoren utsteder som ingen eier tar stilling
    til, er et HULL og feiler testen.

Sammenligningen her er skrevet uavhengig av synkens gruppering: testen
laster fixturen (motor + atlas + kanoniske parametre) fra synken, men
sammenligner selv. En test som bare kaller verktoyet ville maalt verktoyet.
"""
from __future__ import annotations

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


@pytest.fixture(scope="module")
def broer() -> dict:
    return S.broer(S.ATLAS.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def atlas() -> dict:
    return K.atlas_noder(REPO)


# ---------------------------------------------------------------------------
# Dekning: registeret ER registeret
# ---------------------------------------------------------------------------

def test_hver_motor_med_regime_node_er_registrert(broer: dict) -> None:
    """En EFCEngine med regime_node() uten BROER-oppfoering er et HULL:
    da finnes det en bro ingen maaler. Ny motor -> registrer den her.

    En klasse som er en VARIANT av en registrert nodes motor (arver
    regime_node() og utsteder samme node-id) kan ikke faa egen bro —
    den deklareres i ``K.VARIANTER``, og deklarasjonen sjekkes: varianten
    skal peke paa DEN noden den varierer."""
    base = importlib.import_module("efc_inference.engine.base_engine").EFCEngine
    klasser = {}
    for fil in sorted((REPO / "efc_inference" / "engine").glob("*.py")):
        if fil.stem in ("__init__", "base_engine"):
            continue
        modul = importlib.import_module(f"efc_inference.engine.{fil.stem}")
        for navn, verdi in vars(modul).items():
            if (isinstance(verdi, type) and issubclass(verdi, base)
                    and verdi.__module__ == modul.__name__
                    and hasattr(verdi, "regime_node")):
                klasser[navn] = verdi
    registrert = {klasse for _, klasse, _ in S.BROER.values()} | set(K.VARIANTER) | K.IKKE_BRO_MOTORER
    assert set(klasser) == registrert, (
        f"motorer uten bro: {sorted(set(klasser) - registrert)}; "
        f"broer uten motor: {sorted(registrert - set(klasser))}")

    for klasse, nid in K.VARIANTER.items():
        assert nid in S.BROER, f"{klasse}: variant av ukjent node {nid}"
        _, params = K.kanoniske_parametre(REPO, *S.BROER[nid])
        node = klasser[klasse]().regime_node(params)
        assert node == broer[nid]["motor"], (
            f"{klasse} utsteder ikke den samme noden som {nid} — da er den "
            "ikke en variant, og skal ha sin egen bro")


def test_hver_bro_peker_paa_en_node_i_atlaset(broer: dict, atlas: dict) -> None:
    mangler = [nid for nid in broer if nid not in atlas]
    assert not mangler, f"broer uten atlas-node: {mangler}"
    feil_id = sorted(nid for nid, b in broer.items()
                     if b["motor"]["id"] != nid)
    assert not feil_id, (
        "motoren utsteder en annen id enn den registrerte broen: "
        f"{[(nid, broer[nid]['motor']['id']) for nid in feil_id]}")


def test_ingen_engine_node_i_atlaset_uten_bro(atlas: dict) -> None:
    """Speilvendt: en ``efc.*_engine``-node i atlaset uten bro er like blind."""
    uten = sorted(nid for nid in atlas
                  if nid.startswith("efc.") and nid.endswith("_engine")
                  and nid not in S.BROER)
    assert not uten, f"engine-noder uten bro: {uten}"


# ---------------------------------------------------------------------------
# Feltvis: motorens node mot atlas-noden
# ---------------------------------------------------------------------------

def _sammenlign(broer: dict) -> list:
    """Returnerer alle avvik som (node, eier, sti, atlas, motor)."""
    avvik = []
    for nid, b in sorted(broer.items()):
        if b["atlas"] is None:
            continue          # egen test: bro uten atlas-node
        fe, fa = K.flat(b["motor"]), K.flat(b["atlas"])
        for sti in sorted(set(fe) | set(fa)):
            eier = K.eier(sti)
            i_fe, i_fa = sti in fe, sti in fa
            if eier is None:
                if i_fe:
                    avvik.append((nid, "UKLASSIFISERT", sti, "—", fe[sti]))
                continue
            if eier == "motor":
                if i_fe and not i_fa:
                    avvik.append((nid, "MANGLER-I-ATLASET", sti,
                                  "—", fe[sti]))
                elif i_fa and not i_fe:
                    avvik.append((nid, "HULL", sti, fa[sti], "—"))
                elif fe[sti] != fa[sti]:
                    avvik.append((nid, "MOTOR-EIDE", sti, fa[sti], fe[sti]))
                continue
            if not i_fe:
                continue
            if not i_fa:
                avvik.append((nid, "ATLAS-EIDE", sti, "—", fe[sti]))
            elif sti in K.DELMENGDE:
                if [x for x in fe[sti] if x not in fa[sti]]:
                    avvik.append((nid, "ATLAS-EIDE (delmengde)", sti,
                                  fa[sti], fe[sti]))
            elif fe[sti] != fa[sti]:
                avvik.append((nid, "ATLAS-EIDE", sti, fa[sti], fe[sti]))
    return avvik


def test_ingen_avvik_mellom_motor_og_atlas(broer: dict) -> None:
    """Hele klassen, alle felt — motorens regime_node() mot atlas-noden."""
    avvik = _sammenlign(broer)
    linjer = "\n".join(
        f"  {nid:<28} [{eier}] {sti}\n      atlas: {a}\n      motor: {m}"
        for nid, eier, sti, a, m in avvik)
    assert not avvik, f"{len(avvik)} avvik:\n{linjer}"


def test_synken_kan_vedlikeholde_alt_den_eier(broer: dict) -> None:
    """HULL-familien alene: et motor-eid felt atlaset baerer og motoren ikke
    utsteder, kan synken ikke regenerere — det staar stille og driver."""
    hull = [(nid, sti) for nid, eier, sti, a, m in _sammenlign(broer)
            if eier in ("HULL", "MANGLER-I-ATLASET")]
    assert not hull, f"motor-eide felt uten motpart: {hull}"


# ---------------------------------------------------------------------------
# Konvensjonen mot skjemaet: ingen felt uten eier
# ---------------------------------------------------------------------------

def _skjemablader(node: dict, sti: str = "") -> set:
    """Alle bladstier i et skjema-undertre (utvidbare objekt er lov i seg
    selv, men da stopper vi — eierskapet gjelder det navngitte feltet)."""
    ut: set = set()
    if not isinstance(node, dict):
        return ut
    egenskaper = node.get("properties")
    if not egenskaper:
        return {sti} if sti else ut
    for navn, under in egenskaper.items():
        ut |= _skjemablader(under, f"{sti}/{navn}")
    return ut


def _utenfor_broen(sti: str) -> bool:
    n = K._normaliser(sti)
    return any(n == u.rstrip("/") or n.startswith(u.rstrip("/") + "/")
               for u in K.UTENFOR_BROEN)


def test_hvert_skjema_felt_har_en_eier(broer: dict) -> None:
    """Et felt skjemaet kan uttrykke, men konvensjonen ikke nevner, er et
    hull: da finnes det ingen regel for hva som skjer naar de to gaar fra
    hverandre (regel 64: deklarer hver enhet, ogsaa de udekkede).

    Skjemaet rommer ogsaa node-typer som ikke er motornoder (oppgjoer,
    revisjon). De er DEKLARERT utenfor i ``K.UTENFOR_BROEN`` — en navngitt
    utelatelse, ikke en stille.
    """
    skjema = json.loads(
        (REPO / "schema" / "regime_node.schema.json").read_text(encoding="utf-8"))
    blader = _skjemablader(skjema["$defs"]["RegimeNode"])
    uten = sorted(sti for sti in blader
                  if K.eier(sti) is None and not _utenfor_broen(sti))
    assert not uten, f"skjema-felt uten eier i konvensjonen: {uten}"

    flate: set = set()
    for b in broer.values():
        flate |= set(K.flat(b["motor"])) | set(K.flat(b["atlas"]))
    brukt = sorted(sti for sti in flate if K.eier(sti) is None)
    assert not brukt, f"felt i bruk uten eier: {brukt}"


def test_stipulasjoner_motor_er_motorens_kortnavn(broer: dict) -> None:
    """`stipulasjoner.motor` skal vaere motorens kortnavn — ikke node-id-en
    (to konvensjoner levde side om side, maalt 2026-09-18: 28 noder med
    kortnavn, 2 med node-id). Navnet maa vaere entydig: to noder kan ikke
    peke paa samme motor gjennom denne broen."""
    navn = {}
    for nid, b in sorted(broer.items()):
        verdi = b["motor"]["stipulasjoner"]["motor"]
        assert verdi and " " not in verdi, f"{nid}: {verdi!r} er ikke et kortnavn"
        assert verdi != nid, f"{nid}: node-id-en er ikke motorens navn"
        assert b["atlas"]["stipulasjoner"]["motor"] == verdi, (
            f"{nid}: atlaset sier {b['atlas']['stipulasjoner']['motor']!r}")
        assert verdi not in navn, (
            f"{nid} og {navn[verdi]} peker paa samme motornavn {verdi!r}")
        navn[verdi] = nid
