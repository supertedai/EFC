"""Mechanical scorer for the blind EFC-atlas experiment."""
from __future__ import annotations

from typing import Any


def _text(value: str) -> str:
    return (value.strip().lower().replace("æ", "ae").replace("ø", "o").replace("å", "a"))


def _normal(value: Any) -> Any:
    if isinstance(value, str):
        return _text(value)
    if isinstance(value, list):
        values = {_stable(_normal(item)): _normal(item) for item in value}
        return [values[key] for key in sorted(values)]
    if isinstance(value, dict):
        return {key: _normal(item) for key, item in value.items()}
    return value


def _stable(value: Any) -> str:
    if isinstance(value, dict):
        return "{" + ",".join(f"{k}:{_stable(value[k])}" for k in sorted(value)) + "}"
    if isinstance(value, list):
        return "[" + ",".join(_stable(item) for item in value) + "]"
    return repr(value)


def _matches(actual: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return False
        return all(key in actual and _matches(actual[key], value) for key, value in expected.items())
    return _normal(actual) == _normal(expected)


def _expected(question: dict) -> Any:
    return question.get("nokkel")


def _positive_support(value: Any) -> bool:
    if isinstance(value, dict):
        amount = value.get("antall")
        return isinstance(amount, (int, float)) and not isinstance(amount, bool) and amount > 0
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def score(svar: list[dict], key: dict) -> dict:
    by_id = {item.get("id"): item for item in svar}
    questions = {item.get("id"): item for item in key.get("sporsmal", [])}
    result = {"korrekt": 0, "feil": 0, "avstaaelse": 0,
              "falske_stoettepastander": 0, "proveniens": 0}
    for qid, question in questions.items():
        item = by_id.get(qid)
        if item is None:
            result["feil"] += 1
            continue
        if item.get("grunnlag"):
            result["proveniens"] += 1
        if item.get("avstaar") is True:
            result["avstaaelse"] += 1
            continue
        actual = item.get("svar")
        expected = _expected(question)
        if isinstance(expected, dict):
            comparable = {k: expected[k] for k in expected if k in expected}
            correct = _matches(actual, comparable)
        else:
            correct = _matches(actual, expected)
        if correct:
            result["korrekt"] += 1
        else:
            result["feil"] += 1
        if qid == "Q3" and _positive_support(actual):
            result["falske_stoettepastander"] += 1
    return result
