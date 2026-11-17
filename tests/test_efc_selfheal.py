"""Hermetic tests for efc_selfheal — the auto-fix whitelist boundary.

The panel (gpt-5.6-luna, 0.93) found that almost nothing is safe to auto-fix.
These tests lock that boundary in: ONLY own-clone lag is auto-fixable; noise,
unowned cards and DOI mismatch must always escalate (never auto-fixed).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.maintenance.efc_selfheal import AUTO_FIX


def test_only_clone_lag_is_auto_fixable():
    # The whitelist holds exactly ONE entry, by design.
    assert set(AUTO_FIX.keys()) == {"efc-clone-head"}


def test_noise_is_never_auto_fixed():
    assert "working-memory-noise" not in AUTO_FIX


def test_unowned_cards_are_never_auto_fixed():
    assert "kanban-unowned" not in AUTO_FIX


def test_doi_mismatch_is_never_auto_fixed():
    assert "doi-set" not in AUTO_FIX
