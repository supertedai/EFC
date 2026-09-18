"""The silent failure paths in ``efc_ai_brain`` (t_f3d62da3).

A failure dressed up as an empty answer:

1. ``_query_neo4j`` returned ``[]`` for EVERY exception — the same value as
   "the graph answered and there are no edges". The caller then printed
   ``Graph: 0 concepts, 0 related papers``, which reads as a measurement, and
   handed the empty lists to the model as "this paper connects to nothing".
2. ``write_page`` swallowed a broken navbar sanitizer with ``pass`` right
   before writing a public page: the page went out with whatever navbar it
   came in with, and nothing said so.

What is locked here: "the query never ran" has to be a different answer from
"the answer was empty", at every step out to the log and the prompt — and a
sanitizer that fails still lets the write through while naming the page and
the error. Silence is the bug, not the exception.
"""
from __future__ import annotations

import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAINT = ROOT / "scripts" / "maintenance"
PUBLIC = ROOT / "docs" / "public"
sys.path.insert(0, str(MAINT))

import _nav_helper  # noqa: E402
import efc_ai_brain as brain  # noqa: E402

DOI = "10.6084/m9.figshare.12345678"
PAGE = "EFC_Changelog.html"


class _Answer:
    """Minimal stand-in for the context manager ``urlopen`` returns."""

    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None


def _answers(payload: bytes, monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen",
                        lambda *a, **k: _Answer(payload))


# ── 1. the Neo4j query ──────────────────────────────────────────────

def test_an_api_that_never_answered_is_not_an_empty_graph(monkeypatch, capsys):
    def refused(*a, **k):
        raise urllib.error.URLError("Connection refused")

    monkeypatch.setattr(urllib.request, "urlopen", refused)

    assert brain._query_neo4j("MATCH (n) RETURN n") is None
    said = capsys.readouterr().out
    assert "[WARN]" in said and "did not run" in said
    assert "URLError" in said, "the log has to name the failure it swallowed"


def test_a_completed_query_with_no_records_is_an_empty_list(monkeypatch, capsys):
    _answers(b'{"records": []}', monkeypatch)

    assert brain._query_neo4j("MATCH (n) RETURN n") == []
    assert "[WARN]" not in capsys.readouterr().out, (
        "an empty answer is not a failure and must not be reported as one")


def test_an_answer_that_is_not_a_record_list_is_no_answer(monkeypatch, capsys):
    for payload in (b'{"records": {"n": 1}}', b'{"result": 7}', b"[1, 2, 3]"):
        _answers(payload, monkeypatch)
        assert brain._query_neo4j("MATCH (n) RETURN n") is None, payload
        assert "[WARN]" in capsys.readouterr().out, payload


def test_the_graph_context_says_when_it_is_not_measured(monkeypatch):
    monkeypatch.setattr(brain, "_query_neo4j", lambda *a, **k: None)

    ctx = brain._query_graph_context({"doi": DOI, "keywords": ["energy flow"]})

    assert ctx["graph_available"] is False
    assert "concepts" in ctx["graph_error"]
    assert "related_papers" in ctx["graph_error"]
    # Every list stays a list — downstream slices them unguarded.
    for key in ("concepts", "related_papers", "related_validations"):
        assert isinstance(ctx[key], list), key
    # And the graceful degradation survives: the paper's own keywords fill in.
    assert [c["name"] for c in ctx["concepts"]] == ["energy flow"]


def test_a_measured_but_empty_graph_is_not_flagged(monkeypatch):
    monkeypatch.setattr(brain, "_query_neo4j", lambda *a, **k: [])

    ctx = brain._query_graph_context({"doi": DOI})

    assert ctx["graph_available"] is True
    assert ctx["graph_error"] == ""
    assert ctx["concepts"] == []
    assert ctx["related_papers"] == []


def test_the_model_is_told_when_the_graph_was_not_measured(monkeypatch):
    seen = {}

    def capture(prompt, max_tokens=8000, retries=4):
        seen["prompt"] = prompt
        return None  # no answer; we only want the prompt

    monkeypatch.setattr(brain, "call_llm", capture)
    ctx = {
        "concepts": [], "related_papers": [], "related_validations": [],
        "graph_available": False,
        "graph_error": "Neo4j did not answer: concepts, related_papers",
    }

    assert brain.analyze_holistic_impact(
        {"title": "T", "doi": DOI}, "", ctx, {}) is None

    prompt = seen["prompt"]
    assert "NOT MEASURED" in prompt
    assert "Neo4j did not answer: concepts, related_papers" in prompt, (
        "the model has to see WHY the lists are empty")
    assert "do not write that this paper has no graph" in prompt


def test_a_measured_graph_gets_no_such_note(monkeypatch):
    seen = {}
    monkeypatch.setattr(brain, "call_llm",
                        lambda prompt, **k: seen.setdefault("prompt", prompt))
    ctx = {"concepts": [{"name": "IMX", "domain": "core", "type": "concept"}],
           "related_papers": [], "related_validations": [],
           "graph_available": True, "graph_error": ""}

    brain.analyze_holistic_impact({"title": "T", "doi": DOI}, "", ctx, {})

    assert "NOT MEASURED" not in seen["prompt"]
    assert "IMX" in seen["prompt"]


# ── 2. the navbar sanitizer before a public write ───────────────────

def test_a_broken_sanitizer_is_reported_and_the_write_still_happens(
        tmp_path, monkeypatch, capsys):
    side = tmp_path / PAGE
    side.write_text("<html><body>old</body></html>", encoding="utf-8")
    monkeypatch.setattr(brain, "PUBLIC_PAGES", {"changelog": str(side)})

    def broken(html, page=None):
        raise RuntimeError("navbar renderer unavailable")

    monkeypatch.setattr(_nav_helper, "ensure_nav", broken)

    brain.write_page("changelog", "<html><body>new</body></html>")

    # The write is not blocked: the page content is the deliverable.
    assert "new" in side.read_text(encoding="utf-8")
    said = capsys.readouterr().out
    assert "[WARN]" in said, "a failed shield must not be silent"
    assert PAGE in said and "RuntimeError" in said
    assert "navbar renderer unavailable" in said
    assert "navbar it had" in said, "the log has to say what shipped instead"


def test_a_working_sanitizer_is_not_reported(tmp_path, monkeypatch, capsys):
    side = tmp_path / PAGE
    side.write_text((PUBLIC / PAGE).read_text(encoding="utf-8"),
                    encoding="utf-8")
    monkeypatch.setattr(brain, "PUBLIC_PAGES", {"changelog": str(side)})

    brain.write_page("changelog", side.read_text(encoding="utf-8"))

    assert "[WARN]" not in capsys.readouterr().out, (
        "the warning must mean «the sanitizer failed», not «write_page ran»")
    assert "color:#c22;" in side.read_text(encoding="utf-8")
