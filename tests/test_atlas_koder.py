"""Code uniqueness: every node has its own short identifier.

MEASURED 2026-09-17 against origin/main: `efc_atlas_generator.py` had 28 codes
for 82 nodes. The rest fell back to `nid[:2].upper()`, and the 73
public nodes thereby got 18 codes:

    EF  20 nodes   (efc.l1, efc.l2, efc.rotation_engine, ...)
    OB  20 nodes   (obs.bao, obs.cmb_tt, ...)
    HO  12 nodes   (homo.fluxus, ...)
    H2   6 nodes   (h2o.solid, ...)
    RE   2 nodes   (regnbue, regnbue.observator)

A code that points at twenty nodes at the same time identifies none of them.

The code IS an identifier, not decoration: `build.mjs` builds question IDs
from it (`Q-<code><n>`, and the index in SYSTEM.md says "Reference by ID"), and
FLOWS names its hops with it (HA, BI, VU, EF). The decision is
therefore that the code shall be UNAMBIGUOUS, that the table shall cover the whole bank, and
that the generator shall FAIL rather than guess.

The FAILURE MODE that made this invisible is worth naming: the fallback answered
instead of saying so. 15 of the 28 keys moreover named nodes that
never existed under that name (`efc.hubble` vs `efc.hubble_engine`)
— the table had rotted, and nobody could see it. This file tests BOTH
directions, because a test that only looks for holes does not see rot.

The rules live in the generator (`manglende_koder`, `foreldede_koder`,
`kollisjoner`) and not in prose here: then they can be run and mutated against.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROT = Path(__file__).resolve().parents[1]
JSONLD = ROT / "schema" / "regime_nodes.jsonld"
GENERATOR = ROT / "scripts" / "maintenance" / "efc_atlas_generator.py"
DATA_MJS = ROT / "docs" / "efc-atlas" / "atlas" / "data.mjs"

sys.path.insert(0, str(ROT / "scripts" / "maintenance"))
import efc_atlas_generator as gen  # noqa: E402

#: The tile that draws the code is 16 px wide (atlas/template.html) — hence
#: 1-2 characters. The limit is visual, but the code is an identifier, so both
#: requirements must hold at the same time.
KODE_MONSTER = re.compile(r"[A-Z0-9]{1,2}\Z")


def _bank() -> list[dict]:
    return json.loads(JSONLD.read_text(encoding="utf-8"))["nodes"]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class TestAtlasKoder(unittest.TestCase):

    def test_hver_node_i_banken_har_en_deklarert_kode(self):
        """No fallback shall be able to answer for a node. A new node without
        a code is an error that shall be SEEN — not a code that is guessed."""
        mangler = gen.manglende_koder(_bank())
        self.assertEqual(mangler, [],
                         f"{len(mangler)} node(s) without a code: {mangler}")

    def test_kodene_er_entydige(self):
        """The core of the finding: 73 nodes identified by 18 codes."""
        koll = gen.kollisjoner(_bank())
        detalj = "; ".join(f"{k} -> {', '.join(v)}" for k, v in koll.items())
        self.assertEqual(koll, {},
                         f"{len(koll)} code(s) point at several nodes: {detalj}")

    def test_deklarasjonen_raatner_ikke(self):
        """The opposite direction. 15 of the 28 old keys named nodes that do not
        exist (`efc.hubble`, `efc.water`, ...) — they are called `*_engine` in
        the bank. If a node id changes without the code moving with it, it shall fail
        here, not remain as a silently left-over key."""
        doede = gen.foreldede_koder(_bank())
        self.assertEqual(doede, [],
                         f"codes declared for nodes that do not exist: {doede}")

    def test_koden_passer_i_brikken(self):
        """1-2 characters, A-Z0-9. A code that does not fit in the tile is an
        invisible error in the public map."""
        darlige = {k: v for k, v in gen.KODER.items()
                   if not KODE_MONSTER.match(v)}
        self.assertEqual(darlige, {}, f"codes outside [A-Z0-9]{{1,2}}: {darlige}")

    def test_data_mjs_baerer_de_deklarerte_kodene(self):
        """The published artifact, not just the table. The freshness test
        catches a stale file; this one catches that the content is the same as
        the decision."""
        tekst = DATA_MJS.read_text(encoding="utf-8")
        par = re.findall(r'"code": "([^"]+)",\n\s+"name": "([^"]+)"', tekst)
        self.assertTrue(par, "found no code/name pair in data.mjs")
        ut = {navn: kode for kode, navn in par}
        offentlige = [n["id"] for n in _bank()
                      if n.get("synlighet") == "offentlig"]
        self.assertEqual(sorted(ut), sorted(offentlige),
                         "data.mjs and the bank do not show the same node set")
        feil = {n: (ut[n], gen.KODER[n]) for n in ut
                if ut[n] != gen.KODER[n]}
        self.assertEqual(feil, {}, f"data.mjs deviates from KODER: {feil}")
        self.assertEqual(len(set(ut.values())), len(ut),
                         "data.mjs publishes a code that points at several nodes")

    def test_flows_peker_paa_deklarerte_koder(self):
        """FLOWS names nodes with the code (HA -> KL, BI -> EF, VU -> TR).
        That coupling is only meaningful as long as the code is unambiguous —
        and it is the reason why `EF` cannot point at twenty nodes."""
        gyldige = set(gen.KODER.values())
        for f in gen.FLOWS:
            for h in f["hops"]:
                for ende in (h[0], h[1]):
                    self.assertIn(ende, gyldige,
                                  f"FLOWS «{f['id']}» points at the code "
                                  f"«{ende}», which is not declared")

    def test_kode_for_gjetter_ikke(self):
        """The old fallback answered with `nid[:2].upper()`. It shall not
        be able to answer at all."""
        with self.assertRaises(KeyError):
            gen.kode_for("test.finnes_ikke")

    def test_generatoren_har_ingen_stille_fallback(self):
        """Tripwire against reintroducing the lookup itself, not against the word:
        the comment above KODER must be able to NAME the error (`nid[:2].upper()`,
        which turned 20 nodes into «EF»). The proving test is the one below —
        a real run of hoved() — but a `KODER.get(...)` with a value
        after the comma shall not be able to sneak in unseen."""
        kilde = GENERATOR.read_text(encoding="utf-8")
        kode = "\n".join(l for l in kilde.splitlines()
                         if not l.lstrip().startswith("#"))
        self.assertIsNone(
            re.search(r"KODER\.get\s*\(", kode),
            "a lookup with a fallback is back in the generator: "
            "KODER.get(...) answers instead of saying so")

    def _hoved_mot(self, bank: list[dict], *,
                   koder: dict | None = None):
        """Runs hoved() against a fake bank and an empty out directory.

        Both the source and the out directory are swapped, so a guard that does NOT fire writes
        into a temp directory — it cannot touch the real atlas.
        """
        with tempfile.TemporaryDirectory() as tmp:
            falsk = Path(tmp) / "regime_nodes.jsonld"
            falsk.write_text(json.dumps({"nodes": bank}), encoding="utf-8")
            ut = Path(tmp) / "atlas"
            ut.mkdir()
            buffer = io.StringIO()
            with contextlib.ExitStack() as st:
                st.enter_context(mock.patch.object(gen, "JSONLD", falsk))
                st.enter_context(mock.patch.object(gen, "ATLAS_DIR", ut))
                if koder is not None:
                    st.enter_context(mock.patch.dict(gen.KODER, koder))
                with contextlib.redirect_stdout(buffer):
                    rc = gen.hoved()
            return rc, buffer.getvalue(), (ut / "data.mjs").exists()

    def test_ny_node_uten_kode_feller_generatoren(self):
        """Requirement 3, tried for real: a new node without a code shall not be
        able to pass by fallback. It shall stop the build BEFORE data.mjs is written
        — an atlas with wrong codes looks finished, and that is why the law exists."""
        for_ut = _sha(DATA_MJS)
        bank = _bank() + [{"id": "test.ny_uten_kode", "synlighet": "offentlig"}]
        rc, utskrift, skrevet = self._hoved_mot(bank)
        self.assertEqual(rc, 1, f"the generator let it through:\n{utskrift}")
        self.assertIn("mangler kode", utskrift,
                      "failed for the wrong reason — the proof must name the cause")
        self.assertIn("test.ny_uten_kode", utskrift)
        self.assertFalse(skrevet, "data.mjs was written before the guard fired")
        self.assertEqual(_sha(DATA_MJS), for_ut,
                         "the generator touched the real atlas")

    def test_kollisjon_feller_generatoren(self):
        """The same guard, the opposite cause: a code that points at two nodes shall
        not be buildable at all."""
        for_ut = _sha(DATA_MJS)
        rc, utskrift, skrevet = self._hoved_mot(_bank(),
                                                koder={"h2o.solid": "LI"})
        self.assertEqual(rc, 1, f"the generator let it through:\n{utskrift}")
        self.assertIn("flere noder", utskrift,
                      "failed for the wrong reason — the proof must name the cause")
        self.assertIn("h2o.liquid", utskrift)
        self.assertFalse(skrevet, "data.mjs was written before the guard fired")
        self.assertEqual(_sha(DATA_MJS), for_ut,
                         "the generator touched the real atlas")

    def test_foreldet_kode_feller_generatoren(self):
        """And third: a key that no longer names a node shall stop
        the build. That was the state the table was in — unseen."""
        for_ut = _sha(DATA_MJS)
        rc, utskrift, skrevet = self._hoved_mot(_bank(),
                                                koder={"efc.hubble": "ZZ"})
        self.assertEqual(rc, 1, f"the generator let it through:\n{utskrift}")
        self.assertIn("do not exist", utskrift,
                      "failed for the wrong reason — the proof must name the cause")
        self.assertFalse(skrevet, "data.mjs was written before the guard fired")
        self.assertEqual(_sha(DATA_MJS), for_ut,
                         "the generator touched the real atlas")


if __name__ == "__main__":
    unittest.main()
