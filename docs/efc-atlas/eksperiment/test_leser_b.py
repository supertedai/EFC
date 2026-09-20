import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import bank  # noqa: E402
# Pinned to the CORRECTED key (67938617). The previous pinning pointed at
# d3fd75b6, which contained four counting errors found by two independent tracks.
# The purpose is the same: a silent change of the key must fail here.
KEY_SHA256 = "f3e4b880a2c474608053fc553c4f80580a636069066751425fd66d49e1d094f9"


def load_reader():
    spec = importlib.util.spec_from_file_location("leser_b", ROOT / "leser_b.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_fixture():
    key = json.loads((ROOT / "key.json").read_text())
    evidence = json.loads((ROOT / "evidenslag.json").read_text())
    # The SEALED bank, not origin/main: the key is a dated measurement, and
    # reading the living atlas here is what made these tests red on main.
    # See bank.py and the note at the end of RESULTAT.md.
    return bank.load_sealed(), key, evidence


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


def test_q4_finds_a_reversed_observed_in_edge_men_ikke_alle():
    """B finds ONE inverted edge. There are THREE among the eight.

    The assertion below describes what B actually does, not what it ought to
    do. It was built against the key from before the correction (which said
    "1 edge"), and the gap is measured: 1 of 3. That stands in RESULTAT.md,
    not hidden here.
    """
    bank, key, evidence = load_fixture()
    row = answer(load_reader().svar(bank, key, evidence), "Q4")
    assert row["svar"]["subject"] == "efc.hubble_engine"
    assert row["svar"]["predicate"] == "OBSERVED_IN"
    assert row["svar"]["object"] == "obs.bao"


def test_key_is_unchanged():
    assert hashlib.sha256((ROOT / "key.json").read_bytes()).hexdigest() == KEY_SHA256


def test_q5_reports_the_measured_row_count():
    """The pair has 2 rows — one per direction.

    This test originally required 4 rows, because it was pinned to my
    erroneous key. The bank has never had 4: it has 2. A test that inherits
    a wrong answer key guards the wrong answer key — that is why the number
    stands here with the measurement behind it.
    """
    bank, key, evidence = load_fixture()
    row = answer(load_reader().svar(bank, key, evidence), "Q5")
    assert row["svar"]["syklus"] is True
    assert row["svar"]["rader"] == 2
