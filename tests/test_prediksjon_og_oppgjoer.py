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
        node = next((n for n in _noder()
                     if n.get("prediction")), None)
        self.assertIsNotNone(node, "ingen node bærer en prediction")
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
        node = next(n for n in _noder() if n.get("prediction"))
        faktisk = node["prediction"]["expected"]
        if isinstance(faktisk, str):
            faktisk = json.loads(faktisk)
        self.assertEqual(faktisk, ventet)
        self.assertEqual(faktisk["fsigma8_efc"], 0.43)

    def test_arbiter_status_er_med(self):
        """At arbiteren venter er en DEL av prediksjonens tilstand —
        uten den ser en uavgjort prediksjon ut som en avgjort."""
        fixture = json.loads(FIXTUR.read_text(encoding="utf-8"))["hoder"]
        node = next(n for n in _noder() if n.get("prediction"))
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
