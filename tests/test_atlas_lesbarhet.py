"""The atlas's readability: what the user meets must answer what it looks like.

Measured 2026-09-18 (origin/main f4a3e4f2) there were four deviations in the
RENDERED atlas — all in the generator, none in the bank:

1. All 116 one-liners opened with the same template, «Perspective: …». The
   hover text said who holds the view, not what the thing IS, and the substance
   was cut at the back.
2. The texts were cut with `[:70]`/`[:90]`/`[:80]` mid-word — «fase
   identifisert via P_sat(T) o», «rotation engin», «holder temperaturen under
   oppvarming . Epistemic». A cut without a mark looks like the whole text.
3. The question tab got one generated line per node without evidence, identical
   for all seven: «no evidence yet — hypothesis marked honestly». It asked about
   nothing; it repeated `how`. It is the fallback that answers.
4. The S-axis (regime, sektor, klarhet, EBE, RCMP) was written to data.mjs, but
   neither of the two builds reads the key — the layer that was meant to make
   the atlas researchable was invisible.

The tests below are not a repetition of the implementation: they require
EQUALITY where the old ones required a substring, they probe the edge cases
(empty field, long single token), and they read the BUILT files — not only
data.mjs.
"""
from __future__ import annotations

import functools
import importlib.util
import json
import pathlib
import subprocess
import sys

# The interpreter. The generator runs as a subprocess, so it must be the
# one RUNNING this test. Measured 2026-09-18: these calls hardcoded a venv
# path that exists only on the Hermes host — in CI (ubuntu-latest) they
# died with FileNotFoundError.
PYTHON = sys.executable

ROT = pathlib.Path(__file__).resolve().parents[1]
GEN = ROT / "scripts" / "maintenance" / "efc_atlas_generator.py"
ATLAS = ROT / "docs" / "efc-atlas"
DATA = ATLAS / "atlas" / "data.mjs"
BANK = ROT / "schema" / "regime_nodes.jsonld"


def _generator():
    spec = importlib.util.spec_from_file_location("efc_atlas_generator", GEN)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN_MOD = _generator()
G = GEN_MOD.GRENSER


def _les_konstant(navn: str):
    s = DATA.read_text(encoding="utf-8")
    i = s.index(f"export const {navn} = ")
    j = s.index("\nexport const", i + 10)
    return json.loads(s[i:j][s[i:j].index("=") + 1:].strip().rstrip(";"))


@functools.lru_cache(maxsize=1)
def _bygg_og_les():
    """Build the atlas from the bank, and read the RENDERED node list."""
    r = subprocess.run(
        [PYTHON, str(GEN)],
        capture_output=True, text=True, cwd=ROT, timeout=180)
    assert r.returncode == 0, r.stderr[-600:]
    return _les_konstant("NODES"), DATA.read_text(encoding="utf-8")


@functools.lru_cache(maxsize=1)
def _bank():
    return {n["id"]: n for n in
            json.loads(BANK.read_text(encoding="utf-8"))["nodes"]}


def _perspektiv(b):
    return GEN_MOD._perspektiv_tekst(b.get("perspektiv"))


# --- 1. the one-liner says what the thing is ------------------------------

def test_ingen_oneliner_aapner_med_perspektivmalen():
    noder, _ = _bygg_og_les()
    darlige = [n["id"] for n in noder
               if n["one"].lower().startswith(("perspective", "perspektiv"))]
    assert not darlige, f"the one-liner opens with the template: {darlige[:8]}"


def test_onelineren_leder_med_substansen():
    """The key requirement: `one` must BEGIN with the target's target, not with
    a template.

    A weaker requirement («target exists somewhere in the string») lets through
    a one-liner that still leads with something else.
    """
    noder, _ = _bygg_og_les()
    bank = _bank()
    feil = []
    for n in noder:
        b = bank[n["name"]]
        target = GEN_MOD.klipp((b.get("measure") or {}).get("target", ""),
                               G["one"])
        if not target:
            continue          # no substance in the bank -> perspective alone
        if not n["one"].startswith(target):
            feil.append((n["id"], n["one"][:70]))
    assert not feil, feil[:6]


def test_onelinerne_deler_ikke_ett_prefiks():
    """A template is not content, even when it is not called «Perspective»."""
    noder, _ = _bygg_og_les()
    prefiks = [n["one"][:20] for n in noder]
    vanligst = max(set(prefiks), key=prefiks.count)
    assert prefiks.count(vanligst) <= len(noder) * 0.2, (
        f"{prefiks.count(vanligst)} of {len(noder)} one-liners share "
        f"the prefix {vanligst!r}")


def test_perspektivet_er_ikke_borte_fra_noden():
    noder, _ = _bygg_og_les()
    bank = _bank()
    for n in noder:
        forventet = _perspektiv(bank[n["name"]])
        assert n["one"].endswith(f"· perspective: {forventet}"), n["id"]
        assert ["Perspective", forventet] in n["steps"], n["id"]


# --- 2. a cut must be marked, and on a word boundary ----------------------

def test_klipp_kutter_paa_ordgrense_og_merker():
    k = GEN_MOD.klipp
    assert k("kort", 10) == "kort"
    assert k("  to   ord  ", 20) == "to ord"
    ut = k("ord " * 40, 20)
    assert ut.endswith("…") and len(ut) <= 22 and "  " not in ut, repr(ut)


def test_klipp_med_ett_langt_ord():
    """The edge case the reviewer found: the first word is longer than the limit.

    Then there is no word boundary to cut on. The ONE allowed mid-word cut is
    fine — but it must be MARKED, not silent.
    """
    langt = "a" * 40
    ut = GEN_MOD.klipp(langt, 10)
    assert ut.endswith("…"), repr(ut)
    assert len(ut) == 11, repr(ut)
    ut2 = GEN_MOD.klipp(langt + " and more text", 10)
    assert ut2.endswith("…"), repr(ut2)
    tekst, kuttet = GEN_MOD.klipp_med_status(langt, 10)
    assert kuttet is True
    tekst2, kuttet2 = GEN_MOD.klipp_med_status("kort", 10)
    assert (tekst2, kuttet2) == ("kort", False)


def test_klipp_med_status_avslorer_banktekst_som_selv_ender_med_ellipsis():
    """The point of the status: a «…» in the RESULT does not say that WE cut."""
    tekst, kuttet = GEN_MOD.klipp_med_status("banken skrev …", 100)
    assert tekst == "banken skrev …" and kuttet is False
    tekst2, kuttet2 = GEN_MOD.klipp_med_status("banken skrev ...", 100)
    assert kuttet2 is False and tekst2.endswith("...")


def test_alle_renderte_tekster_er_noeyaktig_klipp_av_kilden():
    """EQUALITY, not substring — and all the composite fields with it.

    The substring requirement (which the first version used) can pass when
    production and test share the same bug. Here the whole expected string is
    built up.
    """
    noder, _ = _bygg_og_les()
    bank = _bank()
    for n in noder:
        b = bank[n["name"]]
        maal = b.get("measure") or {}
        buf = b.get("buffer") or {}
        ep = b.get("epistemikk") or {}

        navn = n["name"].split(".")[-1].replace("_", " ")
        assert n["short"] == GEN_MOD.klipp(navn, G["short"]), n["id"]

        target = GEN_MOD.klipp(maal.get("target", ""), G["one"])
        assert n["one"] == (f"{target} · perspective: {_perspektiv(b)}"
                            if target else
                            f"perspective: {_perspektiv(b)}"), n["id"]

        assert n["what"] == (
            f"{GEN_MOD.klipp(maal.get('instrument', ''), G['what'])} — "
            f"proxy chain: "
            f"{GEN_MOD.klipp(' -> '.join(maal.get('proxy_chain', [''])), G['what'])}"
        ), n["id"]

        rolle, kuttet = GEN_MOD.klipp_med_status(
            buf.get("role") or "—", G["how"])
        sakse = GEN_MOD.sakse_tekst(b)
        # The verification chain is part of `how` for the nodes that have taken
        # a position (card t_bf62ce48): the field must sit in a place both
        # builds ACTUALLY read, or it exists only in the diff. The expectation
        # calls the generator's own function rather than copying its expression.
        vkt = GEN_MOD.verifisering_tekst(b)
        assert n["how"] == (
            f"Buffer role: {rolle}{'' if kuttet else '.'} "
            f"Epistemic: {ep.get('sannhetsstatus', '—')} / "
            f"{ep.get('evidensstatus', '—')} / "
            f"{ep.get('konsensusstatus', '—')}."
            + (f" S-axis: {sakse}"
               f"{'' if sakse.endswith(('.', '…')) else '.'}" if sakse else "")
            + (f" Verification: {vkt}"
               f"{'' if vkt.endswith(('.', '…')) else '.'}" if vkt else "")
        ), n["id"]

        assert n["steps"][2][1] == GEN_MOD.klipp(
            ep.get("sosial_mekanisme", "—"), G["sosial"]), n["id"]


def test_ingen_renderte_tekster_baerer_kutteartefakter():
    noder, _ = _bygg_og_les()
    feil = []
    for n in noder:
        for felt in ("short", "one", "what", "how"):
            t = n[felt]
            if (" ." in t or "  " in t or t != t.strip()
                    or "…." in t or ".." in t):
                feil.append((n["id"], felt, repr(t[-40:])))
    assert not feil, feil[:6]


def test_tomme_felter_blir_ikke_til_tom_tekst():
    """`role: None` and `role: ""` gave «Buffer role: . Epistemic: …»."""
    rad = GEN_MOD._node_rad(
        {"id": "h2o.solid", "buffer": {"role": None},
         "epistemikk": {}, "measure": {}}, 0)
    assert "Buffer role: ." not in rad["how"], rad["how"]
    assert "Buffer role: —" in rad["how"], rad["how"]
    rad2 = GEN_MOD._node_rad(
        {"id": "h2o.solid", "buffer": {"role": ""},
         "epistemikk": {}, "measure": {}}, 0)
    assert "Buffer role: —" in rad2["how"], rad2["how"]
    rad3 = GEN_MOD._node_rad({"id": "h2o.solid"}, 0)
    assert rad3["one"] == "perspective: agnostic", rad3["one"]


# --- 3. the questions are not generated -----------------------------------

def test_den_genererte_spoersmaalsteksten_kommer_aldri_tilbake():
    """The measured fallback line must not be able to reappear in any form.

    The first version of this test said «a node with evidensstatus=ingen gets no
    cond». That was right as long as cond could ONLY come from the generated
    line — but wrong the moment the bank got a real question field: a node can
    lack evidence AND have a real, open question from the bank at the same time.
    The requirement is not «no questions», it is «no questions written by the
    generator». Therefore the concrete text is measured, and the provenance is
    measured in the test above.
    """
    noder, _ = _bygg_og_les()
    forbudt = ("no evidence yet", "hypothesis marked honestly")
    feil = [(n["id"], c) for n in noder for c in (n["cond"] or [])
            if any(f in (c["q"] if isinstance(c, dict) else c) for f in forbudt)]
    assert not feil, feil[:6]


def test_hvert_spoersmaal_kommer_fra_banken():
    """A question must be traceable to the bank — not merely be missing.

    Two legal sources: `open_questions` on the node, or `stipulasjoner.motor`
    that begins with KANDIDAT (the bridge waits for the connector deploy). If a
    question appears in the atlas without one of them, it is the generator's own.
    """
    noder, _ = _bygg_og_les()
    bank = _bank()
    for n in noder:
        if not n["cond"]:
            continue
        b = bank[n["name"]]
        motor = (b.get("stipulasjoner") or {}).get("motor", "")
        assert b.get("open_questions") or str(motor).startswith("KANDIDAT"), (
            f"{n['id']} carries a question ({n['cond']}) without "
            f"open_questions in the bank and without a KANDIDAT engine "
            f"(motor={motor!r})")


def test_bankfoedte_spoersmaal_naar_atlaset():
    """The field `open_questions` must actually be read — otherwise it is an
    empty promise.

    Both the text form and the {q, r, to} form, and unknown keys must not leak
    through to the built question list.
    """
    rad = GEN_MOD._node_rad(
        {"id": "h2o.solid", "open_questions": [
            "is there a measurement we have not made?",
            {"q": "holder testen?", "to": "connector deploy", "tull": "nei"},
            {"q": "   "},
            ""]}, 0)
    assert rad["cond"] == [
        "is there a measurement we have not made?",
        {"q": "holder testen?", "to": "connector deploy"}], rad["cond"]


def test_spoersmaalene_er_unike():
    noder, _ = _bygg_og_les()
    sett = [c["q"] if isinstance(c, dict) else c
            for n in noder for c in (n["cond"] or [])]
    assert len(sett) == len(set(sett)), f"duplicate questions: {sett}"


def test_kapittel9_sier_hva_atlaset_bestaar_av():
    """«All at once» must not look fuller than it is.

    Measured: 116 published nodes, 53 of them designed and not built. If the
    number stood only in prose, it would stay there and lie. Here both sides are
    derived and compared: the text in chapter 9 against the actual count in
    data.mjs.
    """
    noder, _ = _bygg_og_les()
    ch = _les_konstant("CH")
    siste = ch[-1]
    bank = _bank()
    ikke_bygget = sum(1 for n in noder
                      if GEN_MOD._gruppe(bank[n["name"]]["id"]) == "ghost")
    uten_evidens = sum(1 for n in noder
                       if (bank[n["name"]].get("epistemikk") or {})
                       .get("evidensstatus") == "ingen")
    assert ikke_bygget > 0 and uten_evidens > 0, "the counts are dead"
    grunn = GEN_MOD.uten_gruppe_grunner(list(bank.values()))
    assert (f"{ikke_bygget} of them without a group yet "
            f"({grunn['observation']} observations") in siste["lede"], (
        f"chapter 9 does not say how many lack a group, and why: "
        f"{siste['lede']}")
    assert f"{uten_evidens} nodes carry no evidence yet" in siste["story"], (
        f"chapter 9 does not say how many lack evidence: {siste['story']}")
    assert len(noder) and f"{len(noder)} nodes" in siste["lede"]


# --- 4. the S-axis reaches BOTH builds -------------------------------------

def test_saksen_staar_i_how_naar_den_er_maalt():
    noder, _ = _bygg_og_les()
    bank = _bank()
    maalt = [n for n in noder if GEN_MOD.sakse_tekst(bank[n["name"]])]
    assert maalt, "no nodes with an S-axis in the excerpt — the measurement is dead"
    mangler = [n["id"] for n in maalt
               if f"S-axis: {GEN_MOD.sakse_tekst(bank[n['name']])}" not in n["how"]]
    assert not mangler, f"the S-axis does not reach `how` for: {mangler[:8]}"


def test_saksen_er_ikke_en_gjentatt_mal():
    """If the S-axis is measured, the text must be the node's own — not one shared line."""
    noder, _ = _bygg_og_les()
    tekster = [n["how"].split("S-axis: ", 1)[1] for n in noder
               if "S-axis: " in n["how"]]
    assert tekster, "no S-axis texts"
    assert len(set(tekster)) > 1, "the S-axis is identical on all nodes"


def test_saksen_naar_teksttvillingen_og_headeren():
    """data.mjs is not enough: both builds read `how`, and the header reads META.

    The renderer is a READ-ONLY copy of the skill's assets — therefore the BUILT
    files are tested, not only that the key exists in data.mjs.
    """
    noder, data = _bygg_og_les()
    bank = _bank()
    eksempel = next(n for n in noder
                    if GEN_MOD.sakse_tekst(bank[n["name"]]))
    tekst = GEN_MOD.sakse_tekst(bank[eksempel["name"]])

    system_md = (ATLAS / "SYSTEM.md").read_text(encoding="utf-8")
    assert tekst in system_md, "the S-axis does not reach SYSTEM.md"

    atlas_html = (ATLAS / "atlas.html").read_text(encoding="utf-8")
    assert '"k":"S-axis"' in atlas_html, (
        "the S-axis is missing from the atlas's stats header (META.stats -> STATS)")

    maalt = len([n for n in noder if GEN_MOD.sakse_tekst(bank[n["name"]])])
    assert f"{maalt} of {len(noder)} measured" in atlas_html, (
        "the header does not show how much of the S-axis is measured")
    assert f"{maalt} of {len(noder)} measured" in data, (
        "the number is not in data.mjs")


def test_verifiseringskjeden_naar_teksttvillingen_og_headeren():
    """The chain must reach the BUILT surfaces, not only data.mjs (t_bf62ce48).

    The whole point of the layer is that a reader can SEE that a fit result is
    not a verified posterior. A key that exists only in data.mjs is shown
    nowhere — which is exactly how the S-axis was invisible — so the built text
    twin and the header are the thing tested.
    """
    noder, data = _bygg_og_les()
    bank = _bank()
    funnet = [n for n in noder if GEN_MOD.verifisering_tekst(bank[n["name"]])]
    assert funnet, "no node with a chain position in the built atlas"
    eksempel = funnet[0]
    tekst = GEN_MOD.verifisering_tekst(bank[eksempel["name"]])

    system_md = (ATLAS / "SYSTEM.md").read_text(encoding="utf-8")
    assert tekst in system_md, (
        "the chain position does not reach SYSTEM.md (the text twin)")

    atlas_html = (ATLAS / "atlas.html").read_text(encoding="utf-8")
    assert '"k":"Verification"' in atlas_html, (
        "the chain is missing from the atlas's stats header (META.stats -> STATS)")

    maalt = len([n for n in noder
                 if GEN_MOD.verifisering_tekst(bank[n["name"]])])
    assert f"{maalt} of {len(noder)} carry a chain position" in atlas_html, (
        "the header does not show how much of the chain is measured")
    assert f"{maalt} of {len(noder)} carry a chain position" in data, (
        "the number is not in data.mjs")


# --- 5. one word, one number -----------------------------------------------

def test_motorordet_betyr_bare_en_ting_paa_hver_flate():
    """«motorer» stood for 32 (engine files) in one place and 19 (engine nodes)
    in another.

    Two different measurements with the same name are not a naming conflict one
    can live with: whoever reads 32 and 19 believes one of the numbers lies.
    Outward they are now called MOTORFILER and ENGINE NODES.
    """
    import subprocess as sp
    r = sp.run([PYTHON,
                str(ROT / "scripts" / "atlas_navigasjon.py"), ".", "--ref",
                "origin/main"], capture_output=True, text=True, cwd=ROT,
               timeout=120)
    assert r.returncode == 0, r.stderr[-300:]
    assert "engine files" in r.stdout, (
        f"the navigator still calls them engines:\n{r.stdout[:200]}")
    assert " motorer · " not in r.stdout, "the ambiguous word still stands"

    system_md = (ATLAS / "SYSTEM.md").read_text(encoding="utf-8")
    noder, _ = _bygg_og_les()
    motorer = sum(1 for n in noder if "_engine" in n["name"])
    assert f"{len(noder)} nodes, {motorer} engine nodes" in system_md, (
        "the text twin does not tell engine file from engine node")
