"""Regression tests for the atlas's own concept space."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
SCRIPTS = ROT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import atlas_lesing  # noqa: E402


KJERNEBEGREPER = (
    "Energy-Flow Cosmology",
    "Entropy Gradient",
    "GHF",
    "HME",
    "IMX",
)


def test_kjernebegrep_svarer_med_navngitt_grunn() -> None:
    """A registered concept must be told apart from a real hole."""
    for begrep in KJERNEBEGREPER:
        svar = atlas_lesing.finn(ROT, begrep, ref="HEAD")
        assert not svar["hull"], begrep
        assert svar["treff"][0]["trefftype"] == "navnerom"
        assert svar["treff"][0]["id"].startswith("efc:")
        assert svar["treff"][0]["grunn"]


def test_navneromstreff_er_ikke_dekning() -> None:
    """A concept without a node must not be readable as «the atlas has this».

    Review 2026-09-18: the namespace hit gave a non-empty hit list, and a
    downstream reader could conclude «covered». The field `har_node` says no —
    and that is the difference between having the concept and having the node.
    """
    svar = atlas_lesing.finn(ROT, "Entropy Gradient", ref="HEAD")
    treff = svar["treff"][0]
    assert treff["har_node"] is False
    assert treff["dekning"] == "navnerom_uten_node"

    # The name must not exist as a node in the bank — otherwise the test is dead.
    bank = json.loads((ROT / "schema" / "regime_nodes.jsonld").read_text(
        encoding="utf-8"))
    ider = {n["id"] for n in bank["nodes"]}
    assert not any("EntropyGradient" in i for i in ider)

    # A REAL hole must not get the namespace hit with it.
    ukjent = atlas_lesing.finn(ROT, "finnes-ikke-som-begrep-eller-node",
                               ref="HEAD")
    assert ukjent["hull"] is True
    assert ukjent["treff"] == []


def test_fem_kjernebegreper_er_deklarert_i_registeret() -> None:
    """The test must not be able to pass because the registry went empty."""
    data = json.loads((ROT / "docs" / "concepts.jsonld").read_text(
        encoding="utf-8"))
    ider = {p.get("@id") for p in data.get("@graph", [])}
    for forventet in ("efc:EFC", "efc:EntropyGradient", "efc:GHF", "efc:HME",
                      "efc:IMX"):
        assert forventet in ider, forventet


def test_defekt_begrepsregister_feiler_hoeyt(monkeypatch, tmp_path) -> None:
    """Invalid JSON in the registry is a read error, not «not found».

    The first version swallowed both JSONDecodeError and a missing file. Then a
    defect in the registry became the answer «the atlas does not know» — an
    answer that looks like knowledge about the content. The test swaps out the
    git reader: a temporary directory is not a git tree, so `_git` would fail
    BEFORE the JSON was read — and then the test measured git, not the read
    error handling.
    """
    def falsk_git(repo, *args):
        if args[:2] == ("show", "HEAD:docs/concepts.jsonld"):
            return "{ not json"
        raise atlas_lesing.AtlasLesingFeil("not found in this test tree")

    monkeypatch.setattr(atlas_lesing, "_git", falsk_git)
    with pytest.raises(atlas_lesing.AtlasLesingFeil, match="is not valid JSON"):
        atlas_lesing._navnerom(tmp_path, "HEAD", "ghf")


def test_oppslag_er_deterministisk_paa_tvers_av_hashfroer() -> None:
    """Sorting must not depend on the process's hash seed."""
    kode = (
        "import json,sys; sys.path.insert(0,'scripts'); import atlas_lesing; "
        "print(json.dumps(atlas_lesing.finn('.', 'Entropy Gradient', ref='HEAD'), "
        "sort_keys=True, ensure_ascii=False))"
    )
    svar = []
    for fro in ("0", "1", "12345"):
        env = {**os.environ, "PYTHONHASHSEED": fro}
        svar.append(subprocess.check_output(
            [sys.executable, "-c", kode], cwd=ROT, env=env, text=True))
    assert svar[0] == svar[1] == svar[2]
