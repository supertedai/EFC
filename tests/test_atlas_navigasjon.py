"""Validator for atlas navigation — can the atlas be used in ALL three layers?

Measured 2026-09-17, the first time anyone measured it:

    nodes    : 82
    engines  : 19   — 19/19 are reachable from a node
    NATS     : 118 topics in 39 domains — 34/118 are reachable

The atlas could be navigated in one layer and read in two. That is not the
same as it being USABLE: «where does this number come from?» requires going
from a topic on the bus to the node and the engine that produces it.

These tests do three things, and the third is the most important:

  1. Ties the navigation to the git ref — an uncommitted engine file must
     not be able to answer, the same rule `atlas_lesing` exists for.
  2. Requires that all 19 engines have a node. That is 100 % today, and it
     must not fall.
  3. LOCKS the coverage as a BASELINE. A gap that grows is a regression; a
     gap that shrinks must update the number ON PURPOSE, not by the test
     ceasing to see it.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

# The interpreter. The navigator runs as a subprocess, so it must be the
# one RUNNING this test. Measured 2026-09-18: these calls hardcoded a venv
# path that exists only on the Hermes host — in CI (ubuntu-latest) they
# died with FileNotFoundError.
PYTHON = sys.executable

import atlas_navigasjon  # noqa: E402

# Measured against origin/main 606b3127, 2026-09-17. These are not targets —
# they are a FLOOR. If they sink, something has become invisible to the
# navigation.
BASELINE_MOTORER_TOTALT = 32
BASELINE_MOTORER_NAADD = 17
BASELINE_EMNER_NAADD = 34
BASELINE_DOMENER_NAADD = 12
BASELINE_EMNER_TOTALT = 118


@pytest.fixture(scope="module")
def nav() -> dict:
    return atlas_navigasjon.naviger(REPO, ref="HEAD")


class TestAlleLagErSynlige:
    def test_tre_lag_er_talt(self, nav: dict) -> None:
        assert nav["lag"]["noder"] > 0, "the atlas must have nodes"
        assert nav["lag"]["motorer"] > 0, "the engines must be visible"
        assert nav["lag"]["emner"] > 0, "the bus must have topics"
        assert nav["lag"]["buss_domener"] > 0

    def test_hver_motor_har_en_node(self, nav: dict) -> None:
        """An engine without a node is a machine with no place on the map.

        It is the failure mode `verden.vaer` shows from the other side: a
        stream without a node. Measured 2026-09-17: all 19 have one.
        """
        mangler = [m for m in nav["kobling"]["motor_til_node"]
                   if not nav["kobling"]["motor_til_node"][m]]
        assert not mangler, f"engines without a node: {mangler}"
        assert len(nav["kobling"]["motor_til_node"]) == nav["lag"]["motorer"], (
            "every engine must have an entry in motor_til_node")

    def test_motordekningen_er_minst_maalet(self, nav: dict) -> None:
        """17 of 19 engines reach the bus — measured, not assumed.

        When I first wrote this test I assumed 19/19 and it passed. It was
        wrong: `grid_mikro` and `samfunn` have a node without
        `buss_domene`, and therefore no path from the stream back to the
        code that computed it. A test that passes on an ASSUMED number
        measures its own assumption — not reality.
        """
        assert nav["dekning"]["motorer"][1] == BASELINE_MOTORER_TOTALT, (
            f"the engine count changed: {nav['dekning']['motorer']}")
        assert nav["dekning"]["motorer"][0] >= BASELINE_MOTORER_NAADD, (
            f"engine coverage fell from {BASELINE_MOTORER_NAADD} to "
            f"{nav['dekning']['motorer'][0]}")


class TestHulleneErNavngitt:
    def test_hull_er_lister_ikke_tall(self, nav: dict) -> None:
        """A gap must be able to be NAMED. «27 domains are missing» is not
        actionable; «kosmos.asteroider is missing» is."""
        for navn, hull in nav["hull"].items():
            assert isinstance(hull, list), f"{navn} must be a list"
            if hull:
                assert all(isinstance(h, str) and h for h in hull), (
                    f"{navn} must name every gap")

    def test_dekningen_og_hullene_stemmer(self, nav: dict) -> None:
        """Coverage and gaps must count the same reality.

        Without this the two numbers could drift apart — and then the test
        above the BASELINE would be guarding a number that no longer means
        anything.
        """
        for navn, nokkel in (("emner", "emner_uten_node"),
                             ("domener", "domener_uten_node"),
                             ("motorer", "motorer_uten_buss")):
            naadd, totalt = nav["dekning"][navn]
            assert naadd + len(nav["hull"][nokkel]) == totalt, (
                f"{navn}: {naadd} naadd + {len(nav['hull'][nokkel])} hull "
                f"!= {totalt} totalt")

    def test_emner_uten_node_er_avledet_av_domener_uten_node(self, nav: dict) -> None:
        """Sanity: a topic cannot lack a node if its domain has one."""
        domener_hull = set(nav["hull"]["domener_uten_node"])
        for e in nav["hull"]["emner_uten_node"]:
            domene = ".".join(e.split(".")[:2])
            assert domene in domener_hull, (
                f"{e} is reported as a gap, but the domain {domene} has a "
                f"node — then the two measurements disagree")


class TestBaseline:
    def test_antallet_emner_er_uendret(self, nav: dict) -> None:
        assert nav["dekning"]["emner"][1] == BASELINE_EMNER_TOTALT, (
            f"the bus had {BASELINE_EMNER_TOTALT} topics; now "
            f"{nav['dekning']['emner'][1]}. If the bus changed, the "
            f"baseline must be updated ON PURPOSE — not by the test "
            f"ceasing to see.")

    def test_dekningen_synker_ikke(self, nav: dict) -> None:
        """The most important test: a gap that GROWS is a regression.

        A gap that shrinks is an improvement and must update the number —
        but only through a deliberate change, so that no node can disappear
        from the navigation without anyone seeing it.
        """
        naadd_emner = nav["dekning"]["emner"][0]
        naadd_domener = nav["dekning"]["domener"][0]
        assert naadd_emner >= BASELINE_EMNER_NAADD, (
            f"topic coverage fell from {BASELINE_EMNER_NAADD} to {naadd_emner} — "
            f"something has become invisible to the navigation")
        assert naadd_domener >= BASELINE_DOMENER_NAADD, (
            f"domain coverage fell from {BASELINE_DOMENER_NAADD} to {naadd_domener}")


class TestKildenErGitRefen:
    def test_ucommittert_motorfil_kan_ikke_svare(self, tmp_path: Path) -> None:
        """The same mutant trap as `atlas_lesing` — in the engine layer.

        An engine file that sits uncommitted on disk does not exist for the
        reader of the ref, and must not be able to show up in the
        navigation.
        """
        repo = tmp_path / "r"
        (repo / "efc_inference" / "engine").mkdir(parents=True)
        (repo / "schema").mkdir()
        (repo / "schema" / "regime_nodes.jsonld").write_text(
            '{"nodes": []}', encoding="utf-8")
        (repo / "schema" / "nats_domener.snapshot.json").write_text(
            '{"domener": {}}', encoding="utf-8")
        (repo / "efc_inference" / "engine" / "ekte.py").write_text(
            "x = 1\n", encoding="utf-8")
        for a in (("init", "-q"), ("config", "user.email", "t@t"),
                  ("config", "user.name", "t"), ("add", "-A"),
                  ("commit", "-q", "-m", "x")):
            subprocess.run(["git", "-C", str(repo), *a], check=True,
                           capture_output=True)
        # ...and a GHOST that only exists on disk
        (repo / "efc_inference" / "engine" / "spokelse.py").write_text(
            "y = 2\n", encoding="utf-8")

        motorer = atlas_navigasjon.les_motorer(repo, "HEAD")
        assert "ekte" in motorer
        assert "spokelse" not in motorer, (
            "the navigation read the working tree — an uncommitted engine "
            "file must not be able to answer")


class TestMotorKoblesTilRiktigNode:
    """Every engine must be coupled to the node that CARRIES its name.

    Review round 6: the mutant `if nid and m in nid` -> `if nid` coupled ALL
    engines to the first node, and all 9 tests passed. The coupling is not
    decoration: it feeds `motorer_uten_buss`, so a wrong coupling gives a
    wrong gap list — in silence, and the report would have looked just as
    convincing.
    """

    def test_hver_motor_peker_paa_en_node_som_inneholder_navnet(self, nav: dict) -> None:
        kobling = nav["kobling"]["motor_til_node"]
        assert kobling, "precondition: at least one engine is coupled"
        feil = {m: n for m, n in kobling.items() if m not in str(n)}
        assert not feil, (
            f"engines coupled to a node that does not contain the engine "
            f"name: {feil} — the coupling has fallen to «first node»")

    def test_koblingene_er_unike(self, nav: dict) -> None:
        """Two engines must not share a node unless the name is shared."""
        noder = list(nav["kobling"]["motor_til_node"].values())
        if len(noder) != len(set(noder)):
            from collections import Counter
            delte = [n for n, c in Counter(noder).items() if c > 1]
            for n in delte:
                motorer = [m for m, x in nav["kobling"]["motor_til_node"].items() if x == n]
                assert all(m in str(n) for m in motorer), (
                    f"several engines point at {n} without sharing the names: "
                    f"{motorer}")

    def test_en_kjent_motor_peker_paa_riktig_node(self, nav: dict) -> None:
        """A concrete anchor: `water` must point at `efc.water_phase_engine`."""
        kobling = nav["kobling"]["motor_til_node"]
        if "water" in kobling:
            assert "water" in str(kobling["water"]), (
                f"`water` points at {kobling['water']} — it must point at "
                f"the node carrying the name")


class TestUdekkedeGrener:
    """Branches review round 7 named as untested.

    These are not tightening — they are branches that have never been run. A
    branch that is never run is a branch nobody knows works.
    """

    def test_ugyldig_ref_reiser(self, tmp_path: Path) -> None:
        """`_git` fails -> NavigasjonFeil. Never a silent empty answer."""
        repo = tmp_path / "r"
        repo.mkdir()
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True,
                       capture_output=True)
        with pytest.raises(atlas_navigasjon.NavigasjonFeil):
            atlas_navigasjon.les_noder(repo, "does/not-exist")

    def test_malformed_json_reiser(self, tmp_path: Path) -> None:
        """Invalid JSON in the nodes must RAISE, not give an empty list."""
        repo = tmp_path / "r"
        repo.mkdir()
        (repo / "schema").mkdir()
        (repo / "schema" / "regime_nodes.jsonld").write_text("{not valid", encoding="utf-8")
        for a in (("init", "-q"), ("config", "user.email", "t@t"),
                  ("config", "user.name", "t"), ("add", "-A"),
                  ("commit", "-q", "-m", "x")):
            subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
        with pytest.raises(Exception):
            atlas_navigasjon.les_noder(repo, "HEAD")

    def test_tomt_snapshot_gir_null_emner(self, tmp_path: Path) -> None:
        """A snapshot without domains must give 0 topics, not crash."""
        repo = tmp_path / "r"
        (repo / "efc_inference" / "engine").mkdir(parents=True)
        (repo / "schema").mkdir()
        (repo / "schema" / "regime_nodes.jsonld").write_text('{"nodes": []}', encoding="utf-8")
        (repo / "schema" / "nats_domener.snapshot.json").write_text('{"domener": {}}', encoding="utf-8")
        for a in (("init", "-q"), ("config", "user.email", "t@t"),
                  ("config", "user.name", "t"), ("add", "-A"),
                  ("commit", "-q", "-m", "x")):
            subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
        d = atlas_navigasjon.naviger(repo, ref="HEAD")
        assert d["lag"]["emner"] == 0
        assert d["dekning"]["emner"] == (0, 0)

    def test_node_uten_id_ignoreres(self, tmp_path: Path) -> None:
        """A node without `id` must not be able to become a key in the
        coupling."""
        repo = tmp_path / "r"
        (repo / "efc_inference" / "engine").mkdir(parents=True)
        (repo / "schema").mkdir()
        (repo / "schema" / "regime_nodes.jsonld").write_text(
            '{"nodes": [{"buss_domene": "verden.energi"}, {"id": "ekte.node"}]}',
            encoding="utf-8")
        (repo / "schema" / "nats_domener.snapshot.json").write_text(
            '{"domener": {"verden.energi": {"emner": ["tilstand.x"]}}}', encoding="utf-8")
        for a in (("init", "-q"), ("config", "user.email", "t@t"),
                  ("config", "user.name", "t"), ("add", "-A"),
                  ("commit", "-q", "-m", "x")):
            subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
        d = atlas_navigasjon.naviger(repo, ref="HEAD")
        assert None not in d["kobling"]["domene_til_noder"].get("verden.energi", []), (
            "a node without an id ended up in the coupling — it cannot be "
            "named")


class TestEpistemiskTilstand:
    """What the loop CONTAINS — not just what it is coupled to.

    Measured 2026-09-17 by USING the lookup: 0 of 73 public nodes could be
    falsified by an observation, and 0 of 82 carried an outcome. Both were
    one-off observations from a conversation. Without a measurement they
    vanish when someone asks again — and an atlas that cannot say how thin
    it is implicitly says it is thick.

    The navigator now measures this too, so the numbers are reproducible and
    a fall is caught.
    """

    def test_falsifikatorer_er_talt(self, nav: dict) -> None:
        e = nav["epistemisk"]
        kf, kt = e["kan_felles"]
        mo, mt = e["maaler_eller_observert"]
        assert 0 <= kf <= kt and 0 <= mo <= mt
        # Together they must cover the WHOLE public atlas — otherwise there
        # are nodes no category owns, and they vanish from every number
        # without anyone seeing it.
        assert kt + mt == e["offentlige"], (
            f"the categories do not cover every public node: {kt} + {mt} "
            f"against {e['offentlige']}")

    def test_prediksjoner_og_oppgjoer_er_talt(self, nav: dict) -> None:
        e = nav["epistemisk"]
        for nokkel in ("prediksjon", "oppgjoer"):
            assert nokkel in e, f"missing the {nokkel} count: {e}"
            naadd, totalt = e[nokkel]
            assert 0 <= naadd <= totalt

    def test_offentlige_og_interne_er_skilt(self, nav: dict) -> None:
        """A gap among the PUBLIC ones is more serious than among the internal.

        The public ones are the published atlas; the internal ones are our
        own.
        """
        e = nav["epistemisk"]
        assert "kan_felles" in e and "maaler_eller_observert" in e, (
            f"the distinction between our claims and the rest is missing: {e}")
        off, tot = e["kan_felles"]
        assert tot > 0, "precondition: there are EFC claims"
        assert off <= tot

    def test_tallet_er_ikke_skjult(self, nav: dict) -> None:
        """When zero public nodes can be falsified, that must STAND — not be
        hidden.

        An atlas where this number is 0 and is not mentioned looks fuller
        than it is. That was the whole finding.
        """
        e = nav["epistemisk"]
        off, tot = e["kan_felles"]
        assert isinstance(off, int) and isinstance(tot, int), (
            "the number must be readable, also when it is 0")
        # and the other half must stand just as clearly
        mo, mt = e["maaler_eller_observert"]
        assert mo == mt, (
            f"{mt - mo} non-EFC nodes lack a reason for being measured")


class TestRefErFaktiskValgt:
    """`--ref` was silently ignored in the first version.

    The CLI only read `sys.argv[1]` and used the default ref otherwise. So
    `--ref origin/wt/vaer-node` actually measured `origin/main` — and
    answered with the old numbers without saying so. The instrument answered
    a neighbouring question, which is the failure class the rest of the
    house guards against.
    """

    def test_ref_maa_kunne_velges(self):
        import subprocess
        r = subprocess.run(
            [PYTHON,
             str(REPO / "scripts" / "atlas_navigasjon.py"), str(REPO),
             "--help"], capture_output=True, text=True)
        assert "--ref" in r.stdout, "the CLI does not offer --ref"

    def test_ugyldig_ref_feiler_hoeyt(self):
        """A ref that does not exist must say so — not fall back."""
        import subprocess
        r = subprocess.run(
            [PYTHON,
             str(REPO / "scripts" / "atlas_navigasjon.py"), str(REPO),
             "--ref", "does/not-exist"], capture_output=True, text=True)
        assert r.returncode != 0, "an unknown ref gave exit 0"


class TestFalsifiserbarhetsSkillet:
    """«Can be falsified» must not count missing instruments.

    `_epistemisk` counted EVERYTHING alike: 0 of 74. But 47 of the 74 are
    not EFC claims — they are established physics, observations and
    instruments. An instrument cannot be falsified by an observation; it IS
    the observation. Counting it as a gap makes the number worse than
    reality, and a number that lies downwards is as useless as one that
    lies upwards.
    """

    def test_kan_felles_teller_bare_efc_paastander(self):
        d = atlas_navigasjon.naviger(REPO, "HEAD")
        e = d["epistemisk"]
        assert "kan_felles" in e, "the distinction is missing"
        n, t_ = e["kan_felles"]
        assert t_ == 31, f"the denominator must be the 31 EFC nodes, got {t_}"
        # Measured 2026-09-20 (card t_2d7a6537): the two engines that carried
        # `terskel_ikke_fastsatt` in a fragment now carry the contract form and
        # count on the claim side: 27 -> 29. Same 31 EFC nodes.
        assert n == 29, (
            f"can be falsified: {n} of {t_} — expected 29 (2 stubs that "
            f"compute nothing, 85 measuring or established)")

    def test_instrumentene_telles_for_seg(self):
        d = atlas_navigasjon.naviger(REPO, "HEAD")
        e = d["epistemisk"]
        assert "maaler_eller_observert" in e, "the instrument nodes are not named"
        n, t_ = e["maaler_eller_observert"]
        assert n == t_ == 85, f"expected 80/80, got {n}/{t_}"


class TestMotornavnetErEntydig:
    """Engine -> node must be a RULE, not an incidental ordering.

    Measured 2026-09-18: `node_ider` was a SET, and the lookup took the first
    node that contained the engine name. `klima` matches four nodes
    (`efc.klima_engine` with a bus domain and three `verden.klima_*`
    without), so the answer depended on PYTHONHASHSEED: the same command on
    the same ref gave «31/32 reachable · GAP klima» in two of five runs and
    «32/32» in three. A gap that comes and goes is not believed when it is
    real.
    """

    def test_samme_svar_uansett_hashseed(self):
        """Two processes, two seeds, ONE answer. That is the whole
        requirement."""
        kode = (
            "import json, sys; sys.path.insert(0, 'scripts');"
            "import atlas_navigasjon as N;"
            "d = N.naviger('.', 'HEAD');"
            "print(json.dumps({'hull': d['hull']['motorer_uten_buss'],"
            " 'dekning': d['dekning']['motorer'],"
            " 'kart': d['kobling']['motor_til_node']}, sort_keys=True))"
        )
        svar = []
        for froe in ("0", "1", "12345"):
            r = subprocess.run(
                [sys.executable, "-c", kode], cwd=REPO,
                capture_output=True, text=True, timeout=120,
                env={"PYTHONHASHSEED": froe, "PATH": "/usr/bin:/bin"})
            assert r.returncode == 0, r.stderr[-400:]
            svar.append(r.stdout.strip())
        assert len(set(svar)) == 1, (
            "same question, different answers:\n" + "\n".join(svar))

    def test_motornavnet_peker_paa_motornoden(self):
        d = atlas_navigasjon.naviger(REPO, "HEAD")
        kart = d["kobling"]["motor_til_node"]
        assert kart.get("klima") == "efc.klima_engine", kart.get("klima")
        # The engine names do not only point into the efc namespace: the
        # homo regime's engines point at the `homo.*` nodes, and that is
        # correct. The requirement is that every pointer lands on a node that
        # EXISTS — a dead pointer is an answer that looks like a coupling.
        kjente = {n["id"] for n in atlas_navigasjon.les_noder(REPO, "HEAD")}
        doede = {m: nid for m, nid in kart.items() if nid not in kjente}
        assert not doede, doede

    def test_flertydige_navn_meldes(self):
        """A rule that chooses must also say what it chose between."""
        d = atlas_navigasjon.naviger(REPO, "HEAD")
        assert "motor_flertydig" in d["kobling"], "the ambiguity is invisible"
        for m, kandidater in d["kobling"]["motor_flertydig"].items():
            assert len(kandidater) > 1, (m, kandidater)
            assert d["kobling"]["motor_til_node"][m] in kandidater
