"""Vær-kontrakten: den operative varianten, speilet fra bussen.

Runde-1-reviewen av PR #467 fant at jeg påstod å ha speilet vær-kontrakten
og ikke hadde det — jeg speilet bare den forseglede forskningsvarianten.
Prediksjonen bar `sted`, `lat`, `lon`, `horisont_bestilt_timer` og
`observert`; oppgjøret bar `forventet` i TILLEGG til `utfall` og `avvik`.
Ingen av dem fantes i skjemaet, og med `additionalProperties: false` ville
en ekte vær-melding ikke validert.

Testen under er derfor skrevet som en GENEREL invariant og ikke som en
liste over feltene jeg tilfeldigvis husket: hver nøkkel i den målte
meldingen skal ha en motpart i skjemaet. Det er invarianten som fanger
neste felt ogsaa, ikke bare de jeg lette etter i dag.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
SKJEMA = ROT / "schema" / "regime_node.schema.json"
FIXTURER = ROT / "tests" / "fixtures"

# Buss-nøkler som IKKE er kontrakt, men ruting: strømmen bruker dem til å
# sende meldingen til rett sted, og de beskriver meldingen selv — ikke
# prediksjonen eller utfallet. De skal derfor ikke inn i RegimeNode.
RUTING = {"Nats-Msg-Id", "lag", "domene", "undertype"}

# Maalt kontrakt -> skjema-felt. Brukes til å verifisere at speilingen
# faktisk dekker hver maalte noekkel.
PREDiksjon_KART = {
    "kilde": "source",
    "sted": "location",
    "lat": "latitude",
    "lon": "longitude",
    "utstedt": "issued_at",
    "gyldig_for": "valid_for",
    "horisont_bestilt_timer": "horizon_ordered_hours",
    "ledetid_min": "lead_time_minutes",
    "observert": "observed_at",
    "korrelasjon": "correlation",
    "forventet": "expected",
    "enheter": "units",
}

OPPGJOER_KART = {
    "kilde": "source",
    "sted": "location",
    "utstedt": "issued_at",
    "gyldig_for": "valid_for",
    "ledetid_min": "lead_time_minutes",
    "observert": "observed_at",
    "utfall_tid": "outcome_time",
    "korrelasjon": "correlation",
    "forventet": "expected",
    "utfall": "outcome",
    "avvik": "deviation",
    "utfall_kilde": "outcome_source",
    "oppgjoer_versjon": "settlement_version",
}

# Den FORSEGLEDE varianten (efc-fs8). Samme toppnivå-felt, men bærer
# forskningsapparatet i stedet for sted/horisont. At begge variantene
# finnes er grunnen til at required-listene bare inneholder det de har
# felles.
FORSEGLET_KART = {
    "kilde": "source",
    "observert": "observed_at",
    "observabel": "observable",
    "utstedt": "issued_at",
    "gyldig_for": "valid_for",
    "ledetid_min": "lead_time_minutes",
    "korrelasjon": "correlation",
    "forventet": "expected",
    "enheter": "units",
    "forseglet_doi": "sealed_doi",
    "forsegling_sha256": "sealing_sha256",
    "frys": "freeze",
    "kriterium": "criterion",
    "kriterier": "criteria",
    "toleranse_regel": "tolerance_rule",
    "grunnlag": "basis",
    "arbiter": "arbiter",
    "arbiter_venter_paa": "arbiter_waiting_for",
    "ebe_l_layer": "ebe_l_layer",
    "ebe_s_regime": "ebe_s_regime",
}


def _skjema() -> dict:
    return json.loads(SKJEMA.read_text(encoding="utf-8"))


def _felt(navn: str) -> dict:
    return _skjema()["$defs"]["RegimeNode"]["properties"][navn]["properties"]


def _hoder(filnavn: str) -> dict:
    return json.loads(
        (FIXTURER / filnavn).read_text(encoding="utf-8"))["hoder"]


class TestVaerkontrakten(unittest.TestCase):
    def test_hver_maalt_prediksjonsnoekkel_har_en_motpart(self):
        """Invarianten: ingen maalt noekkel faar falle utenfor skjemaet."""
        hoder = _hoder("nats-prediksjon-metno.json")
        skjema_felt = _felt("prediction")
        mangler = [k for k in hoder
                   if k not in RUTING and k not in PREDiksjon_KART]
        self.assertEqual(mangler, [],
                         f"maalte noekler uten skjema-felt: {mangler}")
        for buss, felt in PREDiksjon_KART.items():
            self.assertIn(buss, hoder, f"{buss} forsvant fra fixturen")
            self.assertIn(felt, skjema_felt, f"{felt} mangler i skjemaet")

    def test_hver_maalt_oppgjoersnoekkel_har_en_motpart(self):
        hoder = _hoder("nats-oppgjoer-metno.json")
        skjema_felt = _felt("settlement")
        mangler = [k for k in hoder
                   if k not in RUTING and k not in OPPGJOER_KART]
        self.assertEqual(mangler, [],
                         f"maalte noekler uten skjema-felt: {mangler}")
        for buss, felt in OPPGJOER_KART.items():
            self.assertIn(buss, hoder, f"{buss} forsvant fra fixturen")
            self.assertIn(felt, skjema_felt, f"{felt} mangler i skjemaet")

    def test_lat_og_lon_er_strenger_paa_bussen(self):
        """Målt: `lat` er "70.3554" — en streng, ikke et tall. Speiler jeg
        dem som numbers, avviser skjemaet de ekte meldingene."""
        hoder = _hoder("nats-prediksjon-metno.json")
        self.assertIsInstance(hoder["lat"], str)
        self.assertIsInstance(hoder["lon"], str)
        for felt in ("latitude", "longitude"):
            self.assertEqual(_felt("prediction")[felt]["type"], "string",
                             f"{felt} maa vaere string — bussen sender streng")

    def test_oppgjoeret_baerer_begge_sider_av_sloeyfa(self):
        """Oppgjøret har `forventet` I TILLEGG til `utfall` og `avvik`. Det
        er derfor det kan leses alene — og derfor `expected` hoerer hjemme
        paa oppgjørssiden ogsaa, ikke bare paa prediksjonen."""
        hoder = _hoder("nats-oppgjoer-metno.json")
        for nokkel in ("forventet", "utfall", "avvik"):
            self.assertIn(nokkel, hoder)
        self.assertIn("expected", _felt("settlement"))

    def test_freeze_strukturen_er_validert_selv_om_formen_er_streng(self):
        """Runde 3: jeg deklarerte `freeze` som object mens bussen sender
        STRENG — skjemaet ville avvist den ekte meldingen. Formen speiles i
        skjemaet; STRUKTUREN valideres her, ved aa parse den."""
        hoder = _hoder("nats-prediksjon-efc-fs8.json")
        self.assertIsInstance(hoder["frys"], str,
                              "bussen sender JSON-kodet streng, ikke objekt")
        frys = json.loads(hoder["frys"])
        self.assertEqual(set(frys), {"primary_freeze", "secondary_freeze"})
        for navn, blokk in frys.items():
            self.assertEqual(
                set(blokk),
                {"alpha", "sampler", "sha256_truncated", "timestamp_utc"},
                f"{navn} har andre noekler enn maalt")
            self.assertIsInstance(blokk["alpha"], float)
            for k in ("sampler", "sha256_truncated", "timestamp_utc"):
                self.assertIsInstance(blokk[k], str)
        self.assertEqual(_felt("prediction")["freeze"]["type"], "string")

    def test_ingen_tillatt_type_uten_maalt_forekomst(self):
        """Jeg deklarerte `ledetid_min` som integer|string og SKREV i
        beskrivelsen at begge var maalt. Begge maalte forekomster er
        strenger, og efc-fs8 har ikke feltet i det hele tatt — `integer`
        var en antakelse. Samme feilklasse som resten av okta.

        Generalisert: hver type skjemaet TILLATER for et felt skal ha
        minst en maalt forekomst blant fixturene."""
        TYPEMAP = {"str": "string", "int": "integer", "float": "number",
                   "bool": "boolean", "dict": "object", "list": "array"}
        observerte: dict[str, set[str]] = {}
        for filnavn, kart in (
                ("nats-prediksjon-metno.json", PREDiksjon_KART),
                ("nats-oppgjoer-metno.json", OPPGJOER_KART),
                ("nats-prediksjon-efc-fs8.json", FORSEGLET_KART)):
            hoder = _hoder(filnavn)
            for buss, felt in kart.items():
                if buss in hoder:
                    observerte.setdefault(felt, set()).add(
                        TYPEMAP.get(type(hoder[buss]).__name__, "ukjent"))
        for objekt in ("prediction", "settlement"):
            for felt, def_ in _felt(objekt).items():
                tillatte = def_.get("type")
                if isinstance(tillatte, str):
                    tillatte = [tillatte]
                if not isinstance(tillatte, list):
                    continue
                for t in tillatte:
                    self.assertIn(
                        t, observerte.get(felt, set()),
                        f"{objekt}.{felt} tillater '{t}', men ingen maalt "
                        f"fixture har den typen "
                        f"(observert: {sorted(observerte.get(felt, set()))})")

    def test_ingen_felt_uten_maalt_motpart(self):
        """`status` og `settled_at` stod i skjemaet mitt og finnes ikke i
        noen maalt kontrakt. Et felt vi har diktet opp validerer ingenting —
        det later som. Invarianten gjelder ALLE felt i begge objektene,
        ikke bare dem jeg husket aa sjekke."""
        for objekt, kart in (("prediction", PREDiksjon_KART | FORSEGLET_KART),
                             ("settlement", OPPGJOER_KART)):
            skjema_felt = set(_felt(objekt))
            maalte = set(kart.values())
            diktede = skjema_felt - maalte
            self.assertEqual(
                diktede, set(),
                f"{objekt}: felt uten maalt motpart: {sorted(diktede)}")


if __name__ == "__main__":
    unittest.main()
