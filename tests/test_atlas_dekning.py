"""Dekningsinvarianten: intet buss-domene skal være usynlig for atlaset.

FUNNET som gjorde denne testen nødvendig (2026-09-17): prediksjonskontrakten
laa KOMPLETT paa bussen — med forseglet DOI, SHA256, frys, kriterium og
arbiter — og atlaset visste ingenting. Det fantes ingen node, ingen kobling,
ingen advarsel. Jeg fant det bare ved aa lese stroemmene direkte.

    Et kart som ikke viser hvor det er ufullstendig, er farligere enn
    ingen kart — fordi det ser komplett ut.

Atlaset kan ikke selv oppdage at det mangler et lag. Men det kan maales:
kryss emnene som BAERER trafikk mot nodene som FINNES, og navngi de som
ikke har en motpart.

Dette er den invarianten. Den sier ikke at alt skal dekkes — atlaset
beskriver 3 av 39 domener, og det er en aerlig tilstand. Den sier at et gap
skal staa NAVNGITT i schema/atlas_dekning.json, ikke være stille. Et nytt
domene som begynner aa baere meldinger skal felle denne testen inntil noen
har tatt stilling til det.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROT / "schema" / "nats_domener.snapshot.json"
DEKNING = ROT / "schema" / "atlas_dekning.json"
NODER = ROT / "schema" / "regime_nodes.jsonld"

GYLDIGE_STATUS = {"dekket", "delvis", "ikke_dekket"}


def _les(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


class TestDekningsinvarianten(unittest.TestCase):
    def test_hvert_bussdomene_er_deklarert(self):
        """Kjernen. Et domene som baerer meldinger men ikke staar i
        deklarasjonen er usynlig — og usynlig er hvordan prediksjonslaget
        kunne ligge komplett paa bussen uten at atlaset visste det."""
        snap = set(_les(SNAPSHOT)["domener"])
        dekl = set(_les(DEKNING)["domener"])
        udeklarerte = sorted(snap - dekl)
        self.assertEqual(
            udeklarerte, [],
            f"{len(udeklarerte)} bussdomene(r) baerer meldinger uten aa "
            f"staa i atlas_dekning.json — atlaset vet ikke at de finnes:\n  "
            + "\n  ".join(udeklarerte))

    def test_hvert_emne_i_et_kjent_domene_er_tatt_stilling_til(self):
        """Reviewfunn 3: bare domenenoekkelen ble sammenlignet, saa et kjent
        domene kunne faa nye emner usett. Naa sammenlignes emne-listene."""
        snap = _les(SNAPSHOT)["domener"]
        dekl = _les(DEKNING)["domener"]
        for domene, rad in snap.items():
            if domene not in dekl:
                continue  # fanges av testen over
            nye = sorted(set(rad["emner"]) - set(dekl[domene]["emner"]))
            self.assertEqual(
                nye, [],
                f"{domene} har nye buss-emner som ikke er tatt stilling "
                f"til: {nye}")

    def test_deklarasjonen_raatner_ikke(self):
        """Motsatt retning: en deklarasjon for et domene som ikke lenger
        finnes er en påstand om en verden som er borte."""
        snap = set(_les(SNAPSHOT)["domener"])
        dekl = set(_les(DEKNING)["domener"])
        foreldede = sorted(dekl - snap)
        self.assertEqual(
            foreldede, [],
            f"deklarert for domener som ikke finnes i snapshottet: "
            f"{foreldede}")

    def test_hver_deklarasjon_har_status_og_begrunnelse(self):
        """Et gap uten grunn er bare et hull."""
        for domene, rad in _les(DEKNING)["domener"].items():
            self.assertIn(rad.get("status"), GYLDIGE_STATUS, domene)
            self.assertTrue(rad.get("begrunnelse", "").strip(),
                            f"{domene} mangler begrunnelse")

    def test_dekket_status_navngir_noder_som_faktisk_finnes(self):
        """Reviewfunn 1 og 2, det blokkerende. `dekket` og `delvis` er
        PAASTANDER om at atlaset beskriver domenet. Hver navngitte node maa
        finnes — og en dekket-status uten en eneste node er nettopp den
        udekkede påstanden som gjorde at verden.vaer kunne staa som dekket
        uten at noen node hadde den id-en."""
        finnes = {n["id"] for n in _les(NODER)["nodes"]}
        for domene, rad in _les(DEKNING)["domener"].items():
            ns = rad.get("noder", [])
            if rad["status"] in ("dekket", "delvis"):
                self.assertTrue(
                    ns, f"{domene} er '{rad['status']}' uten en eneste node "
                        f"— en dekket-status maa kunne innfris")
            for n in ns:
                self.assertIn(
                    n, finnes,
                    f"{domene} peker paa noden '{n}', som ikke finnes i "
                    f"regime_nodes.jsonld")

    def test_snapshottet_baerer_sin_egen_proveniens(self):
        """Uten maaletidspunkt kan ingen se om snaoshottet er ferskt."""
        prov = _les(SNAPSHOT).get("_proveniens", {})
        self.assertIn("maalt", prov)
        self.assertIn("kilde", prov)
        self.assertIn("lest_av", prov)

    def test_snapshottet_har_ikke_gaatt_ut_paa_dato(self):
        """En maaling uten utloepsdato er en paastand som sakte blir usann.
        Den foreldede kanban-kopien var gyldig, svarte og LOEY: den sluttet
        bare aa bli skrevet. Samme felle. Et snapshot som er for gammelt
        skal tvinge en ny maaling, ikke fortsette aa se verifisert ut."""
        import datetime
        maalt = _les(SNAPSHOT)["_proveniens"]["maalt"]
        naar = datetime.datetime.fromisoformat(maalt.replace("Z", "+00:00"))
        if naar.tzinfo is None:
            naar = naar.replace(tzinfo=datetime.timezone.utc)
        alder = (datetime.datetime.now(datetime.timezone.utc) - naar).days
        self.assertLess(
            alder, 90,
            f"snapshottet er {alder} dager gammelt — maal bussen paa nytt "
            f"og skriv schema/nats_domener.snapshot.json foer du stoler paa "
            f"dekningsbildet")


if __name__ == "__main__":
    unittest.main()
