import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parent
KEY_SHA256 = "d3fd75b640b0adf92bd66154cbe194870bd0303ec4fd226b1b6db3ddf28212c3"


def load_reader():
    spec = importlib.util.spec_from_file_location("leser_b", ROOT / "leser_b.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_fixture():
    key = json.loads((ROOT / "key.json").read_text())
    evidence = json.loads((ROOT / "evidenslag.json").read_text())
    bank = json.loads(__import__("subprocess").check_output(
        ["git", "show", "origin/main:schema/regime_nodes.jsonld"], cwd=ROOT.parent.parent.parent
    ))
    return bank, key, evidence


def answer(answers, question_id):
    return next(row for row in answers if row["id"] == question_id)


def test_analogous_edges_never_become_support():
    evidence = json.loads((ROOT / "evidenslag.json").read_text())
    analogous_pairs = {
        ("homo.aksjonspotensial", "homo.hjerte_syklus"),
        ("homo.hjerte_syklus", "homo.aksjonspotensial"),
    }
    assert not any(
        edge["predicate"] == "STOETTER"
        and (edge["subject"], edge["object"]) in analogous_pairs
        for edge in evidence["kanter"]
    )
    assert all(edge["predicate"] in {"STOETTER", "MOTSIGER"} for edge in evidence["kanter"])


def test_unreported_uncertainty_is_null_not_zero():
    evidence = json.loads((ROOT / "evidenslag.json").read_text())
    beta = next(item for item in evidence["usikkerhet"]["obs.bao"] if item["navn"] == "beta")
    assert beta["verdi"] == 0.16
    assert beta["usikkerhet"] is None
    assert beta["usikkerhet"] != 0


def test_q3_is_zero_without_explicit_support():
    bank, key, evidence = load_fixture()
    row = answer(load_reader().svar(bank, key, evidence), "Q3")
    assert row["svar"]["antall"] == 0
    assert "STOETTER" in row["grunnlag"]


def test_q7_is_zero_and_explains_bank_has_no_uncertainty_field():
    bank, key, evidence = load_fixture()
    row = answer(load_reader().svar(bank, key, evidence), "Q7")
    assert row["svar"]["antall"] == 0
    assert "usikkerhet" in row["grunnlag"]


def test_q4_finds_reversed_observed_in_edge():
    bank, key, evidence = load_fixture()
    row = answer(load_reader().svar(bank, key, evidence), "Q4")
    assert row["svar"] == key["sporsmal"][3]["nokkel"]
    assert "feilrettet" in row["grunnlag"]


def test_key_is_unchanged():
    assert hashlib.sha256((ROOT / "key.json").read_bytes()).hexdigest() == KEY_SHA256


def test_q5_deduplicates_cycle_but_reports_four_rows():
    bank, key, evidence = load_fixture()
    row = answer(load_reader().svar(bank, key, evidence), "Q5")
    assert row["svar"]["syklus"] is True
    assert row["svar"]["rader"] == 4
