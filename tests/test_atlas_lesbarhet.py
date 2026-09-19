"""Atlasets lesbarhet: det brukeren moeter skal svare paa det det ser ut som.

Maalt 2026-09-18 (origin/main f4a3e4f2) var fire avvik i det RENDERte atlaset —
alle i generatoren, ingen i banken:

1. Alle 116 one-linere aapnet med samme mal, «Perspective: …». Hover-teksten
   sa hvem som mener det, ikke hva tingen ER, og substansen ble kuttet bakerst.
2. Tekstene ble kuttet med `[:70]`/`[:90]`/`[:80]` midt i ord — «fase
   identifisert via P_sat(T) o», «rotation engin», «holder temperaturen under
   oppvarming . Epistemic». Et kutt uten merke ser ut som hele teksten.
3. Spoersmaalsfanen fikk en generert linje per node uten evidens, identisk for
   alle sju: «no evidence yet — hypothesis marked honestly». Den spurte ikke om
   noe; den gjentok `how`. Det er fallbacken som svarer.
4. S-aksen (regime, sektor, klarhet, EBE, RCMP) ble skrevet til data.mjs, men
   ingen av de to byggene leser noekkelen — det laget som skal gjoere atlaset
   forskbart var usynlig.

Testene under er ikke en gjentakelse av implementasjonen: de krever LIKHET der
de gamle krevde delstreng, de proever kanttilfellene (tomt felt, langt enkelt-
token), og de leser de BYGGEDE filene — ikke bare data.mjs.
"""
from __future__ import annotations

import functools
import importlib.util
import json
import pathlib
import subprocess

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
    """Bygg atlaset fra banken, og les den RENDERte nodelista."""
    r = subprocess.run(
        ["/opt/venvs/t_123ed6d9/bin/python", str(GEN)],
        capture_output=True, text=True, cwd=ROT, timeout=180)
    assert r.returncode == 0, r.stderr[-600:]
    return _les_konstant("NODES"), DATA.read_text(encoding="utf-8")


@functools.lru_cache(maxsize=1)
def _bank():
    return {n["id"]: n for n in
            json.loads(BANK.read_text(encoding="utf-8"))["nodes"]}


def _perspektiv(b):
    return GEN_MOD._perspektiv_tekst(b.get("perspektiv"))


# --- 1. one-lineren sier hva tingen er ------------------------------------

def test_ingen_oneliner_aapner_med_perspektivmalen():
    noder, _ = _bygg_og_les()
    darlige = [n["id"] for n in noder
               if n["one"].lower().startswith(("perspective", "perspektiv"))]
    assert not darlige, f"one-lineren aapner med malen: {darlige[:8]}"


def test_onelineren_leder_med_substansen():
    """Nøkkelkravet: `one` skal BEGYNNE med maalets target, ikke med en mal.

    Svakere krav («target finnes et sted i strengen») slipper gjennom en
    one-liner som fortsatt leder med noe annet.
    """
    noder, _ = _bygg_og_les()
    bank = _bank()
    feil = []
    for n in noder:
        b = bank[n["name"]]
        target = GEN_MOD.klipp((b.get("measure") or {}).get("target", ""),
                               G["one"])
        if not target:
            continue          # ingen substans i banken -> perspektiv alene
        if not n["one"].startswith(target):
            feil.append((n["id"], n["one"][:70]))
    assert not feil, feil[:6]


def test_onelinerne_deler_ikke_ett_prefiks():
    """En mal er ikke innhold, selv naar den ikke heter «Perspective»."""
    noder, _ = _bygg_og_les()
    prefiks = [n["one"][:20] for n in noder]
    vanligst = max(set(prefiks), key=prefiks.count)
    assert prefiks.count(vanligst) <= len(noder) * 0.2, (
        f"{prefiks.count(vanligst)} av {len(noder)} one-linere deler "
        f"prefikset {vanligst!r}")


def test_perspektivet_er_ikke_borte_fra_noden():
    noder, _ = _bygg_og_les()
    bank = _bank()
    for n in noder:
        forventet = _perspektiv(bank[n["name"]])
        assert n["one"].endswith(f"· perspektiv: {forventet}"), n["id"]
        assert ["Perspective", forventet] in n["steps"], n["id"]


# --- 2. et kutt skal vaere merket, og paa ordgrense -----------------------

def test_klipp_kutter_paa_ordgrense_og_merker():
    k = GEN_MOD.klipp
    assert k("kort", 10) == "kort"
    assert k("  to   ord  ", 20) == "to ord"
    ut = k("ord " * 40, 20)
    assert ut.endswith("…") and len(ut) <= 22 and "  " not in ut, repr(ut)


def test_klipp_med_ett_langt_ord():
    """Kanttilfellet reviewer fant: foerste ord er lengre enn grensen.

    Da finnes det ingen ordgrense aa kutte paa. Den ENE tillatte midt-i-ord-
    kuttingen er greit — men den skal vaere MERKET, ikke stille.
    """
    langt = "a" * 40
    ut = GEN_MOD.klipp(langt, 10)
    assert ut.endswith("…"), repr(ut)
    assert len(ut) == 11, repr(ut)
    ut2 = GEN_MOD.klipp(langt + " og mer tekst", 10)
    assert ut2.endswith("…"), repr(ut2)
    tekst, kuttet = GEN_MOD.klipp_med_status(langt, 10)
    assert kuttet is True
    tekst2, kuttet2 = GEN_MOD.klipp_med_status("kort", 10)
    assert (tekst2, kuttet2) == ("kort", False)


def test_klipp_med_status_avslorer_banktekst_som_selv_ender_med_ellipsis():
    """Poenget med statusen: ordet «…» i RESULTATET sier ikke at VI kuttet."""
    tekst, kuttet = GEN_MOD.klipp_med_status("banken skrev …", 100)
    assert tekst == "banken skrev …" and kuttet is False
    tekst2, kuttet2 = GEN_MOD.klipp_med_status("banken skrev ...", 100)
    assert kuttet2 is False and tekst2.endswith("...")


def test_alle_renderte_tekster_er_noeyaktig_klipp_av_kilden():
    """LIKHET, ikke delstreng — og alle de sammensatte feltene med.

    Delstreng-kravet (som foerste utgave brukte) kan passere naar produksjon og
    test deler samme feil. Her bygges hele den forventede strengen opp.
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
        assert n["one"] == (f"{target} · perspektiv: {_perspektiv(b)}"
                            if target else
                            f"perspektiv: {_perspektiv(b)}"), n["id"]

        assert n["what"] == (
            f"{GEN_MOD.klipp(maal.get('instrument', ''), G['what'])} — "
            f"proxy chain: "
            f"{GEN_MOD.klipp(' -> '.join(maal.get('proxy_chain', [''])), G['what'])}"
        ), n["id"]

        rolle, kuttet = GEN_MOD.klipp_med_status(
            buf.get("role") or "—", G["how"])
        sakse = GEN_MOD.sakse_tekst(b)
        assert n["how"] == (
            f"Buffer role: {rolle}{'' if kuttet else '.'} "
            f"Epistemic: {ep.get('sannhetsstatus', '—')} / "
            f"{ep.get('evidensstatus', '—')} / "
            f"{ep.get('konsensusstatus', '—')}."
            + (f" S-axis: {sakse}"
               f"{'' if sakse.endswith(('.', '…')) else '.'}" if sakse else "")
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
    """`role: None` og `role: ""` ga «Buffer role: . Epistemic: …»."""
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
    assert rad3["one"] == "perspektiv: agnostic", rad3["one"]


# --- 3. spoersmaalene er ikke generert ------------------------------------

def test_den_genererte_spoersmaalsteksten_kommer_aldri_tilbake():
    """Den maalte fallback-linja skal ikke kunne gjenoppstaas i noen form.

    Foerste utgave av denne testen sa «en node med evidensstatus=ingen faar
    ingen cond». Det var riktig saa lenge cond BARE kunne komme fra den
    genererte linja — men feil i det oeyeblikket banken fikk et ekte
    spoersmaalsfelt: en node kan mangle evidens OG ha et reelt, aapent
    spoersmaal fra banken samtidig. Kravet er ikke «ingen spoersmaal», det er
    «ingen spoersmaal skrevet av generatoren». Derfor maales den konkrete
    teksten, og proveniensen maales i testen over.
    """
    noder, _ = _bygg_og_les()
    forbudt = ("no evidence yet", "hypothesis marked honestly")
    feil = [(n["id"], c) for n in noder for c in (n["cond"] or [])
            if any(f in (c["q"] if isinstance(c, dict) else c) for f in forbudt)]
    assert not feil, feil[:6]


def test_hvert_spoersmaal_kommer_fra_banken():
    """Et spoersmaal skal kunne pekes paa i banken — ikke bare mangle.

    To lovlige kilder: `open_questions` paa noden, eller `stipulasjoner.motor`
    som begynner paa KANDIDAT (broen venter paa konnektor-deploy). Kommer det et
    spoersmaal i atlaset uten en av dem, er det generatorens eget.
    """
    noder, _ = _bygg_og_les()
    bank = _bank()
    for n in noder:
        if not n["cond"]:
            continue
        b = bank[n["name"]]
        motor = (b.get("stipulasjoner") or {}).get("motor", "")
        assert b.get("open_questions") or str(motor).startswith("KANDIDAT"), (
            f"{n['id']} baerer et spoersmaal ({n['cond']}) uten "
            f"open_questions i banken og uten KANDIDAT-motor (motor={motor!r})")


def test_bankfoedte_spoersmaal_naar_atlaset():
    """Feltet `open_questions` skal faktisk leses — ellers er det et tomt loft.

    Baade tekstformen og {q, r, to}-formen, og ukjente noekler skal ikke
    lekke gjennom til den bygde spoersmaalslista.
    """
    rad = GEN_MOD._node_rad(
        {"id": "h2o.solid", "open_questions": [
            "stilles det en maaling vi ikke har gjort?",
            {"q": "holder testen?", "to": "connector deploy", "tull": "nei"},
            {"q": "   "},
            ""]}, 0)
    assert rad["cond"] == [
        "stilles det en maaling vi ikke har gjort?",
        {"q": "holder testen?", "to": "connector deploy"}], rad["cond"]


def test_spoersmaalene_er_unike():
    noder, _ = _bygg_og_les()
    sett = [c["q"] if isinstance(c, dict) else c
            for n in noder for c in (n["cond"] or [])]
    assert len(sett) == len(set(sett)), f"dupliserte spoersmaal: {sett}"


def test_kapittel9_sier_hva_atlaset_bestaar_av():
    """«Alt paa en gang» maa ikke se fyldigere ut enn det er.

    Målt: 116 publiserte noder, 53 av dem uten gruppe ennå — og hvorfor de
    mangler den (observasjon, regime eller motor). "Designet og ikke bygget" var
    en byggestatus teksten fant på; se tests/test_atlas_byggestatus.py.
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
    assert ikke_bygget > 0 and uten_evidens > 0, "tellingene er doede"
    grunn = GEN_MOD.uten_gruppe_grunner(list(bank.values()))
    assert (f"{ikke_bygget} of them without a group yet "
            f"({grunn['observasjon']} observations") in siste["lede"], (
        f"kapittel 9 sier ikke hvor mange som mangler gruppe, og hvorfor: "
        f"{siste['lede']}")
    assert f"{uten_evidens} nodes carry no evidence yet" in siste["story"], (
        f"kapittel 9 sier ikke hvor mange som mangler evidens: {siste['story']}")
    assert len(noder) and f"{len(noder)} nodes" in siste["lede"]


# --- 4. S-aksen naar BEGGE byggene ----------------------------------------

def test_saksen_staar_i_how_naar_den_er_maalt():
    noder, _ = _bygg_og_les()
    bank = _bank()
    maalt = [n for n in noder if GEN_MOD.sakse_tekst(bank[n["name"]])]
    assert maalt, "ingen noder med S-akse i utsnittet — maalingen er doed"
    mangler = [n["id"] for n in maalt
               if f"S-axis: {GEN_MOD.sakse_tekst(bank[n['name']])}" not in n["how"]]
    assert not mangler, f"S-aksen naar ikke `how` for: {mangler[:8]}"


def test_saksen_er_ikke_en_gjentatt_mal():
    """Er S-aksen maalt, skal teksten vaere nodens egen — ikke én felles linje."""
    noder, _ = _bygg_og_les()
    tekster = [n["how"].split("S-axis: ", 1)[1] for n in noder
               if "S-axis: " in n["how"]]
    assert tekster, "ingen S-akse-tekster"
    assert len(set(tekster)) > 1, "S-aksen er identisk paa alle noder"


def test_saksen_naar_teksttvillingen_og_headeren():
    """data.mjs er ikke nok: begge byggene leser `how`, og headeren leser META.

    The renderer is a HAND-COPIED copy of the skill's asset, not read-only, so the
    BUILT files are what gets tested — not just that the key exists in data.mjs
    (the copy carries the code-namespace fix from #506; the asset carries it too
    since 2026-09-19, so a further edit belongs in both).
    """
    noder, data = _bygg_og_les()
    bank = _bank()
    eksempel = next(n for n in noder
                    if GEN_MOD.sakse_tekst(bank[n["name"]]))
    tekst = GEN_MOD.sakse_tekst(bank[eksempel["name"]])

    system_md = (ATLAS / "SYSTEM.md").read_text(encoding="utf-8")
    assert tekst in system_md, "S-aksen naar ikke SYSTEM.md"

    atlas_html = (ATLAS / "atlas.html").read_text(encoding="utf-8")
    assert '"k":"S-axis"' in atlas_html, (
        "S-aksen mangler i atlasets stats-header (META.stats -> STATS)")

    maalt = len([n for n in noder if GEN_MOD.sakse_tekst(bank[n["name"]])])
    assert f"{maalt} of {len(noder)} measured" in atlas_html, (
        "headeren viser ikke hvor mye av S-aksen som er maalt")
    assert f"{maalt} of {len(noder)} measured" in data, (
        "tallet staar ikke i data.mjs")


# --- 5. ett ord, ett tall ------------------------------------------------

def test_motorordet_betyr_bare_en_ting_paa_hver_flate():
    """«motorer» sto for 32 (motorfiler) ett sted og 19 (motornoder) et annet.

    To ulike maalinger med samme navn er ikke en navnekonflikt man kan leve
    med: den som leser 32 og 19 tror ett av tallene lyver. Utad heter de naa
    MOTORFILER og ENGINE NODES.
    """
    import subprocess as sp
    r = sp.run(["/opt/venvs/t_123ed6d9/bin/python",
                str(ROT / "scripts" / "atlas_navigasjon.py"), ".", "--ref",
                "origin/main"], capture_output=True, text=True, cwd=ROT,
               timeout=120)
    assert r.returncode == 0, r.stderr[-300:]
    assert "motorfiler" in r.stdout, (
        f"navigatoren kaller dem fortsatt motorer:\n{r.stdout[:200]}")
    assert " motorer · " not in r.stdout, "tvetydig ord staar igjen"

    system_md = (ATLAS / "SYSTEM.md").read_text(encoding="utf-8")
    noder, _ = _bygg_og_les()
    motorer = sum(1 for n in noder if "_engine" in n["name"])
    assert f"{len(noder)} nodes, {motorer} engine nodes" in system_md, (
        "teksttvillingen skiller ikke motorfil fra motornode")
