"""Tests for scripts/maintenance/changelog_projeksjon.py — the projection start must exist.

What must not rot: last_processed_sha is stamped from the commit the projection
ran on, so a squash-merge (or a deleted branch) can leave it on no branch at
all. Measured 2026-09-17: main's recorded 72d91914… was squashed to 1b51a04e;
every run — on main and on every PR — then died with «fatal: Invalid revision
range», so no change whatsoever could turn the gate green. The resolver must
repair such a start deterministically, and must NOT touch a start that already
resolves (a repaired-gate regression would silently re-project history).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAINT = ROOT / "scripts" / "maintenance"
sys.path.insert(0, str(MAINT))

import changelog_projeksjon as cp  # noqa: E402

PHANTOM = "deadbeef" * 5  # 40 hex chars, resolves to nothing


def test_unknown_sha_does_not_resolve():
    assert cp._finnes(PHANTOM) is False
    assert cp._finnes("") is False


def test_head_resolves():
    assert cp._finnes("HEAD") is True


def test_unreachable_start_is_repaired_to_a_real_commit():
    repaired = cp._los_opp_startpunkt(PHANTOM)
    assert repaired != PHANTOM, "a phantom start must not be echoed back"
    assert cp._finnes(repaired), "the repaired start must resolve in this repo"
    # Deterministic: the main line is the documented first fallback.
    if cp._finnes("origin/main"):
        assert repaired == cp._git("rev-parse", "origin/main")


def test_resolvable_start_is_untouched():
    head = cp._git("rev-parse", "HEAD")
    assert cp._los_opp_startpunkt(head) == head


def test_repair_is_idempotent():
    once = cp._los_opp_startpunkt(PHANTOM)
    assert cp._los_opp_startpunkt(once) == once, (
        "the repaired start must itself be stable, or every run rewrites "
        "the projection start")
