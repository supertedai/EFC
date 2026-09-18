"""The dataset scan report is a function of CONTENT, never of the clock.

Measured 2026-09-18 (card t_782249e4): the idempotence guard added in f99aeb71
compared the report's ``date`` field (``datetime.date.today()``) as well as the
findings, so the first run on a new calendar day rewrote
``.claude/dataset_scan_report.json`` with byte-identical findings and two fresh
finding timestamps. The canonical maintenance sequence therefore left a git
diff in the working tree on every new day, with no content behind it — the same
class as rule 51 in the EFC build discipline (a generator that stamps the clock
unconditionally keeps the tree permanently dirty).

What is pinned here:

* a day boundary alone writes nothing — the report stays byte-identical;
* the exit code follows the finding, not the write;
* a finding carries its own ``first_seen`` and KEEPS it across writes (an
  unchanged finding may not be re-stamped as newly observed);
* a legacy report (schema before 2026-09-18) is read, not discarded — its
  ``timestamp`` date part becomes ``first_seen``;
* the expiry the artifact declares for itself is READ: an expired finding is
  reported, a fresh one is silent, and a report that declares no expiry is a
  finding rather than an empty answer;
* ``--dry-run`` writes nothing, and the committed artifact carries provenance
  and an expiry.

The wall-clock age of the COMMITTED report is deliberately NOT asserted in this
suite: that assertion has no resolution reachable from a test run, so it would
be red for every unrelated PR until somebody handled the finding — the
permanently-red gate class rule 51 is about. The consequence lives where it can
be acted on: the scanner reads the expiry on every run and ``--check-stale``
answers exit 1 for a consumer that wants to gate on it.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCANNER = REPO / "scripts" / "maintenance" / "efc_dataset_scanner.py"
REPORT = REPO / ".claude" / "dataset_scan_report.json"
READER = "scripts/maintenance/efc_dataset_scanner.py"

DAY1 = dt.date(2026, 9, 17)
DAY2 = dt.date(2026, 9, 18)

# Canned page content and roadmap: every term below is one of the scanner's own
# search terms, so the fixture yields findings without touching the network.
PAGE = "<html><h2>DESI data release</h2><p>KiDS DR5 cosmic shear</p></html>"
ROADMAP = "<p>DESI DR1 is published</p>"


def load_scanner():
    """The real module, loaded the way the maintenance sequence runs it."""
    spec = importlib.util.spec_from_file_location("efc_dataset_scanner_under_test", SCANNER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def clock(day: dt.date):
    """A datetime module whose today()/utcnow() are frozen on `day`."""
    class D(dt.date):
        @classmethod
        def today(cls):
            return day

    class DT(dt.datetime):
        @classmethod
        def utcnow(cls):
            return dt.datetime(day.year, day.month, day.day, 7, 25, 28)

    return types.SimpleNamespace(date=D, datetime=DT, timedelta=dt.timedelta)


class Rig:
    """The real scanner, pointed at a temp report and a temp roadmap."""

    def __init__(self, tmp_path: Path):
        self.mod = load_scanner()
        self.page = PAGE
        roadmap = tmp_path / "roadmap.html"
        roadmap.write_text(ROADMAP, encoding="utf-8")
        self.report = tmp_path / "dataset_scan_report.json"
        self.mod.ROADMAP = str(roadmap)
        self.mod.REPORT_PATH = str(self.report)
        self.mod.fetch_url = lambda url, timeout=10: self.page

    def run(self, day: dt.date, *flags: str) -> int:
        self.mod.datetime = clock(day)
        argv = sys.argv
        sys.argv = ["efc_dataset_scanner.py", *flags]
        try:
            return self.mod.main()
        finally:
            sys.argv = argv

    def json(self) -> dict:
        return json.loads(self.report.read_text(encoding="utf-8"))

    def first_seen(self) -> dict:
        return {(f["source"], f["term"]): f["first_seen"] for f in self.json()["findings"]}


@pytest.fixture()
def rig(tmp_path):
    return Rig(tmp_path)


def report_shape(findings, stale_after=90, reader=READER):
    return {"reader": reader, "stale_after_days": stale_after, "known": [], "findings": findings}


def finding(first_seen, source="DESI", term="data release", url="https://example.test/x"):
    return {"source": source, "term": term, "url": url, "first_seen": first_seen}


# --- the defect: a day boundary alone rewrites the report -------------------

def test_a_new_day_with_identical_findings_writes_nothing(rig):
    rig.run(DAY1)
    assert rig.report.exists(), "the fixture produced no report at all"
    first_bytes = rig.report.read_bytes()
    first_mtime = rig.report.stat().st_mtime_ns

    rig.run(DAY2)

    assert rig.report.read_bytes() == first_bytes, (
        "the run one calendar day later rewrote the report although the findings "
        "are identical — that is the daily git diff this guard exists to prevent")
    assert rig.report.stat().st_mtime_ns == first_mtime, (
        "the file was written again (the fixture is byte-stable, but a real run "
        "would have stamped new timestamps into an unchanged report)")


def test_the_exit_code_follows_the_findings_not_the_write(rig):
    writing = rig.run(DAY1)
    skipping = rig.run(DAY1)
    assert writing == skipping == 1, (
        "the scanner answered differently on its second run (write vs. skip) "
        "although it found exactly the same thing: the exit code must follow "
        "the finding, not whether the file needed writing")


def test_an_unchanged_finding_keeps_its_first_seen(rig):
    rig.run(DAY1)
    before = rig.first_seen()
    assert before, "the fixture produced no findings"
    assert set(before.values()) == {DAY1.isoformat()}, before

    rig.page = PAGE + "<p>Simons first light</p>"
    rig.run(DAY2)

    after = rig.first_seen()
    assert after[("Simons Observatory", "first light")] == DAY2.isoformat(), (
        "a finding that appears for the first time today must be stamped today")
    for key, seen in before.items():
        assert after[key] == seen, (
            f"{key} was re-stamped as first seen {after[key]} (was {seen}) — a "
            f"write refreshes the observation date of findings nobody re-observed, "
            f"which is provenance drift, not an update")


def test_a_legacy_report_keeps_its_observation_dates(rig):
    """The schema before 2026-09-18 carried `timestamp` and a top-level `date`."""
    rig.report.write_text(json.dumps({
        "date": "2026-09-10",
        "known": ["DESI DR1"],
        "findings": [{
            "source": "DESI", "term": "data release",
            "url": "https://data.desi.lbl.gov/doc/releases/",
            "timestamp": "2026-09-10T07:25:28.189627",
        }],
    }, indent=2), encoding="utf-8")

    rig.run(DAY2)

    seen = rig.first_seen()
    assert seen[("DESI", "data release")] == "2026-09-10", (
        "the legacy timestamp was dropped and the finding re-stamped as new — the "
        "observation date is the one fact the report exists to carry")
    assert "date" not in rig.json(), (
        "the clock stamp is back in the report: it cannot be both idempotent and "
        "true (excluding it from the comparison leaves a date claiming to be the "
        "last scan)")


# --- the expiry the artifact declares for itself (rule 62) ------------------

def test_an_expired_finding_is_reported_and_a_fresh_one_is_silent():
    mod = load_scanner()
    old = finding((DAY2 - dt.timedelta(days=120)).isoformat())
    fresh = finding((DAY2 - dt.timedelta(days=10)).isoformat(), term="DR5")

    expired = mod.expired_findings(report_shape([old, fresh]), DAY2)

    assert [f["term"] for f in expired] == ["data release"], expired
    assert expired[0]["age_days"] == 120, expired
    assert expired[0]["stale_after_days"] == 90, expired


def test_a_report_without_an_expiry_is_a_finding_not_silence():
    mod = load_scanner()
    problems = mod.report_problems({"known": [], "findings": [finding(DAY1.isoformat())]})
    assert any("stale_after_days" in p for p in problems), (
        "a report that declares no expiry answers forever — that is a finding, "
        "not an empty answer; nothing distinguishes it from nobody having looked")


def test_report_problems_names_a_finding_with_no_readable_date():
    mod = load_scanner()
    problems = mod.report_problems(report_shape([finding("last tuesday")]))
    assert any("DESI/data release" in p for p in problems), problems


def test_a_report_that_cannot_be_read_is_not_an_empty_answer(rig, capsys):
    """`no report` and `unreadable report` may not collapse into one value: the
    write path would overwrite observations it could not read and re-date them
    as new."""
    rig.report.write_text("{not json", encoding="utf-8")

    rig.run(DAY1)

    assert rig.report.read_text(encoding="utf-8") == "{not json", (
        "the run rewrote a report it could not read — the observations it "
        "carried are now dated as if they were made today")
    assert "cannot be read" in capsys.readouterr().out


def test_a_missing_report_is_named_by_the_stale_check(tmp_path, capsys):
    mod = load_scanner()
    missing = tmp_path / "nothing-here.json"

    assert mod.check_stale(str(missing), today=DAY2) == 1

    out = capsys.readouterr().out
    assert "no report at" in out, (
        "an absent artifact answered like a clean one — absence is not an answer")


def test_a_broken_report_is_named_by_the_stale_check(tmp_path, capsys):
    mod = load_scanner()
    path = tmp_path / "report.json"
    path.write_text("[]", encoding="utf-8")

    assert mod.check_stale(str(path), today=DAY2) == 1
    assert "not a report object" in capsys.readouterr().out


def test_check_stale_fails_on_an_expired_report_and_passes_a_fresh_one(tmp_path, capsys):
    mod = load_scanner()
    path = tmp_path / "report.json"

    path.write_text(json.dumps(report_shape([
        finding((DAY2 - dt.timedelta(days=120)).isoformat())])), encoding="utf-8")
    assert mod.check_stale(str(path), today=DAY2) == 1
    out = capsys.readouterr().out
    assert "data release" in out and "expired" in out, out

    path.write_text(json.dumps(report_shape([finding(DAY2.isoformat())])), encoding="utf-8")
    assert mod.check_stale(str(path), today=DAY2) == 0


def test_check_stale_never_reaches_the_network(tmp_path):
    """`--check-stale` reads the report and nothing else."""
    mod = load_scanner()
    def boom(url, timeout=10):
        raise AssertionError("--check-stale fetched a page")

    mod.fetch_url = boom
    path = tmp_path / "report.json"
    path.write_text(json.dumps(report_shape([finding(DAY2.isoformat())])), encoding="utf-8")
    assert mod.check_stale(str(path), today=DAY2) == 0


def test_a_run_reads_the_expiry_it_wrote(rig, capsys):
    """The expiry has a consequence on the path that produces the artifact."""
    rig.run(DAY1)
    rig.report.write_text(json.dumps(report_shape(
        [finding("2020-01-01")], stale_after=90)), encoding="utf-8")

    rig.run(DAY1)

    out = capsys.readouterr().out
    assert "EXPIRED" in out and "2020-01-01" in out, out


# --- the flags --------------------------------------------------------------

def test_dry_run_writes_nothing(rig):
    rig.run(DAY1, "--dry-run")
    assert not rig.report.exists(), "--dry-run wrote the report"


# --- the committed artifact -------------------------------------------------

def test_the_committed_report_carries_provenance_and_an_expiry():
    report = json.loads(REPORT.read_text(encoding="utf-8"))

    assert "date" not in report, (
        "a clock stamp is back in the committed report: it cannot be both "
        "idempotent and true")
    assert report.get("reader") == READER, report.get("reader")
    assert (REPO / READER).is_file(), "the reader the report names does not exist"
    assert isinstance(report.get("stale_after_days"), int), report.get("stale_after_days")
    assert report["stale_after_days"] > 0, report["stale_after_days"]

    assert report["findings"], "the report carries no findings — the fixture is empty"
    for f in report["findings"]:
        assert f.get("source") and f.get("term"), f
        assert str(f.get("url", "")).startswith("http"), f
        dt.date.fromisoformat(f["first_seen"])  # raises if it is not a real date
