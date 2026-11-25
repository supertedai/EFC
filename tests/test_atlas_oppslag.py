"""Tests for the atlas lookup — the entry point to the atlas.

Measured need 2026-09-17: the atlas had a reader (`les_atlas`) but no
entry point. The price of consulting it was loading all 82 nodes and
searching by hand, so it never happened spontaneously in conversation.
The atlas was a catalogue you could read, not a reference work you could
query.

These tests defended THREE things, and they are not the same:

  1. The lookup reads from the GIT REF, not from the working tree. The
     same failure mode `les_atlas` exists to prevent — a copy that
     answers reads like a living atlas. A mutant that switches to the
     working tree must be killed.

  2. An empty answer is an ANSWER. "The atlas does not know" must be
     distinguishable from "the lookup failed". A test that only counts
     hits cannot see that.

  3. Each hit names its epistemic status. A reference work that lists
     names without saying what is known and what is stipulated moves the
     work back to the reader.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import atlas_lesing  # noqa: E402


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return p.stdout


@pytest.fixture
def ekte_repo() -> Path:
    """The repo the tests run in — the atlas exists on origin/main or HEAD."""
    return REPO


class TestOppslagetSvarer:
    def test_eierens_spoersmaal_loser_riktig_akse(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "hva maaler", ref="HEAD")
        assert svar["akse"] == "measure.target"
        assert svar["antall"] == len(atlas_lesing.roter_akse(
            atlas_lesing.les_atlas(ekte_repo, ref="HEAD"), "measure.target"))
        assert svar["hull"] is False

    def test_hvem_maaler_loser_measurer_akse(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "hvem maaler", ref="HEAD")
        assert svar["akse"] == "measure.measurer"
        assert svar["antall"] > 0

    def test_ukjent_spoersmaalsform_er_fortsatt_et_hull(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "hvilken drage maaler", ref="HEAD")
        assert svar["akse"] is None
        assert svar["hull"] is True

    def test_kjent_emne_gir_treff(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "h2o", ref="HEAD")
        assert svar["antall"] > 0, "h2o must exist in the atlas"
        assert svar["hull"] is False

    def test_ukjent_emne_er_et_hull_ikke_en_feil(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "kvantegravitasjon_xyzzy", ref="HEAD")
        assert svar["antall"] == 0
        assert svar["hull"] is True, (
            "an empty answer must be NAMED as a hole — 'the atlas does not "
            "know' is an answer, and must be distinguishable from 'the "
            "lookup failed'")

    def test_soket_er_case_insensitivt(self, ekte_repo: Path) -> None:
        a = atlas_lesing.finn(ekte_repo, "H2O", ref="HEAD")
        b = atlas_lesing.finn(ekte_repo, "h2o", ref="HEAD")
        assert a["antall"] == b["antall"] > 0


class TestKildenErNavngitt:
    def test_svaret_navngir_commit(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "h2o", ref="HEAD")
        assert svar["commit"] == _git(ekte_repo, "rev-parse", "HEAD").strip()
        assert svar["kilde"].startswith("git:")

    def test_oppslaget_leser_ikke_arbeidsstreet(self, tmp_path: Path) -> None:
        """MUTANT KILL: a deviating working copy must not be able to answer.

        This is the whole reason the module exists. Builds a working copy
        with a node that does NOT exist in the git tree, and requires that
        the lookup does not see it when reading from the ref.
        """
        repo = tmp_path / "repo"
        repo.mkdir()
        _git(repo, "init", "-q")
        _git(repo, "config", "user.email", "t@t")
        _git(repo, "config", "user.name", "t")
        (repo / "schema").mkdir()
        (repo / "schema" / "regime_nodes.jsonld").write_text(
            json.dumps({"nodes": [{"id": "ekte.node", "synlighet": "offentlig"}]}),
            encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "x")

        # The working tree gets a node that is NOT in the git tree.
        (repo / "schema" / "regime_nodes.jsonld").write_text(
            json.dumps({"nodes": [{"id": "ekte.node"}, {"id": "spokelse.node"}]}),
            encoding="utf-8")

        svar = atlas_lesing.finn(repo, "spokelse", ref="HEAD")
        assert svar["antall"] == 0, (
            "the lookup read the working tree — that is the failure mode "
            "the module exists to prevent. An uncommitted node must not "
            "answer.")
        assert svar["hull"] is True

        # ...and the real node must be found, from the git tree.
        assert atlas_lesing.finn(repo, "ekte", ref="HEAD")["antall"] == 1


class TestEpistemiskStatus:
    def test_hvert_treff_navngir_status(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "h2o", ref="HEAD")
        for t in svar["treff"]:
            assert "synlighet" in t, "a hit must say whether the node is published"
            assert "har_falsifikator" in t, (
                "a hit must say whether the node can be killed by an "
                "observation — otherwise the reader cannot tell a test "
                "from a claim")
            assert "har_prediksjon" in t
            assert "har_oppgjoer" in t

    def test_pending_settlement_is_not_read_as_settled(self, ekte_repo: Path) -> None:
        """A settlement awaiting an arbiter is pending, not settled.

        Regression for the bug where a node with a `settlement` record whose
        outcome is "waiting for arbiter" was reported "is settled" — telling a
        user a pending result is final. Under the allowlist (Option A), only
        the writer's terminal tokens read "settled"; a structured payload
        (weather, blocked, revised) is a record, not a verdict — it reads no
        marker and awaits #634's record_only. The two groups are named
        explicitly, so a future terminal node cannot silently flip the test's
        meaning.
        """
        by_id = {n["id"]: n for n in atlas_lesing.les_atlas(ekte_repo, ref="HEAD")["noder"]}
        pending = ["obs.bao", "obs.fsigma8", "efc.growth_engine"]
        recorded = ["verden.vaer", "opus.dommekraft", "kosmos.asteroider"]
        for nid in pending + recorded:
            assert nid in by_id, f"{nid} must exist in the bank"

        for pid in pending:
            assert atlas_lesing._oppgjoer_status(by_id[pid]) == "pending", (
                f"{pid}: a settlement awaiting its arbiter must read 'pending', "
                "never 'is settled'")
            # the render path: finn() must carry the same status into the
            # treff dict the renderer consumes — the original bug was the
            # rendered "is settled" text, not the classifier.
            treff = [t for t in atlas_lesing.finn(ekte_repo, pid, ref="HEAD")["treff"]
                     if t["id"] == pid]
            assert treff, f"pending node {pid} not reachable through finn()"
            assert treff[0]["oppgjoer_status"] == "pending", (
                f"{pid}: the render path must carry 'pending', never 'is settled'. "
                "If an arbiter has landed, update this expectation — "
                "pending->settled is a legitimate change, not a regression.")
        for rid in recorded:
            assert atlas_lesing._oppgjoer_status(by_id[rid]) is None, (
                f"{rid}: a structured payload is a record, not a verdict — "
                "it must not read 'settled' (record_only is #634's job)")
            # the render path: a structured payload must stay unmarked all
            # the way through the lookup, not just at the classifier.
            treff = [t for t in atlas_lesing.finn(ekte_repo, rid, ref="HEAD")["treff"]
                     if t["id"] == rid]
            assert treff, f"payload node {rid} not reachable through finn()"
            assert treff[0]["oppgjoer_status"] is None, (
                f"{rid}: the render path must not mark a payload 'settled'. "
                "If record_only lands, update this expectation — do not delete "
                "the assertion.")

    def test_settlement_without_outcome_is_not_settled(self) -> None:
        """A settlement record with no outcome must not fall through to 'settled'.

        The classifier's else-branch once labeled an empty/missing outcome as
        settled. No outcome is not a final outcome.
        """
        assert atlas_lesing._oppgjoer_status({}) is None
        assert atlas_lesing._oppgjoer_status({"settlement": {}}) is None
        assert atlas_lesing._oppgjoer_status({"settlement": {"outcome": ""}}) is None
        assert atlas_lesing._oppgjoer_status({"settlement": {"outcome": "   "}}) is None
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": "waiting for arbiter: DESI DR2 full-shape"}}
        ) == "pending"
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": '{"air_temperature": 10.0}'}}
        ) is None

    def test_settlement_result_with_correlation_matching(self) -> None:
        """The `settlement_result` layer must classify a landed verdict.

        Four cases the fix is bound to, plus the fail-closed edges:

          * a pending contract (no landed result) -> "pending";
          * a confirmed result whose correlation matches -> "settled";
          * a contradicted result whose correlation matches -> "settled"
            (a negative result is still a landed result);
          * missing, mismatched or unknown correlation / outcome / node ->
            never "settled" and never "pending": a present-but-invalid verdict
            gets its own marker, "invalid";
          * a landed verdict supersedes a static "waiting for arbiter".

        Correlation is compared strictly (no case folding); `node` is
        mandatory — the writer always writes it, and a verdict without it
        fails closed.
        """
        base = {"id": "efc.test", "settlement": {"correlation": "corr-1"}}

        # 1. Pending: awaiting arbiter, no landed result.
        assert atlas_lesing._oppgjoer_status({
            **base,
            "settlement": {"correlation": "corr-1",
                           "outcome": "waiting for arbiter: DESI DR2 full-shape"},
        }) == "pending"

        # 2. Confirmed, matching correlation and node.
        assert atlas_lesing._oppgjoer_status({
            **base,
            "settlement_result": {"node": "efc.test", "correlation": "corr-1",
                                  "outcome": "confirmed"},
        }) == "settled"

        # 3. Contradicted, matching correlation and node.
        assert atlas_lesing._oppgjoer_status({
            **base,
            "settlement_result": {"node": "efc.test", "correlation": "corr-1",
                                  "outcome": "contradicted"},
        }) == "settled"

        # 4a. Missing correlation -> invalid (unverifiable, never pending).
        assert atlas_lesing._oppgjoer_status({
            **base,
            "settlement_result": {"node": "efc.test", "outcome": "confirmed"},
        }) == "invalid"

        # 4b. Mismatched correlation -> invalid.
        assert atlas_lesing._oppgjoer_status({
            **base,
            "settlement_result": {"node": "efc.test", "correlation": "wrong-corr",
                                  "outcome": "confirmed"},
        }) == "invalid"

        # 4c. Wrong node -> invalid.
        assert atlas_lesing._oppgjoer_status({
            **base,
            "settlement_result": {"node": "other.node", "correlation": "corr-1",
                                  "outcome": "confirmed"},
        }) == "invalid"

        # 4d. Unknown outcome token -> invalid.
        assert atlas_lesing._oppgjoer_status({
            **base,
            "settlement_result": {"node": "efc.test", "correlation": "corr-1",
                                  "outcome": "inconclusive"},
        }) == "invalid"

        # 4e. A verdict without a `node` field is invalid — node is now
        #      mandatory (the writer always writes it).
        assert atlas_lesing._oppgjoer_status({
            **base,
            "settlement_result": {"correlation": "corr-1", "outcome": "confirmed"},
        }) == "invalid"

        # 5. A landed verdict supersedes a static "waiting for arbiter".
        assert atlas_lesing._oppgjoer_status({
            "id": "efc.test",
            "settlement": {"correlation": "corr-1",
                           "outcome": "waiting for arbiter: DESI DR2 full-shape"},
            "settlement_result": {"node": "efc.test", "correlation": "corr-1",
                                  "outcome": "contradicted"},
        }) == "settled"

        # 6. No static settlement -> a lone result cannot settle (correlation
        #    is the declared key and it lives in the static contract) — and an
        #    unverifiable verdict is invalid, not absent.
        assert atlas_lesing._oppgjoer_status({
            "id": "efc.test",
            "settlement_result": {"node": "efc.test", "correlation": "corr-1",
                                  "outcome": "confirmed"},
        }) == "invalid"

        # 7. A non-dict settlement_result is corrupt: it must not fall
        #    through and read as "still awaiting" — it reads "invalid".
        assert atlas_lesing._oppgjoer_status({
            "id": "efc.test",
            "settlement": {"correlation": "corr-1",
                           "outcome": "waiting for arbiter: DESI DR2 full-shape"},
            "settlement_result": "garbage",
        }) == "invalid"

        # 8. An empty settlement_result (the writer's unfilled container)
        #    falls through to the static contract — still pending.
        assert atlas_lesing._oppgjoer_status({
            "id": "efc.test",
            "settlement": {"correlation": "corr-1",
                           "outcome": "waiting for arbiter: DESI DR2 full-shape"},
            "settlement_result": {},
        }) == "pending"

    def test_static_allowlist_rejects_nonterminal_outcomes(self) -> None:
        """Option A: the static path is an allowlist, not a blacklist.

        Only the writer's terminal tokens read 'settled'; pending phrases
        read 'pending'; everything else — non-string, a structured payload,
        or an unknown token — reads no marker (None), never 'settled'.
        """
        # terminal tokens
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": "confirmed"}}) == "settled"
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": "contradicted"}}) == "settled"
        # outcome token is case-insensitive (a semantic label).
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": "CONFIRMED"}}) == "settled"
        # pending phrase
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": "waiting for arbiter: DESI DR2 full-shape"}}) == "pending"
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": "waiting for arbiter"}}) == "pending"
        # unknown / non-terminal tokens -> no marker
        assert atlas_lesing._oppgjoer_status({"settlement": {"outcome": "pending"}}) is None
        assert atlas_lesing._oppgjoer_status({"settlement": {"outcome": "inconclusive"}}) is None
        assert atlas_lesing._oppgjoer_status({"settlement": {"outcome": "not decided"}}) is None
        # non-string outcomes -> no marker
        assert atlas_lesing._oppgjoer_status({"settlement": {"outcome": None}}) is None
        assert atlas_lesing._oppgjoer_status({"settlement": {"outcome": 0}}) is None
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": {"status": "unknown"}}}) is None
        # structured payloads (a record, not a verdict)
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": '{"kildens_ord": "blokkert"}'}}) is None
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": '{"utfall": "revidert"}'}}) is None
        # substring near-misses: not final, and not falsely pending
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": "waiting for arbitrator: DESI"}}) is None
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": "not waiting for arbiter: resolved"}}) is None
        # near-misses: a pending phrase must be followed by a separator
        # (colon, whitespace) or end-of-string — a longer word or stray
        # punctuation is not the phrase.
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": "waiting for arbiterial"}}) is None
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": "waiting for arbiter2: not a valid marker"}}) is None
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": "awaiting arbiters"}}) is None
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": "waiting for arbiter_foo"}}) is None
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": "waiting for arbiter!garbage"}}) is None
        assert atlas_lesing._oppgjoer_status(
            {"settlement": {"outcome": "waiting for arbiter-garbage"}}) is None

    def test_runtime_verdict_rejects_invalid(self) -> None:
        """The runtime path validates outcome, node and correlation strictly.

        Every rejection carries the "invalid" marker: the verdict slot is
        written, so an unverifiable value in it is an integrity anomaly — not
        the absence of a verdict (None) and not "still awaiting" (pending).
        """
        base = {"id": "efc.test", "settlement": {"correlation": "corr-1"}}
        # node: null is present-but-invalid, not absent.
        assert atlas_lesing._oppgjoer_status({
            **base,
            "settlement_result": {"node": None, "correlation": "corr-1",
                                  "outcome": "confirmed"},
        }) == "invalid"
        # absent node is now mandatory -> invalid.
        assert atlas_lesing._oppgjoer_status({
            **base,
            "settlement_result": {"correlation": "corr-1", "outcome": "confirmed"},
        }) == "invalid"
        # explicit settlement_result: null is a value the writer never writes
        # (it setdefaults {}) and the closed schema does not define: an
        # integrity anomaly marked "invalid" — never absent, never "pending".
        assert atlas_lesing._oppgjoer_status({
            "id": "efc.test",
            "settlement": {"correlation": "corr-1",
                           "outcome": "waiting for arbiter: DESI DR2 full-shape"},
            "settlement_result": None,
        }) == "invalid"
        # non-dict verdicts (string, list, number, empty string) -> anomaly.
        for bad in ("garbage", [], 0, ""):
            assert atlas_lesing._oppgjoer_status({
                "id": "efc.test",
                "settlement": {"correlation": "corr-1",
                               "outcome": "waiting for arbiter: DESI DR2 full-shape"},
                "settlement_result": bad,
            }) == "invalid"
        # outcome token is case-insensitive (a semantic label); the
        # correlation is strict (an identifier).
        assert atlas_lesing._oppgjoer_status({
            **base,
            "settlement_result": {"node": "efc.test", "correlation": "corr-1",
                                  "outcome": "Confirmed"},
        }) == "settled"
        assert atlas_lesing._oppgjoer_status({
            **base,
            "settlement_result": {"node": "efc.test", "correlation": "CORR-1",
                                  "outcome": "confirmed"},
        }) == "invalid"

    def test_arbiter_correlation_matches_claim_node(self) -> None:
        """Every arbiter's bridge correlation must equal its claim node's
        declared settlement correlation.

        The reader validates a landed verdict by exact correlation match. That
        match is only safe if the writer's bridge and the claim node's contract
        carry the SAME correlation string — a drift here would make a
        legitimate verdict silently fail closed. Pin it for every arbiter.
        """
        bank = json.loads(
            (REPO / "schema" / "regime_nodes.jsonld").read_text(encoding="utf-8"))
        nodes = {n["id"]: n for n in bank["nodes"]}
        arbiter_files = sorted((REPO / "schema").glob("*.arbiter.json"))
        assert arbiter_files, "precondition: at least one arbiter declaration"
        for arb_path in arbiter_files:
            arb = json.loads(arb_path.read_text(encoding="utf-8"))
            bro_path = arb_path.with_name(
                arb_path.name.replace(".arbiter.json", ".bro.json"))
            bro = json.loads(bro_path.read_text(encoding="utf-8"))
            claim = nodes[arb["claim_node"]]
            assert arb["claim_node"] == claim["id"]
            assert bro["correlation"] == claim["settlement"]["correlation"], (
                f"{arb_path.name}: bridge correlation {bro['correlation']!r} != "
                f"{arb['claim_node']}.settlement.correlation "
                f"{claim['settlement']['correlation']!r}")

    def test_har_oppgjoer_counts_a_landed_result(self) -> None:
        """A node with a landed result (or a non-empty contract) 'has
        settlement'; an empty contract or nothing does not."""
        assert atlas_lesing._har_oppgjoer(
            {"id": "x", "settlement_result": {"outcome": "confirmed"}}) is True
        assert atlas_lesing._har_oppgjoer(
            {"id": "x", "settlement": {"correlation": "c"}}) is True
        assert atlas_lesing._har_oppgjoer({"id": "x", "settlement": {}}) is False
        assert atlas_lesing._har_oppgjoer({"id": "x"}) is False

    def test_har_oppgjoer_and_status_agree_for_record_only(self) -> None:
        """A structured-payload record 'has settlement' but is not a verdict:
        har_oppgjoer=True + status=None, pinned as the pair the review asked
        about."""
        node = {"id": "x", "settlement": {"outcome": '{"kildens_ord": "blokkert"}'}}
        assert atlas_lesing._har_oppgjoer(node) is True
        assert atlas_lesing._oppgjoer_status(node) is None

    def test_settlement_correlations_are_globally_unique(self) -> None:
        """No two nodes may share a settlement correlation.

        The reader validates a landed verdict against the declared settlement
        correlation. That match is only safe while every settlement
        correlation names exactly one node — a shared correlation would let a
        verdict settle the wrong node. Pin the invariant so a future collision
        fails here, not silently in the reader.
        """
        bank = json.loads(
            (REPO / "schema" / "regime_nodes.jsonld").read_text(encoding="utf-8"))
        seen: dict[str, str] = {}
        for n in bank["nodes"]:
            s = n.get("settlement")
            if not isinstance(s, dict):
                continue
            c = s.get("correlation")
            if not c:
                continue
            assert c not in seen, (
                f"correlation {c!r} is shared by {seen[c]!r} and {n['id']!r}")
            seen[c] = n["id"]

    def test_falsifikator_telles_riktig(self, ekte_repo: Path) -> None:
        """The nodes with `ville_falsifisere` must be flagged — the others not."""
        atlas = atlas_lesing.les_atlas(ekte_repo, ref="HEAD")
        with_falsifier = [n["id"] for n in atlas["noder"]
                          if "ville_falsifisere" in json.dumps(n, ensure_ascii=False)]
        assert with_falsifier, "precondition: some nodes have ville_falsifisere"
        svar = atlas_lesing.finn(ekte_repo, with_falsifier[0].split(".")[0], ref="HEAD")
        merket = [t for t in svar["treff"] if t["id"] == with_falsifier[0]]
        assert merket and merket[0]["har_falsifikator"] is True

    def test_hull_sier_hva_som_ble_sokt(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "finnesikke", ref="HEAD")
        assert svar["emne"] == "finnesikke", (
            "a hole must name what was searched for — otherwise the reader "
            "cannot see whether the hole comes from the search or the atlas")


class TestSettlementStatusMatrix:
    """The settlement-status edges the panels asked to pin (Luna #9, DeepSeek
    #4): the runtime branch is unexercised by live data (0 bank nodes carry
    settlement_result), so its fail-closed edges are pinned here rather than
    observed in the bank."""

    def test_empty_result_falls_through_to_static_pending(self) -> None:
        node = {"id": "efc.test",
                "settlement": {"correlation": "corr-1",
                               "outcome": "waiting for arbiter: DESI DR2 full-shape"},
                "settlement_result": {}}
        assert atlas_lesing._oppgjoer_status(node) == "pending"

    def test_empty_result_falls_through_to_static_terminal(self) -> None:
        node = {"id": "efc.test",
                "settlement": {"correlation": "corr-1", "outcome": "confirmed"},
                "settlement_result": {}}
        assert atlas_lesing._oppgjoer_status(node) == "settled"

    def test_whitespace_contract_correlation_is_invalid(self) -> None:
        node = {"id": "efc.test",
                "settlement": {"correlation": "   "},
                "settlement_result": {"node": "efc.test", "correlation": "   ",
                                      "outcome": "confirmed"}}
        assert atlas_lesing._oppgjoer_status(node) == "invalid"

    def test_padded_correlation_is_not_an_exact_match(self) -> None:
        # Correlation is an identifier compared exactly; only a blank value is
        # rejected by .strip(). A padded value is not a match for the clean
        # one, so it reads "invalid" (the writer always writes clean values).
        node = {"id": "efc.test",
                "settlement": {"correlation": " c "},
                "settlement_result": {"node": "efc.test", "correlation": "c",
                                      "outcome": "confirmed"}}
        assert atlas_lesing._oppgjoer_status(node) == "invalid"

    def test_outcome_whitespace_is_stripped(self) -> None:
        node = {"id": "efc.test",
                "settlement": {"correlation": "corr-1"},
                "settlement_result": {"node": "efc.test", "correlation": "corr-1",
                                      "outcome": " CONFIRMED "}}
        assert atlas_lesing._oppgjoer_status(node) == "settled"

    def test_valid_result_without_static_settlement_is_invalid(self) -> None:
        node = {"id": "efc.test",
                "settlement_result": {"node": "efc.test", "correlation": "corr-1",
                                      "outcome": "confirmed"}}
        assert atlas_lesing._oppgjoer_status(node) == "invalid"

    def test_node_without_id_is_invalid(self) -> None:
        node = {"settlement": {"correlation": "corr-1"},
                "settlement_result": {"node": "efc.test", "correlation": "corr-1",
                                      "outcome": "confirmed"}}
        assert atlas_lesing._oppgjoer_status(node) == "invalid"

    @pytest.mark.parametrize("outcome", ["pending", "inconclusive", "maybe"])
    def test_runtime_non_terminal_outcome_is_invalid(self, outcome: str) -> None:
        node = {"id": "efc.test",
                "settlement": {"correlation": "corr-1"},
                "settlement_result": {"node": "efc.test", "correlation": "corr-1",
                                      "outcome": outcome}}
        assert atlas_lesing._oppgjoer_status(node) == "invalid"

    def test_har_oppgjoer_presence_not_judgment_on_malformed_result(self) -> None:
        node = {"id": "efc.test", "settlement_result": "garbage"}
        assert atlas_lesing._har_oppgjoer(node) is True
        assert atlas_lesing._oppgjoer_status(node) == "invalid"

    def test_bank_correlations_carry_no_whitespace(self) -> None:
        bank = json.loads(
            (REPO / "schema" / "regime_nodes.jsonld").read_text(encoding="utf-8"))
        for n in bank["nodes"]:
            s = n.get("settlement")
            if not isinstance(s, dict):
                continue
            c = s.get("correlation")
            if isinstance(c, str) and c:
                assert c == c.strip(), (
                    f"{n['id']}: correlation {c!r} carries whitespace")


class TestUgyldigSettlementResult:
    """A corrupt verdict gets its OWN marker — never the absence answer.

    Measured 2026-11-18 (panel: confirmed independently as a BLOCK finding):
    `_oppgjoer_status` failed closed to None for a present-but-invalid
    `settlement_result`. None is also the answer for "this node carries no
    settlement information at all", so corruption collapsed into absence —
    and a hit that says nothing reads as "nothing to report". The marker is
    "invalid": a third state, distinct from absent (None), pending and
    settled.
    """

    #: Every corruption class the reader must name. None of them may borrow
    #: the absence answer.
    UGYLDIGE = [
        pytest.param(None, id="explicit-null"),
        pytest.param("garbage", id="string"),
        pytest.param([], id="empty-list"),
        pytest.param(0, id="zero"),
        pytest.param("", id="empty-string"),
        pytest.param({"node": "efc.test", "outcome": "confirmed"},
                     id="missing-correlation"),
        pytest.param({"node": "efc.test", "correlation": "wrong",
                      "outcome": "confirmed"}, id="wrong-correlation"),
        pytest.param({"node": "other.node", "correlation": "corr-1",
                      "outcome": "confirmed"}, id="wrong-node"),
        pytest.param({"node": "efc.test", "correlation": "corr-1"},
                     id="missing-outcome"),
        pytest.param({"node": "efc.test", "correlation": "corr-1",
                      "outcome": "inconclusive"}, id="unknown-outcome"),
        pytest.param({"node": "efc.test", "correlation": "corr-1",
                      "outcome": None}, id="null-outcome"),
    ]

    @pytest.mark.parametrize("result", UGYLDIGE)
    def test_corrupt_verdict_is_named_not_silenced(self, result) -> None:
        node = {"id": "efc.test",
                "settlement": {"correlation": "corr-1",
                               "outcome": "waiting for arbiter: DESI DR2"},
                "settlement_result": result}
        assert atlas_lesing._oppgjoer_status(node) == "invalid", (
            f"a present-but-invalid settlement_result ({result!r}) must read "
            "'invalid' — None is the absence answer and must not be borrowed")

    def test_absent_result_is_still_absent(self) -> None:
        """The marker must not turn 'nothing written' into an anomaly."""
        node = {"id": "efc.test", "settlement": {"correlation": "corr-1"}}
        assert atlas_lesing._oppgjoer_status(node) is None
        # the contract is present, the verdict is not: presence + no marker
        assert atlas_lesing._har_oppgjoer(node) is True
        assert atlas_lesing._oppgjoer_status({"id": "efc.test"}) is None
        assert atlas_lesing._har_oppgjoer({"id": "efc.test"}) is False

    def test_unfilled_container_is_not_invalid(self) -> None:
        """`{}` is the writer's unfilled container, not corruption."""
        node = {"id": "efc.test",
                "settlement": {"correlation": "corr-1", "outcome": "confirmed"},
                "settlement_result": {}}
        assert atlas_lesing._oppgjoer_status(node) == "settled"
        # the empty container is not settlement info on its own ...
        assert atlas_lesing._har_oppgjoer({"id": "efc.test",
                                           "settlement_result": {}}) is False
        # ... and the non-empty contract still is.
        assert atlas_lesing._har_oppgjoer(node) is True

    def test_invalid_suppresses_the_static_contract(self) -> None:
        """Corruption must not be downgraded to 'pending' by the contract.

        The static contract still says "waiting for arbiter"; if the invalid
        branch fell through, a corrupt verdict would read as merely awaiting —
        the same masking the marker exists to prevent, one step later.
        """
        for static, masked in (
            ({"correlation": "corr-1",
              "outcome": "waiting for arbiter: DESI DR2"}, "pending"),
            ({"correlation": "corr-1", "outcome": "confirmed"}, "settled"),
        ):
            node = {"id": "efc.test", "settlement": static,
                    "settlement_result": "garbage"}
            assert atlas_lesing._oppgjoer_status(node) == "invalid", masked

    @pytest.mark.parametrize("presence", [None, "garbage", 0, []])
    def test_presence_flag_counts_a_written_verdict_slot(self, presence) -> None:
        """An explicit null or a non-dict is PRESENT: the anomaly must be
        visible as presence + "invalid", not as "no settlement info"."""
        node = {"id": "efc.test", "settlement_result": presence}
        assert atlas_lesing._har_oppgjoer(node) is True
        assert atlas_lesing._oppgjoer_status(node) == "invalid"

    @staticmethod
    def _repo_with_invalid_result(tmp_path: Path) -> Path:
        repo = tmp_path / "repo"
        repo.mkdir()
        _git(repo, "init", "-q")
        _git(repo, "config", "user.email", "t@t")
        _git(repo, "config", "user.name", "t")
        (repo / "schema").mkdir()
        (repo / "schema" / "regime_nodes.jsonld").write_text(
            json.dumps({"nodes": [{
                "id": "test.invalid", "synlighet": "offentlig",
                "settlement": {"correlation": "c-1",
                               "outcome": "waiting for arbiter: DESI DR2"},
                "settlement_result": None,
            }]}), encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "x")
        return repo

    def test_lookup_carries_the_marker(self, tmp_path: Path) -> None:
        """The marker must reach the hit dict the renderer consumes.

        A classifier that says "invalid" while the lookup still answers
        "nothing" would leave the reader exactly where the panel found them.
        """
        repo = self._repo_with_invalid_result(tmp_path)
        svar = atlas_lesing.finn(repo, "test.invalid", ref="HEAD")
        treff = [t for t in svar["treff"] if t["id"] == "test.invalid"]
        assert treff, "precondition: the invalid node must be reachable"
        assert treff[0]["oppgjoer_status"] == "invalid"
        assert treff[0]["har_oppgjoer"] is True

    def test_cli_prints_the_marker(self, tmp_path: Path) -> None:
        """The command line must SAY it, not silently omit a marker."""
        repo = self._repo_with_invalid_result(tmp_path)
        p = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "atlas_lesing.py"),
             str(repo), "--emne", "test.invalid", "--ref", "HEAD"],
            capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        assert "INVALID" in p.stdout, p.stdout


class TestFeilErIkkeStille:
    def test_ukjent_ref_reiser(self, ekte_repo: Path) -> None:
        with pytest.raises(atlas_lesing.AtlasLesingFeil):
            atlas_lesing.finn(ekte_repo, "h2o", ref="no/such/ref")

    def test_refen_er_parameter_ikke_hardkodet(self, ekte_repo: Path) -> None:
        """The default ref must be named, not hidden inside the call."""
        assert atlas_lesing.STANDARD_REF == "origin/main"
        svar = atlas_lesing.finn(ekte_repo, "h2o", ref="HEAD")
        assert svar["ref"] == "HEAD"


class TestTrefftypenErSynlig:
    """A substring hit is not the same as a word hit.

    Measured 2026-09-17: `--emne sol` gave 20 hits, of which `h2o.solid`
    came along because "sol" is a substring of "solid". A reference work
    that does not separate them forces the reader to guess which hits are
    real — and then we merely moved the work back to the reader.
    """

    def test_fire_nivaaer_og_rekkefolgen(self, ekte_repo: Path) -> None:
        """`id` > `domene` > `ord` > `delstreng`.

        "sol" hit `batteri.lading` as a WORD — because the word exists in a
        text inside the node. That is not the same as the node being about
        the sun. The levels must therefore be separated: in the id, as a
        standalone word, as a substring.
        """
        svar = atlas_lesing.finn(ekte_repo, "sol", ref="HEAD")
        assert svar["antall"] > 0
        typer = [t["trefftype"] for t in svar["treff"]]
        assert "id" in typer, "lys.sol has sol in the id"
        for svakere, sterkere in (("domene", "id"), ("ord", "domene"),
                                  ("delstreng", "ord")):
            if svakere in typer and sterkere in typer:
                assert typer.index(sterkere) < typer.index(svakere), (
                    f"{sterkere} must come before {svakere}")
        rekkefolge = {"id": 0, "domene": 1, "ord": 2, "delstreng": 3}
        assert typer == sorted(typer, key=lambda x: rekkefolge[x]), (
            f"wrong order: {typer}")

    def test_delstreng_treffet_navngir_seg_selv(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "sol", ref="HEAD")
        solid = [t for t in svar["treff"] if t["id"] == "h2o.solid"]
        assert solid, "precondition: h2o.solid exists"
        assert solid[0]["trefftype"] == "delstreng"

    def test_id_treffet_er_id_treff(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "regnbue", ref="HEAD")
        assert svar["treff"], "precondition: regnbue exists"
        egne = [t for t in svar["treff"] if t["id"].startswith("regnbue")]
        assert egne, "precondition: the node regnbue exists"
        assert all(t["trefftype"] == "id" for t in egne), (
            "when the topic stands in the node id, it is an id hit — the "
            "strongest")
        # ...and they must come before anything that merely mentions the word in text.
        typer = [t["trefftype"] for t in svar["treff"]]
        if "ord" in typer:
            assert typer.index("id") < typer.index("ord"), (
                f"id hits must come before word hits: {typer}")


class TestSeparatorer:
    """Underscore is a separator in ids, not a word character.

    Measured in review 2026-09-17: `sovn` in `homo.sovn_vaaken` was
    classified as `delstreng`, because `\\b` counts `_` as a word
    character. But in node ids `_` separates parts — `homo.sovn_vaaken`,
    `efc.solar_flare_engine`. So `sovn` IS a separate part of the id, and
    must be marked `id`, not weakened to a substring.
    """

    def test_underscore_skiller_ledd_i_id(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "sovn", ref="HEAD")
        treff = [t for t in svar["treff"] if t["id"] == "homo.sovn_vaaken"]
        assert treff, "precondition: homo.sovn_vaaken exists"
        assert treff[0]["trefftype"] == "id", (
            f"`sovn` is a separate part of `homo.sovn_vaaken` — underscore "
            f"separates parts, it does not glue them together. Got: {treff[0]['trefftype']}")

    def test_bindestrek_skiller_ledd_i_id(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "dayahead", ref="HEAD")
        for t in svar["treff"]:
            if "-" in str(t["id"]):
                assert t["trefftype"] == "id", (
                    "a hyphen also separates parts in an id")

    def test_delstreng_i_midten_av_et_ledd_er_fortsatt_delstreng(self, ekte_repo: Path) -> None:
        """`sol` in `solid` must STILL be a substring — the distinction must not loosen."""
        svar = atlas_lesing.finn(ekte_repo, "sol", ref="HEAD")
        solid = [t for t in svar["treff"] if t["id"] == "h2o.solid"]
        assert solid and solid[0]["trefftype"] == "delstreng", (
            "`sol` is in the middle of the part `solid` — that is a "
            "substring, and must not become an id hit when we widen the "
            "separator set")


class TestKommandolinjen:
    """The CLI is a CLAIM in the PR description — and it must be runnable.

    Review 2026-09-17: `finn()` was covered, but not the subprocess run.
    A CLI that is not tested is a claim that it works.
    """

    def _kjoer(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(REPO / "scripts" / "atlas_lesing.py"), str(REPO), *args],
            capture_output=True, text=True, timeout=120)

    def test_oppslag_paa_kommandolinjen(self) -> None:
        p = self._kjoer("--emne", "sovn", "--ref", "HEAD")
        assert p.returncode == 0, p.stderr
        assert "homo.sovn_vaaken" in p.stdout
        assert "1 hit(s) on" in p.stdout

    def test_hull_paa_kommandolinjen_er_tydelig(self) -> None:
        p = self._kjoer("--emne", "kvantegravitasjon_xyzzy", "--ref", "HEAD")
        assert p.returncode == 0, (
            "a hole is a valid answer — the command line must not fail on it")
        assert "THE ATLAS DOES NOT KNOW" in p.stdout

    def test_uten_emne_listes_hele_atlaset(self) -> None:
        """The count is read from the source — not written in.

        The first version had `assert "82 noder" in p.stdout`. It was true
        when written, and false the same evening: the atlas went to 83 and
        then 84, and the test failed on the NUMBER while it believed it was
        measuring that the CLI lists the whole atlas. A hardcoded number
        outlives its source and eventually lies — that is the same class
        the rest of the house guards against.

        What actually needs measuring is that the CLI and the file AGREE —
        and the file must be read from the SAME place as the CLI. The first
        fix read the working tree while the CLI read `--ref HEAD`; they
        drifted apart the moment a node was added but not committed. The
        working tree and the git tree do not answer the same question —
        the same class once more.
        """
        import json as _json
        import subprocess as _sp
        raa = _sp.run(["git", "show", "HEAD:schema/regime_nodes.jsonld"],
                      cwd=REPO, capture_output=True, text=True, check=True)
        noder = _json.loads(raa.stdout)["nodes"]
        p = self._kjoer("--ref", "HEAD")
        assert p.returncode == 0, p.stderr
        assert f"{len(noder)} nodes" in p.stdout, (
            f"the CLI and the file disagree on the count: {p.stdout[:200]}")


class TestKjenteHull:
    """"The atlas does not know" and "this is a KNOWN hole" are not the same answer.

    Measured 2026-09-17: `finn()` read only `regime_nodes.jsonld`, while
    the coverage status sits in `schema/atlas_dekning.json` (27
    ikke_dekket, 6 delvis, 6 dekket). A reference work that answers "does
    not know" about something someone actually measured and found missing
    throws away the most expensive thing it knows.
    """

    def test_kjent_hull_navngis_som_kjent(self, ekte_repo: Path) -> None:
        """The coverage file's shape is measured, not assumed: `domener` is
        a DICT from domain name to {status, noder, begrunnelse, emner}."""
        import json as _json
        dek = _json.loads(_git(ekte_repo, "show", "HEAD:schema/atlas_dekning.json"))
        domener = dek["domener"]
        assert isinstance(domener, dict), "precondition: domener is a dict"
        ikke_dekket = [k for k, v in domener.items()
                       if isinstance(v, dict) and v.get("status") == "ikke_dekket"]
        # 2026-09-18: all 39 domains now have a node. An empty list means
        # the goal is reached — but then there is no known-hole lookup to
        # test either. We skip honestly instead of failing because the
        # world got better.
        if not ikke_dekket:
            import pytest as _pytest
            _pytest.skip("no known holes — all 39 domains are covered")
        svar = atlas_lesing.finn(ekte_repo, ikke_dekket[0], ref="HEAD")
        assert svar["kjent_hull"] is not None, (
            f"`{ikke_dekket[0]}` is measured as ikke_dekket — the lookup "
            f"must say so, not just 'does not know'")
        assert svar["kjent_hull"]["status"] == "ikke_dekket"

    def test_ukjent_emne_uten_dekning_er_fortsatt_bare_ukjent(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "kvantegravitasjon_xyzzy", ref="HEAD")
        assert svar["hull"] is True
        assert svar["kjent_hull"] is None, (
            "something nobody has measured must not be reported as a known "
            "hole — that would make 'known' meaningless")

    def test_svaret_sier_hvor_dekningen_kom_fra(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "h2o", ref="HEAD")
        assert "dekning_fil" in svar, (
            "the reader must be able to see which file the coverage status came from")


class TestRelevans:
    """A reference work that answers with everything answers nothing.

    Measured 2026-09-17 by USING the lookup on real questions:
      "EF"         → 80 hits, ALL substrings of "efc"/"buffer"/"celle"
      "instrument" → 82 hits — all 82 nodes, because the word is in all
      "atlas"      → 46 hits, ONE is relevant (efc.selv.atlas)

    The weakest hit type must therefore not dominate the answer.
    `buss_domene` is also a signal: a node that covers the domain
    `verden.energi` IS relevant for "energi", even if the word only stands
    in the prose.
    """

    def test_buss_domene_treff_rangeres_over_prosa(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "energi", ref="HEAD")
        domene = [t for t in svar["treff"] if t.get("buss_domene") == "verden.energi"]
        assert domene, "precondition: verden.energi exists"
        assert domene[0]["trefftype"] in ("id", "domene"), (
            f"a node that COVERS the domain must not be ranked as loose "
            f"prose: {domene[0]}")

    def test_for_bredt_sok_navngis(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "instrument", ref="HEAD")
        assert svar["antall"] > 50, "precondition: instrument hits broadly"
        assert svar["for_bredt"] is True, (
            "a search that hits almost the whole atlas must SAY so, not "
            "pretend to be a precise answer")
        assert svar["raad"] is not None, "when the search is too broad, say what can be done"

    def test_presist_sok_er_ikke_for_bredt(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "regnbue", ref="HEAD")
        assert svar["for_bredt"] is False, (
            "a precise search must not be flagged as broad — then the "
            "warning becomes noise and is ignored")

    def test_cli_viser_relevante_forst(self, ekte_repo: Path) -> None:
        import subprocess as _sp
        p = _sp.run([sys.executable, str(REPO / "scripts" / "atlas_lesing.py"),
                     str(REPO), "--ref", "HEAD", "--emne", "energi"],
                    capture_output=True, text=True, timeout=120)
        assert p.returncode == 0, p.stderr
        linjer = [l for l in p.stdout.splitlines() if "efc." in l or "batteri" in l]
        assert linjer, p.stdout[:300]
        assert "efc." in linjer[0], (
            f"public engine nodes must not rank below internal battery "
            f"nodes when both are word hits: {linjer[:3]}")


class TestBareNavnetTeller:
    """Matching happens on the domain NAME — never on the rationale text.

    The claim stood in the commit message for 0a41054b, but was NOT covered
    by a test. Review round 3 showed it: the mutant that also matches the
    rationale passed the whole suite (40/40). A claim about a guard that
    the guard itself cannot kill is the same error as the rest of this
    period.

    The probe is the reviewer's own: `mast-caom-observasjonen` stands in
    the RATIONALE of `kosmos.galakser`, but is not a domain name. Had the
    matching read prose, it would have slipped through as a "known hole".
    """

    def test_begrunnelsestekst_er_ikke_et_treff(self, ekte_repo: Path) -> None:
        import json as _json
        dek = _json.loads(_git(ekte_repo, "show", "HEAD:schema/atlas_dekning.json"))
        domener = dek["domener"]
        # Find a word that stands in a rationale but is not a domain name.
        kandidat = None
        for dom, v in domener.items():
            tekst = (v or {}).get("begrunnelse") or ""
            for ord_ in tekst.replace(",", " ").replace(".", " ").split():
                if len(ord_) > 8 and ord_ not in domener and not any(
                        ord_ in d for d in domener):
                    kandidat = ord_
                    break
            if kandidat:
                break
        assert kandidat, "precondition: a rationale contains a word that is not a domain name"

        svar = atlas_lesing.finn(ekte_repo, kandidat, ref="HEAD")
        assert svar["kjent_hull"] is None, (
            f"`{kandidat}` stands in a RATIONALE, not in a domain name — "
            f"the lookup read prose and reported a 'known hole'. Matching "
            f"must only happen on the name: {svar['kjent_hull']}")

    def test_ordet_finnes_faktisk_i_en_begrunnelse(self, ekte_repo: Path) -> None:
        """Negative control: without this the test above could pass because
        the word existed nowhere — and then it tested nothing."""
        import json as _json
        dek = _json.loads(_git(ekte_repo, "show", "HEAD:schema/atlas_dekning.json"))
        all_tekst = " ".join((v or {}).get("begrunnelse", "")
                             for v in dek["domener"].values())
        assert "mast-caom" in all_tekst, (
            "the reviewer's probe must exist in a rationale — otherwise "
            "the test above is empty")
        svar = atlas_lesing.finn(ekte_repo, "mast-caom", ref="HEAD")
        assert svar["kjent_hull"] is None, (
            "`mast-caom` is not a domain name. That it stands in a "
            "rationale must not make it a known hole.")


class TestBreddeKriteriet:
    """"Too broad" must rest on a PRECISE hit, not on a number.

    Review round 4 measured the threshold I had chosen (50 hits or 60 %):
    sol=20, energi=25, kosmos=32, h2o=36 — all far below. instrument=82,
    above. No real question was close. The number was guessed.

    The meaningful criterion is whether the search has ANYTHING precise:
    an `id` hit or a `domene` hit. `sol` has `lys.sol` — that is not
    broad, no matter how many others mention the word in prose.
    `instrument` has zero precise hits; everything is loose prose.
    """

    def test_sok_uten_presist_treff_er_bredt(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "instrument", ref="HEAD")
        presise = [t for t in svar["treff"] if t["trefftype"] in ("id", "domene")]
        assert not presise, "precondition: instrument has no precise hits"
        assert svar["for_bredt"] is True, (
            "a search with ZERO precise hits is broad — regardless of count")

    def test_sok_med_presist_treff_er_ikke_bredt(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "sol", ref="HEAD")
        presise = [t for t in svar["treff"] if t["trefftype"] in ("id", "domene")]
        assert presise, "precondition: sol has the id hit lys.sol"
        assert svar["for_bredt"] is False, (
            f"a search with a precise hit is not broad, even if "
            f"{svar['antall']} nodes mention the word in prose")

    def test_de_maalte_spoersmaalene_fra_reviewen(self, ekte_repo: Path) -> None:
        """The reviewer's own measurements — they must hold as boundary values."""
        forventet = {"sol": False, "energi": False, "kosmos": False,
                     "h2o": False, "instrument": True}
        for emne, skal_vaere_bredt in forventet.items():
            s = atlas_lesing.finn(ekte_repo, emne, ref="HEAD")
            assert s["for_bredt"] is skal_vaere_bredt, (
                f"'{emne}': expected for_bredt={skal_vaere_bredt}, "
                f"got {s['for_bredt']} ({s['antall']} hits)")

    def test_mange_treff_med_presist_er_ikke_bredt(self, ekte_repo: Path) -> None:
        """THE DECISIVE CASE — where the two criteria disagree.

        `efc` gives 68 hits, of which 32 are precise (`efc.*` nodes). A
        COUNT threshold says "broad" because 68 > 50. That is wrong: 32
        precise hits are the exact opposite of broad.

        Without this test both criteria pass on the same data — and then
        the tests do not measure the distinction they claim to defend.
        """
        svar = atlas_lesing.finn(ekte_repo, "efc", ref="HEAD")
        presise = [t for t in svar["treff"] if t["trefftype"] in ("id", "domene")]
        assert len(presise) > 10, f"precondition: efc has many precise ({len(presise)})"
        assert svar["antall"] > 50, f"precondition: efc has many hits ({svar['antall']})"
        assert svar["for_bredt"] is False, (
            f"'efc' has {len(presise)} PRECISE hits out of {svar['antall']} — "
            f"that is not a broad search. A count threshold would say broad.")

    def test_kriteriet_skalerer_med_atlaset(self, ekte_repo: Path) -> None:
        """The criterion must not depend on how BIG the atlas is.

        A percentage threshold would move as the atlas grew; "is there a
        precise hit" does not.
        """
        s = atlas_lesing.finn(ekte_repo, "h2o", ref="HEAD")
        presise = [t for t in s["treff"] if t["trefftype"] in ("id", "domene")]
        assert presise, "h2o has an id hit"
        assert s["for_bredt"] is False


class TestVisningsgrensen:
    """`_VIS_MAKS` must actually limit — the mutant 999 was not killed."""

    def test_grensen_er_satt_og_lav_nok(self) -> None:
        assert 0 < atlas_lesing._VIS_MAKS <= 30, (
            f"_VIS_MAKS={atlas_lesing._VIS_MAKS} — a limit that limits "
            f"nothing is not a limit")

    def test_cli_kutter_og_sier_hvor_mange_som_ligger_under(self, ekte_repo: Path) -> None:
        import subprocess as _sp
        p = _sp.run([sys.executable, str(REPO / "scripts" / "atlas_lesing.py"),
                     str(REPO), "--ref", "HEAD", "--emne", "instrument"],
                    capture_output=True, text=True, timeout=120)
        assert p.returncode == 0, p.stderr
        linjer = [l for l in p.stdout.splitlines() if "(ord)" in l or "(delstreng)" in l]
        assert len(linjer) <= atlas_lesing._VIS_MAKS, (
            f"CLI viste {len(linjer)} treff, grensen er {atlas_lesing._VIS_MAKS}")
        assert "more — use --alle" in p.stdout, (
            "when the hits are cut, the CLI must say how many lie below")


class TestStorrelsenPaaHullet:
    """"A known hole" without size cannot be prioritised.

    Measured 2026-09-17: `verden.vaer` (190 770 messages) and
    `kosmos.asteroider` (228) gave an IDENTICAL answer. PR #475 makes the
    coverage file carry `meldinger` per domain — but it is not merged, so
    the read must be OPTIONAL: if the field exists, it is shown; if it does
    not, the lookup works as before.

    The alternative — requiring the field — would have locked this PR to
    #475, and a reference work that does not work until another PR lands is
    a reference work that does not work.
    """

    def _repo_med(self, tmp_path: Path, ekstra: dict) -> Path:
        repo = tmp_path / "r"
        (repo / "efc_inference" / "engine").mkdir(parents=True)
        (repo / "schema").mkdir()
        (repo / "schema" / "regime_nodes.jsonld").write_text(
            '{"nodes": []}', encoding="utf-8")
        dekning = {"domener": {"kosmos.asteroider": dict(
            {"status": "ikke_dekket", "noder": [], "begrunnelse": "ingen node"}.items(),
            **ekstra)}}
        (repo / "schema" / "atlas_dekning.json").write_text(
            json.dumps(dekning), encoding="utf-8")
        for a in (("init", "-q"), ("config", "user.email", "t@t"),
                  ("config", "user.name", "t"), ("add", "-A"),
                  ("commit", "-q", "-m", "x")):
            subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
        return repo

    def test_meldinger_er_med_nar_feltet_finnes(self, tmp_path: Path) -> None:
        repo = self._repo_med(tmp_path, {"meldinger": 228})
        svar = atlas_lesing.finn(repo, "kosmos.asteroider", ref="HEAD")
        assert svar["kjent_hull"] is not None
        assert svar["kjent_hull"]["meldinger"] == 228, (
            f"the size is missing: {svar['kjent_hull']}")

    def test_uten_feltet_virker_oppslaget_som_foer(self, tmp_path: Path) -> None:
        repo = self._repo_med(tmp_path, {})
        svar = atlas_lesing.finn(repo, "kosmos.asteroider", ref="HEAD")
        assert svar["kjent_hull"] is not None, (
            "the lookup must work without `meldinger` too — the field is optional")
        assert svar["kjent_hull"]["meldinger"] is None

    def test_navnet_matches_fortsatt_bare_paa_domenenavn(self, tmp_path: Path) -> None:
        """The size must not make more things match."""
        repo = self._repo_med(tmp_path, {"meldinger": 228})
        svar = atlas_lesing.finn(repo, "228", ref="HEAD")
        assert svar["kjent_hull"] is None, (
            "the number 228 is not a domain name")
