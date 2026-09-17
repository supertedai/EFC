"""Synlighet: hva av atlaset skal ut på GitHub Pages — og hva skal ikke.

Målt 2026-09-17 mot origin/main: `docs/efc-atlas/atlas.html` (generert fra
`schema/regime_nodes.jsonld` via `data.mjs`) ligger LIVE på
supertedai.github.io/EFC/efc-atlas/atlas.html og inneholder HELE atlaset:

    efc.selv.atlas, efc.selv.skjema, efc.selv.paradigme_tid,
    efc.selv.paradigme_masse        ← atlasets selvreferanse
    batteri.celle/.lading/.buffer/.inverter
      der measure.measurer sier rett ut «LiFePO4-BMS (privat anlegg)»
    «victron» fem ganger

Det er ikke en hypotetisk risiko. Det laa ute da dette ble maalt.

Atlaset skal fortsatt vaere ETT atlas — kryssdomenet er hele poenget, og
`obs.fsigma8` gir bare mening sammen med `efc.selv.skjema`. Det er
PUBLISERINGEN som skal filtrere, ikke kartet som skal deles.

Derfor baerer hver node `synlighet` (offentlig | intern), og generatoren
skriver bare de offentlige til data.mjs. Filteret skal vaere DEKLARERT per
node — ikke en skjult regel i generatoren — fordi en node som forsvinner
uten at noen ser hvorfor, er samme feilklasse som alt annet her.
"""
import json
import re
import unittest
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
JSONLD = ROT / "schema" / "regime_nodes.jsonld"
SKJEMA = ROT / "schema" / "regime_node.schema.json"
DATA_MJS = ROT / "docs" / "efc-atlas" / "atlas" / "data.mjs"

#: Regel 16: et offentlig artefakt bærer feltkoder, tidsstempel og
#: snapshot-markør — aldri site-identitet eller privat kontekst.
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
        """Uten feltet kan en node havne i public ved uhell — og en node
        som mangler feltet er ikke «sannsynligvis offentlig»."""
        mangler = [n["id"] for n in _noder()
                   if n.get("synlighet") not in ("offentlig", "intern")]
        self.assertEqual(mangler, [],
                         f"noder uten gyldig synlighet: {mangler}")

    def test_skjemaet_deklarerer_synlighet(self):
        """Et felt som ikke staar i skjemaet finnes ikke — `additionalProperties:
        false` avviser det, og da er hele mekanismen en illusjon."""
        s = json.loads(SKJEMA.read_text(encoding="utf-8"))
        props = s["$defs"]["RegimeNode"]["properties"]
        self.assertIn("synlighet", props,
                      "synlighet mangler i RegimeNode-skjemaet")
        enum = props["synlighet"].get("enum", [])
        self.assertEqual(sorted(enum), ["intern", "offentlig"])

    def test_generatoren_skriver_ikke_interne_noder(self):
        """data.mjs er filen Pages faktisk serverer."""
        interne = [n["id"] for n in _noder()
                   if n.get("synlighet") == "intern"]
        self.assertTrue(interne, "ingen interne noder — filteret er uten "
                                 "virkning og testen beviser ingenting")
        data = DATA_MJS.read_text(encoding="utf-8")
        lekkasje = [i for i in interne if i in data]
        self.assertEqual(lekkasje, [],
                         f"interne noder staar i data.mjs: {lekkasje}")

    def test_ingen_offentlig_node_baerer_privat_identitet(self):
        """Regel 16, håndhevet. Denne fanger ogsaa eksisterende brudd."""
        brudd = []
        for n in _noder():
            if n.get("synlighet") != "offentlig":
                continue
            t = json.dumps(n, ensure_ascii=False).lower()
            for f in FORBUDT_I_OFFENTLIG:
                if f in t:
                    brudd.append((n["id"], f))
        self.assertEqual(brudd, [],
                         f"offentlige noder med privat identitet: {brudd}")

    def test_interne_noder_er_ikke_med_i_kapitlene(self):
        """Filtreringen skal skje FOER kapitlene bygges — en intern node som
        fortsatt teller i et kapittel avslorer seg i reveal-lista."""
        interne = {n["id"] for n in _noder()
                   if n.get("synlighet") == "intern"}
        data = DATA_MJS.read_text(encoding="utf-8")
        for i in sorted(interne):
            self.assertNotIn(f'"{i}"', data,
                             f"{i} staar i data.mjs")

    def test_offentlig_visning_teller_det_som_faktisk_publiseres(self):
        """SYSTEM.md sa «82 nodes» mens data.mjs hadde 73. Et hardkodet tall
        som blir staaende lenger enn kilden sin lyver — og røper i tillegg
        at noe er holdt tilbake, som er det motsatte av poenget."""
        offentlige = sum(1 for n in _noder()
                         if n.get("synlighet") == "offentlig")
        tekst = (ROT / "docs" / "efc-atlas" / "SYSTEM.md").read_text(
            encoding="utf-8")
        tall = {int(m) for m in re.findall(r"(\d+) nodes", tekst)}
        self.assertEqual(
            tall, {offentlige},
            f"SYSTEM.md oppgir {sorted(tall)} noder; publisert er "
            f"{offentlige}")


if __name__ == "__main__":
    unittest.main()
