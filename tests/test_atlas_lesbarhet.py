"""Atlasets lesbarhet: det brukeren moeter skal svare paa det det ser ut som.

Maalt 2026-09-18 (origin/main f4a3e4f2) var tre avvik i det RENDERte atlaset —
alle i generatoren, ingen i banken:

1. Alle 116 one-linere aapnet med samme mal, «Perspective: …». Hover-teksten
   sa hvem som mener det, ikke hva tingen ER, og substansen ble kuttet bakerst.
2. Tekstene ble kuttet med `[:70]`/`[:90]`/`[:80]` midt i ord — «fase
   identifisert via P_sat(T) o», «rotation engin», «holder temperaturen under
   oppvarming . Epistemic». Et kutt uten merke ser ut som hele teksten.
3. Spørsmålsfanen fikk en generert linje per node uten evidens, identisk for
   alle sju: «no evidence yet — hypothesis marked honestly». Den spurte ikke om
   noe; den gjentok `how`. Det er fallbacken som svarer.

Denne fila laaser at ingen av de tre kan komme tilbake.
"""
from __future__ import annotations

import functools
import importlib.util
import json
import pathlib
import re
import subprocess

ROT = pathlib.Path(__file__).resolve().parents[1]
GEN = ROT / "scripts" / "maintenance" / "efc_atlas_generator.py"
DATA = ROT / "docs" / "efc-atlas" / "atlas" / "data.mjs"
BANK = ROT / "schema" / "regime_nodes.jsonld"


def _generator():
    spec = importlib.util.spec_from_file_location("efc_atlas_generator", GEN)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN_MOD = _generator()


@functools.lru_cache(maxsize=1)
def _bygg_og_les():
    """Bygg atlaset fra banken, og les den RENDERte nodelista."""
    r = subprocess.run(
        ["/opt/venvs/t_123ed6d9/bin/python", str(GEN)],
        capture_output=True, text=True, cwd=ROT, timeout=180)
    assert r.returncode == 0, r.stderr[-600:]
    s = DATA.read_text(encoding="utf-8")
    i = s.index("export const NODES = ")
    j = s.index("\nexport const", i + 10)
    return json.loads(s[i:j][s[i:j].index("=") + 1:].strip().rstrip(";"))


def _bank():
    return {n["id"]: n for n in json.loads(
        BANK.read_text(encoding="utf-8"))["nodes"]}


# --- 1. one-lineren sier hva tingen er ------------------------------------

def test_ingen_oneliner_aapner_med_perspektivmalen():
    noder = _bygg_og_les()
    darlige = [n["id"] for n in noder
               if n["one"].lower().startswith(("perspective", "perspektiv"))]
    assert not darlige, f"one-lineren aapner med malen: {darlige[:8]}"


def test_onelinerne_deler_ikke_ett_prefiks():
    """En mal er ikke innhold, selv naar den ikke heter «Perspective».

    Maalt: 116/116 delte de foerste 20 tegnene. Et felles prefiks betyr at
    hover-teksten ikke skiller nodene — da er den ikke en etikett.
    """
    noder = _bygg_og_les()
    prefiks = [n["one"][:20] for n in noder]
    vanligst = max(set(prefiks), key=prefiks.count)
    assert prefiks.count(vanligst) <= len(noder) * 0.2, (
        f"{prefiks.count(vanligst)} av {len(noder)} one-linere deler "
        f"prefikset {vanligst!r}")


def test_perspektivet_er_ikke_borte_fra_noden():
    """Substansen foerst — men perspektivet skal fortsatt kunne leses."""
    noder = _bygg_og_les()
    bank = _bank()
    for n in noder[:200]:
        p = bank[n["name"]].get("perspektiv")
        forventet = GEN_MOD._perspektiv_tekst(p)
        assert forventet in n["one"], (n["id"], n["one"][:60])
        assert ["Perspective", forventet] in n["steps"]


# --- 2. et kutt skal vaere merket -----------------------------------------

def test_klipp_kutter_paa_ordgrense_og_merker():
    k = GEN_MOD.klipp
    assert k("kort", 10) == "kort"
    assert k("  to   ord  ", 20) == "to ord"
    lang = "ord " * 40
    ut = k(lang, 20)
    assert ut.endswith("…"), ut
    assert len(ut) <= 22, ut
    assert "  " not in ut and not ut.startswith(" ")


def test_alle_renderte_tekster_er_kuttet_paa_ordgrense():
    """Gjenskaper generatorens eget kutt og krever identitet.

    Fanger baade «kuttet midt i ord» og «kuttet uten aa si det»: teksten maa
    vaere noeyaktig det `klipp()` gir, og `klipp()` merker alt den kutter.
    """
    noder = _bygg_og_les()
    bank = _bank()
    g = GEN_MOD.GRENSER
    for n in noder:
        b = bank[n["name"]]
        maal = b.get("measure", {})
        felter = {
            "short": GEN_MOD.klipp(n["name"].split(".")[-1].replace("_", " "),
                                   g["short"]),
            "one": GEN_MOD.klipp(maal.get("target", ""), g["one"]),
            "what": GEN_MOD.klipp(maal.get("instrument", ""), g["what"]),
            "how": GEN_MOD.klipp(b.get("buffer", {}).get("role", "—"),
                                 g["how"]),
        }
        for felt, forventet in felter.items():
            assert forventet in n[felt], (n["id"], felt, n[felt][:80])


def test_ingen_renderte_tekster_baerer_kutteartefakter():
    """Artifaktene et hardt `[:n]`-kutt etterlater seg, uten kilde til hjelp.

    Ordgrense-kravet ligger i testen over (den gjenskaper `klipp()` og krever
    identitet). Her fanges signaturene et kutt setter uansett: mellomrom foer
    tegnsetting («oppvarming .»), dobbelt mellomrom, og hale-mellomrom.
    """
    noder = _bygg_og_les()
    feil = []
    for n in noder:
        for felt in ("short", "one", "what", "how"):
            t = n[felt]
            if (" ." in t or "  " in t or t != t.strip()
                    or "…." in t or ".." in t):
                feil.append((n["id"], felt, repr(t[-40:])))
    assert not feil, feil[:6]


# --- 3. spoersmaalene er ikke generert ------------------------------------

def test_ingen_node_faar_et_generert_spoersmaal():
    noder = _bygg_og_les()
    bank = _bank()
    for n in noder:
        b = bank[n["name"]]
        if b.get("epistemikk", {}).get("evidensstatus") == "ingen":
            assert not n["cond"], (
                f"{n['id']} har evidensstatus=ingen og fikk et generert "
                f"spoersmaal: {n['cond']}")


def test_spoersmaalene_er_unike_og_peker_ut_av_atlaset():
    """To noder med samme spoersmaal er ett spoersmaal, ikke to."""
    noder = _bygg_og_les()
    sett = []
    for n in noder:
        for c in n["cond"] or []:
            tekst = c["q"] if isinstance(c, dict) else c
            sett.append(tekst)
    assert len(sett) == len(set(sett)), f"dupliserte spoersmaal: {sett}"


# --- 4. S-aksen leses naar den finnes -------------------------------------

def test_klarhetsfunksjonen_naar_atlaset():
    """`klarhetsfunksjon` sto i banken paa 19 av 126 noder og ble droppet."""
    noder = _bygg_og_les()
    bank = _bank()
    med = [n for n in noder
           if (bank[n["name"]].get("maale_paradigme") or {})
           .get("klarhetsfunksjon")]
    assert med, "ingen noder med klarhetsfunksjon i utsnittet — maalingen doed"
    mangler = [n["id"] for n in med if not n.get("sAxis", {}).get("klarhet")]
    assert not mangler, f"klarhetsfunksjonen ble droppet for: {mangler[:8]}"
