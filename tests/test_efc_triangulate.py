"""Tests for scripts/maintenance/efc_triangulate.py — the triangulation layer.

Hermetic: exercises the pure functions with structured Source/Claim objects.
Covers the panel-reviewed holes: circularity (system-derived/same-lineage),
conflated axes, and cosmetic source lists.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "maintenance" / "efc_triangulate.py"


def _load():
    import sys
    spec = importlib.util.spec_from_file_location("efc_triangulate", SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["efc_triangulate"] = mod  # register so @dataclass resolves __module__
    spec.loader.exec_module(mod)
    return mod


def _src(external_id="10.6084/x", system_derived=False, supports=True,
         data=(), code=(), cite=(), authors=(), org="", at="2026-01-01"):
    mod = _load()
    return mod.Source(
        external_id=external_id, system_derived=system_derived, supports=supports,
        data_lineage=frozenset(data), code_lineage=frozenset(code),
        citation_lineage=frozenset(cite), authors=frozenset(authors),
        organization=org, retrieved_at=at,
    )


def _claim(sources, kind="scientific", risk="low"):
    mod = _load()
    return mod.Claim(claim_id="c1", statement="s", kind=kind, risk=risk, sources=tuple(sources))


def test_external_requires_id_and_not_derived():
    mod = _load()
    assert mod.is_external(_src(external_id="10.6084/x"))
    assert not mod.is_external(_src(external_id=""))                      # no identity
    assert not mod.is_external(_src(system_derived=True))                 # self-generated


def test_two_sources_sharing_lineage_are_correlated():
    mod = _load()
    a = _src(external_id="a", data=("planck_2018",))
    b = _src(external_id="b", data=("planck_2018",))
    assert mod.common_ancestor(a, b)
    assert mod.independence([a, b]) == "correlated"


def test_system_derived_source_is_never_independent():
    mod = _load()
    a = _src(external_id="a", data=("desi",))
    b = _src(external_id="b", system_derived=True, data=("desi",))
    assert mod.independence([a, b]) == "unknown"  # self-generated laundered in


def test_disjoint_external_sources_are_independent():
    mod = _load()
    a = _src(external_id="desi", data=("desi_dr2",), authors=("desi",))
    b = _src(external_id="eboss", data=("eboss_dr16",), authors=("eboss",))
    assert mod.independence([a, b]) == "independent"


def test_missing_provenance_is_unknown():
    mod = _load()
    a = _src(external_id="a", at="")  # no retrieval timestamp
    assert mod.independence([a]) == "unknown"


def test_support_counts_and_conflict():
    mod = _load()
    a = _src(external_id="a", data=("d1",))
    b = _src(external_id="b", data=("d2",))
    c = _src(external_id="c", data=("d3",), supports=False)
    assert mod.support([a]) == "single"
    assert mod.support([a, b]) == "replicated"
    assert mod.support([a, b, c]) == "contradicted"
    assert mod.support([]) == "unsupported"


def test_action_policy():
    mod = _load()
    a = _src(external_id="a", data=("d1",))
    b = _src(external_id="b", data=("d2",))
    # independent + replicated + low risk -> auto-accept
    assert mod.classify(_claim([a, b], kind="scientific", risk="low"))["action"] == "auto-accept"
    # single source -> escalate
    assert mod.classify(_claim([a], kind="scientific", risk="low"))["action"] == "escalate"
    # correlated sources -> escalate (not auto-accept)
    a2 = _src(external_id="a", data=("d1",))
    b2 = _src(external_id="b", data=("d1",))  # shared lineage
    assert mod.classify(_claim([a2, b2], kind="scientific", risk="low"))["action"] == "escalate"
    # high risk -> escalate even if replicated
    assert mod.classify(_claim([a, b], kind="scientific", risk="high"))["action"] == "escalate"
    # falsify/canonize/publish -> always owner-gate
    assert mod.classify(_claim([a, b], kind="falsify"))["action"] == "owner-gate"
    assert mod.classify(_claim([a, b], kind="publish"))["action"] == "owner-gate"
    # mechanical -> auto-accept (deterministic)
    assert mod.classify(_claim([], kind="mechanical"))["action"] == "auto-accept"


def test_validate_sources_rejects_cosmetic_lists():
    mod = _load()
    good = _src(external_id="a", data=("d1",))
    derived = _src(external_id="b", system_derived=True, data=("d1",))
    dup = _src(external_id="a", data=("d2",))
    noprov = _src(external_id="c", at="")
    problems = mod.validate_sources([good, derived, dup, noprov])
    assert len(problems) == 3  # derived, duplicate, missing-provenance
    assert mod.validate_sources([good]) == []
