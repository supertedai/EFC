"""Test av det generiske regime-node-skjemaet og H2O-instansen (trinn 2).

TDD: skrives FOER skjemaet finnes — skal feile ved innlesing.

Forankring (skjemaets kanoniske kilde):
  regime/proxy/placement/episenter/compression er definert i
  «Regime-Bound Measurement in Complex Systems: Proxy, Placement, and
  Validity» (DOI 10.6084/m9.figshare.31564123, 2026-03-07) og i
  meta-referansen docs/papers/meta/Proxy/. Mortens utvidelser (maal,
  maaler, maaleinstrument, proxychain, buffer/holding, fase, ontologi,
  observator-baandbredde, emergence-loop, fraktal, lokal-global
  kobling) er strukturelle beholdere — skjemaet hevder ingen fysikk.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# Felles leser av git-treet — se scripts/maintenance/_repo_tre.py.
_MAINT = _REPO / "scripts" / "maintenance"
if str(_MAINT) not in sys.path:
    sys.path.insert(0, str(_MAINT))
from _repo_tre import filer as _tre_filer  # noqa: E402

SCHEMA_PATH = _REPO / "schema" / "regime_node.schema.json"
INSTANCE_PATH = _REPO / "schema" / "regime_nodes.jsonld"

# Den private hjemmeadressen skrives aldri rett ut i denne fila. Den er selv
# sporet, og regresjonsvernet nedenfor skanner alle sporede filer — skrevet
# rett ut ville vakten felt seg selv og måttet hatt et unntak. Bygd av deler
# er ingen fil unntatt, heller ikke vakten selv.
HJEM = "Hassel" + "vegen"
POSTSTED = "4051 " + "Sola"

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

requires_jsonschema = pytest.mark.skipif(
    jsonschema is None, reason="jsonschema ikke installert")


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _instance() -> dict:
    return json.loads(INSTANCE_PATH.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Skjemaet
# --------------------------------------------------------------------------

@requires_jsonschema
def test_schema_is_valid_and_closed():
    s = _schema()
    jsonschema.Draft202012Validator.check_schema(s)
    assert s.get("additionalProperties") is False


def test_schema_requires_mortens_node_fields():
    s = _schema()
    node_req = set(s["$defs"]["RegimeNode"]["required"])
    assert {"id", "regime", "phase", "measure", "episenter", "buffer",
            "ontology", "observer", "emergence", "fractal",
            "coupling"} <= node_req


def test_schema_uses_canonical_episenter_spelling():
    """Review runde 1: kanonisk term i kilde-README-en og PR-en er
    «episenter» — det engelske «epicenter» skal ikke vaere feltnavn."""
    s = _schema()
    props = s["$defs"]["RegimeNode"]["properties"]
    assert "episenter" in props
    assert "epicenter" not in props


def test_context_maps_ids_and_relation_targets_to_iris():
    """Review runde 1: instansen skal vaere en lenket JSON-LD-graf —
    node-id-er og relasjonsendepunkter er IRI-referanser, ikke loes tekst."""
    inst = _instance()
    ctx = inst["@context"]
    assert ctx.get("id") == "@id"
    assert ctx.get("subject") == {"@type": "@id"}
    assert ctx.get("object") == {"@type": "@id"}


def test_schema_requires_measurement_chain():
    s = _schema()
    measure = s["$defs"]["RegimeNode"]["properties"]["measure"]
    req = set(measure["required"])
    assert {"target", "measurer", "instrument", "proxy_chain",
            "placement", "compression"} <= req
    pc = measure["properties"]["proxy_chain"]
    assert pc["type"] == "array"


def test_schema_observer_bandwidth_is_explicit():
    """Observatoren ser et vindu av spekteret — baandbredde er et paakrevd
    felt, og bevissthetsstatusen er en deklarert klasse, ikke en pastand."""
    s = _schema()
    obs = s["$defs"]["RegimeNode"]["properties"]["observer"]
    assert {"bandwidth", "awareness"} <= set(obs["required"])
    awareness_enum = obs["properties"]["awareness"]["enum"]
    assert "instrument_window" in awareness_enum
    assert "hypothesis_open" in awareness_enum
    assert "not_claimed" in awareness_enum


def test_schema_relation_predicates_include_transition_and_emergence():
    s = _schema()
    preds = s["$defs"]["RegimeRelation"]["properties"]["predicate"]["enum"]
    assert "TRANSITIONS_TO" in preds
    assert "EMERGES_FROM" in preds
    assert "COUPLED_TO" in preds


# --------------------------------------------------------------------------
# H2O-instansen
# --------------------------------------------------------------------------

@requires_jsonschema
def test_h2o_instance_validates_against_schema():
    jsonschema.Draft202012Validator(_schema()).validate(_instance())


def test_h2o_instance_has_four_phase_nodes():
    ids = {n["id"] for n in _instance()["nodes"]}
    assert {"h2o.solid", "h2o.liquid", "h2o.gas",
            "h2o.supercritical"} <= ids


def test_h2o_instance_has_triple_point_node():
    ids = {n["id"] for n in _instance()["nodes"]}
    assert "h2o.triple_point" in ids


def test_h2o_transitions_meet_at_triple_point():
    """De tre faseovergangene skal alle vaere representert — det er det
    trippelpunktet BETYR i denne strukturen."""
    rels = _instance()["relations"]
    preds = {(r["subject"], r["predicate"], r["object"]) for r in rels}
    assert ("h2o.solid", "TRANSITIONS_TO", "h2o.liquid") in preds
    assert ("h2o.liquid", "TRANSITIONS_TO", "h2o.gas") in preds
    assert ("h2o.solid", "TRANSITIONS_TO", "h2o.gas") in preds


def test_every_node_declares_empathy_coupling():
    """Systemisk empati: hver node maa deklarere sin lokale rolle OG sin
    globale rekkevidde — ingen node er bare lokal."""
    inst = _instance()
    for n in inst["nodes"]:
        c = n["coupling"]
        assert c["local"], n["id"]
        assert c["global"], n["id"]


def test_every_node_has_ontology_source():
    """Ontologiske antakelser skal ha kilde — ikke sveve loest."""
    inst = _instance()
    for n in inst["nodes"]:
        assert n["ontology"]["source"], n["id"]


def test_phase_nodes_declare_regime_validity():
    """Hver fasenode maa si HVOR den gjelder (gyldighetsomraade)."""
    inst = _instance()
    for n in inst["nodes"]:
        if n["id"].startswith("h2o.") and n["id"] != "h2o.triple_point":
            assert n["regime"]["validity"], n["id"]


# --------------------------------------------------------------------------
# Trinn 3: regnbuen — generisitetstesten (en emergence, ikke en fase)
# --------------------------------------------------------------------------

def test_rainbow_nodes_exist():
    """Regnbuen som andre instans: lys, draape, dispersjon, observator."""
    ids = {n["id"] for n in _instance()["nodes"]}
    assert {"lys.sol", "h2o.droplet", "optikk.dispersjon",
            "regnbue", "regnbue.observator"} <= ids


def test_rainbow_emerges_from_droplets_and_light():
    """Regnbuen er en EMERGENCE av draaper + lys — ikke en node ved siden av."""
    rels = _instance()["relations"]
    preds = {(r["subject"], r["predicate"], r["object"]) for r in rels}
    assert ("regnbue", "EMERGES_FROM", "h2o.droplet") in preds
    assert ("regnbue", "EMERGES_FROM", "lys.sol") in preds


def test_rainbow_is_observed_through_observer():
    """Uten observator i anti-solar geometri er det bare spredt lys —
    regnbuen OBSERVED_THROUGH observatoren."""
    rels = _instance()["relations"]
    preds = {(r["subject"], r["predicate"], r["object"]) for r in rels}
    assert ("regnbue", "OBSERVED_THROUGH", "regnbue.observator") in preds


def test_observer_bandwidth_states_visible_window():
    """«Alt er paa et elektrospektrum totalt, observatoeren ser noen faa nm»
    — oeyets vindu (400-700 nm) skal staa i observatorens baandbredde."""
    inst = _instance()
    obs = next(n for n in inst["nodes"] if n["id"] == "regnbue.observator")
    bw = obs["observer"]["bandwidth"]
    assert "400" in bw and "700" in bw


def test_rainbow_is_emergent_pattern_not_phase():
    """Regnbuen er ingen termodynamisk fase — den er et emergert monster.
    Skjemaet maa kunne baere emergences utover faser."""
    inst = _instance()
    rb = next(n for n in inst["nodes"] if n["id"] == "regnbue")
    assert rb["phase"] == "emergent_pattern"


def test_rainbow_requires_liquid_droplets():
    """Regnbuen krever FLYTENDE (sfaeriske) draaper — iskrystaller gir
    haloer, ikke regnbue. Gyldighetsomraadet maa si det."""
    inst = _instance()
    rb = next(n for n in inst["nodes"] if n["id"] == "regnbue")
    assert "requires liquid (spherical) droplets" in rb["regime"]["validity"].lower()


def test_existing_h2o_nodes_untouched():
    """H2O-nodene fra trinn 2 skal vaere urorte i samme atlas."""
    ids = {n["id"] for n in _instance()["nodes"]}
    assert {"h2o.solid", "h2o.liquid", "h2o.gas",
            "h2o.supercritical", "h2o.triple_point"} <= ids


# --------------------------------------------------------------------------
# Trinn 5: L0–L3-kosmologien — EFCs kjerne inn i samme struktur
# --------------------------------------------------------------------------

def test_l0_l3_nodes_exist():
    """EFCs fire regimer skal staa som noder i atlaset."""
    ids = {n["id"] for n in _instance()["nodes"]}
    assert {"efc.l0", "efc.l1", "efc.l2", "efc.l3"} <= ids


def test_l0_l3_transition_chain():
    """Regimene danner kjeden L0→L1→L2→L3 via TRANSITIONS_TO."""
    rels = _instance()["relations"]
    preds = {(r["subject"], r["predicate"], r["object"]) for r in rels}
    assert ("efc.l0", "TRANSITIONS_TO", "efc.l1") in preds
    assert ("efc.l1", "TRANSITIONS_TO", "efc.l2") in preds
    assert ("efc.l2", "TRANSITIONS_TO", "efc.l3") in preds


def test_l1_l2_is_declared_regime_transition():
    """L1→L2 er EFCs regimeovergang — trippelpunkt-analogien. Den skal
    vaere deklarert i overgangsrelasjonens note (ikke bare en kant)."""
    rels = _instance()["relations"]
    overgang = next(
        (r for r in rels
         if (r["subject"], r["predicate"]) == ("efc.l1", "TRANSITIONS_TO")
         and r["object"] == "efc.l2"),
        None)
    assert overgang is not None
    assert "regime transition" in overgang["note"].lower()


def test_regimes_declare_s_values():
    """Hvert regime skal deklarere sin S-verdi i validity (S→0, S≈0,
    S>0, S→1) — S er regimekoordinaten, ikke dekor."""
    inst = _instance()
    noder = {n["id"]: n for n in inst["nodes"]}
    assert "S" in noder["efc.l0"]["regime"]["validity"]
    assert "S" in noder["efc.l1"]["regime"]["validity"]
    assert "S" in noder["efc.l2"]["regime"]["validity"]
    assert "S" in noder["efc.l3"]["regime"]["validity"]


def test_observer_is_inside_l2():
    """Observatoren er INNE i systemet: vi observerer FRA L2 og ser
    bakover i tid til L1 (CMB) — observatorens plassering er en del av
    strukturen, ikke en noeytral utsiktspost."""
    inst = _instance()
    obs = next(n for n in inst["nodes"] if n["id"] == "efc.l2")
    # L2-noden skal selv deklarere observatorens posisjon.
    assert "observer" in obs["observer"]["bandwidth"].lower() or \
        "observer" in obs["episenter"].lower()


# --------------------------------------------------------------------------
# Trinn 6: Victron/batteri — bufferens elektriske form
# --------------------------------------------------------------------------

def test_battery_nodes_exist():
    """Batteridomenet skal staa som noder: celle, lading, buffer,
    inverter — kjemisk regime, overgang, lagring, konvertering."""
    ids = {n["id"] for n in _instance()["nodes"]}
    assert {"batteri.celle", "batteri.lading",
            "batteri.buffer", "batteri.inverter"} <= ids


def test_cc_cv_transition_declared():
    """CC -> CV-kneet er laderegimets faseovergang — trippelpunkt-
    analogien i elektrisk form. Overgangen skal vaere deklarert i
    relasjonen mellom celle og lading."""
    rels = _instance()["relations"]
    overgang = next(
        (r for r in rels
         if (r["subject"], r["predicate"], r["object"])
         == ("batteri.celle", "TRANSITIONS_TO", "batteri.lading")),
        None)
    assert overgang is not None
    note = overgang["note"].upper()
    assert "CC" in note and "CV" in note


def test_soc_is_regime_coordinate():
    """SOC er batteriets regimekoordinat — flat midt, bratt i endene.
    Cellenoden skal deklarere dette i validity."""
    inst = _instance()
    celle = next(n for n in inst["nodes"] if n["id"] == "batteri.celle")
    assert "SOC" in celle["regime"]["validity"]


def test_buffer_is_broad_electric():
    """Bufferen er Mortens brede buffer i elektrisk form: homeostase,
    lagring, demping — ikke bare en lagerboks."""
    inst = _instance()
    buffer_node = next(n for n in inst["nodes"] if n["id"] == "batteri.buffer")
    rolle = buffer_node["buffer"]["role"].lower()
    assert "homeost" in rolle or "lagr" in rolle or "energi" in rolle


def test_inverter_is_regime_converter():
    """Inverteren er regimekonverteren: DC <-> AC — transformasjonsnoden
    der to regimer motes."""
    inst = _instance()
    inv = next(n for n in inst["nodes"] if n["id"] == "batteri.inverter")
    assert ("DC" in inv["emergence"]["loop"].upper()
            or "DC" in inv["regime"]["validity"].upper())


def test_proxy_chain_v_a_w_to_soc():
    """Victron-instrumentene maaler V/A/W og avleder SOC/SOH — proxy-
    kjeden skal vaere deklarert i cellenodens maaling."""
    inst = _instance()
    celle = next(n for n in inst["nodes"] if n["id"] == "batteri.celle")
    kjede = " ".join(celle["measure"]["proxy_chain"]).upper()
    assert "V" in kjede and "SOC" in kjede


def test_soc_proxy_is_qualified():
    """SOC er et ESTIMAT, ikke en direkte maaling: proxychain skal skille
    coulomb-telling (estimert) fra OCV (kun etter hvile) — ellers
    forveksler vi ladespenning med hvilespenning."""
    inst = _instance()
    celle = next(n for n in inst["nodes"] if n["id"] == "batteri.celle")
    kjede = " ".join(celle["measure"]["proxy_chain"]).upper()
    assert "COULOMB" in kjede and "AFTER REST" in kjede
    assert "ESTIMAT" in kjede or "ESTIMATOR" in kjede


def test_pack_vs_cell_declared():
    """Målingene er PAKKESpenning; cellenivaaet er BMS-intern proxy.
    Skillet skal vaere deklarert i cellenodens validity."""
    inst = _instance()
    celle = next(n for n in inst["nodes"] if n["id"] == "batteri.celle")
    validity = celle["regime"]["validity"].upper()
    assert "PACK" in validity and "BMS" in validity


def test_inverter_is_bidirectional():
    """Inverteren er en TOVEIS konverterer: DC->AC (invertermodus) og
    AC->DC (lademodus) — ikke bare den ene retningen."""
    inst = _instance()
    inv = next(n for n in inst["nodes"] if n["id"] == "batteri.inverter")
    tekst = (inv["regime"]["law_form"] + " " + inv["emergence"]["loop"]).upper()
    assert "DC -> AC" in tekst.replace("DC->AC", "DC -> AC").replace(
        "AC->DC", "AC -> DC") or ("DC->AC" in tekst and "AC->DC" in tekst)
    assert ("CHARGE MODE" in tekst or "CHARGING" in tekst)


def test_no_private_site_info_in_public_instance():
    """Den offentlige instansen skal IKKE baere privat site-info: adresse,
    site-ID eller intern filsti. Full proveniens ligger i et privat
    artifact — regresjonsvern mot aa gjeninnfoere den her."""
    raw = INSTANCE_PATH.read_text(encoding="utf-8")
    for forbudt in [HJEM, "380961", "/opt/hermes-opus", "idSite",
                    "maalt 2026-09-16T13:41:57Z", "intern MCP-bro",
                    "feltkoder"]:
        assert forbudt not in raw, f"privat info lekker: {forbudt}"


# --------------------------------------------------------------------------
# Trinn 7: BAO + kobling av kosmologiske observasjoner til regime-nodene
# --------------------------------------------------------------------------

# De kosmologiske OBSERVASJONENE i docs/validation-ledger/data/atlas.json
# (instrumentbaarne maalinger, ikke modellparametriseringer). Verdien er
# LISTEN av regime-noder observasjonen er koblet til — bro-observasjoner
# (bao, isw, h0_tension) bærer to regimer. Atlasets L-labels er en ANNEN
# akse (lag-akse) enn fasekjeden efc.l0-l3; hver node deklarerer begge.
KOSMOLOGISKE_OBSERVASJONER = {
    "obs.bao": ["efc.l1", "efc.l2"],   # r_d frosset i L1, maalt i L2
    "obs.cmb_tt": ["efc.l1"],
    "obs.cmb_lensing": ["efc.l2"],     # linser L2-struktur
    "obs.bbn": ["efc.l1"],             # fasekjedens tidligste avlesning
    "obs.fsigma8": ["efc.l2"],
    "obs.s8": ["efc.l2"],
    "obs.eg": ["efc.l2"],
    "obs.isw": ["efc.l1", "efc.l2"],   # kryssregime
    "obs.ksz": ["efc.l2"],
    "obs.cluster_mass": ["efc.l2"],
    "obs.cluster_hmf": ["efc.l2"],
    "obs.rar": ["efc.l2"],
    "obs.bullet": ["efc.l2"],
    "obs.satellites": ["efc.l2"],
    "obs.jwst_ems": ["efc.l2"],
    "obs.gw_ct": ["efc.l2"],
    "obs.pta_gwb": ["efc.l2"],
    "obs.h0_tension": ["efc.l1", "efc.l2"],  # spenningen MELLOM regimene
    "obs.w0wa": ["efc.l3"],
    "obs.cc": ["efc.l3"],
}


def test_cosmological_observation_nodes_exist():
    """Hver kosmologisk observasjon i atlaset skal staa som node."""
    ids = {n["id"] for n in _instance()["nodes"]}
    for obs_id in KOSMOLOGISKE_OBSERVASJONER:
        assert obs_id in ids, f"mangler node: {obs_id}"


def test_observations_are_coupled_to_regimes():
    """Hver observasjon skal vaere koblet til sine regime(r) med
    OBSERVED_IN — ikke bare ligge loest i atlaset."""
    rels = _instance()["relations"]
    koblede = {(r["subject"], r["object"])
               for r in rels if r["predicate"] == "OBSERVED_IN"}
    for obs_id, regimer in KOSMOLOGISKE_OBSERVASJONER.items():
        for regime in regimer:
            assert (obs_id, regime) in koblede, \
                f"mangler OBSERVED_IN-kobling: {obs_id} -> {regime}"


def test_bao_is_standard_ruler():
    """BAO-noden skal deklarere lydhorisonten r_d som standardlinjal —
    den eneste kjente fysiske lengden i kosmologien."""
    inst = _instance()
    bao = next(n for n in inst["nodes"] if n["id"] == "obs.bao")
    tekst = (bao["regime"]["validity"] + " " + bao["episenter"]).upper()
    assert "R_D" in tekst or "STANDARDLINJAL" in tekst or \
        "STANDARD RULER" in tekst or "LYDHORISONT" in tekst


def test_bao_declares_lag_axis_vs_phase_chain():
    """BAO-noden skal deklarere at atlasets L-akse er en ANNEN inndeling
    enn regime-nodenes fasekjede — aksene blandes ikke."""
    inst = _instance()
    bao = next(n for n in inst["nodes"] if n["id"] == "obs.bao")
    kilde = bao["ontology"]["source"].lower()
    assert "different axis" in kilde and "phase chain" in kilde


def test_observation_nodes_sourced_from_atlas():
    """Hver observasjonsnode skal peke til atlas.json som kilde —
    koblingen er maskinelt forankret, ikke ad hoc."""
    inst = _instance()
    noder = {n["id"]: n for n in inst["nodes"]}
    for obs_id in KOSMOLOGISKE_OBSERVASJONER:
        kilde = noder[obs_id]["ontology"]["source"].lower()
        assert "atlas.json" in kilde or "validation-ledger" in kilde, \
            f"{obs_id}: kilde peker ikke til atlaset"


# Forbudte strenger for vernet under, bygd av de samme delene som over.
FORBUDTE_ADRESSER = (HJEM, POSTSTED, HJEM + " 5")


def test_ingen_privat_info_i_hele_repoet():
    """Regresjonsvern (utvidet 2026-09-17): hjemmeadressen skal ikke finnes i
    NOEN sporet fil — vakten dekket bare schema-mappen, og efc-toolkit lakk
    adresse + telefon i 13 filer.

    Leser git-treet, ikke disken (`_repo_tre`). En `rglob` over arbeidsstreet
    fant `.worktrees/` i hovedklonen — gitignorert, men på disk — og felt
    testen på filer som ikke er i repoet.
    """
    for sti in _tre_filer(_REPO):
        if sti.suffix.lower() in (".csv", ".png", ".pdf", ".jpg", ".pyc"):
            continue  # vitenskapelige data / kompilert cache
        try:
            raw = sti.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for forbudt in FORBUDTE_ADRESSER:
            if forbudt in raw:
                raise AssertionError(
                    f"privat adresse lekker: {sti.relative_to(_REPO).as_posix()}")


def test_ingen_tomme_redaksjons_felt_i_toolkit():
    """Review-krav PR #455 r2: redaksjonen må ikke etterlate
    «felt»: , — feltet skal fjernes, ikke tømmes."""
    for sti in Path("docs/papers/efc").rglob("*"):
        if not sti.is_file() or sti.suffix not in (".json", ".jsonld"):
            continue
        raw = sti.read_text(encoding="utf-8", errors="ignore")
        if re.search(r'"[^"]+"\s*:\s*,', raw):
            raise AssertionError(f"tomt felt etter redaksjon: {sti}")
