"""A test may not bind itself to an interpreter that exists on one machine.

Why this exists (measured 2026-09-18, first visible in CI): three test files
started the atlas generator and the atlas navigator as subprocesses through an
absolute path into a venv directory that exists only on the Hermes host. On the
host they passed, so the suite looked green; on `ubuntu-latest` they died with
`FileNotFoundError`. A test that passes only on the host is not a gate, and a
host-only suite hides its own failure — which is the shape this scan makes
visible everywhere.

The path was copied from a sibling file, and that is how the class returns: one
worktree finds a literal that works on its machine and the next one reuses it.
So the rule is a SCAN of every test file, not a promise about three of them,
and the forbidden shape is built at run time so this file does not match itself.

Declared limits (the scan covers the measured class, not the whole hypothesis):

* Only `tests/**` is read. Scripts and gates under `scripts/` have their own
  reasons to name host paths; they are out of this rule's scope on purpose.
* The needle is the venv DIRECTORY, not every absolute path. A test may carry an
  absolute path as DATA — a string it asserts *about* — and live test files do
  exactly that. Failing those would be a false positive, and a gate that cries
  wolf gets switched off.
* A binding widened to some other interpreter path (a system python, a
  hardcoded node binary) still passes this scan. It is a floor, not a proof:
  the rule that a subprocess must use the interpreter RUNNING the test is held
  by `sys.executable` at the call sites, and this scan only fences the shape
  that was measured.
"""
from __future__ import annotations

import pathlib

SELF = pathlib.Path(__file__).resolve()
TESTS = SELF.parent

# Built at run time: this file must not itself contain the shape it forbids.
FORBIDDEN = "/opt" + "/venvs"


def test_no_test_file_binds_itself_to_the_host_venv():
    hits = []
    for path in sorted(TESTS.rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for nr, line in enumerate(text.splitlines(), 1):
            if FORBIDDEN in line:
                hits.append(f"{path.relative_to(TESTS.parent)}:{nr}: {line.strip()}")
    assert not hits, (
        "a test binds itself to an interpreter path that exists on one machine "
        "only — use sys.executable, the interpreter the test itself runs "
        "under:\n" + "\n".join(hits))


def test_the_scan_has_a_floor_and_reads_this_file():
    """Tripwire for the scan itself: an empty walk would make the gate vacuous.

    The count is a floor, not a baseline — `tests/` only grows. It also asserts
    the needle rule: the file carrying this text is inside the walk and must
    still come out clean, or the run-time construction above is broken.
    """
    files = sorted(TESTS.rglob("*.py"))
    assert len(files) > 100, f"the scan saw only {len(files)} test files"
    assert SELF in files, "this file is not inside its own scan — it measures nothing"
