"""Retningen på en relasjon skal bety noe — og ett predikat skal ha én betydning.

Målt på `main` 2026-09-18 (`t_efcfe7f0`, lukke K6 i lukkelista `t_7feb0525`):

* **6 `OBSERVED_IN` har en motor som subjekt:** `efc.hubble_engine→obs.bao`,
  `efc.growth_engine→obs.fsigma8`, `efc.growth_engine→obs.s8`,
  `efc.lensing_engine→obs.cmb_lensing`, `efc.cluster_engine→obs.cluster_hmf`,
  `efc.cluster_engine→obs.cluster_mass`. De øvrige 23 går observasjon → regime.
  Samme ord, to betydninger: «observert i dette regimet» og «observert gjennom
  denne motoren».
* **Ett par har samme predikat i begge retninger:** `homo.aksjonspotensial` ↔
  `homo.hjerte_syklus` (`ANALOGOUS_TO`, eksakt 2 rader).

`ANALOGOUS_TO` er den eneste som får være symmetrisk. Den skal da stå **én
gang** per par, ikke to — symmetrien er en egenskap ved predikatet, ikke to
påstander. Alle andre predikater er rettet og skal ha én retning.

Testene er skrevet for å være røde på `main` før rettingen, og grønne etter.
"""
from __future__ import annotations

import collections
import json
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
BANK = ROT / "schema" / "regime_nodes.jsonld"

#: Predikater der symmetri er MENINGEN. `ANALOGOUS_TO` sier at to fenomener
#: følger samme mønster — det er sant i begge retninger, og å skrive det to
#: ganger er å påstå det samme to ganger.
SYMMETRISKE = {"ANALOGOUS_TO"}

#: Faser som betyr «et middel å observere gjennom»: observatøren, instrumentet,
#: eller en motor som regner størrelsen ut.
MIDDEL_FASER = {"observer", "instrument", "regime_engine", "computation_engine"}


def _bank() -> dict:
    return json.loads(BANK.read_text(encoding="utf-8"))


def _noder(bank: dict) -> dict:
    return {n["id"]: n for n in bank["nodes"]}


def _fase(noder: dict, node_id: str) -> str:
    return (noder.get(node_id) or {}).get("phase")


def test_ingen_par_har_samme_predikat_begge_veier():
    """Dobbelthet i to retninger er én påstand som er skrevet feil, ikke to."""
    bank = _bank()
    telling: dict = collections.defaultdict(set)
    for r in bank["relations"]:
        par = (r["predicate"], frozenset([r["subject"], r["object"]]))
        telling[par].add((r["subject"], r["object"]))

    feil = [(k[0], sorted(k[1])) for k, v in telling.items()
            if len(v) > 1 and k[0] not in SYMMETRISKE]
    assert not feil, (
        "relasjoner oppgitt i begge retninger med samme predikat: "
        f"{feil} — velg én retning, eller erklær predikatet symmetrisk")


def test_symmetriske_predikater_star_en_gang_per_par():
    """Symmetrien er en egenskap ved predikatet. Da er to rader en duplikat."""
    bank = _bank()
    telling: dict = collections.defaultdict(int)
    for r in bank["relations"]:
        if r["predicate"] in SYMMETRISKE:
            telling[(r["predicate"], frozenset([r["subject"], r["object"]]))] += 1

    duplikater = [(k[0], sorted(k[1]), n) for k, n in telling.items() if n > 1]
    assert not duplikater, (
        "symmetriske predikater skal stå én gang per par, ikke én per retning: "
        f"{duplikater}")


def test_observed_in_har_en_betydning():
    """`OBSERVED_IN` skal gå observasjon → regime. Aldri med en motor som subjekt."""
    bank = _bank()
    noder = _noder(bank)
    feil = [(r["subject"], r["object"],
             _fase(noder, r["subject"])) for r in bank["relations"]
            if r["predicate"] == "OBSERVED_IN"
            and _fase(noder, r["subject"]) != "observation"]
    assert not feil, (
        "OBSERVED_IN med noe annet enn en observasjon som subjekt — da betyr "
        f"predikatet to ting: {feil}")


def test_observed_through_peker_paa_et_middel():
    """`OBSERVED_THROUGH` betyr «X observeres gjennom Y» — Y er midlet."""
    bank = _bank()
    noder = _noder(bank)
    feil = [(r["subject"], r["object"], _fase(noder, r["object"]))
            for r in bank["relations"]
            if r["predicate"] == "OBSERVED_THROUGH"
            and _fase(noder, r["object"]) not in MIDDEL_FASER]
    assert not feil, (
        "OBSERVED_THROUGH peker ikke på et middel å observere gjennom: "
        f"{feil}")


def test_hver_relasjon_har_eksisterende_knutepunkter():
    """En kant til en node som ikke finnes er en referanse, ikke en relasjon."""
    bank = _bank()
    ider = set(_noder(bank))
    feil = [(r["subject"], r["predicate"], r["object"])
            for r in bank["relations"]
            if r["subject"] not in ider or r["object"] not in ider]
    assert not feil, f"relasjoner med endepunkt som ikke finnes: {feil}"
