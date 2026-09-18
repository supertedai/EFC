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
        self.assertEqual(p["tolerance_rule"], fixture["toleranse_regel"])

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
