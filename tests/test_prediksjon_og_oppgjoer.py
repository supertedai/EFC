"""Prediction and settlement in the atlas — the contract mirrors the bus.

Measured 2026-09-17 on the NATS bus (subject
kosmos.kosmologi.prediksjon.efc-fs8, seq 31058): the prediction contract
already exists, complete, with sealed DOI, SHA256, freeze, criterion,
tolerance rule and arbiter status.

The atlas has zero nodes carrying it. The problem is not that the
settlement is missing — it is that the bus settles and the map does not
see it. The weather domain had 77 112 settlement messages with
expected/outcome/deviation while the atlas had zero.

That is why the contract is mirrored here, not invented anew. The fixture
below is the measured message, field for field — a test that only checks
"the field exists" would not tell a real mirroring from a fabricated one.
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
    """Fetch a node BY ID — not "the first one that happens to carry X".

    Measured by the orchestrator 2026-09-17: three tests in this file found
    their target with `next(n for n in _noder() if n.get("prediction"))`. With
    a new prediction carrier placed FIRST in the node array all three fell;
    the same node placed LAST gave 6 passed. Only the POSITION differed.

    That means the tests claimed "the sealed contract is mirrored" and
    measured "the first node that happens to carry a prediction". It is the
    same error class the rest of the house guards against: the instrument
    answers a neighbouring question.

    The pin is necessary BEFORE a second prediction carrier exists —
    afterwards the error is invisible, because the first node is then the
    right one by chance.
    """
    for n in _noder():
        if n.get("id") == node_id:
            return n
    raise AssertionError(
        f"the node `{node_id}` does not exist — the test measures the wrong atlas")


class TestPrediksjonOgOppgjoer(unittest.TestCase):

    def test_skjemaet_deklarerer_prediction_og_settlement(self):
        for navn in ("prediction", "settlement"):
            p = _prop(navn)
            self.assertTrue(p, f"{navn} is missing from RegimeNode")
            self.assertEqual(p.get("type"), "object")
            self.assertFalse(p.get("additionalProperties", True),
                             f"{navn} must close its own fields")

    def test_correlation_er_nokkelen_paa_begge_sider(self):
        """Without a shared, stable key the link between prediction and
        settlement is a claim that someone remembers what belonged together."""
        for navn in ("prediction", "settlement"):
            self.assertIn("correlation", _prop(navn).get("required", []),
                          f"correlation is missing from required for {navn}")

    def test_den_forseglede_prediksjonen_staar_paa_growth_noden(self):
        """The mirroring: the node must carry the measured contract, not a free
        text that resembles it."""
        fixture = json.loads(FIXTUR.read_text(encoding="utf-8"))["hoder"]
        node = _node_ved_id("efc.growth_engine")
        self.assertIsNotNone(node.get("prediction"),
                             "efc.growth_engine carries no prediction")
        p = node["prediction"]
        for felt in ("observable", "sealed_doi", "sealing_sha256",
                     "criterion", "tolerance_rule", "correlation"):
            self.assertIn(felt, p, f"{felt} is missing from the node's prediction")
        self.assertEqual(p["observable"], fixture["observabel"])
        self.assertEqual(p["sealed_doi"], fixture["forseglet_doi"])
        self.assertEqual(p["sealing_sha256"], fixture["forsegling_sha256"])
        self.assertEqual(p["criterion"], fixture["kriterium"])
        # The fixture is the MEASURED Norwegian message, frozen. The producer
        # (the atlas) now speaks English, so the mirror is pinned to the
        # producer's text — and the fixture is still pinned as an unedited
        # measured message.
        self.assertEqual(p["tolerance_rule"],
                         "within 1 sigma of the DR2 measurement's OWN "
                         "uncertainty, not a fixed band")
        self.assertIn("EGEN usikkerhet", fixture["toleranse_regel"],
                      "the fixture is the measured message — it is not edited "
                      "by hand")

    def test_expected_er_speilet_ikke_avskrevet(self):
        """`forventet` is sent as a JSON-encoded string on the bus. The mirroring
        must carry the NUMBERS — compare parsed, so that a transcription with
        the wrong numbers falls."""
        fixture = json.loads(FIXTUR.read_text(encoding="utf-8"))["hoder"]
        ventet = json.loads(fixture["forventet"])
        node = _node_ved_id("efc.growth_engine")
        faktisk = node["prediction"]["expected"]
        if isinstance(faktisk, str):
            faktisk = json.loads(faktisk)
        self.assertEqual(faktisk, ventet)
        self.assertEqual(faktisk["fsigma8_efc"], 0.43)

    def test_arbiter_status_er_med(self):
        """That the arbiter waits is PART of the prediction's state —
        without it an undecided prediction looks like a decided one."""
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
        self.assertEqual(feil, [], f"validation errors: {feil[:3]}")


if __name__ == "__main__":
    unittest.main()


class TestSloeyfaErLukketDerDenErMaalt(unittest.TestCase):
    """A node that MIRRORS a measured loop must carry BOTH sides.

    Independent review of #484 found that `settlement` could be removed from
    `verden.vaer` without a single test reacting (50 passed on the mutant).
    The schema cannot help: `settlement` is optional, and it MUST be
    optional — `efc.growth_engine` carries a prediction waiting for DESI
    DR2 and must NOT have a settlement.

    But once a node mirrors a measured loop, the two sides are one object.
    Then it is not a schema question, it is an invariant.
    """

    def test_verden_vaer_baerer_begge_sider(self):
        n = _node_ved_id("verden.vaer")
        self.assertIn("prediction", n, "verden.vaer lost the prediction")
        self.assertIn("settlement", n,
                      "verden.vaer mirrors a measured loop — the settlement is "
                      "not optional once the loop has actually run")

    def test_de_to_sidene_deler_korrelasjon(self):
        """Without a shared key the two objects are detached, not a loop."""
        n = _node_ved_id("verden.vaer")
        self.assertEqual(n["prediction"]["correlation"],
                         n["settlement"]["correlation"],
                         "prediction and settlement do not point at the same measurement")

    def test_oppgjoeret_baerer_et_faktisk_utfall(self):
        """A settlement without an outcome is a claim that something was measured."""
        n = _node_ved_id("verden.vaer")
        s = n["settlement"]
        for felt in ("outcome", "outcome_source", "deviation"):
            self.assertTrue(s.get(felt), f"the settlement is missing {felt}")
        self.assertNotEqual(s["outcome"], n["prediction"]["expected"],
                            "outcome and expectation are identical — then it is not "
                            "measured, it is mirrored twice")


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

