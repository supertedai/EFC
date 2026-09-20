r"""Atlas reading: the rule is EXECUTABLE, and references are WHITELISTED.

Two things this file protects, and both came from review findings:

1. THE RULE. The previous edition read the document and required that the words
   «origin/main» and «working copy» were present. A mutant that TURNED the rule
   around — «read from the working copy … Never from git:origin/main» — passed
   3/3. Same error class as `startswith("git:")` in PR #1016: the form was
   checked, any value slipped through.

     A test cannot read meaning out of prose. The rule therefore lives in
     `scripts/atlas_lesing.py`, and is tested by changing the WORLD — the test
     mutates the working tree and requires the reading to be bit-for-bit identical.

2. REFERENCES. Three rounds tried to protect the published document with a
   BLACKLIST of evil path forms:

     round 3: fixed list (/opt/agent-work, /home/morten)
     round 4: the reviewer broke it with /Users/morten, C:\\..., /srv/...
     round 5: the reviewer broke it with UNC, file:///, single-segment absolute
     round 6: the reviewer broke it with path=..., markdown table cells,
              file://<host>/..., windows extended-length (\\?\)

   And gave the answer: «This should not be solved with yet another longer
   blacklist. A whitelist of allowed published references is better.»

   That is right. A blacklist must guess BOTH the path forms AND which characters
   can stand in front of them, and both can always be evaded. The question is
   turned around: not «is this an evil path?» but «is this a form we ALLOW?».
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts"))

from atlas_lesing import AtlasLesingFeil, les_atlas  # noqa: E402


def _git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(ROT), *a],
                          capture_output=True, text=True).stdout


class TestAtlasLesing(unittest.TestCase):
    def test_leser_fra_refen_og_navngir_kilden(self):
        d = les_atlas(ROT)
        self.assertEqual(d["kilde"], "git:origin/main")
        self.assertEqual(d["ref"], "origin/main")
        self.assertTrue(d["commit"], "commit missing — the source is not named")
        self.assertGreater(len(d["noder"]), 0)

    def test_arbeidsstreet_paavirker_ikke_lesningen(self):
        """THE DECISIVE TEST — changes the world, not the text.

        Mutates the working tree's file and requires the result to be BIT-FOR-BIT
        identical. Review finding round 2: the previous edition only compared
        node IDs, so a mutant that changed all FIELDS but kept the ids
        passed. Now the whole structure is compared.
        """
        forsta = les_atlas(ROT)
        fil = ROT / "schema" / "regime_nodes.jsonld"
        opprinnelig = fil.read_bytes()
        try:
            fil.write_text(
                json.dumps({"nodes": [dict(n, tampered=True)
                                      for n in forsta["noder"]]}),
                encoding="utf-8")
            andre = les_atlas(ROT)
        finally:
            fil.write_bytes(opprinnelig)
        self.assertEqual(forsta["noder"], andre["noder"],
                         "the reading changed when the working tree changed — "
                         "it reads the working tree, not the ref")
        self.assertEqual(json.dumps(forsta, sort_keys=True),
                         json.dumps(andre, sort_keys=True),
                         "the whole result must be identical")
        self.assertNotIn("tampered", json.dumps(andre))

    def test_ukjent_ref_feiler_og_faller_ikke_stille_tilbake(self):
        """A silent fallback to the working tree is precisely the error mode."""
        with self.assertRaises(AtlasLesingFeil):
            les_atlas(ROT, ref="no/such/ref")

    def test_den_leste_commiten_er_den_refen_peker_paa(self):
        self.assertEqual(les_atlas(ROT)["commit"],
                         _git("rev-parse", "origin/main").strip())

    def test_foreldet_ref_er_synlig_i_resultatet(self):
        """`origin/main` may be stale — it is a remote-tracking ref.
        The function does not fetch by itself, but it REPORTS the full commit,
        so a stale ref stands in the result and not in the reader's assumption."""
        self.assertEqual(len(les_atlas(ROT, hent=False)["commit"]), 40)


class TestDokumentetPekerPaaKoden(unittest.TestCase):
    """The document shall not carry the rule itself — it cannot be tested.

    A prose rule can be turned around without any test failing (proven in round 1).
    The document shall therefore POINT AT the function, and this test holds
    the pointer fixed.
    """

    def test_dokumentet_navngir_den_kjorbare_regelen(self):
        t = (ROT / "docs" / "atlas-lesing.md").read_text(encoding="utf-8")
        self.assertIn("scripts/atlas_lesing.py", t,
                      "the document does not point at the executable rule")

    def test_funksjonen_som_dokumentet_peker_paa_finnes(self):
        self.assertTrue((ROT / "scripts" / "atlas_lesing.py").exists())


class TestFunksjonensKanter(unittest.TestCase):
    """Invalid JSON and a missing 'nodes' shall give AtlasLesingFeil, not a raw
    JSONDecodeError/KeyError. No silent or wrongly-typed error when a
    reader is to be able to trust the result."""

    def _repo(self, innhold: str) -> Path:
        r = Path(tempfile.mkdtemp())
        (r / "schema").mkdir()
        (r / "schema" / "regime_nodes.jsonld").write_text(innhold,
                                                          encoding="utf-8")
        for cmd in (["init", "-q"], ["add", "-A"],
                    ["-c", "user.name=t", "-c", "user.email=t@t",
                     "commit", "-qm", "x"]):
            subprocess.run(["git", "-C", str(r), *cmd],
                           capture_output=True, text=True)
        return r

    def test_ugyldig_json_gir_AtlasLesingFeil(self):
        with self.assertRaises(AtlasLesingFeil):
            les_atlas(self._repo("{not json"), ref="HEAD")

    def test_manglende_nodes_gir_AtlasLesingFeil(self):
        with self.assertRaises(AtlasLesingFeil):
            les_atlas(self._repo('{"something": "else"}'), ref="HEAD")

    def test_hent_oppdaterer_refen(self):
        """`hent=True` shall actually fetch. The reviewer proved it manually;
        it shall stand in the test set, not only in a report."""
        opp = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q", "--bare", opp],
                       capture_output=True, text=True)
        r = Path(tempfile.mkdtemp())
        for cmd in (["init", "-q", "-b", "main"],
                    ["remote", "add", "origin", opp]):
            subprocess.run(["git", "-C", str(r), *cmd],
                           capture_output=True, text=True)
        (r / "schema").mkdir()
        f = r / "schema" / "regime_nodes.jsonld"
        f.write_text('{"nodes": [{"id": "a"}]}', encoding="utf-8")
        for cmd in (["add", "-A"],
                    ["-c", "user.name=t", "-c", "user.email=t@t",
                     "commit", "-qm", "1"], ["push", "-q", "origin", "main"]):
            subprocess.run(["git", "-C", str(r), *cmd],
                           capture_output=True, text=True)
        forste = les_atlas(r, ref="origin/main", hent=True)["commit"]
        f.write_text('{"nodes": [{"id": "b"}]}', encoding="utf-8")
        for cmd in (["add", "-A"],
                    ["-c", "user.name=t", "-c", "user.email=t@t",
                     "commit", "-qm", "2"], ["push", "-q", "origin", "main"]):
            subprocess.run(["git", "-C", str(r), *cmd],
                           capture_output=True, text=True)
        andre = les_atlas(r, ref="origin/main", hent=True)["commit"]
        self.assertNotEqual(forste, andre, "hent=True did not fetch")


class TestIngenVertsspesifikkeReferanser(unittest.TestCase):
    r"""Rule 16: `docs/` is the Pages root — what stands there IS PUBLISHED.

    WHITELIST, not blacklist. See the module docstring for the history:
    three rounds of tightening were broken three times, and the review gave the
    answer that stands there. Here the opposite question is checked — is this a form
    we ALLOW?

    Allowed: repo-relative paths (two or more segments), http(s) links, and
    git-ref:path. Everything else that carries a path separator is a deviation.
    """

    # Allowed forms. `..` as a WHOLE segment points out of the repo and is
    # rejected — review finding round 7: ../../etc/passwd slipped through
    # because '..' matched [A-Za-z0-9_.-]+. Regex alone is the wrong tool
    # for this (lookahead became too weak), so the segments are checked directly.
    FORME = [
        re.compile(r"^[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+$"),
        re.compile(r"^https?://[^\s]+$"),
        # A git ref may have several segments (origin/feature/foo), capital
        # letters and hyphens (Release-2026), and refs/ form
        # (refs/heads/main). Review finding round 8: the previous form
        # required [a-z]+/[a-z]+ and rejected all of these.
        # The path part after the colon must START with an ordinary
        # character, not "/". Without this, `file:///Users/...` matched the
        # ref form with `file` as the ref and `///Users/...` as the path —
        # and rolled back to exactly what rounds 5-6 had closed.
        re.compile(r"^[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*:[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*$"),
    ]

    @staticmethod
    def _traverserer(t: str) -> bool:
        """`..` as its own segment, in the path or after the git ref's colon."""
        sti = t.split(":", 1)[1] if re.match(r"^[a-z]+/[a-z]+:", t) else t
        return ".." in sti.split("/")

    def _tillatt(self, t: str) -> bool:
        return (not self._traverserer(t)
                and any(r.match(t) for r in self.FORME))

    DEL = re.compile(r"[\s`|<>()\[\]{}\"'*,;]+")

    def _referanser(self, tekst: str):
        ut = []
        for linje in tekst.splitlines():
            if linje.startswith("#!"):
                continue
            for t in self.DEL.split(linje):
                if t in ("/", "\\"):
                    continue
                if "/" in t or "\\" in t or re.match(r"^[A-Za-z]:[\\/]", t):
                    ut.append(t)
        return ut

    def _avvik(self, tekst: str):
        return [t for t in self._referanser(tekst)
                if not self._tillatt(t)]

    def _docstring(self, sti: Path) -> str:
        t = sti.read_text(encoding="utf-8")
        i = t.index('"""') + 3
        return t[i:t.index('"""', i)]

    def test_publisert_dokument_har_bare_tillatte_referanser(self):
        self.assertEqual(
            self._avvik((ROT / "docs" / "atlas-lesing.md")
                        .read_text(encoding="utf-8")), [])

    def test_modulens_docstring_har_bare_tillatte_referanser(self):
        """Only the DOCSTRING — the file also contains code, and
        `except ... as e:` is not a path."""
        self.assertEqual(
            self._avvik(self._docstring(ROT / "scripts" / "atlas_lesing.py")),
            [])

    def test_volummodulens_docstring_har_bare_tillatte_referanser(self):
        """Same rule for the new module. This test came about through a
        measurement: `docs/atlas-lesing.md` got a reference to the house's
        tool path, and the guard above failed it. The rule therefore also applies to
        the module that was written together with it — otherwise the
        published document would have been protected and the code not."""
        self.assertEqual(
            self._avvik(self._docstring(ROT / "scripts" / "atlas_volum.py")),
            [])

    def test_hvitelisten_fanger_formene_seks_runder_fant(self):
        """Every form the blacklist let through the whitelist shall fail.
        Tested explicitly so the list does not drift back into an enumeration of
        evil forms — it is a whitelist of ALLOWED forms, and everything
        outside it fails regardless of which form it has."""
        for form in (
                "/Users", "/Users/morten/EFC", "C:\\Users\\morten",
                "path=/Users/morten/EFC", "|/Users/morten/EFC|",
                "<file:///Users/morten/EFC>", "file:///Users/morten/EFC",
                "file://localhost/Users/morten/EFC",
                "file://server/share/EFC",
                "\\\\?\\C:\\Users\\morten", "\\\\?\\UNC\\server\\share",
                "//server/share", "~/EFC", "\\\\server\\share\\EFC",
                "/opt/agent-work/EFC"):
            self.assertTrue(self._avvik("see " + form),
                            f"the whitelist lets through {form}")

    def test_hvitelisten_slipper_legitime_referanser_gjennom(self):
        for form in ("scripts/atlas_lesing.py", "docs/atlas-lesing.md",
                     "origin/main:schema/regime_nodes.jsonld",
                     "https://example.com/a", "10.5281/zenodo.123"):
            self.assertEqual(self._avvik("see " + form), [],
                             f"the whitelist rejected {form}")


if __name__ == "__main__":
    unittest.main()


class TestTraversering(unittest.TestCase):
    """Review finding round 7: the whitelist allowed `..` as a segment.

    `../../etc/passwd` and `foo/../../etc` slipped through because `..` matched
    `[A-Za-z0-9_.-]+`. A whitelist that allows traversal points out of the
    repo and is not a whitelist. The segment `..` is now rejected explicitly.
    """

    T = TestIngenVertsspesifikkeReferanser()

    def test_traversering_avvises(self):
        for form in ("../../etc/passwd", "../outside/file", "foo/../../etc",
                     "origin/main:../../etc", "a/./../b"):
            self.assertTrue(self.T._avvik("see " + form),
                            f"traversal slips through: {form}")

    def test_vanlige_dotnavn_avvises_ikke(self):
        """`.github/workflows/x.yml` and `a.b/c.d` are legitimate — dots are
        only dangerous as a WHOLE segment."""
        for form in (".github/workflows/x.yml", "a.b/c.d"):
            self.assertEqual(self.T._avvik("see " + form), [],
                             f"rejected a legitimate name: {form}")


class TestGitRefFormer(unittest.TestCase):
    """Review finding round 8: the whitelist was too NARROW, not too wide.

    It rejected origin/feature/foo:..., upstream/release/v1:... and
    Release-2026:... — all legitimate git refs. A whitelist that rejects
    real references is also an error; it forces rewrites of
    correct documentation.

    At the same time the extension shall NOT open up for traversal: `..` is forbidden
    as a segment both in the ref and in the path.
    """

    T = TestIngenVertsspesifikkeReferanser()

    def test_fler_segmenter_store_bokstaver_og_refs_form(self):
        for f in ("origin/main:schema/regime_nodes.jsonld",
                  "origin/feature/foo:schema/x.jsonld",
                  "upstream/release/v1:schema/x.jsonld",
                  "origin/Release-2026:schema/x.jsonld",
                  "refs/heads/main:schema/x.jsonld"):
            self.assertEqual(self.T._avvik("see " + f), [],
                             f"rejected a legitimate git ref: {f}")

    def test_utvidelsen_aapnet_ikke_for_traversering(self):
        for f in ("origin/main:../../etc", "../../etc/passwd", "../x",
                  "foo/../../etc", "origin/../..:x"):
            self.assertTrue(self.T._avvik("see " + f),
                            f"traversal slips through: {f}")
