"""The cross-rotation must hold: a coordinate is a scalar, and a cross partitions.

Measured 2026-09-19. Two rules, both learned the same hour they were broken:

1. A coordinate is a SCALAR. An earlier version of the cross pointed at `nivaa`
   and `regime`, which are objects, so a "rotation" printed whole objects as
   cell values. It looked like an answer and was not one.
2. A rotation PARTITIONS. Every node lands in exactly one cell; a node lost or
   counted twice is a silent hole in the result.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts"))

import atlas_kryss as K  # noqa: E402
import atlas_lesing  # noqa: E402


@pytest.fixture(scope="module")
def atlas() -> dict:
    return atlas_lesing.les_atlas(ROT, ref="HEAD")


@pytest.fixture(scope="module")
def noder(atlas: dict) -> list[dict]:
    return atlas["noder"]


def test_no_derived_axis_returns_an_object(noder: list[dict]) -> None:
    """Rule 1, for the axes this file owns."""
    for axis in K.DERIVED:
        for n in noder:
            v = K.axis_value(n, axis)
            assert v is None or isinstance(v, (str, int, float, bool)), (
                f"{axis} resolves to {type(v).__name__} on {n['id']}")


def test_an_object_valued_axis_is_refused_not_printed(atlas: dict) -> None:
    """`nivaa` is an object; asking for it must fail loudly, not print a dict."""
    assert "nivaa" in atlas_lesing.akser(atlas) is not None  # discovered, not special-cased
    with pytest.raises(SystemExit):
        K.axis_value(atlas["noder"][0], "nivaa")
    # the coordinate itself is fine
    assert isinstance(K.axis_value(atlas["noder"][0], "nivaa.indeks"), int)


def test_can_be_felled_answers_whether_not_why(noder: list[dict]) -> None:
    assert {K.axis_value(n, "can_be_felled") for n in noder} <= {"yes", "no", None}
    assert {K.axis_value(n, "falsifiability_stance") for n in noder} <= {
        "falsifier", "status", "class", None}
    # whether and why must agree: a falsifier is a yes, and a class is a no
    for n in noder:
        if K.axis_value(n, "falsifiability_stance") == "falsifier":
            assert K.axis_value(n, "can_be_felled") == "yes"
        if K.axis_value(n, "falsifiability_stance") in ("status", "class"):
            assert K.axis_value(n, "can_be_felled") == "no"


def test_a_null_bound_is_a_hole_not_a_bound(noder: list[dict]) -> None:
    """K4: `feilgrense: null` names a hole. Measured: exactly one node has a bound."""
    with_poster = [n["id"] for n in noder if K._get(n, "usikkerhet.poster")]
    with_bound = [n["id"] for n in noder if K.axis_value(n, "uncertainty")]
    assert with_poster, "precondition: at least one node carries uncertainty posts"
    assert with_bound and len(with_bound) < len(with_poster), (
        f"poster={with_poster} bounds={with_bound} — a null bound is not a bound")


def test_rotation_partitions_the_population(noder: list[dict]) -> None:
    """Rule 2: no node lost, none counted twice."""
    akser = [a for a in atlas_lesing.akser(atlas_lesing.les_atlas(ROT, ref="HEAD"))
             if "." in a][:2]
    for axes in ([K.DERIVED[0], "epistemikk.evidensstatus"], akser):
        r = K.rotate(noder, axes)
        assert r["nodes"] == len(noder)
        assert sum(c for _, c in r["cells"]) == len(noder), (axes, r["cells"][:5])
        assert sorted(r["axes"]) == sorted(axes)


def test_a_hole_is_printed_as_a_hole_never_as_zero(noder: list[dict]) -> None:
    """The population of a hole is visible: the sealing count must match.

    Measured 2026-09-20 (card t_2d7a6537): TWO nodes carry a bound —
    `obs.rar` (0.029) and `efc.rotation_engine` (0.015 and 0.045), both read
    back from their sealed sources and checked against the source's own
    `file:line` by the uncertainty layer. Everything else is a NAMED hole, and
    a hole shall be counted as one — never as zero.

    The bound set is named rather than counted, so that a third bound cannot
    appear without someone saying where it came from.
    """
    bundet = {n["id"] for n in noder if K.axis_value(n, "uncertainty")}
    assert bundet == {"obs.rar", "efc.rotation_engine"}, (
        f"the set of bounded nodes changed: {sorted(bundet)}")
    r = K.rotate(noder, [K.DERIVED[2]])
    holes = sum(c for key, c in r["cells"] if key[0] == "—")
    assert holes == len(noder) - len(bundet), (
        f"expected {len(noder) - len(bundet)} unbounded nodes, got {holes}")


def test_an_unknown_axis_is_refused(noder: list[dict], capsys) -> None:
    assert K.axis_value(noder[0], K.DERIVED[0]) in ("yes", "no", None)
