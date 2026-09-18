"""The coverage invariant: no bus domain may be invisible to the atlas.

THE FINDING that made this test necessary (2026-09-17): the prediction
contract lay COMPLETELY on the bus — with sealed DOI, SHA256, freeze, criterion and
arbiter — and the atlas knew nothing. There was no node, no link,
no warning. I found it only by reading the streams directly.

    A map that does not show where it is incomplete is more dangerous than
    no map — because it looks complete.

The atlas cannot itself detect that it is missing a layer. But it can be measured:
cross the topics that CARRY traffic against the nodes that EXIST, and name those
that have no counterpart.

This is that invariant. It does not say that everything must be covered — the atlas
describes 3 of 39 domains, and that is an honest state. It says that a gap
must STAND NAMED in schema/atlas_dekning.json, not be silent. A new
domain that starts carrying messages shall fail this test until someone
has taken a stand on it.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROT / "schema" / "nats_domener.snapshot.json"
DEKNING = ROT / "schema" / "atlas_dekning.json"
NODER = ROT / "schema" / "regime_nodes.jsonld"

GYLDIGE_STATUS = {"dekket", "delvis", "ikke_dekket"}


def _les(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


class TestDekningsinvarianten(unittest.TestCase):
    def test_hvert_bussdomene_er_deklarert(self):
        """The core. A domain that carries messages but is not in
        the declaration is invisible — and invisible is how the prediction layer
        could lie complete on the bus without the atlas knowing it."""
        snap = set(_les(SNAPSHOT)["domener"])
        dekl = set(_les(DEKNING)["domener"])
        udeklarerte = sorted(snap - dekl)
        self.assertEqual(
            udeklarerte, [],
            f"{len(udeklarerte)} bus domain(s) carry messages without standing "
            f"in atlas_dekning.json — the atlas does not know they exist:\n  "
            + "\n  ".join(udeklarerte))

    def test_hvert_emne_i_et_kjent_domene_er_tatt_stilling_til(self):
        """Review finding 3: only the domain key was compared, so a known
        domain could gain new topics unseen. Now the topic lists are compared."""
        snap = _les(SNAPSHOT)["domener"]
        dekl = _les(DEKNING)["domener"]
        for domene, rad in snap.items():
            if domene not in dekl:
                continue  # caught by the test above
            nye = sorted(set(rad["emner"]) - set(dekl[domene]["emner"]))
            self.assertEqual(
                nye, [],
                f"{domene} has new bus topics that no one has taken a stand "
                f"on: {nye}")

    def test_deklarasjonen_raatner_ikke(self):
        """The opposite direction: a declaration for a domain that no longer
        exists is a claim about a world that is gone."""
        snap = set(_les(SNAPSHOT)["domener"])
        dekl = set(_les(DEKNING)["domener"])
        foreldede = sorted(dekl - snap)
        self.assertEqual(
            foreldede, [],
            f"declared for domains that do not exist in the snapshot: "
            f"{foreldede}")

    def test_hver_deklarasjon_har_status_og_begrunnelse(self):
        """A gap without a reason is just a hole."""
        for domene, rad in _les(DEKNING)["domener"].items():
            self.assertIn(rad.get("status"), GYLDIGE_STATUS, domene)
            self.assertTrue(rad.get("begrunnelse", "").strip(),
                            f"{domene} is missing a reason")

    def test_dekket_status_navngir_noder_som_faktisk_eier_domenet(self):
        """Review finding round 1 (id existence) and round 2 (SEMANTICS).

        Round 1: `dekket` could be redeemed by any node at all.
        Round 2: even with named nodes the test only checked that the ID
        existed — an existing but irrelevant node would pass.

        Now the node must OWN the domain: its own `buss_domene` field shall point
        back at the domain it justifies. That is the mechanical link
        which makes semantics something a test can see."""
        noder = {n["id"]: n for n in _les(NODER)["nodes"]}
        for domene, rad in _les(DEKNING)["domener"].items():
            ns = rad.get("noder", [])
            if rad["status"] in ("dekket", "delvis"):
                self.assertTrue(
                    ns, f"{domene} is '{rad['status']}' without a single node "
                        f"— a covered status must be redeemable")
            for n in ns:
                self.assertIn(
                    n, noder,
                    f"{domene} points at the node '{n}', which does not exist")
                self.assertEqual(
                    noder[n].get("buss_domene"), domene,
                    f"{domene} points at '{n}', but that node has "
                    f"buss_domene={noder[n].get('buss_domene')!r} — an "
                    f"existing node is not the same as a relevant one")

    def test_nodelistene_er_utledet_av_nodenes_eget_felt(self):
        """Review finding round 3, and it hits me on the word «derived».

        I SAID that the `noder` lists were derived from the nodes' `buss_domene`.
        They were not — I derived them ONCE with a script. The test
        only verified that what STOOD there was consistent, so a node
        could be left out of the list and go straight through. The blocker was
        proven: efc.orbital_engine removed from kosmos.satellitter.noder,
        while the node still had buss_domene set — 8 passed.

        Now the test derives the lists itself and compares BOTH ways. Then
        «derived» is a property of the test and not a claim in a commit.
        """
        from collections import defaultdict
        per: dict[str, list[str]] = defaultdict(list)
        for n in _les(NODER)["nodes"]:
            if n.get("buss_domene"):
                per[n["buss_domene"]].append(n["id"])
        dekl = _les(DEKNING)["domener"]
        for domene in sorted(set(per) | set(dekl)):
            fra_noder = sorted(per.get(domene, []))
            fra_dekl = sorted(dekl.get(domene, {}).get("noder", []))
            self.assertEqual(
                fra_noder, fra_dekl,
                f"{domene}: the nodes say {fra_noder}, the declaration says "
                f"{fra_dekl} — the list must be derived, not written")

    def test_maalingen_baerer_antall_per_emne(self):
        """The volume must be a MEASUREMENT. JetStream carries the count per topic in
        the stream's own `state.subjects`; the snapshot the invariant is tried
        against shall carry the same number, not just the name.

        The earlier note in the file said that per-topic numbers were not
        available. That was an assumption about NATS' monitoring API, not
        a measurement of the JetStream API — and a measurement showed the opposite.
        """
        for domene, rad in _les(SNAPSHOT)["domener"].items():
            self.assertIsInstance(
                rad["emner"], dict,
                f"{domene}: the topics must carry counts, not just names")
            for emne, antall in rad["emner"].items():
                self.assertIsInstance(antall, int, f"{domene}.{emne}")
                self.assertGreaterEqual(
                    antall, 1,
                    f"{domene}.{emne} stands with {antall} messages — a topic "
                    f"without messages carries no traffic and shall not be "
                    f"declared")

    def test_volumet_per_domene_er_utledet_av_maalingen(self):
        """Same requirement as for the `noder` lists, repeated for the volume: I
        could have written a number that LOOKS right. The derivation shall therefore
        be the TEST'S — the sum of the measured per-topic numbers — not
        the author's. A hardcoded volume does not survive a new measurement."""
        snap = _les(SNAPSHOT)["domener"]
        for domene, rad in _les(DEKNING)["domener"].items():
            maalt = sum((snap.get(domene, {}).get("emner") or {}).values())
            self.assertIn("meldinger", rad,
                          f"{domene} is missing 'meldinger' — a gap without "
                          f"size reads the same as any "
                          f"other gap")
            self.assertEqual(
                rad["meldinger"], maalt,
                f"{domene}: the declaration says {rad['meldinger']}, the measurement "
                f"says {maalt} — the volume must be derived, not written")

    def test_deklarasjonens_emneliste_er_maalingens_emneliste(self):
        """The opposite way of the test above: a topic that is DECLARED but does not
        exist in the measurement is a claim about a stream that carries nothing
        any longer. Both ways must hold — otherwise the declaration and
        the measurement count two different worlds, and their sum is not the volume."""
        snap = _les(SNAPSHOT)["domener"]
        for domene, rad in _les(DEKNING)["domener"].items():
            maalt = set((snap.get(domene, {}).get("emner") or {}))
            deklarert = set(rad.get("emner") or [])
            self.assertEqual(
                sorted(deklarert - maalt), [],
                f"{domene}: declared for topics that carry no messages: "
                f"{sorted(deklarert - maalt)}")

    def test_hvert_domene_i_deklarasjonen_har_volum(self):
        """Also a `dekket` channel shall carry the number. Without it a covered
        channel with 23 477 messages behind one node looks as finished as one with one
        message behind twenty."""
        for domene, rad in _les(DEKNING)["domener"].items():
            self.assertIsInstance(rad.get("meldinger"), int, domene)
            self.assertGreaterEqual(rad["meldinger"], 0, domene)

    def test_hvert_domene_med_noder_er_deklarert_dekket(self):
        """The opposite way of the one above: if a node has said that it describes a
        domain, the declaration shall say the same. Without this the atlas could
        describe a domain while the declaration said it was uncovered —
        and the declaration is what humans read."""
        noder = _les(NODER)["nodes"]
        eide = {n["buss_domene"] for n in noder if n.get("buss_domene")}
        dekl = _les(DEKNING)["domener"]
        for domene in sorted(eide):
            self.assertIn(domene, dekl,
                          f"nodes describe {domene}, but it is not in "
                          f"the declaration")
            self.assertIn(
                dekl[domene]["status"], ("dekket", "delvis"),
                f"{domene} has nodes that describe it, but is declared "
                f"'{dekl[domene]['status']}'")

    def test_snapshottet_baerer_sin_egen_proveniens(self):
        """Without a measurement time no one can see whether the snapshot is fresh."""
        prov = _les(SNAPSHOT).get("_proveniens", {})
        self.assertIn("maalt", prov)
        self.assertIn("kilde", prov)
        self.assertIn("lest_av", prov)

    def test_snapshottet_har_ikke_gaatt_ut_paa_dato(self):
        """A measurement without an expiry date is a claim that slowly becomes false.
        The stale kanban copy was valid, answered and LIED: it simply stopped
        being written. Same trap. A snapshot that is too old
        shall force a new measurement, not keep looking verified."""
        import datetime
        maalt = _les(SNAPSHOT)["_proveniens"]["maalt"]
        naar = datetime.datetime.fromisoformat(maalt.replace("Z", "+00:00"))
        if naar.tzinfo is None:
            naar = naar.replace(tzinfo=datetime.timezone.utc)
        alder = (datetime.datetime.now(datetime.timezone.utc) - naar).days
        self.assertLess(
            alder, 90,
            f"the snapshot is {alder} days old — measure the bus anew "
            f"and write schema/nats_domener.snapshot.json before you trust the "
            f"coverage picture")


if __name__ == "__main__":
    unittest.main()
