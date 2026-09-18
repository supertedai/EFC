import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import leser_a
import scorer

KEY_PATH = HERE / "key.json"
BANK_PATH = Path(__file__).parents[3] / "schema" / "regime_nodes.jsonld"
PYTHON = "/opt/venvs/t_123ed6d9/bin/python"
KEY_SHA256 = "d3fd75b640b0adf92bd66154cbe194870bd0303ec4fd226b1b6db3ddf28212c3"


def load_key():
    return json.loads(KEY_PATH.read_text(encoding="utf-8"))


def load_bank():
    raw = subprocess.check_output(
        ["git", "show", "origin/main:schema/regime_nodes.jsonld"],
        cwd=HERE.parents[2],
        text=True,
    )
    return json.loads(raw)


def answers_by_id():
    return {item["id"]: item for item in leser_a.svar(load_bank(), load_key())}


def test_reader_answers_q1_and_q8():
    answers = answers_by_id()
    assert answers["Q1"]["svar"] == {
        "observasjon": ["obs.fsigma8", "obs.s8"],
        "regime": ["efc.l2"],
    }
    assert answers["Q8"]["svar"] == ["efc.l1", "efc.l2"]


def test_reader_abstains_or_returns_zero_for_q3():
    answer = answers_by_id()["Q3"]
    assert answer["avstaar"] or answer["svar"] == {"antall": 0, "merknad": "0 av 86 relasjoner i banken baerer stoette eller motsigelse. De 8 har til sammen 16 relasjoner, alle OBSERVED_IN, COUPLED_TO, ANALOGOUS_TO eller INSTANCE_OF/EMERGES_FROM."}


def test_scorer_normalizes_case_diacritics_and_list_order():
    key = {"sporsmal": [{"id": "Q", "nokkel": ["Æble", "Åse", "Ørn"]}]}
    answer = [{"id": "Q", "svar": ["ørn", "æBLE", "åSE"], "grunnlag": "x:y", "avstaar": False}]
    result = scorer.score(answer, key)
    assert result == {"korrekt": 1, "feil": 0, "avstaaelse": 0, "falske_stoettepastander": 0, "proveniens": 1}


def test_scorer_counts_false_support_claim_for_q3():
    key = {"sporsmal": [{"id": "Q3", "nokkel": {"antall": 0}}]}
    answer = [{"id": "Q3", "svar": {"antall": 2}, "grunnlag": "x:y", "avstaar": False}]
    result = scorer.score(answer, key)
    assert result["falske_stoettepastander"] == 1


def test_reader_does_not_change_key():
    before = hashlib.sha256(KEY_PATH.read_bytes()).hexdigest()
    leser_a.svar(load_bank(), load_key())
    after = hashlib.sha256(KEY_PATH.read_bytes()).hexdigest()
    assert before == after == KEY_SHA256
