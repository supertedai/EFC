"""The subject contract for the arbiter's verdict: producer and consumer
must point at the SAME subject — and that subject must be caught by a
stream.

Measured 2026-09-17: the code was split against itself.

    payload()["emne"]            "kosmos.kosmologi.utfall.efc-fs8-arbiter"
    OPPGJOER_EMNE (publishes)    "kosmos.kosmologi.oppgjoer.efc-fs8-arbiter"
    nats-koblingskart.md         "...utfall..."

Two halves, each with its own test, which passed because each test only
saw its own side. No test tied them together — so they could drift.

AND THE DECISIVE PART: `utfall` is caught by NO stream. The five streams
catch `observasjon, prediksjon, oppgjoer, tilstand, hendelse, diskusjon`.
A subject without a caught layer word gets `+OK` from the server and
vanishes without a trace — no error, no log (house build rule 26).

The arbiter is latent now (`arbiter: "nei"`, waiting for DESI DR2), but it
delivers the verdict the whole validation chain waits for. The bug would
have struck silently in October.
"""
import importlib.util
import sys
import unittest
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT))

# The layer words the streams ACTUALLY catch. Measured against JetStream
# 2026-09-17:
#   VERDEN_OBS        observasjon
#   VERDEN_TILSTAND   tilstand
#   VERDEN_TOLKET     hendelse, diskusjon
#   VERDEN_PROGNOSE   prediksjon, oppgjoer
#   OPUS_SELV         prediksjon, oppgjoer, tilstand, hendelse
# If the streams change, this list must be updated WITH a new measurement
# — not by guessing. The test below fails if a subject uses a word that
# is not listed here.
FANGEDE_LAG = {"observasjon", "prediksjon", "oppgjoer", "tilstand",
               "hendelse", "diskusjon"}


def _les_konstant(sti: Path, navn: str) -> str:
    tekst = sti.read_text(encoding="utf-8")
    for linje in tekst.splitlines():
        if linje.startswith(f"{navn} = "):
            return linje.split("=", 1)[1].strip().strip('"').strip("'")
    raise AssertionError(f"{navn} not found in {sti}")


class TestArbiterEmneKontrakt(unittest.TestCase):

    def test_konsumentens_emne_fanges_av_en_stroem(self):
        """The hard proof: a layer word the streams actually catch."""
        emne = _les_konstant(
            ROT / "scripts" / "maintenance" / "arbiter_vakt_kjoer.py",
            "OPPGJOER_EMNE")
        lag = emne.split(".")[2]
        self.assertIn(lag, FANGEDE_LAG,
                      f"'{lag}' is caught by no stream — the message would "
                      f"get +OK and vanish without a trace")

    def test_payloadens_emne_er_samme_som_konsumentens(self):
        """The `emne` field inside the payload says where the message belongs.
        If it differs from the actual publication, the payload lies."""
        konsument = _les_konstant(
            ROT / "scripts" / "maintenance" / "arbiter_vakt_kjoer.py",
            "OPPGJOER_EMNE")
        for modul in ("efc_inference/arbiter/sealed_fs8.py",
                      "efc_inference/arbiter/rapid_response.py"):
            tekst = (ROT / modul).read_text(encoding="utf-8")
            emner = {linje.split('"')[3]
                     for linje in tekst.splitlines()
                     if '"emne":' in linje and '"' in linje}
            self.assertTrue(emner, f"no emne line in {modul}")
            for e in emner:
                self.assertEqual(
                    e, konsument,
                    f"{modul} points at {e}, the consumer publishes to "
                    f"{konsument} — the two halves have drifted apart")

    def test_dokumentasjonen_nevner_ikke_det_ufangede_emnet(self):
        """The coupling map is the contract external readers use."""
        kart = (ROT / "docs" / "nats-koblingskart.md").read_text(
            encoding="utf-8")
        self.assertNotIn(
            "kosmos.kosmologi.utfall.efc-fs8-arbiter", kart,
            "the map documents a subject no stream catches")


if __name__ == "__main__":
    unittest.main()
