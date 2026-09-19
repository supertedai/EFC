"""The direction of a relation must mean something — and one predicate must
have one meaning.

Measured on `main` 2026-09-18 (`t_efcfe7f0`, closing K6 in the closing list
`t_7feb0525`):

* **6 `OBSERVED_IN` have an engine as subject:** `efc.hubble_engine→obs.bao`,
  `efc.growth_engine→obs.fsigma8`, `efc.growth_engine→obs.s8`,
  `efc.lensing_engine→obs.cmb_lensing`, `efc.cluster_engine→obs.cluster_hmf`,
  `efc.cluster_engine→obs.cluster_mass`. The remaining 23 go observation →
  regime. The same word, two meanings: «observed in this regime» and
  «observed through this engine».
* **One pair has the same predicate in both directions:**
  `homo.aksjonspotensial` ↔ `homo.hjerte_syklus` (`ANALOGOUS_TO`, exactly 2
  rows).

`ANALOGOUS_TO` is the only one allowed to be symmetric. It must then stand
**once** per pair, not twice — the symmetry is a property of the predicate,
not two claims. Every other predicate is directed and must have one
direction.

The tests are written to be red on `main` before the correction, and green
after.
"""
from __future__ import annotations

import collections
import json
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
BANK = ROT / "schema" / "regime_nodes.jsonld"

#: Predicates where symmetry is the POINT. `ANALOGOUS_TO` says that two
#: phenomena follow the same pattern — it is true in both directions, and
#: writing it twice is asserting the same thing twice.
SYMMETRISKE = {"ANALOGOUS_TO"}

#: Phases that mean «a means of observing through»: the observer, the
#: instrument, or an engine that computes the quantity.
MIDDEL_FASER = {"observer", "instrument", "regime_engine", "computation_engine"}


def _bank() -> dict:
    return json.loads(BANK.read_text(encoding="utf-8"))


def _noder(bank: dict) -> dict:
    return {n["id"]: n for n in bank["nodes"]}


def _fase(noder: dict, node_id: str) -> str:
    return (noder.get(node_id) or {}).get("phase")


def test_ingen_par_har_samme_predikat_begge_veier():
    """A doubling in two directions is one claim written wrongly, not two."""
    bank = _bank()
    telling: dict = collections.defaultdict(set)
    for r in bank["relations"]:
        par = (r["predicate"], frozenset([r["subject"], r["object"]]))
        telling[par].add((r["subject"], r["object"]))

    feil = [(k[0], sorted(k[1])) for k, v in telling.items()
            if len(v) > 1 and k[0] not in SYMMETRISKE]
    assert not feil, (
        "relations stated in both directions with the same predicate: "
        f"{feil} — choose one direction, or declare the predicate symmetric")


def test_symmetriske_predikater_star_en_gang_per_par():
    """The symmetry is a property of the predicate. Then two rows are one
    duplicate."""
    bank = _bank()
    telling: dict = collections.defaultdict(int)
    for r in bank["relations"]:
        if r["predicate"] in SYMMETRISKE:
            telling[(r["predicate"], frozenset([r["subject"], r["object"]]))] += 1

    duplikater = [(k[0], sorted(k[1]), n) for k, n in telling.items() if n > 1]
    assert not duplikater, (
        "symmetric predicates must stand once per pair, not once per "
        f"direction: {duplikater}")


def test_observed_in_har_en_betydning():
    """`OBSERVED_IN` must go observation → regime, never with an engine as
    subject."""
    bank = _bank()
    noder = _noder(bank)
    feil = [(r["subject"], r["object"],
             _fase(noder, r["subject"])) for r in bank["relations"]
            if r["predicate"] == "OBSERVED_IN"
            and _fase(noder, r["subject"]) != "observasjon"]
    assert not feil, (
        "OBSERVED_IN with something other than an observation as subject — "
        f"then the predicate means two things: {feil}")


def test_observed_through_peker_paa_et_middel():
    """`OBSERVED_THROUGH` means «X is observed through Y» — Y is the means."""
    bank = _bank()
    noder = _noder(bank)
    feil = [(r["subject"], r["object"], _fase(noder, r["object"]))
            for r in bank["relations"]
            if r["predicate"] == "OBSERVED_THROUGH"
            and _fase(noder, r["object"]) not in MIDDEL_FASER]
    assert not feil, (
        "OBSERVED_THROUGH does not point at a means of observing through: "
        f"{feil}")


def test_hver_relasjon_har_eksisterende_knutepunkter():
    """An edge to a node that does not exist is a reference, not a relation."""
    bank = _bank()
    ider = set(_noder(bank))
    feil = [(r["subject"], r["predicate"], r["object"])
            for r in bank["relations"]
            if r["subject"] not in ider or r["object"] not in ider]
    assert not feil, f"relations with an endpoint that does not exist: {feil}"
