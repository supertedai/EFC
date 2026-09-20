import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import bank  # noqa: E402
import leser_a  # noqa: E402
import scorer  # noqa: E402

KEY_PATH = HERE / "key.json"
# Pinnet til den RETTEDE nokkelen (67938617). Den forrige pinningen pekte paa
# d3fd75b6, som inneholdt fire tellefeil funnet av to uavhengige spor.
# Formaalet er det samme: en stille endring av nokkelen skal feile her.
KEY_SHA256 = "f3e4b880a2c474608053fc553c4f80580a636069066751425fd66d49e1d094f9"


def load_key():
    return json.loads(KEY_PATH.read_text(encoding="utf-8"))


def load_bank():
    # The SEALED bank (bank.SEAL_COMMIT), not origin/main. The key was written
    # and committed before the prototype existed; reading the living atlas here
    # made the sealed answers depend on a bank that is still being edited.
    return bank.load_sealed()


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
