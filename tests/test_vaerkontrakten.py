"""The weather contract: the operational variant, mirrored from the bus.

Round-1 review of PR #467 found that I claimed to have mirrored the
weather contract and had not — I mirrored only the sealed research
variant. The prediction carried `sted`, `lat`, `lon`,
`horisont_bestilt_timer` and `observert`; the settlement carried
`forventet` IN ADDITION to `utfall` and `avvik`. Neither was in the
schema, and with `additionalProperties: false` a real weather message
would not have validated.

The test below is therefore written as a GENERAL invariant and not as a
list of the fields I happened to remember: every key in the measured
message must have a counterpart in the schema. That is the invariant that
catches the next field too, not just the ones I looked for today.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
SKJEMA = ROT / "schema" / "regime_node.schema.json"
FIXTURER = ROT / "tests" / "fixtures"

# Bus keys that are NOT contract, but routing: the stream uses them to
# send the message to the right place, and they describe the message
# itself — not the prediction or the outcome. They must therefore not go
# into RegimeNode.
RUTING = {"Nats-Msg-Id", "lag", "domene", "undertype"}

# Measured contract -> schema field. Used to verify that the mirroring
# actually covers every measured key.
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

# The SEALED variant (efc-fs8). Same top-level fields, but carries the
# research apparatus instead of location/horizon. That both variants
# exist is why the required lists contain only what they have in common.
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
        """The invariant: no measured key may fall outside the schema."""
        hoder = _hoder("nats-prediksjon-metno.json")
        skjema_felt = _felt("prediction")
        mangler = [k for k in hoder
                   if k not in RUTING and k not in PREDiksjon_KART]
        self.assertEqual(mangler, [],
                         f"measured keys without a schema field: {mangler}")
        for buss, felt in PREDiksjon_KART.items():
            self.assertIn(buss, hoder, f"{buss} disappeared from the fixture")
            self.assertIn(felt, skjema_felt, f"{felt} is missing from the schema")

    def test_hver_maalt_oppgjoersnoekkel_har_en_motpart(self):
        hoder = _hoder("nats-oppgjoer-metno.json")
        skjema_felt = _felt("settlement")
        mangler = [k for k in hoder
                   if k not in RUTING and k not in OPPGJOER_KART]
        self.assertEqual(mangler, [],
                         f"measured keys without a schema field: {mangler}")
        for buss, felt in OPPGJOER_KART.items():
            self.assertIn(buss, hoder, f"{buss} disappeared from the fixture")
            self.assertIn(felt, skjema_felt, f"{felt} is missing from the schema")

    def test_lat_og_lon_er_strenger_paa_bussen(self):
        """Measured: `lat` is "70.3554" — a string, not a number. If I mirror
        them as numbers, the schema rejects the real messages."""
        hoder = _hoder("nats-prediksjon-metno.json")
        self.assertIsInstance(hoder["lat"], str)
        self.assertIsInstance(hoder["lon"], str)
        for felt in ("latitude", "longitude"):
            self.assertEqual(_felt("prediction")[felt]["type"], "string",
                             f"{felt} must be a string — the bus sends a string")

    def test_oppgjoeret_baerer_begge_sider_av_sloeyfa(self):
        """The settlement has `forventet` IN ADDITION to `utfall` and
        `avvik`. That is why it can be read alone — and why `expected`
        belongs on the settlement side too, not only on the prediction."""
        hoder = _hoder("nats-oppgjoer-metno.json")
        for nokkel in ("forventet", "utfall", "avvik"):
            self.assertIn(nokkel, hoder)
        self.assertIn("expected", _felt("settlement"))

    def test_freeze_strukturen_er_validert_selv_om_formen_er_streng(self):
        """Round 3: I declared `freeze` as object while the bus sends a
        STRING — the schema would have rejected the real message. The form
        is mirrored in the schema; the STRUCTURE is validated here, by
        parsing it."""
        hoder = _hoder("nats-prediksjon-efc-fs8.json")
        self.assertIsInstance(hoder["frys"], str,
                              "the bus sends a JSON-encoded string, not an object")
        frys = json.loads(hoder["frys"])
        self.assertEqual(set(frys), {"primary_freeze", "secondary_freeze"})
        for navn, blokk in frys.items():
            self.assertEqual(
                set(blokk),
                {"alpha", "sampler", "sha256_truncated", "timestamp_utc"},
                f"{navn} has other keys than measured")
            self.assertIsInstance(blokk["alpha"], float)
            for k in ("sampler", "sha256_truncated", "timestamp_utc"):
                self.assertIsInstance(blokk[k], str)
        self.assertEqual(_felt("prediction")["freeze"]["type"], "string")

    def test_ingen_tillatt_type_uten_maalt_forekomst(self):
        """I declared `ledetid_min` as integer|string and WROTE in the
        description that both were measured. Both measured occurrences are
        strings, and efc-fs8 does not have the field at all — `integer` was
        an assumption. The same error class as the rest of this session.

        Generalised: every type the schema ALLOWS for a field must have at
        least one measured occurrence among the fixtures."""
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
                        TYPEMAP.get(type(hoder[buss]).__name__, "unknown"))
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
                        f"{objekt}.{felt} allows '{t}', but no measured "
                        f"fixture has that type "
                        f"(observed: {sorted(observerte.get(felt, set()))})")

    def test_ingen_felt_uten_maalt_motpart(self):
        """`status` and `settled_at` stood in my schema and exist in no
        measured contract. A field we made up validates nothing — it only
        pretends to. The invariant applies to ALL fields in both objects,
        not just the ones I remembered to check."""
        for objekt, kart in (("prediction", PREDiksjon_KART | FORSEGLET_KART),
                             ("settlement", OPPGJOER_KART)):
            skjema_felt = set(_felt(objekt))
            maalte = set(kart.values())
            diktede = skjema_felt - maalte
            self.assertEqual(
                diktede, set(),
                f"{objekt}: fields without a measured counterpart: {sorted(diktede)}")


if __name__ == "__main__":
    unittest.main()
