"""Tests for the status words in the activity log (t_882cfca, phase 1).

The contract: "maskinelt kontrollert", "eksternt verifisert" and "faglig
godkjent" are three VALID values in `statusord`, and none of them implies
the other two. So we test both that each word alone is enough, and that
the guard does not add or require words that are not in the record. The
one requirement enforced is that "faglig godkjent" belongs to the human.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
SCRIPT = ROT / "scripts" / "maintenance" / "validate_activity_log.py"
sys.path.insert(0, str(ROT / "scripts" / "maintenance"))

import validate_activity_log as val  # noqa: E402


def _post(rolle: str = "faber", statusord: object = None) -> dict:
    e = {"event_id": "EVT-TEST-0001", "occurred_at": "2026-09-17T07:30:00+00:00",
         "action": "validation_finished", "role": rolle, "kanban_card": "t_f882cfca",
         "files": ["scripts/maintenance/blast_radius.py"],
         "why": "test", "result": "success", "reversible": True}
    if statusord is not None:
        e["statusord"] = statusord
    return e


def test_ordene_er_gyldige_hver_for_seg():
    assert val.sjekk_statusord(_post(statusord=["maskinelt kontrollert"]), 1) == []
    assert val.sjekk_statusord(_post(statusord=["eksternt verifisert"]), 1) == []
    assert val.sjekk_statusord(_post("menneske", ["faglig godkjent"]), 1) == []
    assert val.sjekk_statusord(_post("menneske", list(val.STATUSORD)), 1) == []


def test_ordene_impliserer_ikke_hverandre():
    """One value is enough — the guard never adds and never requires the others."""
    e = _post(statusord=["maskinelt kontrollert"])
    forste = dict(e)
    feil = val.sjekk_statusord(e, 1)
    assert feil == []
    assert e == forste, "the guard must not write into the record"
    assert "eksternt verifisert" not in e["statusord"]
    assert "faglig godkjent" not in e["statusord"]
    # and the field is optional: a record without statusord is not an error
    assert val.sjekk_statusord(_post(), 1) == []


def test_ukjent_og_duplikat_avvises():
    assert {f["type"] for f in val.sjekk_statusord(_post(statusord=["maskinelt godkjent"]), 3)} \
        == {"unknown_statusord"}
    assert {f["type"] for f in val.sjekk_statusord(
        _post(statusord=["eksternt verifisert", "eksternt verifisert"]), 4)} \
        == {"duplicate_statusord"}
    assert {f["type"] for f in val.sjekk_statusord(_post(statusord=[]), 5)} == {"bad_statusord"}
    assert {f["type"] for f in val.sjekk_statusord(_post(statusord="maskinelt kontrollert"), 6)} \
        == {"bad_statusord"}


def test_faglig_godkjent_er_menneskets():
    for rolle in ("faber", "researcher", "orchestrator", "verifier"):
        feil = val.sjekk_statusord(_post(rolle, ["faglig godkjent"]), 7)
        assert {f["type"] for f in feil} == {"faglig_godkjent_uten_menneske"}, rolle
    assert val.sjekk_statusord(_post("menneske", ["faglig godkjent"]), 8) == []


def test_loggen_i_treet_er_gyldig_og_feltet_er_valgfritt():
    """Readback: the existing lines have no statusord, and must still
    validate — a required field would be an unsigned inheritance."""
    import subprocess
    r = subprocess.run([sys.executable, str(SCRIPT), "--json"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout
    assert json.loads(r.stdout)["feil"] == []


def test_cli_avviser_faglig_godkjent_fra_en_profil(tmp_path, monkeypatch, capsys):
    logg = tmp_path / "activity.jsonl"
    logg.write_text(json.dumps(_post("faber", ["faglig godkjent"]), ensure_ascii=False) + "\n",
                    encoding="utf-8")
    monkeypatch.setattr(val, "LOGG", logg)
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--json"])
    rc = val.hoved()
    ut = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert {f["type"] for f in ut["feil"]} == {"faglig_godkjent_uten_menneske"}
