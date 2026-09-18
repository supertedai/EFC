"""One-run probe — this test is MEANT to fail. Card t_89eea983.

The card's fourth requirement is a mutation proof: a deliberately failing test
that turns the PR red, because a job that cannot fail is not a gate. The probe
is removed again in the next commit; nothing in this file describes the product.

The job's command carries a TEMPORARY `--ignore=tests/test_atlas_retain.py` in
this same commit, for a measured reason: the collection error from PR #532
stops the whole pytest session before a single test runs, so without the
ignore the probe could never execute and the "proof" would be about the
collection error rather than about a failing test. Both changes are reverted
together in the next commit.

Side effect worth keeping, since it is the same proof for the guard: adding
that `--ignore` also makes
tests/test_workflows_parse.py::TheWholeSuiteRuns::
test_runs_from_the_root_without_exclusions fail in the C10 job — the lock on
the gate's shape fires in CI, not only locally.
"""


def test_ci_gate_probe_fails_on_purpose() -> None:
    assert False, "deliberate failure (t_89eea983) — the gate must go red"
