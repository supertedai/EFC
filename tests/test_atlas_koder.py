"""Kode-entydighet: hver node har sin egen korte identifikator.

MAALT 2026-09-17 mot origin/main: `efc_atlas_generator.py` hadde 28 koder
for 82 noder. Resten falt tilbake til `nid[:2].upper()`, og de 73
offentlige nodene fikk dermed 18 koder:

    EF  20 noder   (efc.l1, efc.l2, efc.rotation_engine, ...)
    OB  20 noder   (obs.bao, obs.cmb_tt, ...)
    HO  12 noder   (homo.fluxus, ...)
    H2   6 noder   (h2o.solid, ...)
    RE   2 noder   (regnbue, regnbue.observator)

En kode som peker paa tjue noder samtidig identifiserer ingen av dem.

Koden ER en identifikator, ikke pynt: `build.mjs` bygger spoersmaal-ID-er
av den (`Q-<kode><n>`, og indeksen i SYSTEM.md sier «Reference by ID»), og
FLOWS navngir hoppene sine med den (HA, BI, VU, EF). Beslutningen er
derfor at koden skal vaere ENTYDIG, at tabellen skal dekke hele banken, og
at generatoren skal FEILE heller enn aa gjette.

FEILMODUSEN som gjorde dette usynlig er verdt aa navngi: fallbacken svarte
i stedet for aa si fra. 15 av de 28 noeklene navnga i tillegg noder som
aldri har eksistert under det navnet (`efc.hubble` mot `efc.hubble_engine`)
— tabellen hadde raatnet, og ingen kunne se det. Denne filen tester BEGGE
retninger, fordi en test som bare ser etter hull ikke ser rot.

Reglene bor i generatoren (`manglende_koder`, `foreldede_koder`,
`kollisjoner`) og ikke i prosa her: da kan de kjores og muteres mot.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROT = Path(__file__).resolve().parents[1]
JSONLD = ROT / "schema" / "regime_nodes.jsonld"
GENERATOR = ROT / "scripts" / "maintenance" / "efc_atlas_generator.py"
DATA_MJS = ROT / "docs" / "efc-atlas" / "atlas" / "data.mjs"

sys.path.insert(0, str(ROT / "scripts" / "maintenance"))
import efc_atlas_generator as gen  # noqa: E402

#: Brikken som tegner koden er 16 px bred (atlas/template.html) — derav
#: 1-2 tegn. Grensen er visuell, men koden er en identifikator, saa begge
#: krav maa holde samtidig.
KODE_MONSTER = re.compile(r"[A-Z0-9]{1,2}\Z")


def _bank() -> list[dict]:
    return json.loads(JSONLD.read_text(encoding="utf-8"))["nodes"]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class TestAtlasKoder(unittest.TestCase):

    def test_hver_node_i_banken_har_en_deklarert_kode(self):
        """Ingen fallback skal kunne svare for en node. En ny node uten
        kode er en feil som skal SEES — ikke en kode som gjettes."""
        mangler = gen.manglende_koder(_bank())
        self.assertEqual(mangler, [],
                         f"{len(mangler)} node(r) uten kode: {mangler}")

    def test_kodene_er_entydige(self):
        """Kjernen i funnet: 73 noder identifisert av 18 koder."""
        koll = gen.kollisjoner(_bank())
        detalj = "; ".join(f"{k} -> {', '.join(v)}" for k, v in koll.items())
        self.assertEqual(koll, {},
                         f"{len(koll)} kode(r) peker paa flere noder: {detalj}")

    def test_deklarasjonen_raatner_ikke(self):
        """Motsatt retning. 15 av de 28 gamle noeklene navnga noder som ikke
        finnes (`efc.hubble`, `efc.water`, ...) — de heter `*_engine` i
        banken. Endres en node-id uten at koden flytter med, skal det felle
        her, ikke bli staaende som en stille etterlatt noekkel."""
        doede = gen.foreldede_koder(_bank())
        self.assertEqual(doede, [],
                         f"koder deklarert for noder som ikke finnes: {doede}")

    def test_koden_passer_i_brikken(self):
        """1-2 tegn, A-Z0-9. En kode som ikke faar plass i brikken er en
        usynlig feil i det offentlige kartet."""
        darlige = {k: v for k, v in gen.KODER.items()
                   if not KODE_MONSTER.match(v)}
        self.assertEqual(darlige, {}, f"koder utenfor [A-Z0-9]{{1,2}}: {darlige}")

    def test_data_mjs_baerer_de_deklarerte_kodene(self):
        """Det publiserte artefaktet, ikke bare tabellen. Ferskhetstesten
        fanger en utdatert fil; denne fanger at innholdet er det samme som
        beslutningen."""
        tekst = DATA_MJS.read_text(encoding="utf-8")
        par = re.findall(r'"code": "([^"]+)",\n\s+"name": "([^"]+)"', tekst)
        self.assertTrue(par, "fant ingen kode/name-par i data.mjs")
        ut = {navn: kode for kode, navn in par}
        offentlige = [n["id"] for n in _bank()
                      if n.get("synlighet") == "offentlig"]
        self.assertEqual(sorted(ut), sorted(offentlige),
                         "data.mjs og banken viser ikke samme nodesett")
        feil = {n: (ut[n], gen.KODER[n]) for n in ut
                if ut[n] != gen.KODER[n]}
        self.assertEqual(feil, {}, f"data.mjs avviker fra KODER: {feil}")
        self.assertEqual(len(set(ut.values())), len(ut),
                         "data.mjs publiserer en kode som peker paa flere noder")

    def test_flows_peker_paa_deklarerte_koder(self):
        """FLOWS navngir noder med koden (HA -> KL, BI -> EF, VU -> TR).
        Den koblingen er bare meningsbaerende saa lenge koden er entydig —
        og den er grunnen til at `EF` ikke kan peke paa tjue noder."""
        gyldige = set(gen.KODER.values())
        for f in gen.FLOWS:
            for h in f["hops"]:
                for ende in (h[0], h[1]):
                    self.assertIn(ende, gyldige,
                                  f"FLOWS «{f['id']}» peker paa koden "
                                  f"«{ende}», som ikke er deklarert")

    def test_kode_for_gjetter_ikke(self):
        """Den gamle fallbacken svarte med `nid[:2].upper()`. Den skal ikke
        kunne svare i det hele tatt."""
        with self.assertRaises(KeyError):
            gen.kode_for("test.finnes_ikke")

    def test_generatoren_har_ingen_stille_fallback(self):
        """Tripwire mot gjeninnfoering av selve oppslaget, ikke mot ordet:
        kommentaren over KODER maa kunne NAVNGI feilen (`nid[:2].upper()`,
        som gjorde 20 noder til «EF»). Den bevisende testen er den under —
        en ekte kjoring av hoved() — men et `KODER.get(...)` med en verdi
        bak komma skal ikke kunne snike seg inn usett."""
        kilde = GENERATOR.read_text(encoding="utf-8")
        kode = "\n".join(l for l in kilde.splitlines()
                         if not l.lstrip().startswith("#"))
        self.assertIsNone(
            re.search(r"KODER\.get\s*\(", kode),
            "et oppslag med fallback er tilbake i generatoren: "
            "KODER.get(...) svarer i stedet for aa si fra")

    def _hoved_mot(self, bank: list[dict], *,
                   koder: dict | None = None):
        """Kjorer hoved() mot en falsk bank og en tom ut-mappe.

        Baade kilden og ut-mappen byttes, saa en vakt som IKKE fyrer skriver
        i en temp-mappe — den kan ikke roere det ekte atlaset.
        """
        with tempfile.TemporaryDirectory() as tmp:
            falsk = Path(tmp) / "regime_nodes.jsonld"
            falsk.write_text(json.dumps({"nodes": bank}), encoding="utf-8")
            ut = Path(tmp) / "atlas"
            ut.mkdir()
            buffer = io.StringIO()
            with contextlib.ExitStack() as st:
                st.enter_context(mock.patch.object(gen, "JSONLD", falsk))
                st.enter_context(mock.patch.object(gen, "ATLAS_DIR", ut))
                if koder is not None:
                    st.enter_context(mock.patch.dict(gen.KODER, koder))
                with contextlib.redirect_stdout(buffer):
                    rc = gen.hoved()
            return rc, buffer.getvalue(), (ut / "data.mjs").exists()

    def test_ny_node_uten_kode_feller_generatoren(self):
        """Krav 3, provd paa ekte: en ny node uten kode skal ikke kunne
        passere ved fallback. Den skal stoppe bygget FOER data.mjs skrives
        — et atlas med feil koder ser ferdig ut, og det er derfor loven."""
        for_ut = _sha(DATA_MJS)
        bank = _bank() + [{"id": "test.ny_uten_kode", "synlighet": "offentlig"}]
        rc, utskrift, skrevet = self._hoved_mot(bank)
        self.assertEqual(rc, 1, f"generatoren slapp gjennom:\n{utskrift}")
        self.assertIn("missing a code", utskrift,
                      "feilet av feil grunn — proven maa navngi aarsaken")
        self.assertIn("test.ny_uten_kode", utskrift)
        self.assertFalse(skrevet, "data.mjs ble skrevet for vakten fyrte")
        self.assertEqual(_sha(DATA_MJS), for_ut,
                         "generatoren roerte det ekte atlaset")

    def test_kollisjon_feller_generatoren(self):
        """Samme vakt, motsatt aarsak: en kode som peker paa to noder skal
        ikke kunne bygges i det hele tatt."""
        for_ut = _sha(DATA_MJS)
        rc, utskrift, skrevet = self._hoved_mot(_bank(),
                                                koder={"h2o.solid": "LI"})
        self.assertEqual(rc, 1, f"generatoren slapp gjennom:\n{utskrift}")
        self.assertIn("several nodes", utskrift,
                      "feilet av feil grunn — proven maa navngi aarsaken")
        self.assertIn("h2o.liquid", utskrift)
        self.assertFalse(skrevet, "data.mjs ble skrevet for vakten fyrte")
        self.assertEqual(_sha(DATA_MJS), for_ut,
                         "generatoren roerte det ekte atlaset")

    def test_foreldet_kode_feller_generatoren(self):
        """Og tredje: en noekkel som ikke lenger navngir en node skal stoppe
        bygget. Det var den tilstanden tabellen sto i — usett."""
        for_ut = _sha(DATA_MJS)
        rc, utskrift, skrevet = self._hoved_mot(_bank(),
                                                koder={"efc.hubble": "ZZ"})
        self.assertEqual(rc, 1, f"generatoren slapp gjennom:\n{utskrift}")
        self.assertIn("do not exist", utskrift,
                      "feilet av feil grunn — proven maa navngi aarsaken")
        self.assertFalse(skrevet, "data.mjs ble skrevet for vakten fyrte")
        self.assertEqual(_sha(DATA_MJS), for_ut,
                         "generatoren roerte det ekte atlaset")


if __name__ == "__main__":
    unittest.main()
