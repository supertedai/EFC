"""Prediksjon og oppgjør i atlaset — kontrakten speiles fra bussen.

Målt 2026-09-17 på NATS-bussen (emne kosmos.kosmologi.prediksjon.efc-fs8,
seq 31058): prediksjonskontrakten finnes ALLEREDE, komplett, med forseglet
DOI, SHA256, frys, kriterium, toleranseregel og arbiter-status.

Atlaset har null noder som bærer den. Problemet er ikke at oppgjøret
mangler — det er at bussen gjør opp og kartet ikke ser det. Vær-domenet
hadde 77 112 oppgjørsmeldinger med forventet/utfall/avvik mens atlaset
hadde null.

Derfor speiles kontrakten her, ikke oppfunnet på nytt. Fixturen under er
den målte meldingen, felt for felt — en test som bare sjekker «feltet
finnes» ville ikke skilt en ekte speiling fra en oppdiktet.
"""
import json
import unittest
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
JSONLD = ROT / "schema" / "regime_nodes.jsonld"
SKJEMA = ROT / "schema" / "regime_node.schema.json"
FIXTUR = ROT / "tests" / "fixtures" / "nats-prediksjon-efc-fs8.json"


def _prop(navn: str) -> dict:
    s = json.loads(SKJEMA.read_text(encoding="utf-8"))
    return s["$defs"]["RegimeNode"]["properties"].get(navn, {})


def _noder():
    return json.loads(JSONLD.read_text(encoding="utf-8"))["nodes"]



def _node_ved_id(node_id: str):
    """Hent en node VED ID — ikke «den foerste som tilfeldigvis baerer X».

    Maalt av orchestrator 2026-09-17: tre tester i denne fila fant maalet
    sitt med `next(n for n in _noder() if n.get("prediction"))`. Med en ny
    prediction-baerer plassert FOERST i nodearrayet falt alle tre; den samme
    noden plassert SIST ga 6 passed. Bare POSISJONEN skilte.

    Det betyr at testene paastod «den forseglede kontrakten er speilet» og
    maalte «den foerste noden som tilfeldigvis baerer en prediction». Det er
    samme feilklasse som resten av huset verner mot: instrumentet svarer paa
    et nabospoersmaal.

    Pinneren er noedvendig FOER en andre prediction-baerer finnes — etterpaa
    er feilen usynlig, fordi den foerste noden da er den riktige av slump.
    """
    for n in _noder():
        if n.get("id") == node_id:
            return n
    raise AssertionError(
        f"noden `{node_id}` finnes ikke — testen maaler feil atlas")


class TestPrediksjonOgOppgjoer(unittest.TestCase):

    def test_skjemaet_deklarerer_prediction_og_settlement(self):
        for navn in ("prediction", "settlement"):
            p = _prop(navn)
            self.assertTrue(p, f"{navn} mangler i RegimeNode")
            self.assertEqual(p.get("type"), "object")
            self.assertFalse(p.get("additionalProperties", True),
                             f"{navn} maa lukke sine egne felt")

    def test_correlation_er_nokkelen_paa_begge_sider(self):
        """Uten en felles, stabil noekkel er koblingen mellom prediksjon og
        oppgjoer en påstand om at noen husker hva som hoerte sammen."""
        for navn in ("prediction", "settlement"):
            self.assertIn("correlation", _prop(navn).get("required", []),
                          f"correlation mangler i required for {navn}")

    def test_den_forseglede_prediksjonen_staar_paa_growth_noden(self):
        """Speilingen: noden skal bære den målte kontrakten, ikke en fri
        tekst som ligner."""
        fixture = json.loads(FIXTUR.read_text(encoding="utf-8"))["hoder"]
        node = _node_ved_id("efc.growth_engine")
        self.assertIsNotNone(node.get("prediction"),
                             "efc.growth_engine bærer ingen prediction")
        p = node["prediction"]
        for felt in ("observable", "sealed_doi", "sealing_sha256",
                     "criterion", "tolerance_rule", "correlation"):
            self.assertIn(felt, p, f"{felt} mangler i nodens prediction")
        self.assertEqual(p["observable"], fixture["observabel"])
        self.assertEqual(p["sealed_doi"], fixture["forseglet_doi"])
        self.assertEqual(p["sealing_sha256"], fixture["forsegling_sha256"])
        self.assertEqual(p["criterion"], fixture["kriterium"])
        self.assertEqual(p["tolerance_rule"], fixture["toleranse_regel"])

    def test_expected_er_speilet_ikke_avskrevet(self):
        """`forventet` sendes som JSON-kodet streng paa bussen. Speilingen
        skal baere TALLENE — sammenlign parset, saa en avskrift med feil
        tall feller."""
        fixture = json.loads(FIXTUR.read_text(encoding="utf-8"))["hoder"]
        ventet = json.loads(fixture["forventet"])
        node = _node_ved_id("efc.growth_engine")
        faktisk = node["prediction"]["expected"]
        if isinstance(faktisk, str):
            faktisk = json.loads(faktisk)
        self.assertEqual(faktisk, ventet)
        self.assertEqual(faktisk["fsigma8_efc"], 0.43)

    def test_arbiter_status_er_med(self):
        """At arbiteren venter er en DEL av prediksjonens tilstand —
        uten den ser en uavgjort prediksjon ut som en avgjort."""
        fixture = json.loads(FIXTUR.read_text(encoding="utf-8"))["hoder"]
        node = _node_ved_id("efc.growth_engine")
        p = node["prediction"]
        self.assertEqual(p.get("arbiter_waiting_for"),
                         fixture["arbiter_venter_paa"])

    def test_alle_noder_validerer_fortsatt(self):
        from jsonschema import Draft202012Validator
        s = json.loads(SKJEMA.read_text(encoding="utf-8"))
        v = Draft202012Validator({"$defs": s["$defs"],
                                  "$ref": "#/$defs/RegimeNode"})
        feil = [(n["id"], e.message[:80])
                for n in _noder() for e in v.iter_errors(n)]
        self.assertEqual(feil, [], f"valideringsfeil: {feil[:3]}")


if __name__ == "__main__":
    unittest.main()


class TestSloeyfaErLukketDerDenErMaalt(unittest.TestCase):
    """En node som SPEILER en maalt sloeyfe maa baere BEGGE sider.

    Uavhengig review av #484 fant at `settlement` kunne fjernes fra
    `verden.vaer` uten at en eneste test reagerte (50 passed paa mutanten).
    Sjekjemaet kan ikke hjelpe: `settlement` er valgfritt, og det MAА vaere
    valgfritt — `efc.growth_engine` baerer en prediction som venter paa DESI
    DR2 og skal IKKE ha et oppgjoer.

    Men naar en node foerst speiler en maalt sloeyfe, er de to sidene ett
    objekt. Da er det ikke et skjemasporsmaal, det er en invariant.
    """

    def test_verden_vaer_baerer_begge_sider(self):
        n = _node_ved_id("verden.vaer")
        self.assertIn("prediction", n, "verden.vaer mistet prediksjonen")
        self.assertIn("settlement", n,
                      "verden.vaer speiler en maalt sloeyfe — oppgjoeret er "
                      "ikke valgfritt naar sloeyfa faktisk har loept")

    def test_de_to_sidene_deler_korrelasjon(self):
        """Uten felles noekkel er de to objektene loesrevne, ikke en sloeyfe."""
        n = _node_ved_id("verden.vaer")
        self.assertEqual(n["prediction"]["correlation"],
                         n["settlement"]["correlation"],
                         "prediksjon og oppgjoer peker ikke paa samme maaling")

    def test_oppgjoeret_baerer_et_faktisk_utfall(self):
        """Et settlement uten utfall er en paastand om at noe ble maalt."""
        n = _node_ved_id("verden.vaer")
        s = n["settlement"]
        for felt in ("outcome", "outcome_source", "deviation"):
            self.assertTrue(s.get(felt), f"oppgjoeret mangler {felt}")
        self.assertNotEqual(s["outcome"], n["prediction"]["expected"],
                            "utfall og forventning er identiske — da er det "
                            "ikke maalt, det er speilet to ganger")


FIXTUR_PAR = ROT / "tests" / "fixtures" / "nats-vaerparet-metno.json"


class TestTheWeatherLoopIsMirroredFromAMeasuredPair(unittest.TestCase):
    """The verden.vaer node mirrors a loop that actually ran on the bus.

    The mirror is checked against the TWO measured messages it was taken
    from, not against prose about them. The fixture is read back from the
    bus (stream VERDEN_PROGNOSE, seq 167904 and 168744) and carries the
    provenance of that read, so a transcribed number cannot pass: both
    sides are parsed and the NUMBERS are compared — the discipline of
    test_expected_er_speilet_ikke_avskrevet, one level out.

    Measured while reading the pair: the SAME correlation key is carried
    by two forecasts for this station, one with a 1-hour horizon and one
    with 24 hours. The correlation key alone therefore does not identify a
    forecast, and the node has to carry the one the outcome settles
    against. That choice is pinned here too.
    """

    @staticmethod
    def _parset(value):
        return json.loads(value) if isinstance(value, str) else value

    def _fixture(self) -> dict:
        return json.loads(FIXTUR_PAR.read_text(encoding="utf-8"))

    def test_the_two_sides_share_one_measured_correlation(self):
        f = self._fixture()
        p, o = f["prediksjon"]["hoder"], f["oppgjoer"]["hoder"]
        self.assertEqual(
            p["korrelasjon"], o["korrelasjon"],
            "the fixture is not one pair: the two messages disagree on the key")
        n = _node_ved_id("verden.vaer")
        self.assertEqual(n["prediction"]["correlation"], p["korrelasjon"])
        self.assertEqual(n["settlement"]["correlation"], o["korrelasjon"])

    def test_expected_is_parsed_from_the_measured_message(self):
        f = self._fixture()
        n = _node_ved_id("verden.vaer")
        measured = json.loads(f["prediksjon"]["hoder"]["forventet"])
        self.assertEqual(self._parset(n["prediction"]["expected"]), measured)
        self.assertEqual(self._parset(n["settlement"]["expected"]), measured)

    def test_the_outcome_side_is_the_measured_one(self):
        f = self._fixture()
        o = f["oppgjoer"]["hoder"]
        s = _node_ved_id("verden.vaer")["settlement"]
        self.assertTrue(s.get("outcome_source"),
                        "settlement without an outcome source is a claim "
                        "that something was measured")
        self.assertEqual(s["outcome_source"], o["utfall_kilde"])
        self.assertEqual(self._parset(s["outcome"]), json.loads(o["utfall"]))
        self.assertEqual(self._parset(s["deviation"]), json.loads(o["avvik"]))

    def test_the_mirrored_forecast_is_the_one_the_outcome_settles(self):
        """Lead time separates the two forecasts that share the key.

        1-hour horizon: 89 min. 24-hour horizon: 1469 min. Only the short
        one has an outcome, so it is the one the node must carry — and the
        field that tells them apart has to be on the node, or the mirror
        would look right while pointing at the other forecast.
        """
        f = self._fixture()
        p = f["prediksjon"]["hoder"]
        pred = _node_ved_id("verden.vaer")["prediction"]
        self.assertEqual(pred["lead_time_minutes"], p["ledetid_min"])
        self.assertEqual(pred["valid_for"], p["gyldig_for"])
        self.assertNotEqual(
            pred["lead_time_minutes"], "1469",
            "the node mirrors the 24-hour forecast, which has no outcome")

