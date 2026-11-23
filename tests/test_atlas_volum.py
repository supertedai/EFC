"""atlas_volum — the volume is read from the measurement, and the gap is sorted by it.

The card that made this test necessary (t_29a426ac) was found by
USING the atlas lookup, not by testing it: `verden.vaer` (190 229
messages) and `verden.utdanning` (2 598) answered the same, because the answer had no
size.

Two things must therefore be pinned, and they are different:

1. **The number is measured.** The tests below feed synthetic measurements where
   the declaration LIES about the volume, and require that the reader answers with
   the measurement. Without them, "sort by significance" could be fulfilled by a
   field someone wrote by hand.
2. **The sorting is a sorting.** A gap of two and one of 190 000 shall
   come in that order, also when the names say the opposite.
   Separating case: `aaa.lite` vs `zzz.stort` — alphabetical and
   volume order are opposite.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
MODUL = ROT / "scripts" / "atlas_volum.py"

_spec = importlib.util.spec_from_file_location("atlas_volum", MODUL)
assert _spec and _spec.loader
av = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(av)

DEKNING = json.loads((ROT / "schema" / "atlas_dekning.json").read_text(
    encoding="utf-8"))
SNAPSHOT = json.loads(
    (ROT / "schema" / "nats_domener.snapshot.json").read_text(encoding="utf-8"))


def _dekl(rader: dict) -> dict:
    return {"domener": {navn: {"status": s, "meldinger": m,
                               "noder": [], "begrunnelse": "test",
                               "emner": list(e)}
                        for navn, (s, m, e) in rader.items()}}


def _snap(rader: dict) -> dict:
    return {"domener": {navn: {"emner": dict(e)}
                        for navn, e in rader.items()}}


class TestSorteringEtterBetydning(unittest.TestCase):
    def test_storrelse_gaar_foran_alfabet(self):
        """The separating case. Alphabetical order would have said `aaa.lite`
        first; that is exactly the reading the card found."""
        dekl = _dekl({"aaa.lite": ("ikke_dekket", 2, ["a"]),
                      "zzz.stort": ("ikke_dekket", 190000, ["b"])})
        ut = av.hull(dekl)
        self.assertEqual([r["domene"] for r in ut], ["zzz.stort", "aaa.lite"],
                         "the gaps came in alphabetical order — then a "
                         "gap of 190 000 cannot be told from one of 2")

    def test_rekkefoelgen_henger_ikke_paa_innsettingsrekkefoelgen(self):
        fram = _dekl({"a": ("ikke_dekket", 5, []), "b": ("ikke_dekket", 500, []),
                      "c": ("ikke_dekket", 50, [])})
        bak = _dekl({"c": ("ikke_dekket", 50, []), "b": ("ikke_dekket", 500, []),
                     "a": ("ikke_dekket", 5, [])})
        self.assertEqual([r["domene"] for r in av.hull(fram)],
                         [r["domene"] for r in av.hull(bak)])

    def test_like_store_hull_sorteres_paa_navn(self):
        """Without this the order between equally large gaps would have been
        random, and a diff would look like a change."""
        dekl = _dekl({"b": ("ikke_dekket", 10, []), "a": ("ikke_dekket", 10, [])})
        self.assertEqual([r["domene"] for r in av.hull(dekl)], ["a", "b"])

    def test_volumet_leses_fra_maalingen_naar_den_finnes(self):
        """The declaration says 3, the measurement says 3000. The reader shall answer
        the measurement — otherwise "sorted by significance" can be fulfilled by a number
        someone wrote by hand, which is exactly the failure mode the card names."""
        dekl = _dekl({"x": ("ikke_dekket", 3, ["e1"])})
        snap = _snap({"x": {"e1": 3000}})
        ut = av.hull(dekl, snap)
        self.assertEqual(ut[0]["meldinger"], 3000)

    def test_emnefordelingen_foelger_domenet(self):
        snap = _snap({"x": {"small": 2, "large": 90}})
        dekl = _dekl({"x": ("ikke_dekket", 92, ["small", "large"])})
        self.assertEqual(av.hull(dekl, snap)[0]["emner"],
                         [("large", 90), ("small", 2)])

    def test_standarden_er_bare_ikke_dekket(self):
        dekl = _dekl({"hull": ("ikke_dekket", 10, []),
                      "nesten": ("delvis", 5000, []),
                      "dekket": ("dekket", 9000, [])})
        self.assertEqual([r["domene"] for r in av.hull(dekl)], ["hull"])

    def test_alle_statuser_kan_vis_se_naar_statuser_er_none(self):
        """`--alle` exists because the opposite error is also invisible: a `dekket`
        channel with much traffic behind one node looks finished."""
        dekl = _dekl({"hull": ("ikke_dekket", 10, []),
                      "dekket": ("dekket", 9000, [])})
        self.assertEqual([r["domene"] for r in av.hull(dekl, statuser=None)],
                         ["dekket", "hull"])

    def test_den_ekte_filen_gir_hull_sortert_etter_volum(self):
        rader = av.hull(DEKNING, SNAPSHOT)
        # 2026-09-18: every one of the 39 domains had a node, and an empty hull
        # was the goal reached, not a fault. Measured 2026-09-19: the bus gained
        # kosmos.exoplanet (63 messages) before anybody had built a node for it,
        # so the hull is non-empty again. The test checks the consistency, not
        # the length: a declared hull must be measured, and sorted by size.
        self.assertIsInstance(rader, list)
        self.assertTrue(all(r["status"] == "ikke_dekket" for r in rader))
        nokler = [(r["meldinger"] is None, -(r["meldinger"] or 0), r["domene"])
                  for r in rader]
        self.assertEqual(nokler, sorted(nokler))
        self.assertTrue(
            all(r["meldinger"] is None or r["meldinger"] > 0 for r in rader),
            "a declared gap with 0 messages is not a measured gap — the bus "
            "builds its domains from the subjects that carry messages, so 0 is "
            "not a number this measurement can produce")

    def test_et_domene_utenfor_maalingen_leses_som_ukjent(self):
        """The reading side of the same rule, and it is the one that made the
        card: the declaration says 6941, the measurement does NOT carry the
        domain. Answering 6941 would show a stream that has stopped answering
        as unchanged — a measurement from before the silence, presented as now.
        """
        dekl = _dekl({"stille.stroem": ("delvis", 6941, ["tilstand.k"])})
        snap = _snap({"annet.domene": {"tilstand.m": 3}})
        rad = av.hull(dekl, snap, statuser=None)[0]
        self.assertEqual(rad["domene"], "stille.stroem")
        self.assertIsNone(
            rad["meldinger"],
            f"the reader answered {rad['meldinger']!r} for a domain the "
            f"measurement does not carry — the declaration's own number is "
            f"from an earlier measurement, and the silence is not visible in it")

    def test_ukjent_volum_staar_sist_og_skrives_som_ukjent(self):
        """A ranking by size cannot rank a number that was never measured.
        The gap that was not measured stands last, by name, and its number
        column says UKJENT — not the declaration's old number, and not 0.
        """
        dekl = _dekl({"maalt.tung": ("ikke_dekket", 500, ["a"]),
                      "stille.stroem": ("ikke_dekket", 9, ["b"]),
                      "maalt.lett": ("ikke_dekket", 5, ["a"])})
        snap = _snap({"maalt.tung": {"a": 500}, "maalt.lett": {"a": 5}})
        rader = av.hull(dekl, snap)
        self.assertEqual([r["domene"] for r in rader],
                         ["maalt.tung", "maalt.lett", "stille.stroem"])
        tabell = av.format_table(rader)
        linje = [l for l in tabell.splitlines() if "stille.stroem" in l][0]
        self.assertTrue(linje.strip().startswith("UKJENT"),
                        f"the row for a domain that was not measured does not "
                        f"say UKJENT: {linje!r}")
        self.assertNotIn("9", linje,
                         f"the old number stands in the row: {linje!r}")


class TestMaalingen(unittest.TestCase):
    def _stub(self, katalog: Path, kropp: str) -> Path:
        fil = katalog / "stub-verden-mcp.py"
        fil.write_text(kropp, encoding="utf-8")
        return fil

    def test_maal_bussen_normaliserer_emnet_til_domenets_form(self):
        """The bus names the topic in full (`verden.vaer.prediksjon.metno`);
        the snapshot carries the short form. A measurement that wrote the full
        form would have double-counted the domain in every row — and failed the test in
        test_atlas_dekning, which compares the topic lists."""
        kropp = (
            "def verden_domener(_args):\n"
            "    return {'domener': {'verden.vaer': [\n"
            "        {'emne': 'verden.vaer.prediksjon.metno', 'meldinger': 7},\n"
            "        {'emne': 'verden.vaer.tilstand.metar', 'meldinger': 3},\n"
            "    ]}, 'tomme_stroemmer': []}\n")
        with tempfile.TemporaryDirectory() as d:
            fil = self._stub(Path(d), kropp)
            gammel = os.environ.get("NATS_VERDEN")
            os.environ["NATS_VERDEN"] = "nats://bruker:hemmelig@eksempel:4222"
            try:
                ut = av.maal_bussen(fil)
            finally:
                if gammel is None:
                    os.environ.pop("NATS_VERDEN", None)
                else:
                    os.environ["NATS_VERDEN"] = gammel
        self.assertEqual(ut["domener"],
                         {"verden.vaer": {"prediksjon.metno": 7,
                                          "tilstand.metar": 3}})

    def test_maal_bussen_nektar_aa_gjette_naar_verktoeyet_mangler(self):
        with self.assertRaises(av.VolumFeil) as ctx:
            av.maal_bussen(Path("/no/such/verden-mcp.py"))
        self.assertIn("verden-mcp.py", str(ctx.exception))

    def test_modulen_har_ingen_volumtabell(self):
        """The mechanical gate against the failure mode the card names: "do not solve it
        by guessing". A number in the code is a claim about the bus that no
        measurement keeps up to date — it rots at the first change in
        the traffic. Comments and docstrings carry measured numbers; the CODE shall
        not carry a single one."""
        tre = ast.parse(MODUL.read_text(encoding="utf-8"))
        tall = [n.value for n in ast.walk(tre)
                if isinstance(n, ast.Constant) and isinstance(n.value, int)
                and not isinstance(n.value, bool) and abs(n.value) >= 1000]
        self.assertEqual(
            tall, [],
            f"a number larger than 999 stands in the code ({tall}) — the volume shall "
            f"come from the measurement, not from a table")


class TestSkrivingen(unittest.TestCase):
    def test_oppdater_dekning_roerer_ikke_stillingtagen(self):
        dekl = {"_form": "x", "domener": {
            "a.b": {"status": "delvis", "noder": ["n1"],
                    "begrunnelse": "because someone has assessed it",
                    "emner": ["tilstand.k"]}}}
        ny, rapport = av.oppdater_dekning(dekl, {"a.b": {"tilstand.k": 41}})
        rad = ny["domener"]["a.b"]
        self.assertEqual(rad["meldinger"], 41)
        self.assertEqual(rad["status"], "delvis")
        self.assertEqual(rad["noder"], ["n1"])
        self.assertEqual(rad["begrunnelse"], "because someone has assessed it")
        self.assertEqual(ny["_form"], "x")
        self.assertEqual(rapport["nye_domener"], [])
        self.assertEqual(rapport["nye_emner"], {})

    def test_nye_domener_og_emner_rapporteres_og_deklareres_ikke(self):
        """The measurement is not allowed to declare a domain: status and
        begrunnelse are a decision. It shall NAME what is missing,
        so that the invariant fails — not make the test green."""
        dekl = {"domener": {"a.b": {"status": "ikke_dekket", "noder": [],
                                    "begrunnelse": "ingen node",
                                    "emner": ["tilstand.k"]}}}
        ny, rapport = av.oppdater_dekning(
            dekl, {"a.b": {"tilstand.k": 1, "diskusion.ny": 9},
                   "c.d": {"tilstand.m": 5}})
        self.assertEqual(rapport["nye_domener"], ["c.d"])
        self.assertEqual(rapport["nye_emner"], {"a.b": ["diskusion.ny"]})
        self.assertNotIn("c.d", ny["domener"])
        self.assertNotIn("diskusion.ny", ny["domener"]["a.b"]["emner"])

    def test_et_domene_ute_av_maalingen_skrives_som_ukjent(self):
        """A domain can leave the measurement: retention empties it, or the
        stream stops answering. Neither gives a MEASURED volume. The old
        number is a claim about now from a measurement that is gone, and 0 is
        a claim that the source answered with nothing — a number the bus
        cannot produce, because it builds its domains from the subjects that
        CARRY messages. What is left is UKJENT, written as `null`.

        The first version of this test asserted `0` and called it "a
        measurement that it no longer carries anything". That is the same
        shape as the defect ADR-043 records: a guard that asserts the wrong
        value cements the defect it was written to catch.
        """
        dekl = {"domener": {"borte.nå": {"status": "ikke_dekket", "noder": [],
                                         "begrunnelse": "x",
                                         "meldinger": 6941,
                                         "emner": ["tilstand.k"]}}}
        ny, rapport = av.oppdater_dekning(dekl, {})
        self.assertIsNone(
            ny["domener"]["borte.nå"]["meldinger"],
            f"the write line answered "
            f"{ny['domener']['borte.nå']['meldinger']!r} for a domain that is "
            f"not in the measurement — 0 is not a measured volume, and 6941 is "
            f"not the volume now")
        self.assertEqual(rapport["borte"], ["borte.nå"])

    def test_snapshottet_baerer_proveniens_og_maalt_antall(self):
        with tempfile.TemporaryDirectory() as d:
            sti = Path(d) / "snap.json"
            av.skriv_snapshot(sti, {"b.d": {"tilstand.k": 4},
                                    "a.c": {"tilstand.m": 1}},
                              lest_av="test", maalt="2026-09-17T00:00:00Z")
            data = json.loads(sti.read_text(encoding="utf-8"))
        prov = data["_proveniens"]
        self.assertEqual(prov["maalt"], "2026-09-17T00:00:00Z")
        self.assertEqual(prov["lest_av"], "test")
        self.assertTrue(prov["kilde"].strip())
        self.assertEqual(data["domener"]["a.c"]["emner"], {"tilstand.m": 1})
        self.assertEqual(list(data["domener"]), ["a.c", "b.d"],
                         "the domains shall stand sorted — an unsorted file gives "
                         "diff noise without information")

    def test_maal_skriver_begge_filene_og_leser_arbeidsstreet(self):
        """The measurement WRITES to the worktree, and must therefore read the
        same worktree. The first version read the declaration from the ref — an
        uncommitted decision would then be silently discarded by a
        maintenance run."""
        with tempfile.TemporaryDirectory() as d:
            rot = Path(d)
            (rot / "schema").mkdir()
            (rot / "schema" / "atlas_dekning.json").write_text(
                json.dumps({"_form": "x", "domener": {
                    "a.b": {"status": "delvis", "noder": ["n1"],
                            "begrunnelse": "ukommitert vurdering",
                            "emner": ["tilstand.k"]}}},
                    indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            opprinnelig = av.maal_bussen
            setattr(av, "maal_bussen",
                    lambda *a, **k: {"domener": {"a.b": {"tilstand.k": 77}},
                                     "tomme_stroemmer": []})
            try:
                self.assertEqual(av.hoved(["--maal", "--repo", str(rot)]), 0)
            finally:
                setattr(av, "maal_bussen", opprinnelig)
            dekl = json.loads((rot / "schema" / "atlas_dekning.json")
                              .read_text(encoding="utf-8"))
            snap = json.loads((rot / "schema" / "nats_domener.snapshot.json")
                              .read_text(encoding="utf-8"))
        self.assertEqual(dekl["domener"]["a.b"]["begrunnelse"],
                         "ukommitert vurdering")
        self.assertEqual(dekl["domener"]["a.b"]["status"], "delvis")
        self.assertEqual(dekl["domener"]["a.b"]["meldinger"], 77)
        self.assertEqual(snap["domener"]["a.b"]["emner"], {"tilstand.k": 77})
        self.assertTrue(snap["_proveniens"]["lest_av"].strip())

    def test_leseren_feiler_forstaaelig_paa_en_maaling_uten_antall(self):
        """Refs older than this module carry the topics as a list of names.
        The first version crashed with `AttributeError: 'list' object has no
        attribute 'values'` — a stack trace that says something is broken,
        not what is missing. The volume does not exist in that shape, and the reader
        shall SAY so."""
        with self.assertRaises(av.VolumFeil) as ctx:
            av.meldinger_per_domene({"domener": {"x": {"emner": ["tilstand.k"]}}})
        self.assertIn("--maal", str(ctx.exception))

    def test_les_fra_ref_feiler_hoeyt_paa_ukjent_ref(self):
        """The same rule as atlas_lesing: an invalid ref shall raise, not
        silently fall back to the worktree."""
        with self.assertRaises(av.VolumFeil):
            av.les_fra_ref(ROT, "no-such-ref")

    def test_les_fra_ref_leser_begge_filene(self):
        lest = av.les_fra_ref(ROT, "HEAD")
        self.assertIn("snapshot", lest)
        self.assertIn("dekning", lest)
        self.assertEqual(len(lest["commit"]), 40)


if __name__ == "__main__":
    unittest.main()
