"""Lock the PR-triage whitelist: auto-act is CLOSE of DEAD/SUPERSEDED only.

These tests encode the second-opinion correction (gpt-5.6-luna, 0.94): a
"routine" PR touching tests/scripts/workflows/Makefile is NOT auto-merge
eligible — it escalates. Only machine-verifiable derived artifacts would
auto-merge, and v1 ships no such class.
"""

import datetime as dt
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.maintenance.efc_pr_triage import (
    PR,
    age_days,
    classify,
    is_canonical,
    is_close_class,
)


def mk(**kw):
    defaults = dict(
        number=1,
        title="fix(docs): navbar",
        is_draft=False,
        merge_state="CLEAN",
        updated_at="2026-11-17T10:00:00Z",
        files=("docs/public/EFC_Changelog.html",),
    )
    defaults.update(kw)
    return PR(**defaults)


def test_dead_point_in_time_draft_closes():
    pr = mk(is_draft=True, merge_state="UNKNOWN",
            title="EFC research-watch v1.9: 5 new deltas", updated_at="2026-06-01T00:00:00Z")
    assert classify(pr) == "close_dead"


def test_superseded_closes():
    pr = mk()
    assert classify(pr, superseded=True) == "close_superseded"


def test_dirty_escalates_rebase():
    pr = mk(merge_state="DIRTY")
    assert classify(pr) == "escalate_needs_rebase"


def test_canonical_paths_escalate_even_if_clean():
    pr = mk(merge_state="CLEAN", files=("schema/regime_nodes.jsonld",))
    assert classify(pr) == "escalate_canonical"


def test_routine_clean_escalates_not_merges():
    # The panel's core correction: a green PR touching only "routine" paths
    # still escalates — there is NO auto-merge class.
    pr = mk(merge_state="CLEAN", files=("docs/public/EFC_Changelog.html",))
    cls = classify(pr)
    assert cls == "escalate_routine"
    assert not is_close_class(cls)


def test_workflows_tests_scripts_are_not_canonical():
    # They are NOT close/canonical — they fall through to routine/unknown.
    for files in ((".github/workflows/efc.yml",), ("tests/test_x.py",),
                  ("scripts/maintenance/x.py",), ("Makefile",)):
        pr = mk(merge_state="CLEAN", files=files)
        assert classify(pr) in ("escalate_routine", "escalate_unknown"), files


def test_unknown_escalates():
    pr = mk(merge_state="UNKNOWN")
    assert classify(pr) == "escalate_unknown"


def test_only_close_classes_are_auto_act():
    # Whitelist lock: exactly two classes are auto-act; nothing else is.
    for cls in ("close_dead", "close_superseded"):
        assert is_close_class(cls)
    for cls in ("escalate_needs_rebase", "escalate_canonical",
                "escalate_routine", "escalate_unknown"):
        assert not is_close_class(cls)


def test_draft_recent_is_not_dead():
    pr = mk(is_draft=True, title="EFC research-watch delta",
            updated_at="2026-11-16T00:00:00Z")
    assert classify(pr) != "close_dead"


def test_draft_old_but_not_point_in_time_is_not_dead():
    pr = mk(is_draft=True, title="feat: something in progress",
            updated_at="2026-06-01T00:00:00Z")
    assert classify(pr) != "close_dead"


def test_stale_point_in_time_draft_dirty_still_dead():
    # A point-in-time draft that also needs rebase is still DEAD, not escalated.
    pr = mk(is_draft=True, merge_state="DIRTY",
            title="external research watchlist: delta scan",
            updated_at="2026-06-01T00:00:00Z")
    assert classify(pr) == "close_dead"


def test_age_days_parses_utc():
    now = dt.datetime(2026, 11, 17, tzinfo=dt.timezone.utc)
    assert age_days("2026-11-07T00:00:00Z", now=now) == 10
