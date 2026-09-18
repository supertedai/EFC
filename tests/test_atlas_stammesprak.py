"""Regresjonstester for atlasets eget begrepsrom."""

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
    """Et registrert begrep skal skilles fra et ekte hull."""
    for begrep in KJERNEBEGREPER:
        svar = atlas_lesing.finn(ROT, begrep, ref="origin/main")
        assert not svar["hull"], begrep
        assert svar["treff"][0]["trefftype"] == "navnerom"
        assert svar["treff"][0]["id"].startswith("efc:")
        assert svar["treff"][0]["grunn"]


def test_doedt_alias_feiler_hoeyt() -> None:
    """Et alias skal aldri skjule at maalnoden mangler."""
    with pytest.raises(atlas_lesing.AtlasLesingFeil, match="alias.*mangler"):
        atlas_lesing._valider_aliaser({"energiflyt": "efc.finnes_ikke"}, {"efc.lag_s"})


def test_oppslag_er_deterministisk_paa_tvers_av_hashfroer() -> None:
    """Sortering skal ikke avhenge av prosessens hashfroe."""
    kode = (
        "import json,sys; sys.path.insert(0,'scripts'); import atlas_lesing; "
        "print(json.dumps(atlas_lesing.finn('.', 'Entropy Gradient', ref='origin/main'), "
        "sort_keys=True, ensure_ascii=False))"
    )
    svar = []
    for fro in ("0", "1", "12345"):
        env = {**os.environ, "PYTHONHASHSEED": fro}
        svar.append(subprocess.check_output(
            [sys.executable, "-c", kode], cwd=ROT, env=env, text=True))
    assert svar[0] == svar[1] == svar[2]
