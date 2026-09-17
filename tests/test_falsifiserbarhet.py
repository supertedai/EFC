"""Hvilke noder KAN felles — og hvilke kan det ikke, med grunn.

Maalt 2026-09-17: 0 av 74 offentlige noder bar en falsifikator. Men «0 av
74» maalte feil ting. 47 av de 74 er ikke EFC-paastander i det hele tatt:

    h2o, lys, optikk, regnbue, kjemi   etablert fysikk — ikke vaare
    obs.*                              observasjoner
    homo.*                             etablert biologi
    verden.*, kosmos.jord.vulkan       instrumenter — de MAALER

En instrument-node har ingen falsifikator fordi den ikke paastaar noe.
Den maaler. Den kan vaere feilkalibrert, men det er en annen feil.

De 27 `efc.*`-nodene er de som paastaar noe EFC-spesifikt. Alle 27 bar
`sannhetsstatus: hypotese` — og en hypotese uten falsifikator har ikke
sagt hva den utelukker. Denne filen holder skillet. Uten den smelter
«kan felles» og «er vaart» sammen til ett tall, og det tallet lyver.
"""
from __future__ import annotations

import json
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
NODER = ROT / "schema" / "regime_nodes.jsonld"

#: Prefikser som IKKE er EFC-paastander, hver med sin grunn. Et prefiks
#: som ikke staar her betyr en ny type node ingen har vurdert.
IKKE_EFC_PAASTAND = {
    "h2o": "etablert fysikk (IAPWS-95) — ikke vaar paastand",
    "lys": "observasjon",
    "optikk": "etablert fysikk (NIST)",
    "regnbue": "etablert fysikk",
    "kjemi": "etablert struktur (IUPAC)",
    "obs": "observasjon — ikke en modellpaastand",
    "homo": "etablert biologi",
    "verden": "instrument — maaler, paastaar ikke",
    "kosmos": "instrument — maaler, paastaar ikke",
}


def _offentlige():
    return [n for n in json.loads(NODER.read_text(encoding="utf-8"))["nodes"]
            if n.get("synlighet") == "offentlig"]


class TestFalsifiserbarhet:

    def test_hver_efc_paastand_kan_felles(self):
        mangler = [n["id"] for n in _offentlige()
                   if n["id"].startswith("efc.") and "ville_falsifisere" not in n]
        assert mangler == [], f"EFC-paastander uten falsifikator: {mangler}"

    def test_falsifikatoren_sier_mer_enn_paastanden(self):
        """«Ville feile om den er feil» er ikke en falsifikator.

        De fire som fantes foer denne testen hadde ALLE identisk tekst:
        «Selvanvendelsen ville feile om atlaset ikke lot seg beskrive av
        sitt eget skjema.» Det er en paastand om ATLASET, ikke om noden —
        og den var kopiert til fire noder. En falsifikator maa vaere
        nodens EGEN.
        """
        tekster = [n["ville_falsifisere"] for n in _offentlige()
                   if "ville_falsifisere" in n]
        duplikater = {t for t in tekster if tekster.count(t) > 1}
        assert duplikater == set(), (
            f"identisk falsifikator paa flere noder: {duplikater}")

    def test_falsifikatoren_er_lang_nok_til_aa_bety_noe(self):
        korte = [n["id"] for n in _offentlige() if "ville_falsifisere" in n
                 and len(n["ville_falsifisere"]) < 40]
        assert korte == [], f"for korte falsifikatorer: {korte}"

    def test_de_ikke_efc_nodene_er_kjent_klassifisert(self):
        """De uten falsifikator skal falle i en KJENT kategori."""
        ukjente = {n["id"].split(".")[0] for n in _offentlige()
                   if not n["id"].startswith("efc.")
                   and "ville_falsifisere" not in n}
        ukjente -= set(IKKE_EFC_PAASTAND)
        assert ukjente == set(), (
            f"nye prefikser uten vurdering: {sorted(ukjente)}")

    def test_tallet_er_27_av_74(self):
        """Tallet skal vaere kjent, ikke bare overraskende.

        Gikk det ned, mistet en EFC-node sin falsifikator. Gikk det opp,
        er en node omklassifisert — og da skal noen ha bestemt det.
        """
        off = _offentlige()
        kan = sum(1 for n in off if "ville_falsifisere" in n)
        assert len(off) == 74, f"offentlige endret: {len(off)}"
        assert kan == 27, f"kan felles: {kan} — forventet 27"
