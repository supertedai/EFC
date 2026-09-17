"""Emne-kontrakten for arbiterens dom: produsent og konsument skal peke
på SAMME emne — og det emnet skal fanges av en strøm.

Målt 2026-09-17: koden var splittet mot seg selv.

    payload()["emne"]            "kosmos.kosmologi.utfall.efc-fs8-arbiter"
    OPPGJOER_EMNE (publiserer)   "kosmos.kosmologi.oppgjoer.efc-fs8-arbiter"
    nats-koblingskart.md         "...utfall..."

To halvdeler, hver med sin test, som passerte fordi hver test bare så sin
egen side. Ingen test bandt dem sammen — derfor kunne de drifte.

OG DET AVGJØRENDE: `utfall` fanges av INGEN strøm. De fem strømmene fanger
`observasjon, prediksjon, oppgjoer, tilstand, hendelse, diskusjon`. Et emne
uten et fanget lag-ord får `+OK` fra serveren og forsvinner sporløst —
ingen feil, ingen logg (husets byggeregel 26).

Arbiteren er latent nå (`arbiter: "nei"`, venter på DESI DR2), men den
feller dommen hele valideringskjeden venter på. Feilen ville rammet i
stillhet i oktober.
"""
import importlib.util
import sys
import unittest
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT))

# Lag-ordene strømmene FAKTISK fanger. Målt mot JetStream 2026-09-17:
#   VERDEN_OBS        observasjon
#   VERDEN_TILSTAND   tilstand
#   VERDEN_TOLKET     hendelse, diskusjon
#   VERDEN_PROGNOSE   prediksjon, oppgjoer
#   OPUS_SELV         prediksjon, oppgjoer, tilstand, hendelse
# Endres strømmene, skal denne lista oppdateres MED en ny måling — ikke
# ved å gjette. Testen under feiler hvis et emne bruker et ord som ikke
# står her.
FANGEDE_LAG = {"observasjon", "prediksjon", "oppgjoer", "tilstand",
               "hendelse", "diskusjon"}


def _les_konstant(sti: Path, navn: str) -> str:
    tekst = sti.read_text(encoding="utf-8")
    for linje in tekst.splitlines():
        if linje.startswith(f"{navn} = "):
            return linje.split("=", 1)[1].strip().strip('"').strip("'")
    raise AssertionError(f"{navn} ikke funnet i {sti}")


class TestArbiterEmneKontrakt(unittest.TestCase):

    def test_konsumentens_emne_fanges_av_en_stroem(self):
        """Den harde proven: et lag-ord strømmene faktisk fanger."""
        emne = _les_konstant(
            ROT / "scripts" / "maintenance" / "arbiter_vakt_kjoer.py",
            "OPPGJOER_EMNE")
        lag = emne.split(".")[2]
        self.assertIn(lag, FANGEDE_LAG,
                      f"«{lag}» fanges av ingen strøm — meldingen ville "
                      f"fått +OK og forsvunnet sporløst")

    def test_payloadens_emne_er_samme_som_konsumentens(self):
        """Feltet `emne` inne i payloaden sier hvor meldingen hører hjemme.
        Sier det noe annet enn den faktiske publiseringen, lyver payloaden."""
        konsument = _les_konstant(
            ROT / "scripts" / "maintenance" / "arbiter_vakt_kjoer.py",
            "OPPGJOER_EMNE")
        for modul in ("efc_inference/arbiter/sealed_fs8.py",
                      "efc_inference/arbiter/rapid_response.py"):
            tekst = (ROT / modul).read_text(encoding="utf-8")
            emner = {linje.split('"')[3]
                     for linje in tekst.splitlines()
                     if '"emne":' in linje and '"' in linje}
            self.assertTrue(emner, f"ingen emne-linje i {modul}")
            for e in emner:
                self.assertEqual(
                    e, konsument,
                    f"{modul} peker på {e}, konsumenten publiserer til "
                    f"{konsument} — de to halvdelene har driftet fra "
                    f"hverandre")

    def test_dokumentasjonen_nevner_ikke_det_ufangede_emnet(self):
        """Koblingskartet er kontrakten eksterne lesere bruker."""
        kart = (ROT / "docs" / "nats-koblingskart.md").read_text(
            encoding="utf-8")
        self.assertNotIn(
            "kosmos.kosmologi.utfall.efc-fs8-arbiter", kart,
            "kartet dokumenterer et emne ingen strøm fanger")


if __name__ == "__main__":
    unittest.main()
