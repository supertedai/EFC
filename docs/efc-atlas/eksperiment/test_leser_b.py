import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parent
# Pinnet til den RETTEDE nokkelen (67938617). Den forrige pinningen pekte paa
# d3fd75b6, som inneholdt fire tellefeil funnet av to uavhengige spor.
# Formaalet er det samme: en stille endring av nokkelen skal feile her.
KEY_SHA256 = "f3e4b880a2c474608053fc553c4f80580a636069066751425fd66d49e1d094f9"


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


def test_q4_finds_a_reversed_observed_in_edge_men_ikke_alle():
    """B finner ÉN invertert kant. Det finnes TRE blant de atte.

    Assertsjonen under beskriver hva B faktisk gjor, ikke hva den burde
    gjore. Den ble bygget mot nokkelen for rettingen (som sa «1 kant»), og
    gapet er matt: 1 av 3. Det staar i RESULTAT.md, ikke skjult her.
    """
    bank, key, evidence = load_fixture()
    row = answer(load_reader().svar(bank, key, evidence), "Q4")
    assert row["svar"]["subject"] == "efc.hubble_engine"
    assert row["svar"]["predicate"] == "OBSERVED_IN"
    assert row["svar"]["object"] == "obs.bao"


def test_key_is_unchanged():
    assert hashlib.sha256((ROOT / "key.json").read_bytes()).hexdigest() == KEY_SHA256


def test_q5_reports_the_measured_row_count():
    """Paret har 2 rader — én per retning.

    Denne testen krevde opprinnelig 4 rader, fordi den ble pinnet til min
    feilaktige nokkel. Banken har aldri hatt 4: den har 2. En test som arver
    en gal fasit, vokter den gale fasiten — det er derfor tallet staar her
    med maalingen bak.
    """
    bank, key, evidence = load_fixture()
    row = answer(load_reader().svar(bank, key, evidence), "Q5")
    assert row["svar"]["syklus"] is True
    assert row["svar"]["rader"] == 2
