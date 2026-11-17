"""The cost gate's cosmetic predicate — the anti-case is pinned, not promised.

efc_council_gate.py may skip the gpt-5 scientific-integrity council, but ONLY
when the fragment is identical after stripping presentational attributes
(class/style/id) and collapsing whitespace. That is a weakening of a gate, so
the interesting assertions are the ones that must NOT be skipped: a reviewer
caught the first version of this predicate auto-approving a validation-status
flip (data-result="Planned" -> "Falsified" — 60x on the live pages), which is
exactly the class of change the council exists to see.

Every miss here falls on the safe side (the council runs), and every case below
is a case the council must see. Added by the rebase pass of t_74d74138: the
branch's commit message named the reviewer's anti-case, and nothing pinned it.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "maintenance"))

import efc_council_gate as gate  # noqa: E402


@pytest.mark.parametrize("old,new", [
    ('<div class="nav">A</div>', '<div class="navbar">A</div>'),
    ('<td style="color:red">val</td>', '<td style="color:blue">val</td>'),
    ('<section id="s1">\n  <p>x</p>\n</section>',
     '<section id="s2"> <p>x</p> </section>'),
])
def test_presentational_only_difference_is_cosmetic(old, new):
    """class/style/id and whitespace are the ONLY differences -> skip the call."""
    assert gate._is_cosmetic(old, new) is True


@pytest.mark.parametrize("old,new,why", [
    ('<p data-result="Planned">x</p>', '<p data-result="Falsified">x</p>',
     "a validation-status flip — the reviewer's case"),
    ('<p>Planned</p>', '<p>Falsified</p>', "visible text"),
    ('<p>beta = 0.16</p>', '<p>beta = 0.17</p>', "a number"),
    ('<a href="/a">t</a>', '<a href="/b">t</a>', "a link target"),
    ('<img alt="A">', '<img alt="B">', "an alt text"),
    ('<span title="A">x</span>', '<span title="B">x</span>', "a title"),
    ('<p>10.6084/m9.figshare.31940469</p>',
     '<p>10.6084/m9.figshare.31943361</p>', "a DOI"),
    ('<p>x</p>', '<div>x</div>', "a tag"),
])
def test_anything_but_presentational_difference_runs_the_council(old, new, why):
    """Every case the council must see is NOT cosmetic — the predicate may err
    only toward calling the council."""
    assert gate._is_cosmetic(old, new) is False, why


def test_identical_fragment_is_cosmetic():
    html = '<p class="a">same</p>'
    assert gate._is_cosmetic(html, html) is True


def test_empty_input_is_not_an_exception():
    """The gate must not crash on a missing fragment; it is called before the
    council prompt is built, and a crash there would block every page update."""
    assert gate._is_cosmetic("", "") is True
    assert gate._is_cosmetic(None, "") is True
