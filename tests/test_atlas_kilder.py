"""Kildeaksen: en kilde som rutes inn i mange domener skal ikke kunne være usynlig.

FUNNET som gjorde denne testen nødvendig (2026-09-18). Domeneaksen
(`test_atlas_dekning.py`) maaler eierskap per BUSSDOMENE. Maalt mot
origin/main etter at alle 39 domener hadde faatt sin node:

    39 av 39 domener dekket.

og samtidig, maalt paa den andre aksen:

    GDELT GKG    20 domener   30 352 meldinger   14 lesere   0 eiere
    World Bank   18 domener      302 meldinger    0 lesere   0 eiere
    MAST/CAOM     6 domener      174 meldinger    0 lesere   0 eiere

Den stoerste kilden paa bussen — 30 352 meldinger, tjue domener — eies av
ingen. Domeneaksen kunne ikke se det: hvert domene har sin node, hver node
staar som `dekket`, og kilden de alle LESER finnes ikke i kartet som noe
annet enn et felt i hver av dem.

    Et kart som maaler hvor mange steder noe kommer inn, og ikke hvor det
    kommer fra, teller symptomer.

## Fire feil denne filen feller

1. En kilde som baerer meldinger uten aa staa i deklarasjonen (stillhet).
2. En deklarert kilde som ikke lenger baerer noe (raatnende påstand).
3. En node som navngir en kilde dens EGET bussdomene ikke baerer. Maalt:
   `kosmos.interstellart`, `kosmos.stjerner` og `kosmos.romfart` hadde
   `measure.measurer = «GDELT-prosjektet»` mens domenene deres baerer
   `observasjon.mast-caom` og `launch-library` og NULL GDELT-meldinger.
   Generatoren hadde en fallback til GDELT der oppslaget skulle sagt fra.
4. En kilde som bæres av flere domener UTEN eier og UTEN begrunnelse.

Terskelen i punkt 4 er ikke valgt: en kilde som bæres av ETT domene eies av
det domenets node — lesningen ER noden, og det finnes ingen skygge. Baeres
den av to eller flere, kan ingen enkelt node dekke den, og da maa fravaeret
av eier stå navngitt.

Listene i deklarasjonen (`lesere`, `domener`, `meldinger`) utledes HER, ikke
i byggeren: en liste som bare sjekkes mot seg selv roterer i takt med feilen.
"""
from __future__ import annotations

import json
import sys
import unittest
from collections import defaultdict
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROT / "schema" / "nats_domener.snapshot.json"
DEKNING = ROT / "schema" / "atlas_dekning.json"
NODER = ROT / "schema" / "regime_nodes.jsonld"
GENERATOR = ROT / "scripts" / "maintenance" / "bygg_kildenoder.py"

sys.path.insert(0, str(ROT / "scripts"))
import atlas_kilder as ak  # noqa: E402


def _les(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _kilde_for_node(n: dict) -> str | None:
    """Kilden noden SELV skriver — ikke en liste vi har skrevet for den."""
    return ((n.get("lagdeling") or {}).get("kilde") or {}).get("kilde")


def _baert(snapshot: dict) -> dict[str, dict]:
    """Kildeleddene bussen bærer, med domener og meldinger — utledet av emnene.

    Skaperen av emnenavnene er `docs/nats-koblingskart.md`: emnene har formen
    `<rot>.<domene>.<lag>.<kilde>`. Det siste leddet ER kilden.
    """
    ut: dict[str, dict] = defaultdict(lambda: {"meldinger": 0, "domener": set()})
    for domene, rad in snapshot["domener"].items():
        for emne, antall in rad["emner"].items():
            ledd = str(emne).split(".")[-1]
            ut[ledd]["meldinger"] += antall
            ut[ledd]["domener"].add(domene)
    return {k: {"meldinger": v["meldinger"], "domener": sorted(v["domener"])}
            for k, v in ut.items()}


class TestKildeaksen(unittest.TestCase):

    def setUp(self):
        self.snapshot = _les(SNAPSHOT)
        self.dekning = _les(DEKNING)
        self.noder = _les(NODER)["nodes"]
        self.baert = _baert(self.snapshot)

    def test_kilder_seksjonen_finnes(self):
        """Uten seksjonen er hele aksen en paastand om at noen husker den."""
        self.assertIn("kilder", self.dekning,
                      "atlas_dekning.json har ingen `kilder`-seksjon — "
                      "kildeaksen er ikke deklarert")

    def test_ingen_kilde_baerer_meldinger_uten_aa_staa_i_deklarasjonen(self):
        """Kjernen, og den samme invarianten som for domenene.

        Et kildeledd som begynner aa baere meldinger skal felle denne
        testen inntil noen har tatt stilling til det — ikke gli inn i
        stillhet fordi domenet den mater alt har en node.
        """
        udeklarerte = sorted(set(self.baert) - set(self.dekning["kilder"]))
        self.assertEqual(
            udeklarerte, [],
            f"{len(udeklarerte)} kildeledd baerer meldinger uten aa staa i "
            f"atlas_dekning.json: {udeklarerte}")

    def test_ingen_deklarert_kilde_har_sluttet_aa_baere(self):
        """Motsatt vei: en deklarasjon for en stroem som er borte er en
        påstand om en verden som ikke finnes lenger."""
        doede = sorted(set(self.dekning["kilder"]) - set(self.baert))
        self.assertEqual(doede, [],
                         f"deklarert for kildeledd som ikke bærer noe: {doede}")

    def test_hver_node_navngir_en_kilde_dens_eget_domene_baerer(self):
        """Fabriceringsvakten. Maalt 2026-09-18: tre noder navnga GDELT for
        domener uten en eneste GDELT-melding, fordi generatorens oppslag
        svarte GDELT naar kilden var ukjent.

        Kravet er maskinelt: kildenoden skriver, maa hoere til et ledd som
        domenet HUN eier faktisk bærer. Da kan etiketten ikke vaere usann —
        den kan bare vaere vilkaarlig, og det er en annen sak.
        """
        navn_til_ledd: dict[str, set[str]] = defaultdict(set)
        for ledd, rad in self.dekning["kilder"].items():
            if rad.get("navn"):
                navn_til_ledd[rad["navn"]].add(ledd)

        feil = []
        for n in self.noder:
            kilde = _kilde_for_node(n)
            domene = n.get("buss_domene")
            if not kilde or not domene:
                continue
            ledd = navn_til_ledd.get(kilde)
            if not ledd:
                feil.append((n["id"], kilde, domene, "kilden er ikke deklarert"))
                continue
            baerer = any(domene in self.baert.get(l, {}).get("domener", [])
                         for l in ledd)
            if not baerer:
                feil.append((n["id"], kilde, domene,
                             "domenet bærer ingen av kildens ledd"))
        self.assertEqual(
            feil, [],
            f"{len(feil)} node(r) navngir en kilde de ikke leser:\n  " +
            "\n  ".join(f"{i} sier «{k}», domenet {d} — {h}" for i, k, d, h in feil))

    def test_leserlisten_er_utledet_av_nodenes_eget_felt(self):
        """Samme krav som `noder`-listene i domeneaksen: en liste som er
        skrevet for haand kan utelate en node uten at noe ser det."""
        for ledd, rad in self.dekning["kilder"].items():
            navn = rad.get("navn")
            maalt = sorted(n["id"] for n in self.noder
                           if navn and _kilde_for_node(n) == navn)
            self.assertEqual(
                sorted(rad.get("lesere") or []), maalt,
                f"{ledd}: deklarasjonen sier leserne {rad.get('lesere')}, "
                f"banken sier {maalt}")

    def test_domenene_og_volumet_er_utledet_av_maalingen(self):
        """Begge veier: en kilde kan ikke tilskrives et domene den ikke
        mater, og et domene den mater kan ikke utelates."""
        for ledd, rad in self.dekning["kilder"].items():
            self.assertIn(ledd, self.baert, f"{ledd} bærer ikke meldinger")
            maalt = self.baert[ledd]
            self.assertEqual(sorted(rad.get("domener") or []), maalt["domener"],
                             f"{ledd}: deklarasjonen sier {rad.get('domener')}, "
                             f"maalingen sier {maalt['domener']}")
            self.assertEqual(rad.get("meldinger"), maalt["meldinger"],
                             f"{ledd}: deklarasjonen sier {rad.get('meldinger')} "
                             f"meldinger, maalingen sier {maalt['meldinger']}")

    def test_en_delt_kilde_uten_eier_maa_baere_grunnen_sin(self):
        """Et fravaer av eier skal staa navngitt, ikke vaere stille.

        Terskelen er ikke valgt: baeres kilden av ett domene, eies den av
        det domenets node. Baeres den av flere, kan ingen enkelt node dekke
        den — og da er stillheten feilen.
        """
        mangler = []
        for ledd, rad in self.dekning["kilder"].items():
            if rad.get("status") == "eid":
                continue
            if len(self.baert.get(ledd, {}).get("domener", [])) > 1:
                if not str(rad.get("begrunnelse", "")).strip():
                    mangler.append(ledd)
        self.assertEqual(
            mangler, [],
            f"{len(mangler)} kildeledd bæres av flere domener og har hverken "
            f"eier eller begrunnelse: {mangler}")

    def test_eid_status_kreve_en_eier_som_navngir_kilden(self):
        """«eid» skal bety at en node ER kilden — ikke at noen nevner den."""
        bank = {n["id"]: n for n in self.noder}
        for ledd, rad in self.dekning["kilder"].items():
            eiere = list(rad.get("eiere") or [])
            if rad.get("status") == "eid":
                self.assertTrue(eiere, f"{ledd} er «eid» uten eier")
            else:
                self.assertEqual(eiere, [],
                                 f"{ledd} navngir eiere {eiere} uten status «eid»")
            for e in eiere:
                self.assertIn(e, bank, f"{ledd}: eieren «{e}» finnes ikke")
                self.assertEqual(_kilde_for_node(bank[e]), rad.get("navn"),
                                 f"{ledd}: eieren «{e}» navngir ikke kilden")

    def test_aksen_er_ikke_tom(self):
        """En test som ikke kan felle noe beviser ingenting. Denne sier at
        kildeaksen faktisk baerer de to formene den ble bygget for: en kilde
        med flere lesere, og en kilde som bæres av flere domener."""
        lesere = sum(1 for rad in self.dekning["kilder"].values()
                     if rad.get("lesere"))
        brede = sum(1 for ledd in self.dekning["kilder"]
                    if len(self.baert.get(ledd, {}).get("domener", [])) > 1)
        self.assertGreater(lesere, 0, "ingen node navngir noen kilde — "
                                      "koblingen mellom bank og kilde er borte")
        self.assertGreater(brede, 0, "ingen kilde bæres av flere domener — "
                                     "da maaler aksen ingenting")

    def test_sjekken_i_verktoyet_og_testen_er_enede(self):
        """`atlas_kilder.py --sjekk` er den kjoerbare inngangen; testene over
        er de som feller. Sier de to ulike ting, er en av dem feil."""
        self.assertEqual(ak.avvik({"snapshot": self.snapshot,
                                   "dekning": self.dekning,
                                   "noder": {"nodes": self.noder}}), [])

    def test_generatoren_gjetter_ikke_paa_kilden(self):
        """Fallbacken som fabrikkerte tre kilder. `KILDE.get(ledd, GDELT)`
        svarte i stedet for aa si fra. Den skal ikke kunne svare igjen."""
        sys.path.insert(0, str(ROT / "scripts" / "maintenance"))
        sys.modules.pop("bygg_kildenoder", None)
        import bygg_kildenoder as bk  # noqa: E402
        with self.assertRaises(bk.KildeFeil):
            bk.kilde_for(["observasjon.finnes_ikke"])
        with self.assertRaises(bk.KildeFeil):
            bk.kilde_for([])
        # og tripwiren mot selve oppslaget: navnet paa den gamle
        # fallbacken skal ikke kunne staa i en kilde-oppslag igjen.
        kilde = GENERATOR.read_text(encoding="utf-8")
        kodelinjer = "\n".join(
            l for l in kilde.splitlines()
            if "KILDE.get(" in l and not l.strip().startswith("#"))
        self.assertEqual(kodelinjer, "", "generatoren har et kilde-oppslag "
                                        f"med fallback igjen: {kodelinjer!r}")


if __name__ == "__main__":
    unittest.main()
