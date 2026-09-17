"""Tester for epistemikk v2 — de strukturelle lukningene.

Basert på tre uavhengige linser (Claude Opus 5 second opinion +
deknings-gransking + gap-gransking, 2026-09-17). Hvert hull lukkes
som en VALIDERBAR INVARIANT, ikke som fritekst:

1. Selvanvendelse: atlaset og skjemaet skal være noder i atlaset —
   `efc.selv.atlas` og `efc.selv.skjema` finnes, og
   `efc.selv.paradigme_tid` m.fl. gjør (d) til noder.
2. Stipulasjons-eksplisitthet: motorenes terskler skal kunne
   deklareres i noden med `stipulert_av_oss: true` — og en node kan
   referere motoren som holder terskelen.
3. Falsifiseringsbetingelse: hver node kan bære `ville_falsifisere`
   og `revisjon` (logg over endrede terskler/antakelser).
4. Observatøren i systemet: `observer.er_del_av_systemet` er
   OBLIGATORISK og skal være true for alle noder — vi er
   måleinstrumentet, ikke en gud utenfor.
5. Analogi vs kausalitet: `analogi` med `bryter_der` (disanalogi)
   er obligatorisk når noden erklærer analogi.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ATLAS = Path("schema/regime_nodes.jsonld")
SKJEMA = Path("schema/regime_node.schema.json")


def _atlas() -> dict:
    return json.loads(ATLAS.read_text(encoding="utf-8"))


def _skjema() -> dict:
    return json.loads(SKJEMA.read_text(encoding="utf-8"))


def test_selvanvendelse_nodene_finnes():
    """Atlaset, skjemaet og grunnparadigmene er noder i atlaset."""
    atlas = _atlas()
    noder = {n["id"] for n in atlas["nodes"]}
    for krevd in ("efc.selv.atlas", "efc.selv.skjema",
                  "efc.selv.paradigme_tid", "efc.selv.paradigme_masse"):
        assert krevd in noder, krevd


def test_observer_er_del_av_systemet_obligatorisk():
    skjema = _skjema()
    obs = skjema["$defs"]["RegimeNode"]["properties"]["observer"]
    assert "er_del_av_systemet" in obs.get("required", []), \
        "observer.er_del_av_systemet må være required"
    assert obs["properties"]["er_del_av_systemet"].get("const") is True, \
        "er_del_av_systemet skal være konst sann — vi er instrumentet"


def test_alle_noder_sier_observeren_er_i_systemet():
    for n in _atlas()["nodes"]:
        assert n["observer"]["er_del_av_systemet"] is True, n["id"]


def test_stipulasjonsfeltet_finnes():
    skjema = _skjema()
    node = skjema["$defs"]["RegimeNode"]
    assert "stipulasjoner" in node["properties"]
    sti = node["properties"]["stipulasjoner"]
    assert "stipulert_av_oss" in sti.get("required", [])


def test_selv_nodene_er_agnostiske_eller_paradigme():
    """efc.selv.*-nodene er vår rammes egne — paradigme; de er ikke
    konsensus og ikke akademia."""
    for n in _atlas()["nodes"]:
        if n["id"].startswith("efc.selv."):
            assert n["perspektiv"] in ("paradigme", "agnostikk"), n["id"]


def test_ingen_node_uten_terskel_deklarasjon():
    """Review-krav (PR #444 r1): stipulasjoner.terskler skal være
    fylt med verdi/kilde ELLER eksplisitt deklarasjon — aldri tom
    maske."""
    for n in _atlas()["nodes"]:
        terskler = n["stipulasjoner"]["terskler"]
        assert terskler, (
            f"{n['id']}: tom terskelliste — populer eller deklarer "
            f"eksplisitt at noden ikke har terskler")


def test_motor_nodene_har_motor_referanse():
    """efc.*-motornodene skal peke på motoren som holder terskelen."""
    for n in _atlas()["nodes"]:
        if n["id"].startswith("efc.") and "_engine" in n["id"]:
            assert n["stipulasjoner"].get("motor"), (
                f"{n['id']}: mangler motor-referanse i stipulasjoner")
