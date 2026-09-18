"""Visibility: what of the atlas goes out to GitHub Pages — and what does not.

Measured 2026-09-17 against origin/main: `docs/efc-atlas/atlas.html` (generated
from `schema/regime_nodes.jsonld` via `data.mjs`) sits LIVE at
supertedai.github.io/EFC/efc-atlas/atlas.html and contains the WHOLE atlas:

    efc.selv.atlas, efc.selv.skjema, efc.selv.paradigme_tid,
    efc.selv.paradigme_masse        <- the atlas's self-reference
    batteri.celle/.lading/.buffer/.inverter
      where measure.measurer says outright "LiFePO4-BMS (privat anlegg)"
    "victron" five times

This is not a hypothetical risk. It was live when this was measured.

The atlas must still be ONE atlas — the cross-domain is the whole point, and
`obs.fsigma8` only makes sense together with `efc.selv.skjema`. It is the
PUBLICATION that must filter, not the map that must be split.

Therefore every node carries `synlighet` (offentlig | intern), and the
generator writes only the public ones to data.mjs. The filter must be DECLARED
per node — not a hidden rule in the generator — because a node that disappears
without anyone seeing why is the same error class as everything else here.
"""
import json
import re
import unittest
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
JSONLD = ROT / "schema" / "regime_nodes.jsonld"
SKJEMA = ROT / "schema" / "regime_node.schema.json"
DATA_MJS = ROT / "docs" / "efc-atlas" / "atlas" / "data.mjs"

#: Rule 16: a public artefact carries field codes, timestamps and a snapshot
#: marker — never site identity or private context.
FORBUDT_I_OFFENTLIG = [
    "privat anlegg",
    "morten",
    "joakim",
    "byopus",
    "energy rent",
    "vennesla",
    "longyearbyen",
]


def _noder():
    return json.loads(JSONLD.read_text(encoding="utf-8"))["nodes"]


class TestAtlasSynlighet(unittest.TestCase):

    def test_alle_noder_har_synlighet(self):
        """Without the field a node can land in public by accident — and a node
        missing the field is not "probably public"."""
        mangler = [n["id"] for n in _noder()
                   if n.get("synlighet") not in ("offentlig", "intern")]
        self.assertEqual(mangler, [],
                         f"nodes without valid visibility: {mangler}")

    def test_skjemaet_deklarerer_synlighet(self):
        """A field that is not in the schema does not exist —
        `additionalProperties: false` rejects it, and then the whole
        mechanism is an illusion."""
        s = json.loads(SKJEMA.read_text(encoding="utf-8"))
        props = s["$defs"]["RegimeNode"]["properties"]
        self.assertIn("synlighet", props,
                      "synlighet is missing from the RegimeNode schema")
        enum = props["synlighet"].get("enum", [])
        self.assertEqual(sorted(enum), ["intern", "offentlig"])

    def test_generatoren_skriver_ikke_interne_noder(self):
        """data.mjs is the file Pages actually serves."""
        interne = [n["id"] for n in _noder()
                   if n.get("synlighet") == "intern"]
        self.assertTrue(interne, "no internal nodes — the filter has no "
                                 "effect and the test proves nothing")
        data = DATA_MJS.read_text(encoding="utf-8")
        lekkasje = [i for i in interne if i in data]
        self.assertEqual(lekkasje, [],
                         f"internal nodes are in data.mjs: {lekkasje}")

    def test_ingen_offentlig_node_baerer_privat_identitet(self):
        """Rule 16, enforced. This one also catches existing violations."""
        brudd = []
        for n in _noder():
            if n.get("synlighet") != "offentlig":
                continue
            t = json.dumps(n, ensure_ascii=False).lower()
            for f in FORBUDT_I_OFFENTLIG:
                if f in t:
                    brudd.append((n["id"], f))
        self.assertEqual(brudd, [],
                         f"public nodes with a private identity: {brudd}")

    def test_interne_noder_er_ikke_med_i_kapitlene(self):
        """The filtering must happen BEFORE the chapters are built — an
        internal node still counted in a chapter gives itself away in the
        reveal list."""
        interne = {n["id"] for n in _noder()
                   if n.get("synlighet") == "intern"}
        data = DATA_MJS.read_text(encoding="utf-8")
        for i in sorted(interne):
            self.assertNotIn(f'"{i}"', data,
                             f"{i} is in data.mjs")

    def test_offentlig_visning_teller_det_som_faktisk_publiseres(self):
        """SYSTEM.md said "82 nodes" while data.mjs had 73. A hardcoded number
        that outlives its source lies — and additionally reveals that something
        was held back, which is the opposite of the point."""
        offentlige = sum(1 for n in _noder()
                         if n.get("synlighet") == "offentlig")
        tekst = (ROT / "docs" / "efc-atlas" / "SYSTEM.md").read_text(
            encoding="utf-8")
        tall = {int(m) for m in re.findall(r"(\d+) nodes", tekst)}
        self.assertEqual(
            tall, {offentlige},
            f"SYSTEM.md states {sorted(tall)} nodes; published is "
            f"{offentlige}")


if __name__ == "__main__":
    unittest.main()
