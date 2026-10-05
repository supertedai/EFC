"""The bench must not read a triage that could not run as a detection.

Measured 2026-10-05 (card t_e253357c, reproduced on the UNTOUCHED main clone
52ba3222): scripts/maintenance/verifier_bench.py answered 4/4 under
/usr/bin/python3 (jsonschema 4.19.2 installed) and 3/4 under a test venv
WITHOUT it -- the same Python version, 3.14.4. The triage imports jsonschema
inside the function; without the package it wrote to stderr and returned 2
with nothing on stdout, and the bench read the empty stdout as {}, so a
non-zero exit became "detected" for three fixtures while the injection fixture
became a gap.

A measurement that could not be made is not an outcome in either direction:
not a detection, and not a gap. These tests pin both halves.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
MAINT = ROT / "scripts" / "maintenance"


def _modul(navn: str, fil: Path):
    spec = importlib.util.spec_from_file_location(navn, fil)
    assert spec and spec.loader, f"could not load {fil}"
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def benk():
    return _modul("verifier_bench_under_test", MAINT / "verifier_bench.py")


@pytest.fixture(scope="module")
def runde():
    return _modul("vedlikeholdsrunde_under_test", MAINT / "vedlikeholdsrunde.py")


def _skjul_jsonschema(tmp_path: Path) -> str:
    """A PYTHONPATH that makes `import jsonschema` fail, on purpose.

    A real interpreter with one module shadowed by a module that raises
    ImportError: the failure mode of a machine where `uv sync` has not been
    run, reproduced without depending on such a machine existing.
    """
    skygge = tmp_path / "jsonschema-skjult"
    skygge.mkdir()
    (skygge / "jsonschema.py").write_text(
        "raise ImportError('simulated: jsonschema is not installed here')\n",
        encoding="utf-8")
    return str(skygge)


def test_exit_uten_svar_er_ikke_deteksjon(benk):
    """/bin/false: rc 1 with nothing on stdout. The old rule read rc != 0 as
    detection; it is not -- nothing was measured."""
    navn, _, tekst, korrekt_hash, krav = benk.KJENTE_FEIL[0]
    utfall = benk.kjoer_fixture(navn, tekst, korrekt_hash, krav,
                                python="/bin/false")
    assert utfall["_rc"] == 1
    assert utfall["_maalt"] is False
    assert utfall["_detektert"] is None


def test_exit_null_uten_svar_er_ikke_deteksjon(benk):
    """The other direction of the same non-answer: rc 0, no output at all."""
    navn, _, tekst, korrekt_hash, krav = benk.KJENTE_FEIL[0]
    utfall = benk.kjoer_fixture(navn, tekst, korrekt_hash, krav,
                                python="/bin/true")
    assert utfall["_maalt"] is False
    assert utfall["_detektert"] is None


def test_triage_uten_jsonschema_svarer_not_measured(tmp_path, monkeypatch, benk):
    """The triage must answer, not go silent: a readable non-answer on stdout
    is what lets a caller tell "could not measure" from a verdict."""
    pytest.importorskip("yaml")
    skygge = _skjul_jsonschema(tmp_path)
    monkeypatch.setenv("PYTHONPATH",
                       skygge + os.pathsep + os.environ.get("PYTHONPATH", ""))
    navn, _, tekst, korrekt_hash, krav = benk.KJENTE_FEIL[1]
    utfall = benk.kjoer_fixture(navn, tekst, korrekt_hash, krav)
    assert utfall["_rc"] == 2
    assert utfall["status"] == "not-measured"
    assert utfall["_maalt"] is False
    assert utfall["_detektert"] is None
    assert "jsonschema" in (utfall["grunn"] or "")


def test_benken_sier_not_measured_uten_jsonschema(tmp_path):
    """End to end: the whole bench, in a child process, with jsonschema
    hidden. It must exit 2 -- never 0 (a clean verdict) and never 1 (a
    detection gap), because neither was measured -- and never crash."""
    miljo = dict(os.environ)
    miljo["PYTHONPATH"] = _skjul_jsonschema(tmp_path)
    kjoer = [sys.executable, str(MAINT / "verifier_bench.py")]
    r = subprocess.run(kjoer + ["--json"], capture_output=True, text=True,
                       env=miljo, timeout=300)
    assert r.returncode == 2, f"expected not-measured, got rc={r.returncode}:\n{r.stdout}\n{r.stderr}"
    assert "Traceback" not in r.stderr
    svar = json.loads(r.stdout)
    assert svar["maalt"] is False
    assert svar["detekterte"] is None  # no verdict at all, not a low number
    assert svar["ikke_malt"] == 4
    assert svar["resultater"] == []
    assert "jsonschema" in (svar["grunn"] or "")
    # The human output must name the missing measurement, not print a count
    # that reads like a verdict about detection.
    h = subprocess.run(kjoer, capture_output=True, text=True, env=miljo,
                       timeout=300)
    assert h.returncode == 2
    assert "NOT MEASURED" in h.stdout
    assert "4/4" not in h.stdout
    assert "3/4" not in h.stdout


def test_med_forutsetningene_paa_plass_er_4_av_4_en_maling(benk):
    """The positive control: on an interpreter that can run the triage the
    bench is still a real measurement, and says so."""
    mangler = benk.forutsetninger_mangler()
    if mangler:
        pytest.skip(f"this interpreter cannot run the triage: {mangler}")
    r = subprocess.run([sys.executable, str(MAINT / "verifier_bench.py"),
                        "--json"], capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout + r.stderr
    svar = json.loads(r.stdout)
    assert svar["maalt"] is True
    assert svar["detekterte"] == 4
    assert svar["ikke_malt"] == 0


def test_runden_skiller_manglende_maling_fra_benkens_gap(runde):
    """The round must not file the bench's "not measured" as a detection gap,
    and must not drop a real gap: exit 1 is the bench's finding channel."""
    umaalt = runde._bench_funn(2, {"maalt": False, "grunn": "no jsonschema",
                                   "interpreter": "/usr/bin/python3"})
    assert umaalt and umaalt[0]["type"] == "bench_not_measured"
    assert umaalt[0]["grunn"] == "no jsonschema"
    assert umaalt[0]["interpreter"] == "/usr/bin/python3"
    assert runde._bench_funn(1, {"maalt": True})[0]["type"] == "bench_gap"
    assert runde._bench_funn(0, {"maalt": True}) == []
