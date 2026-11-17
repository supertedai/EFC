"""Hermetic tests for efc_node_triangulate.classify (the 4-state core).

These prove the CLASSIFICATION mechanics, not the probes. Per the measured
lesson: green tests prove the mechanism, not the usage — probe usage is
verified separately by running the real picture.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.maintenance.efc_node_triangulate import (
    LINIAGE, Observation, Verdict, classify,
    InvariantVerdict, check_consistency, check_threshold,
)


def test_unknown_when_no_observations():
    assert classify([]) == Verdict.UNKNOWN


def test_unknown_when_only_inexact_observations():
    obs = [Observation(family="git-clone", key="k", value="abc", exact=False)]
    assert classify(obs) == Verdict.UNKNOWN


def test_confirmed_when_two_independent_families_agree():
    # git-clone (git lineage) and forge (git-forge lineage) are independent
    obs = [
        Observation(family="git-clone", key="head", value="sha1"),
        Observation(family="forge", key="head", value="sha1"),
    ]
    assert classify(obs) == Verdict.CONFIRMED


def test_pending_when_single_family():
    obs = [Observation(family="git-clone", key="head", value="sha1")]
    assert classify(obs) == Verdict.PENDING


def test_pending_when_same_lineage_only():
    # two clones = same git lineage -> NOT independent confirmation
    obs = [
        Observation(family="git-clone", key="head", value="sha1", ts="/a"),
        Observation(family="git-clone", key="head", value="sha1", ts="/b"),
    ]
    assert classify(obs) == Verdict.PENDING


def test_drift_when_two_values_disagree():
    obs = [
        Observation(family="git-clone", key="head", value="sha1", ts="/a"),
        Observation(family="git-clone", key="head", value="sha2", ts="/b"),
    ]
    assert classify(obs) == Verdict.DRIFT


def test_drift_when_cross_family_disagreement():
    obs = [
        Observation(family="publication", key="doi", value="setA", ts="repo"),
        Observation(family="public-surface", key="doi", value="setB", ts="changelog"),
    ]
    assert classify(obs) == Verdict.DRIFT


def test_set_identity_not_count():
    # same value string = same set; different order normalized upstream.
    # Here we assert: two families asserting the SAME fingerprint -> confirmed,
    # asserting DIFFERENT fingerprints (even if counts equal) -> drift.
    agree = [
        Observation(family="publication", key="doi", value="fp1"),
        Observation(family="public-surface", key="doi", value="fp1"),
    ]
    assert classify(agree) == Verdict.CONFIRMED
    disagree = [
        Observation(family="publication", key="doi", value="fp1"),
        Observation(family="public-surface", key="doi", value="fp2"),
    ]
    assert classify(disagree) == Verdict.DRIFT


def test_unknown_family_is_ignored():
    # a family not in LINIAGE carries no evidence
    obs = [Observation(family="no-such-family", key="k", value="v")]
    assert classify(obs) == Verdict.UNKNOWN


# --- invariant checks (3-state) ---

def test_consistency_ok_when_all_agree():
    obs = [
        Observation(family="git-clone", key="head", value="sha1", ts="/a"),
        Observation(family="git-clone", key="head", value="sha1", ts="/b"),
    ]
    assert check_consistency(obs) == InvariantVerdict.OK


def test_consistency_drift_when_disagree():
    obs = [
        Observation(family="git-clone", key="head", value="sha1"),
        Observation(family="git-clone", key="head", value="sha2"),
    ]
    assert check_consistency(obs) == InvariantVerdict.DRIFT


def test_consistency_unknown_when_empty():
    assert check_consistency([]) == InvariantVerdict.UNKNOWN


def test_threshold_ok_at_expected():
    obs = [Observation(family="working-memory", key="noise", value="0")]
    assert check_threshold(obs, "0") == InvariantVerdict.OK


def test_threshold_drift_above_expected():
    obs = [Observation(family="working-memory", key="noise", value="2")]
    assert check_threshold(obs, "0") == InvariantVerdict.DRIFT


def test_threshold_unknown_when_unmeasured():
    assert check_threshold([], "0") == InvariantVerdict.UNKNOWN
