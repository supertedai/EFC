"""The source axis: a source routed into many domains cannot stay invisible.

THE FINDING that made this test necessary (2026-09-18). The domain axis
(`test_atlas_dekning.py`) measures ownership per BUS DOMAIN. Measured against
origin/main after all 39 domains had been given their node:

    39 of 39 domains covered.

and at the same time, on the other axis:

    GDELT GKG    20 domains   30 352 messages   14 readers   0 owners
    World Bank   18 domains      302 messages    0 readers   0 owners
    MAST/CAOM     6 domains      174 messages    0 readers   0 owners

The largest source on the bus -- 30 352 messages, twenty domains -- is owned by
nobody. The domain axis could not see it: every domain has its node, every node
stands as `covered`, and the source they all READ exists in the map as nothing
but a field inside each of them.

    A map that measures how many places something enters, and not where it
    comes from, is counting symptoms.

## Four faults this file convicts

1. A source that carries messages without standing in the declaration (silence).
2. A declared source that no longer carries anything (a rotting claim).
3. A node naming a source its OWN bus domain does not carry. Measured:
   `kosmos.interstellart`, `kosmos.stjerner` and `kosmos.romfart` carried
   `measure.measurer = "the GDELT project"` while their domains carry
   `observasjon.mast-caom` and `launch-library` and NULL GDELT messages.
   The generator had a fallback to GDELT where the lookup should have said no.
4. A source carried by several domains WITHOUT an owner and WITHOUT a reason.

The threshold in point 4 is not chosen: a source carried by ONE domain is owned
by that domain's node -- the reading IS the node, and there is no shadow.
Carried by two or more, no single node can cover it, and then the absence of an
owner must stand named.

The lists in the declaration (`lesere`, `domener`, `meldinger`) are derived
HERE, not in the builder: a list checked only against itself rotates in step
with the fault.

Language: English only, per the repo-wide language gate
(`scripts/maintenance/efc_spraakvakt.py`), which fails on any Norwegian this
change adds under `tests/`.
"""
from __future__ import annotations

import json
import sys
import unittest
from collections import defaultdict
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROT / "schema" / "nats_domener.snapshot.json"
DEKNING = ROT / "schema" / "atlas_dekning.json"
NODER = ROT / "schema" / "regime_nodes.jsonld"
GENERATOR = ROT / "scripts" / "maintenance" / "bygg_kildenoder.py"

sys.path.insert(0, str(ROT / "scripts"))
import atlas_kilder as ak  # noqa: E402


def _les(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _kilde_for_node(n: dict) -> str | None:
    """The source the node ITSELF writes -- not a list we wrote for it."""
    return ((n.get("lagdeling") or {}).get("kilde") or {}).get("kilde")


def _baert(snapshot: dict) -> dict[str, dict]:
    """The source segments the bus carries, with domains and messages -- derived
    from the subject names.

    The maker of the subject names is `docs/nats-koblingskart.md`: subjects have
    the form `<root>.<domain>.<layer>.<source>`. The last segment IS the source.
    """
    ut: dict[str, dict] = defaultdict(lambda: {"meldinger": 0, "domener": set()})
    for domene, rad in snapshot["domener"].items():
        for emne, antall in rad["emner"].items():
            ledd = str(emne).split(".")[-1]
            ut[ledd]["meldinger"] += antall
            ut[ledd]["domener"].add(domene)
    return {k: {"meldinger": v["meldinger"], "domener": sorted(v["domener"])}
            for k, v in ut.items()}


class TestKildeaksen(unittest.TestCase):

    def setUp(self):
        self.snapshot = _les(SNAPSHOT)
        self.dekning = _les(DEKNING)
        self.noder = _les(NODER)["nodes"]
        self.baert = _baert(self.snapshot)

    def test_kilder_seksjonen_finnes(self):
        """Without the section the whole axis is a claim that somebody remembers
        it."""
        self.assertIn("kilder", self.dekning,
                      "schema/atlas_dekning.json has no `kilder` section -- "
                      "the source axis is not declared at all")

    def test_ingen_kilde_baerer_meldinger_uten_aa_staa_i_deklarasjonen(self):
        """The core, and the same invariant as for the domains.

        A source segment that starts carrying messages must convict this test
        until somebody has taken a position on it -- not slide into silence
        because the domain it feeds already has a node.
        """
        udeklarerte = sorted(set(self.baert) - set(self.dekning["kilder"]))
        self.assertEqual(
            udeklarerte, [],
            f"{len(udeklarerte)} source segments carry messages without "
            f"standing in atlas_dekning.json: {udeklarerte}")

    def test_ingen_deklarert_kilde_har_sluttet_aa_baere(self):
        """The other direction: a declaration for a stream that is gone is a
        claim about a world that no longer exists."""
        doede = sorted(set(self.dekning["kilder"]) - set(self.baert))
        self.assertEqual(doede, [],
                         f"declared for source segments that carry nothing: "
                         f"{doede}")

    def test_hver_node_navngir_en_kilde_dens_eget_domene_baerer(self):
        """The fabrication guard. Measured 2026-09-18: three nodes named GDELT
        for domains without a single GDELT message, because the generator's
        lookup answered GDELT when the source was unknown.

        The requirement is mechanical: the source node writes must belong to a
        segment the domain IT owns actually carries. Then the label cannot be
        false -- it can only be arbitrary, which is another matter.
        """
        navn_til_ledd: dict[str, set[str]] = defaultdict(set)
        for ledd, rad in self.dekning["kilder"].items():
            if rad.get("navn"):
                navn_til_ledd[rad["navn"]].add(ledd)

        feil = []
        for n in self.noder:
            kilde = _kilde_for_node(n)
            domene = n.get("buss_domene")
            if not kilde or not domene:
                continue
            ledd = navn_til_ledd.get(kilde)
            if not ledd:
                feil.append((n["id"], kilde, domene, "the source is not declared"))
                continue
            baerer = any(domene in self.baert.get(l, {}).get("domener", [])
                         for l in ledd)
            if not baerer:
                feil.append((n["id"], kilde, domene,
                             "the domain carries none of the source's segments"))
        self.assertEqual(
            feil, [],
            f"{len(feil)} node(s) name a source they do not read:\n  " +
            "\n  ".join(f"{i} says \"{k}\", the domain {d} -- {h}"
                        for i, k, d, h in feil))

    def test_leserlisten_er_utledet_av_nodenes_eget_felt(self):
        """The same requirement as the `noder` lists of the domain axis: a list
        written by hand can omit a node without anything seeing it."""
        for ledd, rad in self.dekning["kilder"].items():
            navn = rad.get("navn")
            maalt = sorted(n["id"] for n in self.noder
                           if navn and _kilde_for_node(n) == navn)
            self.assertEqual(
                sorted(rad.get("lesere") or []), maalt,
                f"{ledd}: the declaration says the readers "
                f"{rad.get('lesere')}, the bank says {maalt}")

    def test_domenene_og_volumet_er_utledet_av_maalingen(self):
        """Both directions: a source cannot be attributed to a domain it does
        not feed, and a domain it feeds cannot be left out."""
        for ledd, rad in self.dekning["kilder"].items():
            self.assertIn(ledd, self.baert, f"{ledd} carries no messages")
            maalt = self.baert[ledd]
            self.assertEqual(sorted(rad.get("domener") or []), maalt["domener"],
                             f"{ledd}: the declaration says {rad.get('domener')}, "
                             f"the measurement says {maalt['domener']}")
            self.assertEqual(rad.get("meldinger"), maalt["meldinger"],
                             f"{ledd}: the declaration says "
                             f"{rad.get('meldinger')} messages, the measurement "
                             f"says {maalt['meldinger']}")

    def test_en_delt_kilde_uten_eier_maa_baere_grunnen_sin(self):
        """An absence of an owner must stand named, not be silent.

        The threshold is not chosen: carried by one domain, the source is owned
        by that domain's node. Carried by several, no single node can cover it
        -- and then the silence is the fault.
        """
        mangler = []
        for ledd, rad in self.dekning["kilder"].items():
            if rad.get("status") == "eid":
                continue
            if len(self.baert.get(ledd, {}).get("domener", [])) > 1:
                if not str(rad.get("begrunnelse", "")).strip():
                    mangler.append(ledd)
        self.assertEqual(
            mangler, [],
            f"{len(mangler)} source segments are carried by several domains and "
            f"have neither an owner nor a reason: {mangler}")

    def test_eid_status_kreve_en_eier_som_navngir_kilden(self):
        """`eid` must mean that a node IS the source -- not that somebody
        mentions it."""
        bank = {n["id"]: n for n in self.noder}
        for ledd, rad in self.dekning["kilder"].items():
            eiere = list(rad.get("eiere") or [])
            if rad.get("status") == "eid":
                self.assertTrue(eiere, f"{ledd} is `eid` without an owner")
            else:
                self.assertEqual(eiere, [],
                                 f"{ledd} names the owners {eiere} without "
                                 f"status `eid`")
            for e in eiere:
                self.assertIn(e, bank, f"{ledd}: the owner \"{e}\" does not exist")
                self.assertEqual(_kilde_for_node(bank[e]), rad.get("navn"),
                                 f"{ledd}: the owner \"{e}\" does not name the "
                                 f"source")

    def test_aksen_er_ikke_tom(self):
        """A test that cannot convict anything proves nothing. This one says the
        source axis actually carries the two shapes it was built for: a source
        with several readers, and a source carried by several domains."""
        lesere = sum(1 for rad in self.dekning["kilder"].values()
                     if rad.get("lesere"))
        brede = sum(1 for ledd in self.dekning["kilder"]
                    if len(self.baert.get(ledd, {}).get("domener", [])) > 1)
        self.assertGreater(lesere, 0, "no node names any source -- the link "
                                      "between bank and source is gone")
        self.assertGreater(brede, 0, "no source is carried by several domains -- "
                                     "then the axis measures nothing")

    def test_sjekken_i_verktoyet_og_testen_er_enede(self):
        """`atlas_kilder.py --sjekk` is the runnable entry; the tests above are
        the ones that convict. If the two say different things, one of them is
        wrong."""
        self.assertEqual(ak.avvik({"snapshot": self.snapshot,
                                   "dekning": self.dekning,
                                   "noder": {"nodes": self.noder}}), [])

    def test_generatoren_gjetter_ikke_paa_kilden(self):
        """The fallback that fabricated three sources. A source lookup answered
        GDELT instead of saying no. It must not be able to answer again."""
        sys.path.insert(0, str(ROT / "scripts" / "maintenance"))
        sys.modules.pop("bygg_kildenoder", None)
        import bygg_kildenoder as bk  # noqa: E402
        with self.assertRaises(bk.KildeFeil):
            bk.kilde_for(["observasjon.finnes_ikke"])
        with self.assertRaises(bk.KildeFeil):
            bk.kilde_for([])
        # and the tripwire against the lookup itself: the name of the old
        # fallback must not be able to stand inside a source lookup again.
        kilde = GENERATOR.read_text(encoding="utf-8")
        kodelinjer = "\n".join(
            l for l in kilde.splitlines()
            if "KILDE.get(" in l and not l.strip().startswith("#"))
        self.assertEqual(kodelinjer, "", "the generator has a source lookup "
                                         f"with a fallback again: {kodelinjer!r}")


if __name__ == "__main__":
    unittest.main()
